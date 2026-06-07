# Reference Architectures

**Pack:** architecture-pack | **Version:** 1.0

---

## 1. Java Microservice on AWS (Standard)

**When to use:** New bounded context requiring independent deployability, separate scaling, and team autonomy.

```
Client → API Gateway → ALB → ECS Fargate (Spring Boot)
                                    ↓               ↓
                              Aurora PostgreSQL    SQS/EventBridge
                                    ↓
                              Secrets Manager
                              CloudWatch / X-Ray
```

**CDK Stacks:**
- `NetworkStack` — VPC, subnets, security groups
- `DataStack` — Aurora cluster, Secrets Manager secret
- `AppStack` — ECS cluster, task definition, ALB, auto-scaling
- `ObservabilityStack` — dashboards, alarms, X-Ray groups

---

## 2. Event-Driven Platform on AWS

**When to use:** Multiple services communicating asynchronously; fan-out processing; audit requirements.

```
Producer Service → Outbox Table → Outbox Relay → EventBridge
                                                      ↓
                                         ┌────────────┼────────────┐
                                    Consumer A    Consumer B    Consumer C
                                    (SQS Queue)  (SQS Queue)  (Lambda)
```

**Key decisions:**
- Outbox pattern for transactional event publishing (never publish in catch block)
- EventBridge for routing rules; SQS for guaranteed delivery to consumers
- DLQ on every SQS queue; alarm on DLQ depth > 0

---

## 3. Serverless API

**When to use:** Low-traffic, event-triggered APIs; cost-sensitive workloads; PoC/MVP.

```
Client → API Gateway (REST) → Lambda → DynamoDB
                                 ↓
                           Secrets Manager
                           CloudWatch Logs
```

**Considerations:**
- Cold start: use Provisioned Concurrency for latency-sensitive paths
- Max Lambda timeout: 15 minutes — use Step Functions for longer flows
- DynamoDB: design access patterns before table design

---

## 4. Strangler Fig (Legacy Modernisation)

**When to use:** Replacing IBM i, COBOL, or legacy Java systems incrementally without a big-bang rewrite.

```
Client → Proxy Layer (Spring Boot) ─── [New Feature] → New Service → Aurora
                    │
                    └── [Legacy Feature] → IBM i / Legacy System → DB2
```

**Phases:**
1. Introduce proxy (no behaviour change)
2. Implement new service behind proxy (shadow mode — compare outputs)
3. Route traffic to new service (feature flag)
4. Decommission legacy path
5. Repeat per feature/domain area
