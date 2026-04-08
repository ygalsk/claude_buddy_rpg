---
description: Show Jamb's full companion card combining native buddy data with TUI progression
allowed-tools:
  - Read
  - Bash
user-invokable: true
---

# Jamb Companion Card

Read `~/.claude/jamb/save.json` and display a rich companion card. Include:

- **Header**: Name, species, rarity (with stars), shiny status
- **Level & Title**: Current level / level cap, title, stage
- **Stats**: All 5 stats as bar charts showing current value / stat cap
- **Care**: Hunger, energy, happiness percentages
- **Mood**: Current mood with emoji
- **Equipment**: Weapon, armor, accessory
- **Achievements**: Count and notable ones
- **Dungeon**: Highest floor reached
- **Gold**: Current balance

If `native_rarity` is null, suggest running `/jamb:sync` first to pull native bones.

Format the card nicely with box-drawing characters and aligned columns. Keep it compact but informative.
