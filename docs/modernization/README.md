# Modernization

Legacy system transformation guidance: IBM i, COBOL, legacy Spring, and mainframe migration.

---

## Contents

| Document | Covers |
|----------|--------|
| [ibmi-modernization.md](ibmi-modernization.md) | IBM i (AS/400) RPG and CL to Java migration |

---

## What This Section Covers

EEIK includes a dedicated modernization intelligence layer for the most common enterprise legacy transformation programs. This section covers strategy, patterns, playbooks, and tooling for each legacy platform.

### Supported Legacy Platforms

| Platform | Languages | EEIK Support |
|----------|-----------|-------------|
| IBM i (AS/400) | RPG IV, RPGLE, CL, DDS, DB2 for i | `ibmi-modernization-expert` agent + `ibmi-pack` |
| IBM Mainframe | COBOL 6.x, JCL, CICS, DB2 z/OS, HLASM | `modernization-expert` agent + mainframe standards |
| Legacy Spring | Spring 4.x/5.x, `javax.*`, JUnit 4 | Spring Boot 3.x migration guide |

### Modernization Approach

EEIK modernization programs follow the **Strangler Fig** pattern by default:

```
Legacy System
      │
      ├── Identify bounded contexts
      ├── Route new traffic to new services
      ├── Replicate read paths in new system
      ├── Migrate write paths incrementally
      └── Decommission legacy components
```

The `strangler-pattern` reference architecture in `knowledge/reference-architectures/` documents this in detail.

### Key Agents

| Agent | Role |
|-------|------|
| `ibmi-modernization-expert` | Analyse RPG IV / RPGLE / CL programs, map to Java |
| `modernization-expert` | COBOL-to-Java, legacy Spring upgrades, monolith decomposition |
| `architect` | Target state architecture, migration wave planning |
| `java-developer` | Implement the replacement Java services |

### Modernization Workflow

Use the orchestrated workflow:

```
#file:.github/prompts/workflows/ibmi-to-cloud-workflow.prompt.md
```

or

```
#file:.github/prompts/workflows/cobol-to-java-workflow.prompt.md
```

Both workflows guide the full discovery → architecture → phased migration → cutover sequence.
