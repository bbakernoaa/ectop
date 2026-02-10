from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "close", "No"),
    ]

    def __init__(self, message, callback):
        super().__init__()
        self.message = message
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm_container"):
            yield Static(self.message, id="confirm_message")
            with Horizontal(id="confirm_actions"):
                yield Button("Yes (y)", variant="success", id="yes_btn")
                yield Button("No (n)", variant="error", id="no_btn")

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_confirm(self) -> None:
        self.callback()
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes_btn":
            self.action_confirm()
        else:
            self.action_close()
