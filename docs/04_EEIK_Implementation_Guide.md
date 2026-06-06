# EEIK Implementation Guide

> **Version:** 1.0 — 2026-06-06
> Concrete file templates, adoption patterns, and implementation conventions.

---

## 1. CLAUDE.md Pattern

The `CLAUDE.md` at the repository root is the Claude Code session brief. When adopting EEIK, customise these sections:

### What to Customise

```markdown
## What This Repository Is
<!-- Replace with your actual project description -->

## Key agents by domain
<!-- Remove rows for domains not used in your project -->
<!-- Add project-specific agents if you create custom ones -->

## Supported Technology Stack
<!-- Remove sections for technologies not in use -->
<!-- Update version numbers to match your actual dependencies -->
```

### What NOT to Change
- Golden Rules — non-negotiable; enforced by hooks
- Before Writing Code checklist — keep as-is
- Estimation formula — standard across all EEIK projects
- Memory and Context section — keep to establish loading behaviour
- What NOT To Do list — keep as enforcement guidance

---

## 2. Agent File Template

All `.claude/agents/` files use this structure:

```markdown
---
name: agent-slug
description: >
  [Precise trigger condition. Start with "Use for" or "Use when". Be specific enough
  that Claude Code can select this agent without ambiguity. Include the key technical
  terms that match the user's task. 2-4 sentences maximum.]
model: claude-sonnet-4-6
tools: [Read, Write, Edit, Glob, Grep]
---

## Role

[One paragraph: who you are, what your primary mission is, what you read before starting.]

---

## Capabilities

[Bulleted sections by capability group. Be specific about what you can produce.]

---

## Constraints

[List of things you will NOT do. These prevent scope creep and enforce quality.]

---

## Output Format

[How your output is structured. Include templates if the output is highly structured.]

---

## Persona Tone

[One or two sentences describing how the agent communicates.]
```

### GitHub Copilot Agent Template (`.github/agents/`)

```markdown
---
name: 'Agent Display Name'
description: 'Single-sentence trigger. Be precise.'
model: claude-sonnet-4-5
tools: ['read', 'edit', 'search', 'execute', 'runCommands']
target: vscode
---

## Role
[Same as Claude Code agent — agents are mirrors of each other across layers]

## Capabilities
...

## Persona Tone
...
```

---

## 3. Command Template

All `.claude/commands/` files follow this structure:

```markdown
# /command-name — Short Title

One-sentence description of what this command does.

## Usage

```
/command-name "argument if required"
```

## What This Command Does

1. Step one (which agent activates, if any)
2. Step two (what it reads)
3. Step three (what it produces)
4. Step four (what it updates)

## Output Format

Description or template of the output produced.

## Notes

- Any important caveats, prerequisites, or related commands
```

---

## 4. Hook Template

### Shell Hook (`.claude/hooks/`)

```bash
#!/bin/bash
# Hook: pre-bash-guard.sh
# Trigger: PreToolUse:Bash
# Purpose: Block destructive commands

COMMAND="${BASH_TOOL_COMMAND:-}"

# Pattern: exact match or substring
if echo "$COMMAND" | grep -qE 'pattern-to-block'; then
    echo "Blocked: reason for blocking" >&2
    exit 1
fi

exit 0
```

Register in `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/pre-bash-guard.sh"
          }
        ]
      }
    ]
  }
}
```

### Copilot Hook (`.github/hooks/`)

```json
{
  "hooks": [
    {
      "event": "sessionStart",
      "command": "echo \"Session started: $(date)\" >> .copilot-session.log"
    }
  ]
}
```

---

## 5. MCP Server Configuration

To add an MCP server to Claude Code, add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

For HTTP-based MCP servers (SSE transport):
```json
{
  "mcpServers": {
    "server-name": {
      "type": "sse",
      "url": "http://localhost:3000/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_API_KEY}"
      }
    }
  }
}
```

Use the `mcp-engineer` agent to design and implement MCP servers. See `.github/instructions/mcp-protocol.instructions.md` for standards.

---

## 6. GitHub Workflow Examples

### Standard Java CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, 'feature/**']
  pull_request:
    branches: [main]

permissions:
  contents: read
  id-token: write  # OIDC for AWS

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven
      - run: ./mvnw verify -B -Pci

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - run: ./mvnw org.owasp:dependency-check-maven:check -B
      - uses: aquasecurity/trivy-action@v0.18.0
        with:
          scan-type: 'fs'
          exit-code: '1'
          severity: 'CRITICAL'
```

### Angular CI Pipeline

```yaml
# .github/workflows/angular-ci.yml
name: Angular CI

on:
  push:
    branches: [main, 'feature/**']

jobs:
  build-test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
      - run: npm ci
      - run: npm run build -- --configuration production
      - run: npm run test -- --watch=false --code-coverage
      - run: npm audit --audit-level=high
```

---

## 7. Standards File Example

Each `.claude/standards/*.md` file follows this pattern:

```markdown
# {Technology} Standards

> Mandatory standards for all {technology} code. Enforced by {agent names} and {CI tool}.

---

## Core Rules (Non-Negotiable)

- **Rule 1** — rationale and example
- **Rule 2** — rationale and example

---

## Patterns

### Pattern Name
```code example showing the approved pattern```
**Why:** Rationale for this pattern.

---

## Anti-Patterns — Do Not Use

| Anti-Pattern | Why Forbidden | Approved Alternative |
|--------------|--------------|---------------------|

---

## Testing Standards

- Framework versions
- Coverage thresholds
- Specific forbidden patterns (Thread.sleep, etc.)
```

---

## 8. ADR Template

Architecture Decision Records live in `docs/decisions/`. Use `/adr "title"` to scaffold:

```markdown
# ADR-{NNN}: {Title}

## Status
Proposed / Accepted / Superseded by ADR-{NNN} / Reverted

## Date
{YYYY-MM-DD}

## Context
<!-- Problem being solved. Forces in tension. Constraints. -->

## Decision
<!-- What was decided. State clearly and unambiguously. -->

## Consequences

### Positive
- <!-- What improves -->

### Negative / Trade-offs
- <!-- What becomes harder -->

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|-----------------|

## References
- <!-- Related ADRs, RFCs, design docs -->
```

---

## 9. RCA Template

Use `/rca "incident description"` to create. Full template in `.claude/agents/rca-agent.md`. Key sections:

```markdown
# RCA: INCIDENT-{NNN} — {Short Title}

**Date / Duration / Severity / Services / Customer Impact**

## Executive Summary
<!-- 3-5 sentences: what happened, root cause, key actions -->

## Timeline
| Time (UTC) | Event | Source |

## 5-Whys Analysis
Symptom → Why 1 → Why 2 → Why 3 → Why 4 → **Root Cause**

## Contributing Factors
## What Went Well
## Corrective Actions
| Ref | Action | Type | Owner | Target Date | Status |
```

---

## 10. Estimation Templates

Use `/estimate "description"` to produce. Full output format in `.claude/agents/estimator.md`:

```markdown
## Estimate: {Feature Name}

### Assumptions
- {assumptions that could invalidate this estimate}

### Task Breakdown
| Task | Complexity | Raw Hours | Notes |
| **Total** | | **{Σ}h** | |

### Summary
| P50 | {Σ}h | {÷6.4}d |
| P80 | {×1.3}h | {÷6.4}d |
| P90 | {×1.6}h | {÷6.4}d |

### Risks
### Recommended Spike (if applicable)
```

---

## 11. Modernisation Playbooks

### COBOL → Java Playbook

1. **Analyse** (`ibmi-modernization-expert` or `modernization-expert` agent)
   - Read program source, extract business rules
   - Map copybooks to Java data structures
   - Identify external calls and file I/O patterns

2. **Design** (`architect` agent)
   - Map COBOL paragraphs to Java service methods
   - Design JPA entities from DB2 table DDL
   - Design API facade for COBOL callers during transition

3. **Implement** (`java-developer` agent)
   - Implement Java service preserving all business rules exactly
   - Preserve `BigDecimal` precision for all packed/zoned decimal fields
   - Implement unit tests covering every business rule from the COBOL

4. **Test** (`java-tester` agent)
   - Compare Java output against COBOL output for representative inputs
   - Test boundary conditions and error paths

5. **Coexist** — run Java and COBOL in parallel; route new traffic to Java
6. **Cutover** — redirect all traffic; retain COBOL read-only for 30 days
7. **Decommission** — remove COBOL program after validation period

### Spring 4/5 → Spring Boot 3.x Playbook

1. Replace all `javax.*` imports with `jakarta.*`
2. Migrate `WebSecurityConfigurerAdapter` → component-based security config
3. Migrate `WebMvcConfigurerAdapter` → implement `WebMvcConfigurer` directly
4. Migrate `@Configuration` XML imports to Java config
5. Upgrade JUnit 4 → JUnit 5 (`@RunWith` → `@ExtendWith`, `@Before` → `@BeforeEach`)
6. Update Maven POM: Spring Boot parent to 3.x, remove compatibility shims
7. Run full test suite; fix any `jakarta.*` / `javax.*` compilation failures

---

## 12. Memory File Initialisation

When adopting EEIK in a new project, complete these files in order:

### Priority 1 — Fill Immediately
1. `.claude/memory/project-context.md` — service inventory and environments
2. `.claude/memory/constraints.md` — hard constraints specific to your project
3. `.claude/memory/domain-glossary.md` — key business terms

### Priority 2 — Fill During First Sprint
4. `.claude/memory/patterns.md` — add approved patterns as they emerge
5. `.claude/memory/decisions.md` — log any initial architectural decisions

### Priority 3 — Accumulate Over Time
6. `.claude/memory/tech-debt.md` — add as debt is identified in code reviews
7. `.claude/memory/rejected-approaches.md` — add when approaches are tried and fail
8. `.claude/memory/rca-tracker.md` — add after first production incident
9. `.claude/memory/session-log.md` — auto-maintained by `on-stop.sh` hook

### Template Fill Instructions
Each file contains `<!-- TODO: fill in -->` markers. Replace with project-specific content. Remove the `<!-- Bootstrap Note -->` section from `MEMORY.md` once files are populated.
