# AWS Tagging Standard

**Pack:** aws-pack | **Version:** 1.0

All AWS resources must carry the following tags. Untagged resources in dev/staging are subject to automated cleanup after 72 hours.

---

## Required Tags

| Tag Key | Value Format | Example |
|---------|-------------|---------|
| `Project` | kebab-case project name | `claims-platform` |
| `Environment` | `dev` / `staging` / `prod` | `prod` |
| `Team` | owning squad name | `payments-engineering` |
| `CostCentre` | finance cost centre code | `CC-1234` |
| `ManagedBy` | `cdk` / `terraform` / `manual` | `cdk` |
| `Service` | service name within the project | `order-service` |

## Applying Tags in CDK

```typescript
// Apply tags to all resources in a stack
cdk.Tags.of(this).add('Project', props.projectName);
cdk.Tags.of(this).add('Environment', props.environment);
cdk.Tags.of(this).add('Team', props.team);
cdk.Tags.of(this).add('CostCentre', props.costCentre);
cdk.Tags.of(this).add('ManagedBy', 'cdk');
```

## Cost Centre Allocation

Tag-based cost allocation is enforced via AWS Cost Explorer. Any resource without `CostCentre` tag will be flagged in the weekly untagged resources report.
