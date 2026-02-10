from rich.syntax import Syntax
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import RichLog, Static, TabbedContent, TabPane


class MainContent(TabbedContent):
    is_live = False
    last_log_size = 0

    def compose(self) -> ComposeResult:
        with TabPane("Output", id="tab_output"):
            yield RichLog(markup=True, highlight=True, id="log_output")
        with TabPane("Script (.ecf)", id="tab_script"):
            with VerticalScroll():
                yield Static("", id="view_script", classes="code_view")
        with TabPane("Job (Processed)", id="tab_job"):
            with VerticalScroll():
                yield Static("", id="view_job", classes="code_view")

    def update_log(self, content, append=False):
        widget = self.query_one("#log_output", RichLog)
        if not append:
            widget.clear()
            self.last_log_size = len(content)
            widget.write(content)
        else:
            new_content = content[self.last_log_size:]
            if new_content:
                widget.write(new_content)
                self.last_log_size = len(content)

    def update_script(self, content):
        widget = self.query_one("#view_script", Static)
        syntax = Syntax(content, "bash", theme="monokai", line_numbers=True)
        widget.update(syntax)

    def update_job(self, content):
        widget = self.query_one("#view_job", Static)
        syntax = Syntax(content, "bash", theme="monokai", line_numbers=True)
        widget.update(syntax)

    def show_error(self, widget_id, message):
        widget = self.query_one(widget_id)
        if isinstance(widget, RichLog):
            widget.write(f"[italic red]{message}[/]")
        else:
            widget.update(f"[italic red]{message}[/]")
