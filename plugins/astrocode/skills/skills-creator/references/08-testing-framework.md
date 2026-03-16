# Skill Testing Framework

A three-layer testing system for validating Claude skills. Tests run against real `claude -p` processes, observing actual skill behavior.

## Overview

| Layer | What It Tests | How It Works | Cost |
|---|---|---|---|
| 1: Structural | File structure, frontmatter, naming | In-process Python checks (no Claude) | Free |
| 2: Trigger | Does the skill load for the right queries? | Spawns `claude -p`, observes `Skill` tool calls in stream-json | ~$0.01/test |
| 3: Behavioral | Does the skill produce correct output? | Spawns `claude -p` with more turns, evaluates assertions | ~$0.10/test |

## Quick Start

### 1. Create TESTS.yaml in your skill folder

```yaml
version: 1
skill: your-skill-name

config:
  default_model: sonnet
  max_budget_per_test: 0.25
  max_budget_total: 3.00

triggers:
  should_trigger:
    - "query that should invoke your skill"
  should_not_trigger:
    - "unrelated query"

behavioral: []
```

See `templates/TESTS.yaml` for a complete template with all options.

### 2. Run tests

```bash
# Full suite (all layers)
python scripts/run-tests.py /path/to/skill

# Structural only (free, instant)
python scripts/run-tests.py /path/to/skill --layer 1

# Trigger tests only
python scripts/run-tests.py /path/to/skill --layer 2

# Dry run (show plan without executing)
python scripts/run-tests.py /path/to/skill --dry-run

# JSON output for CI/automation
python scripts/run-tests.py /path/to/skill --json

# Override model
python scripts/run-tests.py /path/to/skill --model haiku
```

### 3. Run structural validator standalone

```bash
python scripts/validate-structure.py /path/to/skill
python scripts/validate-structure.py /path/to/skill --json
```

## TESTS.yaml Format

### Top-level fields

```yaml
version: 1                    # Schema version
skill: your-skill-name        # Must match the skill's name field
```

### Config section

```yaml
config:
  default_model: sonnet        # Model alias or full ID
  default_max_turns: 5         # Max turns for behavioral tests
  max_budget_per_test: 0.50    # USD limit per test case
  max_budget_total: 5.00       # USD limit for entire suite
  permission_mode: bypassPermissions
```

### Structural overrides

```yaml
structural:
  max_lines: 500               # Override max line count
  required_references:          # Upgrade missing refs from warning to error
    - references/api-guide.md
  required_scripts:
    - scripts/validate.py
```

### Trigger tests

```yaml
triggers:
  should_trigger:
    - "create a new project"
    - "set up my workspace"

  should_not_trigger:
    - "what's the weather"
    - "review this PR"

  edge_cases:
    - query: "plan my project tasks"
      expect: trigger           # or: no_trigger
      note: "Near the trigger boundary"
```

**How trigger detection works:** Each query spawns `claude -p "query" --output-format stream-json --verbose --max-turns 1`. The stream is parsed for `tool_use` blocks where `name == "Skill"` and the skill name matches. No self-evaluation — we observe real Claude behavior.

### Behavioral tests

```yaml
behavioral:
  - name: "happy path"
    input: "Create a project called TestApp"
    max_turns: 5
    assertions:
      - type: no_errors
      - type: tool_called
        value: "Bash"
      - type: output_matches
        pattern: "project.*created"
      - type: asks_clarification

  - name: "error handling"
    input: "Do the thing"
    max_turns: 3
    assertions:
      - type: asks_clarification
      - type: no_errors
```

## Assertion Types

### Hard assertions (checked from stream data)

These are deterministic — checked directly against the `stream-json` output.

| Type | Value | What it checks |
|---|---|---|
| `no_errors` | — | No errors in output |
| `tool_called` | tool name | Specific tool was invoked |
| `skill_invoked` | skill name | Specific skill was triggered |
| `output_matches` | regex pattern | Response text matches pattern |
| `exit_success` | — | Process exited successfully |
| `max_turns_ok` | — | Completed within turn limit |

### Soft assertions (Claude-evaluated)

These spawn a separate `claude -p` evaluator pass with `--tools ""` to judge the output.

| Type | Value | What it checks |
|---|---|---|
| `asks_clarification` | — | Claude asks for more info instead of guessing |
| `stays_in_scope` | — | Doesn't act outside the skill's domain |
| `suggests_fix` | — | Provides actionable remediation |
| `mentions_error` | keyword | Surfaces a specific error condition |
| `does_not_hallucinate_success` | — | Doesn't claim success when action failed |
| `contains_step` | description | Output includes a specific workflow step |
| `follows_instructions` | — | Follows the skill's documented workflow order |

Soft assertions are advisory (warnings, not errors) since Claude's output is non-deterministic.

## Cost Management

- **Layer 1** is free — no Claude invocations
- **Layer 2** costs ~$0.01-0.02 per trigger test (1 turn each)
- **Layer 3** costs vary by `max_turns` and response length
- Use `--model haiku` for cheaper test runs during development
- Set `max_budget_per_test` and `max_budget_total` to cap spending
- Use `--dry-run` to see estimated costs before running

## JSON Report Structure

```json
{
  "skill_dir": "/path/to/skill",
  "skill_name": "your-skill",
  "summary": {
    "total": 30,
    "passed": 28,
    "errors": 1,
    "warnings": 1,
    "result": "FAIL",
    "total_cost_usd": 0.15,
    "total_duration_ms": 45000
  },
  "layers": {
    "layer1": { "total": 20, "passed": 20, "errors": 0, "warnings": 0, "result": "PASS" },
    "layer2": { "total": 8, "passed": 7, "errors": 1, "warnings": 0, "result": "FAIL" },
    "layer3": { "total": 2, "passed": 1, "errors": 0, "warnings": 1, "result": "PASS" }
  },
  "results": [...]
}
```

## Integration with Skills-Creator

The testing framework integrates into the skills-creator workflow:

- **Phase 1 (Discovery):** Use cases feed directly into trigger test cases
- **Phase 3 (Instructions):** A TESTS.yaml is auto-generated from the use cases
- **Phase 5 (Validation):** Run `python scripts/run-tests.py` as part of validation
- **Phase 6 (Next Steps):** Iterate on test failures to improve the skill
