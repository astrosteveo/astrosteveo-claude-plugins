# Smell Catalog

Complete catalog of smell patterns across both detection layers. Each smell has
detection guidance and examples of what to look for.

## Layer 1: General Code Smells

### 1.1 Dead Abstractions

An interface, base class, or abstraction layer with only one implementation and no
clear reason to expect more.

**What to look for:**
- Interface with a single implementing class
- Abstract base class with one subclass
- Factory that constructs exactly one type
- Strategy pattern with one strategy
- Generic type parameter that's always the same concrete type

**Why it smells:** Abstractions have a cost — they add indirection and cognitive load.
An abstraction that doesn't abstract over anything is pure overhead. It suggests the
author was following a "best practice" checklist rather than solving a real problem.

### 1.2 Cargo-Culted Patterns

Design patterns applied without the problem they solve.

**What to look for:**
- Repository pattern over a database that only one service talks to
- Event bus / pub-sub with one publisher and one subscriber
- Dependency injection where nothing is ever swapped or mocked
- Observer pattern with one observer
- Middleware chains with one middleware
- Command pattern wrapping a single function call

**Why it smells:** Patterns exist to solve specific problems. When the problem isn't
present, the pattern is just ceremony. It suggests the code was written by someone
(or something) that knows patterns exist but doesn't know when to apply them.

### 1.3 Ceremonial Error Handling

Error handling that exists to look like error handling rather than to handle errors.

**What to look for:**
- catch-log-rethrow: catching an exception only to log it and throw it again
- Generic catch-all: `catch (Exception e)` with a one-size-fits-all response
- Swallowed exceptions: empty catch blocks or catch blocks that only log
- Error messages that don't identify the problem: "An error occurred",
  "Something went wrong", "Operation failed"
- Retry logic with no backoff, no max attempts, or that retries non-transient errors
- Error codes that are never checked by callers

**Why it smells:** Real error handling is specific — it knows what can go wrong and
responds appropriately. Ceremonial error handling just wraps code in try/catch to
look robust.

### 1.4 God Files / God Functions

Files or functions that do too much.

**What to look for:**
- Files over 500 lines with multiple unrelated responsibilities
- Functions over 100 lines
- Functions with 6+ parameters
- Functions with boolean flags that make them do completely different things
- Classes with 20+ methods spanning unrelated domains

**Why it smells:** Large units of code suggest the author kept adding to the same place
rather than thinking about structure. In AI-generated code specifically, this happens
because each prompt adds to the same file.

### 1.5 Copy-Paste Variations

Near-identical code blocks with minor differences.

**What to look for:**
- 3+ line blocks that appear in multiple places with small changes
- Functions that differ only in one or two parameters
- Switch/if-else chains where each branch does nearly the same thing
- Repeated configuration or setup code

**Why it smells:** It suggests the code was produced by asking for something similar
multiple times rather than thinking about the shared pattern.

### 1.6 Wrapper Tax

Layers that exist but add nothing.

**What to look for:**
- Service classes that just call repository methods with the same signatures
- Utility functions that wrap a single standard library call
- Configuration classes that just hold values without validation or defaults
- Controller methods that pass request straight to service and return the result
- Adapter classes that don't actually adapt anything

**Why it smells:** Every layer should justify its existence by transforming data,
enforcing rules, or handling errors. Pass-through layers are noise.

### 1.7 Premature Configuration

Code that's configurable when nothing configures it.

**What to look for:**
- Constants defined in config files but only used in one place with one value
- Feature flags that are always on or always off
- Environment variables that are never set (always fall back to default)
- Plugin systems with no plugins
- Strategy/provider interfaces with only a hardcoded default

**Why it smells:** It suggests the author was building for hypothetical future
requirements rather than actual current needs.

## Layer 2: AI Slop Signals

### 2.1 Docstring-on-Everything Syndrome

Every function, method, and class has a docstring — including trivial ones.

**What to look for:**
- `def get_name(): """Gets the name."""`
- `def __init__(): """Initialize the class."""`
- Docstrings that restate the function signature in prose
- JSDoc/Javadoc on private helper functions that are only called from one place
- Type annotations AND docstrings that say the same thing about types

**Why it's slop:** Human developers document selectively — they add docstrings where
the behavior isn't obvious from the name and signature. Blanket documentation is a
strong signal of AI generation because LLMs default to adding docstrings everywhere.

### 2.2 Defensive Code Against Impossible States

Checks and guards for conditions that can't occur given the type system or control flow.

**What to look for:**
- Null/nil checks on values that the type system guarantees are non-null
- Type checks in strongly-typed languages (`if isinstance(x, str)` when x is typed as str)
- Length checks on collections that are always populated by the preceding code
- Redundant validation of data that was already validated upstream
- Guard clauses at the start of private methods called from one place that already validates

**Why it's slop:** AI models are trained on code that handles every edge case. They
add defensive checks by default even when the context makes them impossible. Human
developers trust their own code and the type system.

### 2.3 High Ceremony-to-Substance Ratio

A file where the actual logic is a small fraction of the total code.

**How to measure:**
- Count lines that DO THE THING (core logic, actual computation, real business rules)
- Count lines that WRAP THE THING (validation, logging, error handling, type
  declarations, docstrings, blank lines in excess)
- If wrapper lines exceed substance lines by 3:1 or more, the ratio is suspicious
- A 200-line file with 30 lines of real logic is a strong smell

**Why it's slop:** AI-generated code tends to be thorough about ceremony because it
treats every context the same. Human developers calibrate ceremony to the importance
and complexity of the code.

### 2.4 Tests That Don't Test

Test suites that provide coverage numbers without actually verifying behavior.

**What to look for:**
- `expect(result).toBeTruthy()` / `assert result` / `assertNotNull(result)`
- Tests that only check the happy path
- Tests where the assertion is on the mock, not the system under test
- Test names like "should work correctly", "test basic functionality"
- Setup that mocks away the component being tested
- Tests that verify implementation details (method call order) instead of outcomes
- One-line test bodies: call function, assert no error thrown

**Why it's slop:** AI generates tests to satisfy the request "write tests for this"
without understanding what's actually worth testing. The tests look complete but
catch nothing.

### 2.5 Apologetic Comments

Comments that acknowledge the code isn't production-ready — left in production code.

**What to look for:**
- `// This is a simplified version...`
- `// For production, you'd want to...`
- `// In a real application, this should...`
- `// TODO: implement proper error handling`
- `// Note: this is a basic implementation`
- `// Placeholder for future enhancement`

**Why it's slop:** These comments are artifacts of AI conversation — the model hedges
by noting limitations. A human developer either fixes the limitation or files a
tracked issue. They don't leave apologies in the code.

### 2.6 Born-Complete Files

Files that appear fully-formed in a single commit with no subsequent iteration.

**Detection via git:**
- `git log --follow --oneline -- path/to/file` shows 1-2 commits total
- First commit introduces a large, complex file (200+ lines)
- No subsequent refactoring, bug fixes, or iteration
- Commit message is vague: "add feature", "implement X", "update code"

**Why it's slop:** Real development is iterative. Code gets written, tested, revised,
refactored. A complex file that was born perfect and never changed was likely generated
in one shot and never critically evaluated.

### 2.7 Ceremonial Security

Security measures that look correct but don't actually protect anything.

**What to look for:**
- Password hashing without salting
- CSRF tokens generated but never validated on form submission
- Input sanitization on some endpoints but not others
- SQL parameterization in some queries but raw string interpolation in others
- Auth middleware registered but with broad bypass rules
- CORS configuration that allows everything (`*`)
- Rate limiting set so high it never triggers

**Why it's slop:** AI models know security patterns exist and include them, but don't
always complete the implementation. The presence of partial security can be worse than
none — it creates false confidence.

### 2.8 Inconsistent Style Within a File

Multiple conventions coexisting in the same file.

**What to look for:**
- camelCase and snake_case in the same file (outside of FFI boundaries)
- Tabs and spaces mixed
- Some functions use early returns, others use deep nesting
- Some error handling uses exceptions, some uses return codes, in the same module
- Import style varies (named imports vs. namespace imports vs. default imports)

**Why it's slop:** When a human writes a file, they use one style throughout — it's
natural. When code is assembled from multiple AI-generated blocks pasted together, each
block may use whatever style the model defaulted to in that completion.

### 2.9 Backwards-Compatibility for New Code

Compatibility measures in code that has no users yet.

**What to look for:**
- Deprecated methods alongside their replacements, both introduced in the same commit
- `// Kept for backwards compatibility` on code with no external consumers
- Re-exported types or aliases that were never the canonical name
- Fallback behavior for "old format" data that has never been produced
- Migration code for schemas that don't exist in production yet

**Why it's slop:** AI models are trained on mature codebases that need backwards
compatibility. They apply the same patterns to brand-new code that has zero users.

### 2.10 Over-Specified Types and Structures

Type definitions and data structures that are more complex than the data they represent.

**What to look for:**
- Generic types with 3+ type parameters for simple data
- Nested interfaces 4+ levels deep
- Enum with 2 values wrapped in a class with methods
- Config objects with 15+ optional fields, most never set
- Abstract base types for data that is always concrete

**Why it's slop:** AI models generate comprehensive type hierarchies by default. Human
developers start simple and add complexity when actual data demands it.
