# COBOL Modernisation Standard

Version: IBM Enterprise COBOL 6.x | CICS 5.x | DB2 z/OS 12 | z/OS 2.5+

---

## COBOL Program Analysis Framework

Before any modernisation, every COBOL program must be assessed:

### Complexity Scoring

| Metric | Low | Medium | High | Critical |
|--------|-----|--------|------|----------|
| Lines of code | <500 | 500–2000 | 2000–5000 | >5000 |
| Cyclomatic complexity | <10 | 10–30 | 30–60 | >60 | 
| External calls (CALL, LINK) | 0–2 | 3–5 | 6–10 | >10 |
| DB2 table access | 1–3 | 4–8 | 9–15 | >15 |
| CICS commands | 0 | 1–5 | 6–15 | >15 |
| Copybooks used | 1–5 | 6–15 | 16–30 | >30 |

### Hidden Dependencies (most common migration failures)

```
CICS:
  - COMMAREA / channels+containers (inter-program data passing)
  - CICS temporary storage queues (WRITEQ TS / READQ TS)
  - CICS transient data queues (WRITEQ TD / READQ TD)
  - CICS program control (XCTL, LINK, RETURN)
  - BMS map screens (subfile equivalent)

DB2:
  - Cursors (especially WITH HOLD — survives commits)
  - Stored procedures and UDFs
  - DB2 special registers (CURRENT DATE, CURRENT TIMESTAMP)
  - FETCH FIRST n ROWS ONLY clauses

JCL/Batch:
  - SORT steps that shape data before the COBOL step
  - GDG (Generation Data Groups) — pseudo-versioned files
  - VSAM ESDS/KSDS/RRDS file access patterns
  - IDCAMS utility calls (define, repro, delete)
```

---

## COBOL → Java Migration Mapping

### Data Division → Java Types

| COBOL | Java | Notes |
|-------|------|-------|
| `PIC 9(n)` | `int` / `long` | Choose by precision |
| `PIC 9(n)V9(d)` | `BigDecimal` | Never `double` for money |
| `PIC S9(n) COMP` | `int` / `long` | Signed binary |
| `PIC X(n)` | `String` | Trim trailing spaces |
| `PIC X(8)` (date) | `LocalDate` | Parse YYYYMMDD |
| `PIC 9(7) COMP-3` | `BigDecimal` | Packed decimal → BD |
| `88 level` | `enum` | Model as Java enum |
| `OCCURS n TIMES` | `List<T>` or `T[]` | Prefer List |
| `REDEFINES` | Sealed class / union | Map to polymorphism |

### Procedure Division → Java Patterns

| COBOL pattern | Java equivalent |
|---|---|
| PERFORM UNTIL | `while` loop |
| PERFORM VARYING | `for` loop |
| EVALUATE WHEN | `switch` expression |
| CALL identifier | Service/method call |
| CICS READ/WRITE | JPA Repository |
| EXEC SQL SELECT | Spring Data `@Query` |
| GOBACK | `return` |
| STOP RUN | System exit (rare in services) |

---

## CICS → Spring Boot Mapping

```
CICS Transaction    →  Spring Boot REST endpoint (or Kafka consumer)
COMMAREA            →  Request/Response DTO (Java record)
CICS Program Link   →  Service method call
CICS TS Queue       →  Redis / DynamoDB (temporary state)
CICS TD Queue       →  Kafka topic (event publication)
CICS DB2 READ       →  Spring Data JPA findById
CICS DB2 WRITE      →  Spring Data JPA save
CICS SYNCPOINT      →  @Transactional
CICS ABEND          →  Throw domain exception
```

---

## Strangler Fig for COBOL

### Phase 1: Facade (no COBOL change needed)
```java
// REST facade calls existing COBOL via CICS Web Services or MQ
@RestController
public class OrderFacadeController {
    private final CicsGateway cicsGateway;  // wraps MQ/SOAP call to COBOL

    @PostMapping("/orders")
    public OrderResponse createOrder(@RequestBody CreateOrderRequest req) {
        return cicsGateway.callProgram("ORDCRE01", req);
    }
}
```

### Phase 2: Shadow (parallel execution, compare results)
```java
@PostMapping("/orders")
public OrderResponse createOrder(@RequestBody CreateOrderRequest req) {
    var legacyResult  = cicsGateway.callProgram("ORDCRE01", req);
    var modernResult  = orderService.createOrder(req);   // new Java impl

    if (!legacyResult.equals(modernResult)) {
        log.warn("shadow_divergence", orderId = req.orderId(),
                 legacy = legacyResult, modern = modernResult);
    }
    return legacyResult;   // trust legacy until confident
}
```

### Phase 3: Canary → Cutover
- Route 5% → modern, 95% → COBOL
- Gradually increase to 100% over 2–4 weeks
- Kill switch via feature flag (AWS AppConfig / SSM)

---

## Copybook → Java Record

```cobol
* ORDDETL.CPY
01 ORDER-DETAIL.
   05 ORD-ID         PIC 9(10).
   05 ORD-CUST-ID    PIC X(20).
   05 ORD-AMOUNT     PIC 9(9)V99 COMP-3.
   05 ORD-STATUS     PIC X(2).
      88 ORD-PLACED  VALUE 'PL'.
      88 ORD-SHIPPED VALUE 'SH'.
      88 ORD-CLOSED  VALUE 'CL'.
```

```java
// Java record equivalent
public record OrderDetail(
    long orderId,                   // PIC 9(10)
    String customerIdRaw,           // PIC X(20) — trim before use
    BigDecimal amount,              // PIC 9(9)V99 COMP-3 — always BigDecimal
    OrderStatus status              // 88-levels become enum
) {
    public enum OrderStatus { PLACED, SHIPPED, CLOSED }
}
```

---

## Wave Ordering (COBOL programs)

1. **Utilities** — pure calculation, no I/O (CALC, CONV programs)
2. **Lookup programs** — read-only reference data access
3. **Report generators** — batch read + format (no updates)
4. **Inquiry transactions** — CICS read-only screens
5. **Maintenance transactions** — CICS CRUD screens
6. **Batch update jobs** — JCL-driven mass updates
7. **Core transaction programs** — CICS programs in critical paths (last)

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem |
|---|---|
| Translate PERFORM → method 1:1 | COBOL paragraphs don't map to OO methods — understand intent first |
| Ignore `REDEFINES` | Data overlays are subtle; wrong Java mapping causes silent corruption |
| Replace VSAM with H2 in tests | VSAM has different ordering semantics; use PostgreSQL/Oracle in tests |
| Ignore packed decimal precision | `PIC 9(7) COMP-3` → `double` loses precision on money; use `BigDecimal` |
| Port COBOL logic as-is | Many COBOL programs have implicit dead code from decades of patches — refactor, don't transliterate |
