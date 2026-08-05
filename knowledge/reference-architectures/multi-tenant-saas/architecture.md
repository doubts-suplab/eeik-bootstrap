# Reference Architecture — Multi-Tenant SaaS

**Stack:** Spring Boot 3 · Java 21 · Aurora PostgreSQL (RLS) · Cognito · API Gateway · EventBridge · React · CDK
**Maturity:** Production · **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) (schema-valid)
**Resolves to packs:** `core · architecture · aws · delivery · governance · java · react`

A blueprint for SaaS that shares infrastructure for cost efficiency while keeping every tenant's data and
identity **isolated** — solving the three problems every SaaS faces: tenant isolation, the noisy neighbour,
and per-tenant billing.

---

## 1. Context

```
   Tenant users ─▶ React ─▶ API Gateway ─▶ BFF/App (Spring Boot modular monolith)
                              │                 │ (tenant context set here, once)
                        Cognito (JWT: tenant_id, roles)     │
                                                            ▼
                                        Aurora PostgreSQL — Row-Level Security (tenant_id)
                                                            │
              usage events ─▶ EventBridge ─▶ Metering store ─▶ Billing (Stripe)
   Control plane (admin): onboarding · plans/entitlements · per-tenant feature flags
```

---

## 2. Tenant isolation (the core concern)

### 2.1 Isolation model — pooled with RLS (default)
One database, shared tables, a `tenant_id` column on every tenant-owned row, and **PostgreSQL Row-Level
Security** policies:

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The app sets `app.tenant_id` **from the authenticated token** at the start of each request/transaction. RLS
then makes it *impossible* for a query — even a buggy one — to read or write another tenant's rows. Defence
in depth: repositories also filter by tenant, but RLS is the backstop that a missing filter can't defeat.

### 2.2 The isolation spectrum (per-tenant policy)
```
pooled (shared DB + RLS)  ──▶  bridge (schema-per-tenant)  ──▶  siloed (DB/stack-per-tenant)
   cost-efficient default          stronger isolation             strongest; premium / regulated tenants
```
Isolation is a **per-tenant attribute**, not a platform-wide choice: most tenants are pooled; a regulated or
enterprise tenant can be siloed without re-architecting — the tenant context resolves to the right datasource.

### 2.3 Tenant context — set at the edge, never trusted from the body
The gateway/filter resolves `tenant_id` from the **JWT claim** (Cognito), not from a request parameter, and
binds it to the request + DB session. A tenant id in the request body is ignored. Cross-tenant access is a
security event.

---

## 3. Identity (Cognito)

- **Shared user pool + `custom:tenant_id` claim** (default) or **pool-per-tenant** (stronger separation /
  per-tenant IdP federation). The JWT carries `tenant_id` + roles; the app authorises on both.
- **Onboarding** (control plane): create the tenant record, provision identity (pool/group), seed
  entitlements + feature flags, emit `TenantProvisioned`. **Offboarding** disables access and schedules
  data export + deletion (GDPR).

---

## 4. Noisy neighbour & fairness

| Risk | Control |
|---|---|
| One tenant saturates the DB | Per-tenant rate limits at the gateway; connection-pool fairness; slow-query guard |
| One tenant floods async work | Per-tenant quotas on queue consumption; bulkhead per tenant tier |
| Hot tenant skews cost | Per-tenant metering surfaces it; option to promote to a siloed stack |

---

## 5. Metering & billing

Usage is captured as **domain events** (`ApiCall`, `RecordCreated`, `JobRun`), published to EventBridge, and
aggregated per tenant in a metering store. Billing (Stripe) rates the aggregates against the tenant's plan and
invoices — **downstream of usage**, never on the hot request path. Entitlements (limits/features) are checked
in-request from the tenant's plan.

---

## 6. Non-functional targets

| Concern | Target | How |
|---|---|---|
| Isolation | zero cross-tenant reads | RLS backstop + edge-set tenant context |
| Onboarding | self-serve, minutes | control-plane automation; no infra change for pooled tenants |
| Fairness | no tenant starves another | per-tenant rate limits + quotas + bulkheads |
| Billing accuracy | usage == invoice | event-sourced metering, reconciled |
| Compliance | per-tenant data export/delete | tenant-scoped queries + offboarding workflow (GDPR) |

---

## 7. Why these choices

- **Pooled + RLS over silo-per-tenant** — the cost-efficient default that still guarantees isolation at the
  database; silo only the tenants that require it, as a policy, not a rewrite.
- **Tenant context from the token, enforced by RLS** — isolation that survives application bugs; a forgotten
  `WHERE tenant_id` can't leak data because RLS denies it.
- **Modular monolith over microservices (initially)** — one deployable with strong module boundaries is the
  right SaaS starting point; extract a module to a service when its scaling/ownership demands it.
- **Metering from events** — billing is a projection of usage, decoupled and reconcilable; not request-path logic.

---

## 8. Adopt it

```bash
eeik validate knowledge/reference-architectures/multi-tenant-saas/project-manifest.yaml
# resolves to: core, architecture, aws, delivery, governance, java, react
cp knowledge/reference-architectures/multi-tenant-saas/project-manifest.yaml ./project-manifest.yaml
eeik activate --apply
```

Enterprise governance applies (ADRs required, security + production-readiness reviews). See
[`runbook.md`](runbook.md) for operations (isolation checks, onboarding, noisy-neighbour response).
