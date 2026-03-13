---
name: security-audit
description: >
  Performs security audits on code to identify vulnerabilities, insecure patterns,
  and exposure risks. Checks for OWASP top 10 issues (injection, XSS, SSRF, auth
  bypass), secrets/credentials in code, insecure dependencies, misconfigured auth
  flows, and data exposure. Use when the user says "security audit", "check for
  vulnerabilities", "is this secure", "security review", "find security issues",
  "check for injection", "review auth security", or "scan for secrets". Also use
  when the user runs /security-audit.
compatibility: Requires Claude Code with file system access for codebase scanning.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: security
  tags: [security, audit, vulnerabilities, owasp]
---

# Security Audit

Perform a thorough security audit of the codebase. Produce a prioritized report of vulnerabilities with severity ratings and actionable fix recommendations.

## Scope

Determine audit scope based on the user's request:

- **Full audit:** User says "security audit", "security review", or similar broad request. Scan the entire codebase.
- **Targeted audit:** User points to specific files, directories, or concerns (e.g., "is this endpoint secure?"). Focus on those areas but flag any adjacent risks discovered.

If the scope is ambiguous, ask the user before proceeding.

## Instructions

### Step 1: Reconnaissance

Before scanning, understand the project:

1. Read `CLAUDE.md` (if present) to understand the tech stack, architecture, and conventions.
2. Identify the framework, language, and key dependencies from config files (`package.json`, `requirements.txt`, `go.mod`, etc.).
3. Map the attack surface:
   - API routes and endpoints
   - Authentication and authorization flows
   - Database queries and data access patterns
   - External service integrations
   - File upload/download handling
   - User input entry points

### Step 2: OWASP Top 10 Scan

Check for each category systematically:

**A01 — Broken Access Control**
- Missing or bypassable auth checks on protected routes
- Insecure direct object references (IDOR) — user IDs in URLs without ownership validation
- Missing CSRF protection on state-changing endpoints
- Overly permissive CORS configuration
- Privilege escalation paths (e.g., user can access admin routes)

**A02 — Cryptographic Failures**
- Hardcoded secrets, API keys, or passwords in source code
- Weak hashing algorithms (MD5, SHA1 for passwords)
- Missing encryption for sensitive data in transit or at rest
- Tokens or secrets logged or exposed in error messages

**A03 — Injection**
- SQL injection: string concatenation in queries, missing parameterization
- NoSQL injection: unvalidated user input in query objects
- Command injection: user input passed to shell commands, `exec()`, `eval()`
- XSS: unescaped user input rendered in HTML/templates
- Template injection: user input in template strings
- Path traversal: user-controlled file paths without sanitization

**A04 — Insecure Design**
- Missing rate limiting on auth endpoints or sensitive operations
- No account lockout after failed login attempts
- Predictable resource IDs or tokens
- Missing input validation at system boundaries

**A05 — Security Misconfiguration**
- Debug mode or verbose error messages in production config
- Default credentials or configurations
- Unnecessary features enabled (directory listing, unused endpoints)
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Overly permissive file/directory permissions

**A06 — Vulnerable Components**
- Known vulnerable dependencies (check lock files for outdated packages)
- Deprecated APIs or libraries still in use
- Unmaintained dependencies

**A07 — Auth Failures**
- Weak password policies
- Missing MFA options
- Session fixation or improper session invalidation
- JWT issues: missing expiry, weak signing, algorithm confusion
- Tokens stored in localStorage (XSS-accessible)

**A08 — Data Integrity Failures**
- Missing input validation on deserialized data
- Unsigned or unverified updates/deployments
- Missing integrity checks on critical data flows

**A09 — Logging & Monitoring Failures**
- Sensitive data in logs (passwords, tokens, PII)
- Missing audit logging for security-relevant events
- No alerting on suspicious activity patterns

**A10 — SSRF**
- User-supplied URLs fetched server-side without validation
- Internal service URLs constructable from user input
- Missing allowlist for outbound requests

### Step 3: Secrets and Credentials Scan

Search for exposed secrets:

1. Scan for hardcoded values matching patterns:
   - API keys, tokens, passwords in source files
   - Connection strings with embedded credentials
   - Private keys or certificates
2. Check `.gitignore` covers sensitive files (`.env`, `.env.local`, credentials files, key files)
3. Verify environment variables are used instead of hardcoded values
4. Check that `.env.example` does not contain real values
5. Look for secrets in comments, TODOs, or test fixtures

### Step 4: Dependency Audit

1. Check for known vulnerabilities: review lock file versions against known CVEs where possible
2. Flag severely outdated dependencies (major versions behind)
3. Identify dependencies that are unmaintained or archived

### Step 5: Compile Report

Organize findings into a structured report:

```
## Security Audit Report

**Scope:** [What was audited]
**Date:** [Current date]

### Critical (Immediate action required)
Findings that are actively exploitable or expose sensitive data.

### High (Fix before next deploy)
Findings with significant security impact that require near-term remediation.

### Medium (Plan to address)
Findings that reduce security posture but are not immediately exploitable.

### Low (Improvement opportunities)
Hardening recommendations and defense-in-depth suggestions.

### For each finding:
- **Location:** file:line_number
- **Category:** OWASP category or type
- **Description:** What the issue is
- **Impact:** What could happen if exploited
- **Recommendation:** Specific fix with code example where helpful
```

Sort findings by severity, then by effort to fix (quick wins first within each severity).

## Important

- Do NOT modify any code during the audit unless the user explicitly asks you to fix findings.
- Do NOT run any commands that could affect running services or production systems.
- If you discover a critical vulnerability (e.g., exposed production credentials), alert the user immediately before continuing the audit.
- Be specific — cite exact file paths and line numbers. Vague findings are not actionable.
- Avoid false positives — if you are uncertain whether something is a real issue, note your confidence level.
- Distinguish between issues in application code vs. test code vs. configuration. Test-only issues are generally lower severity.

## Examples

### Example 1: Full Codebase Audit
User says: "Run a security audit"
Actions:
1. Read project config files and CLAUDE.md
2. Map API routes, auth flows, and data access patterns
3. Systematically check each OWASP category
4. Scan for hardcoded secrets
5. Review dependency versions
Result: Prioritized report with all findings, severity ratings, and fix recommendations

### Example 2: Targeted Endpoint Review
User says: "Is this API route secure?" (with a file open or path specified)
Actions:
1. Read the specified file and related files (middleware, auth, DB queries)
2. Check for injection, auth bypass, data exposure, rate limiting
3. Trace data flow from input to output
Result: Focused security assessment of that endpoint with specific findings
