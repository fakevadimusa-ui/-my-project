#!/bin/bash
# session-log.sh — auto-called by Claude Code hook at session end
# Appends a timestamped entry to today's log file

PROJECT="$HOME/Desktop/my-project"
LOGS="$PROJECT/logs"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
LOG_FILE="$LOGS/$DATE.md"

mkdir -p "$LOGS"

# Create file with header if new day
if [ ! -f "$LOG_FILE" ]; then
  echo "# Session Log — $DATE" > "$LOG_FILE"
  echo "" >> "$LOG_FILE"
fi

# Append session entry
echo "## Session ended at $TIME" >> "$LOG_FILE"
echo "- Working dir: $(pwd)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Session logged to $LOG_FILE"
