from __future__ import annotations

from typing import Any, Callable

from textual.app import ComposeResult
from textual.widgets import Button, Label, Static
from textual.containers import VerticalScroll


class Menu(Static):
    """A vertical menu of selectable items."""

    def __init__(
        self, items: list[tuple[str, Callable[[], Any]]], title: str = "", **kwargs
    ) -> None:
        self._items = items
        self._title = title
        self._callbacks: dict[str, Callable[[], Any]] = {}
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        if self._title:
            yield Label(f"  [bold #d946ef]╔══ {self._title} ══╗[/]\n", classes="header")
        with VerticalScroll():
            for i, (label, callback) in enumerate(self._items):
                btn_id = f"menu-btn-{i}"
                self._callbacks[btn_id] = callback
                yield Button(label, id=btn_id, classes="menu-item")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        callback = self._callbacks.get(event.button.id or "")
        if callback:
            callback()
