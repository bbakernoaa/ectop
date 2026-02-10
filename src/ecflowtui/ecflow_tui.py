import ecflow
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, RichLog, TabbedContent, TabPane, Static
from textual.containers import Container, Horizontal, VerticalScroll
from textual.binding import Binding
from rich.syntax import Syntax
from rich.text import Text

# --- Configuration ---
ECFLOW_HOST = "localhost"
ECFLOW_PORT = 3141

# --- State Icons ---
STATE_MAP = {
    "unknown": "⚪",
    "complete": "🟢",
    "queued": "🔵",
    "aborted": "🔴",
    "submitted": "🟡",
    "active": "🔥",
    "suspended": "🟠"
}

class EcflowTUI(App):
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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Tree"),
        Binding("l", "load_node", "Load Logs/Script"),
        Binding("s", "suspend", "Suspend"),
        Binding("u", "resume", "Resume"),
        Binding("k", "kill", "Kill"),
        Binding("f", "force", "Force Complete"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Horizontal(
            # Left Sidebar
            Container(
                Tree("ecFlow Server", id="suite_tree"),
                id="sidebar"
            ),
            # Right Content
            Container(
                TabbedContent(
                    TabPane("Output", id="tab_output", children=[
                        RichLog(markup=True, highlight=True, id="log_output")
                    ]),
                    TabPane("Script (.ecf)", id="tab_script", children=[
                        VerticalScroll(Static("", id="view_script", classes="code_view"))
                    ]),
                    TabPane("Job (Processed)", id="tab_job", children=[
                        VerticalScroll(Static("", id="view_job", classes="code_view"))
                    ]),
                ),
                id="main_content"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Connect to ecFlow and load the initial tree."""
        try:
            self.client = ecflow.Client(ECFLOW_HOST, ECFLOW_PORT)
            self.client.ping() # Check connection
            self.action_refresh()
        except RuntimeError as e:
            self.notify(f"Connection Failed: {e}", severity="error", timeout=10)
            tree = self.query_one("#suite_tree", Tree)
            tree.root.label = "[red]Connection Failed (Check Host/Port)[/]"

    # --- Tree Management ---

    def action_refresh(self) -> None:
        """Fetch suites from server and rebuild the tree."""
        tree = self.query_one("#suite_tree", Tree)
        tree.clear()
        
        try:
            self.client.sync_local()
            defs = self.client.get_defs()
            
            if not defs:
                tree.root.label = "Server Empty"
                return
            
            tree.root.label = f"🌍 {ECFLOW_HOST}:{ECFLOW_PORT}"
            
            for suite in defs.suites:
                self._add_node(tree.root, suite)
                
            self.notify("Tree Refreshed")
            
        except Exception as e:
            self.notify(f"Refresh Error: {e}", severity="error")

    def _add_node(self, parent_ui_node, ecflow_node):
        """Recursively add ecflow nodes to the UI tree."""
        # Determine icon and style based on node type and state
        state = str(ecflow_node.get_state())
        icon = STATE_MAP.get(state, "⚪")
        
        is_family = isinstance(ecflow_node, (ecflow.Family, ecflow.Suite))
        type_icon = "📂" if is_family else "⚙️"
        
        label = Text(f"{type_icon} {ecflow_node.name()} ")
        label.append(f"[{state}]", style="bold italic")
        
        # Add node to UI
        # We store the absolute path in `data` to reference it later
        new_ui_node = parent_ui_node.add(
            label, 
            data=ecflow_node.abs_node_path(),
            expand=False # Collapse by default to save space
        )
        
        # Recurse if there are children
        if hasattr(ecflow_node, 'nodes'):
            for child in ecflow_node.nodes:
                self._add_node(new_ui_node, child)

    def get_selected_path(self):
        """Helper to get the ecFlow path of the selected node."""
        node = self.query_one("#suite_tree", Tree).cursor_node
        return node.data if node else None

    # --- File/Log Loading ---

    def action_load_node(self) -> None:
        """Fetch Output, Script, and Job files for the selected node."""
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return

        self.notify(f"Loading files for {path}...")
        
        # 1. Output Log (RichLog)
        self._load_log_content(path, 'jobout', "#log_output")
        
        # 2. Script (Syntax Highlighted)
        self._load_code_content(path, 'script', "#view_script")
        
        # 3. Job (Syntax Highlighted)
        self._load_code_content(path, 'job', "#view_job")

    def _load_log_content(self, path, file_type, widget_id):
        widget = self.query_one(widget_id, RichLog)
        widget.clear()
        try:
            content = self.client.file(path, file_type)
            widget.write(content)
        except RuntimeError:
            widget.write(f"[italic red]File type '{file_type}' not found (Has the task run yet?)[/]")

    def _load_code_content(self, path, file_type, widget_id):
        widget = self.query_one(widget_id, Static)
        try:
            content = self.client.file(path, file_type)
            # Create a Syntax object for nice highlighting
            syntax = Syntax(content, "bash", theme="monokai", line_numbers=True)
            widget.update(syntax)
        except RuntimeError:
            widget.update(f"[italic red]File type '{file_type}' not available.[/]")

    # --- Control Actions ---

    def _run_client_command(self, command_name, path):
        """Generic helper to run ecflow commands."""
        if not path:
            return
        
        try:
            # Dynamically call the method on self.client (e.g., client.suspend(path))
            getattr(self.client, command_name)(path)
            self.notify(f"{command_name.capitalize()}: {path}")
            # Refresh tree to show new state
            self.action_refresh()
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_suspend(self): self._run_client_command("suspend", self.get_selected_path())
    def action_resume(self): self._run_client_command("resume", self.get_selected_path())
    def action_kill(self): self._run_client_command("kill", self.get_selected_path())
    def action_force(self): self._run_client_command("force_complete", self.get_selected_path())

if __name__ == "__main__":
    EcflowTUI().run()
