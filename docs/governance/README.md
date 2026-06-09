# Governance

Architecture reviews, security reviews, AI governance, production readiness, and compliance.

---

## Contents

| Document | Covers |
|----------|--------|
| [governance-overview.md](governance-overview.md) | Governance model, profiles, and review lifecycle |

---

## What This Section Covers

EEIK embeds governance into the project lifecycle rather than treating it as an afterthought. Governance requirements are derived from the manifest and enforced through generated CI gates, review checklists, and mandatory agent workflows.

### Governance Profiles

| Profile | Applies To | Mandatory Reviews |
|---------|-----------|-------------------|
| `basic` | PoC, internal tools | None |
| `standard` | Internal products | Architecture + Security |
| `regulated` | Insurance, Banking, Healthcare | Architecture + Security + PRR + Compliance |
| `enterprise` | Enterprise platforms | All reviews + ARB gate |

The profile is set in `project-manifest.yaml` under `governance.profile`.

### Review Types

| Review | Agent | Timing | Blocking |
|--------|-------|--------|---------|
| Architecture Review | `architect`, `arb-reviewer` | Before implementation | Yes (standard+) |
| Security Review | `security-auditor` | Before production deploy | Yes (standard+) |
| Production Readiness Review (PRR) | `ops-engineer`, `sre-engineer` | Before first prod deploy | Yes (regulated+) |
| AI Governance Review | `ai-governance-officer` | Before AI model goes live | Yes (if AI enabled) |
| Compliance Review | `arb-reviewer` | Per regulatory checkpoint | Yes (regulated+) |

### Slash Commands

| Command | Action |
|---------|--------|
| `/review` | Full PR review: correctness, security, performance, quality |
| `/security-scan [path]` | OWASP Top 10 + secrets scan |
| `/deploy-check "env: X, service: Y"` | Pre-deployment readiness checklist |

### Governance Workflow

For formal Architecture Review Board submissions:

```
#file:.github/prompts/workflows/arb-review-workflow.prompt.md
```

For AI system governance:

```
#file:.github/prompts/workflows/ai-governance-review.prompt.md
```

### Generated Governance Artifacts

The Governance Generator produces these when you run `/generate-repo`:

```
docs/
├── review-checklist.md        ← Technology and security review checklist
├── risk-register.md           ← Live project risk register (regulated+)
├── compliance-checklist.md    ← Regulatory compliance items (regulated+)
└── architecture/
    └── solution-architecture.md  ← Architecture document (all profiles)
```
