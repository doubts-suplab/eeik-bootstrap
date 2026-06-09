# Governance Extractor

## Purpose

Assess the current governance maturity of an existing project and infer an appropriate governance profile.

---

## Signals to Read

### Evidence of Architecture Governance
```
docs/decisions/ADR-*.md present → architecture decisions recorded
.github/CODEOWNERS → ownership defined
PR templates in .github/PULL_REQUEST_TEMPLATE.md → process defined
Branch protection (cannot read from code — flag for manual check)
```

### Evidence of Security Process
```
.snyk or .snyk-policy → Snyk configured
.github/workflows/*security*.yaml → security scan in CI
SECURITY.md → responsible disclosure policy
dependabot.yml → automated dependency updates
```

### Evidence of Compliance
```
docs/compliance/ directory → compliance tracking
GDPR, PCI-DSS, HIPAA mentioned in README or docs/ → regulatory context
Data classification documents → regulated domain
```

### Evidence of Review Process
```
.github/workflows/deploy-prod.yaml with:
  environment: production
  → environment protection configured (suggests approval requirement)
Multiple reviewers in CODEOWNERS → multi-reviewer requirement
```

---

## Profile Inference Rules

```
Profile: basic
  Signals: No ADRs, no security scans in CI, no CODEOWNERS
  Likely: poc or early-stage project

Profile: standard
  Signals: ADRs present OR security scan in CI OR CODEOWNERS
  Likely: production workload, generic domain

Profile: regulated
  Signals: compliance/ docs OR "GDPR/PCI/HIPAA" in README/docs
           AND production approval gates
  Likely: insurance, banking, healthcare domain

Profile: enterprise
  Signals: Multiple CODEOWNERS teams, ADRs + compliance + security scans
           AND multi-account CDK setup
           AND evidence of ARB process
  Likely: large enterprise program
```

---

## Gap Analysis

For each detected gap, produce a recommendation:

| Gap | Current State | Recommendation |
|-----|--------------|----------------|
| No ADRs | docs/decisions/ missing | Run /create-adr for key past decisions |
| No security scan | No CI security gate | Add OWASP DC or Snyk to build.yaml |
| No test coverage gate | No JaCoCo config | Add jacoco-maven-plugin with minimum coverage |
| No structured logging | System.out.println detected | Replace with SLF4J |
| No secrets scan | No trufflehog/detect-secrets | Add pre-commit hook and CI gate |
| Missing CODEOWNERS | No ownership defined | Create .github/CODEOWNERS |
