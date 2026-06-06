# Mainframe & IBM i Standards

> Standards for COBOL, CICS, JCL, RPG IV, RPGLE, CL, and DB2 code. Enforced by `modernization-expert` and `ibmi-modernization-expert` agents when reviewing or producing mainframe code.

---

## IBM Enterprise COBOL Standards

### Code Structure
- Use fixed-format COBOL (columns 7–72) for existing codebases
- New programs may use free-format (`>>SOURCE FORMAT FREE`) where the compiler supports it
- Divide programs into clear divisions: IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE
- Use meaningful paragraph names that describe the business function performed

### Data Division
- Define all working storage fields explicitly — never use `PIC X OCCURS` without defined bounds
- Use level-88 condition names for all coded values:
  ```cobol
  05 WS-ORDER-STATUS    PIC X(02).
     88 ORDER-PENDING   VALUE 'PN'.
     88 ORDER-CONFIRMED VALUE 'CO'.
     88 ORDER-CANCELLED VALUE 'CA'.
  ```
- Use `COMP-3` (packed decimal) for all arithmetic fields
- Use `COMP` (binary) for counters and subscripts
- Never use `REDEFINES` without a detailed comment explaining why

### Procedure Division
- One paragraph per logical function — paragraphs should be readable in under 30 lines
- Use `EVALUATE` (not nested `IF`) for multi-way conditional logic
- Use `PERFORM UNTIL` with explicit termination conditions — never `PERFORM ... VARYING` with unclear termination
- Never use `GO TO` except for `GO TO EXCEPTION-ROUTINE` patterns in error handling
- Always check `SQLCODE` after every DB2 call

### DB2 Access (COBOL)
- Never use `SELECT *` in embedded SQL
- Always use host variables with declared types matching the column type
- Always handle `SQLCODE +100` (not found) explicitly — do not treat it as an error
- Declare all cursors `WITH HOLD` only when explicitly needed across commit points

---

## IBM i RPG IV / RPGLE (ILE) Standards

### Declarations
- Use fully free-format RPG (`**FREE`) for all new programs
- Define all data structures with explicit subfield types — no implicit length subfields
- Use `LIKE` keyword to mirror database field types in data structures
- Use qualified data structure names (`QUALIFIED`) to avoid ambiguous field references

### File I/O
- Use `CHAIN` for direct access by key; use `READ`/`READP` for sequential; use `SETLL`/`SETGT` for positioning
- Always check operation codes or `%FOUND`, `%EOF`, `%ERROR` after every file operation
- Close files explicitly if opened in program (not by the OS at program end) for long-running programs

### Procedures and Subprocedures
- All new logic in subprocedures (ILE) — no monolithic mainline-only programs for new development
- Define procedure prototypes in separate `*MODULE` binding directory headers
- Return values from subprocedures via `RETURN` — not via output parameters where possible
- Use `EXTPGM` and `EXTPROC` for external calls — document the external program's purpose

### Error Handling
- Use structured error handling: `MONITOR`/`ON-ERROR`/`ENDMON` blocks
- Log errors using `QUSRJOBI` or application logging data queues — not `DSPLY` in batch
- Never ignore `%ERROR` or `%STATUS` indicators

---

## CL Standards

- Use `MONMSG` for every command where failure is possible
- Declare all local variables with `DCL` before use
- Use `CHGVAR` for variable assignment — not substitution in command parameters where avoidable
- Document job or subsystem context at the top of every CL program
- Retrieve and log `*ESCAPE` messages in `MONMSG` handlers — do not silently continue

---

## JCL Standards

- Every JCL job must have a `MSGCLASS` and `MSGLEVEL` statement
- Use catalogued procedures (`PROC`) — avoid inline JCL duplication across jobs
- Document the purpose of each step in a `/*` comment
- Use `COND` or `IF/THEN/ELSE/ENDIF` for conditional step execution — do not rely on abend to stop subsequent steps

---

## Migration Guidance

When modernising mainframe programs:
1. Document the existing program's purpose and business rules before touching the code
2. Maintain the original program in parallel until the new system passes UAT
3. Implement a call-through API so legacy CL programs can invoke new Java services during transition
4. Never rewrite and replace in a single big-bang cutover — use strangler-fig phases
