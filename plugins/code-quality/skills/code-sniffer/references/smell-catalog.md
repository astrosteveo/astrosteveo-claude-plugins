# AI Slop Catalog

Patterns that indicate code was generated without thought. Each entry includes:

- **Signal:** what the pattern looks like
- **What makes it slop:** the specific feature that distinguishes thoughtless generation from legitimate code
- **Devil's Advocate defense:** the most plausible non-slop interpretation, and the conditions under which it holds
- **When to flag:** the gate the finding must pass

Signals are organized by reliability. **Strong signals** rarely false-positive. **Conditional signals** require specific gating. **Context-only signals** amplify confidence in another finding but never create one on their own.

## Out of scope

This catalog does not cover security vulnerabilities, performance issues, dead code, or general code-quality concerns. Use the `code-quality` skill for those — it is the codebase-quality reviewer; this skill is the AI-slop detector. If a sniff turns up a real security or quality issue, mention it briefly in the report and recommend running `code-quality`.

---

## Strong Signals

These rarely false-positive. If the pattern matches and Devil's Advocate fails, flag it.

### Apologetic Comments

**Signal:** Comments that acknowledge the code is incomplete or non-production:

- `// This is a simplified version...`
- `// For production, you'd want to...`
- `// In a real application, this should...`
- `// TODO: implement proper error handling`
- `// Note: this is a basic implementation`
- `// Placeholder for future enhancement`

**What makes it slop:** Humans don't apologize in committed code. They either fix the limitation or file a tracked issue. These comments are artifacts of an AI conversation where the model hedged and the human committed without removing the hedge.

**Devil's Advocate defense:** A `TODO(#1234):` with a tracked issue number is legitimate. A draft branch where the apology IS the work item is legitimate. A comment in a tutorial/example file that calls itself a "simplified example" is legitimate.

**When to flag:** Apologetic comment in committed code on a non-draft branch with no issue reference and no "this is intentionally simplified" framing.

### Docstring-on-Everything

**Signal:** Every function, method, and class has a docstring, including trivial ones that just restate the signature:

- `def get_name(): """Gets the name."""`
- `def __init__(): """Initialize the class."""`
- JSDoc/Javadoc on private helpers called from one place
- Type annotations AND docstrings that say the same thing

**What makes it slop:** Humans document selectively, where behavior isn't obvious from the name. Blanket documentation is the LLM default — the model adds a docstring to every function regardless of whether one helps.

**Devil's Advocate defense:** Public APIs (libraries, SDKs) where every function is part of the contract require docstrings. Style guides that mandate docstrings on every function exist. Generated code (Protobuf, OpenAPI) has uniform documentation.

**When to flag:** Internal/private code where every function — including `__init__`, getters, and one-line helpers — has a docstring that restates the signature, and there is no indication the project requires this style (no docstring linter, no contributor guide).

---

## Conditional Signals (require gating)

These match real slop *and* real legitimate patterns. The gate determines which.

### Defensive Code Against Impossible States

**Signal:** Checks for conditions that cannot occur given the type system or surrounding control flow:

- Null/nil checks on values typed as non-null
- Type checks in strongly-typed languages where the type is already known
- Length checks on collections just populated by the preceding code
- Redundant validation of data validated upstream

**What makes it slop:** AI defaults to defending every edge case regardless of context. Humans trust their own code and the type system.

**Devil's Advocate defense:** In dynamically-typed languages (Python, JS, Ruby) defending against unexpected callers is reasonable. At system boundaries (network requests, user input, deserialization, IPC) defensive checks are correct. In safety-critical code, paranoid checks may be required by policy.

**When to flag:** All three must hold:
1. The state is *impossible per the type system* (TypeScript with strict null checks, Rust, Kotlin, Swift) — not just unlikely.
2. The code is internal — not at a network/user-input/deserialization boundary.
3. The check serves no recovery — it just throws or logs and continues.

### High Ceremony-to-Substance Ratio

**Signal:** A file where wrapper code (validation, logging, error handling, type declarations) dominates the actual logic by 3:1 or more.

**What makes it slop:** AI treats every context the same and applies thorough ceremony to trivial code.

**Devil's Advocate defense:** Public API surfaces, security-sensitive boundaries, well-tested critical paths, and middleware legitimately have high ceremony for good reasons. Configuration objects with validators are not slop. A 200-line file with a 30-line core function but 170 lines of well-justified boundary handling is fine.

**When to flag:** Both must hold:
1. The substance the ceremony surrounds is *trivial* — a getter, a one-line transformation, a pass-through, a constant lookup.
2. The ceremony is generic and serves no specific purpose — `try/log/rethrow` patterns, validating already-validated input, logging that no one will read.

### Over-Specified Types and Structures

**Signal:** Type definitions more complex than the data warrants:

- Generic types with 3+ parameters for simple data
- Nested interfaces 4+ levels deep
- Enum with 2 values wrapped in a class with methods
- Config objects with 15+ optional fields where most are never set
- Abstract base types for data that is always concrete

**What makes it slop:** AI generates comprehensive type hierarchies by default. Humans start simple and add complexity when actual data demands it.

**Devil's Advocate defense:** Library code, framework abstractions, and domain models from regulated/specified domains (finance, healthcare, telecom) often legitimately have rich type hierarchies. Type-driven development is a valid style.

**When to flag:** Application-level code where the type hierarchy serves no observable purpose — no branching on the variants, no consumers of the optional fields, no inheritance actually being used polymorphically.

### Tests That Don't Test

**Signal:** Test suites that provide coverage numbers without verifying behavior:

- `expect(result).toBeTruthy()` / `assert result` / `assertNotNull(result)`
- Tests where the assertion is on the mock, not the system under test
- Tests that verify implementation details (call order, internal state) instead of outcomes
- One-line test bodies: call function, assert no error thrown
- Setup that mocks away the component under test

**What makes it slop:** AI generates tests to satisfy "write tests for this" without understanding what's worth testing. The tests look complete but catch nothing.

**Devil's Advocate defense:** Smoke tests are intentionally shallow. Boundary tests on third-party integrations may legitimately just verify "doesn't throw." Tests in early-stage prototypes may be deliberately thin.

**When to flag:** Tests labeled as unit or integration tests for the system under test (not smoke/boundary tests), with vacuous assertions or assertions only on mocks. The code is past prototype stage (judged by surrounding maturity).

---

## Context-Only Signals (amplify, don't create findings)

These signals boost confidence in a Strong or Conditional finding in the same file. They never create a finding on their own.

### Born-Complete Files

**Detection:** `git log --follow --oneline -- path/to/file` shows 1-2 commits, first commit introduces 200+ lines of complex code, no subsequent iteration, vague commit message ("add feature", "implement X").

**Why context-only:** Reference docs, configs, specs, protocol implementations, generated code, well-prepared migrations, and short utility files are legitimately born complete. Many files are correct on the first write.

**How to use:** If a file already has a confirmed Strong or Conditional slop finding, born-complete adds confidence — raise stink level by one. Never report born-complete as a finding by itself.

### Inconsistent Style Within a File

**Detection:** Mixed naming conventions, mixed import styles, mixed error-handling patterns within the same file (not across files).

**Why context-only:** Many teams have no enforced house style. Files touched by multiple authors over time develop natural inconsistencies. FFI boundaries (binding to a snake_case API from camelCase code) are legitimate. Style migrations in progress look exactly like AI-pasted-from-different-sessions code.

**How to use:** Boost confidence on findings in single-author, single-session files where the inconsistency is within a single function or contiguous block. Cross-file inconsistency is essentially never slop.

### Backwards-Compat for New Code

**Detection:** `// Kept for backwards compatibility` on code with no external consumers; deprecated methods alongside replacements introduced in the same commit; re-exports of types under non-canonical names.

**Why context-only:** You usually can't verify whether the code has external consumers without project context. The shape might exist for an upcoming consumer you can't see, a known migration path, or an internal API guarantee.

**How to use:** Boost confidence on a related finding only when you can verify (via the project's explicit scope or documentation) that no consumers exist or could exist.
