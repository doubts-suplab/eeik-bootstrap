---
mode: "ask"
description: "Translate a COBOL program to a Java class with semantic risk flags and migration notes"
---

## Objective

Translate the provided COBOL program into a Java service class, producing a complete skeleton with mapped business logic, TODO annotations for human validation points, and a semantic risk matrix. This is a migration artifact — not production-ready code. All output requires manual review before deployment.

---

## Instructions to Copilot

1. **Read the full COBOL program** — do not begin translation until the complete source is provided
2. **Extract and enumerate all business rules** — list them explicitly before writing Java code
3. **Map the COBOL structure** to Java:
   - `IDENTIFICATION DIVISION` → class name and Javadoc header
   - `WORKING-STORAGE` fields → instance fields or method-local variables (with type mapping table)
   - `LINKAGE SECTION` → method parameters
   - `PROCEDURE DIVISION` paragraphs → private Java methods (one paragraph = one method)
   - `EXEC SQL` blocks → Spring Data `@Query` or `JdbcTemplate` calls
   - `EXEC CICS` blocks → REST call stub or message queue interaction stub
   - `EVALUATE` → Java `switch` expression
   - `PERFORM UNTIL` → `while` loop
   - `PERFORM n TIMES` → `for` loop
4. **Type mappings** (mandatory — never use `double` for monetary values):
   - `PIC S9(n)V99 COMP-3` → `BigDecimal` with scale 2
   - `PIC 9(n)` → `Long` or `int` depending on magnitude
   - `PIC X(n)` → `String` (apply `.trim()` on conversion — COBOL space-pads)
   - `PIC S9(4) COMP` → `int`
5. **Flag every** `PERFORM THRU`, `GO TO`, and `ALTER` — annotate with `// MIGRATION-RISK`
6. **Produce a `// TODO [MIGRATION-RISK]` comment** at every point where semantic equivalence cannot be guaranteed
7. **Produce a semantic risk matrix** at the end of the output
8. Use Google Java Style formatting throughout the generated Java

---

## Input

Provide:
- **The full COBOL program source** — copy-pasted text
- **Copybook definitions** for any `COPY` statement in the program (if available)
- **DB2 table definitions** for any `EXEC SQL` blocks (if available)
- **Business context** — what does this program do? (1–2 sentences)

---

## Output

Produce in this order:

### 1. Business Rules Extracted

```markdown
1. [rule description]
2. [rule description]
...
```

### 2. COBOL → Java Type Mapping Table

| COBOL Field | COBOL Type | Java Field | Java Type | Risk Notes |
|------------|-----------|-----------|---------|-----------|

### 3. Java Service Class

Complete Java file with:
- Package declaration
- Class-level Javadoc referencing the COBOL program name
- All imports
- Field declarations (from WORKING-STORAGE)
- Methods mapped from COBOL paragraphs
- `// TODO [MIGRATION-RISK]:` comments at every validation point

### 4. Semantic Risk Matrix

| Risk ID | COBOL Construct | Java Equivalent | Risk Level | Human Validation Required |
|---------|----------------|----------------|-----------|--------------------------|

### 5. Migration Notes

- Items that cannot be automatically translated
- External dependencies needed (Spring Data, JDBC, messaging)
- Recommended test cases based on extracted business rules

---

## Quality Gates

- [ ] All monetary COBOL fields mapped to `BigDecimal` — never `double` or `float`
- [ ] All `EXEC SQL` blocks have a Java equivalent stub
- [ ] All `PERFORM THRU` and `GO TO` constructs are flagged with `// MIGRATION-RISK`
- [ ] Semantic risk matrix produced with at minimum one entry per `EXEC SQL` block
- [ ] Business rules extracted and numbered before Java code is generated
- [ ] Java file compiles as a standalone class (may have stub method bodies with `throw new UnsupportedOperationException()`)
