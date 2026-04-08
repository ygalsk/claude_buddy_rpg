---
description: Sync native Claude Code buddy bones with Jamb TUI progression (bidirectional)
allowed-tools:
  - Bash
  - Read
user-invokable: true
---

# Sync Native Buddy with Jamb TUI

Run the bidirectional sync between the native Claude Code buddy system and Jamb's TUI progression:

```bash
PYTHONPATH=/home/dkremer/jamb /usr/bin/python -m jamb sync
```

This command:
1. **Native → TUI**: Reads the native buddy bones (rarity, base stats) computed from your account UUID and syncs them into `~/.claude/jamb/save.json`. On first sync, seeds TUI stats from native base values.
2. **TUI → Native**: Pushes trained stats, level, mood, equipment, and achievements into the `personality` field of `~/.claude.json`, so the native buddy's speech bubbles and system prompt reflect your training progress.

After running, display the sync results to the user.
