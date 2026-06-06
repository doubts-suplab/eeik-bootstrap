# /deploy-check — Pre-Deployment Readiness Checklist

Run a pre-deployment readiness check for a specific service and environment.

## Usage

```
/deploy-check "env: staging, service: payment-service"
/deploy-check "env: prod, service: order-service"
```

## What This Command Does

1. Activates the `aws-deploy-helper` agent
2. Validates AWS credentials and target environment
3. Checks all pre-deployment conditions
4. Confirms the deployment command and rollback path
5. Produces a go/no-go recommendation

## Pre-Deployment Checklist

### Infrastructure
- [ ] AWS credentials: `aws sts get-caller-identity` → expected account + region
- [ ] Target ECS cluster is healthy: all existing tasks running
- [ ] ALB target group: all existing targets healthy before we start
- [ ] Parameter Store / Secrets Manager: all required keys exist for this environment

### Artefact
- [ ] Docker image tag confirmed: `{registry}/{service}:{git-sha}`
- [ ] Image scan passed: no CRITICAL vulnerabilities (Trivy)
- [ ] Image pushed to ECR for the target environment

### Database
- [ ] Flyway migration status: up to date / pending migrations reviewed
- [ ] Pending migration is backward compatible with the current running version (for zero-downtime)
- [ ] Database backup confirmed (for staging and production)

### Testing
- [ ] All CI stages passed for the commit being deployed
- [ ] Staging smoke tests pass (if deploying to production)
- [ ] No open `[BLOCKER]` findings in the PR review

### Operational
- [ ] Runbook updated for any new features or changed behaviour
- [ ] On-call is aware of the deployment (for P1-impact services)
- [ ] Rollback path confirmed: previous ECS task definition revision identified

## Output Format

```
## Deployment Readiness: {service} → {environment}

### Status: ✅ GO / ❌ NO-GO

### Checklist Results
✅ AWS credentials: account 123456789012, region eu-west-1
✅ ECR image: {registry}/{service}:{sha}
✅ Parameter Store: all keys present
❌ Flyway: 2 pending migrations not yet reviewed
⚠️  WARNING: Deploying at 16:45 — approaching Friday cutoff

### Deployment Command
{exact command to run}

### Rollback Command
{exact rollback command}
```

## Notes

- Never deploy to production on Fridays after 15:00 local time (team operational constraint)
- Always confirm the rollback path before starting any deployment
- Production deployments require Tech Lead acknowledgement
