# Lessons Learned Repository

Captured learnings from EEIK-managed projects.

**Purpose:** Prevent teams from repeating the same mistakes. Every lesson here saved real project time.

## How to Contribute

**Manually** — after a sprint retrospective or project milestone, run:

```
/capture-lesson "brief description of learning"
```

The agent will guide you through the full lesson format.

**Closed-loop (from the runtime)** — draft lessons automatically from HALO/APEX audit logs, where every
`BLOCK`/`ALERT` and low-confidence human-review decision already carries a rationale (ADR-012):

```bash
eeik lessons --from audit.json     # → staged LL-NNN drafts under .eeik-staging/lessons/
eeik lessons --list                # the curated lessons already promoted here
```

Capture is **SUGGEST authority**: drafts are *staged*, never auto-committed. Same guarantee whether you
use the CLI, `eeik.capture_lessons()` (SDK), or `eeik_capture_lessons` (MCP).

## Promotion workflow — staged → committed

A staged draft (under `.eeik-staging/lessons/`) is a *proposal*. Promoting it into this directory is a
deliberate, human-curated step:

1. **Review** the draft in `.eeik-staging/lessons/LL-NNN-*.md`. Confirm it describes a real, reusable
   lesson (not a one-off), and that its category/severity are right.
2. **Curate the stubs** the machine leaves for a human: fill in **Root Cause** and **Fix / Prevention**
   with specifics (the runtime knows *what* happened, not *why* or *how to prevent it*).
3. **De-duplicate** — if it overlaps an existing `LL-NNN`, fold the new signal (occurrence count, a fresh
   example) into that lesson instead of adding a near-duplicate.
4. **Number** it: take the next free `LL-NNN` (the draft is pre-numbered, but re-check after de-dup).
5. **Move** the file into `knowledge/lessons-learned/` and **add a row** to the index below.
6. **Consider promotion to a pattern** — if the fix is a reusable *approach* (not just a fix for one
   bug), promote it to `knowledge/patterns/` and link it from the lesson.
7. **Commit** with a `docs(lessons):` message. `eeik lessons --list` should now show it.

Promotion is intentionally manual — the closed loop *proposes*; a human *decides* what enters the
organisation's memory.

## Index

| ID | Lesson | Category | Severity | Project Phase |
|----|--------|----------|----------|---------------|
| [LL-001](LL-001-flyway-baseline-on-existing-db.md) | Flyway baseline migration on existing database | Database | HIGH | Foundation |
| [LL-002](LL-002-testcontainers-startup-time.md) | Testcontainers startup slows CI pipeline | Testing | MEDIUM | Ongoing |
| [LL-003](LL-003-langgraph-recursion-limit.md) | LangGraph infinite loop without recursion_limit | AI/Agents | CRITICAL | AI Integration |
| [LL-004](LL-004-cdk-cross-account-permissions.md) | CDK cross-account deployment permission errors | AWS | HIGH | Infrastructure |

## Categories

`Database` | `Testing` | `AI/Agents` | `AWS` | `Security` | `Architecture` | `CI/CD` | `Governance`
