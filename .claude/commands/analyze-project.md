# /analyze-project — Existing Repository Analyzer

Analyze an existing repository and generate a draft `project-manifest.yaml` + `adoption-report.md`.

Use this when adopting EEIK on a project that already exists — instead of running `/bootstrap` from scratch.

---

## Usage

```
/analyze-project
/analyze-project ./path/to/service
```

If no path is provided, analyzes the current directory.

---

## Execution

Follow the full analysis workflow:

```
generators/project-analyzer/workflows/project-analysis.yaml
```

9 steps — runs automatically:

1. Discover signal files (`pom.xml`, `cdk.json`, `*.tf`, `.github/workflows/`, etc.)
2. Extract technology stack
3. Infer architecture style and patterns from package structure
4. Detect cloud provider and IaC tooling
5. Detect AI capabilities
6. Assess governance maturity — identify gaps
7. Generate `project-manifest.yaml` (with confidence annotations)
8. Generate `adoption-report.md`
9. Output summary with required manual reviews

---

## Output

Two files written to project root:

- `project-manifest.yaml` — draft manifest with `# HIGH/MEDIUM/LOW confidence` comments
- `adoption-report.md` — gap analysis, recommendations, effort estimate for full adoption

---

## After Running

1. Review all `# LOW confidence` fields in `project-manifest.yaml` — these need manual correction
2. Set `project.domain` correctly (affects governance requirements)
3. Run `/validate-manifest` to check for errors
4. Run `/generate-repo` to apply EEIK structure to the existing project
5. Commit both files to a feature branch

---

## What Gets Detected (HIGH confidence)

| Signal | Detected From |
|--------|--------------|
| Java version | `pom.xml <java.version>` |
| Spring Boot | `spring-boot-starter-*` dependencies |
| Database type | `spring.datasource.url` in `application.yaml` |
| Flyway | `flyway-core` dependency |
| AWS CDK | `cdk.json` presence |
| GitHub Actions | `.github/workflows/` directory |
| Outbox pattern | `OutboxEvent.java` or `outbox_events` migration |
| LangGraph | `langgraph` in `requirements.txt` |

## What Needs Manual Review (LOW confidence)

| Field | Why Manual |
|-------|-----------|
| `project.domain` | Cannot infer business domain from code alone |
| `project_type` | Greenfield vs modernization is a business context question |
| `governance.profile` | Regulatory requirements are external to the codebase |
| `cloud.multi_account` | Account topology not visible from code |
