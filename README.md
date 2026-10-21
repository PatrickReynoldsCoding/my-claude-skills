# my-claude-skills

A Claude Code plugin with general-purpose skills and a small hook catalog.

## Install

```
/plugin marketplace add PatrickReynoldsCoding/my-claude-skills
/plugin install my-claude-skills@my-claude-skills
```

## Skills

| Skill | What it does |
|---|---|
| `explain` | Explain code or an idea in short, plain sentences (ASD-STE100 style), answer first. |
| `review-annotate-code` | Temporarily annotate a branch's changes with numbered reading-order comments. Can move them to a GitHub PR as review comments. |
| `review-code-change-flow-notes` | Write flow notes for a code change (old vs new code) so you can learn to read it, with a blank for your own summary of each flow. Set `FLOW_NOTES_ROOT` to choose where notes go. |
| `review-code-diagram` | Draw a code flow as an Excalidraw sequence diagram where every box and arrow opens the exact line in IntelliJ. Ships a local server, a link opener app and a VS Code extension (macOS). |
| `excel-table` | Build a styled `.xlsx` table (wrapped cells, fitted row heights, colour groups, legend). |

## Hooks (copy-paste, not auto-installed)

Nothing in `hooks/` runs on install. Copy a hook into `~/.claude/hooks/` and wire it
into `~/.claude/settings.json` as its README says.

- `notify-claude-ready/` — macOS notification when Claude finishes a turn.
- `notify-permission-request/` — macOS notification when Claude asks for permission.
