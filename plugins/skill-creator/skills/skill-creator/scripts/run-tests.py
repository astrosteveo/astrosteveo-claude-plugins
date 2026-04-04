#!/usr/bin/env python3
"""
Skill Test Runner — Layers 1, 2, and 3.

Runs eval tests against a skill. Test specs (TESTS.yaml) are separate
from the skill itself — they are dev-time artifacts, not shipped with
the skill.

Usage:
    python run-tests.py /path/to/skill --tests /path/to/TESTS.yaml
    python run-tests.py /path/to/skill --tests tests.yaml --json
    python run-tests.py /path/to/skill --tests tests.yaml --layer 2
    python run-tests.py /path/to/skill --tests tests.yaml --model haiku --dry-run
    python run-tests.py /path/to/skill --tests tests.yaml --parallel 4
    python run-tests.py /path/to/skill --tests tests.yaml --runs 3
    python run-tests.py /path/to/skill --tests tests.yaml --save-results
    python run-tests.py /path/to/skill --tests tests.yaml --compare latest
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the structural validator from the same directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


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
                 duration_ms=0, details=None):
        self.name = name
        self.layer = layer
        self.passed = passed
        self.message = message
        self.severity = severity
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
        if self.duration_ms > 0:
            d["duration_ms"] = self.duration_ms
        if self.details:
            d["details"] = self.details
        return d


# TESTS.yaml Schema Validation

CANONICAL_TOP_LEVEL_KEYS = {"version", "skill", "config", "structural", "triggers", "behavioral"}

CANONICAL_CONFIG_KEYS = {
    "default_model": str,
    "default_max_turns": int,
    "permission_mode": str,
}

DEPRECATED_KEYS = {
    "type": ("skill", "Rename 'type' to 'skill' and set value to the skill name"),
    "tests": ("triggers", "Move 'tests.trigger' contents to top-level 'triggers'"),
}

DEPRECATED_CONFIG_KEYS = {
    "model": ("default_model", "Rename 'config.model' to 'config.default_model'"),
    "max_turns": ("default_max_turns", "Rename 'config.max_turns' to 'config.default_max_turns'"),
}

DEPRECATED_EDGE_CASE_KEYS = {
    "should_trigger": ("expect", "Replace 'should_trigger: true/false' with 'expect: trigger/no_trigger'"),
    "reason": ("note", "Rename 'reason' to 'note'"),
}


def validate_tests_yaml(raw_config, tests_path):
    """Validate TESTS.yaml schema. Returns list of TestResult."""
    results = []

    if raw_config is None:
        results.append(TestResult(
            name="schema/parse_error", layer=1, passed=False,
            message=f"TESTS.yaml at {tests_path} parsed as empty/null",
        ))
        return results

    # Check version
    version = raw_config.get("version")
    results.append(TestResult(
        name="schema/version_present", layer=1,
        passed=version is not None,
        message="version field present" if version is not None else "Missing 'version' field",
    ))
    if version is not None and version != 1:
        results.append(TestResult(
            name="schema/version_value", layer=1, passed=False,
            message=f"Unsupported schema version: {version} (expected 1)",
        ))

    # Check skill identifier
    has_skill = "skill" in raw_config
    has_type = "type" in raw_config
    results.append(TestResult(
        name="schema/skill_identifier", layer=1,
        passed=has_skill or has_type,
        message=(
            "skill field present" if has_skill
            else "Missing 'skill' field (found deprecated 'type')" if has_type
            else "Missing 'skill' field — add 'skill: your-skill-name'"
        ),
        severity="error" if not (has_skill or has_type) else ("warning" if has_type and not has_skill else "error"),
    ))

    # Check for deprecated top-level keys
    for old_key, (new_key, migration) in DEPRECATED_KEYS.items():
        if old_key in raw_config:
            results.append(TestResult(
                name=f"schema/deprecated_key:{old_key}", layer=1, passed=False,
                message=f"Deprecated key '{old_key}'. {migration}",
                severity="warning",
            ))

    # Check for unrecognized top-level keys
    known_keys = CANONICAL_TOP_LEVEL_KEYS | set(DEPRECATED_KEYS.keys())
    for key in raw_config:
        if key not in known_keys:
            results.append(TestResult(
                name=f"schema/unknown_key:{key}", layer=1, passed=False,
                message=f"Unrecognized top-level key '{key}'",
                severity="warning",
            ))

    # Validate config section
    config_section = raw_config.get("config", {})
    if isinstance(config_section, dict):
        known_config = set(CANONICAL_CONFIG_KEYS.keys()) | set(DEPRECATED_CONFIG_KEYS.keys())
        for key in config_section:
            if key in DEPRECATED_CONFIG_KEYS:
                _, migration = DEPRECATED_CONFIG_KEYS[key]
                results.append(TestResult(
                    name=f"schema/deprecated_config:{key}", layer=1, passed=False,
                    message=f"Deprecated config key '{key}'. {migration}",
                    severity="warning",
                ))
            elif key not in CANONICAL_CONFIG_KEYS:
                results.append(TestResult(
                    name=f"schema/unknown_config:{key}", layer=1, passed=False,
                    message=f"Unrecognized config key '{key}'",
                    severity="warning",
                ))
            else:
                expected_type = CANONICAL_CONFIG_KEYS[key]
                val = config_section[key]
                if not isinstance(val, expected_type):
                    results.append(TestResult(
                        name=f"schema/config_type:{key}", layer=1, passed=False,
                        message=f"config.{key} should be {expected_type.__name__ if isinstance(expected_type, type) else 'number'}, got {type(val).__name__}",
                        severity="warning",
                    ))

    # Validate triggers section
    triggers = raw_config.get("triggers", {})
    if isinstance(triggers, dict):
        for key in ["should_trigger", "should_not_trigger"]:
            val = triggers.get(key)
            if val is not None and not isinstance(val, list):
                results.append(TestResult(
                    name=f"schema/triggers_type:{key}", layer=1, passed=False,
                    message=f"triggers.{key} should be a list, got {type(val).__name__}",
                ))

        for i, edge in enumerate(triggers.get("edge_cases", [])):
            if not isinstance(edge, dict):
                results.append(TestResult(
                    name=f"schema/edge_case_type:{i}", layer=1, passed=False,
                    message=f"Edge case {i} should be a mapping, got {type(edge).__name__}",
                ))
                continue
            if "query" not in edge:
                results.append(TestResult(
                    name=f"schema/edge_case_query:{i}", layer=1, passed=False,
                    message=f"Edge case {i} missing required 'query' field",
                ))
            if "expect" not in edge and "should_trigger" not in edge:
                results.append(TestResult(
                    name=f"schema/edge_case_expect:{i}", layer=1, passed=False,
                    message=f"Edge case {i} missing 'expect' field (defaults to 'trigger')",
                    severity="warning",
                ))
            for old_key, (new_key, migration) in DEPRECATED_EDGE_CASE_KEYS.items():
                if old_key in edge:
                    results.append(TestResult(
                        name=f"schema/deprecated_edge:{old_key}:{i}", layer=1, passed=False,
                        message=f"Edge case {i}: deprecated key '{old_key}'. {migration}",
                        severity="warning",
                    ))

    # Check for old-style nested triggers (tests.trigger instead of triggers)
    tests_section = raw_config.get("tests", {})
    if isinstance(tests_section, dict) and "trigger" in tests_section:
        results.append(TestResult(
            name="schema/deprecated_nested_triggers", layer=1, passed=False,
            message="Deprecated: 'tests.trigger' detected. Move contents to top-level 'triggers'",
            severity="warning",
        ))

    # Validate behavioral section
    behavioral = raw_config.get("behavioral", [])
    if isinstance(behavioral, list):
        for i, test in enumerate(behavioral):
            if not isinstance(test, dict):
                results.append(TestResult(
                    name=f"schema/behavioral_type:{i}", layer=1, passed=False,
                    message=f"Behavioral test {i} should be a mapping",
                ))
                continue
            if "name" not in test:
                results.append(TestResult(
                    name=f"schema/behavioral_name:{i}", layer=1, passed=False,
                    message=f"Behavioral test {i} missing required 'name' field",
                ))
            if "input" not in test:
                results.append(TestResult(
                    name=f"schema/behavioral_input:{i}", layer=1, passed=False,
                    message=f"Behavioral test {i} missing required 'input' field",
                ))
            if "assertions" not in test:
                results.append(TestResult(
                    name=f"schema/behavioral_assertions:{i}", layer=1, passed=False,
                    message=f"Behavioral test {i} missing 'assertions' field",
                    severity="warning",
                ))

    return results


# Layer 1: Structural

def run_layer1(skill_dir, config, tests_path=None):
    """Run structural validation checks."""
    results = []

    # Schema validation (if TESTS.yaml exists)
    if tests_path and os.path.exists(tests_path):
        results.extend(validate_tests_yaml(config, tests_path))

    vs = load_validate_structure()
    checks = vs.validate_skill(skill_dir)
    report = vs.generate_report(checks, skill_dir)

    for check in report["checks"]:
        results.append(TestResult(
            name=f"structural/{check['name']}",
            layer=1,
            passed=check["passed"],
            message=check["message"],
            severity=check["severity"],
        ))

    # Check required_references from TESTS.yaml (upgrade to errors)
    structural_config = (config.get("structural") or {}) if config else {}
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
                 model=None, extra_flags=None, cwd=None,
                 session_id=None, resume=False):
    """Spawn a claude -p process and return parsed output."""
    cmd = ["claude", "-p", prompt, "--output-format", output_format,
           "--permission-mode", "bypassPermissions"]

    if not resume and not session_id:
        cmd.append("--no-session-persistence")

    if session_id:
        cmd.extend(["--session-id", session_id])
    if resume:
        cmd.append("--resume")

    if output_format == "stream-json":
        cmd.append("--verbose")

    if max_turns is not None:
        cmd.extend(["--max-turns", str(max_turns)])
    if model:
        cmd.extend(["--model", model])
    if extra_flags:
        cmd.extend(extra_flags)

    # Prevent MSYS/Git Bash from mangling slash-prefixed args (e.g. /commit -> C:/Program Files/Git/commit)
    env = os.environ.copy()
    env["MSYS_NO_PATHCONV"] = "1"

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, cwd=cwd, env=env,
            encoding="utf-8", errors="replace"
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Process timed out after 120s", -1
    except FileNotFoundError:
        return "", "claude CLI not found. Is Claude Code installed?", -2


def run_claude_p_multiturn(messages, output_format="stream-json", max_turns=1,
                           model=None, extra_flags=None, cwd=None):
    """Run a multi-turn conversation using --session-id and --resume.

    Args:
        messages: list of str, each a user message in sequence
    Returns:
        combined_stdout, combined_stderr, last_returncode
    """
    sid = str(uuid.uuid4())
    all_stdout = []
    all_stderr = []
    last_rc = 0

    for i, msg in enumerate(messages):
        is_first = (i == 0)
        stdout, stderr, rc = run_claude_p(
            msg, output_format=output_format, max_turns=max_turns,
            model=model, extra_flags=extra_flags,
            cwd=cwd, session_id=sid, resume=not is_first,
        )
        all_stdout.append(stdout)
        all_stderr.append(stderr)
        last_rc = rc
        if rc == -2:
            break

    return "\n".join(all_stdout), "\n".join(all_stderr), last_rc


def parse_stream_json(output):
    """Parse stream-json output into structured events."""
    events = {"init": None, "assistant_messages": [], "tool_calls": [],
              "result": None, "skills_loaded": [], "duration_ms": 0}

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
            events["duration_ms"] += obj.get("duration_ms", 0)

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


def run_trigger_test(query, skill_name, expect_trigger, model=None,
                     extra_flags=None):
    """Run a single trigger test case."""
    start = time.time()
    stdout, stderr, rc = run_claude_p(
        query, output_format="stream-json", max_turns=1,
        model=model, extra_flags=extra_flags
    )
    elapsed = int((time.time() - start) * 1000)

    if rc == -2:
        return TestResult(
            name=f"trigger/{'should' if expect_trigger else 'should_not'}: {query[:60]}",
            layer=2, passed=False,
            message=f"claude CLI not found: {stderr}",
            severity="error", duration_ms=elapsed,
        )

    events = parse_stream_json(stdout)
    triggered = detect_skill_trigger(events, skill_name)

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
        duration_ms=elapsed,
        details={"query": query, "triggered": triggered, "expected": expect_trigger},
    )


def run_layer2(skill_dir, config, extra_flags=None, parallel=1):
    """Run all trigger tests."""
    triggers = config.get("triggers", {})
    skill_name = config.get("skill", os.path.basename(skill_dir))
    model = config.get("config", {}).get("default_model")

    # Build work items: (query, expect_trigger, is_edge, edge_data)
    work = []
    for query in triggers.get("should_trigger", []):
        work.append((query, True, False, None))
    for query in triggers.get("should_not_trigger", []):
        work.append((query, False, False, None))
    for edge in triggers.get("edge_cases", []):
        query = edge.get("query", "")
        expect = edge.get("expect", "trigger") == "trigger"
        work.append((query, expect, True, edge))

    if parallel > 1 and len(work) > 1:
        return _run_trigger_tests_parallel(work, skill_name, model,
                                           extra_flags, parallel)
    else:
        return _run_trigger_tests_sequential(work, skill_name, model,
                                             extra_flags)


def _run_trigger_tests_sequential(work, skill_name, model, extra_flags):
    """Run trigger tests one at a time."""
    results = []
    for query, expect, is_edge, edge_data in work:
        result = run_trigger_test(query, skill_name, expect, model,
                                  extra_flags=extra_flags)
        if is_edge:
            result.severity = "warning"
            if edge_data and edge_data.get("note"):
                result.details["note"] = edge_data["note"]
        results.append(result)
    return results


def _run_trigger_tests_parallel(work, skill_name, model, extra_flags, parallel):
    """Run trigger tests concurrently."""
    results = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        future_map = {}
        for query, expect, is_edge, edge_data in work:
            f = pool.submit(run_trigger_test, query, skill_name, expect, model,
                            extra_flags)
            future_map[f] = (is_edge, edge_data)

        for future in as_completed(future_map):
            is_edge, edge_data = future_map[future]
            result = future.result()
            if is_edge:
                result.severity = "warning"
                if edge_data and edge_data.get("note"):
                    result.details["note"] = edge_data["note"]
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


def get_tool_call_sequence(events):
    """Get ordered list of tool names invoked."""
    return [call["tool"] for call in events.get("tool_calls", [])]


FILESYSTEM_ASSERTION_TYPES = {"file_exists", "file_not_exists", "directory_exists", "file_contains"}


def check_hard_assertion(assertion, events, workdir=None):
    """Check a deterministic assertion against stream data."""
    atype = assertion.get("type", "")

    if atype == "no_errors":
        result_obj = events.get("result") or {}
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

    elif atype == "output_does_not_match":
        pattern = assertion.get("pattern", "")
        text = get_full_response_text(events)
        matched = bool(re.search(pattern, text, re.IGNORECASE))
        return not matched, (
            f"Output correctly does not match pattern '{pattern}'"
            if not matched
            else f"Output unexpectedly matches pattern '{pattern}'"
        )

    elif atype == "exit_success":
        result_obj = events.get("result") or {}
        subtype = result_obj.get("subtype", "")
        passed = subtype == "success"
        return passed, f"Exit: {subtype}"

    elif atype == "max_turns_ok":
        result_obj = events.get("result") or {}
        subtype = result_obj.get("subtype", "")
        passed = subtype != "error_max_turns"
        return passed, "Completed within turn limit" if passed else "Hit max turns limit"

    elif atype == "tool_sequence":
        expected_seq = assertion.get("value", [])
        actual_seq = get_tool_call_sequence(events)
        it = iter(actual_seq)
        matched = all(tool in it for tool in expected_seq)
        return matched, (
            f"Tool sequence {expected_seq} found in order"
            if matched
            else f"Tool sequence {expected_seq} not found. Actual: {actual_seq}"
        )

    elif atype == "tool_call_count":
        tool = assertion.get("value", "")
        expected_count = assertion.get("count", 0)
        actual_count = sum(1 for c in events.get("tool_calls", []) if c["tool"] == tool)
        op = assertion.get("op", "eq")
        if op == "gte":
            passed = actual_count >= expected_count
        elif op == "lte":
            passed = actual_count <= expected_count
        else:
            passed = actual_count == expected_count
        return passed, f"Tool '{tool}' called {actual_count} times (expected {op} {expected_count})"

    # Filesystem assertions
    elif atype in FILESYSTEM_ASSERTION_TYPES:
        if not workdir:
            return False, f"{atype} requires test isolation (add a 'setup' block to the test case)"

        if atype == "file_exists":
            filepath = assertion.get("value", "")
            exists = os.path.exists(os.path.join(workdir, filepath))
            return exists, f"File '{filepath}' {'exists' if exists else 'does not exist'}"

        elif atype == "file_not_exists":
            filepath = assertion.get("value", "")
            exists = os.path.exists(os.path.join(workdir, filepath))
            return not exists, f"File '{filepath}' {'does not exist' if not exists else 'unexpectedly exists'}"

        elif atype == "directory_exists":
            dirpath = assertion.get("value", "")
            exists = os.path.isdir(os.path.join(workdir, dirpath))
            return exists, f"Directory '{dirpath}' {'exists' if exists else 'does not exist'}"

        elif atype == "file_contains":
            filepath = assertion.get("value", "")
            pattern = assertion.get("pattern", "")
            full_path = os.path.join(workdir, filepath)
            if not os.path.exists(full_path):
                return False, f"File '{filepath}' does not exist"
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError) as e:
                return False, f"Cannot read '{filepath}': {e}"
            matched = bool(re.search(pattern, content, re.IGNORECASE))
            return matched, (
                f"File '{filepath}' contains pattern '{pattern}'"
                if matched
                else f"File '{filepath}' does not contain pattern '{pattern}'"
            )

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
            severity=a.get("severity", "warning"),
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
                severity=a.get("severity", "warning"),
            ))
        return results

    # Parse evaluator response
    try:
        eval_data = json.loads(stdout)
        eval_text = eval_data.get("result", "")
    except json.JSONDecodeError:
        eval_text = stdout

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
            severity=a.get("severity", "warning"),
        ))

    return results


def setup_test_environment(workdir, setup):
    """Prepare a test environment in workdir. Mirrors test-hooks.py pattern."""
    if setup.get("git_init"):
        subprocess.run(["git", "init"], cwd=workdir, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@test.local"],
                       cwd=workdir, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test Runner"],
                       cwd=workdir, capture_output=True, text=True)

    for filepath, content in (setup.get("files") or {}).items():
        full = os.path.join(workdir, filepath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    if setup.get("commit") and setup.get("git_init"):
        subprocess.run(["git", "add", "-A"], cwd=workdir, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "initial"],
                       cwd=workdir, capture_output=True, text=True)


def _needs_workdir(test_case):
    """Check if a behavioral test needs an isolated working directory."""
    if test_case.get("setup"):
        return True
    for a in test_case.get("assertions", []):
        if a.get("type", "") in FILESYSTEM_ASSERTION_TYPES:
            return True
    return False


def run_behavioral_test(test_case, config, extra_flags=None):
    """Run a single behavioral test case."""
    name = test_case.get("name", "unnamed")
    input_text = test_case.get("input", "")
    max_turns = test_case.get("max_turns", config.get("config", {}).get("default_max_turns", 5))
    model = config.get("config", {}).get("default_model")
    assertions = test_case.get("assertions", [])
    setup = test_case.get("setup", {})

    workdir = None
    try:
        if _needs_workdir(test_case):
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', name[:20])
            workdir = tempfile.mkdtemp(prefix=f"skill-test-{safe_name}-")
            if setup:
                setup_test_environment(workdir, setup)

        # Run the skill
        start = time.time()
        if isinstance(input_text, list):
            stdout, stderr, rc = run_claude_p_multiturn(
                input_text, output_format="stream-json", max_turns=max_turns,
                model=model, extra_flags=extra_flags,
                cwd=workdir,
            )
        else:
            stdout, stderr, rc = run_claude_p(
                input_text, output_format="stream-json", max_turns=max_turns,
                model=model, extra_flags=extra_flags,
                cwd=workdir,
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
        results = []

        # Check hard assertions
        for assertion in assertions:
            atype = assertion.get("type", "")
            passed, message = check_hard_assertion(assertion, events, workdir=workdir)
            if passed is not None:
                results.append(TestResult(
                    name=f"behavioral/{name}/{atype}",
                    layer=3, passed=passed, message=message,
                    duration_ms=0,
                    details={"assertion": assertion},
                ))
            elif atype not in SOFT_ASSERTION_TYPES:
                results.append(TestResult(
                    name=f"behavioral/{name}/{atype}",
                    layer=3, passed=False,
                    message=f"Unknown assertion type '{atype}'",
                    severity="warning",
                ))

        # Check soft assertions
        soft_results = check_soft_assertions(assertions, events, model)
        results.extend(soft_results)

        # Add metadata to first result
        if results:
            results[0].duration_ms = elapsed

        return results

    finally:
        if workdir:
            shutil.rmtree(workdir, ignore_errors=True)


def run_layer3(skill_dir, config, extra_flags=None, parallel=1):
    """Run all behavioral tests."""
    behavioral = config.get("behavioral", [])
    if parallel > 1 and len(behavioral) > 1:
        results = []
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            futures = {
                pool.submit(run_behavioral_test, tc, config, extra_flags): tc
                for tc in behavioral
            }
            for future in as_completed(futures):
                results.extend(future.result())
        return results
    else:
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
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total": len(results),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "result": "PASS" if len(errors) == 0 else "FAIL",
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
    print(f"  Duration: {s['total_duration_ms']}ms\n")

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


# Flakiness Detection

def run_flakiness_analysis(all_runs):
    """Analyze per-test stability across multiple runs.

    Args:
        all_runs: list of list[TestResult], one inner list per run
    Returns:
        dict with per-test pass rates and flaky test list
    """
    test_passes = {}  # name -> [bool, ...]
    num_runs = len(all_runs)

    for run_results in all_runs:
        for r in run_results:
            test_passes.setdefault(r.name, []).append(r.passed)

    tests = {}
    flaky = []
    for name, passes in test_passes.items():
        rate = sum(passes) / len(passes)
        entry = {"pass_rate": round(rate, 2), "runs": len(passes)}
        if 0 < rate < 1.0:
            entry["flaky"] = True
            flaky.append(name)
        tests[name] = entry

    return {
        "num_runs": num_runs,
        "total_tests": len(tests),
        "flaky_count": len(flaky),
        "flaky_tests": flaky,
        "stability": round(1.0 - len(flaky) / max(len(tests), 1), 2),
        "tests": tests,
    }


def print_flakiness_report(flakiness):
    """Print human-readable flakiness report."""
    print(f"\n{'=' * 70}")
    print(f"  Flakiness Report ({flakiness['num_runs']} runs)")
    print(f"{'=' * 70}")
    print(f"  {flakiness['total_tests']} tests  |  "
          f"{flakiness['flaky_count']} flaky  |  "
          f"stability: {flakiness['stability'] * 100:.0f}%\n")

    if flakiness["flaky_tests"]:
        print("  FLAKY TESTS:")
        for name in flakiness["flaky_tests"]:
            rate = flakiness["tests"][name]["pass_rate"]
            print(f"    {name}: {rate * 100:.0f}% pass rate")
        print()
    else:
        print("  No flaky tests detected.\n")


# Regression Tracking

def save_results(report, output_dir):
    """Save test results to output_dir/test-results/."""
    results_dir = os.path.join(output_dir, "test-results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d_%H%M%S")
    filepath = os.path.join(results_dir, f"{timestamp}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write latest.json
    latest_path = os.path.join(results_dir, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return filepath


def compare_results(current_report, baseline_path):
    """Compare current results against a baseline.

    Returns:
        dict with regressions, improvements, new_tests, removed_tests
    """
    try:
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return {"error": f"Cannot load baseline: {e}"}

    baseline_map = {r["name"]: r["passed"] for r in baseline.get("results", [])}
    current_map = {r["name"]: r["passed"] for r in current_report.get("results", [])}

    regressions = []
    improvements = []
    for name, passed in current_map.items():
        if name in baseline_map:
            if baseline_map[name] and not passed:
                regressions.append(name)
            elif not baseline_map[name] and passed:
                improvements.append(name)

    new_tests = [n for n in current_map if n not in baseline_map]
    removed_tests = [n for n in baseline_map if n not in current_map]

    return {
        "baseline_timestamp": baseline.get("timestamp", "unknown"),
        "regressions": regressions,
        "improvements": improvements,
        "new_tests": new_tests,
        "removed_tests": removed_tests,
        "regression_count": len(regressions),
        "improvement_count": len(improvements),
    }


def print_comparison(diff):
    """Print human-readable comparison."""
    if "error" in diff:
        print(f"\n  Comparison error: {diff['error']}\n")
        return

    print(f"\n{'=' * 70}")
    print(f"  Comparison vs baseline ({diff['baseline_timestamp']})")
    print(f"{'=' * 70}")

    if diff["regressions"]:
        print(f"\n  REGRESSIONS ({diff['regression_count']}):")
        for name in diff["regressions"]:
            print(f"    [REGR] {name}")

    if diff["improvements"]:
        print(f"\n  IMPROVEMENTS ({diff['improvement_count']}):")
        for name in diff["improvements"]:
            print(f"    [IMPR] {name}")

    if diff["new_tests"]:
        print(f"\n  NEW TESTS ({len(diff['new_tests'])}):")
        for name in diff["new_tests"]:
            print(f"    [NEW]  {name}")

    if diff["removed_tests"]:
        print(f"\n  REMOVED TESTS ({len(diff['removed_tests'])}):")
        for name in diff["removed_tests"]:
            print(f"    [DEL]  {name}")

    if not any([diff["regressions"], diff["improvements"], diff["new_tests"], diff["removed_tests"]]):
        print("\n  No changes from baseline.")

    print()


# Suite Execution

def execute_suite(skill_dir, config, layer=None, extra_flags=None,
                  parallel=1, tests_path=None):
    """Run all requested layers and return list of TestResult.

    This is the core test execution loop, isolated from CLI concerns.
    """
    results = []

    if layer is None or layer == 1:
        results.extend(run_layer1(skill_dir, config, tests_path=tests_path))

    if layer is None or layer == 2:
        if config.get("triggers"):
            results.extend(run_layer2(skill_dir, config, extra_flags=extra_flags,
                                      parallel=parallel))

    if layer is None or layer == 3:
        if config.get("behavioral"):
            results.extend(run_layer3(skill_dir, config, extra_flags=extra_flags,
                                      parallel=parallel))

    return results


# Main

def main():
    parser = argparse.ArgumentParser(description="Run skill eval tests")
    parser.add_argument("skill_dir", help="Path to the skill folder")
    parser.add_argument("--tests", metavar="PATH",
                        help="Path to TESTS.yaml (test specs live outside the skill folder)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3],
                        help="Run only a specific layer (1=structural, 2=trigger, 3=behavioral)")
    parser.add_argument("--model", help="Override model for test runs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be tested without running")
    parser.add_argument("--plugin-dir",
                        help="Plugin directory to pass to claude -p (auto-detected if omitted)")
    parser.add_argument("--parallel", type=int, default=1, metavar="N",
                        help="Number of parallel test workers (default: 1)")
    parser.add_argument("--runs", type=int, default=1, metavar="N",
                        help="Run suite N times and report per-test stability")
    parser.add_argument("--save-results", action="store_true",
                        help="Save results to test-results/ next to the TESTS.yaml file")
    parser.add_argument("--compare", metavar="BASELINE",
                        help="Compare results against a baseline file (path or 'latest')")
    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)

    # Load TESTS.yaml — prefer --tests flag, fall back to skill dir (with warning)
    if args.tests:
        tests_path = os.path.abspath(args.tests)
    else:
        tests_path = os.path.join(skill_dir, "TESTS.yaml")

    if not os.path.exists(tests_path):
        if not args.json:
            if args.tests:
                print(f"TESTS.yaml not found at {tests_path}.\n")
            else:
                print(f"No TESTS.yaml provided. Running structural checks only.\n"
                      f"  Hint: use --tests /path/to/TESTS.yaml\n")
        config = {"skill": os.path.basename(skill_dir)}
        tests_path = None
    else:
        if not args.tests and not args.json:
            print(f"  Note: Loading TESTS.yaml from skill folder. Consider moving it\n"
                  f"  outside the skill dir and using --tests instead.\n")
        config = parse_yaml_file(tests_path) or {"skill": os.path.basename(skill_dir)}

    # Apply CLI overrides
    if args.model:
        config.setdefault("config", {})["default_model"] = args.model

    # Dry run
    if args.dry_run:
        triggers = config.get("triggers", {})
        behavioral = config.get("behavioral", [])
        total_trigger = (len(triggers.get('should_trigger', [])) +
                         len(triggers.get('should_not_trigger', [])) +
                         len(triggers.get('edge_cases', [])))
        print(f"Skill: {config.get('skill', os.path.basename(skill_dir))}")
        print(f"Layer 1: structural checks (including schema validation)")
        print(f"Layer 2: {len(triggers.get('should_trigger', []))} should-trigger, "
              f"{len(triggers.get('should_not_trigger', []))} should-not-trigger, "
              f"{len(triggers.get('edge_cases', []))} edge cases")
        print(f"Layer 3: {len(behavioral)} behavioral tests")
        if args.parallel > 1:
            print(f"Parallel workers: {args.parallel}")
        if args.runs > 1:
            print(f"Runs: {args.runs}")
        return

    # Detect plugin directory for --plugin-dir flag
    plugin_dir = args.plugin_dir or detect_plugin_dir(skill_dir)
    extra_flags = []
    if plugin_dir:
        extra_flags.extend(["--plugin-dir", plugin_dir])
        if not args.json and not args.dry_run:
            print(f"  Plugin directory: {plugin_dir}\n")

    # Flakiness detection: multiple runs
    if args.runs > 1:
        all_runs = []
        for i in range(args.runs):
            if not args.json:
                print(f"  Run {i + 1}/{args.runs}...")
            run_results = execute_suite(
                skill_dir, config, layer=args.layer, extra_flags=extra_flags or None,
                parallel=args.parallel, tests_path=tests_path,
            )
            all_runs.append(run_results)

        flakiness = run_flakiness_analysis(all_runs)

        # Use the last run for the primary report
        results = all_runs[-1] if all_runs else []
        report = generate_report(results, config, skill_dir)
        report["flakiness"] = flakiness
    else:
        # Single run
        results = execute_suite(
            skill_dir, config, layer=args.layer, extra_flags=extra_flags or None,
            parallel=args.parallel, tests_path=tests_path,
        )
        report = generate_report(results, config, skill_dir)

    # Save results next to the TESTS.yaml (or skill dir if no --tests)
    results_base_dir = os.path.dirname(tests_path) if tests_path else skill_dir
    if args.save_results:
        path = save_results(report, results_base_dir)
        if not args.json:
            print(f"  Results saved to {path}\n")

    # Compare against baseline (mutate report before printing)
    if args.compare:
        baseline_path = args.compare
        if baseline_path == "latest":
            baseline_path = os.path.join(results_base_dir, "test-results", "latest.json")
        diff = compare_results(report, baseline_path)
        report["comparison"] = diff

    # Output: JSON once at the end, or human-readable
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
        if args.runs > 1:
            print_flakiness_report(report.get("flakiness", {}))
        if args.compare:
            print_comparison(report.get("comparison", {}))

    sys.exit(0 if report["summary"]["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
