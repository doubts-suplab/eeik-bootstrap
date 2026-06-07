# Non-Functional Requirements Standard

**Pack:** architecture-pack | **Version:** 1.0

Every new service must define and document NFRs before implementation begins. Use this standard as a checklist during architecture review.

---

## Required NFR Categories

### Performance
| NFR | Default Target | Notes |
|-----|---------------|-------|
| API p99 latency | < 500ms | Measure at the load balancer |
| API p50 latency | < 100ms | |
| Batch throughput | Define per job | Records/second or records/minute |
| Database query p99 | < 50ms | Measured at the application |

### Availability
| NFR | Default Target |
|-----|---------------|
| Production SLA | 99.9% monthly |
| Planned maintenance window | Sunday 02:00–04:00 UTC |
| RTO (Recovery Time Objective) | < 1 hour |
| RPO (Recovery Point Objective) | < 15 minutes |

### Scalability
- Define the expected peak load in requests/second or events/second
- Define the data volume growth rate (GB/year)
- Define the maximum acceptable scale-out time

### Security
- Authentication method (Cognito / IAM / mTLS)
- Authorisation model (RBAC / ABAC / policy-based)
- Data classification (Public / Internal / Confidential / Restricted)
- PII handling requirements

### Compliance
- Applicable regulatory frameworks (GDPR, PCI-DSS, HIPAA)
- Data residency requirements
- Audit log retention period (minimum 1 year for regulated systems)

### Operability
- Mean Time To Detection (MTTD): < 5 minutes via CloudWatch alarms
- Mean Time To Recovery (MTTR): < 30 minutes for P1 incidents
- Deployment frequency target: at least weekly
- Change failure rate target: < 5%

---

## NFR Sign-Off Process

NFRs are agreed between the architect, tech lead, and product owner before the first sprint.

NFRs are reviewed at:
1. Architecture review gate
2. Production readiness review
3. Post-launch (1 week after go-live)
