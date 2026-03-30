# Review Categories

Detailed checklists for each review category. Not every check applies to every
codebase — skip categories that don't match the project's language, framework, or
domain. Apply judgment, not rote checking.

## 1. Clean Code

### Readability
- Functions longer than ~40 lines that could be decomposed into named steps
- Deeply nested conditionals (3+ levels) — can they be flattened with early returns or
  guard clauses?
- Variable/function names that don't communicate intent (single letters, abbreviations,
  misleading names)
- Magic numbers or strings without named constants or explanation
- Dead code: unreachable branches, unused variables/imports, commented-out code blocks

### Complexity
- Functions with high cyclomatic complexity (many branches, nested loops)
- God classes/modules that handle too many responsibilities
- Long parameter lists (5+) suggesting a missing data structure or config object
- Boolean flag parameters that split a function into two different behaviors

### Comments
- Comments explaining WHAT the code does (redundant) instead of WHY
- Outdated comments that contradict the current code
- Long-standing TODO/FIXME/HACK markers that may indicate unresolved issues

## 2. DRY (Don't Repeat Yourself)

- Near-identical code blocks (3+ lines) appearing in multiple places
- Copy-pasted logic with minor variations that could be parameterized
- Repeated configuration values, thresholds, or constants across files
- Similar functions that differ only in a few parameters

**Judgment call**: not all duplication is bad. Two occurrences may not justify an
abstraction. Flag it, but note when the cure (a premature abstraction) would be worse
than the disease (a little repetition). Three similar lines of straightforward code
can be clearer than a helper function with a name that's harder to understand.

## 3. Security

### Injection
- SQL queries built with string concatenation or interpolation
- Shell commands constructed from unsanitized input
- HTML output without proper escaping (XSS vectors)
- Template injection (SSTI) via user-controlled template strings
- Path traversal: file paths built from user input without validation

### Authentication and Authorization
- Hardcoded credentials, API keys, tokens, or secrets in source code
- Missing authentication on endpoints or operations that need it
- Missing authorization checks (authenticated != authorized)
- Weak password handling: plaintext storage, weak hashing (MD5, SHA1), missing salting
- Session management issues: predictable tokens, no expiry, no rotation

### Data Exposure
- Sensitive data in log output (passwords, tokens, PII, full stack traces)
- Verbose error messages leaking internal paths, versions, or architecture
- Debug endpoints, flags, or admin panels left enabled
- Secrets committed to version control (even if later removed — they're in history)

### Cryptography
- Deprecated algorithms (MD5/SHA1 for security purposes, DES, RC4)
- Hardcoded encryption keys or IVs
- Weak random number generation for security-sensitive operations (Math.random vs
  crypto PRNG)

## 4. Performance

### Algorithmic
- O(n^2) or worse operations where O(n) or O(n log n) is feasible (nested loops over
  the same collection, repeated linear scans)
- Repeated expensive computations that could be cached, memoized, or batched
- N+1 query patterns: a loop of individual queries instead of a single batch query
- Full-collection iteration when early exit or index lookup would suffice

### Resource Management
- Unclosed resources: file handles, database connections, network streams, locks
- Growing collections that are never pruned (memory leaks)
- Unbounded caches or queues that could exhaust memory
- Large allocations inside hot loops (create once outside the loop)

### I/O
- Synchronous blocking I/O on a main thread or event loop
- Missing connection pooling for database or HTTP connections
- Missing pagination for large result sets
- Redundant network calls: fetching the same data multiple times in one flow

## 5. Error Handling

- Swallowed exceptions: empty catch/except blocks that silently hide failures
- Overly broad catches: catching all exceptions when only specific ones are expected
- Missing error handling on I/O, network, parsing, or deserialization operations
- Error messages that don't help diagnose the problem (generic "something went wrong")
- Inconsistent error handling patterns: some modules throw, others return error codes,
  others use Result types — in the same codebase with no clear convention

## 6. Architecture and Design

- Circular dependencies between modules/packages
- Tight coupling: direct references where interfaces, events, or dependency injection
  would be more appropriate
- Layer violations: UI code reaching directly into database/storage, business logic
  mixed into I/O handlers
- Missing separation of concerns: one module handling unrelated responsibilities
- Inconsistent patterns: the same problem solved three different ways in three modules

**Important**: architecture findings require the most context. What looks like a
violation might be an intentional trade-off, a prototype, or a team convention. Always
cross-reference with project documentation before flagging.

## 7. Testing

- Untested critical paths: authentication, authorization, payment, data mutation
- Tests coupled to implementation details instead of testing behavior/outcomes
- Missing edge case coverage: null/nil, empty collections, boundary values, zero, negative
- Flaky tests: time-dependent, order-dependent, dependent on external services
- Test code significantly harder to read than the production code it tests

## 8. Dependencies

- Known vulnerable dependency versions (if version info is available, check against
  known CVE patterns — outdated major versions of security-critical libraries)
- Unused dependencies still declared in manifests
- Multiple dependencies solving the same problem (two HTTP clients, two ORMs)
- Pinned to very old major versions when significant security/performance improvements
  exist in newer versions
