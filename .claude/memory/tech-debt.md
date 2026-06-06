# Tech Debt Register

> Track technical debt with priority and target sprint. Review this register at the start of each sprint to ensure debt is being addressed systematically, not accumulated silently.

---

## Debt Format

```
### TD-NNN: {Short Title}
**Priority:** P1 (critical) / P2 (high) / P3 (medium) / P4 (low)
**Category:** Security / Performance / Maintainability / Reliability / Compliance
**Target Sprint:** Sprint {N} or Quarter {Q}
**Estimated Effort:** {raw hours}
**Description:** {What the debt is and why it exists}
**Risk if Unaddressed:** {What could go wrong if this is not fixed}
**Resolution:** {What done looks like}
```

---

## Priority Guide

| Priority | Definition | SLA |
|----------|-----------|-----|
| P1 | Security vulnerability, compliance risk, or production reliability impact | Must be in current sprint |
| P2 | Significant performance, maintainability, or risk impact | Must be in next sprint |
| P3 | Moderate impact; trade-off with feature work acceptable | Within quarter |
| P4 | Low impact; address when adjacent work occurs | Backlog |

---

## Active Debt Items

<!-- TODO: Add your project's actual tech debt below. Example entries: -->

### TD-001: [Example] Migrate remaining javax.* imports in legacy modules
**Priority:** P1
**Category:** Compliance (Spring Boot 3.x requirement)
**Target Sprint:** <!-- TODO -->
**Estimated Effort:** 4h
**Description:** Three legacy service classes still import `javax.persistence.*` and `javax.validation.*` from the pre-migration codebase.
**Risk if Unaddressed:** Compilation will fail when the javax compatibility shim is removed in the next dependency upgrade.
**Resolution:** All `javax.*` replaced with `jakarta.*`; tests pass; SonarQube confirms zero javax imports.

---

### TD-002: [Example] Replace System.out.println in batch job classes
**Priority:** P2
**Category:** Maintainability / Observability
**Target Sprint:** <!-- TODO -->
**Estimated Effort:** 2h
**Description:** Legacy batch processing classes use `System.out.println` for progress logging; output is not captured in CloudWatch.
**Risk if Unaddressed:** Batch job failures are invisible to monitoring and alerting.
**Resolution:** All `System.out` replaced with SLF4J `log.info/warn/error`; output visible in CloudWatch Logs.

---

## Resolved Debt

<!-- Move items here when resolved, with resolution date -->

| Ref | Title | Resolved | Sprint |
|-----|-------|----------|--------|
| <!-- TD-NNN --> | <!-- title --> | <!-- date --> | <!-- sprint --> |
