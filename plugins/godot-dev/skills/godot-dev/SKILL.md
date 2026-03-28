---
name: godot-dev
description: >
  Guides all Godot 4.x development with engine conventions, architecture patterns,
  and the Recipe-Generator pattern for scalable procedural content. Use when working
  in a Godot project, writing GDScript, creating scenes or nodes, building procedural
  generation systems, designing game architecture, or using Godot MCP tools. Triggers
  on "create a scene", "add a node", "build a system", "generate terrain", "loot tables",
  "enemy waves", "procedural", "GDScript", "Godot", or any .gd/.tscn/.tres file work.
  Do NOT use for non-Godot projects or general programming unrelated to game development.
compatibility: Requires Godot 4.x project. Godot MCP server recommended for editor integration.
metadata:
  author: astrosteveo
  version: 1.0.0
  mcp-server: godot-mcp
  category: game-development
  tags: [godot, gdscript, game-dev, procedural-generation, architecture]
---

# Godot Dev

Comprehensive development guidance for Godot 4.x projects. Enforces engine conventions, idiomatic architecture, and the Recipe-Generator pattern for all procedural content.

## Non-Negotiable Rules

These rules are absolute. No exceptions. No shortcuts.

### 1. NEVER Create Visual Assets in Code

No `new()` calls for meshes, materials, textures, shaders, or any visual resource. NEVER.

- No `BoxMesh.new()`, `SphereMesh.new()`, `PlaneMesh.new()`
- No `StandardMaterial3D.new()` with hardcoded colors
- No `ShaderMaterial.new()` with inline shader code
- No `Gradient.new()`, `GradientTexture2D.new()`
- No `SurfaceTool` or `ImmediateMesh` for permanent geometry

Visual assets MUST be editor-created `.tscn` scenes or `.tres` resources, visible in the inspector, authored by a human or imported from external tools.

**The only exception:** Truly transient runtime visuals (debug draws, temporary indicators) that are never part of the shipped game's art.

### 2. All Procedural Content Uses the Recipe-Generator Pattern

When content needs variation, build a **system**, not a script that spits out random stuff. See `references/recipe-pattern.md` for the full pattern.

- **Recipe** = A Resource defining rules, parameters, and constraints (pure data, no logic)
- **Generator** = A system that reads Recipes and produces deterministic output
- Same Recipe + same seed = same result, every time
- All Recipe parameters are `@export`ed, designer-facing, inspector-editable

### 3. All Scripts Follow Conventions

Every GDScript file must have:
- `@tool` — editor visibility is required
- `class_name` — for type safety and editor integration
- Full static typing — variables, parameters, return types, no exceptions
- `@export` for all tunable values — zero hardcoded gameplay numbers

See `references/conventions.md` for the complete convention set.

### 4. No Code-Generated Assets Means NO CODE-GENERATED ASSETS

This is worth repeating because it is the most commonly violated rule.

A script's job is **logic**. An asset's job is **visuals**. These do not cross. If you need a mesh, material, particle system, or any visual element — it is a `.tscn` or `.tres` file created in the editor. Period.

Read `references/anti-patterns.md` for a catalog of what NOT to do and why.

## Architecture Principles

### Resources for Data, Nodes for Behavior, Scenes for Composition

| Godot Type | Role | Example |
|------------|------|---------|
| Resource | Pure data container, serializable, shareable | GearData, ZoneData, SpawnRecipe |
| Node | Behavior, logic, lifecycle hooks | EnemyController, HealthComponent |
| Scene (.tscn) | Composition of nodes + resources, editor-visible | enemy.tscn, projectile.tscn |

### Component Pattern Over Inheritance

Reusable behaviors are Node-based components added as children, not deep inheritance trees.

```
enemy.tscn
├── EnemyController (CharacterBody3D)
│   ├── HealthComponent
│   ├── HitFlashComponent
│   ├── DamageNumberSpawner
│   ├── DropComponent
│   └── MeshInstance3D (visual — authored in editor)
```

Components auto-connect to siblings via signals. To deal damage to anything: find its `HealthComponent` and call `take_damage()`.

### Signals for Decoupling

Nodes communicate through signals, not direct references. A component emits signals about what happened; the parent or siblings decide what to do about it.

### Groups for Cross-Cutting Queries

Use groups (`"player"`, `"enemies"`, `"zone_root"`) for runtime lookups across the tree. Access via `get_tree().get_first_node_in_group()` or `get_tree().get_nodes_in_group()`.

## The Recipe-Generator Pattern (Overview)

When you need procedural variation — enemy waves, loot drops, terrain features, prop placement, anything — build a Recipe-Generator system.

### Recipe (Resource)

```gdscript
@tool
class_name SpawnRecipe
extends Resource

@export var enemy_scenes: Array[PackedScene] = []
@export var enemy_weights: Array[float] = []
@export var min_count: int = 3
@export var max_count: int = 8
@export var spawn_radius: float = 10.0
@export var difficulty_curve: Curve
```

Recipes are **pure data**. No methods that produce side effects. Designers edit them in the inspector. They live as `.tres` files in `resources/`.

### Generator (Node or Static Class)

```gdscript
@tool
class_name SpawnGenerator
extends RefCounted

static func generate(recipe: SpawnRecipe, rng: RandomNumberGenerator) -> Array[SpawnEntry]:
    var count := rng.randi_range(recipe.min_count, recipe.max_count)
    var entries: Array[SpawnEntry] = []
    for i in count:
        var scene := _weighted_pick(recipe.enemy_scenes, recipe.enemy_weights, rng)
        var angle := rng.randf() * TAU
        var dist := rng.randf() * recipe.spawn_radius
        var pos := Vector3(cos(angle) * dist, 0, sin(angle) * dist)
        entries.append(SpawnEntry.new(scene, pos))
    return entries
```

Generators take a Recipe + RNG seed and produce deterministic results. Same inputs = same outputs.

See `references/recipe-pattern.md` for detailed examples covering terrain, loot, props, VFX, and more.

## MCP Workflow

When using Godot MCP tools for editor integration:

- Always `godot-mcp:open_scene` before `godot-mcp:play_scene` — play runs the last-opened scene
- Set `global_position` after `add_child`, not before — node must be in tree
- Use `call_deferred()` for `add_child` during `_ready` to avoid "parent busy" errors
- After creating/modifying a script, reload via `script.reload()` + `EditorInterface.get_resource_filesystem().scan()`
- Use `godot-mcp:execute_editor_script` to set PackedScene exports on instanced scene nodes
- Use fully qualified tool names: `godot-mcp:create_scene`, `godot-mcp:add_node`, etc.

## Decision Framework

### "I need a visual element"

1. Does it already exist as a `.tscn` or `.tres`? **Use it.**
2. Can it be created in the Godot editor? **Create it there.**
3. Does it need variation? **Build a Recipe Resource that defines the rules, a Generator that reads the recipe, and `.tscn`/`.tres` templates for the visual building blocks.**
4. Is it a debug/dev-only visual? **Only then may code create it, clearly marked as debug.**

### "I need procedural content"

1. Define the **Recipe** — what are the rules, parameters, constraints?
2. Build the **Generator** — deterministic function from Recipe + seed to output
3. Create the **visual building blocks** as editor assets (`.tscn` scenes, `.tres` resources)
4. The Generator references and composes the building blocks — it never creates them

### "I need to add a system"

1. Is it data? **Resource subclass.**
2. Is it behavior? **Node-based component.**
3. Is it global state? **Autoload singleton.**
4. Does it need editor visibility? **`@tool` (which is all scripts).**
5. Does it need variation? **Recipe-Generator pattern.**

## Examples

### Example 1: User says "Add enemy spawning"

**Wrong approach:** A script that calls `BoxMesh.new()` to make placeholder enemies with random colors.

**Right approach:**
1. Create `SpawnRecipe` Resource with `@export` arrays for enemy scenes, weights, counts, radius
2. Create `SpawnGenerator` static class that reads the recipe + RNG seed
3. Enemy visuals are existing `.tscn` scenes authored in the editor
4. Spawner node holds a `SpawnRecipe` export, calls Generator at runtime

### Example 2: User says "I need terrain generation"

**Wrong approach:** A script that creates `PlaneMesh.new()` and `StandardMaterial3D.new()` with random green/brown colors.

**Right approach:**
1. Create `TerrainRecipe` Resource: biome rules, height curve, texture assignments
2. Create `TerrainGenerator` that reads the recipe + seed, outputs placement data
3. Visual terrain tiles/chunks are `.tscn` scenes with proper meshes and materials made in the editor
4. Generator selects and places the right tiles based on recipe rules

### Example 3: User says "Build a loot system"

**Wrong approach:** A script with hardcoded drop rates and item stats scattered through the code.

**Right approach:**
1. Create `LootRecipe` Resource: rarity weights, item pool references, quantity ranges
2. Create `LootGenerator` that rolls against the recipe + RNG seed
3. Item definitions are `GearData` Resources (`.tres` files) with exported stats
4. Generator picks from the pool — it defines no items itself

## Troubleshooting

**"But I need a quick placeholder mesh"**
No. Create a simple `.tscn` with a basic mesh in the editor. It takes 30 seconds and it scales. A code-generated mesh is technical debt from the moment it's written.

**"The Recipe pattern seems like overkill for this"**
If the content needs any variation at all, it's not overkill — it's the minimum viable approach. If it truly needs zero variation, it should be a static `.tscn` scene. Either way, code doesn't create assets.

**"I need to generate geometry at runtime"**
Then you need a Generator that composes pre-authored mesh building blocks (`.tres` MeshLibrary entries, `.tscn` chunk scenes). The Generator arranges them — it doesn't model them.

**MCP tool errors**
- "Tool not found": Use fully qualified names (`godot-mcp:tool_name`)
- "Parent busy": Use `call_deferred()` for `add_child` in `_ready`
- Properties not updating: Reload script + scan filesystem after modifications
