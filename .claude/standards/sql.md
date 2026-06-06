# SQL & Database Standards

> Mandatory standards for all SQL queries, schema changes, and database access code. Enforced by `code-reviewer`, `java-tech-lead`, and `performance-engineer` agents.

---

## Query Rules (Non-Negotiable)

### No SELECT *
Always specify explicit column lists:

```sql
-- CORRECT
SELECT order_id, customer_id, status, created_at
FROM orders
WHERE customer_id = :customerId AND status = :status;

-- WRONG
SELECT * FROM orders WHERE customer_id = :customerId;
```

### Parameterised Queries Only
Never build SQL via string concatenation — SQL injection risk:

```java
// CORRECT — NamedParameterJdbcTemplate
String sql = "SELECT order_id, status FROM orders WHERE customer_id = :customerId";
Map<String, Object> params = Map.of("customerId", customerId);
return jdbcTemplate.query(sql, params, orderMapper);

// WRONG — string concatenation
String sql = "SELECT * FROM orders WHERE customer_id = '" + customerId + "'"; // injection risk
```

### Named Parameters
Use named parameters (`:name`) not positional (`?`) in all queries — readable, reorderable:

```sql
-- CORRECT
WHERE customer_id = :customerId AND status = :status

-- AVOID (positional — fragile)
WHERE customer_id = ? AND status = ?
```

---

## Schema Design

- Use `UUID` primary keys for distributed systems (no auto-increment leaking record counts)
- Always include `created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()` and `updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()` on all entity tables
- Use `NOT NULL` constraints aggressively — nullable columns require defensive null handling everywhere
- Define foreign key constraints — never rely on application code to enforce referential integrity
- Index foreign key columns and all columns used in `WHERE`, `JOIN ON`, or `ORDER BY` clauses

---

## Flyway Migration Standards

- One change per migration file — never combine unrelated schema changes
- Naming: `V{version}__{description_with_underscores}.sql`
- Version numbers are sequential: `V001`, `V002`, ... or `V20260606_1`
- **Never modify an applied migration** — create a new migration to revert or alter
- Test migrations against a copy of the production schema before applying to production
- Include rollback script in the PR description (Flyway Pro) or as a separate `U__` undo migration

```
db/migration/
  V001__create_orders_table.sql
  V002__add_order_status_index.sql
  V003__add_fulfilment_date_column.sql
```

---

## Performance Rules

- Explain all queries that access tables over 10,000 rows before committing
- Never use `OFFSET` for pagination on large tables — use keyset (cursor) pagination
- Avoid `LIKE '%value%'` on large text columns — use full-text search or a search index
- Never load a large result set into application memory — use streaming (`ScrollableResults`, `Stream<T>`)
- Avoid `N+1` query patterns — use `JOIN FETCH` in JPQL or explicit batch loading

---

## Transaction Management

- Keep transactions short — no external API calls inside a transaction
- `@Transactional(readOnly = true)` on all read-only service methods
- Explicit `@Transactional` (with `readOnly = false`) on write methods only
- Never use `SERIALIZABLE` isolation without understanding the performance implications
- Avoid distributed transactions — use the Saga pattern with compensating transactions

---

## Sensitive Data

- Never store passwords in plaintext — use bcrypt or Argon2 hashing
- Classify PII columns and apply appropriate encryption or pseudonymisation
- Implement row-level security where different users should see different rows
- Never return PII in error messages or logs
