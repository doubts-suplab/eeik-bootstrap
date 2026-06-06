---
applyTo: "**/*.rpgle, **/*.rpg, **/*.clle, **/*.cl, **/*.dspf, **/*.pf, **/*.lf"
description: "IBM i RPG IV/RPGLE coding conventions, ILE naming, DB2 for i SQL standards, job structure, error handling, and modernization patterns."
---

# IBM i — Copilot Instructions

> Applied automatically when working with RPG IV, RPGLE, CL, DDS display files, physical files, and logical files. Loaded alongside copilot-instructions.md.

---

## RPG IV / RPGLE Free-Format Conventions

Always write new RPG code in **fully free format** (no `/free`/`/end-free` directives required in RPGLE 7.2+). For legacy fixed-format code being modified, use the existing format; for new code within a legacy program, wrap additions in `/free` / `/end-free`.

### Program Header Specification

```rpgle
**FREE
// ============================================================
// Program  : CUSTINQ
// Purpose  : Customer inquiry — retrieve customer by ID
// Author   : Development Team
// Date     : 2024-11-01
// Called by: CSTMNU (interactive menu) / CUSTAPI (REST wrapper)
// ============================================================
Ctl-Opt DftActGrp(*No) ActGrp(*Caller) Option(*SrcStmt:*NoDebugIO);
Ctl-Opt BndDir('ENTBNDDIR');
Ctl-Opt Main(Main);
```

### Mandatory `Ctl-Opt` Settings

| Option | Required Value | Reason |
|--------|--------------|--------|
| `DftActGrp` | `*No` | Prevents legacy activation group; enables ILE error handling |
| `ActGrp` | `*Caller` or named group | Controls object lifecycle; do not use `*New` for service programs |
| `Option(*SrcStmt)` | Always set | Enables source-level debugging |
| `BndDir` | `'ENTBNDDIR'` (project binding directory) | Makes service programs available |

### Procedure Prototype and Interface Pattern

```rpgle
// ---- Prototype (in QRPGLESRC or copybook CUSTPRT) ----
Dcl-Pr GetCustomer ExtPgm('CUSTINQ');
  PCustomerId    Char(10) Const;
  PCustomerName  Char(50);
  PReturnCode    Int(10);
End-Pr;

// ---- Procedure Interface ----
Dcl-Pi Main;
  PCustomerId    Char(10) Const;
  PCustomerName  Char(50);
  PReturnCode    Int(10);
End-Pi;
```

### Data Structure Naming

```rpgle
// Externally described data structure — preferred over hardcoded fields
Dcl-Ds CustRec ExtName('CUSTPF') Qualified;
End-Ds;

// Program status data structure
Dcl-Ds PSDS PSDS Qualified;
  PgmName    *Proc;
  StatusCode *Status;
  MsgId      Char(7)  Pos(40);
End-Ds;
```

---

## ILE Naming — Service Programs, Modules, Binding Directories

| Object Type | Naming Convention | Example |
|-------------|------------------|---------|
| Module (`*MODULE`) | Verb+Noun, max 10 chars | `GETCUST`, `UPDORDER` |
| Program (`*PGM`) | Uppercase, max 10 chars, matches source member | `CUSTINQ`, `ORDPRC` |
| Service Program (`*SRVPGM`) | Domain prefix + function, max 10 chars | `CUSTSRV`, `PAYMTSRV` |
| Binding Directory (`*BNDDIR`) | Project + `BNDDIR` suffix | `ENTBNDDIR`, `FINBNDDIR` |
| Export list (`*.bnd`) | Same name as SRVPGM | `CUSTSRV.bnd` |

### Creating a Service Program

```cl
/* Create module */
CRTRPGMOD MODULE(ENTLIB/CUSTSRV) SRCFILE(QRPGLESRC) SRCMBR(CUSTSRV)
           DBGVIEW(*SOURCE) OPTIMIZE(*FULL) OUTPUT(*NONE)

/* Create service program from module + export list */
CRTSRVPGM SRVPGM(ENTLIB/CUSTSRV) MODULE(ENTLIB/CUSTSRV)
          EXPORT(*SRCFILE) SRCFILE(QSRVSRC) SRCMBR(CUSTSRV)
          BNDDIR(ENTLIB/ENTBNDDIR) ACTGRP(*CALLER)

/* Add to binding directory */
ADDBNDDIRE BNDDIR(ENTLIB/ENTBNDDIR) OBJ((ENTLIB/CUSTSRV *SRVPGM))
```

---

## CL Procedure Naming

| Object | Convention | Example |
|--------|-----------|---------|
| CL Program (`*PGM`) | Action + domain + suffix `C` | `CRTCUSTC`, `PURGLOGSCC` |
| CL Command (`*CMD`) | Verb + Object, max 10 chars | `CRTCUST`, `PRGLOG` |
| CL Module in ILE | Same as program, used in SRVPGM | `JOBSTRC` |

```cl
PGM        PARM(&CUSTID &RETCODE)

DCL        VAR(&CUSTID)  TYPE(*CHAR) LEN(10)
DCL        VAR(&RETCODE) TYPE(*INT)  LEN(4)
DCL        VAR(&MSGID)   TYPE(*CHAR) LEN(7)

MONMSG     MSGID(CPF0000 MCH0000) EXEC(GOTO CMDLBL(ERRHANDLE))

/* Main logic */
CALL       PGM(ENTLIB/CUSTINQ) PARM(&CUSTID *OMIT &RETCODE)

GOTO       CMDLBL(END)

ERRHANDLE:
RCVMSG     MSGTYPE(*EXCP) MSGID(&MSGID)
CHGVAR     VAR(&RETCODE) VALUE(-1)

END:
ENDPGM
```

---

## DDS Field Naming

### Physical File (PF) Standards

```dds
     A          R CUSTREC                   TEXT('Customer Record')
     A            CUSTID         10A         COLHDG('Customer' 'ID')
     A            CUSTNM         50A         COLHDG('Customer' 'Name')
     A            CUSTBAL        15P 2       COLHDG('Balance')
     A            CRTDT           8S 0       COLHDG('Create' 'Date')
     A          K CUSTID
```

- Record format name: max 10 chars, uppercase, derived from file purpose
- Field names: max 10 chars, uppercase; no leading/trailing spaces
- All numeric monetary fields: packed decimal (`P`) with 2 decimal positions; never floating point
- Date fields: 8-digit numeric (`S 0` or `L` with `DATFMT`)

### Logical File (LF) Standards

```dds
     A          R CUSTNMR                   PFILE(CUSTPF)
     A            CUSTNM
     A            CUSTID
     A            CUSTBAL
     A          K CUSTNM
     A          K CUSTID
```

Logical files: prefix with `L` or domain abbreviation; always specify `PFILE`.

### Display File (DSPF) Standards

- Record format naming: screen purpose + format code (e.g., `CUSTFMT1`, `CUSTMSGS`)
- Use `OVERLAY` indicator to avoid clearing screen between formats
- All user input fields must have `CHECK(RZ)` to strip leading zeros from numeric input
- Error messages through `ERRMSG` or `ERRMSGID` keywords, not hardcoded literals

---

## DB2 for i SQL Standards

### Schema vs Library

- In SQL context: use `SET SCHEMA` or fully qualify with schema name: `ENTSCHEMA.CUSTOMERS`
- In native I/O context: library used directly — `ENTLIB/CUSTPF`
- Do not mix native I/O and SQL on the same file within the same program without commit control alignment

### Parameterized SQL — Forbidden Pattern

```rpgle
// WRONG — EXECUTE IMMEDIATE with string concatenation is FORBIDDEN
SqlStmt = 'SELECT * FROM CUSTOMERS WHERE CUSTID = ''' + CustId + '''';
Exec Sql Execute Immediate :SqlStmt;

// CORRECT — Parameterized with host variables
Exec Sql
  Select CustName, CustBal
  Into   :WsCustName, :WsCustBal
  From   ENTSCHEMA.CUSTOMERS
  Where  CustId = :WsCustId;
```

### SQL Error Handling

```rpgle
Exec Sql
  Select CustName Into :WsCustName
  From ENTSCHEMA.CUSTOMERS
  Where CustId = :WsCustId;

Select;
  When SqlCode = 0;
    // Success
  When SqlCode = 100;
    // Not found
    ReturnCode = 4;
  When SqlCode < 0;
    // SQL error
    ErrMsg = %Char(SqlCode);
    ReturnCode = 12;
EndSl;
```

### JDBC vs Native I/O

| Scenario | Recommended Access Method |
|----------|--------------------------|
| New REST API exposing IBM i data | JDBC via IBM Toolbox for Java (`jt400.jar`) |
| Existing RPG accessing PF directly | Native I/O (file declarations with F-specs) |
| Cross-platform reporting | SQL over JDBC — use `SELECT` with explicit column list |
| Batch record processing > 100K rows | Native I/O with sequential read for performance |

---

## IBM i Job Structure

Every scheduled batch job must have a corresponding job description:

```cl
/* Create Job Description */
CRTJOBD JOBD(ENTLIB/NIGHTBAT) JOBQ(ENTLIB/BATCHQ) TEXT('Nightly batch jobs')
        OUTQ(ENTLIB/BATOUTQ) LOG(4 0 *NOLIST) LOGCLPGM(*YES)
        INQMSGRPY(*SYSRPYL) ACGCDE('BATCHACG')

/* Submit to batch */
SBMJOB CMD(CALL PGM(ENTLIB/NIGHTPRC)) JOB(NIGHTPRC) JOBD(ENTLIB/NIGHTBAT)
        JOBQ(ENTLIB/BATCHQ) MSGQ(*JOBD) HOLD(*NO)
```

- Every production batch job must specify `JOBD` explicitly — never rely on defaults
- `LOG(4 0 *NOLIST)` for production; `LOG(4 0 *SECLVL)` for debugging
- High-volume jobs: specify subsystem routing entry to dedicated batch subsystem

---

## Error Handling — Monitor-On vs Message Handling

### Preferred: Monitor-On in ILE RPG

```rpgle
Monitor;
  Exec Sql
    Insert Into ENTSCHEMA.AUDIT_LOG
    Values (:WsAuditRec);
  On-Error 802;
    // Duplicate key — record already exists, acceptable
    ReturnCode = 0;
  On-Error;
    // All other SQL errors
    ReturnCode = 12;
    Leave;
EndMon;
```

### CL Message Handling

```cl
CALL       PGM(ENTLIB/CUSTUPD) PARM(&CUSTID &RETCODE)
MONMSG     MSGID(CPF9999) EXEC(DO)
  RCVMSG   MSGTYPE(*EXCP) MSGID(&ERRMSGI) MSGDTA(&ERRMSGD)
  SNDPGMMSG MSGID(&ERRMSGI) MSGF(QCPFMSG) MSGDTA(&ERRMSGD) +
              TOPGMQ(*CALLER) MSGTYPE(*DIAG)
  CHGVAR   VAR(&RETCODE) VALUE(-1)
ENDDO
```

---

## Conversion Patterns: RPG to REST API (IWS)

IBM i Integrated Web Services (IWS) exposes RPG programs as REST endpoints without rewriting them:

1. Program must use `EXTPGM` prototype with `CONST` input parameters and output parameters
2. Register in IWS: `WRKWTR` → Web Services → Create Web Service → Program call
3. XML/JSON payload mapping is auto-generated from parameter data types
4. For production: deploy via IWS deployment manager; version with `/v1/` prefix in URI
5. Authentication: IBM i digital certificate + HTTP Basic Auth at minimum; OAuth 2.0 preferred

### RPG to Java Bridge (JDBC)

```java
// IBM Toolbox for Java — jt400.jar
import com.ibm.as400.access.*;

AS400 system = new AS400("ibmi-host.internal", "SVCUSER", credentials);
ProgramCall pgm = new ProgramCall(system);
pgm.setProgram("/QSYS.LIB/ENTLIB.LIB/CUSTINQ.PGM");
ProgramParameter[] params = {
    new ProgramParameter(AS400Text.toBytes("CUST0012345", 10)),  // Input: customer ID
    new ProgramParameter(50),                                      // Output: customer name
    new ProgramParameter(4)                                        // Output: return code
};
pgm.setParameterList(params);
if (!pgm.run()) {
    throw new RuntimeException("CUSTINQ failed: " + pgm.getMessageList()[0].getText());
}
String custName = new AS400Text(50, system).toObject(params[1].getOutputData()).toString().trim();
```

---

## Modernization Risk Classification

### Tight-Coupling Indicators — High Risk to Modernize

| Indicator | Risk | Action |
|-----------|------|--------|
| `CALL` to > 5 external programs in procedure | HIGH | Map call graph before modernizing |
| Native I/O with no SQL equivalent | HIGH | Create SQL view before modernizing |
| `DSPATR(PR)` (protected display fields) driven by runtime data | MEDIUM | Map UI logic carefully |
| `INFDS` used for I/O error trapping | MEDIUM | Replace with structured error handling in Java |
| `%PARMS` (parameter count checking) for optional params | LOW | Implement method overloading in Java |

### Data Dependency Analysis

Before modernizing an RPG program, run:

```sql
-- Find all physical files accessed by this program (via IFS catalog)
SELECT SYSTEM_TABLE_NAME, SYSTEM_TABLE_SCHEMA, TABLE_TYPE
FROM QSYS2.SYSTABLES
WHERE SYSTEM_TABLE_NAME IN (
  SELECT OBJECT_NAME FROM QSYS2.OBJECT_REFERENCES
  WHERE OBJECT_LIBRARY = 'ENTLIB' AND OBJECT_NAME = 'CUSTINQ' AND OBJECT_TYPE = '*PGM'
);
```

See `.github/agents/modernization-expert.agent.md` for the IBM i modernization agent.
