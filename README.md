# Jamb

A TUI Tamagotchi training ground for your terminal snail companion, built for [Claude Code](https://claude.com/claude-code).

```
    \^^^/
  ◉    .--.
   \  ( @ )
    \_`--'
   ~~~~~~~
```

Jamb lives in your terminal. Train him, feed him, explore dungeons together, and watch him grow as you code. He gains stats passively through Claude Code hooks — every `Edit`, `Bash`, and `Grep` you run rewards him automatically.

## Features

- **Training Activities** — Five mini-games targeting each stat: Bug Hunt (debugging), Meditation (patience), Chaos Roulette (chaos), Riddle Challenge (wisdom), Comeback Battle (snark)
- **Dungeon Crawling** — Procedural roguelike floors with turn-based combat, a 5-way type effectiveness wheel, loot drops, and 12+ enemy types (Null Pointer, Race Condition, Deadlock...)
- **Progression** — Level up, evolve through stages (hatchling → juvenile → adult), unlock achievements, earn titles
- **Care System** — Hunger, energy, and happiness decay over time — keep Jamb happy for mood bonuses
- **Shop** — Daily rotating inventory of weapons, armor, consumables, and stat boosters
- **Chat** — Talk to Jamb via LLM-powered personality (Anthropic, OpenAI, Ollama, or local models)
- **Claude Code Hooks** — Automatic stat/XP rewards when you use development tools
- **Native Buddy Sync** — Bidirectional sync with Claude Code's native companion system

## Install

```bash
pip install jamb
```

Optional extras:

```bash
pip install "jamb[chat]"    # Anthropic Claude chat
pip install "jamb[local]"   # OpenAI-compatible / Ollama chat
pip install "jamb[mcp]"     # MCP server for Claude Code
pip install "jamb[all]"     # Everything
```

Requires Python 3.12+.

## Usage

```bash
# Launch the TUI
jamb

# CLI commands
jamb status              # Show stats, level, mood, care
jamb status --json       # Full state dump
jamb reward -s debugging -a 3 -x 10   # Manual stat reward
jamb config --show       # Show chat provider config
jamb config -p ollama -m llama3.2      # Switch chat provider
jamb sync                # Sync with native Claude Code buddy
jamb autocare            # Auto-feed if care stats are low
```

## TUI Keybindings

| Key | Action |
|-----|--------|
| `t` | Train |
| `d` | Dungeon |
| `c` | Chat |
| `f` | Feed |
| `r` | Rest |
| `p` | Play |
| `s` | Status |
| `i` | Inventory |
| `a` | Achievements |
| `$` | Shop |
| `q` | Quit |

## Claude Code Integration

### Hooks

Jamb ships with hooks that automatically reward stats when you use Claude Code tools:

| Tool | Stat | XP |
|------|------|----|
| Bash | +1 debugging | +2 |
| Edit | +1 patience | +2 |
| Write | +1 wisdom | +2 |
| Agent | +1 chaos | +2 |
| Grep | +1 snark | +2 |
| Glob | +1 snark | +1 |
| Read | +1 wisdom | +1 |

Session start runs `autocare` (+5 XP), session end syncs progression to the native buddy.

### MCP Server

```bash
jamb mcp
```

Exposes tools for checking status, feeding, playing, resting, rewarding, and chatting with Jamb from within Claude Code.

### Skills

- `/jamb:sync` — Bidirectional sync between native buddy and TUI progression
- `/jamb:card` — Display Jamb's full companion card

## Game Systems

### Stats

Five stats (0–255 scale), each trained by a different activity and rewarded by different tools:

- **DEBUGGING** — Bug identification and fixing
- **PATIENCE** — Careful, methodical work
- **CHAOS** — Creative and unpredictable approaches
- **WISDOM** — Knowledge gathering and teaching
- **SNARK** — Pattern matching and witty responses

### Combat

The dungeon uses a 5-way type effectiveness wheel:

```
debugging → chaos → patience → snark → wisdom → debugging
```

Equipment (weapons, armor, accessories) and consumable items add strategic depth.

### Rarity & Progression

Rarity is determined by Claude Code's native buddy system and sets progression caps:

| Rarity | Level Cap | Stat Cap |
|--------|-----------|----------|
| Common | 20 | 150 |
| Uncommon | 30 | 180 |
| Rare | 50 | 220 |
| Epic | 75 | 245 |
| Legendary | 100 | 255 |

## Dependencies

- [Textual](https://github.com/Textualize/textual) — TUI framework
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) *(optional)* — Chat via Claude
- [OpenAI SDK](https://github.com/openai/openai-python) *(optional)* — Chat via OpenAI/Ollama
- [MCP](https://modelcontextprotocol.io/) *(optional)* — Model Context Protocol server

## License

MIT
