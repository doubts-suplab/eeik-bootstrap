# Core Capability Pack

## Purpose

The foundational capability pack. Provides cross-cutting agents, standards, commands, and workflows that **every EEIK project receives**, regardless of technology stack, domain, or governance profile.

All other capability packs depend on this one.

## What's Included

| Category | Count | Description |
|----------|-------|-------------|
| Agents | 14 | Cross-cutting specialists: architect, reviewer, security, delivery, ops |
| Standards | 5 | Golden rules, security baseline, observability, commits, estimation |
| Commands | 8 | Always-available commands: /review, /estimate, /security-scan, etc. |
| Workflows | 4 | Core workflows: PR review, security scan, deploy check, incident |
| Knowledge | 3 | Platform-wide patterns, anti-patterns, estimation reference |

## Agents

| Agent | Role |
|-------|------|
| `architect` | System design, ADRs, NFRs, bounded context review |
| `enterprise-architect` | Cross-domain strategy, capability maps, transformation roadmaps |
| `arb-reviewer` | Formal ARB gate reviews for enterprise governance |
| `code-reviewer` | PR review with BLOCKER/MAJOR/MINOR/NIT severity labels |
| `security-auditor` | OWASP Top 10, secrets scan, IAM review, threat modelling |
| `business-analyst` | Requirements elicitation, user stories, acceptance criteria |
| `estimator` | P50/P80/P90 effort estimates using EEIK formula |
| `technical-writer` | API docs, runbooks, ADRs, architecture documents |
| `project-tracker` | Sprint tracking, velocity, risk, delivery reporting |
| `incident-handler` | P1/P2 incident coordination, communication, mitigation |
| `rca-agent` | 5-Whys root cause analysis, post-mortem facilitation |
| `ops-engineer` | Operational health, runbook creation, toil reduction |
| `sre-engineer` | SLO definition, error budget, reliability engineering |
| `devsecops-engineer` | CI/CD security gates, pipeline hardening, supply chain |

## Dependencies

None — this is the foundational pack.

## Activation

Core pack is always active. No manifest condition required.
All agents in this pack are available to every project after `/generate-repo`.
