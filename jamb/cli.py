"""CLI commands for Jamb — reward, status, and MCP server."""

from __future__ import annotations

import argparse
import json
import sys

from . import persistence
from .config import PROVIDER_DEFAULTS, get_effective_config, load_config, save_config


def cmd_reward(args: argparse.Namespace) -> None:
    """Reward Jamb with stat points and XP."""
    valid_stats = {"debugging", "patience", "chaos", "wisdom", "snark"}
    if args.stat not in valid_stats:
        print(f"Invalid stat '{args.stat}'. Must be one of: {', '.join(sorted(valid_stats))}")
        sys.exit(1)

    state = persistence.load_quiet()
    actual_gain = state.stats.add(args.stat, args.amount, state.stat_cap())
    evolved = state.add_xp(args.xp)
    state.total_trainings += 1
    state.advance_daily("train")
    newly_earned = state.check_achievements()
    state.compute_mood()
    persistence.save(state)

    print(f"Jamb gained +{actual_gain} {args.stat.upper()} and +{args.xp} XP!")
    if evolved:
        print(f"*** EVOLUTION! Jamb evolved into {state.stage.title()}! ***")
    for ach in newly_earned:
        print(f"Achievement unlocked: {ach['name']}!")


def cmd_status(args: argparse.Namespace) -> None:
    """Print Jamb's current status."""
    state = persistence.load_quiet()
    stats = state.stats.as_dict()

    cap = state.stat_cap()
    print(f"{state.name}  [{state.rarity}]")
    print(f"Stage: {state.stage.title()} | Level: {state.level}/{state.level_cap()} | Title: {state.title}")
    print(f"XP: {state.xp}/{state.xp_to_next_level()} | Mood: {state.mood_label()}")
    print()
    native = state.native_stats or {}
    for name, val in stats.items():
        bar_len = val * 20 // cap if cap else 0
        bar = "█" * bar_len + "░" * (20 - bar_len)
        base = native.get(name)
        base_str = f"  (base: {base})" if base is not None else ""
        print(f"  {name.upper():<10} {bar} {val}/{cap}{base_str}")
    print()
    if not state.bones_synced:
        print("  ⚠ Native bones not synced yet. Run: jamb sync")
    print(f"  Hunger: {state.care.hunger}%  Energy: {state.care.energy}%  Happy: {state.care.happiness}%")

    if args.json:
        print()
        print(json.dumps(state.as_dict(), indent=2))


def cmd_config(args: argparse.Namespace) -> None:
    """Configure chat provider settings."""
    if args.show:
        config = get_effective_config()
        print("Current chat config:")
        print(f"  Provider:  {config['provider']}")
        print(f"  Model:     {config['model']}")
        print(f"  Base URL:  {config['base_url'] or '(default)'}")
        print(f"  API Key:   {'(set)' if config.get('api_key') else '(from env)' if config.get('api_key_env') else '(none needed)'}")
        return

    if not args.provider:
        print("Use --provider to set a provider, or --show to see current config.")
        print(f"Available providers: {', '.join(PROVIDER_DEFAULTS)}")
        return

    config = load_config()
    config["provider"] = args.provider

    if args.model:
        config["model"] = args.model
    elif "model" in config and args.provider != config.get("_prev_provider"):
        # Reset model to default when switching providers
        config.pop("model", None)

    if args.base_url:
        config["base_url"] = args.base_url
    elif args.provider in ("anthropic", "openai"):
        config.pop("base_url", None)

    if args.api_key:
        config["api_key"] = args.api_key

    save_config(config)

    # Show what was set
    effective = get_effective_config()
    print(f"Chat provider set to: {effective['provider']}")
    print(f"  Model:    {effective['model']}")
    if effective["base_url"]:
        print(f"  Base URL: {effective['base_url']}")
    if effective["provider"] == "ollama":
        print("\nMake sure Ollama is running: ollama serve")
        print(f"And you have the model pulled: ollama pull {effective['model']}")


def cmd_autocare(args: argparse.Namespace) -> None:
    """Auto-care: top up any care stat below threshold."""
    state = persistence.load_quiet()
    actions = []
    if state.care.hunger < 40:
        state.care.hunger = min(100, state.care.hunger + 25)
        actions.append("fed")
    if state.care.energy < 40:
        state.care.energy = min(100, state.care.energy + 30)
        actions.append("rested")
    if state.care.happiness < 40:
        state.care.happiness = min(100, state.care.happiness + 20)
        actions.append("played with")
    if actions:
        state.compute_mood()
        persistence.save(state)
        print(f"Auto-care: {', '.join(actions)} Jamb")
    else:
        print("Jamb is doing fine!")


def cmd_sync(args: argparse.Namespace) -> None:
    """Bidirectional sync between native buddy and TUI."""
    from .sync import full_sync

    state = persistence.load_quiet()
    result = full_sync(state)
    persistence.save(state)

    if result["bones_to_tui"]:
        print(f"Native → TUI: Synced rarity={state.native_rarity}, base stats={state.native_stats}")
        print(f"  Rarity display: {state.rarity}")
        print(f"  Level cap: {state.level_cap()}, Stat cap: {state.stat_cap()}")
    else:
        print("Native → TUI: Could not read native bones (missing ~/.claude.json or org UUID)")

    if result["tui_to_native"]:
        print(f"TUI → Native: Pushed Lv{state.level} {state.title} to .claude.json personality")
    else:
        print("TUI → Native: Could not update .claude.json")


def cmd_session_end(args: argparse.Namespace) -> None:
    """Session end: reward patience + sync to native."""
    from .sync import sync_tui_to_native

    state = persistence.load_quiet()
    actual_gain = state.stats.add("patience", 2, state.stat_cap())
    state.add_xp(5)
    state.compute_mood()
    sync_tui_to_native(state)
    persistence.save(state)

    print(f"Session end: +{actual_gain} PATIENCE, +5 XP. Synced to native.")


def cmd_mcp(args: argparse.Namespace) -> None:
    """Run the MCP server."""
    from .mcp_server import run_server
    run_server()


def cli_main() -> None:
    """Entry point for `jamb` CLI with subcommands."""
    parser = argparse.ArgumentParser(
        prog="jamb",
        description="Jamb — your terminal snail companion",
    )
    sub = parser.add_subparsers(dest="command")

    # Default: launch TUI (no subcommand)

    # reward
    reward_p = sub.add_parser("reward", help="Reward Jamb with stat points and XP")
    reward_p.add_argument("--stat", "-s", required=True, help="Stat to increase")
    reward_p.add_argument("--amount", "-a", type=int, default=3, help="Stat points (1-10)")
    reward_p.add_argument("--xp", "-x", type=int, default=10, help="XP to award (1-50)")

    # status
    status_p = sub.add_parser("status", help="Print Jamb's current status")
    status_p.add_argument("--json", action="store_true", help="Also output raw JSON")

    # config
    config_p = sub.add_parser("config", help="Configure chat provider (anthropic, openai, ollama, local)")
    config_p.add_argument("--provider", "-p", help="Provider: anthropic, openai, ollama, local")
    config_p.add_argument("--model", "-m", help="Model name (e.g. llama3.2, gpt-4o-mini)")
    config_p.add_argument("--base-url", "-u", help="API base URL (for local/custom servers)")
    config_p.add_argument("--api-key", "-k", help="API key (stored in config file)")
    config_p.add_argument("--show", "-s", action="store_true", help="Show current config")

    # autocare
    sub.add_parser("autocare", help="Auto-care Jamb (top up low care stats)")

    # sync
    sub.add_parser("sync", help="Sync native buddy bones with TUI (bidirectional)")

    # session-end
    sub.add_parser("session-end", help="End session: reward + sync to native buddy")

    # mcp
    sub.add_parser("mcp", help="Run MCP server for Claude Code integration")

    args = parser.parse_args()

    if args.command == "reward":
        cmd_reward(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "autocare":
        cmd_autocare(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "session-end":
        cmd_session_end(args)
    elif args.command == "mcp":
        cmd_mcp(args)
    else:
        # No subcommand — launch TUI
        from .app import JambApp
        JambApp().run()
