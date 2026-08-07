# Retail & E-Commerce Standard

**Applies To:** Retail / e-commerce systems (catalog, checkout, order, inventory, fulfilment)
**Compliance:** PCI-DSS (payments) · GDPR (customer PII) · PSD2/SCA (EU card payments)

---

## Golden Rules (Retail)

| Rule | Implementation |
|---|---|
| Money is integer minor units + currency | Never floats; `amountMinor: 4599, currency: "EUR"` |
| Price captured at checkout is the price charged | Snapshot line prices into the order; ignore later catalog changes |
| Reserve inventory before confirming/charging | Availability = on-hand − reserved; release on timeout |
| Idempotent checkout & payment | Idempotency keys; a retry never creates a 2nd order or 2nd charge |
| Order state machine is explicit | Illegal transitions rejected; every transition emits a domain event |
| Never store card data | Tokenise via the provider; PAN/CVV never touch your systems (PCI-DSS) |
| Server-authoritative totals | Tax, shipping, and discounts computed server-side, never trusted from client |
| Bounded contexts, no cross-context joins | Catalog / Inventory / Order / Fulfilment integrate via events or APIs |

## Payments (PCI-DSS)

- Reduce scope: use the provider's hosted fields / iframe / redirect (Stripe Elements, Adyen Components).
  Your servers should never see the PAN or CVV.
- The **payment provider webhook is the source of truth** for settlement — verify its signature, and make
  the handler idempotent (dedupe on event ID).
- Support **3-D Secure / SCA** for EU card payments (PSD2); handle the challenge flow, don't fail it.
- Log payment *references and status*, never card data or full auth responses.

## Inventory & Availability

- `available = on_hand − reserved`. Checkout **reserves**; order confirmation **allocates**; cancellation
  or reservation timeout **releases**.
- Reservations expire (e.g. 15 min) to avoid stranded stock from abandoned carts.
- Omnichannel: reserve from a shared pool or a specific fulfilment node (store vs DC) — the order model
  is unchanged; only allocation differs.

## Data & Privacy (GDPR)

- Minimise customer PII; track consent; support export + deletion (right to erasure).
- Order/transaction retention has a documented lawful basis (tax/audit); PII beyond that is purged.
- Analytics/marketing data is consent-gated and separable from transactional data.

## Order Model (reference)

```
Order { id, customerId, status, currency, totalMinor, placedAt, idempotencyKey }
OrderLine { orderId, sku, quantity, unitPriceMinor, taxMinor }   // prices snapshotted at checkout
Payment { orderId, provider, providerRef, status, amountMinor }  // no card data
Reservation { sku, quantity, orderId, expiresAt }
```

## Resilience & Performance

- Cache catalog / product-list pages at the CDN (stale-while-revalidate); personalise at the edge.
- The checkout/payment path must degrade gracefully — never block it on reviews, recommendations, or
  analytics.
- Timeouts + bounded retries (idempotent only) on every payment/tax/shipping integration.

## Anti-Patterns (Reject in Review)

- Money as float; recomputing order totals from the live catalog post-checkout.
- Charging before reserving stock; confirming an order that could oversell.
- Storing PAN/CVV; trusting a payment webhook without signature verification.
- Client-computed totals/discounts trusted server-side.
- Cross-context DB joins (e.g. Order querying Catalog tables directly).
