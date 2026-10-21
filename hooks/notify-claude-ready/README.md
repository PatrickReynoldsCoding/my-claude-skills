# notify-claude-ready (macOS notification when Claude is ready)

## What this hook does

Pops a macOS notification when Claude finishes a turn and is waiting for your
input — handy when you've tabbed away. The notification shows `Project: <dir>`
(the working-directory basename). Uses `terminal-notifier` if installed,
otherwise falls back to `osascript`.

**Only fires when Claude is actually done.** If the turn ended while Claude is
still waiting on background work — background Bash commands, async agents,
`Monitor`s, or a pending `/loop` wakeup — the notification is skipped. You get
pinged once that work finishes and Claude wraps up. The check is done by
`has_pending_background_work.py`, which reads the session transcript (a launch
counts as pending until its `<task-notification>` arrives, or for at most 4h in
case the task died silently).

## Event

`Stop`

## Install

1. Copy **both** scripts into your own hooks dir (the checker must sit next to
   the notifier):
   ```
   cp hooks/notify-claude-ready/notify-claude-ready.sh hooks/notify-claude-ready/has_pending_background_work.py ~/.claude/hooks/
   chmod +x ~/.claude/hooks/notify-claude-ready.sh ~/.claude/hooks/has_pending_background_work.py
   ```
2. Add this to your `~/.claude/settings.json` under the matching event:
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "$HOME/.claude/hooks/notify-claude-ready.sh",
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
- Needs `jq` and `python3`. Without the checker file it falls back to
  notifying on every `Stop`.
- For "Claude needs your input" pings, pair it with `notify-permission-request/`.
  Avoid a `Notification` / `idle_prompt` hook — it fires while Claude is idle
  waiting on background work, which is the noise this hook avoids.
- `async: true` keeps it off the critical path.
- Reference your own copied path (`$HOME/.claude/hooks/...`) in the snippet —
  these hooks are **not** wired via the plugin, so `${CLAUDE_PLUGIN_ROOT}` does
  not apply.
