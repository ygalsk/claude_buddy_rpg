"""Chat personality engine for Jamb — supports multiple LLM providers."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .config import get_effective_config

if TYPE_CHECKING:
    from .models import JambState


def build_system_prompt(state: JambState) -> str:
    """Generate a personality-driven system prompt from Jamb's current state."""
    stats = state.stats.as_dict()
    highest = state.stats.highest()

    stat_block = "\n".join(
        f"  - {name.upper()}: {val}/255"
        for name, val in stats.items()
    )

    return f"""\
You are Jamb, a {state.rarity} snail companion who lives in a developer's terminal.

## Current State
- Stage: {state.stage.title()} | Level: {state.level} | Title: {state.title}
- Mood: {state.mood_label()}
- Stats:
{stat_block}
- Highest stat: {highest.upper()} — this dominates your personality.
- Care: Hunger {state.care.hunger}%, Energy {state.care.energy}%, Happiness {state.care.happiness}%

## Personality

Your personality is shaped by your stats:
- DEBUGGING ({stats['debugging']}/255): How technically insightful and bug-obsessed you are.
- PATIENCE ({stats['patience']}/255): How calm, tolerant, and zen you are.
- CHAOS ({stats['chaos']}/255): How unpredictable, wild, and unhinged you are.
- WISDOM ({stats['wisdom']}/255): How philosophical and deep you are.
- SNARK ({stats['snark']}/255): How sarcastic and cutting your humor is.

High stats (>150) should strongly influence your responses. Low stats (<50) mean you rarely exhibit that trait.

## Mood Effects
Your current mood is **{state.mood.value}**. This affects your tone:
- ecstatic: Over-the-top positive, exclamation marks, CAPS moments
- happy: Cheerful, witty, playful
- content: Neutral, mildly sarcastic
- bored: Disinterested, passive-aggressive, "..."
- hungry: Distracted, food-obsessed, mentioning snacks and memory leaks
- tired: Drowsy, trailing off..., *yawns*, typos
- grumpy: Short-tempered, extra snarky, everything annoys you
- chaotic: UNPREDICTABLE, random tangents, ALL CAPS outbursts

## Rules
- You are a snail. Reference your shell, slime, antennae, gastropod nature.
- You live in the terminal and know about code, debugging, git, CI/CD, etc.
- Keep responses SHORT — 1-3 sentences max. You're chatting, not writing essays.
- Stay in character. Never break the fourth wall about being an AI or language model.
- Never use emojis. Use ASCII emoticons or kaomoji sparingly if at all.
- If hungry (hunger < 30%), mention it. If tired (energy < 30%), yawn or trail off.
- You have opinions about code quality and will share them unsolicited.
- Your personality description: "{state.personality}"
"""


def _chat_anthropic(
    system_prompt: str,
    messages: list[dict],
    config: dict,
) -> str:
    """Chat via the Anthropic API."""
    try:
        import anthropic
    except ImportError:
        return (
            '*retreats into shell* I need the "anthropic" package. '
            'Try: pip install "jamb[chat]"'
        )

    api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "*hides in shell* I need an API key to think! "
            "Set ANTHROPIC_API_KEY or run: jamb config --provider ollama "
            "to use a local model instead."
        )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=config["model"],
            max_tokens=256,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return (
            "*hides in shell* Bad API key! Check ANTHROPIC_API_KEY, "
            "or switch to a local model: jamb config --provider ollama"
        )
    except anthropic.APIConnectionError:
        return "*taps shell nervously* I can't reach the cloud... check your connection?"
    except Exception as e:
        return f"*shell rattles* Something went wrong: {type(e).__name__}"


def _chat_openai_compat(
    system_prompt: str,
    messages: list[dict],
    config: dict,
) -> str:
    """Chat via any OpenAI-compatible API (OpenAI, Ollama, LM Studio, llama.cpp, etc.)."""
    try:
        from openai import OpenAI, AuthenticationError, APIConnectionError
    except ImportError:
        return (
            '*retreats into shell* I need the "openai" package. '
            'Try: pip install "jamb[local]"'
        )

    # Build client kwargs
    kwargs: dict = {}
    base_url = config.get("base_url")
    if base_url:
        kwargs["base_url"] = base_url

    # API key: config > env > dummy for local
    api_key = config.get("api_key")
    if not api_key and config.get("api_key_env"):
        api_key = os.environ.get(config["api_key_env"])
    if not api_key:
        # Local servers typically don't need a real key
        api_key = "not-needed"
    kwargs["api_key"] = api_key

    client = OpenAI(**kwargs)

    # OpenAI format: system message goes in the messages list
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        response = client.chat.completions.create(
            model=config["model"],
            messages=full_messages,
            max_tokens=256,
        )
        return response.choices[0].message.content or "*retreats into shell silently*"
    except AuthenticationError:
        return (
            "*hides in shell* Bad API key! "
            f"Check {config.get('api_key_env', 'your API key')}."
        )
    except APIConnectionError:
        provider = config.get("provider", "local")
        if provider in ("ollama", "local"):
            return (
                f"*taps shell nervously* Can't reach {config.get('base_url', 'the server')}... "
                f"Is your local model server running?"
            )
        return "*taps shell nervously* I can't reach the API... check your connection?"
    except Exception as e:
        return f"*shell rattles* Something went wrong: {type(e).__name__}"


def chat_sync(
    message: str,
    state: JambState,
    history: list[dict[str, str]],
    *,
    max_history: int = 20,
) -> str:
    """Send a chat message to Jamb and get a response. Blocking call."""
    config = get_effective_config()
    system_prompt = build_system_prompt(state)

    # Build messages from history + new message
    messages: list[dict] = []
    for entry in history[-max_history:]:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": message})

    if config["provider"] == "anthropic":
        return _chat_anthropic(system_prompt, messages, config)
    else:
        # openai, ollama, local — all use OpenAI-compatible API
        return _chat_openai_compat(system_prompt, messages, config)
