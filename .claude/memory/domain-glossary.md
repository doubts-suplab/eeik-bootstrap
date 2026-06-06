# Domain Glossary

> **Bootstrap Template** — Replace with terms specific to your project's business domain.
> Keep definitions precise and unambiguous — the same word often means different things in different bounded contexts.

---

## How to Use This Glossary

When Claude Code encounters a business term, it checks this glossary for the project-specific definition. This prevents the agent from applying generic or incorrect meanings to domain-specific vocabulary.

When adding a term:
1. Use the **exact spelling** used in code, database schemas, and stakeholder documents
2. Note which bounded context owns the term if it varies across contexts
3. Note what the term explicitly does NOT mean in this domain

---

## Terms

<!-- TODO: Replace these examples with your project's actual domain terms -->

### Example Terms (delete and replace)

**Order**
> A confirmed request by a Customer to purchase one or more Products. An Order is created only after payment authorisation succeeds. An Order is NOT a Basket (which is pre-payment).
> *Bounded context: Order Management*

**Customer**
> A registered user who has completed identity verification. A Guest (unregistered shopper) is NOT a Customer in this system.
> *Bounded context: Identity*

**Fulfilment**
> The process of picking, packing, and dispatching an Order. Fulfilment begins only after an Order reaches `CONFIRMED` status.
> *Bounded context: Warehouse*

---

## Bounded Context Map

<!-- TODO: List your bounded contexts and their responsibilities -->

| Bounded Context | Responsibility | Owns |
|----------------|---------------|------|
| <!-- TODO --> | <!-- brief --> | <!-- entities --> |

---

## Ubiquitous Language Rules

<!-- TODO: List terms where usage must be consistent across code, docs, and conversation -->

- Always say **Order**, never "request" or "booking"
- Always say **Customer**, never "user" or "client" in business logic
- Always say **Fulfilment**, never "shipping" or "dispatch" in service names

<!-- Replace with your project's actual ubiquitous language rules -->
