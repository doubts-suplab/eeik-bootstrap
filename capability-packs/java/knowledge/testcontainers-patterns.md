# Testcontainers Integration Test Patterns

**Type**: Testing Pattern  
**Stack**: Spring Boot 3.x, JUnit 5, Testcontainers 1.19+

---

## When to Use Testcontainers

Use for integration tests that verify real behaviour against real infrastructure:
- Repository / DAO layer tests (real DB, not H2)
- Kafka consumer/producer tests
- Redis cache tests
- AWS S3 / SQS (using Localstack)
- Full slice tests: `@SpringBootTest` + real containers

Do NOT use for unit tests — start containers once per test class or suite, not per test.

---

## Spring Boot 3.1+ Integration (ServiceConnection)

The cleanest approach — auto-configures datasource, kafka brokers etc. from container:

```java
@SpringBootTest
@Testcontainers
class OrderRepositoryIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void should_persist_and_retrieve_order() {
        var order = new Order(UUID.randomUUID(), "customer-1", BigDecimal.TEN, OrderStatus.PLACED);
        orderRepository.save(order);

        var found = orderRepository.findById(order.getId());

        assertThat(found).isPresent();
        assertThat(found.get().getStatus()).isEqualTo(OrderStatus.PLACED);
    }
}
```

`@ServiceConnection` eliminates all `@DynamicPropertySource` boilerplate.

---

## Shared Container (reuse across tests — faster)

```java
// Shared base class — container starts once per JVM
@Testcontainers
public abstract class AbstractIntegrationTest {

    @Container
    static final PostgreSQLContainer<?> POSTGRES =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withReuse(true);           // reuse between test runs in dev

    @Container
    static final KafkaContainer KAFKA =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.6.0"))
            .withReuse(true);

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url",      POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username",  POSTGRES::getUsername);
        registry.add("spring.datasource.password",  POSTGRES::getPassword);
        registry.add("spring.kafka.bootstrap-servers", KAFKA::getBootstrapServers);
    }
}
```

```java
// Extend in all integration tests
class OrderServiceIT extends AbstractIntegrationTest {
    @Test void test_order_creation() { ... }
}
```

---

## Kafka Integration Test

```java
@SpringBootTest
@Testcontainers
class OrderEventConsumerIT {

    @Container
    @ServiceConnection
    static KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    @Autowired
    KafkaTemplate<String, OrderPlacedEvent> kafkaTemplate;

    @Autowired
    OrderRepository orderRepository;

    @Test
    void should_process_order_placed_event() throws Exception {
        var event = new OrderPlacedEvent("order-123", "customer-1", BigDecimal.TEN);

        kafkaTemplate.send("orders.placed.v1", event.orderId(), event).get(5, SECONDS);

        await().atMost(10, SECONDS).untilAsserted(() ->
            assertThat(orderRepository.findByExternalId("order-123")).isPresent()
        );
    }
}
```

---

## Localstack (AWS Services)

```java
@Container
@ServiceConnection
static LocalStackContainer localstack =
    new LocalStackContainer(DockerImageName.parse("localstack/localstack:3.2"))
        .withServices(LocalStackContainer.Service.S3, LocalStackContainer.Service.SQS);

@DynamicPropertySource
static void awsProperties(DynamicPropertyRegistry registry) {
    registry.add("aws.endpoint-override", () -> localstack.getEndpoint().toString());
    registry.add("aws.region",            () -> localstack.getRegion());
    registry.add("aws.credentials.access-key", localstack::getAccessKey);
    registry.add("aws.credentials.secret-key", localstack::getSecretKey);
}
```

---

## Flyway Migration Tests

```java
@Test
void flyway_migrations_apply_cleanly() {
    // If the container starts and Spring context loads, Flyway ran successfully.
    // This test simply validates no migration errors exist.
    assertThat(flywayMigrations.info().current()).isNotNull();
    assertThat(flywayMigrations.info().pending()).isEmpty();
}
```

---

## Performance: Container Startup Times

| Container | Typical startup |
|---|---|
| PostgreSQL 16-alpine | 3–5s |
| Kafka (Confluent) | 10–15s |
| LocalStack | 15–25s |
| Redis | 2–3s |
| MongoDB | 5–8s |

**Always use `static` containers** — start once per class, not once per test.  
**Enable reuse** in dev with `.withReuse(true)` — set `testcontainers.reuse.enable=true` in `~/.testcontainers.properties`.
