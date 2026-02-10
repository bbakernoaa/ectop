from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Input

from ectop.client import EcflowClient
from ectop.widgets.content import MainContent
from ectop.widgets.modals.variables import VariableTweaker
from ectop.widgets.modals.why import WhyInspector
from ectop.widgets.search import SearchBox
from ectop.widgets.sidebar import SuiteTree

# --- Configuration ---
ECFLOW_HOST = "localhost"
ECFLOW_PORT = 3141

class Ectop(App):
    """A Textual-based TUI for monitoring and controlling ecFlow."""

    CSS = """
    Screen {
        background: #1a1b26;
    }

    /* Left Sidebar (Tree) */
    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid #565f89;
        background: #16161e;
    }

    Tree {
        background: #16161e;
        color: #a9b1d6;
        padding: 1;
    }

    /* Right Content (Tabs) */
    #main_content {
        width: 70%;
        height: 100%;
    }

    TabbedContent {
        height: 100%;
    }

    /* Content Areas */
    RichLog {
        background: #24283b;
        color: #c0caf5;
        border: none;
    }

    .code_view {
        background: #24283b;
        padding: 1;
        width: 100%;
        height: auto;
    }

    #search_box {
        dock: top;
        display: none;
        background: #24283b;
        color: #c0caf5;
        border: tall #565f89;
    }

    #search_box.visible {
        display: block;
    }

    #why_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 60%;
        height: 60%;
    }

    #why_title {
        text-align: center;
        background: #565f89;
        color: white;
        margin-bottom: 1;
    }

    #confirm_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 40%;
        height: 20%;
    }

    #confirm_message {
        text-align: center;
        margin-bottom: 1;
    }

    #confirm_actions {
        align: center middle;
    }

    #confirm_actions Button {
        margin: 0 1;
    }

    #var_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 80%;
        height: 80%;
    }

    #var_title {
        text-align: center;
        background: #565f89;
        color: white;
        margin-bottom: 1;
    }

    #var_input.hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Tree"),
        Binding("l", "load_node", "Load Logs/Script"),
        Binding("s", "suspend", "Suspend"),
        Binding("u", "resume", "Resume"),
        Binding("k", "kill", "Kill"),
        Binding("f", "force", "Force Complete"),
        Binding("/", "search", "Search"),
        Binding("w", "why", "Why?"),
        Binding("e", "edit_script", "Edit & Rerun"),
        Binding("t", "toggle_live", "Toggle Live Log"),
        Binding("v", "variables", "Variables"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SearchBox(placeholder="Search nodes...", id="search_box")
        yield Horizontal(
            Container(SuiteTree("ecFlow Server", id="suite_tree"), id="sidebar"),
            MainContent(id="main_content"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Connect to ecFlow and load the initial tree."""
        try:
            self.ecflow_client = EcflowClient(ECFLOW_HOST, ECFLOW_PORT)
            self.ecflow_client.ping()
            self.action_refresh()
            self.set_interval(2.0, self._live_log_tick)
        except Exception as e:
            self.notify(f"Connection Failed: {e}", severity="error", timeout=10)
            tree = self.query_one("#suite_tree", SuiteTree)
            tree.root.label = "[red]Connection Failed (Check Host/Port)[/]"

    def action_refresh(self) -> None:
        """Fetch suites from server and rebuild the tree."""
        tree = self.query_one("#suite_tree", SuiteTree)
        try:
            self.ecflow_client.sync_local()
            defs = self.ecflow_client.get_defs()
            tree.update_tree(self.ecflow_client.host, self.ecflow_client.port, defs)
            self.notify("Tree Refreshed")
        except Exception as e:
            self.notify(f"Refresh Error: {e}", severity="error")

    def get_selected_path(self):
        """Helper to get the ecFlow path of the selected node."""
        node = self.query_one("#suite_tree", SuiteTree).cursor_node
        return node.data if node else None

    def action_load_node(self) -> None:
        """Fetch Output, Script, and Job files for the selected node."""
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return

        self.notify(f"Loading files for {path}...")
        content_area = self.query_one("#main_content", MainContent)

        # 1. Output Log
        try:
            content = self.ecflow_client.file(path, "jobout")
            content_area.update_log(content)
        except Exception:
            content_area.show_error("#log_output", "File type 'jobout' not found (Has the task run yet?)")

        # 2. Script
        try:
            content = self.ecflow_client.file(path, "script")
            content_area.update_script(content)
        except Exception:
            content_area.show_error("#view_script", "File type 'script' not available.")

        # 3. Job
        try:
            content = self.ecflow_client.file(path, "job")
            content_area.update_job(content)
        except Exception:
            content_area.show_error("#view_job", "File type 'job' not available.")

    def _run_client_command(self, command_name, path):
        """Generic helper to run ecflow commands."""
        if not path:
            return
        try:
            getattr(self.ecflow_client, command_name)(path)
            self.notify(f"{command_name.replace('_', ' ').capitalize()}: {path}")
            self.action_refresh()
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_suspend(self):
        self._run_client_command("suspend", self.get_selected_path())

    def action_resume(self):
        self._run_client_command("resume", self.get_selected_path())

    def action_kill(self):
        self._run_client_command("kill", self.get_selected_path())

    def action_force(self):
        self._run_client_command("force_complete", self.get_selected_path())

    def action_toggle_live(self):
        content_area = self.query_one("#main_content", MainContent)
        content_area.is_live = not content_area.is_live
        state = "ON" if content_area.is_live else "OFF"
        self.notify(f"Live Log: {state}")
        if content_area.is_live:
            content_area.active = "tab_output"

    def _live_log_tick(self):
        content_area = self.query_one("#main_content", MainContent)
        if content_area.is_live and content_area.active == "tab_output":
            path = self.get_selected_path()
            if path:
                try:
                    # In a real app we might want to fetch only the end,
                    # but for now we'll follow the requirement to fetch and compare length
                    content = self.ecflow_client.file(path, "jobout")
                    content_area.update_log(content, append=True)
                except Exception:
                    pass

    def action_why(self):
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return
        self.push_screen(WhyInspector(path, self.ecflow_client))

    def action_variables(self):
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return
        self.push_screen(VariableTweaker(path, self.ecflow_client))

    def action_edit_script(self):
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return

        import os
        import subprocess
        import tempfile

        try:
            content = self.ecflow_client.file(path, "script")
            with tempfile.NamedTemporaryFile(suffix=".ecf", delete=False, mode='w') as f:
                f.write(content)
                temp_path = f.name

            editor = os.environ.get("EDITOR", "vi")

            with self.suspend():
                subprocess.run([editor, temp_path])

            with open(temp_path) as f:
                new_content = f.read()

            os.unlink(temp_path)

            if new_content != content:
                self.ecflow_client.alter(path, "change", "script", new_content)
                self.notify("Script updated on server")
                # Prompt for re-queue
                self._prompt_requeue(path)
            else:
                self.notify("No changes detected")

        except Exception as e:
            self.notify(f"Edit Error: {e}", severity="error")

    def _prompt_requeue(self, path):
        # Using a simple notification with a callback might be hard in current Textual
        # I'll create a simple modal for this
        from ectop.widgets.modals.confirm import ConfirmModal
        self.push_screen(ConfirmModal(f"Re-queue {path} now?", lambda: self.ecflow_client.requeue(path)))

    def action_search(self) -> None:
        """Show the search box."""
        search_box = self.query_one("#search_box", SearchBox)
        search_box.add_class("visible")
        search_box.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        if event.input.id == "search_box":
            query = event.value
            if query:
                tree = self.query_one("#suite_tree", SuiteTree)
                if tree.find_and_select(query):
                    # Keep focus on search box to allow cycling with Enter
                    pass
                else:
                    self.notify(f"No match found for '{query}'", severity="warning")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Optional: live search as typing? The requirement says 'As they type'."""
        if event.input.id == "search_box":
            query = event.value
            if query:
                tree = self.query_one("#suite_tree", SuiteTree)
                tree.find_and_select(query)
