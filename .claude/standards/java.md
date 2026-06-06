# Java / Spring Boot Coding Standards

> Mandatory standards for all Java code. Enforced by code review (`code-reviewer`, `java-tech-lead`), SonarQube, and CI gates.

---

## Framework & Language

- **Spring Boot 3.x** with **Java 21** (minimum Java 17)
- `jakarta.*` exclusively — never `javax.*`
- Use virtual threads (Project Loom) for I/O-bound operations when on Java 21
- Sealed classes and records for immutable value objects

---

## Dependency Injection

- **Constructor injection only** — all injected fields are `final`
- Never use `@Autowired` on fields or setters
- Never use `ApplicationContext.getBean()` in application code

```java
// CORRECT
@Service
public class OrderService {
    private final OrderRepository repository;
    private final EventPublisher publisher;

    public OrderService(OrderRepository repository, EventPublisher publisher) {
        this.repository = repository;
        this.publisher = publisher;
    }
}

// WRONG — field injection
@Service
public class OrderService {
    @Autowired private OrderRepository repository; // never
}
```

---

## Logging

- **SLF4J only** — never `System.out.println`, `System.err.println`, or `java.util.logging`
- Use parameterised messages — never string concatenation in log statements
- Log at the correct level: `DEBUG` (trace flow), `INFO` (significant events), `WARN` (recoverable problem), `ERROR` (unrecoverable, requires attention)
- **Never log PII** (names, emails, IDs that can identify individuals) at any level

```java
// CORRECT
private static final Logger log = LoggerFactory.getLogger(OrderService.class);
log.info("Order placed: orderId={}, customerId={}", order.getId(), order.getCustomerId());

// WRONG
System.out.println("Order placed: " + order.getId());
log.info("Order placed: " + order.getId()); // string concatenation
```

---

## Exception Handling

- Never use empty catch blocks
- Log exceptions at `WARN` (expected, recoverable) or `ERROR` (unexpected, requires investigation)
- Use `RuntimeException` subclasses for domain exceptions; use checked exceptions only at system boundaries
- Apply RFC 7807 `ProblemDetail` for all REST error responses
- Use `orElseThrow()` with descriptive message; never `Optional.get()` without `isPresent()`

---

## Date & Time

- Use `java.time` exclusively: `LocalDate`, `LocalDateTime`, `ZonedDateTime`, `Instant`, `Duration`
- Never use `java.util.Date`, `java.util.Calendar`, or `java.sql.Date` in new code
- Store timestamps in UTC (`Instant` or `OffsetDateTime` with `+00:00`)
- Use `ZoneId.of("UTC")` explicitly — never rely on JVM default timezone

---

## Immutability & Value Objects

- Use Java records for DTOs and value objects
- Use `Collections.unmodifiableList()` or Guava `ImmutableList` when returning collections
- Use `@Value` (Lombok) or records for configuration properties

---

## Null Safety

- Annotate nullable parameters and return types with `@Nullable` (Spring `@Nullable` or JSpecify)
- Use `Objects.requireNonNull(x, "x must not be null")` in constructors for required parameters
- Use `Optional<T>` as return type when absence is a valid domain concept — never as a parameter type

---

## Code Structure

- One class per file; package by feature, not layer
- Service classes: single responsibility — if a service has more than 5 public methods, review for decomposition
- Avoid God classes (>500 lines); split by responsibility
- Keep methods under 30 lines; extract well-named private methods
- No magic numbers — use named constants or enums

---

## SQL & Data Access

- Never write `SELECT *` — always specify column lists
- Use named parameters (`@Param("name")` in JPQL, `:name` in JDBC) — never positional parameters in named queries
- Never build SQL via string concatenation — use `NamedParameterJdbcTemplate`, JPA, or QueryDSL
- Use `@EntityGraph` to control fetch behaviour explicitly; never rely on lazy-loading accidentally

---

## Testing Standards

- JUnit 5 + AssertJ + Mockito 5
- Unit tests: fast, no Spring context, stub all collaborators
- `@WebMvcTest` for controller slice tests
- `@DataJpaTest` for repository tests (in-memory or Testcontainers)
- Integration tests: `@SpringBootTest` + Testcontainers for database/messaging
- Never use `Thread.sleep()` — use `Awaitility.await().atMost(...).until(...)`
- Test coverage: minimum 80% line, 70% branch (enforced by JaCoCo)
