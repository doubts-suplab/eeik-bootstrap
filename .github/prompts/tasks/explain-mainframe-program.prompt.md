---
mode: "ask"
description: "Explain a COBOL, JCL, or Assembler program in plain English for developers and analysts"
---

## Objective

Produce a clear, structured plain-English explanation of a mainframe program (COBOL, JCL, or HLASM Assembler). The explanation must be accessible to Java developers who are unfamiliar with mainframe technology, and also meaningful to business analysts who need to understand the business logic.

---

## Instructions to Copilot

1. **Identify the program type:** COBOL online (CICS), COBOL batch, JCL job stream, or Assembler
2. **Produce a program summary card** (name, type, calling mechanism, data stores, estimated complexity)
3. **Explain the structure** according to program type:

   **For COBOL programs:**
   - Explain each division briefly
   - Walk through the `PROCEDURE DIVISION` paragraph by paragraph
   - For each paragraph: what it does in plain English + the Java method equivalent
   - Explain all `EXEC SQL` blocks: what table, what operation, what happens on each SQLCODE
   - Explain all `EXEC CICS` interactions: what resource, what operation, success/failure handling
   - Explain all `COPY` statements: what copybook is referenced and what data structure it defines

   **For JCL job streams:**
   - Explain the overall job purpose
   - Walk through each step: what program runs, what files it reads/writes
   - Explain DD statements: what datasets are involved
   - Explain PROC calls and what the procedure does
   - Identify conditional step execution (`COND` parameters)

   **For Assembler programs:**
   - Explain the register save/restore conventions
   - Explain the macro invocations
   - Explain each labelled code block
   - Map to Java equivalent concepts where possible

4. **Extract and list business rules** — explicitly number them
5. **List side effects** — what databases are read/written, what files are accessed, what CICS transactions are called
6. **Note modernization considerations** — what would this look like as a Java microservice?

---

## Input

Paste the program source directly. Indicate:
- **Program type** if not obvious (COBOL online, COBOL batch, JCL, Assembler)
- **Target audience** — Java developer, business analyst, architect

---

## Output

```markdown
## Program Explanation — {PROGRAM-ID}

### Program Summary Card
| Attribute | Value |
|-----------|-------|
| Program Name | CUSTINQ |
| Type | COBOL Online (CICS) |
| Business Function | ... |
| Called By | CICS transaction CINQ |
| DB2 Tables | SCHEMA.CUSTOMERS (read) |
| VSAM Files | None |
| Approximate LOC | 350 |
| Complexity | Medium |

---

### What This Program Does (Plain English)
<1-2 paragraph non-technical summary>

---

### Program Structure Walkthrough

#### Paragraph: 1000-INITIALIZE
**Plain English:** Resets all working storage fields to their initial values at the start of each transaction.
**Java Equivalent:**
\`\`\`java
private void initialize() {
    returnCode = 0;
    customerRecord = new CustomerRecord();
}
\`\`\`

#### Paragraph: 2100-INQUIRE-CUSTOMER
...

---

### Business Rules
1. A customer inquiry requires a 10-digit numeric customer ID
2. ...

---

### Side Effects
| Type | Details |
|------|---------|
| DB2 Read | SCHEMA.CUSTOMERS — reads CUST_NAME, BALANCE, STATUS |
| CICS Return | Returns to calling transaction via EXEC CICS RETURN |

---

### Modernization Notes
- This program maps to a `GET /customers/{id}` REST endpoint
- The COMMAREA pattern maps to a request/response DTO
- DB2 access maps to a Spring Data JPA repository
- CICS RETURN maps to the HTTP response
```

---

## Quality Gates

- [ ] Plain English summary is readable without mainframe knowledge
- [ ] Every `EXEC SQL` block explained with table name and operation
- [ ] Every `EXEC CICS` interaction explained
- [ ] Business rules explicitly numbered
- [ ] Modernization notes included
- [ ] Suitable for the specified target audience
