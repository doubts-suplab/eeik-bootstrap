# AWS Standard

**Pack:** aws-pack | **Version:** 1.0

---

## Infrastructure as Code

- **CDK TypeScript** for all new infrastructure — L2/L3 constructs preferred
- Terraform HCL for multi-provider or CDK-unsupported resources
- No manual console changes in dev/staging/prod — all via IaC PRs
- CDK stacks are separated by lifecycle: `NetworkStack`, `DataStack`, `AppStack`, `ObservabilityStack`
- All CDK stacks parameterised by environment — no hardcoded env-specific values

## Security Baseline (Non-Negotiable)

- **Least-privilege IAM always** — no `*` in `actions` or `resources` in production policies
- No long-lived IAM access keys in CI/CD — OIDC federation for GitHub Actions
- All secrets in Secrets Manager or Parameter Store (SecureString) — never in source code
- S3: `blockPublicAccess: BlockPublicAccess.BLOCK_ALL` on every bucket by default
- RDS: encryption at rest enabled; `deletionProtection: true` in production
- VPC: application servers in private subnets only; ALB in public subnets
- TLS 1.2 minimum for all data in transit; TLS 1.3 preferred

## CDK Patterns

```typescript
// ✅ L2 construct with explicit configuration
const bucket = new s3.Bucket(this, 'DataBucket', {
  bucketName: `${props.projectName}-data-${props.environment}`,
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  versioned: true,
  removalPolicy: props.environment === 'prod'
    ? cdk.RemovalPolicy.RETAIN
    : cdk.RemovalPolicy.DESTROY,
});

// ✅ Parameter Store for cross-stack references
new ssm.StringParameter(this, 'BucketArn', {
  parameterName: `/${props.environment}/${props.service}/bucket-arn`,
  stringValue: bucket.bucketArn,
});
```

## Naming Convention

```
{project}-{resource-type}-{environment}

# Examples
myapp-ecs-cluster-prod
myapp-rds-primary-prod
myapp-alb-external-staging

# Parameter Store paths
/{environment}/{service-name}/{parameter-name}
/prod/order-service/db/password
```

## Observability Baseline

Every service must ship with:
- CloudWatch Logs via `awslogs` driver (ECS) or built-in (Lambda)
- X-Ray tracing enabled in staging and production
- At minimum: error rate alarm, p99 latency alarm, and DLQ depth alarm
- Custom metrics via `aws-embedded-metrics` or CloudWatch SDK
