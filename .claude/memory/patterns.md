# Approved Patterns & Anti-Patterns

> This file records the patterns the team has explicitly approved and the anti-patterns to avoid. Claude Code agents check here before implementing new abstractions.

---

## Approved Patterns

### Spring Boot

#### Service Layer Pattern
```java
@Service
@Transactional(readOnly = true)
public class OrderService {
    private final OrderRepository orderRepository;
    private final OrderEventPublisher eventPublisher;

    public OrderService(OrderRepository orderRepository, OrderEventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public Order placeOrder(PlaceOrderCommand command) {
        // ...
    }
}
```
**Why:** Constructor injection, `readOnly = true` default (performance), explicit `@Transactional` for writes.

#### Repository Query Pattern
```java
@Query("SELECT o FROM Order o JOIN FETCH o.lineItems WHERE o.customerId = :customerId AND o.status = :status")
List<Order> findByCustomerIdAndStatus(@Param("customerId") UUID customerId, @Param("status") OrderStatus status);
```
**Why:** Named JPQL parameters, explicit fetch join to avoid N+1, no `SELECT *`.

#### RFC 7807 Error Response
```java
@ExceptionHandler(OrderNotFoundException.class)
public ResponseEntity<ProblemDetail> handleOrderNotFound(OrderNotFoundException ex) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    problem.setTitle("Order Not Found");
    problem.setProperty("orderId", ex.getOrderId());
    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(problem);
}
```
**Why:** RFC 7807 standard error format; structured, parseable by clients.

---

### Angular

#### Standalone Component Pattern
```typescript
@Component({
  selector: 'app-order-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `...`
})
export class OrderListComponent {
  private readonly orderService = inject(OrderService);
  orders = signal<Order[]>([]);
}
```
**Why:** Standalone components, `OnPush` for performance, `inject()` for DI, signals for reactive state.

---

### AWS / Infrastructure

#### Parameter Store Pattern for Configuration
```typescript
// CDK
new ssm.StringParameter(this, 'DbUrl', {
  parameterName: `/${props.environment}/${props.serviceName}/db/url`,
  stringValue: dbCluster.clusterEndpoint.socketAddress,
});
```
**Why:** Hierarchical naming convention enables per-environment, per-service isolation with IAM path-based access control.

---

## Anti-Patterns — Do Not Use

| Anti-Pattern | Why Forbidden | Approved Alternative |
|--------------|--------------|---------------------|
| `@Autowired` on fields | Breaks testability; hides dependencies | Constructor injection |
| `SELECT *` in SQL | Schema evolution breaks queries silently | Explicit column list |
| `System.out.println` | Not captured in log aggregation | `log.info(...)` with SLF4J |
| `new Date()` / `Calendar` | Legacy, timezone-unsafe | `LocalDate`, `LocalDateTime`, `Instant` |
| `Optional.get()` without `isPresent()` | NoSuchElementException in production | `.orElseThrow()` with descriptive message |
| `Thread.sleep()` in tests | Flaky, timing-dependent | `Awaitility.await().until(...)` |
| Empty catch blocks | Swallows errors silently | Log at `WARN`/`ERROR`, rethrow or handle |
| `javax.*` imports in Boot 3.x | Compilation failure | `jakarta.*` exclusively |
| `@Transactional` on `private` methods | Spring proxy cannot intercept | Move to `public` or restructure |
| Shared mutable state between tests | Test ordering dependencies | `@BeforeEach` setup, no static mutable fields |

---

## Pattern Approval Process

When a new pattern is established by the team:
1. Implement it in at least one production service
2. Get Tech Lead (`java-tech-lead` agent) sign-off
3. Add the pattern here with the rationale
4. Reference this file in code review when rejecting the anti-pattern alternative

<!-- TODO: Add project-specific patterns as they emerge -->
