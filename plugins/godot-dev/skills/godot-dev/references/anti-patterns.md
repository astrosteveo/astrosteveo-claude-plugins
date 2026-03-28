# Common Mistakes: What Claude Gets Wrong in Godot

These are patterns Claude defaults to when working in Godot projects. Every one of them hides game structure inside scripts instead of using Godot's node and scene system. Recognize them and redirect to the correct approach.

## 1. The Empty Scene Tree

**What Claude does:**
Creates a single node with a massive script that builds the entire game at runtime.

```
main.tscn
└── Game (Node)  ← one node, everything else is add_child() in code
```

The script calls `add_child()` dozens of times to create the player, enemies, environment, UI — all invisible in the editor.

**Why it's a problem:**
- The user opens the project and sees nothing
- Cannot select, move, or inspect anything in the editor
- Cannot use the inspector to tweak properties
- The entire game structure is locked inside code

**What to do instead:**
Build the scene tree with actual nodes — either in the editor or via Godot MCP tools. Every significant game element should be a node in the tree. Scripts add behavior to those nodes.

## 2. Script-Constructed Visuals

**What Claude does:**
```gdscript
# Creates geometry in code instead of using the editor
var mesh := BoxMesh.new()
mesh.size = Vector3(2, 1, 2)
var mesh_instance := MeshInstance3D.new()
mesh_instance.mesh = mesh
add_child(mesh_instance)
```

**Why it's a problem:**
- Invisible in the editor — you cannot see, select, or tweak it without running the game
- No artist or designer can touch it — it is buried in code
- Uses programmatic placeholders when a 30-second editor scene would be better
- Ten variations means ten code blocks generating slightly different boxes

**What to do instead:**
Create a `.tscn` scene in the editor with the mesh. Reference it as a `PackedScene` export. Instantiate it at runtime if needed.

**When code-generated geometry IS correct:** the mesh must be computed algorithmically (voxel terrain, heightmaps, ropes, trails, dynamic water). These are legitimate uses of `SurfaceTool`, `ArrayMesh`, and `ImmediateMesh`. The test: could an artist author this mesh? If yes, it should be a scene. If the shape is algorithmic, generate it in code.

## 3. Script-Constructed Materials

**What Claude does:**
```gdscript
var mat := StandardMaterial3D.new()
mat.albedo_color = Color(0.2, 0.6, 0.3)
mat.metallic = 0.5
mat.roughness = 0.8
mesh_instance.material_override = mat
```

**Why it's a problem:**
- Materials are visual — they need to be authored visually, not numerically
- Cannot preview in editor, cannot iterate without code changes
- `Color(0.2, 0.6, 0.3)` is meaningless — is that grass? Jade? No one knows.

**What to do instead:**
Create `.tres` material resources in the editor. Assign them to meshes in scenes. If you need variation, use a config Resource with material references.

## 4. Hardcoded Gameplay Values

**What Claude does:**
```gdscript
var speed := 5.0
var health := 100
var damage := 25
```

**Why it's a problem:**
- Cannot tune without code changes
- Scattered across scripts with no central reference
- Invisible to the inspector

**What to do instead:**
```gdscript
@export var speed: float = 5.0
@export var max_health: int = 100
@export var damage: int = 25
```

Every tunable value should be `@export`. Editable in the inspector.

## 5. Runtime Scene Construction Instead of MCP

**What Claude does:**
Writes a script that builds the entire scene tree programmatically:

```gdscript
func _ready() -> void:
    var ground := StaticBody3D.new()
    var ground_mesh := MeshInstance3D.new()
    ground_mesh.mesh = PlaneMesh.new()
    ground.add_child(ground_mesh)
    var ground_col := CollisionShape3D.new()
    ground_col.shape = WorldBoundaryShape3D.new()
    ground.add_child(ground_col)
    add_child(ground)

    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-45, 30, 0)
    add_child(light)
    # ... 50 more lines of this
```

**Why it's a problem:**
- This is literally what the Godot editor and MCP tools are for
- The scene tree shows nothing — all structure is hidden in `_ready()`
- Cannot rearrange, inspect, or tweak any of it without editing code
- Godot MCP can create these nodes directly in the editor

**What to do instead:**
Use `godot-mcp:create_scene`, `godot-mcp:add_node`, etc. to build the scene tree. Or guide the user to create it in the editor. The result is a `.tscn` file with real nodes.

## 6. Inline Shader Code

**What Claude does:**
```gdscript
var shader := Shader.new()
shader.code = """
shader_type spatial;
void fragment() {
    ALBEDO = vec3(0.5, 0.8, 0.3);
}
"""
```

**Why it's a problem:**
- No syntax highlighting, no editor preview, no error checking until runtime
- Shader parameters are not exposed to the inspector

**What to do instead:**
Write shaders as `.gdshader` files. Create `ShaderMaterial` resources (`.tres`) in the editor.

## 7. God Scripts

**What Claude does:**
A single script handling movement, health, damage, spawning, UI, and sound.

**Why it's a problem:**
- Cannot reuse any single behavior
- Cannot test in isolation
- Every change risks breaking unrelated functionality

**What to do instead:**
Component pattern. Each behavior is its own Node script added as a child. A 500-line god script becomes five 80-line components that are individually reusable.

## 8. Deep Inheritance Trees

**What Claude does:**
```
Entity -> LivingEntity -> Combatant -> Enemy -> RangedEnemy -> BossRangedEnemy
```

**Why it's a problem:**
- Fragile base class problem — changing `Combatant` breaks everything below
- Cannot mix behaviors
- Godot's node system is designed for composition

**What to do instead:**
Flat hierarchy with components:
```
CharacterBody3D (with EnemyController script)
├── HealthComponent
├── DamageComponent
├── AIComponent
└── MeshInstance3D
```

## 9. Global Randomness

**What Claude does:**
```gdscript
var count := randi_range(3, 8)
var pos := Vector3(randf() * 10, 0, randf() * 10)
```

**Why it's a problem:**
- Not reproducible — cannot recreate the same generation with a seed
- Global random state is shared — other systems affect your results

**What to do instead:**
```gdscript
var rng := RandomNumberGenerator.new()
rng.seed = hash(seed_value)
var count := rng.randi_range(3, 8)
```

Inject a seeded `RandomNumberGenerator` for any procedural content. Same seed = same results.

## The Common Thread

Every mistake above shares the same root cause: **Claude defaults to doing everything in scripts instead of using Godot's editor and node system.** The fix is always the same direction:

- Structure belongs in scenes and nodes, not in scripts
- Visual assets belong in the editor, not in code
- Data belongs in Resources, not hardcoded in scripts
- Use MCP tools to build scene trees, not `add_child()` chains
- Scripts add behavior — they do not replace the editor
