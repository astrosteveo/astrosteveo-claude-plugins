# Skill Fundamentals

## What Is a Skill?

A skill is a folder containing instructions that teach Claude how to handle specific tasks or workflows. Instead of re-explaining preferences, processes, and domain expertise every conversation, skills let you teach Claude once and benefit every time.

Skills are powerful for repeatable workflows: generating frontend designs from specs, conducting research with consistent methodology, creating documents that follow style guides, or orchestrating multi-step processes.

## Folder Contents

```
your-skill-name/
├── SKILL.md                # Required — main skill file
├── scripts/                # Optional — executable code
│   ├── process_data.py
│   └── validate.sh
├── references/             # Optional — documentation loaded as needed
│   ├── api-guide.md
│   └── examples/
└── assets/                 # Optional — templates, fonts, icons
    └── report-template.md
```

## Critical Naming Rules

**SKILL.md:**
- Must be exactly `SKILL.md` (case-sensitive)
- No variations: ~~SKILL.MD~~, ~~skill.md~~, ~~Skill.md~~

**Folder name:**
- kebab-case only: `notion-project-setup`
- No spaces: ~~`Notion Project Setup`~~
- No underscores: ~~`notion_project_setup`~~
- No capitals: ~~`NotionProjectSetup`~~

**No README.md** inside the skill folder. All documentation goes in SKILL.md or `references/`.

## Progressive Disclosure

Skills use a three-level system to minimize token usage:

1. **Level 1 — YAML frontmatter:** Always loaded in Claude's system prompt. Provides just enough for Claude to know when the skill should be used.
2. **Level 2 — SKILL.md body:** Loaded when Claude thinks the skill is relevant. Contains the full instructions.
3. **Level 3 — Linked files:** Additional files in `references/`, `scripts/`, `assets/` that Claude loads only as needed.

Keep SKILL.md focused on core instructions. Move detailed documentation to `references/` and link to it.

## Composability

Claude can load multiple skills simultaneously. Your skill should work well alongside others — don't assume it's the only capability available.

## Portability

Skills work across Claude.ai, Claude Code, and the API. Create once, use everywhere — provided the environment supports any dependencies the skill requires.

## Skills + MCP

If the skill enhances an MCP integration:

| MCP (Connectivity) | Skills (Knowledge) |
|---|---|
| Connects Claude to your service | Teaches Claude how to use the service effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What Claude **can** do | How Claude **should** do it |

**Without skills:** Users connect MCP but don't know what to do next, results are inconsistent, each conversation starts from scratch.

**With skills:** Pre-built workflows activate automatically, consistent and reliable tool usage, best practices embedded in every interaction.
