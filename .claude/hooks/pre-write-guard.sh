#!/usr/bin/env bash
# Pre-tool hook: guards against writes to protected or sensitive paths.
# Called by Claude Code before Write/Edit/MultiEdit tool execution.
# Exit 2 = block; Exit 0 = allow.

set -euo pipefail

INPUT=$(cat)

# Extract file path from JSON
FILE_PATH=""
if command -v python3 &>/dev/null; then
  FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
path = (data.get('input', {}).get('file_path', '') or
        data.get('file_path', '') or
        data.get('path', ''))
print(path)
" 2>/dev/null || true)
fi

if [ -z "$FILE_PATH" ]; then
  FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]*' | head -1 || true)
fi

[ -z "$FILE_PATH" ] && exit 0

# ─── BLOCK: System paths ──────────────────────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '^(/etc/|/usr/|/bin/|/sbin/|~/.ssh/)'; then
  echo "BLOCKED: Writing to system paths is not allowed." >&2
  exit 2
fi

# ─── BLOCK: Private key and certificate files ─────────────────────────────────
if echo "$FILE_PATH" | grep -qE '\.(pem|key|p12|pfx)$'; then
  echo "BLOCKED: Do not write private keys or certificates to the repository." >&2
  exit 2
fi

# ─── BLOCK: Production environment files ──────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '\.env\.(production|prod)$'; then
  echo "BLOCKED: Production environment files must not be written by automation." >&2
  exit 2
fi

# ─── WARN: Dependency manifests ───────────────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '(pom\.xml|package\.json|build\.gradle)$'; then
  echo "WARNING: Modifying dependency manifest — review all changes carefully before committing." >&2
fi

# ─── WARN: CI/CD pipeline files ───────────────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '\.github/workflows/.*\.ya?ml$'; then
  echo "WARNING: Modifying CI/CD workflow — test in a branch before merging to main." >&2
fi

exit 0
