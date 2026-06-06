# Architecture Decision Log

> Decisions recorded here are in addition to formal ADRs in `docs/decisions/`.
> Use this file for lightweight, team-level decisions that don't warrant a full ADR.
> For significant decisions, create a proper ADR: `/adr "decision title"`

---

## Decision Format

```
### D-NNN: {Decision Title}
**Date:** YYYY-MM-DD
**Status:** Accepted / Superseded by D-XXX / Reverted
**Context:** Why this decision was needed
**Decision:** What was decided
**Consequences:** What changed as a result; what is now harder or easier
```

---

## Decisions

<!-- TODO: Log your team's architecture decisions below. Example: -->

### D-001: Use Spring Data JPA for persistence layer
**Date:** <!-- TODO -->
**Status:** Accepted
**Context:** Team needed to choose between JdbcTemplate, Spring Data JDBC, and Spring Data JPA for the primary persistence layer.
**Decision:** Spring Data JPA with Hibernate for entity relationships; Spring Data JDBC for performance-critical read paths.
**Consequences:** Easier CRUD implementation; lazy-loading N+1 risk requires explicit `@EntityGraph` usage on collection fetches.

<!-- Add real decisions below: -->

