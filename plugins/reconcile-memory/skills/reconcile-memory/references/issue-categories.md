# Detection Procedures

Concrete checks to run while analyzing memory files in Phase 1 Step 2. The category names and one-line summaries live in SKILL.md; this reference adds the verifiable procedures and pattern-matching cues that don't fit there.

## Verifying stale references

Cross-reference each memory against the live codebase and recent activity:

- Use `Glob` and `Grep` to check whether referenced files, functions, classes, endpoints, or identifiers still exist at the named paths.
- Run `git log --oneline -50` and `git log --since="30 days ago"` to identify completed work, removed features, or renames that would invalidate a memory.
- Scan the 3-5 most recent chat transcripts (`.jsonl` files sibling to the `memory/` directory) for explicit supersession, contradiction, or confirmation of continued relevance.
- Apply the type-based decay rates and confidence-level definitions in `references/staleness-criteria.md`. `project` memories decay fastest; `user` memories slowest.
- Memories that name specific file paths go stale fastest. Verify these first.

## Spotting duplicates and near-duplicates

Pattern-match on:

- Same topic keywords, similar phrasing, or overlapping file/function references across two memories.
- One memory's scope fully contained inside another's (the larger subsumes the smaller).
- Two memories created at different times that say the same thing in different words — common when a follow-up conversation re-records a decision the original session already captured.

## Spotting consolidation candidates

Look for:

- Multiple short memories on the same topic, scattered across separate files.
- Topic-related entries that have drifted into separate files over time and would read more clearly merged.
- Fragmented information where each piece is below the threshold for being useful in isolation.

## Index integrity checks

While reading the directory, verify `MEMORY.md` against disk:

- **Orphaned file** — present on disk, not referenced from `MEMORY.md`. Either add an index entry or delete if the content is duplicated elsewhere.
- **Dangling index entry** — `MEMORY.md` points at a file that does not exist. Remove the line.
