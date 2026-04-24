# Slop Report Format

How to structure code-sniffer findings.

## Stink Levels

| Level | Label | Meaning |
|-------|-------|---------|
| 1 | Stale | One unambiguous slop signal that survived Devil's Advocate. |
| 2 | Funky | Multiple converging slop signals in the same code. |
| 3 | Rotten | Pervasive slop across a file or module. Strong evidence of unreviewed generation. |
| 4 | Biohazard | Code that creates false confidence — hollow tests that look like coverage, error handling that hides errors. |

There is no Whiff level. **If a finding is "might be intentional," it is not a finding — drop it.**

### Calibration

- A typical sniff on a moderately-sized file should yield 0-2 findings. Five findings on a 200-line file usually means over-triggering, not heavy slop. Re-run Devil's Advocate.
- Biohazard is rare. Reserve it for code that misleads the reader about what it does — hollow tests labeled as real tests, error handlers that swallow errors silently.
- A context-only signal (born-complete, style inconsistency, backwards-compat for new code) raises an existing finding's stink level by one. It does not create a finding on its own.
- Security and quality issues are out of scope. If you spot one in passing, mention it briefly and recommend `code-quality`. Do not list it as a slop finding.

## Report Structure

### 1. Verdict Summary

2-3 sentences. State the verdict directly.

Required:
- Total findings count by stink level
- AI slop verdict: Clean / Some signals / Significant slop / Heavy slop
- Confidence: Low / Medium / High
- Single worst offender (file or pattern), or "none" if the codebase is clean

### 2. Findings

Group by slop signal. If the same signal appears in multiple files, report it once with all locations.

Each finding:

**[Stink Level] Signal Name** — `path/to/file:line`

_Evidence:_ the actual code (short snippet, not paraphrase).

_Why it's slop:_ which catalog signal it matches and how the code matches the gate criteria.

_Devil's Advocate considered:_ the strongest defense you constructed, and why it failed (e.g., "could be defending against API misuse, but the function is private, the type system already prevents the state, and there's no recovery — just a throw").

If the same signal shows up across multiple files, list all locations and describe the pattern once.

### 3. Considered and Dropped

**Required.** List candidate findings you investigated and dropped after Devil's Advocate. For each:

**[Pattern]** — `file:line`

_What I saw:_ the code that triggered the consideration.
_Why I dropped it:_ the Devil's Advocate defense that held.

If you have no dropped findings, say so explicitly: "No candidates were dropped — every signal investigated led to a confirmed finding." This outcome is rare and worth noting if it happens.

This section proves the calibration is honest. **A report with findings and no dropped section is not trustworthy.**

### 4. Slop Verdict

A focused assessment.

- **Verdict:** Clean / Some signals / Significant slop / Heavy slop
- **Evidence for:** specific slop signals found, with file references
- **Evidence against:** signs of human authorship — iterative git history, calibrated documentation, voice consistency, targeted comments, etc.
- **Confidence:** Low / Medium / High

Be honest about uncertainty. Some human code looks AI-generated. Some AI code is well-reviewed and clean. The verdict is probabilistic, not definitive.

### 5. What Smells Clean

Briefly note areas of the codebase that smell good. This calibrates the report and prevents it from being purely negative. Skipping this section is a sign the report is biased toward findings.

## Tone

- **Direct, irreverent, evidence-based.** "This `def get_name(): \"\"\"Gets the name.\"\"\"` is the LLM-default docstring pattern" — not "Consider whether the documentation adds value."
- **Conservative.** Trust is earned by being right, not by being thorough.
- **Fair.** Always note the alternative interpretation you considered. The Devil's Advocate defense — even when it fails — should appear in the finding so the reader can judge the call.
- **Not cruel.** Describe the code, not the coder. The goal is to help the user trust their codebase, not to mock whoever wrote it.
