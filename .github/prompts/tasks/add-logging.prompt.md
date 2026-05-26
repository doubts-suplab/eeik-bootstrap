---
mode: "ask"
description: "Add SLF4J logging at appropriate levels throughout a Java class"
---

## Objective

Add SLF4J logging to the provided Java class at the correct log levels, following the team's logging standards. Logging must be structured, parameterized, and never expose sensitive data.

---

## Instructions to Copilot

1. Add the SLF4J logger declaration at the top of the class:
   ```java
   private static final Logger log = LoggerFactory.getLogger(ClassName.class);
   ```
2. Apply log levels according to these rules:

   | Level | When to Use |
   |-------|-------------|
   | `TRACE` | Very detailed diagnostic info — method argument values, loop iteration counts (disabled in production by default) |
   | `DEBUG` | Entry into significant methods with key parameters; results of external calls |
   | `INFO` | Significant business events: entity created, transaction committed, user authenticated, job started/completed |
   | `WARN` | Recoverable errors: retried operation, fallback used, deprecated API called, resource near limit |
   | `ERROR` | Unrecoverable exceptions that affect correctness; always include the exception object as last argument |

3. Always use parameterized logging — never string concatenation:
   ```java
   log.debug("Processing order {} for customer {}", orderId, customerId);  // CORRECT
   log.debug("Processing order " + orderId + " for customer " + customerId);  // WRONG
   ```
4. On every `catch` block that does not rethrow, add at minimum `log.warn(...)` or `log.error(..., exception)`
5. On every `catch` block that rethrows, add `log.debug(...)` or `log.warn(...)` before rethrowing (so the context is logged at this layer)
6. Never log:
   - Passwords, tokens, API keys, or secrets
   - Full credit card numbers, SSNs, or PII fields (log masked versions only: `****1234`)
   - Full HTTP request/response bodies if they contain sensitive data
7. Log external service calls at `DEBUG` (before) and `DEBUG` (success) / `WARN` (failure)
8. Log Spring Batch step entry/exit at `INFO`
9. For CICS-style transaction programs: log transaction start and completion at `INFO`

---

## Input

Paste the Java class that needs logging added.

---

## Output

The complete Java class with logging added. Include a summary:

```markdown
### Logging Added

| Location | Level | Message |
|----------|-------|---------|
| `findById()` entry | DEBUG | "Fetching order by id {}" |
| `findById()` not found | DEBUG | "Order {} not found" |
| `createOrder()` success | INFO | "Order {} created for customer {}" |
| `catch PaymentException` | WARN | "Payment failed for order {}, reason: {}" |
| `catch Exception` | ERROR | "Unexpected error processing order {}" + exception |
```

---

## Quality Gates

- [ ] Logger declared as `private static final Logger log = LoggerFactory.getLogger(...)`
- [ ] All catch blocks have at least a WARN or ERROR log entry (unless rethrowing immediately)
- [ ] All parameterized — no string concatenation in log calls
- [ ] No sensitive data in log messages
- [ ] INFO level used for business events, not for debug info
- [ ] Exception object passed as last argument to `log.error(...)` calls to include stack trace
