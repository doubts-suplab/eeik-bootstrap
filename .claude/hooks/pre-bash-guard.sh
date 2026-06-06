#!/usr/bin/env bash
# Pre-tool hook: guards against destructive bash commands.
# Called by Claude Code before every Bash tool execution.
# Exit 2 = block; Exit 0 = allow.

set -euo pipefail

# Read JSON input from stdin
INPUT=$(cat)

# Extract command from JSON
CMD=""
if command -v python3 &>/dev/null; then
  CMD=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
cmd = data.get('input', {}).get('command', data.get('command', ''))
print(cmd)
" 2>/dev/null || true)
fi

# Fallback grep extraction
if [ -z "$CMD" ]; then
  CMD=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"\K[^"]*' | head -1 || true)
fi

[ -z "$CMD" ] && exit 0

# ─── BLOCK: Destructive git operations ────────────────────────────────────────
if echo "$CMD" | grep -qE 'git push\s+(--force|-f)'; then
  echo "BLOCKED: Force push is not allowed. Raise a PR instead." >&2
  exit 2
fi

if echo "$CMD" | grep -qE 'git reset\s+--hard'; then
  echo "BLOCKED: Hard reset discards uncommitted work. Use git stash or git restore." >&2
  exit 2
fi

# ─── BLOCK: Dangerous file system operations ──────────────────────────────────
if echo "$CMD" | grep -qE 'rm\s+-rf\s+(/|~|/home|/usr|/etc)(/|$)'; then
  echo "BLOCKED: Recursive deletion of system or home directories is not allowed." >&2
  exit 2
fi

# ─── BLOCK: Destructive database operations ───────────────────────────────────
if echo "$CMD" | grep -qiE '(DROP\s+DATABASE|DROP\s+SCHEMA|TRUNCATE\s+TABLE)'; then
  echo "BLOCKED: Destructive database operations require manual execution with explicit sign-off." >&2
  exit 2
fi

# ─── BLOCK: Infrastructure teardown ───────────────────────────────────────────
if echo "$CMD" | grep -qE 'cdk\s+destroy'; then
  echo "BLOCKED: CDK destroy requires manual execution from your terminal." >&2
  exit 2
fi

if echo "$CMD" | grep -qE 'aws\s+(ec2 terminate-instances|rds delete-db-instance|s3 rb --force)'; then
  echo "BLOCKED: Destructive AWS operations require manual execution." >&2
  exit 2
fi

# ─── WARN: Direct push to protected branches ──────────────────────────────────
if echo "$CMD" | grep -qE 'git push' && echo "$CMD" | grep -qE '\b(main|master|develop)\b'; then
  echo "WARNING: Pushing directly to a protected branch. Consider using a feature branch." >&2
fi

# ─── WARN: git clean ──────────────────────────────────────────────────────────
if echo "$CMD" | grep -qE 'git\s+clean'; then
  echo "WARNING: git clean will delete untracked files. Verify nothing important will be lost." >&2
fi

exit 0
