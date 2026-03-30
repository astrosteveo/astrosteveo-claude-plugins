# Skill Testing Framework

A three-layer testing system for validating Claude skills. Tests run against real `claude -p` processes, observing actual skill behavior.

## Overview

| Layer | What It Tests | How It Works | Token Usage |
|---|---|---|---|
| 1: Structural | Schema validation, file structure, frontmatter, naming | In-process Python checks (no Claude) | None |
| 2: Trigger | Does the skill load for the right queries? | Spawns `claude -p`, observes `Skill` tool calls in stream-json | Lightweight (1 turn each) |
| 3: Behavioral | Does the skill produce correct output? | Spawns `claude -p` with more turns, evaluates assertions | Heavier (varies by `max_turns`) |

## Quick Start

### 1. Create TESTS.yaml in your skill folder

```yaml
version: 1
skill: your-skill-name

config:
  default_model: sonnet
  default_max_turns: 5

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

# Run tests in parallel (4 workers)
python scripts/run-tests.py /path/to/skill --parallel 4

# Flakiness detection (run 3 times)
python scripts/run-tests.py /path/to/skill --runs 3

# Save results for regression tracking
python scripts/run-tests.py /path/to/skill --save-results

# Compare against previous run
python scripts/run-tests.py /path/to/skill --compare latest
```

### 3. Run structural validator standalone

```bash
python scripts/validate-structure.py /path/to/skill
python scripts/validate-structure.py /path/to/skill --json
```

## TESTS.yaml Format

### Top-level fields

```yaml
version: 1                    # Schema version (required, must be 1)
skill: your-skill-name        # Must match the skill's name field (required)
```

### Config section

```yaml
config:
  default_model: sonnet        # Model alias or full ID
  default_max_turns: 5         # Max turns for behavioral tests
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

### Test isolation and file system assertions

Behavioral tests that include a `setup` block or file system assertions run in an isolated temp directory. The directory is automatically created before and cleaned up after each test.

```yaml
behavioral:
  - name: "creates output file"
    input: "Create a hello.txt file"
    setup:
      files:
        "existing.txt": "some content"   # Pre-create files
      git_init: true                     # Optional: init a git repo
      commit: true                       # Optional: commit initial files
    assertions:
      - type: file_exists
        value: "hello.txt"
      - type: file_contains
        value: "hello.txt"
        pattern: "hello|greeting"
      - type: directory_exists
        value: "output"
      - type: file_not_exists
        value: "temp.txt"
```

### Multi-turn conversation tests

Set `input` to a list of strings to test multi-turn conversations. Each message is sent after the previous turn completes, using session persistence.

```yaml
behavioral:
  - name: "multi-turn clarification"
    input:
      - "Create something"
      - "A Python web scraper"
      - "Yes, use requests library"
    max_turns: 5
    assertions:
      - type: tool_called
        value: "Write"
```

## Assertion Types

### Hard assertions (checked from stream data)

These are deterministic — checked directly against the `stream-json` output.

| Type | Value/Options | What it checks |
|---|---|---|
| `no_errors` | -- | No errors in output |
| `tool_called` | tool name | Specific tool was invoked |
| `skill_invoked` | skill name | Specific skill was triggered |
| `output_matches` | regex pattern | Response text matches pattern |
| `output_does_not_match` | regex pattern | Response text does NOT match pattern |
| `exit_success` | -- | Process exited successfully |
| `max_turns_ok` | -- | Completed within turn limit |
| `tool_sequence` | list of tool names | Tools invoked in this order (subsequence match) |
| `tool_call_count` | tool name, count, op | Tool invoked N times (op: eq/gte/lte) |
| `file_exists` | relative path | File exists in workdir (requires setup) |
| `file_not_exists` | relative path | File does NOT exist (requires setup) |
| `directory_exists` | relative path | Directory exists in workdir (requires setup) |
| `file_contains` | path + regex pattern | File contains matching text (requires setup) |

### Soft assertions (Claude-evaluated)

These spawn a separate `claude -p` evaluator pass with `--tools ""` to judge the output.

| Type | Value | What it checks |
|---|---|---|
| `asks_clarification` | -- | Claude asks for more info instead of guessing |
| `stays_in_scope` | -- | Doesn't act outside the skill's domain |
| `suggests_fix` | -- | Provides actionable remediation |
| `mentions_error` | keyword | Surfaces a specific error condition |
| `does_not_hallucinate_success` | -- | Doesn't claim success when action failed |
| `contains_step` | description | Output includes a specific workflow step |
| `follows_instructions` | -- | Follows the skill's documented workflow order |

Soft assertions default to advisory (warnings). Add `severity: error` to promote to hard failures:

```yaml
assertions:
  - type: stays_in_scope
    severity: error    # Now fails the suite instead of warning
```

## Schema Validation

Layer 1 includes automatic TESTS.yaml schema validation. It checks for:

- Required fields (`version`, `skill`)
- Type correctness of config values
- Unrecognized keys (flagged as warnings)
- Deprecated key names with migration instructions
- Structural correctness of behavioral tests and edge cases

### Migrating from old schema format

Some older TESTS.yaml files use deprecated key names. The validator will warn you with exact migration steps. Common renames:

| Old Key | New Key |
|---|---|
| `type` | `skill` (set to the skill name) |
| `config.model` | `config.default_model` |
| `config.max_turns` | `config.default_max_turns` |
| `tests.trigger.*` | `triggers.*` (top-level) |
| edge case `should_trigger: bool` | `expect: trigger` or `expect: no_trigger` |
| edge case `reason` | `note` |

## Token Usage

Layers 2 and 3 spawn headless `claude -p` processes, consuming tokens from your normal Claude Code session.

- **Layer 1** uses no tokens — pure Python checks
- **Layer 2** is lightweight — one turn per trigger test
- **Layer 3** is heavier — multiple turns per behavioral test, varies by `max_turns`
- Use `--model haiku` for lighter token usage during development
- Use `--dry-run` to preview the test plan before running
- Use `--parallel N` to run tests faster (same token usage, less wall time)

## Parallel Execution

Use `--parallel N` to run trigger and behavioral tests concurrently:

```bash
python scripts/run-tests.py /path/to/skill --parallel 4
```

Layer 2 (trigger) and Layer 3 (behavioral) tests are independent and safe to parallelize. Layer 1 (structural) always runs sequentially since it's in-process and fast.

## Flakiness Detection

Use `--runs N` to run the entire suite N times and get per-test stability metrics:

```bash
python scripts/run-tests.py /path/to/skill --runs 5
```

The flakiness report shows:
- Pass rate per test across all runs
- List of flaky tests (pass rate between 0% and 100%)
- Overall stability score

This is useful for identifying non-deterministic trigger or soft assertion failures.

## Regression Tracking

Save test results to track changes over time:

```bash
# Save results after a run
python scripts/run-tests.py /path/to/skill --save-results

# Compare against the most recent saved run
python scripts/run-tests.py /path/to/skill --compare latest

# Compare against a specific file
python scripts/run-tests.py /path/to/skill --compare /path/to/baseline.json
```

Results are saved to `skill-folder/test-results/` as timestamped JSON files. The comparison report shows regressions, improvements, new tests, and removed tests.

## JSON Report Structure

```json
{
  "skill_dir": "/path/to/skill",
  "skill_name": "your-skill",
  "timestamp": "2025-03-26T14:30:00",
  "summary": {
    "total": 30,
    "passed": 28,
    "errors": 1,
    "warnings": 1,
    "result": "FAIL",
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

When using `--runs N`, the report includes a `flakiness` key with per-test stability data. When using `--compare`, a `comparison` key is included with regression/improvement details.

## CLI Reference

| Flag | Description |
|---|---|
| `--json` | Output JSON only |
| `--layer N` | Run only layer 1, 2, or 3 |
| `--model MODEL` | Override model for test runs |
| `--dry-run` | Show plan without running |
| `--plugin-dir DIR` | Plugin directory (auto-detected if omitted) |
| `--parallel N` | Number of parallel test workers (default: 1) |
| `--runs N` | Run suite N times for flakiness detection (default: 1) |
| `--save-results` | Save results to test-results/ in the skill folder |
| `--compare BASELINE` | Compare results against a baseline file (path or 'latest') |

## Integration with Skill-Creator

The testing framework integrates into the skill-creator workflow:

- **Phase 1 (Discovery):** Use cases feed directly into trigger test cases
- **Phase 3 (Instructions):** A TESTS.yaml is auto-generated from the use cases
- **Phase 5 (Validation):** Run `python scripts/run-tests.py` as part of validation
- **Phase 6 (Next Steps):** Iterate on test failures to improve the skill
