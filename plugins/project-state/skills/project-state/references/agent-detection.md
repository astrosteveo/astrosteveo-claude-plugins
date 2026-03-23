# Agent Detection Reference

Complete list of agent configuration files to detect and how to inject the state pointer into each.

## Detection Order

Search the project root for these files. Check all of them — a project may have multiple.

| Priority | File | Agent | Notes |
|----------|------|-------|-------|
| 1 | `CLAUDE.md` | Claude Code | Auto-loaded into context |
| 2 | `AGENTS.md` | Multi-agent / generic | Emerging standard |
| 3 | `.cursorrules` | Cursor | Project-level rules |
| 4 | `.github/copilot-instructions.md` | GitHub Copilot | Inside .github directory |
| 5 | `GEMINI.md` | Gemini | Google AI agent |
| 6 | `.windsurfrules` | Windsurf (Codeium) | Project-level rules |
| 7 | `COPILOT.md` | GitHub Copilot | Alternative location |
| 8 | `.ai/README.md` | Various | Convention in some projects |

## Injection Strategy

### General Rules

1. **Append, don't overwrite** — Always add the pointer as a new section at the end of the file
2. **Check for existing pointer** — Search the file for `.agents/` before injecting. If a pointer already exists, skip
3. **Preserve formatting** — Match the existing file's heading style (# vs ## vs ###)
4. **Add a blank line** — Ensure there's a blank line before the injected section

### Pointer Templates

**For markdown files (CLAUDE.md, AGENTS.md, GEMINI.md, COPILOT.md):**

```markdown

## Project State

This project maintains persistent agent state in `.agents/`.
Read `.agents/CONTEXT.md` at the start of each session to orient yourself.
Update the relevant files in `.agents/` after completing meaningful units of work.
```

**For rule files (.cursorrules, .windsurfrules):**

These files use plain text or markdown-like syntax without strict structure. Append:

```
# Project State

This project maintains persistent agent state in .agents/.
Read .agents/CONTEXT.md at the start of each session to orient yourself.
Update the relevant files in .agents/ after completing meaningful units of work.
```

**For nested files (.github/copilot-instructions.md, .ai/README.md):**

Same as the markdown template. Ensure the parent directory exists before writing.

## Fallback Behavior

If no agent configuration file is detected:

1. Create `CLAUDE.md` in the project root
2. Add a minimal header: `# Project Guidelines`
3. Add the pointer section
4. Inform the user that `CLAUDE.md` was created as the default

## Detecting Existing Pointers

Before injecting, check if the file already contains a reference to `.agents/`:

- Search for `.agents/` or `agents/CONTEXT` in the file content
- If found, do not inject a duplicate pointer
- If the existing pointer is outdated or incomplete, update it in place rather than appending a new one
