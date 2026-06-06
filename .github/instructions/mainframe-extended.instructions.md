---
applyTo: "**/*.cbl, **/*.jcl, **/*.asm, **/vsam/**, **/ims/**"
description: "Extended mainframe standards covering JES2/JES3 job classes, VSAM access patterns, IMS DB/DC, IBM MQ, z/OS batch tuning, DFSORT, RACF security, and CICS resource definitions."
---

# Mainframe Extended — Copilot Instructions

> Applied automatically for COBOL, JCL, Assembler, VSAM, and IMS source files. Extends mainframe.instructions.md with advanced z/OS subsystem patterns.

---

## JES2/JES3 — Job Classes and Priorities

### Job Card Standards

```jcl
//PAYROLL1 JOB (FIN-001),'PAYROLL WEEKLY RUN',
//             CLASS=B,
//             MSGCLASS=X,
//             MSGLEVEL=(1,1),
//             NOTIFY=&SYSUID,
//             PRTY=8,
//             REGION=0M,
//             TIME=(30,0)
```

| Parameter | Usage |
|-----------|-------|
| `CLASS=A` | Short interactive/test jobs (< 5 min elapsed) |
| `CLASS=B` | Medium batch jobs (5–30 min), non-priority |
| `CLASS=C` | Long-running production batch (> 30 min) |
| `CLASS=S` | STC (started task) — do not use in JOB cards |
| `PRTY=1–15` | JES2 input priority; production jobs ≥ 8; test jobs ≤ 4 |
| `TIME=(mm,ss)` | CPU time limit — always set to prevent runaway jobs |
| `REGION=0M` | Uses installation-defined maximum region; preferred over a hardcoded value |

### JES3 Job Classes

In JES3 environments, job class maps to a device group: `CLASS=D` for tape jobs, `CLASS=T` for test. Confirm with your JES3 JCLOPTs member for the local definition.

---

## VSAM — Access Patterns and IDCAMS

### VSAM Dataset Types

| Type | Key Structure | Access Pattern | Java Equivalent |
|------|-------------|---------------|----------------|
| KSDS (Key-Sequenced) | Variable-length key | Random + sequential by key | HashMap + sorted map |
| ESDS (Entry-Sequenced) | RBA (byte offset) | Sequential append; random by RBA | Append-only log / sequential file |
| RRDS (Relative Record) | Relative record number | Direct by slot number | Array or DB table with surrogate key |

### IDCAMS Commands

```jcl
//DEFVSAM  EXEC PGM=IDCAMS
//SYSPRINT DD   SYSOUT=*
//SYSIN    DD   *
  DEFINE CLUSTER ( -
    NAME(PROD.CUSTOMER.KSDS) -
    INDEXED -
    KEYS(10 0) -
    RECORDSIZE(200 500) -
    FREESPACE(20 10) -
    SHAREOPTIONS(2 3) -
    CYLINDERS(100 20) -
    VOLUMES(PROD01) ) -
  DATA ( NAME(PROD.CUSTOMER.KSDS.DATA) ) -
  INDEX ( NAME(PROD.CUSTOMER.KSDS.INDEX) )
/*
```

### COBOL VSAM REWRITE Rules

```cobol
* READ for UPDATE before REWRITE — mandatory
       READ CUSTFILE INTO WS-CUSTOMER-RECORD
           KEY IS WS-CUST-ID
           INVALID KEY MOVE 4 TO WS-RETURN-CODE
           NOT INVALID KEY
               PERFORM 3000-UPDATE-RECORD
       END-READ.

       3000-UPDATE-RECORD.
      * Must REWRITE immediately after READ with UPDATE — no intervening I/O on same file
           MOVE WS-NEW-BALANCE TO WS-CUST-BALANCE
           REWRITE CUSTREC FROM WS-CUSTOMER-RECORD
               INVALID KEY MOVE 8 TO WS-RETURN-CODE
           END-REWRITE.
```

Never issue `READ ... UPDATE` without a subsequent `REWRITE` or `UNLOCK`. An un-unlocked VSAM record holds a lock for the duration of the task — this causes ENQ conflicts on shared files.

---

## IMS DB — Hierarchical Data Model

### PCB/PSB/DBD Concepts

| Component | Purpose | Analogy |
|-----------|---------|---------|
| DBD (Database Definition) | Defines physical segment types and hierarchical relationships | Schema/DDL |
| PCB (Program Communication Block) | One PCB per database accessed; defines segment access intent (PROCOPT) | JDBC Connection with permissions |
| PSB (Program Specification Block) | Collection of PCBs for one application program | Spring Bean with multiple DataSource references |

### PROCOPT Values

| PROCOPT | Access | Use |
|---------|--------|-----|
| `G` | Get only (read) | Read-only programs |
| `GU` | Get Unique | Random read by key |
| `GN` | Get Next | Sequential read |
| `I` | Insert | Insert only |
| `D` | Delete | Delete only |
| `R` | Replace (update) | Update only |
| `A` | All | Full CRUD — use only when necessary |

### IMS DL/I Call Pattern (COBOL)

```cobol
       WORKING-STORAGE SECTION.
           EXEC DLI SCHD PSB(CUSTPSB) END-EXEC.

       01 CUST-SSA.
          05 SSA-SEGNAME    PIC X(8)  VALUE 'CUSTSEG '.
          05 SSA-BEGIN-PAREN PIC X    VALUE '('.
          05 SSA-FIELD      PIC X(8)  VALUE 'CUSTID  '.
          05 SSA-OPERATOR   PIC X(2)  VALUE '= '.
          05 SSA-VALUE      PIC X(10) VALUE SPACES.
          05 SSA-END-PAREN  PIC X    VALUE ')'.

       2000-GET-CUSTOMER.
           MOVE WS-CUST-ID TO SSA-VALUE
           EXEC DLI GU SEGMENT(CUSTSEG) INTO(WS-CUST-RECORD)
               WHERE CUSTID = :SSA-VALUE
           END-EXEC
           IF DIBSTAT = 'GE'
               MOVE 4 TO WS-RETURN-CODE
           END-IF.
```

---

## IMS DC — Message Processing

| Program Type | Trigger | Use Case |
|-------------|---------|---------|
| MPP (Message Processing Program) | IMS transaction code | Interactive online transaction |
| BMP (Batch Message Processing) | Scheduled; can access IMS DB | Batch update with IMS DB access |
| IFP (IMS Fast Path) | High-speed DEDB transactions | Ultra-high volume (> 10K TPS) |

### MPP Transaction Flow

1. Terminal input → IMS TM → Input queue → MPP scheduled in IMS region
2. MPP issues `GU IOPCB` to get message from queue
3. MPP processes; issues `ISRT IOPCB` to send response back
4. IMS TM routes response to terminal

```cobol
       2000-GET-INPUT.
           EXEC DLI GU USING PCB(IOPCB)
               SEGMENT(INMSEG) INTO(WS-INPUT-MSG)
           END-EXEC.
           IF IOAREAL(1:2) = 'QC'
               EXEC DLI CHKP USING PCB(IOPCB) END-EXEC
               STOP RUN
           END-IF.
```

---

## IBM MQ Series

### Key Concepts

| Concept | Description |
|---------|------------|
| Queue Manager | MQ server instance; name convention: `QM.{ENV}.{LOCATION}` (e.g., `QM.PROD.LONDON`) |
| Local Queue | Queue owned by this queue manager; prefix `QL.` |
| Remote Queue Definition | Pointer to queue on another QM; prefix `QR.` |
| Transmission Queue | Holds messages in transit; prefix `QT.` |
| Dead Letter Queue | Undeliverable messages; every QM must have one named `DLQ.{QMGR}` |
| Channel | Communication path between queue managers; `TO.{TARGET-QMGR}` |

### Message Persistence

```
MQMD.Persistence = MQPER_PERSISTENT (1)    -- Survives queue manager restart; use for financial messages
MQMD.Persistence = MQPER_NOT_PERSISTENT (0) -- Lost on restart; use for audit/log-only messages
```

Always use `MQPER_PERSISTENT` for messages that represent financial transactions, order state changes, or audit events.

### MQ + CICS Bridge Pattern (COBOL)

```cobol
      * Put message to MQ from CICS
           EXEC CICS PUT CONTAINER('MQMSG')
               FROM(WS-MQ-PAYLOAD)
               FLENGTH(WS-PAYLOAD-LEN)
               CHANNEL('MQCHANNEL')
           END-EXEC.

           EXEC CICS LINK PROGRAM('CKTI')
               CHANNEL('MQCHANNEL')
               RESP(WS-CICS-RESP)
           END-EXEC.
```

For new development, prefer the MQ CICS bridge (`CKTI`) over direct `MQPUT` within CICS to maintain unit-of-work consistency.

---

## z/OS Batch Tuning

### SMF Records for Batch Analysis

| SMF Record Type | Content | Use |
|----------------|---------|-----|
| Type 30 | Job/step accounting (CPU, I/O, elapsed time) | Identify slow steps |
| Type 42 | VSAM statistics | VSAM buffer tuning |
| Type 14/15 | Dataset open/close | Identify excessive dataset allocations |

```jcl
//SMFPRINT EXEC PGM=IFASMFDP
//SMFIN    DD   DSN=SYS1.MAN1,DISP=SHR
//SMFOUT   DD   DSN=&&SMFWORK,DISP=(NEW,PASS),SPACE=(CYL,(10,5))
//SYSIN    DD   *
  INDD(SMFIN,OPTIONS(DUMP))
  OUTDD(SMFOUT,TYPE(30))
  DATE(2024001,2024365)
/*
```

### Checkpoint/Restart with SYSCHK DD

```jcl
//BATCHJOB JOB (ACCT),'LONG RUNNING',CLASS=C
//STEP1    EXEC PGM=LONGPROG,PARM='RESTART'
//SYSCHK   DD   DSN=PROD.CHECKPOINT.DATA,
//             DISP=(MOD,CATLG,KEEP),
//             SPACE=(CYL,(1,1)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=0)
//CHECKPT  DD   SYSOUT=*
```

In COBOL: use `RERUN ON SYSCHK EVERY 1000 RECORDS OF filename` in `ENVIRONMENT DIVISION` for checkpoint insertion.

### JES Spool Management

```jcl
/* Limit SYSOUT — critical for high-volume batch */
//SYSPRINT DD   SYSOUT=*,FREE=CLOSE
//SYSOUT   DD   SYSOUT=(X,,9999)  /* Limit to 9999 lines */

/* Route SYSOUT to specific class for archival */
//AUDITOUT DD   SYSOUT=A,DEST=ARCHIVER
```

---

## SORT Utility — DFSORT / SYNCSORT

```jcl
//SORTSTEP EXEC PGM=SORT
//SYSOUT   DD   SYSOUT=*
//SORTIN   DD   DSN=INPUT.DATASET,DISP=SHR
//SORTOUT  DD   DSN=OUTPUT.SORTED,DISP=(NEW,CATLG,DELETE),
//             SPACE=(CYL,(10,5),RLSE),
//             DCB=(RECFM=FB,LRECL=100,BLKSIZE=0)
//SYSIN    DD   *
  SORT FIELDS=(1,10,CH,A,21,8,ZD,D)
  INCLUDE COND=(51,2,CH,EQ,C'GB')
  OUTREC FIELDS=(1,10,21,8,51,2,C'PROCESSED')
  SUM FIELDS=(31,10,ZD)
/*
```

| Parameter | Meaning |
|-----------|---------|
| `FIELDS=(pos,len,fmt,dir)` | Sort key: position, length, format (`CH`=char, `ZD`=zoned decimal, `PD`=packed), direction (`A`/`D`) |
| `INCLUDE COND=` | Filter records before sort |
| `OUTREC FIELDS=` | Reformat output records |
| `SUM FIELDS=` | Aggregate numeric fields with matching keys |
| `OPTION EQUALS` | Preserve original order for equal keys |

---

## RACF Security

### Dataset Security

```
/* Protect a new production dataset */
ADDSD 'PROD.CUSTOMER.DATA.**' UACC(NONE) OWNER(PRODOWNR)
PERMIT 'PROD.CUSTOMER.DATA.**' ID(PRODGRP) ACCESS(UPDATE)
PERMIT 'PROD.CUSTOMER.DATA.**' ID(AUDITGRP) ACCESS(READ)
PERMIT 'PROD.CUSTOMER.DATA.**' ID(BATCH01) ACCESS(ALTER)

/* RACF audit — log all access attempts */
ALTDSD 'PROD.CUSTOMER.DATA.**' AUDIT(ALL(READ))
```

### CICS Transaction Security

```
/* Define CICS transaction in RACF */
RDEFINE TCICSTRN CUSTINQ UACC(NONE)
PERMIT CUSTINQ CLASS(TCICSTRN) ID(CICSTELR) ACCESS(READ)
SETROPTS RACLIST(TCICSTRN) REFRESH
```

All production CICS transactions must be defined in RACF class `TCICSTRN` with `UACC(NONE)`. Access only via named RACF groups — never via individual user IDs for transaction authorization.

---

## CICS Transaction Naming and Resource Definition

### Transaction Naming Convention

| Prefix | Usage |
|--------|-------|
| `C` + 3 chars | Customer-facing transactions (e.g., `CINQ`, `CUPD`) |
| `B` + 3 chars | Batch-triggered CICS transactions |
| `A` + 3 chars | Administration/operational transactions |
| `Z` + 3 chars | Technical/infrastructure transactions (exclude from user menus) |

### CSD Resource Definition (DFHCSDUP)

```
DEFINE TRANSACTION(CINQ)
       PROGRAM(CUSTINQ)
       TWASIZE(256)
       TASKDATALOC(ANY)
       TASKDATAKEY(USER)
       STORAGECLEAR(NO)
       RUNAWAY(5000)
       SHUTDOWN(DISABLED)
       STATUS(ENABLED)
       DTIMEOUT(30)
       GROUP(CUSTGRP)

DEFINE PROGRAM(CUSTINQ)
       LANGUAGE(COBOL)
       DATALOCATION(ANY)
       EXECKEY(USER)
       STATUS(ENABLED)
       GROUP(CUSTGRP)
```

- `RUNAWAY`: CPU time limit in milliseconds — always set; prevents runaway transactions consuming CPU
- `DTIMEOUT`: Deadlock timeout in seconds — always set for transactions accessing shared resources
- `TASKDATAKEY(USER)`: Prevents task data from being in CICS key storage — required for all application transactions
