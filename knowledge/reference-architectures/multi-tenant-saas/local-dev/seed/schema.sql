-- Multi-Tenant SaaS — local schema with ROW-LEVEL SECURITY (the isolation guarantee).
-- Every tenant-scoped table carries tenant_id and an RLS policy keyed on the session variable
-- app.tenant_id, which the application sets from the Cognito tenant_id claim on each request.

CREATE TABLE IF NOT EXISTS tenants (
    id          UUID PRIMARY KEY,
    name        TEXT        NOT NULL,
    plan        VARCHAR(16) NOT NULL DEFAULT 'standard',   -- free|standard|enterprise
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
    id          UUID PRIMARY KEY,
    tenant_id   UUID        NOT NULL REFERENCES tenants(id),
    name        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Per-tenant usage metering (drives billing).
CREATE TABLE IF NOT EXISTS usage_events (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id   UUID        NOT NULL REFERENCES tenants(id),
    metric      VARCHAR(32) NOT NULL,                       -- api_calls|storage_mb|agent_runs
    quantity    BIGINT      NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Row-level security: a session may only see rows for its own tenant ───────────────
ALTER TABLE projects     ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_projects ON projects
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
CREATE POLICY tenant_isolation_usage ON usage_events
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- The application role is subject to RLS (the table owner bypasses it, so the app must not be owner).
CREATE ROLE app_user NOLOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON projects, usage_events TO app_user;
GRANT SELECT ON tenants TO app_user;
