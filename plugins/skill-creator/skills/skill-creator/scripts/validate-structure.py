#!/usr/bin/env python3
"""
Layer 1: Deterministic structural validator for Claude skills.

Validates a skill folder against all known structural rules without
needing Claude. Returns JSON report + human-readable summary.

Usage:
    python validate-structure.py /path/to/skill-folder
    python validate-structure.py /path/to/skill-folder --json
"""

import argparse
import json
import os
import re
import sys
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_frontmatter(text):
    """Parse YAML frontmatter using a lenient line-based parser.

    Claude Code uses a lenient frontmatter parser that does not require
    quoting for values containing colons, double quotes, or brackets.
    Standard YAML parsers (PyYAML) are too strict for this format, so
    we always use the line-based parser to match Claude Code's behavior.

    Handles: key: value (rest of line is the value), key: >\\n  multiline,
    booleans, nested objects, and simple lists.
    """
    result = {}
    current_key = None
    current_value_lines = []
    multiline_mode = None  # None, '>' (folded), '|' (literal)
    indent_level = 0
    nested_key = None
    nested_dict = {}

    def flush():
        nonlocal current_key, current_value_lines, multiline_mode, nested_key, nested_dict
        if nested_key and nested_dict:
            result[nested_key] = nested_dict
            nested_key = None
            nested_dict = {}
        if current_key and current_value_lines:
            val = " ".join(current_value_lines).strip() if multiline_mode == ">" else "\n".join(current_value_lines).strip()
            result[current_key] = _coerce(val)
            current_key = None
            current_value_lines = []
            multiline_mode = None

    def _coerce(val):
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        # Simple list: [item1, item2]
        if val.startswith("[") and val.endswith("]"):
            items = [i.strip().strip("'\"") for i in val[1:-1].split(",")]
            return [i for i in items if i]
        return val

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check if this is a continuation of a multiline value
        if multiline_mode and line.startswith("  "):
            current_value_lines.append(line.strip())
            continue

        # Check if this is a nested key: value under a parent
        if nested_key and line.startswith("  ") and ":" in stripped:
            k, _, v = stripped.partition(":")
            nested_dict[k.strip()] = _coerce(v.strip())
            continue

        # Flush any pending state
        flush()

        # Parse key: value
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value == ">" or value == "|":
                current_key = key
                multiline_mode = value
                current_value_lines = []
            elif value == "":
                # Could be a nested object
                nested_key = key
                nested_dict = {}
            else:
                result[key] = _coerce(value)

    flush()
    return result


class Check:
    """Represents a single validation check result."""

    def __init__(self, name, category, passed, message="", severity="error"):
        self.name = name
        self.category = category
        self.passed = passed
        self.message = message
        self.severity = severity  # "error" or "warning"

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }


def validate_skill(skill_dir):
    """Run all structural validation checks on a skill directory."""
    checks = []
    skill_dir = os.path.abspath(skill_dir)
    folder_name = os.path.basename(skill_dir)

    # Directory checks

    if not os.path.isdir(skill_dir):
        checks.append(Check(
            "folder_exists", "structure", False,
            f"Directory does not exist: {skill_dir}"
        ))
        return checks  # Can't continue without the folder

    kebab_re = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
    checks.append(Check(
        "folder_kebab_case", "structure",
        bool(kebab_re.match(folder_name)),
        f"Folder name '{folder_name}' {'is' if kebab_re.match(folder_name) else 'is not'} kebab-case"
    ))

    readme_exists = os.path.exists(os.path.join(skill_dir, "README.md"))
    checks.append(Check(
        "no_readme", "structure",
        not readme_exists,
        "README.md found in skill folder (not allowed)" if readme_exists else "No README.md in skill folder"
    ))

    # SKILL.md checks

    skill_md_path = os.path.join(skill_dir, "SKILL.md")

    # Check SKILL.md exists with exact casing
    if os.path.exists(skill_md_path):
        # Verify exact casing by listing directory
        files_in_dir = os.listdir(skill_dir)
        has_exact_casing = "SKILL.md" in files_in_dir
        checks.append(Check(
            "skill_md_exists", "structure", has_exact_casing,
            "SKILL.md exists with correct casing" if has_exact_casing
            else "SKILL.md exists but with wrong casing"
        ))
    else:
        checks.append(Check(
            "skill_md_exists", "structure", False,
            "SKILL.md not found"
        ))
        return checks  # Can't continue without SKILL.md

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    line_count = len(lines)
    checks.append(Check(
        "line_count", "structure",
        line_count <= 500,
        f"SKILL.md is {line_count} lines ({'within' if line_count <= 500 else 'exceeds'} 500 line limit)",
        severity="error" if line_count > 500 else "warning"
    ))

    # Check no XML angle brackets (outside of code blocks and frontmatter)
    # Frontmatter is validated separately via description_no_xml;
    # skip it here to avoid false positives on YAML indicators like > and |
    fm_end_line = 0
    if content.startswith("---"):
        fm_close = content.find("---", 3)
        if fm_close > 0:
            fm_end_line = content[:fm_close + 3].count("\n")

    in_code_block = False
    xml_bracket_lines = []
    for i, line in enumerate(lines, 1):
        if i <= fm_end_line:
            continue
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and re.search(r"[<>]", line):
            xml_bracket_lines.append(i)

    checks.append(Check(
        "no_xml_brackets", "structure",
        len(xml_bracket_lines) == 0,
        f"XML angle brackets found on lines: {xml_bracket_lines}" if xml_bracket_lines
        else "No XML angle brackets outside code blocks"
    ))

    # Frontmatter checks

    has_frontmatter = content.startswith("---")
    second_delimiter = content.find("---", 3)
    has_closing = second_delimiter > 0

    checks.append(Check(
        "frontmatter_delimiters", "frontmatter",
        has_frontmatter and has_closing,
        "YAML frontmatter has opening and closing --- delimiters"
        if (has_frontmatter and has_closing)
        else "Missing frontmatter --- delimiters"
    ))

    if not (has_frontmatter and has_closing):
        return checks  # Can't parse frontmatter

    frontmatter_text = content[3:second_delimiter].strip()
    try:
        fm = parse_frontmatter(frontmatter_text)
        if not isinstance(fm, dict):
            raise ValueError("Frontmatter is not a YAML mapping")
        checks.append(Check(
            "frontmatter_valid_yaml", "frontmatter", True,
            "Frontmatter is valid YAML"
        ))
    except Exception as e:
        checks.append(Check(
            "frontmatter_valid_yaml", "frontmatter", False,
            f"Frontmatter YAML parse error: {e}"
        ))
        return checks

    # Name field checks
    # name is optional — defaults to directory name. Validate the effective name
    # (from frontmatter if present, otherwise the folder name).

    name = fm.get("name")
    effective_name = str(name) if name is not None else folder_name

    if name is not None:
        checks.append(Check(
            "name_present", "frontmatter", True,
            f"name field is set (optional — folder name '{folder_name}' would also work)",
            severity="warning"
        ))

        checks.append(Check(
            "name_matches_folder", "frontmatter",
            effective_name == folder_name,
            f"name '{effective_name}' {'matches' if effective_name == folder_name else 'does not match'} folder name '{folder_name}'"
        ))
    else:
        checks.append(Check(
            "name_present", "frontmatter", True,
            f"name field omitted — defaults to folder name '{folder_name}'",
            severity="warning"
        ))

    checks.append(Check(
        "name_kebab_case", "frontmatter",
        bool(kebab_re.match(effective_name)),
        f"effective name '{effective_name}' {'is' if kebab_re.match(effective_name) else 'is not'} kebab-case"
    ))

    checks.append(Check(
        "name_max_length", "frontmatter",
        len(effective_name) <= 64,
        f"effective name is {len(effective_name)} chars ({'within' if len(effective_name) <= 64 else 'exceeds'} 64 char limit)"
    ))

    has_reserved = "claude" in effective_name.lower() or "anthropic" in effective_name.lower()
    checks.append(Check(
        "name_no_reserved", "frontmatter",
        not has_reserved,
        f"effective name contains reserved word" if has_reserved
        else "effective name does not contain reserved words (claude/anthropic)"
    ))

    # Description field checks

    desc = fm.get("description")

    checks.append(Check(
        "description_present", "frontmatter",
        desc is not None,
        "description field is present" if desc else "description field is missing (recommended)",
        severity="warning" if desc is None else "error"
    ))

    if desc is not None:
        desc_str = str(desc)

        checks.append(Check(
            "description_max_length", "frontmatter",
            len(desc_str) <= 1024,
            f"description is {len(desc_str)} chars ({'within' if len(desc_str) <= 1024 else 'exceeds'} 1024 char soft limit)",
            severity="warning" if len(desc_str) > 1024 else "error"
        ))

        when_to_use = fm.get("when_to_use")
        combined_len = len(desc_str) + (len(str(when_to_use)) if when_to_use else 0)
        checks.append(Check(
            "description_listing_budget", "frontmatter",
            combined_len <= 1536,
            f"combined description + when_to_use is {combined_len} chars "
            f"({'within' if combined_len <= 1536 else 'exceeds'} 1,536-char listing budget — excess is truncated)",
            severity="warning"
        ))

        has_xml = bool(re.search(r"[<>]", desc_str))
        checks.append(Check(
            "description_no_xml", "frontmatter",
            not has_xml,
            "description contains XML angle brackets" if has_xml
            else "description has no XML angle brackets"
        ))

        # Check for trigger phrases (heuristic: look for "when", "use when", trigger-like patterns)
        trigger_patterns = [
            r"\bwhen\b", r"\buse\b.*\bwhen\b", r"\btrigger\b",
            r"\bsay[s]?\b", r"\bask[s]?\b", r"\brun[s]?\b\s*/",
            r'"[^"]+?"',  # quoted phrases
        ]
        trigger_count = sum(1 for p in trigger_patterns if re.search(p, desc_str, re.IGNORECASE))
        checks.append(Check(
            "description_has_triggers", "frontmatter",
            trigger_count >= 2,
            f"description has {trigger_count} trigger indicators (recommend 3+)",
            severity="warning" if trigger_count == 1 else "error"
        ))

        # Check for third person (heuristic: flag first/second person)
        first_person = bool(re.search(r"\bI\s+(can|will|help|am)\b", desc_str))
        second_person = bool(re.search(r"\bYou\s+(can|should|will)\b", desc_str))
        checks.append(Check(
            "description_third_person", "frontmatter",
            not (first_person or second_person),
            "description uses first/second person (should be third person)"
            if (first_person or second_person)
            else "description uses third person",
            severity="warning"
        ))

    # Optional field checks

    compatibility = fm.get("compatibility")
    if compatibility is not None:
        compat_str = str(compatibility)
        checks.append(Check(
            "compatibility_length", "frontmatter",
            1 <= len(compat_str) <= 500,
            f"compatibility is {len(compat_str)} chars ({'within' if 1 <= len(compat_str) <= 500 else 'outside'} 1-500 range)",
            severity="warning"
        ))

    disable_model = fm.get("disable-model-invocation")
    if disable_model is not None:
        checks.append(Check(
            "disable_model_invocation_bool", "frontmatter",
            isinstance(disable_model, bool),
            f"disable-model-invocation should be boolean, got {type(disable_model).__name__}",
            severity="warning"
        ))

    user_invocable = fm.get("user-invocable")
    if user_invocable is not None:
        checks.append(Check(
            "user_invocable_bool", "frontmatter",
            isinstance(user_invocable, bool),
            f"user-invocable should be boolean, got {type(user_invocable).__name__}",
            severity="warning"
        ))

    # Reference integrity checks

    # Find all referenced files in SKILL.md body (after frontmatter)
    # Only check references OUTSIDE code blocks
    body = content[second_delimiter + 3:]
    body_lines = body.split("\n")
    non_code_lines = []
    in_code = False
    for line in body_lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            non_code_lines.append(line)
    non_code_body = "\n".join(non_code_lines)

    backtick_refs = re.findall(r"`((?:references|scripts|assets)/[^`]+)`", non_code_body)
    referenced_files = set(backtick_refs)

    missing_refs = []
    for ref in referenced_files:
        full_path = os.path.join(skill_dir, ref)
        if not os.path.exists(full_path):
            missing_refs.append(ref)

    checks.append(Check(
        "references_exist", "references",
        len(missing_refs) == 0,
        f"Missing referenced files: {missing_refs}" if missing_refs
        else f"All {len(referenced_files)} referenced files exist"
        if referenced_files else "No file references found in body",
        severity="warning"  # Warning by default; use TESTS.yaml required_references for strict
    ))

    # Path style checks

    # Check for Windows-style backslash paths in body (outside code blocks)
    in_code_block = False
    backslash_lines = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and re.search(r"\\[a-zA-Z]", line):
            # Exclude common escapes like \n, \t, \r
            cleaned = re.sub(r"\\[ntr\\]", "", line)
            if re.search(r"\\[a-zA-Z]", cleaned):
                backslash_lines.append(i)

    checks.append(Check(
        "no_windows_paths", "content",
        len(backslash_lines) == 0,
        f"Possible Windows-style paths on lines: {backslash_lines}" if backslash_lines
        else "No Windows-style backslash paths detected",
        severity="warning"
    ))

    return checks


def generate_report(checks, skill_dir):
    """Generate JSON and human-readable reports from check results."""
    errors = [c for c in checks if not c.passed and c.severity == "error"]
    warnings = [c for c in checks if not c.passed and c.severity == "warning"]
    passed = [c for c in checks if c.passed]

    report = {
        "skill_dir": skill_dir,
        "summary": {
            "total": len(checks),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "result": "PASS" if len(errors) == 0 else "FAIL",
        },
        "checks": [c.to_dict() for c in checks],
    }
    return report


def print_human_readable(report):
    """Print a human-readable summary of the validation report."""
    summary = report["summary"]
    print(f"\n{'=' * 60}")
    print(f"  Skill Structural Validation: {summary['result']}")
    print(f"  {report['skill_dir']}")
    print(f"{'=' * 60}")
    print(f"  {summary['passed']}/{summary['total']} checks passed"
          f"  |  {summary['errors']} errors  |  {summary['warnings']} warnings\n")

    # Group by category
    categories = {}
    for check in report["checks"]:
        cat = check["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(check)

    for cat, cat_checks in categories.items():
        print(f"  [{cat.upper()}]")
        for c in cat_checks:
            icon = "PASS" if c["passed"] else ("WARN" if c["severity"] == "warning" else "FAIL")
            print(f"    [{icon}] {c['name']}: {c['message']}")
        print()

    if summary["result"] == "FAIL":
        print(f"  {summary['errors']} error(s) must be fixed before the skill is valid.\n")
    elif summary["warnings"] > 0:
        print(f"  All checks passed with {summary['warnings']} warning(s).\n")
    else:
        print(f"  All checks passed.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Claude skill folder structure"
    )
    parser.add_argument("skill_dir", help="Path to the skill folder to validate")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    checks = validate_skill(args.skill_dir)
    report = generate_report(checks, args.skill_dir)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_readable(report)

    # Exit code: 0 if pass, 1 if fail
    sys.exit(0 if report["summary"]["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
