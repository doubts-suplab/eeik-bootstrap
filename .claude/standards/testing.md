# Testing Standards

> Mandatory standards for all test code across Java and Angular. Enforced by `java-tester`, `angular-tester`, `test-quality-enforcer`, and `code-reviewer` agents.

---

## Test Pyramid

```
           /\
          /  \   E2E (few, slow, high confidence)
         /----\
        /      \  Integration (moderate, Spring context / Testcontainers)
       /--------\
      /          \  Unit (many, fast, no external dependencies)
     /____________\
```

Target ratio: **~70% unit / ~20% integration / ~10% E2E** by count.

---

## Java Testing Standards

### Framework Stack
- **JUnit 5** (`@Test`, `@BeforeEach`, `@AfterEach`, `@Nested`, `@ParameterizedTest`)
- **AssertJ** for assertions — never JUnit `assertEquals`
- **Mockito 5** for mocking (`@Mock`, `@InjectMocks` only for unit tests with no Spring context)
- **Testcontainers** for integration tests requiring real databases or messaging
- **`@WebMvcTest`** for controller slice tests
- **`@DataJpaTest`** for repository slice tests

### Naming Convention
```java
// Pattern: {method}_{scenario}_{expectedOutcome}
@Test
void placeOrder_whenPaymentAuthorised_createsOrderWithConfirmedStatus() { ... }

@Test
void placeOrder_whenInventoryNotAvailable_throwsInsufficientStockException() { ... }
```

### Unit Test Structure (AAA)
```java
@Test
void calculateTotal_withTaxExemptCustomer_returnsPriceWithoutTax() {
    // Arrange
    var customer = CustomerFixtures.taxExempt();
    var items = List.of(new LineItem(product, 2));

    // Act
    var total = pricingService.calculateTotal(customer, items);

    // Assert
    assertThat(total.amount()).isEqualByComparingTo(BigDecimal.valueOf(100.00));
    assertThat(total.taxAmount()).isEqualByComparingTo(BigDecimal.ZERO);
}
```

### Anti-Patterns (Forbidden)
- No `Thread.sleep()` — use `Awaitility.await().atMost(5, SECONDS).until(...)`
- No `assertTrue(result != null)` — use `assertThat(result).isNotNull()`
- No empty `catch` blocks in tests — let exceptions propagate or use `assertThatThrownBy()`
- No `@InjectMocks` with `@SpringBootTest` — `@MockBean` for Spring context tests
- No static mutable state in test classes — use `@BeforeEach` for setup
- No testing implementation details — test observable behaviour only

### Coverage Thresholds (enforced by JaCoCo)
- Line coverage: **80% minimum**
- Branch coverage: **70% minimum**
- Exclusions: DTOs without logic, config classes, generated code

---

## Angular Testing Standards

### Framework Stack
- **Jasmine** + **Karma** + **Istanbul**
- `TestBed` for component tests
- `HttpClientTestingModule` for service tests

### Component Test Pattern
```typescript
describe('OrderListComponent', () => {
  let component: OrderListComponent;
  let fixture: ComponentFixture<OrderListComponent>;
  let orderService: jasmine.SpyObj<OrderService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('OrderService', ['getOrders']);
    spy.getOrders.and.returnValue(of([orderFixture()]));

    await TestBed.configureTestingModule({
      imports: [OrderListComponent],
      providers: [{ provide: OrderService, useValue: spy }],
    }).compileComponents();

    fixture = TestBed.createComponent(OrderListComponent);
    component = fixture.componentInstance;
    orderService = TestBed.inject(OrderService) as jasmine.SpyObj<OrderService>;
    fixture.detectChanges();
  });

  it('should display orders returned by the service', () => {
    expect(fixture.nativeElement.querySelectorAll('.order-card')).toHaveSize(1);
  });
});
```

### Coverage Thresholds (enforced by Istanbul/karma-coverage)
- Statements: **80% minimum**
- Branches: **70% minimum**

---

## Test Data Management

- Use builder pattern or factory functions for test fixtures — no raw `new Entity(...)` scattered across tests
- Keep fixture files in `src/test/java/.../fixtures/` (Java) or `*.fixture.ts` (Angular)
- Use Testcontainers with `@DynamicPropertySource` for database integration tests — never rely on a shared dev database
- Reset state between tests — no test order dependencies
