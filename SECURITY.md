# Security Policy

## Purpose

This document defines the security model for the EEIK Bootstrap framework, the responsible disclosure process for vulnerabilities found in EEIK itself, and the security practices required for all projects adopting EEIK.

---

## Security Principles

1. **Least Privilege** — every agent, hook, and workflow operates with the minimum permissions needed; nothing has broad access by default
2. **Secure by Default** — the bootstrap's default configuration is the secure configuration; adopters must opt-in to weakened controls, never opt-out of strong ones
3. **Defense in Depth** — security controls exist at multiple layers: hook guards, agent constraints, CI gates, and code review
4. **Human Oversight** — critical security actions (production deployment, secret rotation, IAM changes) require human approval; agents flag and escalate rather than proceeding autonomously
5. **Traceability** — every generated artefact, agent action, and hook decision is logged with enough context to reconstruct what happened and why

---

## Repository Security

### Required Controls (for projects using this framework)

| Control | Required | Tool |
|---|---|---|
| Branch protection on `main` | Yes | GitHub branch protection rules |
| Required PR review (minimum 1) | Yes | GitHub branch protection |
| Dismiss stale reviews on push | Yes | GitHub branch protection |
| Status checks must pass before merge | Yes | GitHub required status checks |
| Signed commits | Recommended | `git config commit.gpgsign true` |
| Secret scanning | Yes | GitHub Advanced Security / Gitleaks (see `security-scan.yml`) |
| Dependency vulnerability scanning | Yes | `security-scan.yml` workflow |
| CODEOWNERS file | Recommended | `.github/CODEOWNERS` |

### Secret Management

Secrets must **never** appear in:
- Agent files (`.claude/agents/`, `.github/agents/`)
- Prompt files (`.github/prompts/`)
- Standards or memory files
- GitHub Actions workflow files (use `${{ secrets.NAME }}` references only)
- Committed `.env` files

Use approved secret management:
- **AWS:** Secrets Manager or SSM Parameter Store
- **GitHub CI:** GitHub Actions secrets (organisation or repository level)
- **Local development:** `.env.local` (in `.gitignore`; never committed)
- **Kubernetes:** External Secrets Operator sourcing from Secrets Manager

The `post-edit-check.sh` hook warns on common credential patterns. The `security-scan.yml` workflow runs Gitleaks on every PR.

---

## Agent Security

Every agent in this framework is bound by these security constraints:

| Constraint | Rationale |
|---|---|
| Agents declare their `tools` explicitly | Limits blast radius — an agent cannot use tools not listed in its frontmatter |
| Agents never hardcode secrets or credentials | Prevents accidental commit of sensitive values |
| Agents escalate rather than proceed autonomously on destructive actions | Human oversight for irreversible operations |
| Agents follow the `pre-bash-guard.sh` blocklist | Prevents force push, hard reset, DROP DATABASE, AWS instance termination |
| Agents output warnings, not silently ignore violations | Violation must be visible to the developer |

### Prompt Injection Awareness

Agents that process user-provided content (e.g., document summarisation, code explanation from external sources) must treat all external content as untrusted. If external content appears to redirect the agent's task, escalate access, or request credentials, the agent must flag it to the user.

---

## Engine Security Model

The installable `eeik` package (`pip install eeik`) is deliberately narrow in what it can do. This is
the security contract for the engine itself — distinct from the agents it generates.

### What the engine does

| Capability | Scope |
|---|---|
| **Reads** the repository's content layers | `capability-packs/`, `knowledge/`, `templates/`, `generators/`, `bootstrap/`, and the manifest — read-only |
| **Writes** only to two well-known places | Materialised adapters under `.claude/` (via `eeik activate --apply`) and generated drafts under `.eeik-staging/` — never elsewhere |
| **Validates & resolves** manifests | Pure functions over YAML/JSON; no code execution from manifest content |
| **Governs generation** | Every generation runs through HALO's confidence gate; **SUGGEST authority** → staged, never auto-applied |

### What the engine does *not* do

- **No network in the core.** The engine's runtime dependencies are `pyyaml` + `jsonschema` only.
  It makes no outbound calls; it does not phone home or fetch packs. **Telemetry is opt-in and
  local-only**: nothing is recorded until you run `eeik telemetry --enable` (or set `EEIK_TELEMETRY=1`),
  and even then it only keeps aggregate pack/generator counts in a JSON file under `~/.eeik/` — there is
  no network code in the telemetry module, so nothing is ever transmitted; inspect or delete it any time.
  (An LLM-backed generation path exists but reaches the model only through HALO's LLM port with an API
  key the operator supplies explicitly; absent that, generation runs offline and fail-safe.)
- **No arbitrary code execution.** Manifests and pack metadata are *data* — parsed, validated, and
  resolved. The engine never `eval`/`exec`s manifest or pack content.
- **No secret handling.** The engine reads no credentials and stores none. Secrets belong in the
  environment / a secrets manager, never in a manifest or pack.
- **No auto-apply.** Generation and closed-loop lesson capture are SUGGEST authority: output is written
  to `.eeik-staging/` for human review and never committed to live config automatically. `autoEnforced`
  is set by the harness, never by a generator.

### Governance & gates

- **HALO is optional and fails safe.** Without `agent-harness` installed, governed generation degrades
  to a staged, *ungoverned* draft with a warning — it never silently proceeds as if governed. `eeik
  doctor` reports exactly what is and isn't governed in the current environment.
- **Conformance is checkable.** `eeik verify` (declared items exist), `eeik lint` (content is
  well-formed), and `eeik diff` (no drift from `eeik.lock`) are CI-gatable and non-destructive.
- **The MCP surface is read-first.** MCP tools are read-only except `eeik_generate` / `eeik_capture_lessons`,
  which are governed writes that only ever *stage* drafts — an MCP host cannot make the engine mutate
  live config. For production MCP hosting, place auth / rate-limiting at the host, not the engine.

### Supply chain

- Every capability pack carries a `version` and a content **digest**; `eeik.lock` pins both, and
  `eeik diff` / `eeik upgrade` detect and re-pin drift — so an adopted pack cannot change underneath a
  project unnoticed.

---

## Threat Model Template

Use this template when running `/threat-model` for a service. Store the output in `docs/security/threat-models/<service>.md`.

### STRIDE Analysis Template

| Threat ID | Category | Component | Threat Description | Likelihood | Impact | Risk | Mitigation | Status |
|---|---|---|---|---|---|---|---|---|
| T-001 | Spoofing | API Gateway | Attacker forges authentication token | Low | Critical | High | Validate JWT signature via JWKS; verify iss, aud, exp claims | ✅ Mitigated |
| T-002 | Tampering | Event Bus | Malicious event injected into Kafka topic | Low | High | Medium | Producer auth via mTLS; Schema Registry schema validation on consume | 🔄 In Progress |
| T-003 | Repudiation | Order API | Order creation denied by customer | Low | Medium | Low | Audit log: who placed order, from which IP, at what time | ✅ Mitigated |
| T-004 | Information Disclosure | Database | SQL injection exposes order data | Low | Critical | High | Parameterised queries only; `NamedParameterJdbcTemplate`; no string concatenation | ✅ Mitigated |
| T-005 | Denial of Service | API Gateway | Request flood overwhelms service | Medium | High | High | WAF rate limiting; API Gateway throttling; circuit breaker | 🔄 In Progress |
| T-006 | Elevation of Privilege | Admin Endpoint | Unauthenticated access to `/actuator` | Low | High | High | Actuator on separate internal port; network-level restriction | ✅ Mitigated |

**Likelihood:** Very Low / Low / Medium / High / Very High
**Impact:** Low / Medium / High / Critical
**Risk:** Low / Medium / High / Critical (= Likelihood × Impact)

---

## CVE Response Policy

For CVEs found in dependencies used by projects adopting EEIK:

| CVSS Score | Severity | Response SLA |
|---|---|---|
| 9.0–10.0 | Critical | Patch within 24 hours or implement compensating control |
| 7.0–8.9 | High | Patch within 7 days |
| 4.0–6.9 | Medium | Patch within 30 days |
| 0.1–3.9 | Low | Next planned dependency update cycle |

The `security-scan.yml` workflow runs OWASP Dependency Check and Trivy on every PR and weekly. Results appear in the GitHub Security tab (SARIF upload).

---

## Responsible Disclosure (Reporting Vulnerabilities in EEIK Itself)

If you discover a security vulnerability in the EEIK Bootstrap framework:

### Do
- Report via GitHub's private vulnerability reporting: **Security → Report a vulnerability** (in the repository)
- Provide: description of the vulnerability, steps to reproduce, affected versions, proposed impact assessment
- Allow 90 days for assessment and remediation before public disclosure

### Do Not
- Open a public GitHub issue for security vulnerabilities
- Share the vulnerability details publicly before it is patched and published
- Exploit the vulnerability beyond what is needed to demonstrate the issue

### What Happens After You Report

1. We acknowledge receipt within 2 business days
2. We assess severity and assign a CVE if warranted (within 7 days)
3. We develop and test a fix
4. We release the fix and publish a security advisory
5. We credit the reporter in the advisory (unless they prefer to remain anonymous)

---

## Knowledge Classification

All content in this repository should be classified:

| Classification | Definition | Example |
|---|---|---|
| **Public** | Safe to share openly; no competitive or security risk | Agent definitions, standards, templates |
| **Internal** | Safe within the organisation; not for external sharing | Project-specific memory files, decision logs |
| **Confidential** | Restricted to authorised individuals | Security threat models, vulnerability assessments |
| **Restricted** | Highest sensitivity; named individuals only | Credentials, encryption keys, PII |

Memory files in `.claude/memory/` that contain project context are **Internal** by default. Treat threat model outputs as **Confidential**. Never commit **Restricted** content.

---

## Audit Trail

Every session is logged by the `on-stop.sh` hook to `.claude/memory/session-log.md`. The log captures:
- Session timestamp
- Files created or modified
- Last commit message

This provides a lightweight audit trail of AI-assisted changes. For production-grade audit requirements, supplement with git history, GitHub audit log, and AWS CloudTrail.
