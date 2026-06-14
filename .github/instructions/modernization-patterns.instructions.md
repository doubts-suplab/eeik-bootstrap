---
applyTo: "**/legacy/**/*.java, **/migration/**/*.java, **/*.cbl, **/*.cob, **/*.rpgle, **/cobol/**/*.java, **/modernization/**/*.java"
---

## Context

This instruction file applies to legacy system modernisation work: COBOL-to-Java migration, RPG IV / RPGLE to Java conversion, Spring Framework 4/5 to Spring Boot 3.x upgrades, and `javax.*` to `jakarta.*` namespace migrations. The guiding principle is **controlled, incremental migration** using the Strangler Fig pattern — never a big-bang rewrite. All legacy behaviour must be preserved exactly; the Anti-Corruption Layer (ACL) isolates modern code from legacy data models.

---

## Coding Standards

- **Strangler Fig only:** Migrate by route/feature, running old and new code simultaneously; switch traffic via feature flag
- **Anti-Corruption Layer (ACL):** Always introduce an ACL adapter when modern code calls legacy systems; never expose legacy data models to the domain layer
- **Parallel run first:** Run new implementation in shadow mode (write-only, no traffic served) before switching; compare outputs
- **javax → jakarta:** In Spring Boot 3.x, every `javax.*` import must be `jakarta.*`; use `spring-boot-migration` or IDE migration tool
- **No big-bang rewrites:** Never attempt to migrate an entire COBOL program in a single step; decompose into functions
- **Preserve business rules exactly:** Copy business logic verbatim before optimising; document every deliberate deviation
- **Feature flags for cutover:** Use LaunchDarkly or Spring `@ConditionalOnProperty` to control legacy/modern routing
- **Data migration is separate:** Schema migrations run independently of code changes; use Flyway with phased scripts

---

## Preferred Patterns

### Strangler Fig Router

```java
// ✅ CORRECT — feature-flagged routing to legacy or modern implementation
@Service
@RequiredArgsConstructor
public class OrderServiceRouter {

    private final LegacyOrderService legacyOrderService;
    private final ModernOrderService modernOrderService;
    private final FeatureFlags flags;

    public Order placeOrder(PlaceOrderCommand cmd) {
        if (flags.isEnabled("modern-order-service", cmd.customerId())) {
            return modernOrderService.placeOrder(cmd);
        }
        return legacyOrderService.placeOrder(cmd);
    }
}
```

### Anti-Corruption Layer

```java
// ✅ CORRECT — ACL translates legacy COBOL copybook structure to domain model
@Component
public class LegacyOrderAdapter implements OrderPort {

    private final LegacyOrderServiceClient legacyClient;

    @Override
    public Order findById(OrderId orderId) {
        LegacyCustRec legacyRecord = legacyClient.fetchOrder(orderId.value());
        return Order.builder()
            .id(OrderId.of(legacyRecord.getOrdId().trim()))
            .customerId(legacyRecord.getCustId().trim())
            .totalAmount(new BigDecimal(legacyRecord.getTotalAmt()).movePointLeft(2))
            .status(mapLegacyStatus(legacyRecord.getOrdSts()))
            .build();
    }

    private OrderStatus mapLegacyStatus(String legacyCode) {
        return switch (legacyCode.trim()) {
            case "OP" -> OrderStatus.OPEN;
            case "CL" -> OrderStatus.CLOSED;
            case "CA" -> OrderStatus.CANCELLED;
            default -> throw new UnknownLegacyStatusException(legacyCode);
        };
    }
}

// ❌ WRONG — leaking legacy model into the domain layer
public Order findById(String id) {
    LegacyCustRec rec = legacyClient.fetchOrder(id);
    return rec;  // LegacyCustRec used as domain object — coupling
}
```

### javax → jakarta Migration

```java
// ✅ CORRECT — Spring Boot 3.x uses jakarta.*
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.validation.constraints.NotNull;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.transaction.Transactional;

// ❌ WRONG — javax.* in Spring Boot 3.x [BLOCKER]
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.validation.constraints.NotNull;
import javax.servlet.http.HttpServletRequest;
import javax.transaction.Transactional;
```

### COBOL Field Mapping (PIC clause → Java type)

```java
// COBOL:   05 CUST-ID         PIC X(10).
// Java:    String customerId;  // trim() required — fixed-width padded with spaces

// COBOL:   05 ORDER-AMT       PIC 9(7)V99.
// Java:    BigDecimal amount = new BigDecimal(raw).movePointLeft(2);

// COBOL:   05 ORDER-DATE      PIC 9(8).  (YYYYMMDD)
// Java:    LocalDate date = LocalDate.parse(raw, DateTimeFormatter.BASIC_ISO_DATE);

// COBOL:   05 STATUS-FLAG     PIC X(1).  ('Y'/'N')
// Java:    boolean active = "Y".equals(raw.trim());
```

---

## Anti-Patterns — Do NOT Generate

```java
// WRONG: big-bang rewrite — replace all legacy code at once [BLOCKER]
// Never migrate 50,000 lines of COBOL in a single sprint

// WRONG: javax.* in Spring Boot 3.x [BLOCKER]
import javax.persistence.Entity;

// WRONG: legacy model leaking into domain [MAJOR]
public LegacyCustRec getOrder(String id) {
    return legacyClient.fetchOrder(id);  // legacy type in public API
}

// WRONG: silent field truncation [MAJOR]
String customerId = legacyRecord.getOrdId();  // missing .trim() — trailing spaces cause lookup failures

// WRONG: direct DB join across legacy and modern schemas [MAJOR]
// SELECT o.order_id, c.email FROM legacy_orders o JOIN modern_customers c ON o.cust_id = c.id
// Cross-schema joins tightly couple two bounded contexts

// WRONG: hardcoded feature flag value [MINOR]
if (true) {  // should be flags.isEnabled("feature-name")
    return modernService.process(cmd);
}
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| Spring Boot | 3.x | Requires Java 17+; `jakarta.*` namespace exclusively |
| spring-boot-properties-migrator | 3.x | Auto-migrates deprecated property names on startup |
| openrewrite | 8.x | Automated refactoring; `UpgradeSpringBoot_3_2` recipe |
| LaunchDarkly Java SDK | 7.x | Feature flags for Strangler Fig routing |
| spring-cloud-config | 4.x | Externalise feature flag config for phased rollout |

---

## Migration Verification

After each migration phase:

1. **Functional equivalence:** Run the legacy and modern implementations in parallel with identical inputs; assert output equality
2. **Data mapping:** Verify every COBOL PIC clause maps to the correct Java type (trim strings, scale decimals, parse dates)
3. **javax → jakarta:** Run `grep -r "import javax\." src/main/java/` — must return zero results in Spring Boot 3.x modules
4. **No cross-context joins:** Run `grep -r "legacy_\|LEGACY_" src/main/java/` in modern service modules — must return zero results
5. **Feature flag coverage:** Every cutover point has a named feature flag; no hardcoded `if (true)` routing
