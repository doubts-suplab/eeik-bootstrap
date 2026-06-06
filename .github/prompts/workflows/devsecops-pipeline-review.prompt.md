# DevSecOps Pipeline Review Workflow

Review and harden the CI/CD pipeline for the following service.

**Service:** $SERVICE_NAME
**Pipeline:** GitHub Actions / Jenkins / GitLab CI

## Workflow Steps

### Step 1 — Current State Assessment
Activate the `devsecops-engineer` agent to audit the existing pipeline:
- [ ] Review `.github/workflows/` or equivalent pipeline definition
- [ ] Identify missing security stages (secrets scan, SAST, dependency check, container scan)
- [ ] Check action version pinning (SHA vs. mutable tags)
- [ ] Review GITHUB_TOKEN permissions (least privilege)
- [ ] Check for hardcoded credentials in pipeline YAML

### Step 2 — Security Gate Gap Analysis

| Gate | Present | Threshold Defined | Failure Action |
|------|---------|------------------|----------------|
| Secrets scan | ❌/✅ | ❌/✅ | ❌/✅ |
| OWASP Dependency Check | ❌/✅ | ❌/✅ | ❌/✅ |
| SAST (SonarQube/CodeQL) | ❌/✅ | ❌/✅ | ❌/✅ |
| Container image scan | ❌/✅ | ❌/✅ | ❌/✅ |
| DAST (if applicable) | ❌/✅ | ❌/✅ | ❌/✅ |

### Step 3 — Remediation
For each missing or misconfigured gate:
- [ ] Add the security stage to the pipeline
- [ ] Configure appropriate threshold
- [ ] Confirm failure action blocks pipeline progression

### Step 4 — Artefact Security
- [ ] Docker image scanned before push to ECR
- [ ] Image tagged with git SHA (not `latest` in production)
- [ ] SBOM generated for production images
- [ ] Image signing configured (if required)

### Step 5 — Validation
- [ ] Run the pipeline with a known-bad input to confirm security gates fail correctly
- [ ] Confirm suppression file for accepted CVEs is peer-reviewed and dated
- [ ] Verify secrets scanning catches a test credential (use a non-real test pattern)

## Output

Hardened pipeline YAML, security gate configuration, and suppression file with peer review requirement documented.
