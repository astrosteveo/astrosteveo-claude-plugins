---
description: Audits and reconciles Claude Code auto-memory files. Finds duplicates, contradictions, stale references, and over-specific entries that degrade session quality through context poisoning.
disable-model-invocation: true
argument-hint: "[--full to include rules and CLAUDE.md]"
---

# Reconcile Memory

Audit and reconcile auto-memory files for the current project. Identifies duplicates, contradictions, stale references, and over-specific entries that silently degrade session quality through context poisoning and attention dilution.

## Why This Matters

Auto-memory accumulates monotonically with no built-in cleanup. Every memory file is injected into the context window at session start, where it competes for attention with everything else. Stale, contradictory, or duplicate memories don't throw errors -- they silently shift the probability distribution of outputs. This skill gives you a way to periodically defragment your context.

## Current Project Memory Location

!`bash ${CLAUDE_SKILL_DIR}/scripts/find-memory-dirs.sh`

## Important

Staleness assessment requires careful cross-referencing across multiple sources — git history, codebase state, and chat transcripts. Shallow analysis risks deleting memories the user still relies on.

NEVER delete or modify any memory file without presenting the full plan to the user and receiving explicit confirmation. All changes are destructive and irreversible.

## Instructions

This skill operates in three phases: **Analyze**, **Report and Plan**, then **Execute**. Never modify files without explicit user approval.

### Phase 1: Analyze

#### Step 1: Locate and Read Memory Files

**Default:** Identify the correct memory directory for the current project from the output above.

**Cross-project:** If the user specifies a different project, accept an explicit path to a memory directory or a project name to resolve under `~/.claude/projects/`.

1. If multiple directories are listed and the target is ambiguous, ask the user which project to audit
2. If no directories are found, inform the user that no auto-memory exists for any project and stop
3. Read `MEMORY.md` in full -- this is the index file
4. Read every file referenced from `MEMORY.md` and every `.md` file in the memory directory (orphaned files count too)
5. For each memory file, extract frontmatter fields (`name`, `description`, `type`) and body content
6. Note the total number of files and approximate total size
7. Flag any orphaned files (present on disk but missing from MEMORY.md) and any dangling index entries (listed in MEMORY.md but file missing)

#### Step 2: Analyze for Issues

Classify issues into five categories. For each issue found, record the specific file(s), the relevant content, and why it is problematic.

- **Contradictions** — conflicting guidance across memories, or memory vs. observable code. Highest priority; these cause non-deterministic behavior.
- **Duplicates and near-duplicates** — the same concept expressed across multiple files or in different words.
- **Stale references** — memories pointing at files, functions, paths, or dependencies that no longer exist.
- **Over-specific entries** — one-time corrections or incident-specific debugging steps with no reusable value.
- **Consolidation candidates** — multiple small memories on the same topic that belong together.

Consult `references/02-issue-categories.md` for detection criteria and cross-reference procedures (git log, transcripts, confidence levels) for each category.

#### Step 3: Check Extended Context (if --full or user requests)

If the user passes `--full` or asks for a complete audit, also scan:

1. **`.claude/rules/` files** in the project directory:
   - Rules that contradict each other
   - Rules that contradict memory entries
   - Rules referencing stale file paths or patterns
   - Overly broad rules that may cause false triggers

2. **Project CLAUDE.md** (`./.claude/CLAUDE.md` or `./CLAUDE.md`):
   - Instructions that conflict with memory entries or rules
   - Stale references to project structure that has changed
   - Overly verbose sections that could be trimmed

3. **Global CLAUDE.md** (`~/.claude/CLAUDE.md`):
   - Preferences set for a different project that bleed into all sessions
   - Instructions that conflict with project-level guidance
   - Content that should be project-scoped rather than global

4. **Cross-source conflicts**:
   - Memory says X, but a rule says Y
   - Global CLAUDE.md says X, but project CLAUDE.md says Y
   - Any instruction that appears in multiple places with different wording

### Phase 2: Report and Plan

#### Step 4: Present the Reconciliation Report

Present findings in this structure:

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
   - File A: `memory/foo.md` -- "[summary]"
   - File B: `memory/bar.md` -- "[summary]"
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

If the extended audit was performed, add sections for rules, project CLAUDE.md, and global CLAUDE.md conflicts using the same format.

#### Step 5: Present the Execution Plan

After the report, present a concrete action plan:

```
## Proposed Changes

1. DELETE `memory/bar.md` (duplicate of foo.md)
2. EDIT `memory/foo.md` -- merge content from bar.md
3. DELETE `memory/stale-reference.md` (references removed files)
4. EDIT `memory/MEMORY.md` -- remove pointer to deleted files
5. ...

Total: [X] deletions, [Y] edits, [Z] merges
Net reduction: [N] files, ~[size] of context
```

**Wait for explicit user approval before proceeding.** The user may want to:
- Approve all changes
- Approve selectively (e.g., "do 1-3 but skip 4")
- Modify a recommendation before execution
- Reject the plan entirely

### Phase 3: Execute

#### Step 6: Execute Approved Changes

Only after the user explicitly approves:

1. Execute changes in this order:
   - Edits and merges first (preserve content before deleting sources)
   - Deletions second
   - MEMORY.md index updates last
2. For each change, briefly confirm what was done
3. After all changes, show a summary:
   - Files before: [count]
   - Files after: [count]
   - Estimated context reduction: [size/lines]

#### Step 7: Verify

After execution:
1. Read `MEMORY.md` to verify the index is consistent with remaining files
2. Check that no orphaned references remain
3. Report the final state

## Examples

### Example 1: Routine audit
User says: "/reconcile-memory"
Actions: Locate memory dir, read all files, analyze, present report, wait for approval, execute
Result: Consolidated memories with duplicates removed and stale references cleaned up

### Example 2: Full context audit
User says: "/reconcile-memory --full"
Actions: Same as above plus scan rules, project CLAUDE.md, global CLAUDE.md for cross-source conflicts
Result: Clean, non-contradictory context across all persistent injection points

### Example 3: Targeted check
User says: "my memories are getting bloated, can you clean them up"
Actions: Focus on volume reduction -- identify merge candidates and over-specific entries
Result: Reduced file count with no loss of meaningful context

## Troubleshooting

**No memory directory found**
The current project may not have auto-memory enabled, or no memories have been written yet. Check `~/.claude/projects/` to see which projects have memory directories. The directory name is derived from the git repository path.

**User disagrees with a recommendation**
Adjust the plan per the user's feedback. Never argue about whether a memory is stale -- the user has context you may not have.

**Memory references code that might exist in another branch**
If a memory references something you cannot find, flag it but note that it may exist in a branch you have not checked. Let the user decide.

**Very large memory directory (20+ files)**
Start with contradictions and stale references first -- these have the highest impact. Present the report in batches if the full report would be overwhelming.

**Chat transcripts are very large**
`.jsonl` transcript files can be many megabytes for long sessions. Only read the last 200 lines of the 3 most recent transcripts. Use Grep to search for specific topic keywords rather than reading entire files.

**Memory file has no frontmatter**
Older or manually created memory files may lack the `---` delimited YAML frontmatter. Treat as an untyped memory. Assess based on content alone. If keeping, add proper frontmatter during the rewrite.

**User wants to prune a specific type only**
Run the full inventory but filter the recommendation report to only the requested type. Keep, merge, and prune decisions should still consider cross-type relationships.
