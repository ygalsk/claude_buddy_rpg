"""Chat screen — talk to Jamb directly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, Static
from textual import work

from ..chat_engine import chat_sync
from .. import persistence

if TYPE_CHECKING:
    from ..app import JambApp


class ChatMessage(Static):
    """A single chat message bubble."""

    def __init__(self, sender: str, text: str, **kwargs) -> None:
        self._sender = sender
        self._text = text
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        if self._sender == "user":
            yield Label(f"  [bold #c084fc]You:[/] {self._text}")
        else:
            yield Label(f"  [bold #22c55e]Jamb:[/] [lightskyblue]{self._text}[/]")


class ChatScreen(Screen):

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]

        with Vertical(classes="screen-box"):
            yield Label("  [bold #d946ef]╔══ CHAT WITH JAMB ══╗[/]\n", classes="header")

            with VerticalScroll(id="chat-history"):
                # Load existing chat history
                for entry in app.state.chat_history[-30:]:
                    yield ChatMessage(entry["role"], entry["content"])

            yield Label("", id="typing-indicator")
            yield Input(placeholder="Say something to Jamb...", id="chat-input")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat-input", Input).focus()
        self._scroll_to_bottom()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:
            return

        # Clear input
        input_widget = self.query_one("#chat-input", Input)
        input_widget.value = ""

        # Add user message to UI
        self._add_message("user", message)

        # Show typing indicator
        indicator = self.query_one("#typing-indicator", Label)
        indicator.update("  [dim italic]Jamb is thinking...[/]")

        # Advance daily challenge for chat
        app: JambApp = self.app  # type: ignore[assignment]
        daily_done = app.state.advance_daily("chat")
        if daily_done:
            app.award_daily_challenge()

        # Send to API in background thread
        self._send_to_jamb(message)

    @work(thread=True)
    def _send_to_jamb(self, message: str) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        # Increment achievement counter
        state.achievement_counters["messages_sent"] = (
            state.achievement_counters.get("messages_sent", 0) + 1
        )

        # Add to history before sending
        state.chat_history.append({"role": "user", "content": message})

        response = chat_sync(message, state, state.chat_history[:-1])

        # Add response to history
        state.chat_history.append({"role": "assistant", "content": response})

        # Trim history to last 50 messages
        if len(state.chat_history) > 50:
            state.chat_history = state.chat_history[-50:]

        persistence.save(state)

        # Update UI from thread
        self.app.call_from_thread(self._add_message, "assistant", response)
        self.app.call_from_thread(self._clear_typing)

    def _add_message(self, sender: str, text: str) -> None:
        history = self.query_one("#chat-history", VerticalScroll)
        msg = ChatMessage(sender, text)
        history.mount(msg)
        self._scroll_to_bottom()

    def _clear_typing(self) -> None:
        indicator = self.query_one("#typing-indicator", Label)
        indicator.update("")

    def _scroll_to_bottom(self) -> None:
        try:
            history = self.query_one("#chat-history", VerticalScroll)
            history.scroll_end(animate=False)
        except Exception:
            pass

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()
