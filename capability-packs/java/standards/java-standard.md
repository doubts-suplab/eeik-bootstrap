# Java / Spring Boot Standard

**Pack:** java-pack | **Version:** 1.0  
**Enforced by:** `java-code-reviewer`, `java-tech-lead`, CI JaCoCo gate, SonarQube

---

## Framework & Language

- **Java 21** minimum (Java 25 permitted; Java 17 legacy only)
- **Spring Boot 3.x** exclusively for new services
- `jakarta.*` — never `javax.*` in any Spring Boot 3.x code
- Use records for DTOs and value objects (immutable by design)
- Use sealed classes for closed type hierarchies (e.g. domain events)
- Virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`) for I/O-bound operations

## Dependency Injection

```java
// ✅ Constructor injection — all injected fields are final
@Service
public class OrderService {
    private final OrderRepository repository;
    private final DomainEventPublisher publisher;

    public OrderService(OrderRepository repository, DomainEventPublisher publisher) {
        this.repository = repository;
        this.publisher = publisher;
    }
}

// ❌ Never — field injection
@Autowired private OrderRepository repository;
```

## Logging

- SLF4J only — `LoggerFactory.getLogger(ClassName.class)`
- Parameterised messages: `log.info("Order placed: orderId={}", id)` — never string concatenation
- Never log PII at any level
- `DEBUG` = trace flow; `INFO` = significant events; `WARN` = recoverable; `ERROR` = unrecoverable

## Error Handling & Exceptions

- RFC 7807 `ProblemDetail` for all REST error responses
- Domain exceptions extend `RuntimeException` with descriptive message
- Never use empty catch blocks — minimum: `log.warn("...", e)`
- `Optional.orElseThrow()` always — never `Optional.get()` without `isPresent()`

## Data & SQL

- Never `SELECT *` — always explicit column list
- Named parameters only: `@Param("id")` in JPQL, `:id` in native SQL
- Never build SQL via string concatenation
- `@EntityGraph` for explicit fetch control; never rely on accidental lazy loading
- Store timestamps as `Instant` (UTC) — never `java.util.Date`

## Code Quality Gates

| Gate | Threshold |
|------|-----------|
| JaCoCo line coverage | ≥ 80% |
| JaCoCo branch coverage | ≥ 70% |
| SonarQube quality gate | Pass |
| Zero critical vulnerabilities | Required |

## Testing

- JUnit 5 + AssertJ + Mockito 5 for unit tests
- `@WebMvcTest` for controller slices; `@DataJpaTest` for repository slices
- `@SpringBootTest` + Testcontainers for integration tests
- `Awaitility.await()` for async assertions — never `Thread.sleep()`
- Test method naming: `methodName_scenario_expectedOutcome()`

## Prohibited Patterns

| Pattern | Alternative |
|---------|-------------|
| `@Autowired` on fields | Constructor injection |
| `javax.*` imports | `jakarta.*` |
| `System.out.println` | SLF4J `log.info/warn/error` |
| `SELECT *` | Explicit column list |
| `new Date()` / `Calendar` | `java.time` |
| `Optional.get()` without guard | `orElseThrow()` |
| Empty catch blocks | Log + rethrow or handle |
| `Thread.sleep()` in tests | `Awaitility` |
| Partial implementations | Complete every method body |
