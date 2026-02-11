"""
Modal screen for inspecting why an ecFlow node is not running.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.

If you modify features, API, or usage, you MUST update the documentation immediately.
"""

import re
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Tree
from textual.widgets.tree import TreeNode

from ectop.client import EcflowClient


class WhyInspector(ModalScreen[None]):
    """
    A modal screen to inspect dependencies and triggers of an ecFlow node.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("w", "close", "Close"),
    ]

    def __init__(self, node_path: str, client: EcflowClient) -> None:
        """
        Initialize the WhyInspector.

        Parameters
        ----------
        node_path : str
            The absolute path to the ecFlow node.
        client : EcflowClient
            The ecFlow client instance.
        """
        super().__init__()
        self.node_path: str = node_path
        self.client: EcflowClient = client

    def compose(self) -> ComposeResult:
        """
        Compose the modal UI.

        Returns
        -------
        ComposeResult
            The UI components for the modal.
        """
        with Vertical(id="why_container"):
            yield Static(f"Why is {self.node_path} not running?", id="why_title")
            yield Tree("Dependencies", id="dep_tree")
            with Horizontal(id="why_actions"):
                yield Button("Close", variant="primary", id="close_btn")

    def on_mount(self) -> None:
        """Handle the mount event to initialize the dependency tree."""
        self.refresh_deps()

    def action_close(self) -> None:
        """Close the modal."""
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Parameters
        ----------
        event : Button.Pressed
            The button press event.
        """
        if event.button.id == "close_btn":
            self.app.pop_screen()

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        """
        Jump to the selected dependency node in the main tree.

        Parameters
        ----------
        event : Tree.NodeSelected[str]
            The tree node selection event.
        """
        node_path = event.node.data
        if node_path:
            from ectop.widgets.sidebar import SuiteTree

            try:
                tree = self.app.query_one("#suite_tree", SuiteTree)
                tree.select_by_path(node_path)
                self.app.notify(f"Jumped to {node_path}")
                self.app.pop_screen()
            except Exception as e:
                self.app.notify(f"Failed to jump: {e}", severity="error")

    @work(thread=True)
    def refresh_deps(self) -> None:
        """Fetch dependencies from the server and rebuild the tree."""
        tree = self.query_one("#dep_tree", Tree)
        self.call_from_thread(tree.clear)

        try:
            self.client.sync_local()
            defs = self.client.get_defs()
            if not defs:
                self.call_from_thread(self._update_tree_root, tree, "Server Empty")
                return

            node = defs.find_abs_node(self.node_path)

            if not node:
                self.call_from_thread(self._update_tree_root, tree, "Node not found")
                return

            # Populate the tree (UI operations must be on main thread)
            self.call_from_thread(self._populate_dep_tree, tree, node, defs)

        except Exception as e:
            self.call_from_thread(self._update_tree_root, tree, f"Error: {e}")

    def _update_tree_root(self, tree: Tree, label: str) -> None:
        """
        Update the tree root label.

        Parameters
        ----------
        tree : Tree
            The tree widget.
        label : str
            The new label for the root.
        """
        tree.root.label = label

    def _populate_dep_tree(self, tree: Tree, node: Any, defs: Any) -> None:
        """
        Populate the dependency tree UI.

        Parameters
        ----------
        tree : Tree
            The tree widget to populate.
        node : Any
            The ecFlow node.
        defs : Any
            The ecFlow definitions.
        """
        # Server's "Why" explanation
        try:
            # Standard ecflow node.get_why() might require a client sync
            # but usually it's available on the node if it was synced.
            why_str = node.get_why()
            if why_str:
                tree.root.add(f"💡 Reason: [italic]{why_str}[/]", expand=True)
        except AttributeError:
            pass

        # Triggers
        trigger = node.get_trigger()
        if trigger:
            t_node = tree.root.add("Triggers")
            self._parse_expression(t_node, trigger.get_expression(), defs)

        # Complete
        complete = node.get_complete()
        if complete:
            c_node = tree.root.add("Complete Expression")
            self._parse_expression(c_node, complete.get_expression(), defs)

        # Limits
        self._add_limit_deps(tree.root, node)

        # Times, Dates, Crons
        self._add_time_deps(tree.root, node)

        tree.root.expand_all()

    def _add_limit_deps(self, parent_ui_node: TreeNode[str], node: Any) -> None:
        """
        Add limit-based dependencies to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        node : Any
            The ecFlow node to inspect.
        """
        inlimits = list(node.inlimits)
        if inlimits:
            limit_node = parent_ui_node.add("Limits")
            for il in inlimits:
                limit_node.add(f"🔒 Limit: {il.name()} (Path: {il.value()})")

    def _parse_expression(self, parent_ui_node: TreeNode[str], expr_str: str, defs: Any) -> None:
        """
        Parse an ecFlow expression and add it to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        expr_str : str
            The expression string to parse.
        defs : Any
            The ecFlow definitions for node lookups.
        """
        if " or " in expr_str:
            parts = expr_str.split(" or ")
            or_node = parent_ui_node.add("OR (Any must be true)", expand=True)
            for part in parts:
                self._parse_expression(or_node, part.strip().strip("()"), defs)
            return

        if " and " in expr_str:
            parts = expr_str.split(" and ")
            and_node = parent_ui_node.add("AND (All must be true)", expand=True)
            for part in parts:
                self._parse_expression(and_node, part.strip().strip("()"), defs)
            return

        # Leaf node (actual condition)
        # Match paths and optional state comparison
        match = re.search(r"(/[a-zA-Z0-9_/]+)(\s*==\s*(\w+))?", expr_str)
        if match:
            path = match.group(1)
            expected_state = match.group(3) or "complete"
            target_node = defs.find_abs_node(path)
            if target_node:
                actual_state = str(target_node.get_state())
                is_met = actual_state == expected_state
                icon = "✅" if is_met else "❌"
                parent_ui_node.add(f"{icon} {path} == {actual_state} (Expected: {expected_state})", data=path)
            else:
                parent_ui_node.add(f"❓ {path} (Not found)")
        else:
            parent_ui_node.add(f"📝 {expr_str}")

    def _add_time_deps(self, parent_ui_node: TreeNode[str], node: Any) -> None:
        """
        Add time-based dependencies to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        node : Any
            The ecFlow node to inspect.
        """
        for t in node.get_times():
            parent_ui_node.add(f"⏳ Time: {t}")
        for d in node.get_dates():
            parent_ui_node.add(f"📅 Date: {d}")
        for c in node.get_crons():
            parent_ui_node.add(f"⏰ Cron: {c}")
