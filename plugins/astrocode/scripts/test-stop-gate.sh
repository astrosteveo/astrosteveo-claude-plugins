#!/bin/bash
# Test harness for stop-gate.sh
#
# Runs all scenarios in an isolated .test-workdir directory to prevent
# accidental commits or artifacts in the real repo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STOP_GATE="$SCRIPT_DIR/stop-gate.sh"
WORKDIR="$SCRIPT_DIR/.test-workdir"

passed=0
failed=0

# Clean up on exit
cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

# Create a fresh isolated git repo for a test scenario
setup_repo() {
  rm -rf "$WORKDIR"
  mkdir -p "$WORKDIR"
  cd "$WORKDIR"
  git init -q
}

# Run a single test scenario
# Usage: run_test "description" expected_exit_code
run_test() {
  local desc="$1"
  local expected="$2"
  local actual

  actual=0
  bash "$STOP_GATE" 2>/dev/null || actual=$?

  if [ "$actual" -eq "$expected" ]; then
    echo "  PASS: $desc (exit $actual)"
    passed=$((passed + 1))
  else
    echo "  FAIL: $desc (expected exit $expected, got $actual)"
    failed=$((failed + 1))
  fi
}

# Guard: refuse to run if workdir somehow points outside scripts dir
if [[ "$WORKDIR" != "$SCRIPT_DIR"/* ]]; then
  echo "ERROR: workdir resolved outside scripts dir, aborting"
  exit 1
fi

echo "Running stop-gate tests..."
echo ""

# --- Scenario 1: No changes at all ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
run_test "No changes at all" 0

# --- Scenario 2: Source + .agents/ both modified ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
echo "changed" > app.js
echo "updated" > .agents/CONTEXT.md
run_test "Source + .agents/ both modified" 0

# --- Scenario 3: Source modified, .agents/ unchanged ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
echo "changed" > app.js
run_test "Source modified, .agents/ unchanged" 1

# --- Scenario 4: No .agents/ directory ---
setup_repo
echo "src" > app.js
git add -A && git commit -q -m "init"
echo "changed" > app.js
run_test "No .agents/ directory" 0

# --- Scenario 5: New untracked source file, .agents/ unchanged ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
echo "new" > newfile.js
run_test "Untracked source file, .agents/ unchanged" 1

# --- Scenario 6: Both source and .agents/ have untracked files ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
echo "new" > newfile.js
echo "topic" > .agents/newtopic.md
run_test "Both source + .agents/ have untracked files" 0

# --- Scenario 7: Only .agents/ changed, no source changes ---
setup_repo
mkdir .agents && echo "ctx" > .agents/CONTEXT.md && echo "src" > app.js
git add -A && git commit -q -m "init"
echo "updated" > .agents/CONTEXT.md
run_test "Only .agents/ changed, no source changes" 0

# --- Results ---
echo ""
echo "Results: $passed passed, $failed failed"

if [ "$failed" -gt 0 ]; then
  exit 1
fi
