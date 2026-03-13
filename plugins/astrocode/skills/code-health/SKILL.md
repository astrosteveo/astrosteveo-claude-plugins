---
name: code-health
user-invocable: false
description: >
  Analyzes codebase for tech debt, code quality issues, anti-patterns, and convention
  violations. Identifies complexity hotspots, deprecated usage, inconsistent patterns,
  missing error handling, dead code, and architectural concerns. Use when the user says
  "find tech debt", "code quality review", "check code health", "what needs refactoring",
  "code smells", "check conventions", "are we following best practices", "review code
  quality", or "what should we clean up". Also use when the user runs /code-health.
compatibility: Requires Claude Code with file system access for codebase scanning.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: code-quality
  tags: [tech-debt, code-quality, refactoring, conventions]
---

# Code Health

Analyze the codebase for tech debt, code quality issues, and convention violations. Produce a prioritized report with actionable recommendations.

## Scope

Determine scope based on the user's request:

- **Full health check:** User says "code health", "find tech debt", "what needs refactoring", or similar broad request. Scan the entire codebase.
- **Targeted review:** User points to specific files, directories, or areas of concern. Focus analysis there.
- **Convention check:** User asks about best practices or consistency. Focus on patterns and conventions.

If the scope is ambiguous, ask the user before proceeding.

## Instructions

### Step 1: Understand the Project

1. Read `CLAUDE.md` (if present) to understand the tech stack, architecture, conventions, and project context.
2. Identify the framework, language, and tooling from config files.
3. Note any established patterns, style guides, or conventions already documented.
4. Review the project structure to understand the architectural approach.

### Step 2: Code Smells and Anti-Patterns

Scan for common quality issues:

**Complexity**
- Functions or methods that are excessively long (doing too many things)
- Deeply nested conditionals or loops (arrow code)
- God objects/files — modules that have too many responsibilities
- Complex conditional logic that could be simplified

**Duplication**
- Copy-pasted code blocks across files
- Similar logic implemented differently in multiple places
- Repeated patterns that should be abstracted (only flag if 3+ occurrences)

**Naming and Clarity**
- Inconsistent naming conventions (mixing camelCase and snake_case within same language context)
- Unclear or misleading variable/function names
- Magic numbers or strings without named constants
- Overly abbreviated names that obscure meaning

**Dead Code**
- Unused exports, functions, or variables
- Commented-out code blocks left behind
- Unreachable code paths
- Feature flags or conditional paths that are always true/false

**Error Handling**
- Swallowed exceptions (empty catch blocks)
- Generic catch-all error handlers that hide root causes
- Missing error handling on I/O operations, API calls, or database queries
- Inconsistent error handling patterns across similar operations

### Step 3: Architectural Concerns

Evaluate structural health:

**Separation of Concerns**
- Business logic mixed into route handlers or UI components
- Database queries scattered across unrelated modules instead of centralized
- Tight coupling between modules that should be independent

**Consistency**
- Same problem solved different ways in different parts of the codebase
- Inconsistent file organization or module structure
- Mixed paradigms without clear reasoning (e.g., some routes use middleware pattern, others don't)

**Dependency Health**
- Circular dependencies between modules
- Over-reliance on a single module (fragile bottleneck)
- Inappropriate dependencies (e.g., importing server code in client components)

### Step 4: Tech Debt Markers

Search for explicit and implicit debt:

**Explicit**
- `TODO`, `FIXME`, `HACK`, `XXX`, `TEMP`, `WORKAROUND` comments
- Suppressed linter rules (`eslint-disable`, `noqa`, `@ts-ignore`) — each one is a debt marker
- Pinned dependency versions with comments explaining why

**Implicit**
- Deprecated API or library usage
- Outdated patterns that the framework/language has better alternatives for
- Configuration that contradicts current best practices
- Missing types in TypeScript (excessive `any` usage)
- Test gaps — critical paths without test coverage

### Step 5: Convention Violations

Check for internal consistency:

1. Identify the dominant patterns in the codebase (how most files do things)
2. Flag deviations from those dominant patterns
3. Check adherence to any conventions documented in `CLAUDE.md`, linter configs, or style guides
4. Note where the project's own established patterns are broken

### Step 6: Compile Report

Organize findings into a structured report:

```
## Code Health Report

**Scope:** [What was analyzed]
**Date:** [Current date]

### Summary
Brief overview of overall codebase health — what's working well and what needs attention.

### High Priority (Address soon)
Issues that actively impede development velocity, cause bugs, or will get significantly
worse if left unaddressed.

### Medium Priority (Plan to address)
Issues that increase maintenance burden or reduce code clarity but aren't urgent.

### Low Priority (Nice to have)
Minor improvements, consistency fixes, and cleanup opportunities.

### For each finding:
- **Location:** file:line_number (or directory for architectural concerns)
- **Category:** What type of issue (complexity, duplication, convention, etc.)
- **Description:** What the issue is and why it matters
- **Recommendation:** Specific action to take
- **Effort:** Quick fix / Moderate / Significant refactor
```

Sort findings by priority, then by effort (quick wins first within each priority level).

## Important

- Do NOT modify any code during the analysis unless the user explicitly asks you to fix findings.
- Be pragmatic — not every imperfection is tech debt worth fixing. Focus on issues that actually impact development velocity, reliability, or maintainability.
- Respect existing patterns — if the codebase consistently uses a pattern you wouldn't choose, that's a convention, not a violation. Only flag it if it causes real problems.
- Avoid bike-shedding — don't flag stylistic preferences that have no functional impact and are already consistent within the codebase.
- Distinguish between "different from what I'd do" and "actually problematic." Only report the latter.
- Credit what's done well — note strong patterns and good practices alongside issues. This provides useful context and helps the user understand what to preserve.

## Examples

### Example 1: Full Codebase Health Check
User says: "Check code health" or "Find tech debt"
Actions:
1. Read project config and CLAUDE.md
2. Scan for code smells and anti-patterns across the codebase
3. Evaluate architectural patterns and consistency
4. Search for TODO/FIXME/HACK markers and linter suppressions
5. Check convention adherence
Result: Comprehensive health report with prioritized findings and effort estimates

### Example 2: Targeted Quality Review
User says: "Review the quality of src/lib/" or "What needs refactoring in the API routes?"
Actions:
1. Focus on the specified directory/files
2. Check for quality issues, patterns, and consistency within that area
3. Note how the area relates to the rest of the codebase
Result: Focused quality report for the specified area

### Example 3: Convention Check
User says: "Are we following best practices?" or "Check conventions"
Actions:
1. Identify established patterns in the codebase
2. Find deviations from those patterns
3. Check against framework/language best practices
Result: List of convention violations and inconsistencies with recommendations
