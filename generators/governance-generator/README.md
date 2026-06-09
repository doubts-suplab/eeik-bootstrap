# Governance Generator

## Purpose

Generates governance artifacts for a project based on its selected governance profile.

The Governance Generator reads the `governance_profile` field from `selected-capabilities.yaml` and produces the mandatory review checklists, CI/CD gate configuration, documentation requirements, and compliance templates appropriate to that profile.

## Design Principle

```
selected-capabilities.yaml (governance_profile: regulated)
        ↓
Governance Generator
        ↓
docs/review-checklist.md
docs/risk-register.md
.github/workflows/governance-gate.yml
CLAUDE.md (governance section)
.github/copilot-instructions.md (governance section)
```

## Governance Profiles

| Profile | Applies To | Mandatory Reviews | CI Gates |
|---------|-----------|-------------------|----------|
| `basic` | PoC, internal tools | None | Build + Test |
| `standard` | Internal products, non-regulated | Architecture, Security | Build + Test + Security scan + Prod approval |
| `regulated` | Insurance, Banking, Healthcare | Architecture + Security + PRR + Compliance | All gates + Manual approval on staging and prod |
| `enterprise` | Enterprise platforms | All reviews + ARB gate | All gates + ARB sign-off |

Profile definitions live in `governance-profiles/`.

## Generated Artifacts

| Artifact | Template | Profile |
|----------|----------|---------|
| `docs/review-checklist.md` | `governance-profiles/{profile}.yaml` | all |
| `docs/risk-register.md` | `capability-packs/governance/templates/risk-register.md.template` | standard+ |
| `docs/compliance-checklist.md` | governance template | regulated+ |
| `.github/workflows/governance-gate.yml` | CI gate config | all |
| `CLAUDE.md` governance section | `templates/claude-md-{profile}.md` | all |
| `.github/copilot-instructions.md` | `templates/copilot-{profile}.md` | all |

## Files

```
governance-generator/
│
└── governance-profiles/
    ├── basic.yaml       ← PoC / internal tools profile
    ├── standard.yaml    ← Standard production profile
    ├── regulated.yaml   ← Regulated industry profile
    └── enterprise.yaml  ← Full enterprise governance profile
```
