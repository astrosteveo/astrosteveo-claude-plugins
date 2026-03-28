# Godot 4.x Development Conventions

Complete reference for GDScript conventions, scene architecture, and project organization patterns.

## Script Header

A GDScript file typically starts with these elements in this order:

```gdscript
@tool                    # Only if this script needs to run in the editor
class_name MyClassName   # Only if this type is referenced elsewhere
extends BaseType

## Brief description of what this script does.
```

1. `@tool` (optional) — only for scripts that need editor execution (see When to Use @tool below)
2. `class_name` (optional) — PascalCase, matches the filename (e.g., `enemy_controller.gd` -> `EnemyController`). Only needed when the type is referenced elsewhere.
3. `extends` — the base type
4. Doc comment — single `##` line describing purpose

## When to Use @tool

`@tool` makes a script execute inside the Godot editor. This is powerful but carries risk — bugs in `@tool` scripts can crash the editor, corrupt scene data, or cause unintended side effects.

**Use `@tool` for:**
- Editor plugins and addons (custom docks, inspectors, importers)
- Custom Resource subclasses that need inspector previews
- Level design tools that show results in the viewport
- Scripts with `@export` properties that need visual editor feedback

**Do NOT use `@tool` for:**
- Player controllers, enemy AI, game managers
- Gameplay logic, combat systems, inventory management
- Anything that spawns nodes, modifies global state, or runs `_process()` loops

When a script needs both editor and runtime behavior, guard runtime code:

```gdscript
@tool
extends Node3D

func _ready() -> void:
    if Engine.is_editor_hint():
        # Editor-only setup (e.g., preview gizmo)
        return
    # Gameplay setup here
```

## When to Use class_name

`class_name` registers a global class — it appears in the "Add Node" dialog and is accessible from every script. GDScript has no namespaces, so every `class_name` occupies the global scope.

**Use `class_name` for:**
- Custom Resource types (GearData, SpawnConfig, LootConfig)
- Reusable components referenced by type (`var health: HealthComponent`)
- Types used in `is` checks or typed arrays (`Array[EnemyController]`)
- Autoload singletons

**Skip `class_name` for:**
- Scripts attached to a single specific scene node and never referenced by name
- One-off scripts that don't need type checking
- Scripts in addons where generic names could clash with user code

## Type System

### Static Typing

GDScript is gradually typed — static typing is optional but strongly recommended. It catches errors at parse time, improves autocompletion, and produces faster bytecode.

```gdscript
# Explicitly typed
var speed: float = 5.0
var max_health: int = 100
var direction: Vector3 = Vector3.ZERO
var enemies: Array[EnemyController] = []
var target: Node3D = null

# Inferred with := (fine when the type is obvious)
var rng := RandomNumberGenerator.new()
var count := enemies.size()
```

### Parameters and Return Types

```gdscript
func take_damage(amount: int, source: Node3D) -> void:
    pass

func get_nearest_enemy(position: Vector3) -> EnemyController:
    return null

func calculate_damage(base: int, multiplier: float) -> int:
    return roundi(base * multiplier)
```

### Constants and Enums

```gdscript
const MAX_LEVEL: int = 50
const GRAVITY: float = 9.8

enum State { IDLE, CHASE, ATTACK, DEAD }
var current_state: State = State.IDLE
```

## Export Variables

### Basic Exports

All tunable gameplay values should be `@export` — editable in the inspector without code changes.

```gdscript
@export var move_speed: float = 5.0
@export var max_health: int = 100
@export var attack_damage: int = 25
@export var attack_range: float = 2.0
```

### Export Groups

```gdscript
@export_group("Movement")
@export var move_speed: float = 5.0
@export var acceleration: float = 10.0
@export var friction: float = 8.0

@export_group("Combat")
@export var attack_damage: int = 25
@export var attack_range: float = 2.0
```

### Resource and Scene Exports

```gdscript
# Reference editor-authored assets
@export var projectile_scene: PackedScene
@export var death_effect: PackedScene
@export var gear_data: GearData
@export var spawn_config: SpawnConfig

# Arrays of assets
@export var enemy_scenes: Array[PackedScene] = []
@export var loot_pool: Array[GearData] = []
```

### Export Hints

```gdscript
@export_range(0.0, 100.0, 0.1) var health_percent: float = 100.0
@export_range(1, 10) var difficulty_level: int = 1
@export_enum("Melee", "Ranged", "Support") var enemy_type: int = 0
@export_file("*.tscn") var scene_path: String
@export_multiline var description: String
```

## Signals

### Declaration and Emission

```gdscript
# Signals declare what happened, not what should happen next
signal damage_taken(amount: int)
signal health_changed(new_health: int, max_health: int)
signal died

func take_damage(amount: int) -> void:
    current_health -= amount
    damage_taken.emit(amount)
    health_changed.emit(current_health, max_health)
    if current_health <= 0:
        died.emit()
```

### Connection

```gdscript
# Prefer code connections in _ready for clarity
func _ready() -> void:
    health_component.damage_taken.connect(_on_damage_taken)
    health_component.died.connect(_on_died)
```

### Auto-Connection Pattern for Components

Components that need sibling references find them in `_ready`:

```gdscript
func _ready() -> void:
    var health: HealthComponent = _find_sibling(HealthComponent)
    if health:
        health.damage_taken.connect(_on_damage_taken)

func _find_sibling(type: Variant) -> Node:
    for sibling in get_parent().get_children():
        if is_instance_of(sibling, type):
            return sibling
    return null
```

## Resource Subclasses

### Data Resources

```gdscript
class_name GearData
extends Resource

@export var item_name: String = ""
@export_enum("Weapon", "Armor", "Accessory") var slot: int = 0
@export_range(0, 3) var rarity: int = 0
@export var damage_bonus: int = 0
@export var max_health_bonus: int = 0
```

Resources are saved as `.tres` files in `resources/` subdirectories. They are pure data — no side effects, no scene tree access. Use `class_name` on Resources so they appear in the "Create Resource" dialog.

## Node Organization

### Scene Tree Structure

```
game.tscn (persistent root)
├── Player (CharacterBody3D)
│   ├── HealthComponent
│   ├── MeshInstance3D
│   └── CollisionShape3D
├── Camera3D
├── HUD (CanvasLayer)
│   ├── HealthBar
│   └── ScoreLabel
├── ZoneManager
│   └── [loaded zone scene]
└── DeathOverlay (CanvasLayer)
```

The scene tree should reflect the game's structure. Every significant element is a node, visible and selectable in the editor.

### Component Pattern

Reusable behaviors are self-contained Node scripts added as children:

```gdscript
class_name HealthComponent
extends Node

signal damage_taken(amount: int)
signal health_changed(current: int, maximum: int)
signal died

@export var max_health: int = 100
var current_health: int

func _ready() -> void:
    current_health = max_health

func take_damage(amount: int) -> void:
    current_health = maxi(current_health - amount, 0)
    damage_taken.emit(amount)
    health_changed.emit(current_health, max_health)
    if current_health <= 0:
        died.emit()
```

Components are added as children in the scene editor. They find siblings and connect via signals in `_ready`.

## Groups

```gdscript
# Querying groups at runtime
var player: Node = get_tree().get_first_node_in_group("player")
var all_enemies: Array[Node] = get_tree().get_nodes_in_group("enemies")
```

Common groups: `"player"`, `"enemies"`, `"zone_root"`, `"zone_manager"`. Prefer adding nodes to groups in the editor rather than in code.

## Collision Layers

Define collision layers semantically and document them:

| Layer | Name | Used By |
|-------|------|---------|
| 1 | Environment | Ground, walls, static geometry |
| 2 | Player | Player CharacterBody3D |
| 3 | Enemy | Enemy CharacterBody3D |
| 4 | PlayerProjectile | Player's projectile Area3D |
| 5 | Pickup | Pickup Area3D |

Set collision layers and masks in the editor, not in code.

## State Machines

```gdscript
enum State { IDLE, CHASE, ATTACK, DEAD }

var current_state: State = State.IDLE

func _physics_process(delta: float) -> void:
    match current_state:
        State.IDLE:
            _process_idle(delta)
        State.CHASE:
            _process_chase(delta)
        State.ATTACK:
            _process_attack(delta)
        State.DEAD:
            pass
```

## Autoloads

Global singletons for truly cross-cutting concerns only (inventory, save data, game settings). Most systems should be node-based components.

```gdscript
class_name Inventory
extends Node

signal material_changed(material_name: StringName, new_amount: int)

var _materials: Dictionary = {}

func add_material(material_name: StringName, amount: int) -> void:
    _materials[material_name] = _materials.get(material_name, 0) + amount
    material_changed.emit(material_name, _materials[material_name])
```

## Project Organization

```
project/
├── scenes/
│   ├── player/          # Player scenes
│   ├── enemy/           # Enemy scenes
│   ├── combat/          # Projectiles, weapons
│   ├── effects/         # VFX scenes
│   ├── hud/             # UI panels
│   └── world/           # Levels, zones, environment
├── scripts/
│   ├── components/      # Reusable components
│   └── [mirrors scenes structure]
├── resources/
│   ├── configs/         # Config Resources (.tres)
│   ├── gear/            # Item data (.tres)
│   └── materials/       # Material resources (.tres)
├── shaders/             # .gdshader files
└── assets/              # Imported art, audio, fonts
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Scripts | snake_case.gd | `enemy_controller.gd` |
| Classes | PascalCase | `EnemyController` |
| Scenes | snake_case.tscn | `enemy_melee.tscn` |
| Resources | snake_case.tres | `spawn_config_zone1.tres` |
| Variables | snake_case | `move_speed` |
| Constants | UPPER_SNAKE_CASE | `MAX_HEALTH` |
| Signals | snake_case (past tense) | `damage_taken`, `died` |
| Enums | PascalCase | `State.IDLE` |
| Functions | snake_case | `take_damage()` |
| Private | _prefix | `_process_chase()` |
| Node paths | PascalCase in tree | `HealthComponent`, `MeshInstance3D` |

## Input Handling

Define input actions in Project Settings, reference by name:

```gdscript
func _physics_process(delta: float) -> void:
    var input_dir := Vector3.ZERO
    input_dir.x = Input.get_axis("move_left", "move_right")
    input_dir.z = Input.get_axis("move_forward", "move_back")

    if Input.is_action_just_pressed("attack"):
        _fire_projectile()
```

Never hardcode key codes. Always use input action names.
