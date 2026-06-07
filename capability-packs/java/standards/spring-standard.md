# Spring Boot Standard

**Pack:** java-pack | **Version:** 1.0

---

## Layer Responsibilities

| Layer | Package | Responsibility |
|-------|---------|----------------|
| Web | `web` | HTTP routing, request/response mapping, validation — no business logic |
| Application | `application` | Use case orchestration, transaction boundaries |
| Domain | `domain` | Business logic, domain models, domain events — no framework dependencies |
| Infrastructure | `infrastructure` | Database, messaging, external APIs — implements domain ports |

## Service Pattern

```java
@Service
@Transactional(readOnly = true)          // read-only default for performance
public class OrderService {
    private final OrderRepository repository;
    private final DomainEventPublisher publisher;

    public OrderService(OrderRepository repository, DomainEventPublisher publisher) {
        this.repository = repository;
        this.publisher = publisher;
    }

    @Transactional                        // explicit for write operations
    public Order placeOrder(PlaceOrderCommand command) {
        var order = Order.place(command); // domain logic in domain object
        var saved = repository.save(order);
        publisher.publish(new OrderPlacedEvent(saved.getId()));
        return saved;
    }
}
```

## Controller Pattern

```java
@RestController
@RequestMapping("/v1/orders")
@Tag(name = "Orders", description = "Order management")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Place a new order")
    @ApiResponse(responseCode = "201", description = "Order created")
    @ApiResponse(responseCode = "400", description = "Validation error")
    public OrderResponse placeOrder(@Valid @RequestBody PlaceOrderRequest request) {
        return OrderMapper.toResponse(orderService.placeOrder(request.toCommand()));
    }
}
```

## Configuration Properties

```java
@ConfigurationProperties(prefix = "app.payments")
@Validated
public record PaymentProperties(
    @NotBlank String gatewayUrl,
    @Positive int timeoutSeconds,
    @NotBlank String secretName
) {}
```

## Outbox Pattern (Transactional Events)

Never publish events in a catch block or outside a transaction.

```java
@Transactional
public Order placeOrder(PlaceOrderCommand command) {
    var order = repository.save(Order.place(command));
    // Write to outbox table in same transaction
    outboxRepository.save(OutboxEvent.from(new OrderPlacedEvent(order.getId())));
    return order;
    // Outbox relay picks up and publishes asynchronously
}
```
