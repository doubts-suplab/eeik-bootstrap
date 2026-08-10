#!/bin/sh
# Create the checkpoint + audit tables in DynamoDB Local (idempotent).
set -eu
EP="http://dynamodb:8000"

create() {
  name="$1"; sort_key="$2"
  if aws dynamodb describe-table --table-name "$name" --endpoint-url "$EP" >/dev/null 2>&1; then
    echo "table $name already exists — skipping"
    return 0
  fi
  aws dynamodb create-table \
    --table-name "$name" \
    --attribute-definitions AttributeName=pk,AttributeType=S AttributeName="$sort_key",AttributeType=S \
    --key-schema AttributeName=pk,KeyType=HASH AttributeName="$sort_key",KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$EP" >/dev/null
  echo "created table $name"
}

create agent-platform-checkpoints checkpoint_id
create agent-platform-audit ts
echo "✓ tables ready"
