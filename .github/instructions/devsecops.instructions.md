---
applyTo: "**/.github/workflows/**, **/security/**, **/Dockerfile*, **/docker-compose*.yml"
description: "DevSecOps CI/CD security gate sequence, SBOM generation, container scanning, secrets detection, OPA policy enforcement, and supply chain security standards."
---

# DevSecOps — Copilot Instructions

> Applied automatically when working with CI/CD workflows, Dockerfiles, docker-compose files, and security configuration. Loaded alongside copilot-instructions.md.

---

## Security Gate Sequence

Every CI/CD pipeline must enforce security gates in this order. A failure at any gate **blocks the pipeline** — gates are not advisory.

```
[ Build ] → [ SAST ] → [ Dependency Check ] → [ Container Scan ] → [ Secrets Scan ] → [ DAST ] → [ SBOM ] → [ OPA Policy ] → [ Deploy ]
```

| Gate | Tool | Failure Threshold | Stage |
|------|------|------------------|-------|
| SAST | Semgrep (rules: p/java, p/python, p/secrets) | Any CRITICAL or HIGH finding | Pre-merge |
| Dependency check | OWASP Dependency-Check 9.x, `mvn dependency-check:check` | CVSS ≥ 7.0 (HIGH) | Pre-merge |
| Container image scan | Trivy 0.50+ | CRITICAL = fail, HIGH = warning | Pre-merge |
| Secrets scan | Gitleaks 8.x | Any secret detected | Pre-commit + pre-merge |
| DAST | OWASP ZAP 2.14 (baseline scan) | Any CRITICAL or HIGH alert | Post-deploy to staging |
| SBOM generation | CycloneDX (Maven) / Syft (containers) | Missing SBOM = fail deploy | Pre-deploy |
| OPA policy | OPA 0.60 + Rego policies in `security/opa/policies/` | Any deny rule fires | Pre-deploy |

---

## SAST — Semgrep Configuration

`.semgrep.yml` at repo root:

```yaml
rules:
  - id: no-sql-injection
    pattern: $STMT.execute($INPUT + ...)
    message: "SQL injection risk — use parameterized queries"
    severity: ERROR
    languages: [java]

# Run in CI:
# semgrep --config=p/java --config=p/python --config=p/secrets \
#   --error --json --output=semgrep-results.json .
# Fail on exit code 1 (findings present)
```

GitHub Actions step:

```yaml
- name: SAST — Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/java
      p/python
      p/secrets
      p/owasp-top-ten
  env:
    SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

---

## Dependency Vulnerability Check

### Maven (Java)

```xml
<!-- pom.xml — add to build/plugins -->
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <version>9.0.9</version>
  <configuration>
    <failBuildOnCVSS>7</failBuildOnCVSS>
    <suppressionFiles>
      <suppressionFile>security/dependency-check-suppression.xml</suppressionFile>
    </suppressionFiles>
    <format>JSON</format>
    <outputDirectory>${project.build.directory}/security</outputDirectory>
  </configuration>
  <executions>
    <execution>
      <goals><goal>check</goal></goals>
    </execution>
  </executions>
</plugin>
```

### Python

```bash
# pip-audit: audits against PyPA Advisory Database
pip-audit --requirement requirements.txt --format json --output audit-results.json
# Fail on CVSS >= 7.0
pip-audit --requirement requirements.txt --vulnerability-service pypa --fail-on MEDIUM
```

### Suppression Process

CVE suppressions in `security/dependency-check-suppression.xml` must include:
- The CVE ID
- Justification: why the vulnerability is not exploitable in this context
- Expiry date (max 90 days)
- Approver name

---

## Container Scanning — Trivy

```bash
# Scan image — fail on CRITICAL, warn on HIGH
trivy image \
  --severity CRITICAL,HIGH \
  --exit-code 1 \
  --format sarif \
  --output trivy-results.sarif \
  --ignore-unfixed \
  myregistry.azurecr.io/myservice:${GIT_SHA}

# Scan Dockerfile for misconfigurations
trivy config \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  Dockerfile
```

### Severity Thresholds

| Severity | Pipeline Action |
|----------|----------------|
| CRITICAL | Build fails — must be patched before merge |
| HIGH | Build warning — must be resolved within 7 days; tracked in security backlog |
| MEDIUM | Logged only — review quarterly |
| LOW/NEGLIGIBLE | Suppressed |

### Dockerfile Security Standards

```dockerfile
# REQUIRED: Use a specific digest, not a floating tag
FROM eclipse-temurin:21.0.4_7-jre-jammy@sha256:abc123def456...

# REQUIRED: Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# REQUIRED: No secrets in ENV or ARG
# WRONG: ENV DATABASE_PASSWORD=secret123
# RIGHT: Read from AWS Secrets Manager at runtime

# REQUIRED: Read-only root filesystem where possible
# docker run --read-only ...

# REQUIRED: Drop all capabilities
# docker run --cap-drop ALL --cap-add NET_BIND_SERVICE ...

# Minimise layers — combine RUN commands
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-* \
    && rm -rf /var/lib/apt/lists/*
```

---

## Secrets Detection — Gitleaks

`gitleaks.toml` at repo root:

```toml
[extend]
useDefault = true

[[rules]]
id = "aws-access-key"
description = "AWS Access Key ID"
regex = '''(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'''
tags = ["key", "AWS"]

[[rules]]
id = "internal-api-token"
description = "Internal API token pattern"
regex = '''ent_[a-zA-Z0-9]{32,}'''
tags = ["token", "internal"]

[allowlist]
description = "Test fixtures and known safe values"
paths = [
  '''src/test/resources/.*''',
  '''\.github/workflows/.*'''  # GitHub Actions uses ${{ secrets.X }} — not real values
]
```

Pre-commit hook (add to `.git/hooks/pre-commit`):

```bash
#!/bin/bash
gitleaks protect --staged --config=gitleaks.toml --redact
if [ $? -ne 0 ]; then
  echo "ERROR: Secrets detected. Remove secrets before committing."
  exit 1
fi
```

---

## SBOM — Software Bill of Materials

### CycloneDX for Maven

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.cyclonedx</groupId>
  <artifactId>cyclonedx-maven-plugin</artifactId>
  <version>2.7.11</version>
  <executions>
    <execution>
      <phase>package</phase>
      <goals><goal>makeAggregateBom</goal></goals>
    </execution>
  </executions>
  <configuration>
    <projectType>library</projectType>
    <schemaVersion>1.5</schemaVersion>
    <includeBomSerialNumber>true</includeBomSerialNumber>
    <includeCompileScope>true</includeCompileScope>
    <includeTestScope>false</includeTestScope>
    <outputFormat>json</outputFormat>
    <outputName>bom</outputName>
  </configuration>
</plugin>
```

### SPDX for Containers (Syft)

```bash
# Generate SPDX SBOM from container image
syft myregistry.azurecr.io/myservice:${GIT_SHA} \
  --output spdx-json \
  --file sbom-container.spdx.json

# Attach SBOM to OCI image (cosign)
cosign attach sbom \
  --sbom sbom-container.spdx.json \
  --type spdx \
  myregistry.azurecr.io/myservice:${GIT_SHA}
```

SBOMs must be stored in S3: `s3://enterprise-sbom-store/{service-name}/{git-sha}/bom.json`.

---

## SLSA Level 2 Requirements

All production container images must meet SLSA Level 2:

| Requirement | Implementation |
|------------|---------------|
| Hosted build platform | GitHub Actions (not self-hosted runners for production builds) |
| Scripted build | No manual steps; all in `build.yml` |
| Build provenance generated | `actions/attest-build-provenance@v1` |
| Provenance signed | Sigstore/Cosign via GitHub OIDC |

```yaml
# .github/workflows/build.yml
- name: Generate SLSA provenance
  uses: actions/attest-build-provenance@v1
  with:
    subject-name: myregistry.azurecr.io/myservice
    subject-digest: ${{ steps.build.outputs.digest }}
    push-to-registry: true
```

Verify provenance before deploy:

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp "https://github.com/enterprise-org/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.azurecr.io/myservice:${GIT_SHA}
```

---

## DAST — OWASP ZAP

```yaml
# .github/workflows/dast.yml — runs against staging only
- name: OWASP ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.12.0
  with:
    target: 'https://staging.internal.enterprise.com'
    rules_file_name: 'security/zap-rules.tsv'
    cmd_options: '-a -j'  # -a: include alpha rules; -j: use Ajax spider
    fail_action: true      # Fail on CRITICAL/HIGH
  env:
    ZAP_AUTH_HEADER: ${{ secrets.ZAP_AUTH_HEADER }}
```

ZAP rules file `security/zap-rules.tsv`:

```
# ID	Action	Parameters	Name
10202	FAIL		CWEID 1275 - Sensitive Cookie without SameSite Attribute
10021	FAIL		X-Content-Type-Options Header Missing
10038	FAIL		Content Security Policy (CSP) Header Not Set
90022	WARN		Application Error Disclosure
```

---

## OPA/Rego Policy Files

Policy files in `security/opa/policies/`:

```rego
# security/opa/policies/container-policy.rego
package enterprise.container

deny[msg] {
  not input.spec.securityContext.runAsNonRoot
  msg := "Containers must not run as root (runAsNonRoot: true)"
}

deny[msg] {
  not input.spec.containers[_].resources.limits.cpu
  msg := "All containers must specify CPU limits"
}

deny[msg] {
  input.spec.containers[_].image == _
  not regex.match(`^myregistry\.azurecr\.io/`, input.spec.containers[_].image)
  msg := sprintf("Image must be from approved registry: %v", [input.spec.containers[_].image])
}
```

Evaluate in CI:

```bash
opa eval \
  --input k8s-deployment.json \
  --data security/opa/policies/ \
  --format pretty \
  "data.enterprise.container.deny" | \
  python3 -c "import sys,json; findings=json.load(sys.stdin); sys.exit(1) if findings['result'][0]['expressions'][0]['value'] else sys.exit(0)"
```

---

## CVE Remediation Workflow

When a CRITICAL or HIGH CVE is identified by Trivy or OWASP Dependency-Check:

1. **Assess exploitability**: Is the vulnerable code path reachable from the application's attack surface?
2. **Patch or suppress**:
   - If exploitable: update the dependency; target fix within 24h (CRITICAL) or 7 days (HIGH)
   - If not exploitable: add a suppression entry with justification and 90-day expiry
3. **Open a Jira ticket** with label `security-vuln`, CVE ID, and CVSS score
4. **Link to pipeline failure** in the Jira ticket for traceability
5. **Exception process**: If patching is not possible within SLA, a formal risk acceptance must be approved by the CISO with a documented compensating control

---

## AWS Config Rules for Compliance

Ensure these AWS Config Rules are enabled in all accounts:

```bash
# Check that all Config rules pass — fail if any non-compliant
aws configservice describe-compliance-by-config-rule \
  --compliance-types NON_COMPLIANT \
  --query 'ComplianceByConfigRules[].ConfigRuleName' \
  --output text

# Required rules:
# - s3-bucket-ssl-requests-only
# - encrypted-volumes
# - rds-storage-encrypted
# - guardduty-enabled-centralized
# - iam-no-inline-policy-check
# - root-mfa-enabled
# - vpc-flow-logs-enabled
```
