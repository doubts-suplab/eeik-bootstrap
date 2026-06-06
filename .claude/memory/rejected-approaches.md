# Rejected Approaches

> Records approaches that were tried and rejected, with the reason. This prevents the team (and Claude Code agents) from re-proposing solutions that have already been evaluated and discarded.

---

## Format

```
### RA-NNN: {Short Title of Rejected Approach}
**Date Rejected:** YYYY-MM-DD
**Proposed For:** {What problem this was proposed to solve}
**Approach:** {What was proposed or tried}
**Why Rejected:** {The specific reason — evidence, test result, constraint violated}
**Approved Alternative:** {What was used instead}
```

---

## Rejected Approaches

<!-- TODO: Add entries as the team tries and rejects approaches. Example: -->

### RA-001: [Example] Field injection with @Autowired
**Date Rejected:** <!-- TODO -->
**Proposed For:** All Spring bean wiring
**Approach:** Using `@Autowired` on private fields for dependency injection
**Why Rejected:** Breaks unit testability (cannot inject mocks without Spring context); violates immutability (fields cannot be `final`); hides dependencies (not visible in constructor signature). Violates Golden Rule #1.
**Approved Alternative:** Constructor injection with `final` fields.

---

### RA-002: [Example] Shared database schema between bounded contexts
**Date Rejected:** <!-- TODO -->
**Proposed For:** Cross-context data access between Order and Inventory services
**Approach:** Both services reading from the same PostgreSQL schema/tables
**Why Rejected:** Creates tight coupling at the data layer; schema changes in one context break the other; prevents independent scaling and deployment. Violates DDD bounded context principles (Golden Rule #5).
**Approved Alternative:** Inventory exposes a REST API; Order service calls the API; eventual consistency via domain events for read-model updates.

---

<!-- Add real rejected approaches as they occur during the project -->
