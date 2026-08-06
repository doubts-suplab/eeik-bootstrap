# Multi-Tenant SaaS — CDK

Deployable infrastructure for the [Multi-Tenant SaaS](../architecture.md) reference architecture: a
Cognito user pool (with a per-user `tenant_id` claim), an Aurora PostgreSQL cluster whose isolation is
enforced by **row-level security**, an EventBridge domain bus, and the Spring Boot modular monolith on
ECS Fargate behind an ALB. See [`lib/multi-tenant-saas-stack.ts`](lib/multi-tenant-saas-stack.ts).

> The tenant-isolation guarantee lives in the **database** (RLS policies keyed on the tenant claim,
> shipped as Flyway migrations). This stack's job is to make sure the `tenant_id` claim flows
> identity → app → DB session variable on every request. App image is a `REPLACE_ME/...` placeholder.

## Deploy

```bash
npm install
npx cdk bootstrap
npx cdk deploy MultiTenantSaas
```

| Construct | Purpose |
|---|---|
| `Identity` (Cognito) | auth; immutable `tenant_id` custom claim on every token |
| `TenantStore` (Aurora) | shared DB; RLS policies isolate tenants; writer + reader |
| `DomainBus` (EventBridge) | cross-module events — metering, provisioning, billing |
| `App` (Fargate + ALB) | modular monolith; sets `app.tenant_id` per request so RLS applies |

Local iteration without AWS: [`../local-dev/`](../local-dev/).
