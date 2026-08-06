-- Multi-Tenant SaaS — two tenants with overlapping data so isolation is demonstrable.

INSERT INTO tenants (id, name, plan) VALUES
  ('7e000000-0000-0000-0000-0000000000a1', 'Acme Corp',   'enterprise'),
  ('7e000000-0000-0000-0000-0000000000b2', 'Globex Ltd',  'standard')
ON CONFLICT (id) DO NOTHING;

INSERT INTO projects (id, tenant_id, name) VALUES
  ('11110000-0000-0000-0000-000000000001', '7e000000-0000-0000-0000-0000000000a1', 'Acme — Billing Revamp'),
  ('11110000-0000-0000-0000-000000000002', '7e000000-0000-0000-0000-0000000000a1', 'Acme — Mobile App'),
  ('22220000-0000-0000-0000-000000000001', '7e000000-0000-0000-0000-0000000000b2', 'Globex — Data Lake')
ON CONFLICT (id) DO NOTHING;

INSERT INTO usage_events (tenant_id, metric, quantity) VALUES
  ('7e000000-0000-0000-0000-0000000000a1', 'api_calls', 12000),
  ('7e000000-0000-0000-0000-0000000000a1', 'agent_runs',  340),
  ('7e000000-0000-0000-0000-0000000000b2', 'api_calls',  3000);
