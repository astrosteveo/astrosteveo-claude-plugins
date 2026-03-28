---
name: godot-dev
description: "Enforces proper Godot 4.x node-and-scene architecture so game structure is visible in the editor, not hidden in scripts. TRIGGER when: code imports or references .gd/.tscn/.tres files, project has a project.godot file, or user asks to build game objects, scenes, enemies, levels, spawning, loot, or procedural content in Godot. Also triggers on 'add an enemy', 'create a scene', 'write a GDScript', 'build a level', 'set up a spawner', 'make a player controller', 'help me with my Godot game', 'how should I structure this in Godot', or any Godot MCP tool usage. DO NOT trigger for non-Godot projects, general programming, or game development in other engines (Unity, Unreal, Pygame)."
compatibility: Requires Godot 4.x project. Godot MCP server recommended for editor integration.
metadata:
  author: astrosteveo
  version: 2.0.0
  mcp-server: godot-mcp
  category: game-development
  tags: [godot, gdscript, game-dev, procedural-generation, architecture]
---

# Godot Dev

Development guidance for Godot 4.x projects. The core goal: build games using Godot's node and scene system so the editor reflects the actual structure of the game. Scripts add behavior to nodes — they do not replace them.

## The Core Problem This Skill Solves

Claude's default behavior in Godot projects is to put everything in `.gd` scripts. Instead of creating nodes in the editor or via MCP, it writes scripts that programmatically construct the entire scene tree at runtime. The user opens their project and sees a barren scene tree — one node, one script, everything hidden inside code.

This is wrong. Godot's strength is its node and scene system. A game's structure should be visible, inspectable, and editable in the editor. Scripts add logic to nodes. They do not replace the scene tree.

### The Rule

**Build with nodes and scenes first. Add scripts for behavior.**

- When the user needs a game object, create it as nodes in a scene (`.tscn`), not as runtime code in a script
- When using MCP tools, use `godot-mcp:create_scene`, `godot-mcp:add_node`, etc. to build the scene tree — do not write a script that calls `add_child()` for everything
- The Godot editor's scene tree should reflect the game's actual structure
- A user should be able to open any `.tscn` file and see what it contains, select nodes, move them, inspect their properties

### What This Looks Like

**Wrong — everything hidden in a script:**
```
main.tscn
└── GameManager (Node)     ← one node, one script, everything else created at runtime
```

**Right — scene tree reflects the game:**
```
main.tscn
├── Player (CharacterBody3D)
│   ├── CollisionShape3D
│   ├── MeshInstance3D
│   ├── HealthComponent (Node)
│   └── Camera3D
├── Environment (Node3D)
│   ├── Ground (StaticBody3D)
│   ├── DirectionalLight3D
│   └── WorldEnvironment
├── EnemySpawner (Node3D)
└── HUD (CanvasLayer)
    ├── HealthBar (ProgressBar)
    └── ScoreLabel (Label)
```

## Architecture Principles

### Nodes for Structure, Scripts for Behavior, Resources for Data

| Godot Type | Role | Example |
|------------|------|---------|
| Node / Scene (.tscn) | Visible structure, composition, editor-editable | enemy.tscn, projectile.tscn, main_level.tscn |
| Script (.gd) | Behavior and logic attached to nodes | enemy_controller.gd, health_component.gd |
| Resource (.tres) | Pure data, serializable, shareable, inspector-editable | gear_data.tres, spawn_config.tres |

### Component Pattern Over Deep Inheritance

Reusable behaviors are Node-based components added as children, not deep inheritance trees.

```
enemy.tscn
├── EnemyController (CharacterBody3D)
│   ├── HealthComponent
│   ├── HitFlashComponent
│   ├── DamageNumberSpawner
│   ├── DropComponent
│   ├── CollisionShape3D
│   └── MeshInstance3D
```

Components connect to siblings via signals. To deal damage to anything: find its `HealthComponent` and call `take_damage()`. See `references/conventions.md` for the full component pattern.

### Signals for Decoupling

Nodes communicate through signals, not direct references. A component emits signals about what happened; the parent or siblings decide what to do.

### Groups for Cross-Cutting Queries

Use groups (`"player"`, `"enemies"`, `"zone_root"`) for runtime lookups across the tree. Access via `get_tree().get_first_node_in_group()` or `get_tree().get_nodes_in_group()`.

## GDScript Conventions

### Recommended for All Scripts

- **Static typing** — type your variables, parameters, and return values. GDScript's type system catches bugs at parse time and improves editor autocompletion. The official docs recommend it; use it as your default.
- **`@export` for tunable values** — gameplay numbers belong in the inspector, not hardcoded in scripts. This lets designers (and you) adjust values without editing code.

### Use Selectively, Not Everywhere

- **`@tool`** — makes a script run in the editor. Use it for editor plugins, custom Resource previews, and scripts that need to show something in the viewport at edit time. Do NOT put it on gameplay scripts (enemy AI, player controllers, game managers) — it can cause editor instability, unintended side effects, and performance drag. Guard editor-only code with `Engine.is_editor_hint()`.
- **`class_name`** — registers a global class. Use it on types you reference elsewhere (custom Resources, components used via `is` checks, classes used as type hints). Skip it on scripts that are only attached to one specific scene node — it pollutes the global namespace and clutters the "Add Node" dialog.

See `references/conventions.md` for the complete convention set with examples.

## Data-Driven Design with Resources

When game content needs configuration or variation — enemy stats, loot tables, spawn rules, zone definitions — use custom Resource subclasses. This is standard Godot practice, equivalent to Unity's ScriptableObjects.

### The Pattern

1. **Config Resource** — a Resource subclass with `@export` fields defining rules and parameters. Pure data, no side effects. Designers edit it in the inspector. Saved as `.tres` files.
2. **Logic** — a script (or static function) that reads the config and produces results. Takes a seeded `RandomNumberGenerator` when randomness is involved.
3. **Building blocks** — visual assets referenced by the config as `PackedScene` or `Resource` arrays. Editor-authored `.tscn` and `.tres` files.

### Example: Spawn Config

```gdscript
class_name SpawnConfig
extends Resource

## Enemy scenes to choose from (editor-authored .tscn files)
@export var enemy_scenes: Array[PackedScene] = []
@export var enemy_weights: Array[float] = []
@export var min_count: int = 3
@export var max_count: int = 8
@export var spawn_radius: float = 10.0
```

A spawner node holds a `SpawnConfig` export, reads the config at runtime, and instantiates the referenced scenes. The key: enemy visuals are existing `.tscn` scenes built in the editor, not meshes generated in code.

See `references/data-driven-resources.md` for detailed examples covering spawning, loot, and prop placement.

## Procedural Geometry

Godot provides `SurfaceTool`, `ArrayMesh`, `ImmediateMesh`, and `MeshDataTool` for generating meshes in code. These are legitimate tools for:

- Voxel terrain (Minecraft-style worlds)
- Heightmap-based terrain generation
- Rope, chain, and cable physics visualization
- Trail and ribbon effects
- Dynamic water surfaces
- Navigation meshes for procedural levels
- Debug visualization

**When procedural geometry is appropriate:** the mesh itself needs to be algorithmic — its shape is computed, not authored.

**When it is NOT appropriate:** using `BoxMesh.new()` or `SphereMesh.new()` as lazy placeholders because creating a proper `.tscn` scene feels like more work. If an artist could author it, it should be a scene. If it must be computed, use the procedural geometry tools.

## MCP Workflow

When using Godot MCP tools for editor integration:

- Use MCP to **create nodes and build scene trees** — this is the primary workflow, not writing scripts that construct everything
- Always `godot-mcp:open_scene` before `godot-mcp:play_scene` — play runs the last-opened scene
- Set `global_position` after `add_child`, not before — node must be in tree
- Use `call_deferred()` for `add_child` during `_ready` to avoid "parent busy" errors
- After creating/modifying a script, reload via `script.reload()` + `EditorInterface.get_resource_filesystem().scan()`
- Use `godot-mcp:execute_editor_script` to set PackedScene exports on instanced scene nodes
- Use fully qualified tool names: `godot-mcp:create_scene`, `godot-mcp:add_node`, etc.

## Decision Framework

### "I need to build a game object"

1. **Create a scene** (`.tscn`) with the appropriate node types — use MCP or guide the user to create it in the editor
2. **Add child nodes** for collision, visuals, components
3. **Attach scripts** only for behavior that nodes need
4. **Export tunable values** so they are inspector-editable

### "I need content with variation"

1. Define a **Config Resource** — what are the parameters and rules?
2. Write **logic** that reads the config + a seeded RNG to produce deterministic results
3. **Visual building blocks** are editor-authored scenes and resources referenced by the config
4. Same config + same seed = same result

### "I need to add a system"

1. Is it data? **Resource subclass**, saved as `.tres`
2. Is it behavior? **Node-based component**, added as a child
3. Is it global state? **Autoload singleton** (use sparingly)
4. Does it need editor preview? **Add `@tool`** to that specific script
5. Does it need variation? **Data-driven Resource pattern**

### "I need procedural geometry"

1. Does the shape need to be computed algorithmically? **Use SurfaceTool/ArrayMesh**
2. Could an artist author this mesh instead? **Make it a `.tscn` scene**
3. Am I using `BoxMesh.new()` as a placeholder? **Stop. Create a scene instead.**

## Examples

### Example 1: User says "Add enemy spawning"

**Wrong:** Write a script that creates MeshInstance3D nodes with BoxMesh.new() at runtime.

**Right:**
1. Create enemy `.tscn` scenes in the editor with proper meshes, collision, and components
2. Create a `SpawnConfig` Resource with exported arrays for enemy scenes, weights, counts
3. Create a spawner node that reads the config and instantiates the enemy scenes
4. The scene tree shows the spawner; the enemies appear as instanced scenes at runtime

### Example 2: User says "Build a level"

**Wrong:** Write a script that programmatically creates StaticBody3D, MeshInstance3D, lights, etc.

**Right:**
1. Use MCP to create a level scene with nodes: ground, walls, lights, spawn points
2. Each element is a visible, selectable node in the scene tree
3. Scripts handle logic (door opening, trigger zones) — not scene construction
4. The user can open the scene and see the entire level layout

### Example 3: User says "I need a loot system"

**Wrong:** Hardcode drop rates and item stats in a script.

**Right:**
1. Create `GearData` Resource subclass with exported stats (damage, rarity, etc.)
2. Save individual items as `.tres` files — editable in the inspector
3. Create a `LootConfig` Resource with item pool references and drop weights
4. Loot logic reads the config + RNG seed — it defines no items itself

## Testing

Automate what you can. Hand off what you can't with clear playtest instructions.

- **Unit test** pure logic: damage calculations, state machines, inventory, Resource configs. Use GUT or GdUnit4.
- **Integration test** scenes: instantiate a scene, advance frames, assert on node state and signals.
- **Prompt the user for manual playtesting** when the thing being tested is feel, visuals, balance, AI behavior, or anything requiring human judgment. Give them specific things to check.
- **Simulated input is for verifying wiring, not gameplay.** Simulate a keypress to confirm "jump" makes the character leave the ground — that's an integration test. Do NOT simulate input to evaluate feel, balance, or combat. You cannot see the screen. Ask the user to playtest and give you feedback.

See `references/testing.md` for framework setup, test structure, CI patterns, and when to hand off to the user.

## Troubleshooting

**Scene tree is empty / everything is runtime-generated**
This is the core problem. Identify what was created in scripts and move it to scenes/nodes. Use MCP to build the scene tree. Scripts should reference nodes, not create them.

**"But I need things to spawn at runtime"**
Runtime instantiation is fine — `PackedScene.instantiate()` to spawn pre-authored scenes. The scene itself (the enemy, the projectile, the pickup) should be a `.tscn` file, not geometry assembled in code.

**"The user just wants a quick prototype"**
Even prototypes benefit from a visible scene tree. Create simple scenes with basic meshes in the editor. It takes seconds and the user can actually see and modify what they have.

**MCP tool errors**
- "Tool not found": Use fully qualified names (`godot-mcp:tool_name`)
- "Parent busy": Use `call_deferred()` for `add_child` in `_ready`
- Properties not updating: Reload script + scan filesystem after modifications

Read `references/anti-patterns.md` for a catalog of common mistakes and how to avoid them.
