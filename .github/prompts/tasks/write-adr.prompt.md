# Write Architecture Decision Record

Scaffold a new Architecture Decision Record for the following decision:

**Decision:** $DECISION_TITLE

## Instructions

1. Read any existing ADRs in `docs/decisions/` to determine the next sequence number
2. Create `docs/decisions/ADR-{NNN}-{slugified-title}.md`
3. Populate the template below with the context from the discussion
4. Set status to `Proposed` until the decision is confirmed by Tech Lead or ARB

## ADR Template

```markdown
# ADR-{NNN}: {Title}

## Status
Proposed

## Date
{YYYY-MM-DD}

## Context
<!-- What is the problem? What forces are in tension? What constraints apply? -->

## Decision
<!-- What was decided? Be specific and unambiguous. -->

## Consequences

### Positive
- <!-- What improves as a result? -->

### Negative / Trade-offs
- <!-- What becomes harder or more complex? -->

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|-----------------|

## References
- <!-- Related ADRs, RFCs, design documents -->
```

## Checklist

- [ ] Context explains the problem without assuming the reader already knows the background
- [ ] Decision is stated clearly and can be understood without reading the context
- [ ] At least two alternatives considered and rejected with rationale
- [ ] Consequences are honest about both positives and trade-offs
