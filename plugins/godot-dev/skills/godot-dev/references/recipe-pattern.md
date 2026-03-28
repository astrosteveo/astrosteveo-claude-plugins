# The Recipe-Generator Pattern

A scalable, data-driven approach to procedural content in Godot. This pattern separates **what to generate** (Recipe) from **how to generate it** (Generator), keeping visual assets in the editor where they belong.

## Core Concepts

### Recipe = Rules, Not Assets

A Recipe is a Resource subclass that defines parameters, constraints, and rules. It contains zero logic and zero visual assets. It is pure, serializable, inspector-editable data.

Recipes answer: "What are the rules for this content?"

### Generator = Algorithm, Not Art

A Generator reads a Recipe and an RNG seed, then produces deterministic output. It never creates meshes, materials, or visual resources. It selects, arranges, and composes pre-authored building blocks.

Generators answer: "Given these rules, what's the result?"

### Building Blocks = Editor-Authored Assets

The visual elements that Generators work with are `.tscn` scenes and `.tres` resources created in the Godot editor. Generators reference them via `@export` PackedScene arrays or Resource arrays on the Recipe.

### Determinism

Same Recipe + same seed = same output, every single time. This is non-negotiable. It enables:
- Reproducible worlds (share a seed, get the same result)
- Debugging (reproduce any generation exactly)
- Testing (assert specific outputs for specific inputs)
- Previewing (show what a Recipe will produce before committing)

## Pattern Structure

```
Recipe (Resource)
├── @export parameters (designer-facing)
├── @export building block references (PackedScene[], Resource[])
├── @export curves/distributions (Curve, Gradient)
└── No methods with side effects

Generator (RefCounted or static methods)
├── Input: Recipe + RandomNumberGenerator
├── Output: Data (positions, selections, configurations)
├── References building blocks from Recipe
└── Never creates visual assets

Runtime Consumer (Node)
├── Holds @export Recipe reference
├── Calls Generator when needed
├── Instantiates building blocks based on Generator output
└── Adds instances to the scene tree
```

## Example: Enemy Spawn System

### Recipe

```gdscript
@tool
class_name SpawnRecipe
extends Resource

## Enemy scenes to choose from (must be editor-authored .tscn files)
@export var enemy_scenes: Array[PackedScene] = []

## Relative weights for each enemy scene (parallel array)
@export var enemy_weights: Array[float] = []

## How many enemies to spawn per wave
@export var min_count: int = 3
@export var max_count: int = 8

## Spatial distribution
@export var spawn_radius: float = 10.0
@export var min_distance_between: float = 2.0

## Difficulty scaling — X is wave number (0-1 normalized), Y is difficulty multiplier
@export var difficulty_curve: Curve
```

### Generator

```gdscript
@tool
class_name SpawnGenerator
extends RefCounted

static func generate(recipe: SpawnRecipe, wave: int, max_waves: int, rng: RandomNumberGenerator) -> Array[Dictionary]:
    var difficulty: float = recipe.difficulty_curve.sample(float(wave) / max_waves) if recipe.difficulty_curve else 1.0
    var count: int = rng.randi_range(recipe.min_count, ceili(recipe.max_count * difficulty))

    var results: Array[Dictionary] = []
    var positions: Array[Vector3] = []

    for i in count:
        var scene: PackedScene = _weighted_pick(recipe.enemy_scenes, recipe.enemy_weights, rng)
        var pos: Vector3 = _find_valid_position(recipe.spawn_radius, recipe.min_distance_between, positions, rng)
        positions.append(pos)
        results.append({"scene": scene, "position": pos})

    return results


static func _weighted_pick(items: Array[PackedScene], weights: Array[float], rng: RandomNumberGenerator) -> PackedScene:
    var total: float = 0.0
    for w in weights:
        total += w
    var roll: float = rng.randf() * total
    var cumulative: float = 0.0
    for i in items.size():
        cumulative += weights[i]
        if roll <= cumulative:
            return items[i]
    return items[-1]


static func _find_valid_position(radius: float, min_dist: float, existing: Array[Vector3], rng: RandomNumberGenerator) -> Vector3:
    for attempt in 30:
        var angle: float = rng.randf() * TAU
        var dist: float = rng.randf() * radius
        var candidate := Vector3(cos(angle) * dist, 0.0, sin(angle) * dist)
        var valid: bool = true
        for pos in existing:
            if candidate.distance_to(pos) < min_dist:
                valid = false
                break
        if valid:
            return candidate
    # Fallback: accept the last attempt even if spacing is tight
    var angle: float = rng.randf() * TAU
    var dist: float = rng.randf() * radius
    return Vector3(cos(angle) * dist, 0.0, sin(angle) * dist)
```

### Runtime Consumer

```gdscript
@tool
class_name EnemySpawner
extends Node3D

@export var recipe: SpawnRecipe
@export var seed_value: int = 0
@export var max_waves: int = 10

var _current_wave: int = 0

func spawn_wave() -> void:
    var rng := RandomNumberGenerator.new()
    rng.seed = hash(seed_value + _current_wave)

    var entries: Array[Dictionary] = SpawnGenerator.generate(recipe, _current_wave, max_waves, rng)
    var zone_root: Node = get_tree().get_first_node_in_group("zone_root")

    for entry in entries:
        var instance: Node3D = entry["scene"].instantiate()
        zone_root.add_child(instance)
        instance.global_position = global_position + entry["position"]

    _current_wave += 1
```

## Example: Loot Drop System

### Recipe

```gdscript
@tool
class_name LootRecipe
extends Resource

## Item pool — each entry is a GearData resource authored in the editor
@export var item_pool: Array[Resource] = []

## Weights for each item (parallel array)
@export var item_weights: Array[float] = []

## Rarity thresholds — chance of upgrading rarity tier
@export var rarity_upgrade_chance: float = 0.15

## Quantity range
@export var min_drops: int = 1
@export var max_drops: int = 3

## Guaranteed drop on first kill in a zone
@export var first_kill_guaranteed: bool = true
```

### Generator

```gdscript
@tool
class_name LootGenerator
extends RefCounted

static func generate(recipe: LootRecipe, rng: RandomNumberGenerator, is_first_kill: bool = false) -> Array[Resource]:
    var count: int = rng.randi_range(recipe.min_drops, recipe.max_drops)
    if is_first_kill and recipe.first_kill_guaranteed:
        count = maxi(count, 1)

    var drops: Array[Resource] = []
    for i in count:
        var item: Resource = _weighted_pick(recipe.item_pool, recipe.item_weights, rng)
        drops.append(item)

    return drops


static func _weighted_pick(items: Array[Resource], weights: Array[float], rng: RandomNumberGenerator) -> Resource:
    var total: float = 0.0
    for w in weights:
        total += w
    var roll: float = rng.randf() * total
    var cumulative: float = 0.0
    for i in items.size():
        cumulative += weights[i]
        if roll <= cumulative:
            return items[i]
    return items[-1]
```

## Example: Prop Placement System

For scattering rocks, trees, debris, or decorations across a zone.

### Recipe

```gdscript
@tool
class_name PropScatterRecipe
extends Resource

## Prop scenes to scatter (editor-authored .tscn files)
@export var prop_scenes: Array[PackedScene] = []
@export var prop_weights: Array[float] = []

## Density: props per square unit
@export var density: float = 0.5

## Area to scatter within (centered on the node)
@export var area_size: Vector2 = Vector2(20, 20)

## Random rotation range (degrees)
@export var rotation_min: float = 0.0
@export var rotation_max: float = 360.0

## Random scale range
@export var scale_min: float = 0.8
@export var scale_max: float = 1.2

## Minimum distance between props
@export var min_spacing: float = 1.5

## Exclusion zones — areas where props should not spawn
@export var exclusion_radius: float = 3.0
```

### Generator

```gdscript
@tool
class_name PropScatterGenerator
extends RefCounted

static func generate(recipe: PropScatterRecipe, rng: RandomNumberGenerator, exclusion_points: Array[Vector3] = []) -> Array[Dictionary]:
    var area: float = recipe.area_size.x * recipe.area_size.y
    var count: int = roundi(area * recipe.density)

    var results: Array[Dictionary] = []
    var positions: Array[Vector3] = []

    for i in count:
        var pos: Vector3 = _find_valid_position(recipe, positions, exclusion_points, rng)
        if pos == Vector3.INF:
            continue  # Could not place — skip

        positions.append(pos)
        var scene: PackedScene = _weighted_pick(recipe.prop_scenes, recipe.prop_weights, rng)
        var rot_y: float = rng.randf_range(recipe.rotation_min, recipe.rotation_max)
        var scl: float = rng.randf_range(recipe.scale_min, recipe.scale_max)

        results.append({
            "scene": scene,
            "position": pos,
            "rotation_y": deg_to_rad(rot_y),
            "scale": scl,
        })

    return results


static func _find_valid_position(recipe: PropScatterRecipe, existing: Array[Vector3], exclusions: Array[Vector3], rng: RandomNumberGenerator) -> Vector3:
    var half_x: float = recipe.area_size.x / 2.0
    var half_z: float = recipe.area_size.y / 2.0

    for attempt in 30:
        var candidate := Vector3(
            rng.randf_range(-half_x, half_x),
            0.0,
            rng.randf_range(-half_z, half_z)
        )

        var valid: bool = true
        for pos in existing:
            if candidate.distance_to(pos) < recipe.min_spacing:
                valid = false
                break
        if valid:
            for ex in exclusions:
                if candidate.distance_to(ex) < recipe.exclusion_radius:
                    valid = false
                    break
        if valid:
            return candidate

    return Vector3.INF  # Signal: could not place


static func _weighted_pick(items: Array[PackedScene], weights: Array[float], rng: RandomNumberGenerator) -> PackedScene:
    var total: float = 0.0
    for w in weights:
        total += w
    var roll: float = rng.randf() * total
    var cumulative: float = 0.0
    for i in items.size():
        cumulative += weights[i]
        if roll <= cumulative:
            return items[i]
    return items[-1]
```

## Example: VFX Parameter System

For varying particle effects without creating assets in code.

### Recipe

```gdscript
@tool
class_name VFXRecipe
extends Resource

## Base particle scene (editor-authored, has GPUParticles3D)
@export var particle_scene: PackedScene

## Parameter overrides — the Generator applies these to the instanced scene
@export var lifetime_range: Vector2 = Vector2(0.5, 2.0)
@export var amount_range: Vector2i = Vector2i(8, 32)
@export var speed_scale_range: Vector2 = Vector2(0.8, 1.5)
@export var color_ramp: Gradient
```

### Generator

```gdscript
@tool
class_name VFXGenerator
extends RefCounted

## Returns a dictionary of property overrides to apply to the instanced particle scene
static func generate(recipe: VFXRecipe, rng: RandomNumberGenerator) -> Dictionary:
    return {
        "lifetime": rng.randf_range(recipe.lifetime_range.x, recipe.lifetime_range.y),
        "amount": rng.randi_range(recipe.amount_range.x, recipe.amount_range.y),
        "speed_scale": rng.randf_range(recipe.speed_scale_range.x, recipe.speed_scale_range.y),
    }
```

The consumer instantiates the `particle_scene` from the Recipe, then applies the generated overrides to the GPUParticles3D node's properties. The particle scene itself — its mesh, material, emission shape — is entirely editor-authored.

## Composing Recipes

Recipes can reference other Recipes for complex systems:

```gdscript
@tool
class_name ZoneRecipe
extends Resource

@export var terrain_recipe: TerrainRecipe
@export var prop_recipe: PropScatterRecipe
@export var spawn_recipe: SpawnRecipe
@export var loot_recipe: LootRecipe
@export var ambient_vfx_recipe: VFXRecipe
```

A `ZoneGenerator` reads the `ZoneRecipe` and delegates to each sub-generator. This composes naturally without any single system becoming monolithic.

## Key Principles

1. **Recipes never import Node or SceneTree** — they are pure Resource data
2. **Generators never call `new()` on visual types** — they output data, not assets
3. **Building blocks are always PackedScene or Resource references** — editor-authored, version-controlled
4. **RNG is always injected** — never use global randomness, always pass a seeded RandomNumberGenerator
5. **Output is data, not instances** — Generators return Arrays/Dictionaries, the consumer handles instantiation
