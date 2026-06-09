# Project Analyzer

## Purpose

Analyze an existing repository and infer a `project-manifest.yaml` from what's actually in the codebase.

This is the **adoption path** for teams that already have a project — they don't start with `/bootstrap`; they start with `/analyze-project`.

## Why It Matters

Most EEIK adopters have an existing codebase. Without a project-analyzer, they must fill in the manifest manually, which creates friction and inaccuracies. The analyzer reads the actual code to produce an accurate starting manifest.

## Flow

```
Existing repo (any state)
        ↓
/analyze-project
        ↓
Project Analyzer reads:
  pom.xml / pyproject.toml / package.json
  src/ directory structure
  Dockerfile / docker-compose.yaml
  .github/workflows/
  infrastructure/ (CDK / Terraform)
  application.yaml / .env files
        ↓
Infers:
  Technology stack
  Architecture style (monolith / microservices / serverless)
  Patterns in use (DDD / CQRS detected from package names)
  Cloud provider and IaC tooling
  Governance gaps (what's missing)
        ↓
Generates:
  project-manifest.yaml (draft)
  adoption-report.md (gaps + recommendations)
        ↓
/validate-manifest → /generate-repo (fills gaps)
```

## Accuracy

The analyzer produces a **draft** manifest — not a perfect one. The user must review and correct it. The output includes confidence levels for each inferred field.

## Structure

```
project-analyzer/
├── README.md
├── prompts/
│   ├── analyze-project.md        ← Master analysis prompt
│   └── infer-architecture.md     ← Architecture style detection
├── extractors/
│   ├── tech-stack-extractor.md   ← Language, framework, version detection
│   ├── cloud-extractor.md        ← Cloud provider and IaC detection
│   ├── architecture-extractor.md ← Style and pattern inference
│   └── governance-extractor.md   ← Review maturity assessment
├── workflows/
│   └── project-analysis.yaml     ← End-to-end analysis workflow
└── reports/
    └── adoption-report-template.md
```

## Command

```
/analyze-project [path]
```

If `[path]` is omitted, analyzes the current working directory.
