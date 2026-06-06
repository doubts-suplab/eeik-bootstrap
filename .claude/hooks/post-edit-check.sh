#!/usr/bin/env bash
# Post-tool hook: runs quick quality checks after file edits.
# Called by Claude Code after Write/Edit/MultiEdit tool execution.
# Always exits 0 — this hook warns but never blocks.

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
[ ! -f "$FILE_PATH" ] && exit 0

# ─── Java files ───────────────────────────────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '\.java$'; then
  if grep -n 'System\.out\.print' "$FILE_PATH" 2>/dev/null | head -3; then
    echo "WARNING: System.out.println detected in $FILE_PATH — use SLF4J logger instead." >&2
  fi
  if grep -n '@Autowired' "$FILE_PATH" 2>/dev/null | grep -v '//' | head -3; then
    echo "WARNING: @Autowired field injection in $FILE_PATH — use constructor injection." >&2
  fi
  if grep -n 'import javax\.' "$FILE_PATH" 2>/dev/null | head -3; then
    echo "WARNING: javax.* import in $FILE_PATH — Spring Boot 3.x uses jakarta.* exclusively." >&2
  fi
fi

# ─── TypeScript files (non-test) ──────────────────────────────────────────────
if echo "$FILE_PATH" | grep -qE '\.ts$' && ! echo "$FILE_PATH" | grep -qE '\.(spec|test)\.ts$'; then
  if grep -n 'console\.log' "$FILE_PATH" 2>/dev/null | head -3; then
    echo "WARNING: console.log in $FILE_PATH — remove before merging to main." >&2
  fi
fi

# ─── Any file: potential credential patterns ──────────────────────────────────
if grep -nE '(AKIA[0-9A-Z]{16}|aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40})' "$FILE_PATH" 2>/dev/null | head -3; then
  echo "WARNING: Potential AWS credentials detected in $FILE_PATH — use Secrets Manager." >&2
fi

exit 0
