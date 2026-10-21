#!/bin/bash
# Notify (macOS) when Claude finishes a turn and is ready for input.
# Wire to the `Stop` event. Shows the current project (working-dir basename).
# Stays quiet on turns where Claude is only waiting on background work
# (background commands, async agents, monitors, /loop wakeups) — see
# has_pending_background_work.py, which must sit next to this script.

read -r hook_input
transcript_path=$(echo "$hook_input" | jq -r '.transcript_path // ""' 2>/dev/null)

checker="$(dirname "$0")/has_pending_background_work.py"
if [ -n "$transcript_path" ] && [ -f "$checker" ] && python3 "$checker" "$transcript_path"; then
  exit 0
fi

dir_name=$(basename "$(pwd)")
message="Project: $dir_name"
title="Claude ready"

if command -v terminal-notifier >/dev/null 2>&1; then
  terminal-notifier -message "$message" -title "$title" -activate com.apple.Terminal 2>/dev/null || true
else
  safe_message=${message//\"/\\\"}
  safe_title=${title//\"/\\\"}
  osascript -e "display notification \"$safe_message\" with title \"$safe_title\" sound name \"Glass\"" 2>/dev/null || true
fi
