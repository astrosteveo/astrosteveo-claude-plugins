# Data-Driven Design with Custom Resources

A standard Godot approach to configurable, variable content. Custom Resources hold data and configuration; logic reads them to produce results. Visual building blocks are editor-authored scenes and resources — never generated in code as a shortcut.

This is the Godot equivalent of Unity's ScriptableObjects pattern.

## Core Concepts

### Config Resource = Data, Not Logic

A Config Resource is a Resource subclass with `@export` fields defining parameters, rules, and references. It contains no logic and no side effects. Designers edit it in the inspector. It lives as a `.tres` file.

Config Resources answer: "What are the rules for this content?"

### Logic = Algorithm, Not Art

Logic reads a Config Resource and produces results. When randomness is involved, it takes a seeded `RandomNumberGenerator` for deterministic output. It selects, arranges, and composes pre-authored building blocks — it does not create visual assets.

Logic answers: "Given these rules, what's the result?"

### Building Blocks = Editor-Authored Assets

The visual elements that logic works with are `.tscn` scenes and `.tres` resources created in the Godot editor. Config Resources reference them via `@export` PackedScene arrays or Resource arrays.

### Determinism

Same config + same seed = same output, every time. This enables:
- Reproducible worlds (share a seed, get the same result)
- Debugging (reproduce any generation exactly)
- Testing (assert specific outputs for specific inputs)
- Previewing (show what a config will produce before committing)

## Pattern Structure

```
Config Resource (Resource subclass)
├── @export parameters (designer-facing)
├── @export building block references (PackedScene[], Resource[])
├── @export curves/distributions (Curve, Gradient)
└── No methods with side effects

Logic (function, static class, or node)
├── Input: Config + RandomNumberGenerator
├── Output: Data (positions, selections, configurations)
├── References building blocks from Config
└── Does not create visual assets as shortcuts

Runtime Consumer (Node)
├── Holds @export Config reference
├── Calls logic when needed
├── Instantiates building blocks based on output
└── Adds instances to the scene tree
```

## Example: Enemy Spawn System

### Config Resource

```gdscript
class_name SpawnConfig
extends Resource

## Enemy scenes to choose from (editor-authored .tscn files)
@export var enemy_scenes: Array[PackedScene] = []

## Relative weights for each enemy scene (parallel array)
@export var enemy_weights: Array[float] = []

## How many enemies to spawn per wave
@export var min_count: int = 3
@export var max_count: int = 8

## Spatial distribution
@export var spawn_radius: float = 10.0
@export var min_distance_between: float = 2.0

## Difficulty scaling -- X is wave number (0-1 normalized), Y is difficulty multiplier
@export var difficulty_curve: Curve
```

### Generator

```gdscript
class_name SpawnGenerator
extends RefCounted

static func generate(config: SpawnConfig, wave: int, max_waves: int, rng: RandomNumberGenerator) -> Array[Dictionary]:
    var difficulty: float = config.difficulty_curve.sample(float(wave) / max_waves) if config.difficulty_curve else 1.0
    var count: int = rng.randi_range(config.min_count, ceili(config.max_count * difficulty))

    var results: Array[Dictionary] = []
    var positions: Array[Vector3] = []

    for i in count:
        var scene: PackedScene = _weighted_pick(config.enemy_scenes, config.enemy_weights, rng)
        var pos: Vector3 = _find_valid_position(config.spawn_radius, config.min_distance_between, positions, rng)
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
    var angle: float = rng.randf() * TAU
    var dist: float = rng.randf() * radius
    return Vector3(cos(angle) * dist, 0.0, sin(angle) * dist)
```

### Runtime Consumer

```gdscript
class_name EnemySpawner
extends Node3D

@export var config: SpawnConfig
@export var seed_value: int = 0
@export var max_waves: int = 10

var _current_wave: int = 0

func spawn_wave() -> void:
    var rng := RandomNumberGenerator.new()
    rng.seed = hash(seed_value + _current_wave)

    var entries: Array[Dictionary] = SpawnGenerator.generate(config, _current_wave, max_waves, rng)
    var zone_root: Node = get_tree().get_first_node_in_group("zone_root")

    for entry in entries:
        var instance: Node3D = entry["scene"].instantiate()
        zone_root.add_child(instance)
        instance.global_position = global_position + entry["position"]

    _current_wave += 1
```

Note: the enemy scenes referenced in `config.enemy_scenes` are `.tscn` files built in the editor with proper meshes, collision shapes, components, and scripts. The spawner instantiates them — it does not construct them.

## Example: Loot Drop System

### Config

```gdscript
class_name LootConfig
extends Resource

## Item pool -- each entry is a GearData resource authored in the editor
@export var item_pool: Array[Resource] = []
@export var item_weights: Array[float] = []

## Quantity range
@export var min_drops: int = 1
@export var max_drops: int = 3

## Guaranteed drop on first kill in a zone
@export var first_kill_guaranteed: bool = true
```

### Generator

```gdscript
class_name LootGenerator
extends RefCounted

static func generate(config: LootConfig, rng: RandomNumberGenerator, is_first_kill: bool = false) -> Array[Resource]:
    var count: int = rng.randi_range(config.min_drops, config.max_drops)
    if is_first_kill and config.first_kill_guaranteed:
        count = maxi(count, 1)

    var drops: Array[Resource] = []
    for i in count:
        var item: Resource = _weighted_pick(config.item_pool, config.item_weights, rng)
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

### Config

```gdscript
class_name PropScatterConfig
extends Resource

## Prop scenes to scatter (editor-authored .tscn files)
@export var prop_scenes: Array[PackedScene] = []
@export var prop_weights: Array[float] = []

## Density: props per square unit
@export var density: float = 0.5

## Area to scatter within (centered on the node)
@export var area_size: Vector2 = Vector2(20, 20)

## Random rotation and scale ranges
@export var rotation_min: float = 0.0
@export var rotation_max: float = 360.0
@export var scale_min: float = 0.8
@export var scale_max: float = 1.2

## Minimum distance between props
@export var min_spacing: float = 1.5
```

### Generator

```gdscript
class_name PropScatterGenerator
extends RefCounted

static func generate(config: PropScatterConfig, rng: RandomNumberGenerator) -> Array[Dictionary]:
    var area: float = config.area_size.x * config.area_size.y
    var count: int = roundi(area * config.density)

    var results: Array[Dictionary] = []
    var positions: Array[Vector3] = []

    for i in count:
        var pos: Vector3 = _find_valid_position(config, positions, rng)
        if pos == Vector3.INF:
            continue

        positions.append(pos)
        var scene: PackedScene = _weighted_pick(config.prop_scenes, config.prop_weights, rng)
        var rot_y: float = rng.randf_range(config.rotation_min, config.rotation_max)
        var scl: float = rng.randf_range(config.scale_min, config.scale_max)

        results.append({
            "scene": scene,
            "position": pos,
            "rotation_y": deg_to_rad(rot_y),
            "scale": scl,
        })

    return results


static func _find_valid_position(config: PropScatterConfig, existing: Array[Vector3], rng: RandomNumberGenerator) -> Vector3:
    var half_x: float = config.area_size.x / 2.0
    var half_z: float = config.area_size.y / 2.0

    for attempt in 30:
        var candidate := Vector3(
            rng.randf_range(-half_x, half_x),
            0.0,
            rng.randf_range(-half_z, half_z)
        )
        var valid: bool = true
        for pos in existing:
            if candidate.distance_to(pos) < config.min_spacing:
                valid = false
                break
        if valid:
            return candidate

    return Vector3.INF


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

## Composing Configs

Configs can reference other configs for complex systems:

```gdscript
class_name ZoneConfig
extends Resource

@export var terrain_config: TerrainConfig
@export var prop_config: PropScatterConfig
@export var spawn_config: SpawnConfig
@export var loot_config: LootConfig
```

A zone generator reads the `ZoneConfig` and delegates to each sub-system. This composes naturally without any single system becoming monolithic.

## Key Principles

1. **Config Resources never import Node or SceneTree** — they are pure data
2. **Logic does not construct visual assets as shortcuts** — if a mesh could be authored in the editor, it should be a scene
3. **Building blocks are always PackedScene or Resource references** — editor-authored, version-controlled
4. **RNG is always injected** — never use global randomness, always pass a seeded RandomNumberGenerator
5. **Output is data, not instances** — generators return Arrays/Dictionaries, the consumer handles instantiation
