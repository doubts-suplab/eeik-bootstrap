# AGENTS.md — Infrastructure / IaC Directory

> **Deploy to**: `infrastructure/AGENTS.md` in your project
> Codex CLI reads this automatically when working in CDK/Terraform files.

---

You are working in the **infrastructure as code** directory.

## IaC Stack

This project uses **AWS CDK TypeScript** (preferred) or Terraform HCL.

### CDK Conventions

```
infrastructure/
├── bin/
│   └── app.ts              ← CDK app entry; one stack per environment
├── lib/
│   ├── stacks/
│   │   ├── network-stack.ts   ← VPC, subnets, security groups
│   │   ├── data-stack.ts      ← RDS, ElastiCache, DynamoDB
│   │   ├── compute-stack.ts   ← ECS/EKS, Lambda, API Gateway
│   │   └── observability-stack.ts  ← CloudWatch, alarms, dashboards
│   └── constructs/         ← Reusable L3 constructs
├── test/
│   └── *.test.ts           ← CDK assertions tests
└── cdk.json
```

## Non-Negotiable Rules

1. **L2/L3 constructs preferred** — avoid L1 (`Cfn*`) unless no L2 exists
2. **No hardcoded account IDs or regions** — use `Stack.of(this).account` / `Stack.of(this).region`
3. **No hardcoded secrets** — use `SecretValue.ssmSecure()` or Secrets Manager
4. **Removal policy explicit** — always set `removalPolicy` on stateful resources
5. **Encryption by default** — S3 buckets, RDS, EBS all encrypted at rest
6. **Least privilege IAM** — no `*` actions unless justified with a comment
7. **VPC endpoints** — use VPC endpoints for AWS services (S3, DynamoDB, SSM) in production
8. **Tag all resources** — Environment, Project, Owner, CostCentre tags on every resource
9. **`cdk diff` before deploy** — always check diff in CI before applying
10. **Destroy protection** — `terminationProtection: true` for production stacks

## CDK Patterns

### Standard resource tagging
```typescript
Tags.of(this).add('Project',     props.projectName);
Tags.of(this).add('Environment', props.environment);
Tags.of(this).add('Owner',       props.teamEmail);
Tags.of(this).add('ManagedBy',   'CDK');
```

### Secrets from Secrets Manager
```typescript
// ✅ Reference existing secret — never create with plaintext value
const dbPassword = secretsmanager.Secret.fromSecretNameV2(this, 'DbPassword', '/myapp/db/password');

// ✅ Pass to container
taskDefinition.addContainer('app', {
  secrets: { DB_PASSWORD: ecs.Secret.fromSecretsManager(dbPassword) }
});
```

### Conditional removal policy
```typescript
const removalPolicy = props.environment === 'prod'
  ? cdk.RemovalPolicy.RETAIN
  : cdk.RemovalPolicy.DESTROY;

new rds.DatabaseCluster(this, 'Database', {
  removalPolicy,
  // ...
});
```

## Terraform Conventions

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf       ← explicit provider + terraform version constraints
├── modules/          ← reusable modules
└── environments/
    ├── dev/
    │   └── terraform.tfvars
    └── prod/
        └── terraform.tfvars
```

Remote state: S3 bucket + DynamoDB lock table. Never local state in production.

## Security Checklist Before Any Infra PR

- [ ] No hardcoded credentials or account IDs
- [ ] IAM policies follow least privilege
- [ ] Stateful resources have explicit removal policy
- [ ] Encryption enabled on S3, RDS, DynamoDB
- [ ] Security groups do not allow `0.0.0.0/0` inbound on sensitive ports
- [ ] CloudWatch alarms on critical metrics
- [ ] `cdk diff` output reviewed and attached to PR
