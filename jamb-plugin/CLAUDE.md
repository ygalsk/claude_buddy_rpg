# Jamb Plugin — Native Buddy Bridge

This plugin bridges the native Claude Code buddy system with Jamb's TUI progression system.

## How It Works

- **Native bones** (species, rarity, base stats) are computed deterministically from your account UUID by Claude Code. They're static and never change.
- **TUI progression** (XP, leveling, trained stats, inventory, dungeon) is stored at `~/.claude/jamb/save.json` and grows as you use Claude Code.
- The plugin's hooks automatically reward Jamb when you use Bash (debugging), Edit (patience), or Write (wisdom) tools.
- At session end, TUI progression is pushed back to the native buddy's personality in `~/.claude.json`, making speech bubbles progression-aware.

## Key Commands

- `/jamb:sync` — Bidirectional sync (pull native bones, push TUI progress)
- `/jamb:card` — Display full companion card with stats and progression

## Stats Reference

Jamb's 5 stats: DEBUGGING, PATIENCE, CHAOS, WISDOM, SNARK

Stats are capped by native rarity:
- Common: stat cap 150, level cap 20
- Uncommon: stat cap 180, level cap 30
- Rare: stat cap 220, level cap 50
- Epic: stat cap 245, level cap 75
- Legendary: stat cap 255, level cap 100

## Reading Jamb's State

Always read `~/.claude/jamb/save.json` for current stats. Key fields:
- `native_rarity`: The real rarity from native bones (null if not synced yet)
- `native_stats`: Base stats from bones (0-100 scale)
- `stats`: Trained TUI stats (0-255 scale, capped by rarity)
- `level`, `xp`, `title`, `stage`: Progression
- `care`: hunger/energy/happiness (0-100%)
- `mood`: Current mood state
