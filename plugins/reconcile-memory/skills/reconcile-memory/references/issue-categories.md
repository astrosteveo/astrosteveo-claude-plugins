# Issue Categories — Detection Criteria

Detailed detection guidance for each category of memory issue. Consult this while analyzing memory files in Phase 1 Step 2 of the main workflow.

## Duplicates and near-duplicates

- Multiple memories describing the same concept, preference, or pattern
- Memories with overlapping scope where one subsumes the other
- Memories that were created at different times but say the same thing in different words
- Look for: same topic keywords, similar phrasing, overlapping file/function references

## Contradictions

- Two or more memories that give conflicting guidance
- A memory that contradicts what is observable in the current codebase
- Memories where one says "do X" and another says "do not X" or "do Y instead"

These are the highest-priority issues — contradictions cause non-deterministic behavior.

## Stale references

Consult `references/staleness-criteria.md` for detailed assessment guidance including confidence levels and type-based decay rates.

- Memories that reference files, functions, classes, endpoints, or patterns that no longer exist in the codebase
- Use `Glob` and `Grep` to verify whether referenced paths and identifiers still exist
- Cross-reference against git history (`git log --oneline -50`, `git log --since="30 days ago"`) to identify completed work and removed features
- Scan the 3-5 most recent chat transcripts (`.jsonl` files sibling to `memory/`) for contradictions, superseded decisions, or confirmation of continued relevance
- Memories about dependencies, tools, or configurations that have since changed
- Pay special attention to memories referencing specific file paths — these go stale fastest
- Assign confidence levels: High (multiple signals agree), Medium (one strong signal), Low (weak signals only — recommend keeping unless user decides)

## Over-specific entries

- Memories that capture a one-time correction rather than a general rule
- Memories so narrowly scoped that they are unlikely to apply again
- Memories that encode a debugging step for a specific incident rather than a reusable pattern

These waste context budget on information with near-zero future value.

## Consolidation candidates

- Multiple small memories on the same topic that could be merged into one coherent entry
- Fragmented information that would be more useful as a single reference
- Related memories spread across multiple files that belong together
