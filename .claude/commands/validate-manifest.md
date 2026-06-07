# /validate-manifest — Validate a Project Manifest

Validate a `project-manifest.yaml` against the EEIK manifest schema, check for incompatible combinations, verify governance rules, and produce a readiness report.

## Usage

```
/validate-manifest
/validate-manifest path/to/project-manifest.yaml
```

If no path is given, defaults to `project-manifest.yaml` in the current directory.

---

## What This Command Does

1. Reads the manifest file
2. Checks all required fields are present
3. Validates all values against allowed enums in `bootstrap/schemas/manifest-schema.json`
4. Applies governance rules (regulated domain → regulated+ profile)
5. Checks for known incompatible combinations
6. Checks for missing capability packs (📋 planned packs that are selected)
7. Produces a readiness report with PASS / WARN / FAIL per check

---

## Validation Checks

### Required Fields

Check each required field is present and non-empty:

| Field | Required |
|-------|----------|
| `schema_version` | ✅ Yes |
| `project.name` | ✅ Yes |
| `project.domain` | ✅ Yes |
| `project.project_type` | ✅ Yes |
| `technology.backend.language` | ✅ Yes |
| `architecture.style` | ✅ Yes |
| `cloud.provider` | ✅ Yes |
| `governance.profile` | ✅ Yes |
| `delivery.model` | ✅ Yes |

---

### Enum Validation

Validate each field value is in the allowed set from `bootstrap/schemas/manifest-schema.json`. Key fields:

| Field | Allowed Values |
|-------|---------------|
| `project.domain` | insurance, banking, healthcare, retail, generic |
| `project.project_type` | greenfield, modernization, poc, mvp, enterprise-platform, agent-platform |
| `technology.backend.language` | java, python, mixed |
| `technology.frontend.framework` | react, angular, none |
| `architecture.style` | monolith, modular-monolith, microservices, event-driven, serverless, agentic |
| `cloud.provider` | aws, azure, gcp, hybrid |
| `cloud.infra_as_code` | cdk, terraform, both, none |
| `ai.pattern` | rag, single-agent, multi-agent, enterprise-agent-platform, none |
| `ai.framework` | langgraph, crewai, autogen, mcp, bedrock-agents, none |
| `governance.profile` | basic, standard, regulated, enterprise |
| `delivery.model` | single-team, multi-team, enterprise-program |
| `modernization.source_platform` | ibmi, rpg, cobol, mainframe, oracle-forms, vb6, mixed, none |
| `modernization.strategy` | strangler-fig, rewrite, lift-and-shift, encapsulate, hybrid |

---

### Governance Rules

Apply these rules in order:

```
RULE 1: Regulated domain governance
  IF project.domain IN [insurance, banking, healthcare]
  AND governance.profile IN [basic, standard]
  THEN → FAIL: "Domain '{domain}' requires governance profile 'regulated' or 'enterprise'. Found: '{profile}'"

RULE 2: AI governance for multi-agent systems
  IF ai.pattern IN [multi-agent, enterprise-agent-platform]
  AND ai.governance_required != true
  THEN → WARN: "Multi-agent AI patterns should set ai.governance_required: true"

RULE 3: SLO requirement for regulated governance
  IF governance.profile IN [regulated, enterprise]
  AND observability.slo_required != true
  THEN → WARN: "Regulated/enterprise governance should define SLOs. Set observability.slo_required: true"

RULE 4: AI enabled but no framework
  IF ai.enabled = true
  AND ai.framework is missing or null
  THEN → WARN: "ai.enabled is true but no ai.framework is specified"
```

---

### Incompatible Combination Checks

```
COMBINATION 1: Serverless + Mainframe modernization
  IF architecture.style = serverless
  AND modernization.source_platform IN [cobol, mainframe]
  THEN → WARN: "Serverless architecture is unusual for mainframe modernization. Confirm this is intentional."

COMBINATION 2: Monolith + Multi-team delivery
  IF architecture.style = monolith
  AND delivery.model = enterprise-program
  THEN → WARN: "Monolith architecture with enterprise-program delivery creates coordination risk. Consider modular-monolith."

COMBINATION 3: PoC + Enterprise governance
  IF project.project_type = poc
  AND governance.profile = enterprise
  THEN → WARN: "Enterprise governance on a PoC may slow exploration. Consider 'standard' unless required by policy."

COMBINATION 4: Agent platform without AI
  IF project.project_type = agent-platform
  AND (ai.enabled = false OR ai.pattern = none)
  THEN → FAIL: "project_type 'agent-platform' requires ai.enabled: true"
```

---

### Capability Pack Availability

Check each resolved pack against `bootstrap/resolvers/capability-matrix.yaml`.

For each selected pack:
- ✅ `built` → pack exists and has content
- 🔧 `stub` → pack structure exists, content is minimal
- 📋 `planned` → pack is on roadmap but does not exist yet

Report any `📋 planned` packs as WARN: "Pack '{name}' is selected but not yet built. It will not contribute standards/agents until implemented."

---

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EEIK Manifest Validation Report
  File: project-manifest.yaml
  Schema: 1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Required Fields         {PASS|FAIL}
  Enum Validation         {PASS|FAIL}
  Governance Rules        {PASS|WARN|FAIL}
  Combination Checks      {PASS|WARN}
  Pack Availability       {PASS|WARN}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FAILURES (must fix before proceeding):
  {list each FAIL with field, found value, expected values}

  WARNINGS (review recommended):
  {list each WARN with explanation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Overall: READY TO PROCEED | NEEDS FIXES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Result Codes

| Result | Meaning |
|--------|---------|
| `PASS` | Check passed with no issues |
| `WARN` | Non-blocking issue — review recommended but won't block generation |
| `FAIL` | Blocking issue — manifest must be corrected before proceeding |

If any FAIL exists → overall result is `NEEDS FIXES`.
If only WARN exists → overall result is `READY TO PROCEED (with warnings)`.
If all PASS → overall result is `READY TO PROCEED`.

---

## After Validation

If manifest is valid, suggest next steps:

```
Next steps:
  /estimate "first feature"    → estimate effort
  /adr "first decision"        → record architecture decisions
  /memory-update "project bootstrapped with EEIK manifest"
```
