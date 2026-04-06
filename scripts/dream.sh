#!/bin/bash
# dream.sh — KYROS memory consolidation
# Run weekly or when memory feels messy
# Usage: bash scripts/dream.sh

PROJECT="$HOME/Desktop/my-project"
MEMORY="$PROJECT/memory/MEMORY.md"
LOGS="$PROJECT/logs"
DATE=$(date +%Y-%m-%d)

echo "=== KYROS Dream Mode ==="
echo "Consolidating memory..."

# Count log files
LOG_COUNT=$(ls "$LOGS"/*.md 2>/dev/null | wc -l)
echo "Found $LOG_COUNT session logs"

# Trim MEMORY.md if over 180 lines
LINE_COUNT=$(wc -l < "$MEMORY")
if [ "$LINE_COUNT" -gt 180 ]; then
  echo "MEMORY.md is $LINE_COUNT lines — needs cleanup. Open it and trim old entries."
else
  echo "MEMORY.md is $LINE_COUNT lines — looks good."
fi

# Show recent logs
echo ""
echo "Recent sessions:"
ls -t "$LOGS"/*.md 2>/dev/null | head -5 | while read f; do
  echo "  - $(basename $f)"
done

echo ""
echo "Dream complete. Review memory/MEMORY.md and trim anything stale."
echo "Then: git add . && git commit -m 'dream: memory consolidation $DATE' && git push"
