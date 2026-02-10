"""
Search box widget for finding nodes in the suite tree.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from textual.binding import Binding
from textual.widgets import Input


class SearchBox(Input):
    """
    An input widget for searching nodes in the tree.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel Search"),
        Binding("enter", "submit", "Search Next"),
    ]

    def action_cancel(self) -> None:
        """Clear search, hide box, and return focus to the tree."""
        self.value = ""
        self.remove_class("visible")
        self.app.set_focus(self.app.query_one("#suite_tree"))

    def on_blur(self) -> None:
        """Hide the search box when it loses focus."""
        self.remove_class("visible")
