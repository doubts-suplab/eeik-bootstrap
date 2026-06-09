# IBM i Modernization Patterns

## Common RPG → Java Mappings

| IBM i Concept | Java Equivalent | Notes |
|---------------|----------------|-------|
| Physical File (PF) | JPA Entity + DB table | Map DDS field types to Java types |
| Logical File (LF) | JPA Query / Spring Data method | Keyed logical files → `findBy{field}` |
| Display File (DSPF) | REST API + React/Angular UI | Separate concerns — display from business logic |
| Data Queue | SQS Queue | LIFO data queues → FIFO SQS |
| Data Area | AWS SSM Parameter / DynamoDB item | Small shared data → SSM; complex → DynamoDB |
| Job Queue | ECS Task / SQS + Lambda | Batch jobs → ECS Fargate scheduled task |
| Spool File | S3 + PDF generation | Reports → S3 PDF with pre-signed URL |
| CL Program | Shell script / Lambda orchestration | Job orchestration → Step Functions |
| \*LIBL (Library List) | Spring profiles / environment config | Library list context → Spring profile |
| Commitment Control | Spring `@Transactional` | Multi-file updates → `@Transactional` |
| OPNQRYF | Spring Specification / JPA Criteria | Dynamic queries → Spring Specification |

## DDS to JPA Type Mapping

| DDS Type | IBM i | Java / JPA |
|----------|-------|-----------|
| `A` (character) | CHAR(n) | `String` |
| `S` (packed decimal) | DECIMAL(p,s) | `BigDecimal` |
| `P` (packed decimal) | PACKED(p,s) | `BigDecimal` |
| `B` (binary) | SMALLINT/INT | `Integer` / `Long` |
| `L` (date) | DATE | `LocalDate` |
| `T` (time) | TIME | `LocalTime` |
| `Z` (timestamp) | TIMESTAMP | `Instant` |

## Common Hidden Integration Points

When analyzing IBM i programs, always look for:

1. **Data Queue writes** — `DTAARA(*LDA)` or `SNDDTAQ` calls → async messaging that must be preserved
2. **User spaces** (`QUSRTOOL`) — sometimes used as inter-process shared memory
3. **\*USRPRF checks** — application-level authorization in RPG → migrate to IAM/Spring Security
4. **Exit points** (`QIBM_*`) — system-level hooks → replace with Spring AOP or event listeners
5. **Subfile record formats** — complex display file patterns that carry business logic in `READC` loops
6. **CHAIN/READE loops** — file cursor logic that often contains the core business algorithm

## Wave Ordering for IBM i

Typical dependency chain (leaf → core):

```
Utility programs (no business logic, no outbound calls)
    ↓
Report programs (read-only, no state changes)
    ↓
Inquiry programs (display-only, no updates)
    ↓
Maintenance programs (CRUD operations — low complexity)
    ↓
Transaction programs (multi-file updates with business rules)
    ↓
Batch programs (complex processing, often month-end / year-end)
    ↓
Core transaction programs (order entry, claims, payments — highest risk)
```
