# /adr — Scaffold an Architecture Decision Record

Scaffold a new Architecture Decision Record in `docs/decisions/`.

## Usage

```
/adr "Use Kafka for cross-context event streaming"
```

## What This Command Does

1. Reads existing ADRs in `docs/decisions/` to determine the next sequence number
2. Creates a new file `docs/decisions/ADR-{NNN}-{slugified-title}.md`
3. Populates the ADR template with the title and today's date
4. Presents the draft for you to complete

## Output Template

```markdown
# ADR-{NNN}: {Title}

## Status
Proposed

## Date
{YYYY-MM-DD}

## Context
<!-- What is the problem being solved? What forces are in tension? What constraints apply? -->

## Decision
<!-- What was decided? State it clearly and unambiguously. -->

## Consequences

### Positive
- <!-- What gets better as a result of this decision? -->

### Negative / Trade-offs
- <!-- What gets harder, more complex, or more expensive? -->

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|-----------------|
| <!-- option --> | <!-- pros --> | <!-- cons --> | <!-- reason --> |

## References
- <!-- Link to relevant design docs, RFCs, or prior ADRs -->
```

## Notes

- For decisions that need full ARB review, use the `arb-reviewer` agent after drafting the ADR
- Update `docs/decisions/` index when adding a new ADR
- Change status from `Proposed` to `Accepted` once the decision is confirmed by the Tech Lead or ARB
- Use `Superseded by ADR-{NNN}` if a later decision overrides this one
