# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Main content area for displaying ecFlow node information.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from typing import Any

from rich.syntax import Syntax
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import RichLog, Static, TabbedContent, TabPane


class MainContent(TabbedContent):
    """
    A tabbed container to display Output logs, Scripts, and Job files.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.

    Attributes
    ----------
    is_live : bool
        Whether live log updates are enabled.
    last_log_size : int
        The size of the log content at the last update.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the MainContent widget.

        Parameters
        ----------
        *args : Any
            Positional arguments for TabbedContent.
        **kwargs : Any
            Keyword arguments for TabbedContent.
        """
        super().__init__(*args, **kwargs)
        self.is_live: bool = False
        self.last_log_size: int = 0

    def compose(self) -> ComposeResult:
        """
        Compose the tabs for Output, Script, and Job.

        Returns
        -------
        ComposeResult
            The UI components for the tabs.
        """
        with TabPane("Output", id="tab_output"):
            yield RichLog(markup=True, highlight=True, id="log_output")
        with TabPane("Script (.ecf)", id="tab_script"):
            with VerticalScroll():
                yield Static("", id="view_script", classes="code_view")
        with TabPane("Job (Processed)", id="tab_job"):
            with VerticalScroll():
                yield Static("", id="view_job", classes="code_view")

    def update_log(self, content: str, append: bool = False) -> None:
        """
        Update the Output log tab.

        Parameters
        ----------
        content : str
            The content to display or append.
        append : bool, optional
            Whether to append to existing content, by default False.
        """
        widget = self.query_one("#log_output", RichLog)
        if not append:
            widget.clear()
            self.last_log_size = len(content)
            widget.write(content)
        else:
            new_content = content[self.last_log_size :]
            if new_content:
                widget.write(new_content)
                self.last_log_size = len(content)

    def update_script(self, content: str) -> None:
        """
        Update the Script tab with syntax highlighting.

        Parameters
        ----------
        content : str
            The script content.
        """
        widget = self.query_one("#view_script", Static)
        syntax = Syntax(content, "bash", theme="monokai", line_numbers=True)
        widget.update(syntax)

    def update_job(self, content: str) -> None:
        """
        Update the Job tab with syntax highlighting.

        Parameters
        ----------
        content : str
            The job content.
        """
        widget = self.query_one("#view_job", Static)
        syntax = Syntax(content, "bash", theme="monokai", line_numbers=True)
        widget.update(syntax)

    def show_error(self, widget_id: str, message: str) -> None:
        """
        Display an error message in a specific widget.

        Parameters
        ----------
        widget_id : str
            The ID of the widget where the error should be shown.
        message : str
            The error message to display.
        """
        widget = self.query_one(widget_id)
        if isinstance(widget, RichLog):
            widget.write(f"[italic red]{message}[/]")
        elif isinstance(widget, Static):
            widget.update(f"[italic red]{message}[/]")
