"""Chat provider configuration for Jamb."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".claude" / "jamb"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Provider presets with sensible defaults
PROVIDER_DEFAULTS: dict[str, dict[str, Any]] = {
    "anthropic": {
        "model": "claude-haiku-4-5-20251001",
        "base_url": None,
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "model": "gpt-4o-mini",
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
    },
    "ollama": {
        "model": "llama3.2",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
    },
    "local": {
        "model": "default",
        "base_url": "http://localhost:8080/v1",
        "api_key_env": None,
    },
}


def load_config() -> dict[str, Any]:
    """Load chat config, falling back to anthropic defaults."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return {"provider": "anthropic"}


def save_config(config: dict[str, Any]) -> None:
    """Save chat config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")


def get_effective_config() -> dict[str, Any]:
    """Get config with provider defaults merged in."""
    config = load_config()
    provider = config.get("provider", "anthropic")
    defaults = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["local"])

    return {
        "provider": provider,
        "model": config.get("model", defaults["model"]),
        "base_url": config.get("base_url", defaults["base_url"]),
        "api_key": config.get("api_key"),
        "api_key_env": defaults["api_key_env"],
    }
