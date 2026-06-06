# IBM i to Cloud Migration Workflow

Migrate the following IBM i workload to a cloud-native architecture on AWS.

**IBM i System / Application:** $SYSTEM_NAME
**Target Architecture:** Spring Boot on ECS Fargate / Lambda / other

## Workflow Steps

### Step 1 — Discovery & Assessment
Activate the `ibmi-modernization-expert` agent to:
- [ ] Inventory all RPG, CL, and COBOL programs in scope
- [ ] Map DB2 for i physical files to relational tables
- [ ] Identify program call chains and external dependencies
- [ ] Classify programs: re-host / re-platform / re-architect / retire
- [ ] Estimate migration effort per program

### Step 2 — Architecture Design
Activate the `architect` agent to design the target state:
- [ ] Define Java service boundaries from the IBM i program structure
- [ ] Design data migration from DB2 for i to PostgreSQL / Aurora
- [ ] Design API facades for calling new Java services from remaining IBM i code
- [ ] Define the coexistence strategy: how old and new run simultaneously

### Step 3 — Phased Migration Plan
Produce the migration phase plan:
- [ ] Phase 1: Strangler-fig API facade (IBM i calls new Java APIs)
- [ ] Phase 2: Migrate read paths (new Java services serve queries)
- [ ] Phase 3: Migrate write paths (new Java services own the data)
- [ ] Phase 4: Decommission IBM i programs one by one after cutover verification

### Step 4 — Data Migration Design
Activate the `aws-architect` agent for:
- [ ] Schema translation: DB2 for i → PostgreSQL / Aurora schema
- [ ] Data type mapping (packed decimal, zoned, dates)
- [ ] Initial data load strategy (DMS, custom ETL, or batch extract)
- [ ] Ongoing sync strategy during parallel running period

### Step 5 — Implementation
- Java services: `java-developer` agent
- AWS infrastructure: `cdk-terraform-helper` agent
- Integration tests: `java-tester` agent

### Step 6 — Cutover Planning
- [ ] Define go/no-go criteria for each cutover phase
- [ ] Produce rollback plan for each phase
- [ ] Schedule parallel running period and validation tests
- [ ] Confirm IBM i decommission timeline

## Output

Migration assessment, phased plan, target architecture design, and cutover checklist.
