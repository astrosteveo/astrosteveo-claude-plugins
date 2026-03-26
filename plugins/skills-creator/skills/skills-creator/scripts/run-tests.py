#!/usr/bin/env python3
"""
Skill Test Runner — Layers 1, 2, and 3.

Reads TESTS.yaml from a skill directory and runs:
  Layer 1: Structural validation (in-process, no Claude needed)
  Layer 2: Trigger tests (spawns claude -p, observes skill invocation)
  Layer 3: Behavioral tests (spawns claude -p, evaluates output)

Usage:
    python run-tests.py /path/to/skill-folder
    python run-tests.py /path/to/skill-folder --json
    python run-tests.py /path/to/skill-folder --layer 2
    python run-tests.py /path/to/skill-folder --model haiku --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

# Import the structural validator from the same directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from importlib import import_module


def load_validate_structure():
    """Import validate-structure.py as a module."""
    spec_path = os.path.join(SCRIPT_DIR, "validate-structure.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("validate_structure", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_yaml_file(path):
    """Parse a YAML file, using PyYAML if available or a minimal parser."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if HAS_YAML:
        return yaml.safe_load(content)
    raise RuntimeError(
        "PyYAML is required for parsing TESTS.yaml. "
        "Install with: pip install pyyaml\n"
        "Or use the structural validator directly: python validate-structure.py /path/to/skill"
    )


# Result Types

class TestResult:
    """A single test result."""

    def __init__(self, name, layer, passed, message="", severity="error",
                 cost=0.0, duration_ms=0, details=None):
        self.name = name
        self.layer = layer
        self.passed = passed
        self.message = message
        self.severity = severity
        self.cost = cost
        self.duration_ms = duration_ms
        self.details = details or {}

    def to_dict(self):
        d = {
            "name": self.name,
            "layer": self.layer,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }
        if self.cost > 0:
            d["cost_usd"] = round(self.cost, 6)
        if self.duration_ms > 0:
            d["duration_ms"] = self.duration_ms
        if self.details:
            d["details"] = self.details
        return d


# Layer 1: Structural

def run_layer1(skill_dir, config):
    """Run structural validation checks."""
    vs = load_validate_structure()
    checks = vs.validate_skill(skill_dir)
    report = vs.generate_report(checks, skill_dir)

    results = []
    for check in report["checks"]:
        results.append(TestResult(
            name=f"structural/{check['name']}",
            layer=1,
            passed=check["passed"],
            message=check["message"],
            severity=check["severity"],
        ))

    # Check required_references from TESTS.yaml (upgrade to errors)
    structural_config = config.get("structural", {})
    required_refs = structural_config.get("required_references", [])
    for ref in required_refs:
        ref_path = os.path.join(skill_dir, ref)
        exists = os.path.exists(ref_path)
        results.append(TestResult(
            name=f"structural/required_ref:{ref}",
            layer=1,
            passed=exists,
            message=f"Required reference '{ref}' {'exists' if exists else 'is missing'}",
            severity="error",
        ))

    required_scripts = structural_config.get("required_scripts", [])
    for script in required_scripts:
        script_path = os.path.join(skill_dir, script)
        exists = os.path.exists(script_path)
        results.append(TestResult(
            name=f"structural/required_script:{script}",
            layer=1,
            passed=exists,
            message=f"Required script '{script}' {'exists' if exists else 'is missing'}",
            severity="error",
        ))

    return results


def detect_plugin_dir(skill_dir):
    """Walk up from skill_dir to find the plugin root (.claude-plugin/plugin.json)."""
    current = os.path.abspath(skill_dir)
    while True:
        candidate = os.path.join(current, ".claude-plugin", "plugin.json")
        if os.path.isfile(candidate):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


# Layer 2: Trigger Tests

def run_claude_p(prompt, output_format="stream-json", max_turns=1,
                 model=None, max_budget=None, extra_flags=None):
    """Spawn a claude -p process and return parsed output."""
    cmd = ["claude", "-p", prompt, "--output-format", output_format,
           "--no-session-persistence", "--permission-mode", "bypassPermissions"]

    if output_format == "stream-json":
        cmd.append("--verbose")

    if max_turns:
        cmd.extend(["--max-turns", str(max_turns)])
    if model:
        cmd.extend(["--model", model])
    if max_budget:
        cmd.extend(["--max-budget-usd", str(max_budget)])
    if extra_flags:
        cmd.extend(extra_flags)

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Process timed out after 120s", -1
    except FileNotFoundError:
        return "", "claude CLI not found. Is Claude Code installed?", -2


def parse_stream_json(output):
    """Parse stream-json output into structured events."""
    events = {"init": None, "assistant_messages": [], "tool_calls": [],
              "result": None, "skills_loaded": [], "cost": 0.0, "duration_ms": 0}

    for line in output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type = obj.get("type", "")

        if msg_type == "system":
            events["init"] = obj
            events["skills_loaded"] = obj.get("skills", [])

        elif msg_type == "assistant":
            msg = obj.get("message", {})
            events["assistant_messages"].append(msg)
            for block in msg.get("content", []):
                if block.get("type") == "tool_use":
                    events["tool_calls"].append({
                        "tool": block.get("name", ""),
                        "input": block.get("input", {}),
                    })

        elif msg_type == "result":
            events["result"] = obj
            events["cost"] = obj.get("total_cost_usd", 0.0)
            events["duration_ms"] = obj.get("duration_ms", 0)

    return events


def detect_skill_trigger(events, skill_name):
    """Check if a specific skill was triggered in the stream events."""
    for call in events["tool_calls"]:
        if call["tool"] == "Skill":
            invoked = call["input"].get("skill", "")
            # Match with or without namespace prefix
            if invoked == skill_name or invoked.endswith(":" + skill_name):
                return True
    return False


def run_trigger_test(query, skill_name, expect_trigger, model=None, max_budget=None,
                     extra_flags=None):
    """Run a single trigger test case."""
    start = time.time()
    stdout, stderr, rc = run_claude_p(
        query, output_format="stream-json", max_turns=1,
        model=model, max_budget=max_budget, extra_flags=extra_flags
    )
    elapsed = int((time.time() - start) * 1000)

    if rc == -2:
        return TestResult(
            name=f"trigger/{'should' if expect_trigger else 'should_not'}: {query[:50]}",
            layer=2, passed=False,
            message=f"claude CLI not found: {stderr}",
            severity="error", duration_ms=elapsed,
        )

    events = parse_stream_json(stdout)
    triggered = detect_skill_trigger(events, skill_name)
    cost = events.get("cost", 0.0)

    if expect_trigger:
        passed = triggered
        message = (f"Skill '{skill_name}' triggered as expected"
                   if passed else f"Skill '{skill_name}' did NOT trigger (expected trigger)")
    else:
        passed = not triggered
        message = (f"Skill '{skill_name}' correctly not triggered"
                   if passed else f"Skill '{skill_name}' triggered unexpectedly")

    return TestResult(
        name=f"trigger/{'should' if expect_trigger else 'should_not'}: {query[:60]}",
        layer=2, passed=passed, message=message,
        cost=cost, duration_ms=elapsed,
        details={"query": query, "triggered": triggered, "expected": expect_trigger},
    )


def run_layer2(skill_dir, config, extra_flags=None):
    """Run all trigger tests."""
    triggers = config.get("triggers", {})
    skill_name = config.get("skill", os.path.basename(skill_dir))
    model = config.get("config", {}).get("default_model")
    max_budget = config.get("config", {}).get("max_budget_per_test", 0.50)

    results = []

    for query in triggers.get("should_trigger", []):
        results.append(run_trigger_test(query, skill_name, True, model, max_budget,
                                        extra_flags=extra_flags))

    for query in triggers.get("should_not_trigger", []):
        results.append(run_trigger_test(query, skill_name, False, model, max_budget,
                                        extra_flags=extra_flags))

    for edge in triggers.get("edge_cases", []):
        query = edge.get("query", "")
        expect = edge.get("expect", "trigger") == "trigger"
        result = run_trigger_test(query, skill_name, expect, model, max_budget,
                                  extra_flags=extra_flags)
        result.severity = "warning"  # Edge cases are advisory
        if edge.get("note"):
            result.details["note"] = edge["note"]
        results.append(result)

    return results


# Layer 3: Behavioral Tests

def get_full_response_text(events):
    """Extract all assistant text from stream events."""
    texts = []
    for msg in events.get("assistant_messages", []):
        for block in msg.get("content", []):
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
    return "\n".join(texts)


def get_tool_names_called(events):
    """Get set of tool names invoked."""
    return {call["tool"] for call in events.get("tool_calls", [])}


def check_hard_assertion(assertion, events):
    """Check a deterministic assertion against stream data."""
    atype = assertion.get("type", "")

    if atype == "no_errors":
        result_obj = events.get("result", {})
        is_error = result_obj.get("is_error", False)
        return not is_error, "No errors detected" if not is_error else "Errors detected in output"

    elif atype == "tool_called":
        tool = assertion.get("value", "")
        called = get_tool_names_called(events)
        found = tool in called
        return found, f"Tool '{tool}' was called" if found else f"Tool '{tool}' was NOT called (called: {called})"

    elif atype == "skill_invoked":
        skill = assertion.get("value", "")
        triggered = detect_skill_trigger(events, skill)
        return triggered, f"Skill '{skill}' was invoked" if triggered else f"Skill '{skill}' was NOT invoked"

    elif atype == "output_matches":
        pattern = assertion.get("pattern", "")
        text = get_full_response_text(events)
        matched = bool(re.search(pattern, text, re.IGNORECASE))
        return matched, f"Output matches pattern '{pattern}'" if matched else f"Output does NOT match pattern '{pattern}'"

    elif atype == "exit_success":
        result_obj = events.get("result", {})
        subtype = result_obj.get("subtype", "")
        passed = subtype == "success"
        return passed, f"Exit: {subtype}"

    elif atype == "max_turns_ok":
        result_obj = events.get("result", {})
        subtype = result_obj.get("subtype", "")
        passed = subtype != "error_max_turns"
        return passed, "Completed within turn limit" if passed else "Hit max turns limit"

    return None, None  # Not a hard assertion


SOFT_ASSERTION_TYPES = {
    "asks_clarification", "stays_in_scope", "suggests_fix",
    "mentions_error", "does_not_hallucinate_success",
    "contains_step", "follows_instructions",
}


def check_soft_assertions(assertions, events, model=None):
    """Evaluate soft assertions using a separate Claude evaluator pass."""
    soft = [a for a in assertions if a.get("type", "") in SOFT_ASSERTION_TYPES]
    if not soft:
        return []

    response_text = get_full_response_text(events)
    if not response_text.strip():
        return [TestResult(
            name=f"behavioral/soft:{a['type']}",
            layer=3, passed=False,
            message="No response text to evaluate",
            severity="warning",
        ) for a in soft]

    # Build evaluation prompt
    assertions_desc = "\n".join(
        f"- {a['type']}" + (f" (value: {a['value']})" if a.get('value') else "")
        for a in soft
    )

    eval_prompt = f"""Evaluate the following Claude response against these assertions.
For each assertion, respond with PASS or FAIL and a brief explanation.

ASSERTIONS TO CHECK:
{assertions_desc}

CLAUDE'S RESPONSE:
{response_text}

Respond in this exact format (one line per assertion):
ASSERTION_TYPE: PASS|FAIL - explanation"""

    stdout, stderr, rc = run_claude_p(
        eval_prompt, output_format="json", max_turns=1,
        model=model or "haiku",  # Use cheaper model for evaluation
        extra_flags=["--tools", ""]
    )

    results = []

    if rc != 0 or not stdout.strip():
        for a in soft:
            results.append(TestResult(
                name=f"behavioral/soft:{a['type']}",
                layer=3, passed=False,
                message=f"Evaluator failed (rc={rc})",
                severity="warning",
            ))
        return results

    # Parse evaluator response
    try:
        eval_data = json.loads(stdout)
        eval_text = eval_data.get("result", "")
        eval_cost = eval_data.get("total_cost_usd", 0.0)
    except json.JSONDecodeError:
        eval_text = stdout
        eval_cost = 0.0

    for a in soft:
        atype = a["type"]
        # Search for the assertion result in evaluator output
        pattern = re.compile(rf"{atype}:\s*(PASS|FAIL)\s*-\s*(.*)", re.IGNORECASE)
        match = pattern.search(eval_text)

        if match:
            passed = match.group(1).upper() == "PASS"
            explanation = match.group(2).strip()
        else:
            passed = False
            explanation = "Evaluator did not produce a result for this assertion"

        results.append(TestResult(
            name=f"behavioral/soft:{atype}",
            layer=3, passed=passed,
            message=explanation,
            severity="warning",  # Soft assertions are advisory
            cost=eval_cost / max(len(soft), 1),
        ))

    return results


def run_behavioral_test(test_case, config, extra_flags=None):
    """Run a single behavioral test case."""
    name = test_case.get("name", "unnamed")
    input_text = test_case.get("input", "")
    max_turns = test_case.get("max_turns", config.get("config", {}).get("default_max_turns", 5))
    model = config.get("config", {}).get("default_model")
    max_budget = test_case.get("max_budget", config.get("config", {}).get("max_budget_per_test", 0.50))
    assertions = test_case.get("assertions", [])

    # Run the skill
    start = time.time()
    stdout, stderr, rc = run_claude_p(
        input_text, output_format="stream-json", max_turns=max_turns,
        model=model, max_budget=max_budget, extra_flags=extra_flags
    )
    elapsed = int((time.time() - start) * 1000)

    if rc == -2:
        return [TestResult(
            name=f"behavioral/{name}",
            layer=3, passed=False,
            message=f"claude CLI not found: {stderr}",
            severity="error", duration_ms=elapsed,
        )]

    events = parse_stream_json(stdout)
    cost = events.get("cost", 0.0)
    results = []

    # Check hard assertions
    for assertion in assertions:
        passed, message = check_hard_assertion(assertion, events)
        if passed is not None:
            results.append(TestResult(
                name=f"behavioral/{name}/{assertion['type']}",
                layer=3, passed=passed, message=message,
                cost=0, duration_ms=0,
                details={"assertion": assertion},
            ))

    # Check soft assertions
    soft_results = check_soft_assertions(assertions, events, model)
    results.extend(soft_results)

    # Add metadata to first result
    if results:
        results[0].cost = cost
        results[0].duration_ms = elapsed

    return results


def run_layer3(skill_dir, config, extra_flags=None):
    """Run all behavioral tests."""
    behavioral = config.get("behavioral", [])
    results = []
    for test_case in behavioral:
        results.extend(run_behavioral_test(test_case, config, extra_flags=extra_flags))
    return results


# Report Generation

def generate_report(results, config, skill_dir):
    """Generate a full test report."""
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    passed = [r for r in results if r.passed]
    total_cost = sum(r.cost for r in results)
    total_duration = sum(r.duration_ms for r in results)

    layer_summary = {}
    for layer_num in [1, 2, 3]:
        layer_results = [r for r in results if r.layer == layer_num]
        if layer_results:
            layer_errors = [r for r in layer_results if not r.passed and r.severity == "error"]
            layer_warnings = [r for r in layer_results if not r.passed and r.severity == "warning"]
            layer_summary[f"layer{layer_num}"] = {
                "total": len(layer_results),
                "passed": len([r for r in layer_results if r.passed]),
                "errors": len(layer_errors),
                "warnings": len(layer_warnings),
                "result": "PASS" if len(layer_errors) == 0 else "FAIL",
            }

    return {
        "skill_dir": skill_dir,
        "skill_name": config.get("skill", os.path.basename(skill_dir)),
        "summary": {
            "total": len(results),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "result": "PASS" if len(errors) == 0 else "FAIL",
            "total_cost_usd": round(total_cost, 4),
            "total_duration_ms": total_duration,
        },
        "layers": layer_summary,
        "results": [r.to_dict() for r in results],
    }


def print_report(report):
    """Print human-readable test report."""
    s = report["summary"]
    print(f"\n{'=' * 70}")
    print(f"  Skill Test Report: {s['result']}")
    print(f"  {report['skill_dir']}")
    print(f"{'=' * 70}")
    print(f"  {s['passed']}/{s['total']} tests passed  |  "
          f"{s['errors']} errors  |  {s['warnings']} warnings")
    print(f"  Cost: ${s['total_cost_usd']:.4f}  |  "
          f"Duration: {s['total_duration_ms']}ms\n")

    # Per-layer summary
    for layer_key, layer_data in report.get("layers", {}).items():
        layer_label = {"layer1": "Structural", "layer2": "Trigger", "layer3": "Behavioral"}.get(layer_key, layer_key)
        icon = "PASS" if layer_data["result"] == "PASS" else "FAIL"
        print(f"  [{icon}] {layer_label}: "
              f"{layer_data['passed']}/{layer_data['total']} passed"
              f"  ({layer_data['errors']} errors, {layer_data['warnings']} warnings)")
    print()

    # Failures and warnings
    failures = [r for r in report["results"] if not r["passed"]]
    if failures:
        print("  ISSUES:")
        for r in failures:
            icon = "FAIL" if r["severity"] == "error" else "WARN"
            print(f"    [{icon}] {r['name']}: {r['message']}")
        print()

    if s["result"] == "PASS":
        print(f"  All tests passed" +
              (f" with {s['warnings']} warning(s)." if s["warnings"] > 0 else ".") + "\n")
    else:
        print(f"  {s['errors']} error(s) must be fixed.\n")


# Main

def main():
    parser = argparse.ArgumentParser(description="Run skill tests from TESTS.yaml")
    parser.add_argument("skill_dir", help="Path to the skill folder")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3],
                        help="Run only a specific layer (1=structural, 2=trigger, 3=behavioral)")
    parser.add_argument("--model", help="Override model for test runs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be tested without running")
    parser.add_argument("--plugin-dir",
                        help="Plugin directory to pass to claude -p (auto-detected if omitted)")
    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)

    # Load TESTS.yaml
    tests_path = os.path.join(skill_dir, "TESTS.yaml")
    if not os.path.exists(tests_path):
        # Fall back to running structural only
        if not args.json:
            print(f"No TESTS.yaml found in {skill_dir}. Running structural checks only.\n")
        config = {"skill": os.path.basename(skill_dir)}
    else:
        config = parse_yaml_file(tests_path)

    # Apply CLI overrides
    if args.model:
        config.setdefault("config", {})["default_model"] = args.model

    # Dry run
    if args.dry_run:
        triggers = config.get("triggers", {})
        behavioral = config.get("behavioral", [])
        print(f"Skill: {config.get('skill', os.path.basename(skill_dir))}")
        print(f"Layer 1: {20}+ structural checks")
        print(f"Layer 2: {len(triggers.get('should_trigger', []))} should-trigger, "
              f"{len(triggers.get('should_not_trigger', []))} should-not-trigger, "
              f"{len(triggers.get('edge_cases', []))} edge cases")
        print(f"Layer 3: {len(behavioral)} behavioral tests")
        est_cost = (len(triggers.get('should_trigger', [])) +
                    len(triggers.get('should_not_trigger', [])) +
                    len(triggers.get('edge_cases', []))) * 0.02
        est_cost += len(behavioral) * 0.10
        print(f"Estimated cost: ~${est_cost:.2f}")
        return

    # Detect plugin directory for --plugin-dir flag
    plugin_dir = args.plugin_dir or detect_plugin_dir(skill_dir)
    extra_flags = []
    if plugin_dir:
        extra_flags.extend(["--plugin-dir", plugin_dir])
        if not args.json and not args.dry_run:
            print(f"  Plugin directory: {plugin_dir}\n")

    # Run tests
    results = []
    total_cost = 0.0
    budget_total = config.get("config", {}).get("max_budget_total", 5.00)

    if args.layer is None or args.layer == 1:
        results.extend(run_layer1(skill_dir, config))

    if args.layer is None or args.layer == 2:
        if config.get("triggers"):
            results.extend(run_layer2(skill_dir, config, extra_flags=extra_flags or None))
            total_cost = sum(r.cost for r in results)
            if total_cost >= budget_total:
                if not args.json:
                    print(f"\n  Budget cap reached (${total_cost:.4f} >= ${budget_total:.2f}). Stopping.\n")

    if (args.layer is None or args.layer == 3) and total_cost < budget_total:
        if config.get("behavioral"):
            results.extend(run_layer3(skill_dir, config, extra_flags=extra_flags or None))

    # Generate report
    report = generate_report(results, config, skill_dir)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    sys.exit(0 if report["summary"]["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
