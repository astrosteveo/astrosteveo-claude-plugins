---
name: perf-audit
user-invocable: false
description: >
  Performance audit — identifies N+1 queries, missing indexes, slow API routes,
  bundle bloat, unnecessary re-renders, and caching opportunities. Use when the
  user says "performance audit", "why is this slow", "perf check", "optimize",
  "speed up", "slow queries", "bundle size", or "performance review". Also use
  when the user runs /perf-audit.
compatibility: Requires file system access for codebase scanning.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: performance
  tags: [performance, optimization, queries, bundle, caching]
---

# Performance Audit

Identify performance bottlenecks across the stack — database queries, API routes, frontend rendering, and infrastructure. Produce a prioritized report with specific fixes.

## Scope

Determine scope based on the user's request:

- **Full audit:** User says "performance audit" or "perf check" — scan everything
- **Targeted audit:** User points to a specific area ("this page is slow", "this API is slow") — focus there
- **Specific concern:** User asks about queries, bundle size, or rendering specifically — focus on that layer

## Instructions

### Step 1: Understand the Stack

Read `CLAUDE.md` and project config to understand:
- Framework and rendering model (SSR, SSG, client-side, hybrid)
- Database and ORM/query approach
- Caching layers (Redis, CDN, in-memory)
- Deployment platform (serverless, containers, edge)

These determine which optimizations are relevant.

### Step 2: Database & Query Performance

Scan data access patterns:

**N+1 Queries**
- Loop that makes a query per iteration (the most common perf bug)
- Look for: `for (const item of items) { await query(...) }` patterns
- Fix: batch queries, JOINs, or `WHERE id IN ($1)` with array

**Missing Indexes**
- Read schema files for index definitions
- Check query patterns in route handlers and lib files
- Flag columns used in `WHERE`, `JOIN ON`, `ORDER BY` that lack indexes
- Flag foreign key columns without indexes (common oversight)

**Expensive Queries**
- Full table scans (SELECT * without WHERE on large tables)
- Unbound queries (no LIMIT on potentially large result sets)
- Correlated subqueries that run per-row
- Complex aggregations that could be materialized or cached

**Connection Management**
- Pool-per-query in serverless (acceptable but note the overhead)
- Missing connection reuse in long-running processes (workers, scripts)
- Connection leaks (pool created but never closed)

### Step 3: API Route Performance

Scan API route handlers:

**Sequential Awaits**
- Multiple independent `await` calls that could run in parallel with `Promise.all()`
- Common: fetching user, then fetching unrelated data, then fetching more data — serially

**Missing Early Returns**
- Auth checks or validation that happen after expensive operations
- Should fail fast before doing database queries or external API calls

**Response Size**
- `SELECT *` when only a few columns are needed
- Returning full objects when the client only uses a subset
- Missing pagination on list endpoints

**External API Calls**
- Synchronous calls to third-party APIs in the request path
- Missing timeouts on external requests
- No caching of rarely-changing external data

### Step 4: Frontend Performance

If the project has a frontend (React, Next.js, etc.):

**Rendering**
- Components that re-render unnecessarily (missing memoization on expensive computations)
- Client components that could be server components (unnecessary JS shipped to browser)
- Large component trees without code splitting or lazy loading

**Bundle Size**
- Heavy dependencies imported for minor functionality
- Missing tree-shaking (importing entire libraries vs specific exports)
- Large static assets (images, fonts) without optimization

**Data Fetching**
- Waterfalls: component renders, fetches data, renders child, child fetches data
- Missing loading states that block interaction
- Client-side fetches that could be server-side (in SSR frameworks)

### Step 5: Caching Opportunities

Identify data that's fetched repeatedly but changes rarely:

- Dashboard stats computed on every page load
- User profile/settings fetched on every request
- External API responses that change infrequently
- Static configuration or lookup tables

For each, suggest the appropriate caching strategy:
- **HTTP caching:** `Cache-Control` headers for static or semi-static responses
- **In-memory:** Request-scoped memoization for data used multiple times in one request
- **Redis/KV:** Cross-request caching for expensive computations
- **Materialized views:** For complex aggregations computed from the same data

### Step 6: Infrastructure

Check deployment and infrastructure patterns:

- **Cold starts:** Serverless functions with heavy imports or initialization
- **Region placement:** Database and compute in the same region?
- **Cron frequency:** Jobs running more/less often than needed
- **Worker concurrency:** Appropriate for the workload?

### Step 7: Compile Report

```
## Performance Audit Report

**Scope:** [What was analyzed]
**Date:** [Current date]

### Summary
Brief overview: what's fast, what's slow, where the biggest wins are.

### High Impact (Significant improvement expected)
Issues that measurably affect user experience or infrastructure costs.

### Medium Impact (Moderate improvement)
Issues that add latency or waste resources but aren't critical.

### Low Impact (Micro-optimizations)
Small improvements. Only worth doing if you're already in the file.

### For each finding:
- **Location:** file:line_number
- **Category:** Query / API / Frontend / Caching / Infrastructure
- **Issue:** What's slow and why
- **Impact:** Estimated effect (e.g., "saves ~200ms per page load", "reduces DB queries from N to 1")
- **Fix:** Specific code change or approach
- **Effort:** Quick fix / Moderate / Significant refactor
```

Sort by impact (biggest wins first), then by effort (quick wins first within each tier).

## Important

- **Measure, don't guess.** When possible, cite query patterns and code paths rather than speculating about performance. "This loop makes N queries" is actionable. "This might be slow" is not.
- **Don't prematurely optimize.** If the project has 10 users, don't suggest Redis caching for everything. Scale optimizations to the project's current and near-term needs.
- **Respect the architecture.** Pool-per-query in serverless is intentional, not a bug. Client components in Next.js sometimes make sense. Understand the tradeoffs before flagging patterns.
- **Do NOT modify code** during the audit unless the user explicitly asks for fixes.
- **Quick wins first.** `Promise.all()` for parallel awaits is a 2-line fix with immediate impact. Suggest those before large refactors.
