# DevSecOps Skill

## Trigger

Use this skill when integrating security controls into CI/CD pipelines, configuring security scanning tools, or reviewing pipeline security configurations.

## What This Skill Does

1. Configures SAST integration (SonarQube, CodeQL, Semgrep) in CI pipelines
2. Sets up dependency vulnerability scanning (OWASP Dependency Check, `npm audit`)
3. Configures secrets scanning (gitleaks, truffleHog) as a pre-commit and CI gate
4. Sets up container image scanning (Trivy, Grype) with threshold-based failure
5. Defines security quality gates with appropriate thresholds for each tool
6. Produces pipeline YAML with all security stages integrated

## Inputs Required

- Current CI/CD platform (GitHub Actions, Jenkins, GitLab CI)
- Technology stack (Java/Maven, Node.js/npm, Docker)
- SonarQube / SonarCloud project key (if applicable)
- Desired security gate thresholds

## Outputs Produced

- Complete CI pipeline YAML with all security stages
- Security gate threshold configuration
- Tool configuration files (`.sonarcloud.properties`, `dependency-check-suppression.xml`)
- Triage guide for common false positives per tool

## Security Gate Defaults

| Gate | Threshold | Failure Action |
|------|-----------|----------------|
| OWASP Dependency Check | CVSS ≥ 7.0 | Build FAIL |
| Container scan | CRITICAL severity | Build FAIL |
| Secrets scan | Any finding | Build FAIL |
| SonarQube Quality Gate | Not passed | Build FAIL |

## Standards Applied

See `.github/instructions/devsecops.instructions.md` and `.claude/standards/cicd.md`

## Related Agents

- `devsecops-engineer` — Claude Code agent for DevSecOps pipeline work
- `security-auditor` — for OWASP Top 10 code reviews
- `ci-engineer` — for broader CI/CD pipeline design
