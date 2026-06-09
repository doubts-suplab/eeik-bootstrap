# AGENTS.md — Java Source Root

> **Deploy to**: `src/main/java/AGENTS.md` in your project
> Codex CLI reads this automatically when working in Java source files.

---

You are working in the **Java application source**. This is a Spring Boot 3.x project.

## Architecture

This codebase follows **Hexagonal Architecture** with DDD:

```
com.{company}.{service}/
├── domain/           ← Pure business logic. Zero framework dependencies.
│   ├── model/        ← Entities, value objects, aggregates
│   ├── port/         ← Interfaces (inbound/outbound ports)
│   └── event/        ← Domain events
├── application/      ← Use cases. Orchestrates domain. No HTTP/DB here.
│   ├── command/      ← Write operations
│   └── query/        ← Read operations
├── infrastructure/   ← Adapters: JPA repos, messaging, HTTP clients
└── web/              ← REST controllers, request/response DTOs
```

**Dependencies only flow inward.** `infrastructure` depends on `application` depends on `domain`. `domain` depends on nothing.

## Non-Negotiable Rules

1. **Constructor injection only** — `final` fields, no `@Autowired` on fields
2. **`jakarta.*` exclusively** — never `javax.*` in this Spring Boot 3.x codebase
3. **SLF4J logging** — `log.info("message {}", param)` not `System.out.println()`
4. **No `SELECT *`** — explicit columns in all JPQL and native queries
5. **`java.time`** — `LocalDate`, `Instant`, `ZonedDateTime`. Never `new Date()` or `Calendar`
6. **No hardcoded secrets** — use `@Value` from env or AWS Secrets Manager
7. **`Optional.orElseThrow()`** — never `Optional.get()` without guard
8. **BigDecimal for money** — never `double` or `float` for monetary amounts
9. **No partial implementations** — complete every method; no `// TODO implement`
10. **Conventional Commits** — `feat(orders): add payment validation`

## Patterns in Use

- Outbox pattern for event publishing (see `knowledge/patterns/java-outbox-pattern.md`)
- Repository pattern — Spring Data JPA; repositories in `infrastructure/`
- Value objects for identifiers — `OrderId`, `CustomerId` not raw `UUID`/`String`
- Domain events published via application event bus after successful commit

## Before Writing Code

1. Identify which layer (domain / application / infrastructure / web)
2. Check `knowledge/patterns/` for existing patterns
3. Check `knowledge/anti-patterns/` for what NOT to do
4. Check `capability-packs/java/` for Java-specific standards
