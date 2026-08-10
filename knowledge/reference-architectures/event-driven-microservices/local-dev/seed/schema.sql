-- Minimal per-service write store + transactional outbox for the Event-Driven Microservices arch.
-- A service persists its state change AND the outbox row in ONE transaction (no dual-write); a
-- relay/CDC process then publishes committed outbox rows to Kafka and marks them published.

CREATE TABLE IF NOT EXISTS orders (
    id            UUID PRIMARY KEY,
    customer_id   UUID NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('PLACED','CONFIRMED','CANCELLED')),
    total_minor   BIGINT NOT NULL,
    currency      CHAR(3) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Transactional outbox: written in the same tx as the state change above.
CREATE TABLE IF NOT EXISTS outbox (
    id            UUID PRIMARY KEY,
    aggregate_id  UUID NOT NULL,
    event_type    TEXT NOT NULL,
    payload       JSONB NOT NULL,
    occurred_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at  TIMESTAMPTZ            -- NULL until the relay publishes it to Kafka
);

CREATE INDEX IF NOT EXISTS idx_outbox_unpublished ON outbox (occurred_at) WHERE published_at IS NULL;

-- Consumer-side idempotency: dedupe by event id (at-least-once delivery is assumed).
CREATE TABLE IF NOT EXISTS processed_events (
    event_id      UUID PRIMARY KEY,
    processed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
