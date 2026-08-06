-- AI-Augmented Service — seed corpus for local dev / demos.
-- Two short documents chunked into retrievable passages. Embeddings are left NULL here; run the
-- service's ingestion job (or `POST /ingest`) to compute Titan embeddings against real Bedrock.

INSERT INTO documents (id, title, source_uri) VALUES
  ('d1111111-1111-1111-1111-111111111111', 'Refund Policy',      's3://docs/refund-policy.md'),
  ('d2222222-2222-2222-2222-222222222222', 'Shipping SLA',       's3://docs/shipping-sla.md')
ON CONFLICT (id) DO NOTHING;

INSERT INTO chunks (id, document_id, ordinal, content) VALUES
  ('c1111111-0000-0000-0000-000000000001', 'd1111111-1111-1111-1111-111111111111', 0,
   'Customers may request a refund within 30 days of delivery for unused items in original packaging.'),
  ('c1111111-0000-0000-0000-000000000002', 'd1111111-1111-1111-1111-111111111111', 1,
   'Refunds are issued to the original payment method within 5 business days of approval.'),
  ('c2222222-0000-0000-0000-000000000001', 'd2222222-2222-2222-2222-222222222222', 0,
   'Standard shipping is delivered within 3-5 business days; express within 1-2 business days.')
ON CONFLICT (id) DO NOTHING;
