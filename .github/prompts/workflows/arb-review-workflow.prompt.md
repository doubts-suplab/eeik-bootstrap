# ARB Review Workflow

Conduct a formal Architecture Review Board gate review for the following proposal.

**Proposal:** $PROPOSAL_NAME
**Type:** New Service / Major Feature / Technology Change / API Contract

## Workflow Steps

### Step 1 — Submission Intake
Collect the following before starting the review:
- [ ] ADR or design document reference
- [ ] Bounded context and domain
- [ ] Non-functional requirements (throughput, latency, availability)
- [ ] Technology choices (with justification)
- [ ] Integration points (upstream callers, downstream dependencies)
- [ ] Data classification of information handled

### Step 2 — Standards Compliance Check
Review against enterprise standards:
- [ ] Technology is on the approved list
- [ ] Security architecture follows standards in `.github/instructions/architecture-governance.instructions.md`
- [ ] Data handling complies with privacy and retention policies
- [ ] API design follows REST maturity and versioning standards

### Step 3 — Architectural Review
Activate the `arb-reviewer` agent for structured review across all dimensions:
- Strategic fit, technology standards, security, scalability, operability, data, dependencies

### Step 4 — Produce Recommendation Report
Output the formal ARB Recommendation Report:
- **APPROVED** — proceed to build
- **APPROVED WITH CONDITIONS** — proceed with specific remediations
- **REJECTED** — cannot proceed; redesign required

### Step 5 — Track Conditions
If approved with conditions:
- [ ] List each required condition with owner and target date
- [ ] Schedule follow-up ARB checkpoint before go-live
- [ ] Record conditions in `.claude/memory/decisions.md`

## Output

Formal ARB Recommendation Report following the template in `.claude/agents/arb-reviewer.md`
