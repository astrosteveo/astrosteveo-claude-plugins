# Reconciliation Report Templates

Output skeletons for Phase 2 of the reconcile-memory workflow. Copy the structure verbatim and fill in the bracketed placeholders. If the extended audit was performed, append matching sections for rules, project CLAUDE.md, and global CLAUDE.md conflicts.

## Step 4 — Audit Report

```
## Memory Audit Report

**Project:** [project path]
**Files scanned:** [count]
**Total memory size:** [size]
**Issues found:** [count by category]

### Critical: Contradictions ([count])

1. **[Short description]**
   - File A: `memory/foo.md` says: "[quoted content]"
   - File B: `memory/bar.md` says: "[quoted content]"
   - Impact: [why this is problematic]
   - Recommendation: [keep A / keep B / rewrite as ...]

### Duplicates ([count])

1. **[Topic]**
   - File A: `memory/foo.md` — "[summary]"
   - File B: `memory/bar.md` — "[summary]"
   - Recommendation: Merge into `memory/foo.md` as: "[proposed merged content]"

### Stale References ([count])

1. **[Reference description]**
   - File: `memory/foo.md` says: "[quoted content]"
   - Verified: [file/function/path] no longer exists
   - Confidence: [High / Medium / Low]
   - Recommendation: Remove / Update to [current state]

### Over-Specific Entries ([count])

1. **[Description]**
   - File: `memory/foo.md` says: "[quoted content]"
   - Why: [one-time fix / too narrow / incident-specific]
   - Recommendation: Remove

### Consolidation Opportunities ([count])

1. **[Topic]**
   - Files: `memory/a.md`, `memory/b.md`, `memory/c.md`
   - Recommendation: Merge into single `memory/[topic].md`
   - Proposed content: "[merged content]"

### Orphaned / Dangling Entries ([count])

1. **[Issue type]**
   - Detail: [Orphan: file exists but not in MEMORY.md / Dangling: index entry points to nonexistent file]
   - Recommendation: [Add to index / Remove file / Remove index entry]
```

## Step 5 — Execution Plan

```
## Proposed Changes

1. DELETE `memory/bar.md` (duplicate of foo.md)
2. EDIT `memory/foo.md` — merge content from bar.md
3. DELETE `memory/stale-reference.md` (references removed files)
4. EDIT `memory/MEMORY.md` — remove pointer to deleted files
5. ...

Total: [X] deletions, [Y] edits, [Z] merges
Net reduction: [N] files, ~[size] of context
```
