#!/bin/bash
# Notify (macOS) when Claude requests permission to use a tool.
# Wire to the `PermissionRequest` event. Shows the tool name + current project.

read -r hook_input
tool_name=$(echo "$hook_input" | jq -r '.tool_name // "tool"' 2>/dev/null)

dir_name=$(basename "$(pwd)")
message="Project: $dir_name"
title="Claude needs permission ($tool_name)"

if command -v terminal-notifier >/dev/null 2>&1; then
  terminal-notifier -message "$message" -title "$title" -activate com.apple.Terminal 2>/dev/null || true
else
  safe_message=${message//\"/\\\"}
  safe_title=${title//\"/\\\"}
  osascript -e "display notification \"$safe_message\" with title \"$safe_title\" sound name \"Glass\"" 2>/dev/null || true
fi
