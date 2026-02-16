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
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Input, RichLog, Static, TabbedContent, TabPane


class MainContent(Vertical):
    """
    A container to display Output logs, Scripts, and Job files in tabs.

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
            Positional arguments for Vertical.
        **kwargs : Any
            Keyword arguments for Vertical.
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
        yield Input(placeholder="Search in content...", id="content_search", classes="hidden")
        with TabbedContent(id="content_tabs"):
            with TabPane("Output", id="tab_output"):
                yield RichLog(markup=True, highlight=True, id="log_output")
            with TabPane("Script (.ecf)", id="tab_script"):
                with VerticalScroll():
                    yield Static("", id="view_script", classes="code_view")
            with TabPane("Job (Processed)", id="tab_job"):
                with VerticalScroll():
                    yield Static("", id="view_job", classes="code_view")

    @property
    def active(self) -> str | None:
        """
        Get the active tab ID.

        Returns
        -------
        str | None
            The ID of the active tab.
        """
        return self.query_one("#content_tabs", TabbedContent).active

    @active.setter
    def active(self, value: str) -> None:
        """
        Set the active tab ID.

        Parameters
        ----------
        value : str
            The ID of the tab to activate.
        """
        self.query_one("#content_tabs", TabbedContent).active = value

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

    def action_search(self) -> None:
        """
        Toggle the content search input.

        Returns
        -------
        None
        """
        search_input = self.query_one("#content_search", Input)
        if "hidden" in search_input.classes:
            search_input.remove_class("hidden")
            search_input.focus()
        else:
            search_input.add_class("hidden")
            # Refocus the active tab's content
            active_tab = self.active
            if active_tab == "tab_output":
                self.query_one("#log_output").focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle content search submission.

        Parameters
        ----------
        event : Input.Submitted
            The input submission event.

        Returns
        -------
        None
        """
        if event.input.id == "content_search":
            query = event.value
            if not query:
                return

            self.app.notify(f"Searching for '{query}'...")
            # For now, we just notify of matches.
            # Real highlighting would require re-rendering content with markup.
            # In a future update, we could implement a more sophisticated highlighter.

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
