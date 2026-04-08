from __future__ import annotations

import random

from textual.widgets import Static

from ..constants import QUIPS, mood_style

MOOD_ICONS: dict[str, str] = {
    "ecstatic": "★ Jamb is ECSTATIC",
    "happy": "☺ Jamb says...",
    "content": "◉ Jamb says...",
    "bored": "… Jamb sighs...",
    "hungry": "◉ Jamb grumbles...",
    "tired": "☽ Jamb mumbles...",
    "grumpy": "☠ Jamb growls...",
    "chaotic": "⚡ Jamb shrieks...",
}


class SpeechBubble(Static):
    """A speech bubble that shows mood-themed quips."""

    def __init__(self, mood: str = "happy", **kwargs) -> None:
        self._mood = mood
        super().__init__(self._random_quip(), **kwargs)

    def on_mount(self) -> None:
        self.border_title = MOOD_ICONS.get(self._mood, "Jamb says...")
        self.add_class(mood_style(self._mood))

    def _random_quip(self) -> str:
        pool = QUIPS.get(self._mood, QUIPS["content"])
        return f'"{random.choice(pool)}"'

    def update_mood(self, mood: str) -> None:
        self._mood = mood
        self.border_title = MOOD_ICONS.get(mood, "Jamb says...")
        self.remove_class("mood-good", "mood-neutral", "mood-bad")
        self.add_class(mood_style(mood))
        self.rotate()

    def rotate(self) -> None:
        self.update(self._random_quip())
