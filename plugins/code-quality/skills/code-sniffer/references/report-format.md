# Smell Report Format

How to structure and present code sniffer findings.

## Stink Levels

Forget traditional severity ratings. Smelly code gets stink levels:

| Level | Label | Meaning |
|-------|-------|---------|
| 1 | Whiff | Faint smell. Might be intentional. Worth noting. |
| 2 | Stale | Noticeable smell. Probably not intentional. Should be addressed. |
| 3 | Funky | Clearly smells bad. Multiple smell signals in the same code. |
| 4 | Rotten | Unmistakably bad. Strong evidence of thoughtless generation. |
| 5 | Biohazard | Dangerously smelly. Ceremonial security, tests that test nothing, code that actively misleads about what it does. |

### Calibration

- Most findings should be Stale (2) or Funky (3)
- Biohazard (5) is reserved for code that creates false confidence — security that
  doesn't secure, tests that don't test, error handling that hides errors
- A single AI slop signal is a Whiff. Multiple signals in the same file raise the level.
- Git history confirming born-complete status adds +1 to any finding in that file.

## Report Structure

### 1. Quick Sniff Summary

2-3 sentences. How does this code smell overall? Is it clean, musty, or a dumpster fire?

Include:
- Total findings count by stink level
- Whether AI slop signals were detected (yes/no/maybe)
- The single worst offender (file or pattern)

### 2. Findings

Group by smell pattern, not by file. If the same smell appears in 10 files, report it
once with all locations.

Each finding:

**[Stink Level] Smell Pattern Name** — `path/to/file:line`

What: 1-2 sentences describing what you see.

Why it stinks: The specific reason this code suggests thoughtlessness. Connect to the
smell catalog entry.

Evidence: the code snippet or pattern (keep short — show the pattern, not the whole file).

AI slop? Yes/No — if yes, which specific slop signal(s) from the catalog.

### 3. AI Slop Assessment

A dedicated section answering: does this code show signs of AI generation or vibe coding?

Structure:
- **Verdict**: Clean / Some signals / Likely AI-assisted / Probably vibe-coded
- **Evidence for**: list the specific AI slop signals found, with file references
- **Evidence against**: list signs of human authorship (iterative git history, targeted
  documentation, calibrated error handling, etc.)
- **Confidence**: How confident are you in this assessment? Low/Medium/High

Be honest about uncertainty. Some human code looks AI-generated. Some AI code is
well-reviewed and clean. The assessment is probabilistic, not definitive.

### 4. Worst Offenders

Top 3-5 files or modules ranked by smell density. For each:
- File path
- Stink level (highest finding in that file)
- Primary smells detected
- One-sentence summary of the problem

### 5. What Smells Clean

Briefly note areas of the codebase that smell good. Calibrates the report and
prevents it from being purely negative.

## Tone

- **Direct and irreverent** — this tool is opinionated by design. "This function has
  a docstring that restates the function name" not "Consider whether the documentation
  adds value."
- **Evidence-based** — every opinion backed by a specific code reference
- **Fair** — acknowledge when a pattern that looks like slop might be intentional.
  Always note the alternative interpretation.
- **Not cruel** — the goal is to help improve code, not to mock whoever wrote it.
  Describe the code, not the coder.
