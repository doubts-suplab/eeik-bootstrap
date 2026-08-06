# Multi-Tenant SaaS — Local Dev

Run the tenant-isolation model locally and **prove it works**. Postgres stands in for Aurora; the
schema ships the row-level-security policies and two seeded tenants (Acme, Globex).

```bash
docker compose up -d          # Postgres :5432 · RLS schema + 2 tenants seeded
```

Prove isolation — set the session tenant and see only that tenant's rows:

```sql
-- Connect as the RLS-subject role, then:
SET ROLE app_user;
SET app.tenant_id = '7e000000-0000-0000-0000-0000000000a1';   -- Acme
SELECT name FROM projects;      -- → only Acme's 2 projects

SET app.tenant_id = '7e000000-0000-0000-0000-0000000000b2';   -- Globex
SELECT name FROM projects;      -- → only Globex's 1 project
```

The application sets `app.tenant_id` from the Cognito `tenant_id` claim at the start of each request's
transaction; every tenant-scoped query is then filtered by the RLS policy — isolation can't be
forgotten in application code. Tear down: `docker compose down -v`.
