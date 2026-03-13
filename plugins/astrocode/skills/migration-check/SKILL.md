---
name: migration-check
user-invocable: false
description: >
  Review database migration files for safety before running against a live database.
  Checks for destructive operations, backward compatibility, index coverage, idempotency,
  and rollback plans. Use when the user says "migration check", "review migration",
  "is this migration safe", "check schema change", "review SQL", or "migration safety".
  Also use when the user runs /migration-check.
compatibility: Requires file system access. Works with any SQL-based migration system.
metadata:
  author: astrosteveo
  version: 1.0.0
  category: database
  tags: [database, migration, schema, safety, sql]
---

# Migration Check

Review database migration files for safety before running them against a live database. A bad migration with real users is the fastest way to lose data and trust.

## Instructions

### Step 1: Find Migration Files

Locate migration files based on the user's request:

1. **User points to specific files:** Review those.
2. **User says "check migrations" broadly:** Look for migration directories:
   - `src/lib/migrations/`, `migrations/`, `db/migrate/`, `prisma/migrations/`, `drizzle/`, or similar
   - Also check for uncommitted/new SQL files in `git status`
3. **User asks about a schema change in progress:** Check for SQL in the diff

Read the current schema (`schema.sql` or equivalent) for context.

### Step 2: Destructive Operation Scan

Flag any operation that could lose data:

| Operation | Risk Level | Notes |
|-----------|-----------|-------|
| `DROP TABLE` | CRITICAL | Total data loss for that table |
| `DROP COLUMN` | HIGH | Column data is gone |
| `TRUNCATE` | CRITICAL | All rows deleted |
| `DELETE` without WHERE | CRITICAL | All rows deleted |
| `ALTER COLUMN ... TYPE` | MEDIUM | Can fail or lose precision on existing data |
| `DROP INDEX` | LOW | Performance impact, no data loss |
| `DROP CONSTRAINT` | MEDIUM | May allow invalid data going forward |
| `RENAME TABLE/COLUMN` | HIGH | Breaks any code referencing the old name |

For each destructive operation found, explain the risk and ask: "Is this intentional?"

### Step 3: Backward Compatibility

Check if the migration is safe for zero-downtime deployment (old code + new schema):

- **Column additions:** Safe — old code ignores new columns
- **Column removals:** Unsafe — old code will break querying removed columns
- **Column renames:** Unsafe — old code references the old name
- **NOT NULL additions to existing columns:** Unsafe if existing rows have NULLs
- **New required foreign keys:** Unsafe if existing rows don't satisfy the constraint
- **Table renames:** Unsafe — old code references the old name

If backward-incompatible changes are found, suggest a safe migration path:
1. Add new column (nullable)
2. Deploy code that writes to both old and new
3. Backfill data
4. Deploy code that reads from new only
5. Drop old column

### Step 4: Index Coverage

For any new columns used in `WHERE`, `JOIN`, or `ORDER BY` clauses:

- Check if an index exists or is being created
- Flag missing indexes on foreign key columns
- Note composite indexes that might be needed for common query patterns

For any removed indexes:
- Check if the index is still referenced in query patterns
- Flag if removing the index will cause performance regression

### Step 5: Idempotency

Check if the migration can run twice safely:

- `CREATE TABLE` without `IF NOT EXISTS` — fails on second run
- `ADD COLUMN` without checking existence — fails if column exists
- `INSERT` without `ON CONFLICT` — creates duplicates
- `CREATE INDEX` without `IF NOT EXISTS` or `CONCURRENTLY` — fails or locks

Suggest idempotent alternatives where possible.

### Step 6: Data Integrity

Check for potential data issues:

- `NOT NULL` constraint added to a column that may contain NULLs
- `UNIQUE` constraint added to a column with duplicate values
- `CHECK` constraint added that existing data may violate
- Default values that may not be appropriate for existing rows
- Foreign key constraints where referenced rows may not exist

### Step 7: Rollback Plan

For each migration file, assess rollback difficulty:

- **Easy rollback:** Adding columns, indexes, tables (just drop them)
- **Hard rollback:** Dropping columns (data is gone), type changes (may lose precision)
- **No rollback:** Destructive operations without a backup

If the migration includes hard-to-rollback operations, suggest writing an explicit rollback script and recommend taking a database snapshot before running.

### Step 8: Report

```
## Migration Safety Report

**Files reviewed:** [list]
**Database:** [if known from CLAUDE.md or connection config]

| Check | Status | Notes |
|-------|--------|-------|
| Destructive operations | PASS/WARN/FAIL | [details] |
| Backward compatibility | PASS/WARN | [details] |
| Index coverage | PASS/WARN | [details] |
| Idempotency | PASS/WARN | [details] |
| Data integrity | PASS/WARN | [details] |
| Rollback plan | EASY/HARD/NONE | [details] |

**Recommendation:** Safe to run / Run with caution / Needs revision
```

If the migration is safe, say so. If it needs changes, provide specific SQL rewrites.

## Important

- **Never run migrations.** This skill reviews them — it does not execute them.
- **Assume production data exists.** Even if the database is empty today, review as if it has real data. It will soon.
- **Context matters.** A `DROP COLUMN` during initial development is fine. The same operation with 1000 users is a different conversation. Ask about the current state if unsure.
- **Suggest, don't block.** Some destructive operations are intentional. Flag them, explain the risk, and let the user decide.
