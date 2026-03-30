---
name: memory-pruner
description: >
  Consolidates and prunes stale auto-memory files in Claude Code project memory
  directories (~/.claude/projects/*/memory/). Reads MEMORY.md index and individual
  memory files, cross-references against git history, recent codebase activity, and
  chat transcripts to assess relevance. Merges duplicate or overlapping memories and
  removes stale ones. Use when user says "prune memory", "clean up memory",
  "consolidate memories", "audit memory files", "remove stale memories", or
  "memory cleanup".
metadata:
  author: AstroSteveo
  version: 1.0.0
  category: productivity
  tags: [memory, cleanup, maintenance]
---

# Memory Pruner

Consolidate and prune stale auto-memory files so only current, relevant memories are loaded into future conversations.

## Important

Use ultrathink for staleness assessment. Each memory requires careful cross-referencing across multiple sources — git history, codebase state, and chat transcripts. Shallow analysis risks deleting memories the user still relies on.

NEVER delete or modify any memory file without presenting the full plan to the user and receiving explicit confirmation. All changes are destructive and irreversible.

## Step 1: Identify Target Memory Directory

Determine which project's memory to prune.

**Default:** Use the current project's memory directory. Derive it from the working directory:
- Convert the absolute project path to the Claude projects format (replace path separators with `--`, e.g., `C--Users-name-Projects-myproject`)
- The memory directory is `~/.claude/projects/{converted-path}/memory/`

**If the user specifies a different project:** Accept an explicit path to a memory directory, or a project name to resolve under `~/.claude/projects/`.

**If the memory directory is empty or missing:** Tell the user there are no memories to prune and stop.

## Step 2: Inventory All Memories

Read the full contents of every file in the memory directory:

1. Read `MEMORY.md` to get the index of all memories
2. Read every `.md` file in the directory (not just those listed in MEMORY.md — orphaned files count too)
3. For each memory file, extract:
   - Frontmatter fields: `name`, `description`, `type`
   - Body content
   - Any file paths, function names, or specific references mentioned

Build an inventory table:

```
| File | Type | Name | Key References |
|------|------|------|----------------|
| user_role.md | user | User role | — |
| project_dash.md | project | Dash phasing | dash.gd, PlayerController |
| feedback_testing.md | feedback | Test before ship | get_godot_errors, play_scene |
```

Flag any orphaned files (present on disk but missing from MEMORY.md) and any dangling index entries (listed in MEMORY.md but file missing).

## Step 3: Assess Staleness

For each memory, cross-reference against multiple sources to determine if it is still relevant. Consult `references/staleness-criteria.md` for detailed assessment guidance.

### 3a. Git History Analysis

Navigate to the project's working directory (derive from the projects path, reversing the conversion from Step 1) and run:

- `git log --oneline -50` — recent commit history
- `git log --oneline --since="30 days ago"` — recent activity window
- `git log --all --oneline -- {path}` — for any specific file paths referenced in memories
- `git branch -a` — active branches (may indicate ongoing work areas)

Use this to determine:
- Which areas of the codebase are actively being worked on
- Whether referenced files/features still exist or were removed
- Whether project memories about planned work have been completed

### 3b. Codebase Verification

For memories that reference specific files, functions, classes, or patterns:

- Use Glob to check if referenced files still exist
- Use Grep to check if referenced functions/classes still exist
- Read key files if needed to verify architectural claims

### 3c. Chat Transcript Analysis

Chat transcripts are `.jsonl` files stored alongside the `memory/` directory in the project folder. Each line is a JSON object with conversation data.

- Scan the 3-5 most recent transcripts (by modification time) for mentions of each memory's topic
- Look for contradictions, superseded decisions, or confirmation of continued relevance
- Recent discussion of a topic is a signal the memory is still active

### 3d. Content-Based Assessment

Examine each memory's content for internal staleness signals:

- Absolute dates that have passed
- References to "current" or "ongoing" work that may have concluded
- Type-based decay: `project` memories decay fastest, `user` memories decay slowest
- Duplicates or near-duplicates covering the same topic

## Step 4: Build the Recommendation Report

Present a single, comprehensive report to the user. Group recommendations by action:

### Memories to KEEP (no changes)
```
| File | Type | Reason |
|------|------|--------|
| user_role.md | user | Evergreen user context, no contradictions found |
```

### Memories to PRUNE (delete)
```
| File | Type | Reason | Confidence |
|------|------|--------|------------|
| project_dash.md | project | Feature completed in commit abc123, 2 months ago | High |
```

### Memories to MERGE (consolidate)
```
| Files | Into | Reason |
|-------|------|--------|
| feedback_testing.md + feedback_errors.md | feedback_testing.md | Both cover pre-ship validation, overlapping content |
```

### Orphaned / Dangling entries
```
| Issue | Detail |
|-------|--------|
| Orphan: old_note.md | File exists but not in MEMORY.md index |
| Dangling: [Old ref](missing.md) | Index entry points to nonexistent file |
```

Include the confidence level for each prune recommendation (High / Medium / Low). For low-confidence items, note that the user should decide.

## Step 5: Get Bulk Confirmation

Present the full plan and ask the user to confirm in one message:

"Here is the proposed cleanup plan. Please review and confirm:
- **X memories** will be kept as-is
- **Y memories** will be deleted
- **Z memories** will be merged into N consolidated files
- **W orphaned/dangling entries** will be cleaned up

Reply 'yes' to proceed, or tell me which items to change."

Do NOT proceed until the user explicitly confirms. If they want to adjust specific items, update the plan and re-present.

## Step 6: Execute Changes

Once confirmed, execute all changes:

1. **Merges first:** For each merge group:
   - Read all source files
   - Write the consolidated content to the target file, preserving frontmatter format
   - Delete the source files that were merged in (not the target)

2. **Deletions:** Remove each pruned memory file

3. **Orphan cleanup:** Either add orphaned files to MEMORY.md or delete them (based on the confirmed plan)

4. **Rewrite MEMORY.md:** Rebuild the index from scratch based on the remaining files:
   - Read each surviving memory file
   - Generate a one-line entry: `- [Title](filename.md) -- one-line hook`
   - Keep entries under 150 characters each
   - Organize semantically by topic, not alphabetically
   - Keep total index concise (under 200 lines)

5. **Dangling entry cleanup:** Remove any MEMORY.md entries pointing to deleted/nonexistent files

## Step 7: Summary

Present a final summary:

- How many memories existed before
- How many were pruned, merged, kept
- How many remain after cleanup
- Any notes about low-confidence decisions the user may want to revisit

## Examples

### Example 1: Full Memory Cleanup

User says: "prune my memory"

Actions:
1. Detect current project memory at `~/.claude/projects/C--Users-name-Projects-myapp/memory/`
2. Read all 15 memory files and MEMORY.md
3. Cross-reference against git history showing the project shifted from React to Svelte 2 months ago
4. Find 4 stale project memories about React migration planning (completed), 2 duplicate feedback memories about testing
5. Present report: keep 9, prune 4, merge 2 into 1
6. User confirms
7. Execute: delete 4 files, merge 2, rewrite MEMORY.md with 10 entries

Result: Memory directory trimmed from 15 to 10 relevant, non-redundant entries.

### Example 2: Cross-Project Audit

User says: "clean up memory for my epoch project"

Actions:
1. Resolve to `~/.claude/projects/C--Users-name-Projects-epoch/memory/`
2. Inventory 23 memory files across user, feedback, project, and reference types
3. Check git history in the epoch project directory for recent activity
4. Scan recent chat transcripts for topic mentions
5. Find 3 project memories about completed features, 1 orphaned file, 2 merge candidates
6. Present grouped report with confidence levels
7. User confirms with one adjustment
8. Execute changes, rewrite MEMORY.md

Result: 23 memories consolidated to 18, with cleaner index.

## Troubleshooting

**Cannot find project directory from memory path**
Cause: The `~/.claude/projects/` path uses a mangled format (e.g., `C--Users-name-Projects-foo`). The reverse mapping may be ambiguous if multiple drives or symlinks are involved.
Solution: Ask the user to confirm the actual project directory path. Use `ls` on the project folder to verify it contains the expected codebase.

**Chat transcripts are very large**
Cause: `.jsonl` transcript files can be many megabytes for long sessions.
Solution: Only read the last 200 lines of the 3 most recent transcripts. Use Grep to search for specific topic keywords rather than reading entire files.

**Memory file has no frontmatter**
Cause: Older or manually created memory files may lack the `---` delimited YAML frontmatter.
Solution: Treat as an untyped memory. Assess based on content alone. If keeping, add proper frontmatter during the rewrite.

**User wants to prune a specific type only**
Cause: User says "remove stale project memories" rather than a full cleanup.
Solution: Run the full inventory but filter the recommendation report to only the requested type. Keep, merge, and prune decisions should still consider cross-type relationships (e.g., a project memory that supports a feedback memory).
