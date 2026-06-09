# Getting Started

Everything you need to adopt EEIK on a new or existing project.

---

## Contents

| Document | Purpose |
|----------|---------|
| [quick-start.md](quick-start.md) | End-to-end walkthrough: bootstrap → manifest → repository generation |

---

## Minimum Steps to Get Running

1. **Clone EEIK** into your project or as a standalone repository
2. **Copy the configuration layers** (`.claude/`, `.github/`, `.vscode/`, `.editorconfig`) into your project root
3. **Run `/bootstrap`** in Claude Code to generate your `project-manifest.yaml`
4. **Customise** `CLAUDE.md` and `.claude/memory/project-context.md` with your project specifics
5. **Run `/generate-repo`** to scaffold the full project structure

The [quick-start guide](quick-start.md) walks through each step with a worked example.

---

## Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| Claude Code | Yes | Runs all slash commands and agents |
| Git | Yes | Repository required |
| GitHub Copilot | Recommended | Activates `.github/` layer |
| AWS account | Optional | Required if `cloud.provider: aws` |
| Java 21+ | Optional | Required if `backend.language: java21` |

---

## What Gets Generated

After running `/bootstrap` and `/generate-repo`, your project will have:

```
.claude/              ← Claude Code agents, commands, memory, hooks, standards
.github/              ← Copilot agents, instructions, prompts, skills, hooks
src/                  ← Skeleton source code per technology stack
docs/                 ← Architecture, ADRs, review checklists
infrastructure/       ← CDK stacks or Terraform modules (if AWS)
.github/workflows/    ← CI/CD pipeline with governance gates
```

---

## Next Steps After Quick Start

- Read [docs/concepts/](../concepts/README.md) to understand the EEIK design model
- Read [docs/architecture/](../architecture/README.md) for internal platform architecture
- Explore [docs/examples/](../examples/README.md) for domain-specific worked examples
