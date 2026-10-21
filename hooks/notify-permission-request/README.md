# notify-permission-request (macOS notification when Claude needs permission)

## What this hook does

Pops a macOS notification when Claude asks for permission to use a tool, so you
can come back and approve/deny without watching the terminal. The title shows
the tool name (e.g. `Claude needs permission (Bash)`) and the body shows
`Project: <dir>` (the working-directory basename). Uses `terminal-notifier` if
installed, otherwise falls back to `osascript`.

## Event

`PermissionRequest`

## Install

1. Copy the script into your own hooks dir:
   ```
   cp hooks/notify-permission-request/notify-permission-request.sh ~/.claude/hooks/notify-permission-request.sh
   chmod +x ~/.claude/hooks/notify-permission-request.sh
   ```
2. Add this to your `~/.claude/settings.json` under the matching event:
   ```json
   {
     "hooks": {
       "PermissionRequest": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "$HOME/.claude/hooks/notify-permission-request.sh",
               "async": true
             }
           ]
         }
       ]
     }
   }
   ```
3. Restart Claude Code / start a new session.

## Notes

- **macOS only** (`terminal-notifier` / `osascript`). `brew install terminal-notifier`
  for the nicer notification that can re-activate Terminal on click; without it,
  the `osascript` fallback still works.
- Requires `jq` (to read the tool name from the event JSON).
- `async: true` keeps it off the critical path.
- Reference your own copied path (`$HOME/.claude/hooks/...`) in the snippet —
  these hooks are **not** wired via the plugin, so `${CLAUDE_PLUGIN_ROOT}` does
  not apply.
