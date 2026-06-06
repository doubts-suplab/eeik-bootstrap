# AWS Standards

> Mandatory standards for all AWS infrastructure, CDK, and deployment code. Enforced by `aws-architect`, `cdk-terraform-helper`, and `security-auditor` agents.

---

## Infrastructure as Code

- **CDK TypeScript** for all new infrastructure (L2/L3 constructs preferred over L1/CfnResources)
- **Terraform HCL** for resources not supported by CDK or for multi-provider scenarios
- All infrastructure changes via IaC — no manual console changes in dev/staging/prod
- Remote state: S3 bucket + DynamoDB lock table (Terraform) or CDK bootstrap stack

---

## Security Baseline (Non-Negotiable)

### IAM
- **Least privilege always** — never use `*` in `actions` or `resources` in production policies
- No long-lived IAM user access keys in CI/CD — use OIDC federation for GitHub Actions
- ECS task roles and Lambda execution roles scope to specific resources
- No inline policies for shared responsibilities — use managed policies

### Secrets
- **Never hardcode credentials** in source code, CDK stacks, or parameter files
- All secrets in AWS Secrets Manager or Parameter Store (SecureString)
- Rotate secrets on a schedule; never use rotation-exempt secrets without documented justification
- Reference secrets in ECS task definitions by ARN, not value

### Encryption
- S3 buckets: SSE-S3 or SSE-KMS enabled; public access blocked by default
- RDS: encryption at rest enabled; use AWS-managed key minimum
- EBS volumes: encrypted by default
- Data in transit: TLS 1.2 minimum; TLS 1.3 preferred

### Network
- Resources deployed into private subnets by default
- Public subnets for ALB only — application servers never in public subnet
- Security groups follow least privilege: only required ports from specific sources
- VPC Flow Logs enabled for all production VPCs

---

## CDK Patterns

```typescript
// Correct: L2 construct with explicit settings
const bucket = new s3.Bucket(this, 'DataBucket', {
  bucketName: `${props.projectName}-data-${props.environment}`,
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  versioned: true,
  removalPolicy: props.environment === 'prod'
    ? cdk.RemovalPolicy.RETAIN
    : cdk.RemovalPolicy.DESTROY,
  autoDeleteObjects: props.environment !== 'prod',
});

// Correct: Parameter Store for cross-stack references
new ssm.StringParameter(this, 'BucketName', {
  parameterName: `/${props.environment}/${props.projectName}/bucket-name`,
  stringValue: bucket.bucketName,
});
```

---

## Naming Conventions

```
# Pattern: {project}-{resource-type}-{environment}
# Examples:
myapp-ecs-cluster-prod
myapp-rds-primary-prod
myapp-alb-external-prod
myapp-lambda-processor-prod

# Parameter Store path:
/{environment}/{service-name}/{parameter-name}
# Example:
/prod/order-service/db/password
```

---

## Tagging Strategy

All resources must have these tags:

| Tag | Value |
|-----|-------|
| `Project` | `{project-name}` |
| `Environment` | `dev` / `staging` / `prod` |
| `Team` | `{team-name}` |
| `CostCentre` | `{cost-centre-code}` |
| `ManagedBy` | `cdk` or `terraform` |

---

## Observability

- CloudWatch Logs: all ECS containers log to CloudWatch via `awslogs` driver
- CloudWatch Metrics: custom metrics via `aws-embedded-metrics` or CloudWatch SDK
- X-Ray: enable for all Lambda functions and ECS services in staging and production
- CloudWatch Alarms: define alarms for all services before production deployment

---

## Cost Controls

- Set `removalPolicy: RETAIN` on all stateful resources in production (databases, buckets)
- Use Savings Plans / Reserved Instances for predictable compute workloads
- Tag all resources — untagged resources are subject to automatic cleanup in dev
- Set budget alerts in AWS Budgets for dev and staging accounts

---

## Region & Multi-Region

- Primary region: `eu-west-1` (unless project requires otherwise)
- Disaster recovery region: `eu-west-2` (if applicable)
- S3 cross-region replication for critical data (if DR is required)
