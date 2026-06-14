---
applyTo: "**/events/**/*.java, **/messaging/**/*.java, **/kafka/**/*.java, **/listeners/**/*.java, **/publishers/**/*.java, **/events/**/*.ts, **/messaging/**/*.ts"
---

## Context

This instruction file applies to event-driven and messaging code: Kafka producers, Kafka consumers, Spring `@EventListener` / `ApplicationEventPublisher`, AWS SNS/SQS integrations, and Outbox Pattern implementations. Events are the primary integration mechanism between bounded contexts. All events must have a versioned schema registered with the Schema Registry. Consumers must be idempotent and route failures to a Dead-Letter Queue.

---

## Coding Standards

- **Event envelope:** Every domain event carries `eventId` (UUID), `eventType`, `aggregateId`, `aggregateType`, `occurredAt` (ISO 8601 UTC), `schemaVersion`, and `payload`
- **Naming convention:** `{domain}.{entity}.{verb}` in past tense — e.g. `orders.order.placed`, `payments.payment.authorised`
- **Schema evolution:** Only additive changes (add nullable fields); never remove or rename fields without a deprecation lifecycle
- **Outbox Pattern:** Publish events via a transactional outbox table — never produce directly inside a `@Transactional` method
- **Idempotent consumer:** Track processed `eventId` values in a deduplication store; skip already-processed events
- **DLQ routing:** After 3 retry attempts, route to `{topic}.dlq` with error metadata headers
- **Manual offset commit:** `enable.auto.commit=false`; commit only after successful processing and DLQ routing
- **No event sourcing without explicit approval:** CQRS/ES adds significant complexity; get ARB sign-off before introducing

---

## Preferred Patterns

### Event Envelope (Java)

```java
// ✅ CORRECT — structured event envelope
public record DomainEvent<T>(
    UUID eventId,
    String eventType,
    String aggregateId,
    String aggregateType,
    Instant occurredAt,
    int schemaVersion,
    T payload
) {
    public static <T> DomainEvent<T> of(String eventType, String aggregateId,
                                         String aggregateType, T payload) {
        return new DomainEvent<>(
            UUID.randomUUID(), eventType, aggregateId, aggregateType,
            Instant.now(), 1, payload
        );
    }
}

// Usage
var event = DomainEvent.of("orders.order.placed", order.getId().toString(), "Order", new OrderPlacedPayload(order));
```

### Outbox Pattern

```java
// ✅ CORRECT — write event to outbox table in same transaction as aggregate
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepo;
    private final OutboxRepository outboxRepo;

    @Transactional
    public Order placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd);
        orderRepo.save(order);

        OutboxEntry entry = OutboxEntry.from(
            DomainEvent.of("orders.order.placed", order.getId().toString(), "Order",
                new OrderPlacedPayload(order))
        );
        outboxRepo.save(entry);  // same transaction — atomically consistent

        return order;
    }
}

// ❌ WRONG — publishing directly in @Transactional risks dual-write inconsistency
@Transactional
public Order placeOrder(PlaceOrderCommand cmd) {
    Order order = orderRepo.save(Order.create(cmd));
    kafkaTemplate.send("orders.placed", order.getId().toString(), payload); // may succeed after DB rollback
    return order;
}
```

### Idempotent Consumer

```java
// ✅ CORRECT — deduplication via processed event store
@KafkaListener(topics = "orders.order.placed", groupId = "inventory-service")
public void onOrderPlaced(ConsumerRecord<String, OrderPlacedEvent> record) {
    String eventId = record.headers().lastHeader("eventId").toString();

    if (processedEventStore.exists(eventId)) {
        log.info("Skipping duplicate event: eventId={}", eventId);
        return;
    }

    try {
        inventoryService.reserveStock(record.value());
        processedEventStore.markProcessed(eventId);
    } catch (RetryableException exc) {
        throw exc;  // Spring Kafka retries
    } catch (Exception exc) {
        log.error("Non-retryable failure; routing to DLQ: eventId={}", eventId, exc);
        dlqProducer.send(record.topic() + ".dlq", record.key(), record.value(), _errorHeaders(eventId, exc));
    }
}
```

### Retry + DLQ Configuration (Spring Kafka)

```java
// ✅ CORRECT — fixed retry with DLQ after exhaustion
@Bean
public DefaultErrorHandler errorHandler(KafkaTemplate<String, ?> template) {
    var dlqPublisher = new DeadLetterPublishingRecoverer(template,
        (rec, ex) -> new TopicPartition(rec.topic() + ".dlq", rec.partition()));

    var backOff = new FixedBackOff(2_000L, 3L);  // 2s delay, 3 attempts
    return new DefaultErrorHandler(dlqPublisher, backOff);
}
```

---

## Anti-Patterns — Do NOT Generate

```java
// WRONG: direct Kafka produce inside @Transactional [BLOCKER]
@Transactional
public void placeOrder(PlaceOrderCommand cmd) {
    orderRepo.save(order);
    kafkaTemplate.send("orders.placed", payload);  // dual-write — can desync
}

// WRONG: no deduplication — consumer is not idempotent [BLOCKER]
@KafkaListener(topics = "orders.order.placed")
public void handle(OrderPlacedEvent event) {
    inventoryService.reserveStock(event);  // runs twice if message replayed
}

// WRONG: silently swallowing failures [BLOCKER]
try {
    process(record);
} catch (Exception e) {
    log.warn("Failed to process");  // no DLQ, record lost
}

// WRONG: past-tense violation — event named in present tense [MINOR]
"orders.order.place"  // should be "orders.order.placed"

// WRONG: breaking schema change — removing a field [MAJOR]
// Removing 'currency' field from OrderPlacedPayload — breaks existing consumers
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| spring-kafka | 3.x | `@KafkaListener`, `DefaultErrorHandler`, `DeadLetterPublishingRecoverer` |
| confluent-kafka-java | 7.x | `KafkaProducer` / `KafkaConsumer` with Schema Registry |
| avro | 1.11+ | Schema Registry Avro serialisation; use specific record types |
| resilience4j | 2.x | Circuit breaker for downstream calls triggered by events |
| aws-java-sdk-sqs | 2.x | `SqsAsyncClient`; visibility timeout ≥ max processing time |
| aws-java-sdk-sns | 2.x | Fan-out pattern; `MessageAttributes` for filtering |

---

## Test Conventions

- Integration test consumers with `@EmbeddedKafka` or Testcontainers Kafka container
- Test idempotency: publish the same event twice and assert the downstream effect occurs once
- Test DLQ routing: configure retries to 0 and inject a failing handler; assert message appears in `.dlq` topic
- Test Outbox relay: commit a transaction containing an outbox entry; assert the relay process publishes to Kafka
- Verify event envelope fields: `eventId`, `occurredAt`, `schemaVersion` are populated on every published event
- Use `@MockBean` to isolate consumer logic from downstream service calls in unit tests
