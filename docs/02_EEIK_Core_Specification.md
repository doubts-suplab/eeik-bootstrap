# EEIK Core Specification

> **Version:** 1.0 — 2026-06-06
> **Status:** Current

---

## 1. Vision and Principles

EEIK (Enterprise Engineering Intelligence Kit) is a bootstrap seed that makes AI-assisted development context-aware from the moment a developer opens a project. The kit operates across two AI tool layers simultaneously:

- **GitHub Copilot layer** (`.github/`) — auto-applied instructions, agent personas, prompt libraries, skills, and lifecycle hooks
- **Claude Code layer** (`.claude/`) — specialist agents, slash commands, persistent memory, coding standards, and safety hooks

### Design Principles

| Principle | Expression |
|-----------|-----------|
| **Context over conversation** | Project knowledge is embedded in files, not re-explained every session |
| **Specialist over generalist** | Precise agent personas produce higher-quality, more consistent outputs than a single general agent |
| **Standards enforced, not suggested** | Quality gates and hooks enforce standards automatically; agents read standards files |
| **Memory persists** | `.claude/memory/` files accumulate project knowledge across sessions and agent handoffs |
| **Safety by default** | Hooks block destructive commands; agents cannot override safety constraints |
| **Live documentation** | All docs reflect the current state of the repository; stale docs are treated as bugs |

---

## 2. Repository Structure

```
eeik-bootstrap/
├── .github/                         ← GitHub Copilot configuration layer
│   ├── copilot-instructions.md      ← Master context (always-on, loaded for every request)
│   ├── agents/          (44 files)  ← .agent.md persona files
│   ├── instructions/    (29 files)  ← .instructions.md auto-applied by applyTo glob
│   ├── prompts/
│   │   ├── tasks/       (22 files)  ← Single-purpose task prompts
│   │   └── workflows/   (14 files)  ← Multi-step orchestration prompts
│   ├── skills/          (12 dirs)   ← SKILL.md capability packs
│   └── hooks/            (2 files)  ← Lifecycle hooks (JSON)
├── .claude/                         ← Claude Code configuration layer
│   ├── settings.json                ← Model, permissions, hook registration
│   ├── agents/          (44 files)  ← .md agent files (auto-selected)
│   ├── commands/        (10 files)  ← Slash command definitions
│   ├── hooks/            (4 files)  ← Shell scripts (pre-bash, pre-write, post-edit, on-stop)
│   ├── memory/          (10 files)  ← Persistent project context
│   └── standards/        (8 files)  ← Technology-specific coding standards
├── .vscode/                         ← VS Code settings and extension recommendations
├── .editorconfig                    ← Cross-editor formatting rules
├── intellij/                        ← IntelliJ Copilot setup and plugin guides
├── docs/                            ← Deep-dive specifications
├── AGENTS.md                        ← Complete agent catalogue
├── CLAUDE.md                        ← Claude Code session brief
├── README.md                        ← Primary adoption guide
└── TRACKER.md                       ← Completion tracker
```

---

## 3. Governance Model

### Activation Hierarchy

```
copilot-instructions.md   (always-on — loaded for every Copilot request)
    ↓
*.instructions.md         (path-specific — auto-applied when applyTo glob matches)
    ↓
*.agent.md / agents/*.md  (persona-specific — activated by user selection or agent description)
    ↓
SKILL.md                  (capability-specific — auto-loaded by Copilot when relevant)
    ↓
*.prompt.md               (task-specific — invoked explicitly via #file: or slash command)
```

### Authority and Responsibility

| Layer | Authority | Updated By |
|-------|-----------|-----------|
| Golden Rules (`CLAUDE.md`) | Non-negotiable; enforced by hooks | Tech Lead + team agreement |
| Standards (`.claude/standards/`) | Mandatory per domain | Tech Lead |
| Agent descriptions | Selection trigger — must be precise | Agent author |
| Memory (`.claude/memory/`) | Living project context | Team via `/memory-update` |
| TRACKER.md | Completion state | Automatically via commits |

---

## 4. Standards Framework

Standards are stored in `.claude/standards/` and referenced by agents before producing code. Each standards file covers a technology domain:

| File | Domain | Key Rules |
|------|--------|-----------|
| `java.md` | Spring Boot 3.x / Java 21 | Constructor injection, jakarta.*, SLF4J, no SELECT *, parameterised SQL |
| `angular.md` | Angular 17+ | Standalone components, OnPush, signals, strict TypeScript, inject() |
| `aws.md` | AWS / CDK / Terraform | IAM least privilege, encryption at rest/transit, tagging, naming conventions |
| `sql.md` | SQL / Flyway | No SELECT *, named parameters, Flyway versioning, no string-concatenated SQL |
| `testing.md` | JUnit 5 / Jasmine | AAA pattern, no Thread.sleep, 80% line / 70% branch thresholds |
| `cicd.md` | GitHub Actions | Pipeline stages, quality gates, OIDC auth, SHA-pinned actions |
| `containers.md` | Docker / Kubernetes | Multi-stage builds, non-root users, resource limits, health probes |
| `mainframe.md` | COBOL / RPG / CL / JCL | Level-88 conditions, EVALUATE over nested IF, no GO TO, SQL error handling |

Standards are enforced at three levels:
1. **Agents** — read standards files before generating code
2. **Hooks** — block writes that violate structural safety rules
3. **CI gates** — SonarQube, JaCoCo thresholds, OWASP Dependency Check

---

## 5. Memory Architecture

`.claude/memory/` files persist project knowledge across sessions. They are loaded at session start and provide context that would otherwise be re-explained every time.

### File Roles

| File | Type | Updated By |
|------|------|-----------|
| `project-context.md` | Living facts | Team manually or `/memory-update` |
| `domain-glossary.md` | Definitions | Business Analyst agent |
| `decisions.md` | Decision log | Architect, Tech Lead |
| `constraints.md` | Hard constraints | Tech Lead |
| `patterns.md` | Approved patterns | Tech Lead |
| `tech-debt.md` | Debt register | Team |
| `rca-tracker.md` | Incident log | `rca-agent`, `incident-handler` |
| `session-log.md` | Session history | `on-stop.sh` hook (automatic) |
| `rejected-approaches.md` | Anti-patterns tried | Team |

### Update Protocol
- Use `/memory-update "description"` to trigger structured updates
- All files committed with `chore(memory):` conventional commit messages
- Files kept under 500 lines each — large files slow session initialisation

---

## 6. Model Routing

### Claude Code
Defined in `.claude/settings.json`:
```json
{
  "model": "claude-sonnet-4-6"
}
```
Individual agents may specify a different model in their frontmatter (`model: claude-opus-4-8` for complex tasks).

### GitHub Copilot
Each `.agent.md` file specifies:
```yaml
model: claude-sonnet-4-5
```
Model selection follows the same principle: use the most capable model for complex architectural or governance tasks; use faster models for routine generation.

---

## 7. GitHub Copilot Integration

### Master Context Loading
`copilot-instructions.md` is auto-loaded for every Copilot request in the workspace. It contains:
- Project identity and bounded contexts
- Technology stack summary
- Dependency policy
- Agent catalogue reference
- Key conventions

### Path-Specific Context
`*.instructions.md` files use `applyTo` glob patterns to load automatically when the user opens a matching file. A developer working on `OrderService.java` automatically receives Spring Boot 3.x standards; a developer working on `Dockerfile` automatically receives container standards.

### Agent Selection
Agents in `.github/agents/` are available via the `@` selector in Copilot Chat. Each agent has a focused `description` that describes exactly when to use it. The Copilot orchestration layer uses this description for automatic selection.

### Skills
`.github/skills/*/SKILL.md` files are auto-loaded by Copilot when the conversation context matches the skill's trigger. Skills provide domain-specific instructions and reference material without requiring the user to select them explicitly.

---

## 8. Claude Code Integration

### Agent Auto-Selection
Claude Code reads the `description` field in each `.claude/agents/*.md` frontmatter and selects the most relevant agent for the task. Explicit invocation overrides auto-selection.

### Slash Commands
`.claude/commands/*.md` files define slash commands that appear as skills in the Claude Code UI. Each command activates a specialist workflow and produces structured output.

### Safety Hooks
Four hooks registered in `.claude/settings.json`:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre-bash-guard.sh` | PreToolUse:Bash | Blocks destructive commands |
| `pre-write-guard.sh` | PreToolUse:Write | Validates write targets |
| `post-edit-check.sh` | PostToolUse:Edit | Post-edit validation |
| `on-stop.sh` | Stop | Updates session-log.md |

---

## 9. MCP Integration

The `.claude/settings.json` supports MCP server configuration via the `mcpServers` section. MCP servers expose tools to Claude Code for:
- Database access
- External API calls
- File system operations beyond the workspace
- Custom business tool integrations

MCP server design follows the standards in `.github/instructions/mcp-protocol.instructions.md`. Use the `mcp-engineer` Claude Code agent to implement new MCP servers.

---

## 10. Security and Compliance

### Hook-Enforced Blocks (Claude Code)
The `pre-bash-guard.sh` hook blocks:
- `git push --force` / `git push -f`
- `git reset --hard`
- `rm -rf /` and variations
- `DROP DATABASE` / `DROP TABLE`
- `cdk destroy`
- AWS EC2/RDS/ECS termination and deletion commands

### Coding Standards Enforcement
- No hardcoded secrets (enforced by `devsecops-engineer` reviews and gitleaks in CI)
- No `SELECT *` (enforced by `code-reviewer` and SQL standards)
- No `@Autowired` on fields (enforced by Java standards and `java-tech-lead`)
- No `javax.*` in Spring Boot 3.x (enforced by hooks and CI compilation)

### Data Protection
- PII must not appear in logs (`java.md` standard, SLF4J parameterised logging)
- Credentials in Secrets Manager only — never in source (Golden Rule #2)
- Memory files must not contain credentials or environment-specific secrets

---

## 11. CI/CD Architecture

The EEIK bootstrap provides standards and pipeline templates but does not include running CI/CD pipelines (this is a seed, not an application). When adopting, the CI pipeline should implement:

```
build → unit-test → integration-test → security-scan → publish-artefact → deploy-dev → [approve] → deploy-staging → [approve] → deploy-prod
```

Quality gates that must fail the build:
- Unit test pass rate: 100%
- Line coverage: 80% (JaCoCo/Istanbul)
- Branch coverage: 70%
- OWASP Dependency Check: CVSS ≥ 7.0
- Container scan: CRITICAL severity
- Secrets scan: any finding
- SonarQube Quality Gate: not passed

See `.claude/standards/cicd.md` for full pipeline standards.

---

## 12. Knowledge Management

### Session Continuity
The `on-stop.sh` hook records the last commit and changed files at the end of every Claude Code session. The next session starts with this context, enabling continuity without manual re-briefing.

### Decision Recording
Two-tier decision logging:
- **Lightweight:** `.claude/memory/decisions.md` — quick team-level decisions
- **Formal:** `docs/decisions/ADR-NNN-*.md` — full ADRs via `/adr` command

### Tech Debt Visibility
`.claude/memory/tech-debt.md` maintains a prioritised register. The `java-tech-lead` and `code-reviewer` agents add entries when reviewing code. The register is visible to all agents and informs refactoring decisions.

---

## 13. Domain Packs

The bootstrap is divided into domain packs that can be adopted selectively:

| Pack | Files | Remove If |
|------|-------|----------|
| Modern Java | `spring-boot`, `java-quality`, `sql`, `test` instructions; `java-*`, `senior-developer` agents; java standards | No Java |
| Legacy Java | `java-legacy` instructions; `modernization-expert` agent | No legacy Java |
| Angular | `angular` instructions; `angular-*` agents; angular standards | No frontend |
| Mainframe | `mainframe*`, `ibmi` instructions; `modernization-expert`, `ibmi-modernization-expert` agents; mainframe standards | No mainframe |
| AWS / Cloud | `aws-*`, `cdk-terraform`, `deployment` instructions; `aws-*`, `cdk-*`, `containerisation-*`, `ci-engineer` agents; aws, cicd, containers standards | No AWS |
| Data / ML / AI | `aws-data-ml-ai`, `mlops-pipeline`, `ai-governance` instructions; `ai-engineer`, `ml-engineer`, `data-scientist`, `mlops-engineer`, `ai-governance-officer` agents | No ML/AI |
| Agentic AI | `langgraph`, `crewai`, `autogen`, `mcp-protocol`, `a2a-protocol` instructions; `langraph-engineer`, `crewai-engineer`, `autogen-engineer`, `mcp-engineer`, `a2a-engineer` agents | No agentic AI |
| Operations | `incident-ops`, `sre` instructions; `incident-handler`, `rca-agent`, `ops-engineer`, `sre-engineer` agents | No operational responsibility |
