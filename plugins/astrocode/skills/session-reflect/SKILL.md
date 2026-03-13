---
name: session-reflect
user-invocable: false
description: >
  Reflect on the current session to extract lessons learned and persist them
  as auto-memory entries. Scans the conversation for mistakes made, corrections
  received, decisions determined, bugs encountered, and anything that will
  improve future performance. Use when the user says "reflect", "reflect on
  this session", "what did we learn", "session retrospective", or "save what
  we learned". Writes memories using the existing auto-memory format (user,
  feedback, project, reference types) into the project memory directory.
metadata:
  author: astrocode
  version: 1.0.0
  tags:
    - memory
    - reflection
    - learning
---

# Session Reflect

Review the current conversation and extract lessons worth remembering. Write them as auto-memory entries using the existing memory system — same format, same location, same MEMORY.md index.

## Instructions

### Step 1: Scan the conversation

Review the full conversation and identify entries that fall into these categories:

- **Mistakes made** — Approaches that failed, wrong assumptions, bad code generated, things you had to redo. Focus on *why* it went wrong so you can avoid the pattern next time.
- **Corrections received** — Any time the user pushed back, redirected, or said "no, instead do X." These map directly to `feedback` type memories.
- **Decisions determined** — Architecture choices, tool selections, design tradeoffs, or scope decisions made during the session. Include the reasoning.
- **Bugs encountered** — Runtime errors, test failures, unexpected behavior discovered. Include root cause if identified.
- **Codebase insights** — Non-obvious things learned about the project that aren't derivable from just reading the code (e.g., "this API silently fails when X", "these two modules have a hidden coupling").

Skip anything trivial (typo fixes, simple syntax errors) or anything already saved to memory during the session.

### Step 2: Categorize each finding

Map each finding to the appropriate memory type:

| Finding | Memory type |
|---|---|
| Correction or "don't do X" | `feedback` |
| User preference or working style | `user` |
| Architecture decision, bug context, project goal | `project` |
| External resource discovered | `reference` |

### Step 3: Check for duplicates

Read `MEMORY.md` and any existing memory files that might overlap. If an existing memory covers the same ground, update it rather than creating a new file. Do not write duplicate memories.

### Step 4: Draft memory entries

For each finding, draft a memory entry using the standard format:

```
---
name: [concise name]
description: [one-line description — specific enough to judge relevance in future conversations]
type: [user|feedback|project|reference]
---

[Content. For feedback/project types, structure as:]
[Rule or fact]
**Why:** [the reason — what happened that led to this]
**How to apply:** [when and where this matters in future work]
```

### Step 5: Present findings to the user

Before saving anything, present the full list of findings to the user in a summary like:

```
## Session Reflection

### Findings

1. **[Category]:** [Brief description]
   → Memory: `[filename.md]` ([type])

2. **[Category]:** [Brief description]
   → Memory: `[filename.md]` ([type])
```

Ask the user: "Want me to save all of these, or should I adjust any?"

### Step 6: Save approved memories

For each approved finding:
1. Write the memory file to the project memory directory
2. Add a pointer to `MEMORY.md` with a brief description
3. If updating an existing memory, edit in place and update the MEMORY.md description if needed

Report what was saved.

## Important

- **Do not invent lessons.** Only extract what actually happened in the conversation. If the session was clean with no mistakes or corrections, say so — don't force findings.
- **Do not save things the auto-memory system already caught.** If a correction was already saved as a memory during the conversation, skip it.
- **Prefer updating over creating.** If an existing memory file covers similar ground, update it with the new context rather than creating a separate file.
- **Be specific in descriptions.** The `description` field is what determines whether a memory gets loaded in future conversations — vague descriptions mean the memory never gets used.
