# Godot 4.x Development Conventions

Complete reference for GDScript conventions, scene architecture, and project organization patterns.

## Script Header

Every GDScript file starts with these elements in this order:

```gdscript
@tool
class_name MyClassName
extends BaseType

## Brief description of what this script does.
```

1. `@tool` — always first line, no exceptions
2. `class_name` — PascalCase, matches the filename (e.g., `enemy_controller.gd` → `EnemyController`)
3. `extends` — the base type
4. Doc comment — single `##` line describing purpose

## Type System

### Variables

```gdscript
# Every variable has an explicit type
var speed: float = 5.0
var max_health: int = 100
var direction: Vector3 = Vector3.ZERO
var enemies: Array[EnemyController] = []
var items: Dictionary = {}  # Dictionary typing available in 4.4+
var target: Node3D = null
```

### Parameters and Return Types

```gdscript
# Every function has typed parameters and return type
func take_damage(amount: int, source: Node3D) -> void:
    pass

func get_nearest_enemy(position: Vector3) -> EnemyController:
    return null

func calculate_damage(base: int, multiplier: float) -> int:
    return roundi(base * multiplier)
```

### Constants

```gdscript
# Constants for fixed values that never change
const MAX_LEVEL: int = 50
const GRAVITY: float = 9.8
const ITEM_CATEGORIES: Array[StringName] = [&"weapon", &"armor", &"accessory"]
```

### Enums

```gdscript
enum State { IDLE, CHASE, ATTACK, DEAD }

var current_state: State = State.IDLE
```

## Export Variables

### Basic Exports

```gdscript
# All tunable values are @export — zero hardcoded gameplay numbers
@export var move_speed: float = 5.0
@export var max_health: int = 100
@export var attack_damage: int = 25
@export var attack_range: float = 2.0
@export var attack_cooldown: float = 1.0
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
@export var attack_cooldown: float = 1.0

@export_group("Visuals")
@export var death_effect_scene: PackedScene
@export var hit_flash_duration: float = 0.1
```

### Resource and Scene Exports

```gdscript
# Reference to editor-authored assets
@export var projectile_scene: PackedScene
@export var death_effect: PackedScene
@export var gear_data: GearData
@export var spawn_recipe: SpawnRecipe

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
@export_dir var save_directory: String
@export_multiline var description: String
@export_color_no_alpha var base_color: Color
```

## Signals

### Declaration

```gdscript
# Signals declare what happened, not what should happen next
signal damage_taken(amount: int)
signal health_changed(new_health: int, max_health: int)
signal died
signal state_changed(old_state: State, new_state: State)
```

### Emission

```gdscript
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

### Auto-Connection Pattern

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
@tool
class_name GearData
extends Resource

@export var item_name: String = ""
@export_enum("Weapon", "Armor", "Accessory") var slot: int = 0
@export_range(0, 3) var rarity: int = 0
@export var damage_bonus: int = 0
@export var max_health_bonus: int = 0
@export var move_speed_bonus: float = 0.0
```

Resources are saved as `.tres` files in `resources/` subdirectories. They are pure data — no side effects, no scene tree access.

### Recipe Resources

See `references/recipe-pattern.md` for the full Recipe-Generator pattern. Recipes are a specialized form of data Resource that define generation rules.

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

### Component Pattern

Reusable behaviors are self-contained Node scripts:

```gdscript
@tool
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

Components are added as children in the scene editor. They auto-connect to siblings via signals in `_ready`.

## Groups

```gdscript
# Adding to groups (typically done in editor, not code)
add_to_group("player")
add_to_group("enemies")

# Querying groups
var player: Node = get_tree().get_first_node_in_group("player")
var all_enemies: Array[Node] = get_tree().get_nodes_in_group("enemies")
```

Common groups:
- `"player"` — the player node
- `"enemies"` — all enemy nodes
- `"zone_root"` — current zone's root (for adding runtime children that clean up on zone swap)
- `"zone_manager"` — the zone management node

## Collision Layers

Define collision layers semantically and document them:

| Layer | Name | Used By |
|-------|------|---------|
| 1 | Environment | Ground, walls, static geometry |
| 2 | Player | Player CharacterBody3D |
| 3 | Enemy | Enemy CharacterBody3D |
| 4 | PlayerProjectile | Player's projectile Area3D |
| 5 | Pickup | Pickup Area3D |
| 6 | EnemyProjectile | Enemy projectile Area3D |

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
            pass  # No processing when dead


func _change_state(new_state: State) -> void:
    var old_state: State = current_state
    current_state = new_state
    state_changed.emit(old_state, new_state)
```

## Autoloads

Global singletons for cross-cutting concerns:

```gdscript
@tool
class_name Inventory
extends Node

signal material_changed(material_name: StringName, new_amount: int)
signal inventory_cleared

var _materials: Dictionary = {}

func add_material(material_name: StringName, amount: int) -> void:
    _materials[material_name] = _materials.get(material_name, 0) + amount
    material_changed.emit(material_name, _materials[material_name])

func get_material_count(material_name: StringName) -> int:
    return _materials.get(material_name, 0)
```

Use autoloads sparingly — only for truly global state (inventory, save data, game settings). Most systems should be node-based components.

## Project Organization

```
project/
├── scenes/
│   ├── player/          # Player prefab
│   ├── enemy/           # Enemy prefabs
│   ├── combat/          # Projectiles, weapons
│   ├── effects/         # VFX scenes
│   ├── loot/            # Pickup, gear scenes
│   ├── hud/             # UI panels
│   └── world/           # Game root, zones, environment
│       ├── zones/       # Individual zone scenes
│       └── ruins/       # Environment building blocks
├── scripts/
│   ├── player/          # Player scripts
│   ├── enemy/           # Enemy AI scripts
│   ├── combat/          # Combat logic
│   ├── effects/         # VFX scripts
│   ├── loot/            # Loot/inventory scripts
│   ├── hud/             # UI scripts
│   ├── components/      # Reusable components
│   └── world/           # Zone system, game state
├── resources/
│   ├── zones/           # ZoneData .tres files
│   ├── materials/       # Material .tres files
│   ├── recipes/         # Recipe .tres files
│   └── gear/            # GearData .tres files
├── shaders/             # .gdshader files
└── assets/              # Imported art, audio, fonts
```

Scenes and scripts mirror each other. Resources are grouped by type. Shaders and imported assets have their own top-level directories.

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Scripts | snake_case.gd | `enemy_controller.gd` |
| Classes | PascalCase | `EnemyController` |
| Scenes | snake_case.tscn | `enemy_melee.tscn` |
| Resources | snake_case.tres | `spawn_recipe_zone1.tres` |
| Shaders | snake_case.gdshader | `dematerialize.gdshader` |
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
