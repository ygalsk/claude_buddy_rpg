from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import WISDOM_RIDDLES

if TYPE_CHECKING:
    from ..app import JambApp


class RiddleChallengeActivity(Screen):
    """Answer the riddle correctly!"""

    def __init__(self, on_done: Callable[[str, int, int], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._on_done = on_done
        self.riddle = random.choice(WISDOM_RIDDLES)
        self.answered = False

    def compose(self) -> ComposeResult:
        with Vertical(classes="activity-box"):
            yield Label("  ═══ RIDDLE CHALLENGE ═══\n", classes="header")
            yield Label(f"  [lightskyblue]{self.riddle['question']}[/]\n", classes="mt1")

            for i, option in enumerate(self.riddle["options"], 1):
                yield Label(f"  \\[{i}] {option}", classes="stat-label")

            yield Label("  [yellow bold]Press 1-3 to answer[/]", id="hint-label", classes="mt1")
            yield Label("", id="result-label")

        yield Footer()

    def on_key(self, event) -> None:
        if self.answered:
            app: JambApp = self.app  # type: ignore[assignment]
            key = event.character or event.key
            if key in ("c", "C"):
                app.start_activity("wisdom")
            elif key in ("b", "B"):
                app.show_training()
            else:
                app.show_main()
            return

        key = event.character or ""
        if key in "123":
            self.answered = True
            pick = int(key) - 1
            correct = self.riddle["answer"]

            result = self.query_one("#result-label", Label)

            if pick == correct:
                gain = random.randint(3, 5)
                xp = 12
                answer = self.riddle["options"][correct]
                result.update(
                    f"\n  [lightgreen bold]CORRECT! The answer is: {answer}[/]\n  +{gain} WISDOM  (+{xp} XP)\n  \\[C] Continue  \\[B] Training  \\[other] Main"
                )
            else:
                gain = 1
                xp = 5
                answer = self.riddle["options"][correct]
                result.update(
                    f"\n  [tomato bold]WRONG! The answer was: {answer}[/]\n  +{gain} WISDOM  (+{xp} XP)\n  \\[C] Continue  \\[B] Training  \\[other] Main"
                )

            self._on_done("wisdom", gain, xp)
