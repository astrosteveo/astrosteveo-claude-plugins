---
name: code-sniffer
description: Detects code smells and AI-generated slop in codebases. Analyzes code for suspicious patterns: over-engineering, cargo-culted abstractions, ceremonial error handling, defensive code against impossible states, tests that assert truthy instead of behavior, and ceremony-to-substance ratio problems. Use when the user says "sniff this code", "check for AI slop", "is this vibe coded", "smell check", "detect AI-generated code", "how smelly is this", "check for code smells", "sniff for slop", or asks whether code looks AI-generated or over-engineered. Works on any language or framework. Do NOT use for comprehensive quality audits (use code-quality instead), formatting/linting, writing or fixing code, or single-function refactors.
metadata:
  author: astrosteveo
  version: 0.1.0
  tags:
    - code-quality
    - code-smells
    - ai-slop
    - static-analysis
---

# Code Sniffer

Detect code smells and AI-generated slop. Two detection layers: general code
smells that indicate careless or low-quality code, plus AI-slop-specific signals
that indicate code was generated without thought.

Use ultrathink for thorough pattern analysis throughout this review.

## How This Differs From Code Quality Review

This skill is fast and opinionated. It does NOT build a full project mental model
first. It hunts for specific smell patterns and AI slop signals. For comprehensive,
context-aware quality audits, use the code-quality skill instead.

## Workflow

### Step 1: Scope

Determine what to sniff:

1. **User specified a target** — sniff exactly what they asked for (file, directory, PR)
2. **No target specified** — ask: "What should I sniff? A specific file, directory, PR,
   or the whole codebase?"
3. **Whole codebase** — use Glob to map source files, skip vendored/generated/build
   artifacts. For large codebases (200+ files), launch parallel Agent subagents
   (subagent_type: Explore) to map modules, then general-purpose agents to sniff
   independent modules simultaneously.

### Step 2: Sniff

Read the code and check against both smell layers. Consult `references/smell-catalog.md`
for the full catalog of smells and detection guidance.

**Layer 1 — General Code Smells:**
- Complexity without justification
- Dead abstractions (interfaces with one implementation, factories that build one thing)
- Cargo-culted patterns (repository pattern over a single DB, event bus with one subscriber)
- Ceremonial error handling (catch-log-rethrow, generic messages, swallowed exceptions)
- God files / god functions
- Copy-paste with minor variations
- Constants defined, used once, never configurable
- Wrapper classes that add nothing

**Layer 2 — AI Slop Signals:**
- Over-engineering born in a single commit (check `git log` / `git blame`)
- Docstrings on every function including obvious ones
- Defensive code against impossible states (null checks in non-nullable contexts, type
  checks in typed languages)
- Ceremony-to-substance ratio: how much code is actually doing the thing vs. wrapping,
  validating, logging around doing the thing
- Tests that assert truthy/existence instead of specific behavior
- Tests that mock away the interesting parts
- Backwards-compatibility shims for code that was just written
- TODO/FIXME comments in production code with no tracking reference
- Apologetic comments ("simplified version", "for production you'd want to...")
- Generic error messages that sound helpful but say nothing
- Feature flags or config options that nothing uses
- Imports that aren't used, variables declared but never read
- Inconsistent naming conventions within the same file
- Security code that's ceremonial (hashing without salting, CSRF tokens generated but
  never validated)

### Step 3: Check Git History (When Available)

Git history is a powerful slop signal. Run these checks for suspicious code:

1. **Birth check** — `git log --follow --diff-filter=A` on suspicious files. Was the
   file born fully-formed in a single commit? Large files appearing complete in one
   commit with no iteration are a strong AI slop signal.
2. **Iteration check** — does the file have a healthy edit history, or was it created
   once and never touched? Code that was never iterated on often wasn't thought through.
3. **Commit message check** — vague messages like "add feature", "update code",
   "implement changes" alongside large diffs suggest vibe-coded sessions.

Do NOT treat git signals as conclusive — they're additional context, not proof. Some
legitimate code is written correctly the first time. These signals strengthen or weaken
findings from Layers 1 and 2.

### Step 4: Score and Report

Produce a smell report following `references/report-format.md`.

For each finding:
1. Identify the smell pattern by name (from the catalog)
2. Show the specific code location (`path/to/file:line_number`)
3. Explain WHY it smells — what about this code suggests it was written without thought?
4. Rate the stink level (see report format)
5. If AI slop signals are present, flag them explicitly

After individual findings, produce:
- **Smell summary** — counts by category and stink level
- **AI Slop Assessment** — overall judgment: does this codebase show signs of being
  AI-generated or vibe-coded? Back it up with specific evidence.
- **Worst offenders** — top 3-5 files or modules that need the most attention

## Rules

- **Be specific** — "this smells" is not a finding. Say exactly what pattern you see
  and why it's a problem.
- **No false morality** — simple code that works is good code. Don't penalize code for
  being straightforward. The enemy is unnecessary complexity, not simplicity.
- **Respect intentional patterns** — if the project has a consistent pattern (even an
  unusual one), it's probably intentional. Smell it if it's inconsistent.
- **Git signals are context, not proof** — a file born in one commit might be a
  well-prepared migration. Don't convict on git history alone.
- **AI slop is a spectrum** — code can have some AI slop signals without being entirely
  vibe-coded. Calibrate your assessment.
- **File references always** — include `path/to/file:line_number` for every finding.

## Examples

### Example 1: Sniffing a directory
User says: "sniff src/auth/"
1. Read all source files in src/auth/
2. Check each file against both smell layers
3. Run git log on suspicious files
4. Produce smell report scoped to src/auth/

### Example 2: AI slop check on a PR
User says: "is this PR vibe coded?"
1. Get the PR diff (files changed)
2. Read the changed files in full (not just the diff — context matters)
3. Check against AI slop signals specifically
4. Check commit history and messages for slop patterns
5. Produce focused AI slop assessment

### Example 3: Full codebase sniff
User says: "how smelly is this codebase?"
1. Map source files, identify modules
2. For large codebases, launch parallel agents per module
3. Sniff each module against both layers
4. Synthesize findings, rank worst offenders
5. Produce full smell report with AI slop assessment
