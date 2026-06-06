# Modernise RPG to Java

Translate the following IBM i RPG IV / RPGLE program to a Java Spring Boot service:

**RPG Program:** $PROGRAM_NAME
**Target Java Service:** $SERVICE_NAME

## Instructions

1. Read and understand the RPG program's business logic completely before writing any Java
2. Preserve all business rules exactly — modernisation changes the platform, not the logic
3. Map IBM i data types to Java equivalents (packed decimal → `BigDecimal`, etc.)
4. Map file I/O to Spring Data JPA repositories or Spring Data JDBC
5. Implement the Java service following all standards in `.claude/standards/java.md`

See `.github/instructions/ibmi.instructions.md` and `.github/instructions/spring-boot.instructions.md`.

## Data Type Mapping Reference

| IBM i Type | Java Type | Notes |
|-----------|-----------|-------|
| `PACKED(n,d)` | `BigDecimal` | Preserve precision and scale |
| `ZONED(n,d)` | `BigDecimal` | |
| `CHAR(n)` | `String` | Trim trailing spaces |
| `DATE` | `LocalDate` | |
| `TIME` | `LocalTime` | |
| `TIMESTAMP` | `LocalDateTime` | |
| `IND` (indicator) | `boolean` | |
| `INTEGER(4)` | `int` | |
| `INTEGER(8)` | `long` | |

## Output Required

1. **Java entity classes** mapping to the DB2 for i physical file structure
2. **Spring Data JPA repository** with equivalent query methods
3. **Java service class** implementing the business logic
4. **Unit tests** covering the key business rules
5. **Coexistence notes** — how the RPG program and Java service can run in parallel during migration

## Constraints

- Do not change business logic — if the RPG calculates something in a specific way, the Java must calculate it identically
- Preserve precision for all decimal arithmetic — use `BigDecimal` with explicit scale and `RoundingMode`
- Document any IBM i behaviour that has no direct Java equivalent
