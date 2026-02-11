"""
Status bar widget for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import Static


class StatusBar(Static):
    """
    A status bar widget to display server information and health.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the StatusBar."""
        super().__init__(*args, **kwargs)
        self.server_info: str = "Disconnected"
        self.last_sync: str = "Never"
        self.status: str = "Unknown"

    def update_status(self, host: str, port: int, status: str = "Connected") -> None:
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
        """
        self.server_info = f"{host}:{port}"
        self.status = status
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
        return Text.assemble(
            (" Server: ", "bold"),
            (self.server_info, "cyan"),
            (" | Status: ", "bold"),
            (self.status, "green" if "Connected" in self.status else "red"),
            (" | Last Sync: ", "bold"),
            (self.last_sync, "yellow"),
        )
