# AWS Cost Governance Standard

**Pack:** aws-pack | **Version:** 1.0

---

## Cost Controls

- Set `removalPolicy: RETAIN` on all stateful resources in production (RDS, S3, ElastiCache)
- Dev and staging environments use `DESTROY` removal policy with automated off-hours shutdown
- ECS Fargate: right-size task CPU/memory — start small and scale from CloudWatch data
- Lambda: set memory based on profiling — not default 128MB for everything
- Use Savings Plans for predictable ECS / Fargate compute (production workloads > 3 months old)
- S3 Intelligent-Tiering for data stores with variable access patterns > 128KB

## Budget Alerts

Every project must configure AWS Budgets:

```typescript
new budgets.CfnBudget(this, 'MonthlyBudget', {
  budget: {
    budgetName: `${props.projectName}-monthly`,
    budgetType: 'COST',
    timeUnit: 'MONTHLY',
    budgetLimit: { amount: props.monthlyBudgetUsd, unit: 'USD' },
  },
  notificationsWithSubscribers: [{
    notification: {
      notificationType: 'ACTUAL',
      comparisonOperator: 'GREATER_THAN',
      threshold: 80,
    },
    subscribers: [{ subscriptionType: 'EMAIL', address: props.alertEmail }],
  }],
});
```

## Cost Review Gate

Before production deployment: produce a cost estimate using `/estimate-cloud-cost` command. Review must be part of the production readiness checklist.
