#!/usr/bin/env bash
# Posts a resource + log snapshot to the CI monitor issue every 3 minutes.
# Usage: tools/ci_monitor.sh <logfile> <label> &
LOG="$1"; LABEL="$2"; ISSUE="${CFX_MONITOR_ISSUE:-1}"
cid=""
while true; do
  body="$(printf '%s run %s at %s UTC\n\n```\n%s\n%s\n%s\n--- top mem ---\n%s\n--- log tail ---\n%s\n```\n' \
    "$LABEL" "$GITHUB_RUN_ID" "$(date -u +%H:%M)" "$(df -h / /home/runner/src 2>/dev/null)" "$(free -m)" "$(uptime)" \
    "$(ps -eo rss,comm --sort=-rss | head -6)" "$(tail -n 25 "$LOG" 2>/dev/null | cut -c1-200)")"
  if [ -z "$cid" ]; then
    cid="$(gh api "repos/$GITHUB_REPOSITORY/issues/$ISSUE/comments" -f body="$body" -q .id 2>/dev/null)"
  else
    gh api -X PATCH "repos/$GITHUB_REPOSITORY/issues/comments/$cid" -f body="$body" >/dev/null 2>&1
  fi
  sleep 180
done
