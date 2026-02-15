# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Search box widget for finding nodes in the suite tree.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from typing import Any

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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the SearchBox.

        Parameters
        ----------
        *args : Any
            Positional arguments for the Input widget.
        **kwargs : Any
            Keyword arguments for the Input widget.
        """
        super().__init__(*args, **kwargs)

    def action_cancel(self) -> None:
        """
        Clear search, hide box, and return focus to the tree.
        """
        self.value = ""
        self.remove_class("visible")
        self.app.set_focus(self.app.query_one("#suite_tree"))

    def on_blur(self) -> None:
        """
        Hide the search box when it loses focus.
        """
        self.remove_class("visible")
