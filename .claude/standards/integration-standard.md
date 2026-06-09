# eeik-managed pack=architecture
# Integration Standard

**Pack:** architecture-pack | **Version:** 1.0

---

## Synchronous Integration (REST)

### When to Use
- The caller requires an immediate response to continue processing
- Reading data from another context (query, not command)
- External-facing APIs consumed by clients or third parties

### Rules
- Use REST with OpenAPI 3 contracts — no undocumented endpoints
- Use HTTP semantics correctly: GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE (remove)
- Return RFC 7807 `ProblemDetail` for all error responses
- Version APIs: `/v1/`, `/v2/` — never break an existing contract without a new version
- Set timeouts on all outbound HTTP calls (default: 5s connect, 10s read)
- Apply circuit breakers (Resilience4j) on all synchronous service calls
- Never expose internal service ports — route through API Gateway or ALB

### Error Handling
```
2xx → success
400 → client error (do not retry)
401/403 → auth error (do not retry)
404 → not found (do not retry)
429 → rate limited (retry with backoff)
5xx → server error (retry with exponential backoff + jitter, max 3 attempts)
```

---

## Asynchronous Integration (Events)

### When to Use
- Cross-bounded-context communication where the producer does not need the result
- Long-running operations (decoupled processing)
- Fan-out scenarios (one event, multiple consumers)

### Rules
- Events are immutable facts: use past tense (`OrderPlaced`, `PaymentAuthorised`)
- Event schema must be versioned and registered in the Event Catalog
- Events must include: `eventId` (UUID), `eventType`, `timestamp` (ISO-8601 UTC), `correlationId`, `payload`
- Never put PII in event headers — only in encrypted payload if required
- Consumers must be idempotent — the same event may be delivered more than once
- Use the Outbox Pattern for transactional event publishing (never publish in a catch block)

### AWS Messaging Selection
| Pattern | Use | AWS Service |
|---------|-----|-------------|
| Point-to-point queue | One consumer, guaranteed delivery | SQS |
| Fan-out | Multiple consumers | SNS → SQS |
| Event bus (decoupled routing) | Dynamic routing rules | EventBridge |
| High-throughput streaming | Analytics, audit, replay | Kinesis |

---

## Anti-Patterns

- ❌ Shared databases between bounded contexts
- ❌ Synchronous chains longer than 3 hops (A→B→C→D) — use events
- ❌ Polling loops instead of event subscriptions
- ❌ Direct repository calls across service boundaries
- ❌ Undocumented REST endpoints
- ❌ Events without a registered schema
