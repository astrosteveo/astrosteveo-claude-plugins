# Anti-Patterns: What NOT To Do

Every pattern below is something that has been done wrong, repeatedly, by AI assistants and developers taking shortcuts. Each one produces code that is ugly, fragile, unscalable, and a pain to maintain. Do not do any of these. Ever.

## 1. Code-Generated Meshes

**The violation:**
```gdscript
# NEVER DO THIS
var mesh := BoxMesh.new()
mesh.size = Vector3(2, 1, 2)
var mesh_instance := MeshInstance3D.new()
mesh_instance.mesh = mesh
add_child(mesh_instance)
```

**Why it's terrible:**
- Invisible in the editor — you can't see it, select it, or tweak it without running the game
- No artist can touch it — it's buried in code
- Doesn't scale — want 10 variations? Now you have 10 code blocks generating slightly different boxes
- Looks bad — procedurally assembled geometry with no artistic intent is obvious placeholder forever

**What to do instead:**
Create a `.tscn` scene in the editor with the mesh. Reference it as a `PackedScene` export. Instantiate it at runtime if needed.

## 2. Code-Generated Materials

**The violation:**
```gdscript
# NEVER DO THIS
var mat := StandardMaterial3D.new()
mat.albedo_color = Color(0.2, 0.6, 0.3)
mat.metallic = 0.5
mat.roughness = 0.8
mesh_instance.material_override = mat
```

**Why it's terrible:**
- Materials are visual art — they need to be authored visually, not numerically in code
- Can't preview in editor, can't iterate on the look without changing code and re-running
- Color values like `Color(0.2, 0.6, 0.3)` are meaningless — is that grass? Jade? Mold? Who knows.
- Every material becomes a unique snowflake, no reuse, no consistency

**What to do instead:**
Create `.tres` material resources in the editor. Assign them to meshes in `.tscn` scenes. If you need variation, use a Recipe with material references.

## 3. Hardcoded Gameplay Values

**The violation:**
```gdscript
# NEVER DO THIS
var speed := 5.0
var health := 100
var damage := 25
var spawn_rate := 2.5
```

**Why it's terrible:**
- Can't tune without code changes
- Different values scattered across different scripts with no central reference
- Can't expose to designers or even to yourself in the inspector
- Makes balancing a nightmare

**What to do instead:**
```gdscript
# ALWAYS DO THIS
@export var speed: float = 5.0
@export var max_health: int = 100
@export var damage: int = 25
@export var spawn_interval: float = 2.5
```

Every tunable value is `@export`. No exceptions.

## 4. Static Procedural Generation

**The violation:**
```gdscript
# NEVER DO THIS — "procedural" that's really just random static junk
func _ready() -> void:
    for i in 20:
        var rock := MeshInstance3D.new()
        var mesh := SphereMesh.new()
        mesh.radius = randf_range(0.3, 1.5)
        rock.mesh = mesh
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color(randf_range(0.3, 0.5), randf_range(0.3, 0.5), randf_range(0.3, 0.5))
        rock.material_override = mat
        rock.position = Vector3(randf_range(-10, 10), 0, randf_range(-10, 10))
        add_child(rock)
```

**Why it's terrible:**
- This is the worst of all worlds: code-generated meshes AND materials AND randomness with no system
- Not reproducible — different every run, can't debug specific layouts
- Not tunable — want fewer rocks? Bigger rocks? Different distribution? Change code.
- Looks terrible — random spheres with random gray-brown colors is not "rocks"
- Doesn't scale — want rocks AND trees AND debris? Copy-paste this mess three times?

**What to do instead:**
1. Author rock `.tscn` scenes in the editor (with actual rock meshes and materials)
2. Create a `PropScatterRecipe` Resource with density, spacing, and scene references
3. Build a `PropScatterGenerator` that reads the Recipe + seed
4. Instantiate the editor-authored rock scenes at the generated positions

## 5. Inline Shader Code

**The violation:**
```gdscript
# NEVER DO THIS
var shader := Shader.new()
shader.code = """
shader_type spatial;
void fragment() {
    ALBEDO = vec3(0.5, 0.8, 0.3);
}
"""
var shader_mat := ShaderMaterial.new()
shader_mat.shader = shader
```

**Why it's terrible:**
- Shader code in a GDScript string — no syntax highlighting, no editor preview, no error checking until runtime
- Can't iterate on the visual in the editor
- Shader parameters aren't exposed to the inspector

**What to do instead:**
Write shaders as `.gdshader` files. Create `ShaderMaterial` resources (`.tres`) in the editor that reference the shader. Assign materials to meshes in scenes.

## 6. God Scripts

**The violation:**
A single script that handles movement, health, damage, spawning, UI updates, and sound effects.

**Why it's terrible:**
- Can't reuse any single behavior
- Can't test anything in isolation
- Every change risks breaking unrelated functionality
- Multiple systems coupled through shared state

**What to do instead:**
Component pattern. Each behavior is its own Node script. Components communicate through signals. A 500-line god script becomes five 80-line components that are individually testable and reusable.

## 7. Deep Inheritance Trees

**The violation:**
```
Entity
  └── LivingEntity
        └── Combatant
              └── Enemy
                    └── RangedEnemy
                          └── BossRangedEnemy
```

**Why it's terrible:**
- Fragile base class problem — changing `Combatant` breaks everything below it
- Can't mix behaviors — what if you want a non-combat LivingEntity?
- Godot's node system is designed for composition, not deep inheritance

**What to do instead:**
Flat hierarchy with components:
```
CharacterBody3D (with EnemyController script)
  ├── HealthComponent
  ├── DamageComponent
  ├── AIComponent
  └── MeshInstance3D
```

## 8. Global Randomness

**The violation:**
```gdscript
# NEVER DO THIS
var count := randi_range(3, 8)
var pos := Vector3(randf() * 10, 0, randf() * 10)
```

**Why it's terrible:**
- Not reproducible — can't recreate the same generation with a seed
- Can't test — output is different every run
- Global random state is shared — other systems calling `randf()` affect your results

**What to do instead:**
```gdscript
# ALWAYS DO THIS
var rng := RandomNumberGenerator.new()
rng.seed = hash(seed_value)
var count := rng.randi_range(3, 8)
var pos := Vector3(rng.randf() * 10, 0, rng.randf() * 10)
```

Always inject a seeded `RandomNumberGenerator`. Same seed = same results.

## 9. Missing @tool

**The violation:**
```gdscript
class_name MyComponent
extends Node3D
# No @tool — invisible in editor
```

**Why it's terrible:**
- Script doesn't run in the editor — `@export` values don't trigger visual updates
- Can't preview behavior or see component state in the editor
- Editor tools and MCP integration can't interact with the script

**What to do instead:**
Every script starts with `@tool`. Always.

## 10. Missing class_name

**The violation:**
```gdscript
@tool
extends Node3D
# No class_name — anonymous script
```

**Why it's terrible:**
- Can't reference the type in other scripts
- No type safety — `var enemy: Node3D` instead of `var enemy: EnemyController`
- Doesn't appear in the editor's "Add Node" dialog
- Can't use `is` type checking

**What to do instead:**
Every script has `class_name`. Always. The name should match the script's filename in PascalCase.

## 11. Untyped Code

**The violation:**
```gdscript
var speed = 5.0
var enemies = []

func take_damage(amount):
    health -= amount
```

**Why it's terrible:**
- No editor autocompletion
- Runtime type errors instead of editor-time errors
- Ambiguous intent — is `enemies` an `Array[Node3D]`? `Array[Enemy]`? Who knows.

**What to do instead:**
```gdscript
var speed: float = 5.0
var enemies: Array[EnemyController] = []

func take_damage(amount: int) -> void:
    health -= amount
```

Type everything. Variables, parameters, return types. No exceptions.

## The Pattern

Notice that every anti-pattern shares the same root causes:
1. **Shortcuts** — doing the quick thing instead of the right thing
2. **Code doing art's job** — scripts creating visual assets instead of referencing authored ones
3. **Missing structure** — no systems, no patterns, just ad-hoc code
4. **No editor integration** — invisible to the inspector, untweakable without code changes

The Recipe-Generator pattern and Godot conventions exist specifically to prevent all of these. Follow them.
