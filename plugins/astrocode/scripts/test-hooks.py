#!/usr/bin/env python3
"""
Hook Test Runner — Deterministic testing for Claude Code plugin hooks.

Reads hooks/TESTS.yaml and runs each scenario in an isolated git repository,
asserting on exit codes, stdout/stderr content, file state, and git history.

No API calls, no LLM — pure filesystem + subprocess assertions.

Usage:
    python scripts/test-hooks.py                          # Run all hook tests
    python scripts/test-hooks.py --hook stop-gate         # Run tests for one hook
    python scripts/test-hooks.py --scenario no-changes    # Run a specific scenario
    python scripts/test-hooks.py --json                   # JSON output
    python scripts/test-hooks.py --dry-run                # Show plan without running
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_yaml_file(path):
    """Parse a YAML file using PyYAML."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if HAS_YAML:
        return yaml.safe_load(content)
    raise RuntimeError(
        "PyYAML is required. Install with: pip install pyyaml"
    )


# ── Result Type ──────────────────────────────────────────────────────

class TestResult:
    """A single test assertion result."""

    def __init__(self, name, passed, message="", severity="error",
                 duration_ms=0, details=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.severity = severity
        self.duration_ms = duration_ms
        self.details = details or {}

    def to_dict(self):
        d = {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }
        if self.duration_ms > 0:
            d["duration_ms"] = self.duration_ms
        if self.details:
            d["details"] = self.details
        return d


# ── Structural Validation ────────────────────────────────────────────

VALID_EVENTS = {
    "SessionStart", "InstructionsLoaded", "UserPromptSubmit",
    "PreToolUse", "PermissionRequest", "PostToolUse", "PostToolUseFailure",
    "Notification", "SubagentStart", "SubagentStop",
    "Stop", "StopFailure", "TeammateIdle", "TaskCompleted",
    "ConfigChange", "WorktreeCreate", "WorktreeRemove",
    "PreCompact", "PostCompact", "SessionEnd",
    "Elicitation", "ElicitationResult",
}

VALID_HOOK_TYPES = {"command", "http", "prompt", "agent"}


def run_structural_checks(plugin_dir, hooks_config):
    """Validate hooks.json schema and script availability."""
    results = []

    hooks_json_path = os.path.join(plugin_dir, "hooks", "hooks.json")
    exists = os.path.exists(hooks_json_path)
    results.append(TestResult(
        name="structural/hooks_json_exists",
        passed=exists,
        message="hooks.json exists" if exists else "hooks.json not found",
    ))
    if not exists:
        return results

    # Parse hooks.json
    try:
        with open(hooks_json_path) as f:
            hooks_json = json.load(f)
    except json.JSONDecodeError as e:
        results.append(TestResult(
            name="structural/hooks_json_valid",
            passed=False,
            message=f"Invalid JSON: {e}",
        ))
        return results

    results.append(TestResult(
        name="structural/hooks_json_valid",
        passed=True,
        message="hooks.json is valid JSON",
    ))

    # Top-level structure
    has_hooks_key = "hooks" in hooks_json
    results.append(TestResult(
        name="structural/has_hooks_key",
        passed=has_hooks_key,
        message="Has 'hooks' top-level key" if has_hooks_key
        else "Missing 'hooks' top-level key",
    ))
    if not has_hooks_key:
        return results

    # Validate each event and its matcher groups
    for event_name, matcher_groups in hooks_json["hooks"].items():
        results.append(TestResult(
            name=f"structural/valid_event:{event_name}",
            passed=event_name in VALID_EVENTS,
            message=f"'{event_name}' is a recognized hook event"
            if event_name in VALID_EVENTS
            else f"'{event_name}' is not a recognized hook event",
        ))

        if not isinstance(matcher_groups, list):
            results.append(TestResult(
                name=f"structural/matcher_groups_array:{event_name}",
                passed=False,
                message=f"'{event_name}' value must be an array",
            ))
            continue

        for i, group in enumerate(matcher_groups):
            if not isinstance(group, dict):
                results.append(TestResult(
                    name=f"structural/matcher_group_object:{event_name}[{i}]",
                    passed=False,
                    message="Matcher group must be an object",
                ))
                continue

            has_hooks = "hooks" in group and isinstance(group["hooks"], list)
            results.append(TestResult(
                name=f"structural/has_hooks_array:{event_name}[{i}]",
                passed=has_hooks,
                message="Matcher group has 'hooks' array"
                if has_hooks else "Missing or invalid 'hooks' array",
            ))
            if not has_hooks:
                continue

            for j, hook in enumerate(group["hooks"]):
                hook_type = hook.get("type")
                results.append(TestResult(
                    name=f"structural/valid_hook_type:{event_name}[{i}][{j}]",
                    passed=hook_type in VALID_HOOK_TYPES,
                    message=f"Hook type '{hook_type}' is valid"
                    if hook_type in VALID_HOOK_TYPES
                    else f"Invalid hook type: '{hook_type}'",
                ))

                if hook_type == "command":
                    has_cmd = bool(hook.get("command"))
                    results.append(TestResult(
                        name=f"structural/has_command:{event_name}[{i}][{j}]",
                        passed=has_cmd,
                        message="Command field present"
                        if has_cmd else "Missing 'command' field",
                    ))

    # Validate scripts referenced in TESTS.yaml
    scripts_dir = os.path.join(plugin_dir, "scripts")
    for hook_name, hook_data in hooks_config.items():
        script_file = hook_data.get("script", "")
        script_path = os.path.join(scripts_dir, script_file)
        exists = os.path.exists(script_path)
        results.append(TestResult(
            name=f"structural/script_exists:{hook_name}",
            passed=exists,
            message=f"Script '{script_file}' exists"
            if exists else f"Script '{script_file}' not found",
        ))

        if exists:
            try:
                proc = subprocess.run(
                    ["bash", "-n", script_path],
                    capture_output=True, text=True, timeout=5,
                )
                results.append(TestResult(
                    name=f"structural/script_parseable:{hook_name}",
                    passed=proc.returncode == 0,
                    message="Script has valid bash syntax"
                    if proc.returncode == 0
                    else f"Syntax error: {proc.stderr.strip()}",
                ))
            except Exception as e:
                results.append(TestResult(
                    name=f"structural/script_parseable:{hook_name}",
                    passed=False,
                    message=f"Could not check syntax: {e}",
                ))

    return results


# ── Scenario Setup ───────────────────────────────────────────────────

def setup_scenario(workdir, setup):
    """Prepare an isolated test environment from the scenario spec."""
    if setup.get("git_init", False):
        subprocess.run(["git", "init", "-q"], cwd=workdir, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@hook-test.local"],
            cwd=workdir, check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Hook Test"],
            cwd=workdir, check=True,
        )

    # Create initial files
    for filepath, content in setup.get("files", {}).items():
        full_path = os.path.join(workdir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    # Commit initial state
    if setup.get("commit", False):
        subprocess.run(["git", "add", "-A"], cwd=workdir, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "initial commit"],
            cwd=workdir, check=True,
        )

    # Post-commit modifications to tracked files
    for filepath, content in setup.get("modifications", {}).items():
        full_path = os.path.join(workdir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    # New untracked files added after commit
    for filepath, content in setup.get("new_files", {}).items():
        full_path = os.path.join(workdir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)


# ── Hook Execution ───────────────────────────────────────────────────

def run_hook_script(script_path, workdir, timeout=30):
    """Execute a hook script in the given working directory."""
    try:
        proc = subprocess.run(
            ["bash", script_path],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Script timed out", -1


# ── Assertion Checking ───────────────────────────────────────────────

def check_assertions(workdir, stdout, stderr, exit_code, expect):
    """Evaluate all assertions for a scenario. Returns list of TestResults."""
    results = []

    # ── Exit code ──
    if "exit_code" in expect:
        expected = expect["exit_code"]
        passed = exit_code == expected
        results.append(TestResult(
            name="exit_code",
            passed=passed,
            message=f"exit {exit_code}" + ("" if passed else f" (expected {expected})"),
        ))

    # ── stdout assertions ──
    for s in expect.get("stdout_contains", []):
        found = s in stdout
        results.append(TestResult(
            name=f"stdout_contains:{_trunc(s)}",
            passed=found,
            message="found in stdout" if found else "not found in stdout",
        ))

    for s in expect.get("stdout_not_contains", []):
        found = s in stdout
        results.append(TestResult(
            name=f"stdout_not_contains:{_trunc(s)}",
            passed=not found,
            message="absent from stdout" if not found
            else "unexpectedly found in stdout",
        ))

    # ── stderr assertions ──
    for s in expect.get("stderr_contains", []):
        found = s in stderr
        results.append(TestResult(
            name=f"stderr_contains:{_trunc(s)}",
            passed=found,
            message="found in stderr" if found else "not found in stderr",
        ))

    for s in expect.get("stderr_not_contains", []):
        found = s in stderr
        results.append(TestResult(
            name=f"stderr_not_contains:{_trunc(s)}",
            passed=not found,
            message="absent from stderr" if not found
            else "unexpectedly found in stderr",
        ))

    # ── File existence ──
    for filepath in expect.get("file_exists", []):
        exists = os.path.exists(os.path.join(workdir, filepath))
        results.append(TestResult(
            name=f"file_exists:{filepath}",
            passed=exists,
            message=f"{filepath} exists" if exists else f"{filepath} not found",
        ))

    for filepath in expect.get("file_not_exists", []):
        exists = os.path.exists(os.path.join(workdir, filepath))
        results.append(TestResult(
            name=f"file_not_exists:{filepath}",
            passed=not exists,
            message=f"{filepath} absent" if not exists
            else f"{filepath} unexpectedly exists",
        ))

    # ── File content ──
    for filepath, patterns in expect.get("file_contains", {}).items():
        content = _read_file(workdir, filepath)
        for p in patterns:
            if content is None:
                results.append(TestResult(
                    name=f"file_contains:{filepath}:{_trunc(p)}",
                    passed=False,
                    message=f"{filepath} does not exist",
                ))
            else:
                found = p in content
                results.append(TestResult(
                    name=f"file_contains:{filepath}:{_trunc(p)}",
                    passed=found,
                    message=f"found in {filepath}" if found
                    else f"not found in {filepath}",
                ))

    for filepath, patterns in expect.get("file_not_contains", {}).items():
        content = _read_file(workdir, filepath)
        for p in patterns:
            if content is None:
                results.append(TestResult(
                    name=f"file_not_contains:{filepath}:{_trunc(p)}",
                    passed=True,
                    message=f"{filepath} absent (pattern trivially absent)",
                ))
            else:
                found = p in content
                results.append(TestResult(
                    name=f"file_not_contains:{filepath}:{_trunc(p)}",
                    passed=not found,
                    message=f"absent from {filepath}" if not found
                    else f"unexpectedly found in {filepath}",
                ))

    # ── Git log ──
    git_log = _git_log(workdir)

    for s in expect.get("git_log_contains", []):
        found = s in git_log
        results.append(TestResult(
            name=f"git_log_contains:{_trunc(s)}",
            passed=found,
            message="found in git log" if found else "not found in git log",
        ))

    for s in expect.get("git_log_not_contains", []):
        found = s in git_log
        results.append(TestResult(
            name=f"git_log_not_contains:{_trunc(s)}",
            passed=not found,
            message="absent from git log" if not found
            else "unexpectedly found in git log",
        ))

    # ── Working tree clean ──
    if "working_tree_clean" in expect:
        is_clean = _working_tree_clean(workdir)
        expected_clean = expect["working_tree_clean"]
        passed = is_clean == expected_clean
        results.append(TestResult(
            name="working_tree_clean",
            passed=passed,
            message=f"working tree {'clean' if is_clean else 'dirty'}"
            + ("" if passed else f" (expected {'clean' if expected_clean else 'dirty'})"),
        ))

    return results


def _trunc(s, maxlen=50):
    """Truncate a string for display."""
    return s[:maxlen] + "..." if len(s) > maxlen else s


def _read_file(workdir, filepath):
    """Read a file's content, returning None if it doesn't exist."""
    full_path = os.path.join(workdir, filepath)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r") as f:
        return f.read()


def _git_log(workdir):
    """Get git log output, empty string if not a git repo."""
    try:
        proc = subprocess.run(
            ["git", "log", "--oneline", "-20"],
            cwd=workdir, capture_output=True, text=True, timeout=5,
        )
        return proc.stdout if proc.returncode == 0 else ""
    except Exception:
        return ""


def _working_tree_clean(workdir):
    """Check if the git working tree is clean."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=workdir, capture_output=True, text=True, timeout=5,
        )
        return proc.returncode == 0 and proc.stdout.strip() == ""
    except Exception:
        return False


# ── Scenario Runner ──────────────────────────────────────────────────

def run_scenario(hook_name, scenario, script_path, verbose=False):
    """Run a single scenario in an isolated temp directory."""
    name = scenario["name"]
    setup = scenario.get("setup", {})
    expect = scenario.get("expect", {})

    start = time.time()
    workdir = tempfile.mkdtemp(prefix=f"hook-test-{hook_name}-")

    try:
        setup_scenario(workdir, setup)
        stdout, stderr, exit_code = run_hook_script(script_path, workdir)
        assertion_results = check_assertions(
            workdir, stdout, stderr, exit_code, expect,
        )

        if verbose:
            for r in assertion_results:
                if not r.passed:
                    r.details["stdout"] = stdout[:500] if stdout else ""
                    r.details["stderr"] = stderr[:500] if stderr else ""
                    break  # Attach to first failure only

    except Exception as e:
        assertion_results = [TestResult(
            name="setup",
            passed=False,
            message=f"Scenario setup failed: {e}",
        )]
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    elapsed = int((time.time() - start) * 1000)

    # Prefix all result names with hook/scenario
    for r in assertion_results:
        r.name = f"{hook_name}/{name}/{r.name}"
        r.duration_ms = 0
    if assertion_results:
        assertion_results[0].duration_ms = elapsed

    return assertion_results


# ── Report ───────────────────────────────────────────────────────────

def generate_report(all_results, hooks_tested):
    """Generate a structured test report."""
    errors = [r for r in all_results if not r.passed and r.severity == "error"]
    warnings = [r for r in all_results if not r.passed and r.severity == "warning"]
    passed = [r for r in all_results if r.passed]
    total_duration = sum(r.duration_ms for r in all_results)

    hook_summary = {}
    for hook_name in hooks_tested:
        hook_results = [r for r in all_results if r.name.startswith(f"{hook_name}/")]
        hook_errors = [r for r in hook_results
                       if not r.passed and r.severity == "error"]
        hook_warnings = [r for r in hook_results
                         if not r.passed and r.severity == "warning"]
        hook_summary[hook_name] = {
            "total": len(hook_results),
            "passed": len([r for r in hook_results if r.passed]),
            "errors": len(hook_errors),
            "warnings": len(hook_warnings),
            "result": "PASS" if len(hook_errors) == 0 else "FAIL",
        }

    return {
        "type": "hooks",
        "summary": {
            "total": len(all_results),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "result": "PASS" if len(errors) == 0 else "FAIL",
            "total_duration_ms": total_duration,
        },
        "hooks": hook_summary,
        "results": [r.to_dict() for r in all_results],
    }


def print_report(report):
    """Print a human-readable test report."""
    s = report["summary"]
    print(f"\n{'=' * 70}")
    print(f"  Hook Test Report: {s['result']}")
    print(f"{'=' * 70}")
    print(f"  {s['passed']}/{s['total']} assertions passed  |  "
          f"{s['errors']} errors  |  {s['warnings']} warnings")
    print(f"  Duration: {s['total_duration_ms']}ms\n")

    for hook_name, data in report.get("hooks", {}).items():
        icon = "PASS" if data["result"] == "PASS" else "FAIL"
        print(f"  [{icon}] {hook_name}: "
              f"{data['passed']}/{data['total']} passed"
              f"  ({data['errors']} errors, {data['warnings']} warnings)")
    print()

    failures = [r for r in report["results"] if not r["passed"]]
    if failures:
        print("  FAILURES:")
        for r in failures:
            icon = "FAIL" if r["severity"] == "error" else "WARN"
            print(f"    [{icon}] {r['name']}")
            print(f"           {r['message']}")
            if r.get("details", {}).get("stdout"):
                print(f"           stdout: {r['details']['stdout'][:200]}")
            if r.get("details", {}).get("stderr"):
                print(f"           stderr: {r['details']['stderr'][:200]}")
        print()

    if s["result"] == "PASS":
        print(f"  All hook tests passed.\n")
    else:
        print(f"  {s['errors']} error(s) must be fixed.\n")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run hook tests from TESTS.yaml",
    )
    parser.add_argument(
        "--hook", help="Run tests for a specific hook only",
    )
    parser.add_argument(
        "--scenario", help="Run a specific scenario only",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON report",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show plan without running",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show stdout/stderr for failed scenarios",
    )
    parser.add_argument(
        "--tests", help="Path to TESTS.yaml (auto-detected if omitted)",
    )
    args = parser.parse_args()

    # Locate plugin root from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(script_dir)

    # Find TESTS.yaml
    if args.tests:
        tests_path = os.path.abspath(args.tests)
    else:
        tests_path = os.path.join(plugin_dir, "hooks", "TESTS.yaml")

    if not os.path.exists(tests_path):
        print(f"ERROR: TESTS.yaml not found at {tests_path}", file=sys.stderr)
        sys.exit(1)

    config = parse_yaml_file(tests_path)
    hooks_config = config.get("hooks", {})

    # Filter by --hook
    if args.hook:
        if args.hook not in hooks_config:
            print(
                f"ERROR: Hook '{args.hook}' not found. "
                f"Available: {', '.join(hooks_config.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        hooks_config = {args.hook: hooks_config[args.hook]}

    # Dry run
    if args.dry_run:
        total = 0
        for hook_name, hook_data in hooks_config.items():
            scenarios = hook_data.get("scenarios", [])
            if args.scenario:
                scenarios = [s for s in scenarios if s["name"] == args.scenario]
            print(f"  {hook_name} ({hook_data.get('script', '?')}): "
                  f"{len(scenarios)} scenarios")
            for s in scenarios:
                print(f"    - {s['name']}: {s.get('description', '')}")
            total += len(scenarios)
        print(f"\n  Total: {total} scenarios (+ structural checks)")
        return

    # ── Run structural checks ──
    all_results = []
    hooks_tested = ["structural"]

    if not args.json:
        print("  Running structural checks...")
    structural_results = run_structural_checks(plugin_dir, hooks_config)
    all_results.extend(structural_results)
    structural_pass = all(r.passed for r in structural_results)
    if not args.json:
        icon = "PASS" if structural_pass else "FAIL"
        print(f"    [{icon}] {len([r for r in structural_results if r.passed])}"
              f"/{len(structural_results)} checks passed\n")

    # ── Run scenario tests ──
    scripts_dir = os.path.join(plugin_dir, "scripts")

    for hook_name, hook_data in hooks_config.items():
        script_file = hook_data.get("script", "")
        script_path = os.path.join(scripts_dir, script_file)

        if not os.path.exists(script_path):
            all_results.append(TestResult(
                name=f"{hook_name}/script_missing",
                passed=False,
                message=f"Script not found: {script_path}",
            ))
            hooks_tested.append(hook_name)
            continue

        scenarios = hook_data.get("scenarios", [])
        if args.scenario:
            scenarios = [s for s in scenarios if s["name"] == args.scenario]

        if not args.json:
            print(f"  Testing {hook_name} ({len(scenarios)} scenarios)...")

        for scenario in scenarios:
            results = run_scenario(
                hook_name, scenario, script_path, verbose=args.verbose,
            )
            all_results.extend(results)

            if not args.json:
                scenario_pass = all(r.passed for r in results)
                icon = "PASS" if scenario_pass else "FAIL"
                print(f"    [{icon}] {scenario['name']}")

        if not args.json:
            print()

        hooks_tested.append(hook_name)

    # ── Report ──
    report = generate_report(all_results, hooks_tested)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    sys.exit(0 if report["summary"]["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
