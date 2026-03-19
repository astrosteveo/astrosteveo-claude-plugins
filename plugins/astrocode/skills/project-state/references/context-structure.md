# Context Structure Reference

Detailed specs for `.agents/CONTEXT.md` and topic files.

## CONTEXT.md

The index file. It is the first thing an agent reads when starting a session. Design it to give a complete orientation in under 60 seconds of reading.

### Principles

- **Thin index** — CONTEXT.md points to topic files, it does not contain deep detail itself
- **Scannable** — Use tables, bullet lists, and short descriptions. No prose paragraphs
- **Current** — The `Last updated` timestamp tells the agent how fresh the context is
- **Complete** — Every topic file in `.agents/` must be linked from the Topics table

### Section Guidelines

**Overview** — What the project is, in 1-3 sentences. Answer: "If I've never seen this codebase, what is it?"

**Stack** — Key-value pairs only. No explanations of why a tool was chosen. Just what's in use.

**Structure** — Top 2-3 levels of the directory tree. Annotate each entry with its purpose. Omit generated directories (node_modules, dist, __pycache__).

**Active Work** — What's being worked on right now. Include in-progress features, known bugs being addressed, and upcoming priorities. Keep to 3-5 bullet points.

**Topics** — Table linking to every `.md` file in `.agents/` (except CONTEXT.md itself). Each row: topic name, relative link, one-line description.

## Topic Files

Each topic file covers one area of the project in detail. They follow this structure:

```markdown
# {Topic Name}

> Part of [Project Context](CONTEXT.md)

## {Section 1}

{Details}

## {Section 2}

{Details}
```

### Default Topic Files

**architecture.md**

Covers:
- High-level architecture (monolith, microservices, monorepo, etc.)
- Key directories and what they contain
- Important patterns (how data flows, how components communicate)
- Naming conventions and code organization rules
- Design decisions that are not obvious from the code

**status.md**

Covers:
- Current work streams (what's actively being developed)
- Recent changes (last 5-10 significant changes with dates)
- Known issues and technical debt
- Next steps and upcoming priorities
- Blockers or risks

### Optional Topic Files

Create these only when the project has enough complexity to warrant them:

**dependencies.md** — Key external dependencies, what they do, version constraints, known issues with specific versions.

**testing.md** — How to run tests, test structure, coverage expectations, test data setup, integration test requirements.

**deployment.md** — Deployment pipeline, environments (dev/staging/prod), configuration management, rollback procedures.

**api.md** — API endpoints, request/response formats, authentication, rate limits, versioning strategy.

### Topic File Guidelines

- Keep each file under 200 lines. If it grows beyond that, split into subtopics
- Start with a back-link to CONTEXT.md for navigation
- Use headers, tables, and code blocks for scannability
- Include concrete examples where they help (e.g., example API calls, example directory paths)
- Date-stamp volatile information (status, known issues) so staleness is visible
- Do not duplicate information that's in CONTEXT.md — reference it instead
