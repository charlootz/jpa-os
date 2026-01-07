"""
jpa-os Terminal UI — Talk to Vega.

Usage:
    python -m engine.tui
    vega
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Header, Input, Static
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text

from dotenv import load_dotenv
load_dotenv()


class Message(Static):
    """A message in the conversation."""

    def __init__(self, sender: str, content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.sender = sender
        self._content = content

    def compose(self) -> ComposeResult:
        yield Static(self._content)

    def update_content(self, content: str) -> None:
        """Update the message content."""
        self._content = content
        self.query_one(Static).update(content)

    def append_content(self, text: str) -> None:
        """Append to the message content."""
        self._content += text
        self.query_one(Static).update(self._content)


class ThinkingIndicator(Static):
    """Shows when Vega is thinking."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self._dots = 0
        self._timer = None

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.3, self._animate)

    def _animate(self) -> None:
        self._dots = (self._dots + 1) % 4
        dots = "." * self._dots
        self.update(f"Vega is thinking{dots}")

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()


class VegaApp(App):
    """jpa-os — Talk to Vega"""

    TITLE = "jpa-os"
    SUB_TITLE = "Pro uno vincimus"

    CSS = """
    Screen {
        background: #0d1117;
    }

    Header {
        background: #161b22;
        color: #c9d1d9;
        dock: top;
    }

    #conversation {
        background: #0d1117;
        padding: 1 2;
        margin-bottom: 5;
        scrollbar-color: #30363d;
        scrollbar-color-hover: #484f58;
    }

    .user-message {
        background: #1f6feb;
        color: #ffffff;
        padding: 1 2;
        margin: 1 0;
        border: none;
    }

    .vega-message {
        background: #21262d;
        color: #c9d1d9;
        padding: 1 2;
        margin: 1 0;
        border: none;
    }

    .system-message {
        color: #8b949e;
        padding: 0 2;
        margin: 1 0;
        text-style: italic;
    }

    .thinking {
        color: #8b949e;
        padding: 0 2;
        margin: 1 0;
        text-style: italic;
    }

    #input-container {
        dock: bottom;
        height: auto;
        background: #161b22;
        padding: 1;
    }

    #message-input {
        background: #0d1117;
        border: tall #30363d;
        padding: 0 1;
    }

    #message-input:focus {
        border: tall #1f6feb;
    }

    #status {
        background: #161b22;
        color: #8b949e;
        height: 1;
        padding: 0 2;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
        Binding("escape", "quit", "Quit"),
    ]

    is_processing = reactive(False)

    def __init__(self):
        super().__init__()
        self._current_response: Message | None = None
        self._thinking: ThinkingIndicator | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="conversation")
        yield Static("Ready", id="status")
        yield Container(
            Input(placeholder="Talk to Vega...", id="message-input"),
            id="input-container"
        )

    def on_mount(self) -> None:
        self.query_one("#message-input", Input).focus()
        self._add_system_message("Vega online. How can I help?")

    def _add_system_message(self, text: str) -> None:
        """Add a system message."""
        conversation = self.query_one("#conversation", VerticalScroll)
        msg = Static(text, classes="system-message")
        conversation.mount(msg)
        conversation.scroll_end(animate=False)

    def _add_user_message(self, text: str) -> None:
        """Add a user message."""
        conversation = self.query_one("#conversation", VerticalScroll)
        content = Text()
        content.append("jpa: ", style="bold")
        content.append(text)
        msg = Static(content, classes="user-message")
        conversation.mount(msg)
        conversation.scroll_end(animate=False)

    def _start_vega_response(self) -> Message:
        """Start a new Vega response."""
        conversation = self.query_one("#conversation", VerticalScroll)

        content = Text()
        content.append("Vega: ", style="bold cyan")
        msg = Message("vega", classes="vega-message")
        msg._content = content
        conversation.mount(msg)
        conversation.scroll_end(animate=False)
        return msg

    def _show_thinking(self) -> None:
        """Show thinking indicator."""
        conversation = self.query_one("#conversation", VerticalScroll)
        self._thinking = ThinkingIndicator(classes="thinking")
        conversation.mount(self._thinking)
        conversation.scroll_end(animate=False)

    def _hide_thinking(self) -> None:
        """Hide thinking indicator."""
        if self._thinking:
            self._thinking.remove()
            self._thinking = None

    def _update_status(self, text: str) -> None:
        self.query_one("#status", Static).update(text)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission."""
        if self.is_processing:
            return

        message = event.value.strip()
        if not message:
            return

        event.input.value = ""
        self._add_user_message(message)

        self.is_processing = True
        self._update_status("Thinking...")
        self._show_thinking()

        try:
            from engine.agents.base import run_vega_streaming

            self._hide_thinking()

            # Create response container
            conversation = self.query_one("#conversation", VerticalScroll)
            response_text = Text()
            response_text.append("Vega: ", style="bold cyan")
            response_widget = Static(response_text, classes="vega-message")
            conversation.mount(response_widget)

            full_response = ""

            async for chunk in run_vega_streaming(message):
                full_response += chunk
                response_text = Text()
                response_text.append("Vega: ", style="bold cyan")
                response_text.append(full_response)
                response_widget.update(response_text)
                conversation.scroll_end(animate=False)
                self._update_status("Responding...")

            self._update_status("Ready")

        except Exception as e:
            self._hide_thinking()
            self._add_system_message(f"Error: {str(e)}")
            self._update_status("Error")

        finally:
            self.is_processing = False

    def action_clear(self) -> None:
        """Clear the conversation."""
        conversation = self.query_one("#conversation", VerticalScroll)
        conversation.remove_children()
        self._add_system_message("Cleared.")

    def action_quit(self) -> None:
        self.exit()


def main():
    app = VegaApp()
    app.run()


if __name__ == "__main__":
    main()
