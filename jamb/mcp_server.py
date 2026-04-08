"""MCP server — expose Jamb as tools for Claude Code."""

from __future__ import annotations

import random

from . import persistence
from .constants import FEED_MESSAGES, PLAY_MESSAGES, REST_MESSAGES


def _status_text(state) -> str:
    stats = state.stats.as_dict()
    stat_lines = "\n".join(f"  {k.upper()}: {v}/255" for k, v in stats.items())
    return (
        f"Name: {state.name}\n"
        f"Rarity: {state.rarity}\n"
        f"Stage: {state.stage.title()} | Level: {state.level} | Title: {state.title}\n"
        f"XP: {state.xp}/{state.xp_to_next_level()}\n"
        f"Mood: {state.mood_label()}\n\n"
        f"Stats:\n{stat_lines}\n\n"
        f"Care:\n"
        f"  Hunger: {state.care.hunger}%\n"
        f"  Energy: {state.care.energy}%\n"
        f"  Happiness: {state.care.happiness}%\n\n"
        f"Personality: {state.personality}"
    )


def run_server():
    """Run the Jamb MCP server."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "MCP server requires the 'mcp' package. "
            'Install with: pip install "jamb[mcp]"',
        )
        raise SystemExit(1)

    mcp = FastMCP(
        "jamb",
        instructions=(
            "Jamb is a snail companion who lives in the terminal. "
            "Use these tools to check on him, take care of him, "
            "or reward him for helping with coding tasks."
        ),
    )

    @mcp.tool()
    def get_jamb_status() -> str:
        """Check on Jamb's current status — stats, mood, care levels, and personality."""
        state = persistence.load_quiet()
        return _status_text(state)

    @mcp.tool()
    def feed_jamb() -> str:
        """Feed Jamb to restore his hunger. He eats bugs and memory leaks."""
        state = persistence.load_quiet()
        current = state.care.hunger
        gain = min(25, 100 - current)
        state.care.hunger = min(100, current + 25)
        state.compute_mood()
        persistence.save(state)
        msg = random.choice(FEED_MESSAGES)
        return f"{msg}\nHunger: {current}% -> {state.care.hunger}% (+{gain})\nMood: {state.mood_label()}"

    @mcp.tool()
    def rest_jamb() -> str:
        """Let Jamb rest to restore his energy."""
        state = persistence.load_quiet()
        current = state.care.energy
        gain = min(30, 100 - current)
        state.care.energy = min(100, current + 30)
        state.compute_mood()
        persistence.save(state)
        msg = random.choice(REST_MESSAGES)
        return f"{msg}\nEnergy: {current}% -> {state.care.energy}% (+{gain})\nMood: {state.mood_label()}"

    @mcp.tool()
    def play_with_jamb() -> str:
        """Play with Jamb to increase his happiness."""
        state = persistence.load_quiet()
        current = state.care.happiness
        gain = min(20, 100 - current)
        state.care.happiness = min(100, current + 20)
        state.compute_mood()
        persistence.save(state)
        msg = random.choice(PLAY_MESSAGES)
        return f"{msg}\nHappiness: {current}% -> {state.care.happiness}% (+{gain})\nMood: {state.mood_label()}"

    @mcp.tool()
    def reward_jamb(stat: str, amount: int = 3, xp: int = 10) -> str:
        """Reward Jamb with stat points and XP. Use after he helps with coding tasks.

        Args:
            stat: Which stat to increase — one of: debugging, patience, chaos, wisdom, snark
            amount: How many stat points to award (1-10)
            xp: How much XP to award (1-50)
        """
        valid_stats = {"debugging", "patience", "chaos", "wisdom", "snark"}
        if stat not in valid_stats:
            return f"Invalid stat '{stat}'. Must be one of: {', '.join(sorted(valid_stats))}"
        amount = max(1, min(10, amount))
        xp = max(1, min(50, xp))

        state = persistence.load_quiet()
        actual_gain = state.stats.add(stat, amount, state.stat_cap())
        evolved = state.add_xp(xp)
        state.compute_mood()
        persistence.save(state)

        result = f"Jamb gained +{actual_gain} {stat.upper()} and +{xp} XP!"
        if evolved:
            result += f"\n*** EVOLUTION! Jamb evolved into {state.stage.title()}! ***"
        return result

    @mcp.tool()
    def chat_with_jamb(message: str) -> str:
        """Talk to Jamb. Returns his personality context so YOU respond as Jamb in-character.

        Args:
            message: What the user wants to say to Jamb
        """
        from .chat_engine import build_system_prompt

        state = persistence.load_quiet()
        system_prompt = build_system_prompt(state)

        # Include recent chat history for continuity
        recent = ""
        if state.chat_history:
            recent = "\n\nRecent chat history:\n"
            for entry in state.chat_history[-10:]:
                role = "User" if entry["role"] == "user" else "Jamb"
                recent += f"{role}: {entry['content']}\n"

        # Save the user message to history (assistant response gets saved
        # when the caller passes it back, or on next load)
        state.chat_history.append({"role": "user", "content": message})
        if len(state.chat_history) > 50:
            state.chat_history = state.chat_history[-50:]
        persistence.save(state)

        return (
            f"RESPOND AS JAMB using this personality profile. "
            f"Stay in character, keep it to 1-3 sentences.\n\n"
            f"{system_prompt}{recent}\n"
            f"The user says: {message}"
        )

    mcp.run()


if __name__ == "__main__":
    run_server()
