---
description: Detects obvious AI-generated slop in code — patterns that unambiguously indicate code was produced without thought. Narrow by design: only flags findings where the slop signal is clear, not borderline cases. Use when the user says "sniff this code", "check for AI slop", "is this vibe coded", "smell check", or asks whether code looks AI-generated. For broader code-quality concerns (dead code, complexity, security), use the code-quality skill instead.
argument-hint: "[target: file, directory, or PR]"
---

# Code Sniffer

Detect obvious AI-generated slop. Single-purpose: find patterns that no thoughtful human author would plausibly produce.

If `$ARGUMENTS` specifies a target, sniff exactly that.

## How This Differs From Code Quality

`code-quality` reviews everything — security vulnerabilities, dead code, complexity, performance, clean-code concerns. It surfaces nuanced "this could be better" findings and is the right tool for codebase quality assessment.

`code-sniffer` does one thing: catch obvious AI slop. **It is not a security review, performance review, or quality review** — those belong to `code-quality`. If a finding requires a paragraph explaining why it's plausibly slop, it isn't slop — it's a code-quality concern. Recommend running `code-quality` for those.

The signature failure mode of an AI slop detector is over-triggering. A report full of "might be intentional" findings destroys the user's trust in the verdict. The skill earns trust by being conservative and being right, not by being thorough.

## Workflow

### Step 1: Scope

1. **Target specified** — sniff exactly what the user asked for (file, directory, PR).
2. **No target** — ask: "What should I sniff? A specific file, directory, PR, or the whole codebase?"
3. **Whole codebase** — map source files with Glob, skip vendored/generated/build artifacts. For 200+ files, use parallel Agent subagents.

### Step 2: Sniff

Read the code and check against the slop signals in `references/smell-catalog.md`. Each catalog entry includes detection criteria AND the conditions under which the signal is *not* slop — read both before deciding.

The catalog organizes signals by reliability:

- **Strong signals** rarely false-positive: apologetic comments, docstring-on-everything.
- **Conditional signals** require specific gating: defensive against impossible states, ceremony-to-substance ratio, over-specified types, tests that don't test.
- **Context-only signals** amplify confidence in another finding but are never standalone findings: born-complete files, inconsistent style, backwards-compat for new code.

A context-only signal alone is not a finding. It can raise the stink level of a real finding in the same file.

### Step 3: Devil's Advocate

For each candidate finding, construct the strongest defense before reporting it.

The question is not "could this be intentional?" — almost anything could be. The question is: "what's the most plausible non-AI reason a thoughtful author might have written this?"

If you can construct a defense that a careful human might genuinely give, **drop the finding entirely**. Do not downgrade it. Do not include it as a "noted observation." Drop it.

Common defenses that should kill a finding:

- **Defensive against impossible states** — if the language doesn't enforce the impossibility (Python, JS, untyped function args), defending against bad input is reasonable. Only flag when the type system actually guarantees the state cannot occur AND the code is internal (not at a network/user-input boundary).
- **Ceremony-to-substance ratio** — wrapper code (logging, validation, error handling) belongs around important boundaries. Only flag when ceremony surrounds *trivial* substance, like a logging-then-rethrowing wrapper around a one-line getter.
- **Born-complete file** — reference docs, configs, specs, protocol implementations, and small scripts are legitimately born complete. Only flag when paired with another slop signal in the file.
- **Inconsistent style** — multiple authors, gradual house-style migration, FFI boundaries. Only flag when inconsistency is within a single function or short file written in one session.
- **Premature configuration** — flags can be there for upcoming features or A/B tests you can't see. Only flag when you can verify no consumer exists or could.
- **Apologetic comment** — `TODO(#1234):` with a tracked issue is legitimate; a draft branch where the apology IS the work item is legitimate. Only flag committed code on a non-draft branch with no issue reference.

If the only defense is "maybe they did it on purpose" with no plausible reason why, the defense fails. Flag it.

This step is the heart of the skill. The report you produce will be trusted in proportion to how visibly you applied this gate.

### Step 4: Check Git History (borderline cases only)

Only for findings where the Devil's Advocate gate barely held or barely failed:

1. **Birth check** — `git log --follow --diff-filter=A` on the file. Born fully-formed in a single commit is a context signal that boosts confidence in a real finding. It does not create one on its own.
2. **Iteration check** — healthy edit history versus created once and untouched.
3. **Commit message check** — vague messages alongside large diffs.

Git signals are context, never the basis for a finding. A file born complete with no slop signals in the code is just a file that was correct on the first try.

### Step 5: Report

Produce a report following `references/report-format.md`. The report has two non-negotiable sections beyond the findings themselves:

- **Considered and dropped** — the candidate findings you investigated and dropped after Devil's Advocate, with the defense that held. This proves the calibration is honest.
- **What smells clean** — areas that look good. Calibrates the report.

## Rules

- **The skill's value is being trusted.** A trusted "this is slop" verdict is worth more than ten "might be slop" findings.
- **Drop, don't downgrade.** A finding that survives Devil's Advocate is a finding. One that doesn't is dropped, not demoted to a lower stink level.
- **Show the dropped findings.** Every report includes a "considered and dropped" section. A report with findings and no dropped section is not trustworthy.
- **Code references always** — `path/to/file:line_number` for every finding.
- **Unfamiliarity is not slop.** Simple code that works is good code. Conventions you don't recognize might just be the project's house style.

## Examples

**Targeted sniff** — "sniff src/auth/":
1. Read all source files in src/auth/
2. Check each against the catalog
3. Run Devil's Advocate on every candidate
4. Report findings + dropped + clean

**AI slop check** — "is this PR vibe coded?":
1. Get PR diff, read changed files in full
2. Check against the catalog
3. Devil's Advocate on every candidate
4. Git history on the borderline ones
5. Verdict with explicit confidence level

**Full codebase sniff** — "how slop-y is this codebase?":
1. Map source files
2. Parallel agents for large codebases
3. Each agent runs the full workflow including Devil's Advocate
4. Aggregate verdict with dropped-findings transparency
