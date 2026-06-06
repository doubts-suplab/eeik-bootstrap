#!/usr/bin/env bash
# Stop hook: appends a session summary to the session log.
# Runs automatically when Claude Code finishes a task.

set -euo pipefail

LOG_FILE=".claude/memory/session-log.md"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')

# Ensure log file exists with header
if [ ! -f "$LOG_FILE" ]; then
  printf '# Session Log\n\nAuto-updated by on-stop.sh. Most recent entry at top.\n\n' > "$LOG_FILE"
fi

# Capture changed files
CHANGED=$(git status --short 2>/dev/null | head -10 | sed 's/^/  /')
[ -z "$CHANGED" ] && CHANGED="  (no git changes this session)"

# Capture last commit message
LAST_COMMIT=$(git log --oneline -1 2>/dev/null || echo "  (no commits)")

# Prepend new entry (newest at top)
TMP=$(mktemp)
{
  printf '## %s\n\n**Last commit:** %s\n\n**Changed files:**\n```\n%s\n```\n\n' \
    "$TIMESTAMP" "$LAST_COMMIT" "$CHANGED"
  cat "$LOG_FILE"
} > "$TMP"

mv "$TMP" "$LOG_FILE"
exit 0
