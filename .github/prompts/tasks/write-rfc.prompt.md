# Write Request for Comments (RFC)

Produce a technical RFC document for the following proposal:

**Proposal:** $RFC_TITLE

## Instructions

1. Create `docs/rfcs/RFC-{NNN}-{slugified-title}.md`
2. Populate the template below with the technical proposal
3. RFC status begins as `Draft` — it moves to `Accepted` after the review period

## RFC Template

```markdown
# RFC-{NNN}: {Title}

**Status:** Draft
**Author:** {author}
**Date:** {YYYY-MM-DD}
**Review Period:** {YYYY-MM-DD} to {YYYY-MM-DD} (2 weeks default)

## Summary
<!-- One paragraph: what are you proposing and why? -->

## Motivation
<!-- Why is this change needed? What problem does it solve? What is the current situation? -->

## Proposed Design

### Overview
<!-- High-level description of the proposed solution -->

### Detailed Design
<!-- Specific technical implementation details, APIs, schemas, interactions -->

### Alternatives Considered
| Alternative | Reason Not Chosen |
|-------------|------------------|

## Impact Analysis

### Breaking Changes
<!-- Will this break existing interfaces, APIs, or data schemas? -->

### Migration Path
<!-- How do adopters migrate from the current state to the new state? -->

### Performance Implications
<!-- What is the expected impact on throughput, latency, and resource utilisation? -->

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

## Open Questions
<!-- Questions that must be resolved before this RFC can be accepted -->

## References
<!-- Prior art, related RFCs, academic papers, external documentation -->
```

## Checklist

- [ ] Summary can be understood without reading the full RFC
- [ ] All breaking changes are explicitly listed
- [ ] Migration path is actionable (not just "update your code")
- [ ] At least one alternative considered and rejected
- [ ] Open questions listed for community resolution
