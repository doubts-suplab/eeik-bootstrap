# Platform Engineering Standard

**Applies To:** Organisations running an internal developer platform (IDP) for many stream-aligned teams.
**Grounded in:** Team Topologies (platform-as-a-service to reduce cognitive load) and the
thinnest-viable-platform principle.

> The platform is a **product**. Developers are its customers. Success is measured by adoption and
> developer experience, not by how much you built or how many teams you can mandate onto it.

---

## Golden Rules (Platform Engineering)

| Rule | Implementation |
|---|---|
| The platform is a product | Roadmap, user research with dev teams, DevEx metrics — not a ticket queue |
| Pave the road, don't wall the garden | Golden path is the easy default; an escape hatch exists for real needs |
| Self-service by default | Provision a service/DB/queue via portal or CLI + guardrails, no ticket |
| Compliant by construction | Software templates bake in standards, observability, security from line 1 |
| Guardrails over gates | Policy-as-code + safe defaults beat approval queues that block flow |
| Thinnest viable platform | Start minimal; grow by demonstrated demand, not speculation |
| Reduce cognitive load | The platform absorbs the undifferentiated heavy lifting for stream teams |
| Adoption is earned | If teams route around it, fix the DevEx — don't mandate |

## The golden path

An opinionated, supported route from *new repo* to *running in production*:

```
software template → scaffold (repo, CI/CD, IaC)
        → standards + linters wired in     (compliant by construction)
        → observability (logs/metrics/traces) by default
        → security baseline (secrets, SBOM, scanning) by default
        → deploy to a paved environment     (self-service, guardrailed)
        → registered in the developer portal (ownership, docs, scorecard)
```

A developer starting a new service of this type should reach a deployed, observable, compliant service
in **minutes**, without learning the platform's internals.

## Developer portal (Backstage-style)

- **Software catalog** — every service, its owner, its docs, its dependencies, its scorecard.
- **Software templates** — generate a golden-path service; the template *is* the standard, executable.
- **Scorecards** — surface health (test coverage, on-call defined, runbook present) as nudges, not gates.
- **TechDocs** — docs live with the code and render in the portal.

## Measuring it (DevEx)

- **Lead time for change** and **time-to-first-deploy** for a new service.
- **Golden-path adoption rate** — share of new services created from templates.
- **Self-service ratio** — provisioning done without a platform-team ticket.
- **Developer satisfaction** — periodic survey; qualitative friction is a real signal.

## Anti-Patterns

| Anti-Pattern | Correct Alternative |
|---|---|
| Mandating the platform | Earn adoption through better DevEx; measure and fix friction |
| A walled garden (only path) | Paved road + documented escape hatch |
| Ticket-driven "self-service" | Real self-service via portal/CLI with guardrails |
| Big-bang platform build | Thinnest viable platform; grow by demand |
| Approval gates everywhere | Policy-as-code guardrails + safe defaults |
| Platform team as a bottleneck | Automate provisioning; the team builds capabilities, not tickets |

## Enforcement

- New service types ship with a **software template** — the golden path is executable, not a doc.
- Compliance is by construction (templates wire in standards/observability/security), verified by
  scorecards rather than manual review.
- The platform has a **product owner** and a roadmap driven by DevEx metrics + team research.
- The `platform-engineer` agent designs golden paths, self-service interfaces, and templates.
