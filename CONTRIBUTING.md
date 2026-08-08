# Contributing to EEIK Bootstrap

Thank you for contributing. EEIK is a community-maintained framework — every improvement benefits every project that adopts it.

---

## Guiding Principles

Contributions must:
- **Increase reuse** — solve a problem once; apply everywhere
- **Reduce duplication** — check whether an existing agent, command, or standard covers the need first
- **Improve consistency** — follow existing patterns exactly; do not invent new structure
- **Include working examples** — every agent, standard, and command must have a realistic usage example

---

## What You Can Contribute

| Type | Location | Description |
|---|---|---|
| **Capability Pack** | `capability-packs/<name>/` | Bundles agents, standards, commands, and knowledge for a domain |
| **Agent** | `.claude/agents/` + `.github/agents/` | A specialist role definition for Claude Code and GitHub Copilot |
| **Slash Command** | `.claude/commands/` | A reusable workflow invoked with `/command-name` |
| **Standard** | `.claude/standards/` + `.github/instructions/` | A mandatory coding or process standard |
| **GitHub Prompt** | `.github/prompts/tasks/` or `.github/prompts/workflows/` | A reusable Copilot prompt template |
| **GitHub Workflow** | `.github/workflows/` | A CI/CD pipeline for the framework or projects using it |
| **Hook** | `.claude/hooks/` | A guard script that enforces rules automatically |
| **ADR** | `docs/decisions/` | An architectural decision for the framework itself |
| **Runbook** | `docs/runbooks/` | An operational runbook template |

### Domain-pack contribution criteria

Domain packs (banking, insurance, healthcare, retail, …) are high-value but risk becoming sparse or
organisation-specific. To keep them reusable, a domain pack must:

- **Be generic and extensible, not org-specific.** Encode the *domain's* invariants and regulatory
  concerns (e.g. "never store PAN/CVV", "reserve stock before charging"), not one company's product,
  service names, or internal systems. No proprietary rules, endpoints, or account IDs.
- **Carry substantive content, not stubs.** At least one real agent *and* one standard, each passing
  `eeik lint` (valid frontmatter, a usable description, real body) and `eeik verify` (everything the
  `metadata.yaml` declares resolves to a file). A one-paragraph placeholder is not a pack.
- **Keep regulated examples generic.** Reference the framework by name (GDPR, PCI-DSS, HIPAA, Solvency
  II, Basel III) and the *control*, not a specific auditor's checklist or a jurisdiction-specific form.
- **Declare compliance hints + a version** in `metadata.yaml`, and resolve from a manifest field
  (`project.domain: <name>`) — wire it into `eeik/packs.py` and the canonical capability matrix.
- **Prefer patterns over prescriptions.** Where a concern generalises (an order state machine, a
  reservation model), promote it to `knowledge/patterns/` so other domains can reuse it.

If a rule only applies inside one organisation, it belongs in that org's *downstream* project (via
`eeik seed` + a project-local pack), not in the shared seed.

---

## Branch and Commit Conventions

### Branching

```
main          — stable, always releasable
develop       — integration branch for next release
feature/<slug>     — new capability or agent
fix/<slug>         — bug fix in existing content
docs/<slug>        — documentation-only change
chore/<slug>       — tooling, CI, housekeeping
```

Always branch from `develop`. Never commit directly to `main`.

### Commit Messages (Conventional Commits)

```
<type>(<scope>): <description>

feat(agents): add python-developer agent with FastAPI and pytest support
fix(hooks): correct bare-except detection regex in post-edit-check.sh
docs(standards): expand api-standard with auth and rate limiting sections
chore(workflows): add quality-gate workflow for Java and Angular
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`

**Scope examples:** `agents`, `commands`, `standards`, `hooks`, `workflows`, `memory`, `capability-packs`, `docs`

---

## File Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Agent | `<role-slug>.md` | `python-developer.md` |
| GitHub Copilot agent | `<role-slug>.agent.md` | `python-developer.agent.md` |
| Standard | `<technology-slug>.md` | `fastapi.md` |
| GitHub instruction | `<domain>.instructions.md` | `fastapi.instructions.md` |
| Command | `<verb-noun>.md` | `migrate-db.md` |
| GitHub prompt (task) | `<action-subject>.prompt.md` | `generate-fastapi-router.prompt.md` |
| Capability pack | `<domain>/` directory | `python/`, `data-engineering/` |
| ADR | `ADR-<NNN>-<slug>.md` | `ADR-003-kafka-over-sqs.md` |

---

## Agent Template

Every new agent must follow this structure. Copy from an existing agent (e.g., `java-developer.md`) and customise.

```markdown
---
name: <slug>
description: >
  Use for <specific trigger condition>. Trigger when <precise activation scenario>.
model: claude-sonnet-4-6
tools: [Read, Write, Edit, MultiEdit, Bash, Glob, Grep]
---

## Role
[One paragraph: who you are, what you do, what you read before writing code]

## Capabilities
[Bulleted list of concrete things this agent can do]

## Implementation Rules
[Non-negotiable rules specific to this agent's domain]

## Constraints
[What this agent must never do]

## Output Format
[Numbered steps describing what the agent produces]

## Persona Tone
[One sentence describing the agent's communication style]
```

**Checklist before submitting an agent:**
- [ ] Description is a precise activation trigger, not a generic description
- [ ] References the correct `.claude/standards/` file in the Role section
- [ ] Has at least 5 Capabilities (concrete, not vague)
- [ ] Has at least 3 Constraints (things it must not do)
- [ ] Has a matching `.agent.md` in `.github/agents/`
- [ ] Has a matching `.instructions.md` in `.github/instructions/` if a new domain

---

## Standard Template

Every new standard must follow this structure. Copy from `java.md` and customise.

```markdown
# <Technology> <Type> Standard

> One-sentence summary. Enforced by <agent(s)> and <CI gate>.

## Section 1 — Rule Set
[Rules with code examples showing CORRECT and WRONG patterns]

## Anti-Patterns
| Anti-Pattern | Correct Alternative |
|---|---|

## Enforcement
[How the standard is enforced: hooks, CI gates, agent reviews]
```

**Checklist before submitting a standard:**
- [ ] At least 5 rules with CORRECT/WRONG code examples
- [ ] Anti-patterns table with concrete alternatives
- [ ] Enforcement section listing how violations are caught
- [ ] Referenced in the relevant agent's Role section

---

## Command Template

Every new command must follow this structure. Copy from `estimate.md` and customise.

```markdown
# /command-name — Short Description

One sentence describing what this command does.

## Usage
[Code block showing typical invocation]

## What This Command Does
[Numbered steps]

## Output Format
[Description or example of the produced output]

## Tips
[3–5 practical tips for effective use]
```

---

## Pull Request Requirements

Your PR must include:

### Title
```
feat(agents): add kubernetes-engineer agent
```

### Description Template
```markdown
## What
[What is being added or changed]

## Why
[Business value — what use case does this enable or improve]

## Checklist
- [ ] Agent has matching .agent.md in .github/agents/
- [ ] Standard has code examples (CORRECT/WRONG)
- [ ] Command has usage example and output format
- [ ] File naming follows conventions (see CONTRIBUTING.md)
- [ ] No hardcoded credentials, secrets, or project-specific values
- [ ] Tested: invoked in a test project and confirmed it activates correctly
```

---

## Review Process

All PRs require:
- **Maintainer review** — checks structure, naming, and framework consistency
- **Domain owner review** (if modifying an existing domain) — checks technical accuracy

Review criteria:
- Does the agent/standard/command add value not already covered?
- Does it follow the naming and structure conventions exactly?
- Are code examples realistic and correct?
- Is there any project-specific content that should be made generic?

---

## Quality Gate

Your PR must pass:
1. The `eeik-validate.yml` workflow — validates manifest structure and naming conventions
2. Manual review of at least one example invocation (include a screenshot or transcript in the PR)

---

## Capability Pack Structure

New capability packs must follow this layout:

```
capability-packs/<name>/
  metadata.yaml           # Pack identity, version, tags, dependencies
  README.md               # Pack description and adoption guide
  agents/                 # Pack-specific agents (installed to .claude/agents/)
  standards/              # Pack-specific standards (installed to .claude/standards/)
  commands/               # Pack-specific commands (installed to .claude/commands/)
  knowledge/              # Reference docs, pattern libraries, domain glossaries
  templates/              # Code templates, scaffold files
  workflows/              # GitHub Actions workflows specific to this pack
```

`metadata.yaml` must include:
```yaml
name: python
version: 1.0.0
description: Python backend engineering with FastAPI and pytest
tags: [python, fastapi, pydantic, pytest, backend]
dependencies: [core]
agents: [python-developer]
standards: [python, fastapi]
commands: []
```

---

## What Not to Contribute

- Project-specific agents with hardcoded service names, URLs, or account IDs
- Standards for technologies with no existing adopter use case
- Agents that duplicate an existing agent's scope without clear differentiation
- Commands that are a thin wrapper around a single existing command
