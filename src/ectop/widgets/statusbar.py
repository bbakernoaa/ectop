# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Status bar widget for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.text import Text
from textual.widgets import Static

from ectop.constants import COLOR_STATUS_HALTED


class StatusBar(Static):
    """
    A status bar widget to display server information and health.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the StatusBar.

        Parameters
        ----------
        *args : Any
            Positional arguments for the Static widget.
        **kwargs : Any
            Keyword arguments for the Static widget.
        """
        super().__init__(*args, **kwargs)
        self.server_info: str = "Disconnected"
        self.last_sync: str = "Never"
        self.status: str = "Unknown"
        self.server_version: str = "Unknown"

    def update_status(self, host: str, port: int, status: str = "Connected", version: str = "Unknown") -> None:
        """
        Update the status bar information.

        Parameters
        ----------
        host : str
            The ecFlow server hostname.
        port : int
            The ecFlow server port.
        status : str, optional
            The server status message, by default "Connected".
        version : str, optional
            The ecFlow server version, by default "Unknown".
        """
        self.server_info = f"{host}:{port}"
        self.status = str(status)
        self.server_version = str(version)
        self.last_sync = datetime.now().strftime("%H:%M:%S")
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Refresh the rendered content of the status bar."""
        self.refresh()

    def render(self) -> Text:
        """
        Render the status bar.

        Returns
        -------
        Text
            The rendered status bar content.
        """
        status_color = "red"
        if self.status == "RUNNING":
            status_color = "green"
        elif self.status == "HALTED":
            status_color = COLOR_STATUS_HALTED
        elif "Connected" in self.status:
            status_color = "green"

        return Text.assemble(
            (" Server: ", "bold"),
            (self.server_info, "cyan"),
            (" (v", "bold"),
            (self.server_version, "magenta"),
            (")", "bold"),
            (" | Status: ", "bold"),
            (self.status, status_color),
            (" | Last Sync: ", "bold"),
            (self.last_sync, "yellow"),
        )
