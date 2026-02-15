# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Confirmation modal dialog.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmModal(ModalScreen[None]):
    """
    A modal screen for confirmation actions.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "close", "No"),
    ]

    def __init__(self, message: str, callback: Callable[[], None]) -> None:
        """
        Initialize the ConfirmModal.

        Parameters
        ----------
        message : str
            The message to display in the modal.
        callback : Callable[[], None]
            The function to call if confirmed.
        """
        super().__init__()
        self.message: str = message
        self.callback: Callable[[], None] = callback

    def compose(self) -> ComposeResult:
        """
        Compose the modal UI.

        Returns
        -------
        ComposeResult
            The UI components for the modal.
        """
        with Vertical(id="confirm_container"):
            yield Static(self.message, id="confirm_message")
            with Horizontal(id="confirm_actions"):
                yield Button("Yes (y)", variant="success", id="yes_btn")
                yield Button("No (n)", variant="error", id="no_btn")

    def action_close(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()

    def action_confirm(self) -> None:
        """Confirm the action and call the callback."""
        self.callback()
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Parameters
        ----------
        event : Button.Pressed
            The button press event.
        """
        if event.button.id == "yes_btn":
            self.action_confirm()
        else:
            self.action_close()
