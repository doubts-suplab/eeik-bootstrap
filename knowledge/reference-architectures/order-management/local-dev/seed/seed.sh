#!/usr/bin/env bash
# Re-apply the Order Management seed data to the local Postgres (schema is applied on first boot).
# Usage: ./seed.sh    (run from local-dev/, after `docker compose up -d`)
set -euo pipefail

DB_URL="${DB_URL:-postgres://orders:orders_dev@localhost:5432/orders}"
here="$(cd "$(dirname "$0")" && pwd)"

echo "Applying schema + seed to ${DB_URL} ..."
psql "${DB_URL}" -v ON_ERROR_STOP=1 -f "${here}/schema.sql"
psql "${DB_URL}" -v ON_ERROR_STOP=1 -f "${here}/seed.sql"
echo "Done. 3 orders + outbox events loaded."
