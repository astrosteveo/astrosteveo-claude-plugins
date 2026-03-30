# Staleness Assessment Criteria

## Signal Sources

### 1. Git History

Run `git log` in the project directory associated with the memory. Look for:

- **Recent activity areas:** Which files/directories have the most commits in the last 30 days? Memories about inactive areas are candidates for pruning.
- **Deleted or renamed files:** If a memory references a specific file path, check if that file still exists. If it was renamed, the memory may need updating rather than pruning.
- **Completed work:** If a `project` memory describes work that git history shows was completed (merged PRs, closed branches), it is stale.
- **Reverted decisions:** If git history shows a referenced approach was abandoned or replaced, the memory is stale.

### 2. Codebase State

Use Grep and Glob to verify references in memories:

- **Functions/classes mentioned:** Do they still exist? Have they been renamed?
- **File paths mentioned:** Do the files still exist at those paths?
- **Architecture claims:** Does the code still follow the pattern the memory describes?
- **Tool/dependency references:** Are the referenced tools still in use?

### 3. Chat Transcripts

Chat transcripts are stored as `.jsonl` files in the project directory (sibling to the `memory/` folder). Each line is a JSON object representing a conversation turn.

- **Recent mentions:** Was the memory topic discussed recently? If so, it may still be relevant.
- **Contradictions:** Did a recent conversation establish something that contradicts the memory?
- **Superseded decisions:** Did the user explicitly change direction on something a memory records?

### 4. Memory Content Analysis

Examine the memory itself for staleness signals:

- **Absolute dates:** If the memory mentions a date that has passed (e.g., "merge freeze begins 2026-03-05"), check if the event is still relevant.
- **Relative time language:** Words like "currently", "right now", "this week" suggest time-bound information that may have expired.
- **Specificity vs. generality:** Highly specific project memories decay faster than general user preferences or feedback.
- **Type-based decay rates:**
  - `user` — Slow decay. Preferences and background rarely change. Only prune if contradicted.
  - `feedback` — Medium decay. Guidance may become irrelevant if the project's tech stack or workflow changes significantly.
  - `project` — Fast decay. Ongoing work, deadlines, and initiatives change frequently.
  - `reference` — Medium decay. External systems may move or be decommissioned.

## Confidence Levels

Assign each memory a confidence level for the staleness verdict:

- **High confidence stale:** Multiple signals agree (file deleted + not mentioned recently + time-bound content expired)
- **Medium confidence stale:** One strong signal (referenced file deleted) but no contradicting signals
- **Low confidence stale:** Weak signals only (just hasn't been mentioned recently) — recommend keeping unless user decides otherwise
- **Not stale:** Active references in code, recent chat mentions, or evergreen content

## Merge Candidates

Two or more memories should be merged when:

- They cover the same topic from different angles (e.g., two `feedback` memories about testing practices)
- One is a subset of another (e.g., a specific memory and a general memory about the same area)
- They were created at different times but describe the same evolving decision
- Combined, they would be under ~30 lines and coherent as a single memory

When merging, preserve the most current information and the strongest reasoning. Keep the filename of the more comprehensive memory and delete the other(s).
