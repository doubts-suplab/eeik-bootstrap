# Architecture Principles

**Pack:** architecture-pack | **Version:** 1.0

These principles apply to all systems built with EEIK. Agents read this file before producing architectural recommendations.

---

## 1. API First

Design and agree the API contract before implementation begins. Produce an OpenAPI 3 specification as the first deliverable of any new service. Never implement an API without a published contract.

**Why:** Contract-first enables parallel development, early consumer feedback, and prevents integration surprises.

## 2. Event-Driven Where Appropriate

Use asynchronous events for cross-bounded-context communication. Use synchronous REST/RPC only within a bounded context or for read-heavy queries where consistency is required immediately.

**Why:** Events decouple bounded contexts, enable resilience, and allow consumers to evolve independently.

**Decision rule:** Choose events when the producer does not need the result of processing. Choose synchronous calls when the caller needs an immediate response to continue.

## 3. Cloud Native

Design for horizontal scaling, stateless compute, and infrastructure immutability. Externalise configuration. Containerise all workloads. Use managed services over self-managed.

**Why:** Cloud-native design enables elastic scaling, reduced operational burden, and repeatable deployments.

## 4. Security by Design

Threat model every new service boundary. Apply least-privilege IAM at every layer. Never expose internal services directly to the internet. Encrypt data at rest and in transit. Never store secrets in code.

**Why:** Security retrofitted after design is expensive and incomplete.

## 5. Observability by Default

Every service ships with structured logging (SLF4J / CloudWatch), distributed tracing (X-Ray), and key business metrics. Define SLIs and SLOs before production deployment.

**Why:** Without observability, incidents become guesswork. Observability is not an afterthought.

## 6. Automate Everything

No manual deployment steps in staging or production. No manual schema changes. All infrastructure is code. All quality gates are automated.

**Why:** Manual steps introduce variation, human error, and invisible drift.

## 7. Reuse Before Build

Check for existing capability packs, shared services, and internal libraries before building new abstractions. Every new dependency added is a long-term maintenance liability.

**Why:** Duplication compounds over time. Reuse requires discipline up front but saves cost over the system's life.

## 8. Document Decisions

Every significant architectural decision is recorded as an ADR. An ADR is required for: technology choices, pattern selections, security trade-offs, and departures from these principles.

**Why:** Decisions made without documentation are forgotten, re-litigated, and repeatedly re-made at cost.

## 9. Bounded Context Integrity

Never share a database between two bounded contexts. Never call another context's repository directly. Communicate via APIs or events. Each context owns its data model.

**Why:** Shared databases couple contexts at the data layer, eliminating the ability to evolve them independently.

## 10. Fail Fast, Recover Gracefully

Design for failure from the start. Define circuit breakers, timeouts, and retry policies at every external call. Prefer letting requests fail fast over cascading failures.

**Why:** Distributed systems fail. The question is how gracefully.
