# CI/CD Pipeline Standards

> Mandatory standards for all CI/CD pipeline configuration. Enforced by `ci-engineer` and `devsecops-engineer` agents.

---

## Pipeline Structure

All pipelines must implement these stages in order:

```
build → unit-test → integration-test → security-scan → publish-artefact → deploy-dev → [approve] → deploy-staging → [approve] → deploy-prod
```

Skipping stages is not permitted. If a stage is not applicable (e.g., no integration tests yet), create a placeholder that passes with a documented reason.

---

## GitHub Actions Standards

### Security
- Set explicit `permissions` on every workflow — never rely on default token permissions
- Use `permissions: contents: read` as the minimum; expand only what is needed
- Never store secrets in workflow YAML — use GitHub Encrypted Secrets or OIDC
- Use OIDC for AWS authentication in CI — no long-lived access keys

```yaml
permissions:
  contents: read
  id-token: write  # required for OIDC
```

### Action Versioning
- Pin third-party actions to SHA hash for security — not to a mutable tag
- Use `actions/checkout@v4`, `actions/setup-java@v4` — check for current major versions
- Never use `@latest` or floating minor versions

### Timeouts
- Set `timeout-minutes` on every job — default is 6 hours (unacceptable cost risk)
- Standard timeouts: build (15m), test (30m), security scan (20m), deploy (20m)

### Caching
- Cache Maven `~/.m2/repository` keyed on `pom.xml` hash
- Cache npm `~/.npm` keyed on `package-lock.json` hash
- Cache Docker layers using `docker/build-push-action` cache backends

---

## Quality Gates (Mandatory — Pipeline Must Fail on Breach)

| Gate | Tool | Threshold | Stage |
|------|------|-----------|-------|
| Unit test pass rate | JUnit / Karma | 100% | `unit-test` |
| Code coverage | JaCoCo / Istanbul | 80% line, 70% branch | `unit-test` |
| Dependency vulnerabilities | OWASP Dep Check | CVSS ≥ 7.0 | `security-scan` |
| Container vulnerabilities | Trivy | CRITICAL severity | `security-scan` |
| Secrets scan | gitleaks | Any finding | `security-scan` |
| Static analysis | SonarQube Quality Gate | Not passed | `security-scan` |

---

## Deployment Patterns

### Feature Branches
- Build and test on every push — no deployment
- PR status checks must pass before merge to `main`

### Main Branch
- Automatically deploy to `dev` environment after merge
- Staging deployment requires manual approval
- Production deployment requires two approvals (Tech Lead + Engineering Manager)

### Environment Promotion
- Deploy the same Docker image through all environments — never rebuild
- Image identified by git commit SHA tag: `{registry}/{service}:{git-sha}`
- Never use `latest` tag in any environment

---

## Artefact Standards

- Docker images pushed to Amazon ECR
- Image tagged with: `{git-sha}` (primary), `{branch-name}` (secondary), `latest` (main branch only)
- Image signed with AWS Signer or cosign for production artefacts
- Maven artefacts published to CodeArtifact (if applicable)

---

## Branch Protection Rules

Enforce on `main`:
- Require PR with minimum 1 approval (2 for production-impacting changes)
- Require all status checks to pass before merge
- Require branches to be up to date before merging
- No force-push to `main`
- No deletions of `main`
