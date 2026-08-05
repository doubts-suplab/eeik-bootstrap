# Runbook — Multi-Tenant SaaS

Operational guide for the [Multi-Tenant SaaS reference architecture](architecture.md).

---

## Key signals

| Signal | Where | Healthy |
|---|---|---|
| Cross-tenant access attempts | audit / security events | **0** (any is a P1) |
| RLS enforced | DB session `app.tenant_id` set on every tx | always; missing = block the request |
| Per-tenant error/latency | metrics tagged by tenant | no single tenant degrading others |
| Metering → billing drift | usage events vs invoiced | reconciled; within tolerance |
| Onboarding success | control-plane `TenantProvisioned` | completes; identity + entitlements seeded |
| Per-tenant rate-limit hits | gateway | expected under load; sustained = investigate a tenant |

## SLOs
- **Isolation:** zero cross-tenant data access, always. **Availability** 99.9% (platform), degradation
  isolated to a tenant, not fleet-wide. **Billing accuracy:** usage == invoice.

---

## Common incidents

### Suspected cross-tenant data exposure — P1
The most serious SaaS incident.
1. Confirm scope: which endpoint/query, which tenants, read or write?
2. **RLS is the backstop** — verify `app.tenant_id` was set for the offending session. If RLS was bypassed
   (superuser role, `SET ROLE`, a connection not going through the app), that's the root cause.
3. Freeze the affected path (feature flag), notify security + affected tenants per policy, preserve audit.
4. Post-incident: add a test that the query denies across tenants; RLS policy coverage check in CI.

### One tenant degrading others (noisy neighbour)
1. Identify the tenant from per-tenant metrics (latency/error/throughput by tenant tag).
2. Apply/adjust the per-tenant rate limit + queue quota; the platform should shed *that tenant's* excess,
   not everyone's.
3. Chronic offender → promote to a siloed datasource/stack (per-tenant isolation policy) or a higher tier.

### Onboarding stuck
1. Which step failed — tenant record, identity provisioning (Cognito), entitlements, or the provisioned event?
2. Onboarding is idempotent: re-run from the failed step. A half-provisioned tenant must not be able to log in.

### Billing / metering mismatch
1. Compare raw usage events to the metering aggregate to the invoice — where does it diverge?
2. Missing events (dropped on the bus) vs double-count (non-idempotent aggregation). Metering consumers
   de-dup on event id; reconcile from the event log (source of truth), never edit invoices by hand.

### Offboarding / GDPR erasure
1. Disable tenant access immediately (identity + entitlements).
2. Export then delete tenant-scoped data (RLS makes "all of tenant X" a scoped operation); record completion.

---

## Routine operations

- **Deploy:** CDK infra; blue/green on the app; Flyway migrations before the new version. Migrations must be
  tenant-safe (RLS-compatible; no long locks that stall all tenants).
- **New tenant:** self-serve control-plane flow; no infra change for pooled tenants.
- **Tier change (pool → silo):** provision the dedicated datasource, migrate the tenant's data, repoint its
  context; other tenants unaffected.
- **Feature flags:** per-tenant flags gate rollout; enable for a cohort before fleet-wide.
- **Isolation test in CI:** a standing test asserts a query for tenant A returns nothing for tenant B.

## Escalation
P1 (cross-tenant exposure, fleet-wide outage) → security + platform on-call. P2 (single-tenant degradation,
billing drift, onboarding failure) → platform on-call. Attach: tenant id(s), endpoint/query, audit entries.
