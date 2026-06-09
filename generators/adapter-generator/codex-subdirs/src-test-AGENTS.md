# AGENTS.md — Test Source Root

> **Deploy to**: `src/test/AGENTS.md` in your project
> Codex CLI reads this automatically when working in test files.

---

You are writing **tests** for a Spring Boot 3.x application.

## Test Pyramid

```
Unit tests (fast, no Spring context)
  → Domain logic, value objects, service methods with mocked deps
  → Tools: JUnit 5, AssertJ, Mockito 5
  → Target: all domain and application layer classes

Integration tests (Spring slice or Testcontainers)
  → Repository layer: @DataJpaTest + Testcontainers (real PostgreSQL)
  → Web layer: @WebMvcTest (no DB)
  → Full slice: @SpringBootTest + Testcontainers
  → Tools: Testcontainers 1.19+, @ServiceConnection

Contract tests
  → Consumer-driven contracts with Pact
  → Verify API contracts without calling real services
```

## Non-Negotiable Rules

1. **No `Thread.sleep()`** — use `Awaitility.await().atMost(10, SECONDS).untilAsserted(...)`
2. **No `Optional.get()` in tests** — use `assertThat(optional).isPresent()` then `.get()`
3. **Testcontainers not H2** — test against real PostgreSQL for repository tests
4. **`static` containers** — start once per class, not once per test method
5. **Descriptive test names** — `should_reject_payment_when_balance_insufficient()`
6. **AAA structure** — Arrange / Act / Assert with blank lines between sections
7. **No logic in tests** — if/else in a test means you need two tests
8. **AssertJ not JUnit assertions** — `assertThat(result).isEqualTo(expected)` not `assertEquals`
9. **Mock only what you own** — don't mock third-party classes directly; wrap them
10. **Coverage target: 80%** — lines and branches; check `jacoco` report

## Test Class Templates

### Unit test (no Spring)
```java
class OrderServiceTest {
    private final OrderRepository repository = mock(OrderRepository.class);
    private final OrderService service = new OrderService(repository);

    @Test
    void should_create_order_for_valid_request() {
        // Arrange
        var request = new CreateOrderCommand(customerId(), BigDecimal.TEN);
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        // Act
        var result = service.createOrder(request);

        // Assert
        assertThat(result.status()).isEqualTo(OrderStatus.PLACED);
        verify(repository).save(argThat(o -> o.amount().equals(BigDecimal.TEN)));
    }
}
```

### Integration test (Testcontainers)
```java
@DataJpaTest
@Testcontainers
class OrderRepositoryIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired OrderRepository repository;

    @Test
    void should_persist_order_and_retrieve_by_id() { ... }
}
```

## What to Test

- Domain invariants — test that invalid state throws domain exceptions
- Repository queries — test custom `@Query` methods with real data
- REST endpoints — test request validation, response shape, error codes
- Event publishing — verify outbox table has entry after command
- Security — test `@PreAuthorize` rules with `@WithMockUser`
