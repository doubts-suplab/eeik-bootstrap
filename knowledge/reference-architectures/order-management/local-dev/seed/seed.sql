-- Order Management — deterministic seed data for local dev / demos.
-- Three orders across the saga states so the read model and event flow have something to show.

INSERT INTO orders (id, customer_id, status, total_minor, currency) VALUES
  ('11111111-1111-1111-1111-111111111111', 'c0000000-0000-0000-0000-000000000001', 'PLACED',    4599, 'EUR'),
  ('22222222-2222-2222-2222-222222222222', 'c0000000-0000-0000-0000-000000000002', 'RESERVED', 12000, 'EUR'),
  ('33333333-3333-3333-3333-333333333333', 'c0000000-0000-0000-0000-000000000001', 'PAID',       999, 'EUR')
ON CONFLICT (id) DO NOTHING;

INSERT INTO order_lines (id, order_id, sku, quantity, unit_price_minor) VALUES
  ('a1000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'SKU-KEYBOARD', 1, 4599),
  ('a2000000-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'SKU-MONITOR',  2, 6000),
  ('a3000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 'SKU-CABLE',    1,  999)
ON CONFLICT (id) DO NOTHING;

-- Seed the outbox with the events each order would have emitted (published=false → relay picks up).
INSERT INTO outbox (aggregate_id, event_type, payload) VALUES
  ('11111111-1111-1111-1111-111111111111', 'OrderPlaced',   '{"orderId":"11111111-1111-1111-1111-111111111111","totalMinor":4599}'),
  ('22222222-2222-2222-2222-222222222222', 'StockReserved', '{"orderId":"22222222-2222-2222-2222-222222222222"}'),
  ('33333333-3333-3333-3333-333333333333', 'PaymentSettled','{"orderId":"33333333-3333-3333-3333-333333333333","amountMinor":999}');
