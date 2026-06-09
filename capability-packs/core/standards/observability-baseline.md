# Observability Baseline Standard

**Applies To:** All production services  
**Enforced By:** `sre-engineer` agent, `/deploy-check` command  
**Minimum Bar:** Standard governance profile

---

## Three Pillars

### 1. Logging

| Rule | Implementation |
|------|---------------|
| Structured JSON logs | Logback with `logstash-logback-encoder` (Java) or structlog (Python) |
| MDC context on all logs | `correlationId`, `serviceId`, `traceId` on every log line |
| Log levels used correctly | ERROR: user-visible failures; WARN: recoverable issues; INFO: business events; DEBUG: dev only |
| No PII in logs | Mask email, name, card numbers before logging |
| Retention policy | CloudWatch: 90 days dev, 1 year prod |
| Centralized | All logs to CloudWatch Logs; optional: Splunk/ELK for regulated |

**Minimum required log events:**

```
Application startup (INFO)
Request received — method, path, correlationId (INFO)
Response sent — status code, duration_ms (INFO)
Business event occurred — event type, aggregateId (INFO)
External call made — service, endpoint, duration_ms (INFO)
External call failed — service, endpoint, error, duration_ms (ERROR)
Database query — table, operation, duration_ms (DEBUG)
Unhandled exception — full stack trace (ERROR)
```

### 2. Metrics

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| `http.request.count` | Counter | — |
| `http.request.duration_ms` | Histogram | p99 > 500ms → WARN |
| `http.error.rate` | Gauge | > 1% → WARN, > 5% → CRITICAL |
| `jvm.memory.used` | Gauge | > 80% heap → WARN |
| `jvm.gc.pause_ms` | Histogram | p99 > 500ms → WARN |
| `db.pool.active_connections` | Gauge | > 80% pool → WARN |
| `outbox.events.pending` | Gauge | > 100 for 5 min → CRITICAL |

**Spring Boot (Micrometer + CloudWatch):**

```yaml
management:
  metrics:
    export:
      cloudwatch:
        namespace: ${SERVICE_NAME}
        step: 1m
  observations:
    key-values:
      service: ${SERVICE_NAME}
      environment: ${ENVIRONMENT}
```

### 3. Tracing

| Rule | Implementation |
|------|---------------|
| Distributed tracing enabled | AWS X-Ray (all services) |
| Trace propagation | X-Ray trace header propagated on all outbound calls |
| Sampling rate | 5% default; 100% for errors |
| Service map | X-Ray service map in CloudWatch |

---

## SLO Templates (regulated/enterprise)

When `observability.slo_required: true`:

```yaml
slos:
  - name: availability
    target: 99.9%            # 99.95% for enterprise
    window: 30d
    indicator: "1 - error_rate"
    
  - name: latency_p99
    target: 500ms
    window: 30d
    indicator: "http.request.duration_ms p99"
    
  - name: latency_p50
    target: 100ms
    window: 30d
    indicator: "http.request.duration_ms p50"

error_budget:
  monthly_minutes: 43.8      # for 99.9% availability (30d × 60m × 0.1%)
  alert_at_burn_rate: 2x     # page when burning budget 2x faster than expected
```

---

## CloudWatch Dashboard (CDK)

Every service must have a CloudWatch dashboard with:

```typescript
new cloudwatch.Dashboard(this, 'ServiceDashboard', {
  dashboardName: `${serviceName}-${environment}`,
  widgets: [
    // Row 1: Request rate, error rate, p99 latency
    // Row 2: JVM memory, GC pause, DB pool
    // Row 3: Outbox queue depth, external call error rates
    // Row 4: Business metrics (orders per minute, etc.)
  ],
});
```
