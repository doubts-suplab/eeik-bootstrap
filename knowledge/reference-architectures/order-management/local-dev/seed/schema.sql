-- Order Management — local schema (mirrors the Flyway V1 baseline).
-- Order aggregate + transactional outbox in one database, one transaction on write.

CREATE TABLE IF NOT EXISTS orders (
    id              UUID PRIMARY KEY,
    customer_id     UUID        NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'PLACED',   -- PLACED|RESERVED|PAID|CANCELLED
    total_minor     BIGINT      NOT NULL,                    -- amount in minor units (cents)
    currency        CHAR(3)     NOT NULL DEFAULT 'EUR',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_lines (
    id              UUID PRIMARY KEY,
    order_id        UUID        NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    sku             VARCHAR(64) NOT NULL,
    quantity        INT         NOT NULL CHECK (quantity > 0),
    unit_price_minor BIGINT     NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_order_lines_order ON order_lines(order_id);

-- Transactional outbox: events written in the same tx as the aggregate; a relay publishes to Kafka.
CREATE TABLE IF NOT EXISTS outbox (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aggregate_id    UUID        NOT NULL,
    event_type      VARCHAR(64) NOT NULL,
    payload         JSONB       NOT NULL,
    published       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished ON outbox(created_at) WHERE published = FALSE;
