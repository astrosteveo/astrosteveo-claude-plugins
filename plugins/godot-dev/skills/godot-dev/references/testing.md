# Testing in Godot 4.x

Godot has no built-in test framework. Testing is third-party. The ecosystem is functional but immature compared to web/backend — there is no code coverage for GDScript, and many things in game development require human playtesting. This guide covers what you can automate, how to set it up, and when to hand off to the user.

## Frameworks

Two real options:

**GUT (Godot Unit Test)** — https://github.com/bitwes/Gut
- The most widely used. GDScript only.
- Install via AssetLib or Git submodule under `addons/gut/`.
- Tests extend `GutTest`. Methods prefixed with `test_`.
- Supports assertions, signal watching, doubles/stubs, async waits, parameterized tests.
- In-editor panel and command-line runner.

**GdUnit4** — https://github.com/MikeSchulze/gdUnit4
- Newer, built specifically for Godot 4.x. Supports GDScript and C#.
- Scene runners for integration tests (advance frames, simulate input).
- Fluent assertion API, mocking/spying, fuzz testing.
- JUnit XML output with GitHub Actions integration.
- Growing in adoption; recommended for new 4.x projects.

Pick one. Both work. GdUnit4 has better scene testing; GUT has more community tutorials.

## What to Automate

### Unit Tests — Pure Logic

Test anything that is data in, data out with no scene tree dependency:

```gdscript
# GUT example
extends GutTest

func test_damage_calculation() -> void:
    var base_damage: int = 10
    var multiplier: float = 1.5
    var result: int = DamageCalculator.calculate(base_damage, multiplier)
    assert_eq(result, 15)

func test_loot_config_deterministic() -> void:
    var config := LootConfig.new()
    config.min_drops = 2
    config.max_drops = 2

    var rng := RandomNumberGenerator.new()
    rng.seed = 12345
    var drops_a: Array = LootGenerator.generate(config, rng)

    rng.seed = 12345
    var drops_b: Array = LootGenerator.generate(config, rng)

    assert_eq(drops_a.size(), drops_b.size())
```

Good candidates for unit tests:
- Damage/health calculations
- State machine transitions
- Inventory add/remove/check logic
- Config Resource validation
- Data-driven generators (same seed = same output)
- Pathfinding algorithms
- Save/load serialization

### Integration Tests — Scenes and Components

Test that nodes work together in a scene:

```gdscript
# GdUnit4 scene runner example
extends GdUnitTestSuite

func test_health_component_emits_died() -> void:
    var scene: Node = auto_free(load("res://scenes/enemy/enemy.tscn").instantiate())
    add_child(scene)

    var health: HealthComponent = scene.find_child("HealthComponent")
    assert_that(health).is_not_null()

    # Monitor the signal
    monitor_signals(health)

    # Deal lethal damage
    health.take_damage(health.max_health)

    # Assert signal was emitted
    assert_signal(health).is_emitted("died")
    assert_eq(health.current_health, 0)
```

```gdscript
# GUT equivalent
extends GutTest

func test_health_component_emits_died() -> void:
    var scene: Node = load("res://scenes/enemy/enemy.tscn").instantiate()
    add_child_autofree(scene)

    var health: HealthComponent = scene.find_child("HealthComponent")
    watch_signals(health)

    health.take_damage(health.max_health)

    assert_signal_emitted(health, "died")
```

Good candidates for integration tests:
- Component signal wiring (HealthComponent emits `died`, parent responds)
- Scene instantiation (scene loads without errors, required nodes exist)
- Spawner systems (config + seed produces expected number of instances)
- UI updates in response to game state changes

### Signal Tests

Signals are Godot's primary decoupling mechanism. Test them:

```gdscript
func test_inventory_emits_on_add() -> void:
    var inventory := Inventory.new()
    add_child_autofree(inventory)
    watch_signals(inventory)

    inventory.add_material(&"wood", 5)

    assert_signal_emitted_with_parameters(
        inventory, "material_changed", [&"wood", 5]
    )
```

### Static Analysis

GDScript has no standard linter, but you can catch issues with:
- `godot --headless --check-only` — parse-check all scripts without running
- Static typing catches type errors at parse time (another reason to use it)
- GdUnit4 can validate scene integrity (required nodes exist, exports are set)

## What You Cannot Automate

These require human judgment. When you reach one of these, **stop and ask the user to playtest.** Do not try to test these yourself.

### Simulated Input: When to Use It and When to Stop

Simulated keypresses and input actions are a legitimate testing tool — for verifying **wiring and mechanics**, not for evaluating **feel and gameplay**.

**Use simulated input to verify wiring:**
- Does pressing "jump" make the character leave the ground? (CharacterBody3D.velocity.y changed)
- Does pressing "attack" trigger the attack state and fire the `attack_started` signal?
- Does the pause menu open when "ui_cancel" is pressed?
- Does movement input produce velocity in the correct direction?

These are integration tests. They confirm that input bindings, state transitions, and node connections work. The answer is binary — it works or it doesn't.

**Do NOT use simulated input to evaluate gameplay:**
- Do not simulate a combat encounter to see if it "works" — you cannot see the screen
- Do not simulate movement to judge if it "feels responsive"
- Do not chain attack inputs to test if rate of fire "feels right"
- Do not simulate a full playthrough of a level

**The line:**
- "Does pressing X cause Y to happen?" — simulate it, assert the result
- "Does X feel good when the player does it?" — stop, ask the user to playtest

**Example — attack rate change:**
You've changed the attack cooldown from 0.5s to 0.3s.
- Automate: simulate an attack input, assert the cooldown timer is set to 0.3s, assert a second attack within 0.3s is blocked. This confirms the mechanic works.
- Hand off: "I've updated the attack cooldown to 0.3s and verified the mechanic works in tests. Play a combat encounter and let me know if the fire rate feels right — I can adjust further based on your feedback."

### What Requires Playtesting

**Physics and movement feel:**
- Does character movement feel responsive?
- Does the jump arc feel natural?
- Do collisions resolve correctly in edge cases (corners, slopes, fast movement)?

**Combat and gameplay feel:**
- Does attack speed / rate of fire feel right?
- Is hit feedback satisfying (screen shake, knockback, VFX)?
- Do weapon/ability timings feel punchy or sluggish?

**Visual quality:**
- Do materials and lighting look correct?
- Are there visual artifacts, z-fighting, or seams?
- Does the UI layout work at different resolutions?

**AI behavior:**
- Does the enemy feel challenging but fair?
- Does the AI get stuck on geometry?
- Are engagement distances and patrol routes reasonable?

**Balance and progression:**
- Are difficulty curves appropriate?
- Are loot drop rates satisfying?
- Is progression pacing right?

**Audio:**
- Do sounds play at the right time and at balanced volumes?
- Does audio feel appropriate for the action?

## How to Hand Off to the User

When you've done what you can programmatically, prompt the user with specific playtest instructions:

**Example handoff:**
```
I've added the enemy spawning system and written automated tests for:
- SpawnConfig produces correct enemy counts (test_spawn_count)
- Same seed produces same spawn layout (test_spawn_deterministic)
- HealthComponent signals work correctly (test_enemy_takes_damage)

Please playtest the following manually:
1. Run the zone_01 scene and trigger a spawn wave
2. Check: Do enemies appear at reasonable positions? (not inside walls, not stacked)
3. Check: Does the difficulty curve feel right across waves 1-5?
4. Check: Do enemy death animations and loot drops look correct?
5. Try edge cases: trigger multiple waves rapidly, leave and re-enter the zone
```

Be specific. "Test the spawning" is useless. "Trigger a wave, check enemies aren't spawning inside walls" is actionable.

## Test Directory Structure

```
project/
├── addons/
│   └── gut/ or gdUnit4/
├── test/
│   ├── unit/
│   │   ├── test_damage_calculator.gd
│   │   ├── test_inventory.gd
│   │   ├── test_loot_generator.gd
│   │   └── test_spawn_generator.gd
│   ├── integration/
│   │   ├── test_enemy_scene.gd
│   │   ├── test_health_component.gd
│   │   └── test_spawner.gd
│   └── .gutconfig.json or gdunit4.cfg
```

## CI/CD

### GitHub Actions with GUT

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    container: barichello/godot-ci:4.3
    steps:
      - uses: actions/checkout@v4
      - name: Import assets
        run: godot --headless --import
      - name: Run tests
        run: godot --headless --script addons/gut/gut_cmdln.gd -gexit
```

### GitHub Actions with GdUnit4

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    container: barichello/godot-ci:4.3
    steps:
      - uses: actions/checkout@v4
      - name: Import assets
        run: godot --headless --import
      - name: Run tests
        run: godot --headless --script addons/gdUnit4/runtest.gd --path . -gexit
```

GdUnit4 produces JUnit XML that integrates with GitHub's test summary UI.

## Known Limitations

- **No code coverage for GDScript.** The engine does not expose line-level execution tracing. This is a genuine ecosystem gap.
- **Physics tests can be flaky.** Frame timing sensitivity means physics assertions need tolerances. Use `assert_almost_eq()` or `is_equal_approx()`.
- **Scene tests require asset import.** CI pipelines need a `godot --headless --import` step before tests can load scenes.
- **`--headless` mode quirks.** Some rendering-adjacent code may behave differently in headless mode.
- **No visual regression testing.** No Percy/Chromatic equivalent for Godot. Visual quality is manual.

## Summary

| What | How | Automated? |
|------|-----|-----------|
| Logic (math, state, data) | Unit tests (GUT/GdUnit4) | Yes |
| Components and signals | Integration tests with scene runner | Yes |
| Scene integrity | Load scene, assert nodes exist | Yes |
| Script syntax | `godot --headless --check-only` | Yes |
| Deterministic generation | Same seed = same output assertions | Yes |
| Physics feel | User playtests | No — prompt user |
| Visual quality | User playtests | No — prompt user |
| AI behavior | User playtests | No — prompt user |
| Gameplay balance | User playtests | No — prompt user |
| Audio | User playtests | No — prompt user |
