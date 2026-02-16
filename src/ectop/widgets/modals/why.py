# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Modal screen for inspecting why an ecFlow node is not running.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Tree
from textual.widgets.tree import TreeNode

from ectop.client import EcflowClient
from ectop.constants import (
    EXPR_AND_LABEL,
    EXPR_OR_LABEL,
    ICON_CRON,
    ICON_DATE,
    ICON_MET,
    ICON_NOT_MET,
    ICON_NOTE,
    ICON_REASON,
    ICON_TIME,
    ICON_UNKNOWN,
)

if TYPE_CHECKING:
    from ecflow import Defs, Node


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

        Returns
        -------
        None
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
        """
        Handle the mount event to initialize the dependency tree.

        Returns
        -------
        None
        """
        self.refresh_deps()

    def action_close(self) -> None:
        """
        Close the modal.

        Returns
        -------
        None
        """
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Parameters
        ----------
        event : Button.Pressed
            The button press event.

        Returns
        -------
        None
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

        Returns
        -------
        None
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

    def refresh_deps(self) -> None:
        """
        Fetch dependencies from the server and rebuild the tree.

        Returns
        -------
        None
        """
        tree = self.query_one("#dep_tree", Tree)
        self._refresh_deps_worker(tree)

    @work(thread=True)
    def _refresh_deps_worker(self, tree: Tree) -> None:
        """
        Worker to fetch dependencies from the server and rebuild the tree in a background thread.

        Parameters
        ----------
        tree : Tree
            The tree widget to refresh.

        Returns
        -------
        None

        Notes
        -----
        This is a background worker that performs blocking I/O.
        """
        self._refresh_deps_logic(tree)

    def _refresh_deps_logic(self, tree: Tree) -> None:
        """
        The actual logic for fetching dependencies and updating the UI tree.

        Parameters
        ----------
        tree : Tree
            The tree widget to refresh.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If server synchronization fails.

        Notes
        -----
        This method can be called directly for testing.
        """
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

        except RuntimeError as e:
            self.call_from_thread(self._update_tree_root, tree, f"Error: {e}")
        except Exception as e:
            self.call_from_thread(self._update_tree_root, tree, f"Unexpected Error: {e}")

    def _update_tree_root(self, tree: Tree, label: str) -> None:
        """
        Update the tree root label.

        Parameters
        ----------
        tree : Tree
            The tree widget.
        label : str
            The new label for the root.

        Returns
        -------
        None
        """
        tree.root.label = label

    def _populate_dep_tree(self, tree: Tree, node: Node, defs: Defs) -> None:
        """
        Populate the dependency tree UI.

        Parameters
        ----------
        tree : Tree
            The tree widget to populate.
        node : Node
            The ecFlow node.
        defs : Defs
            The ecFlow definitions.

        Returns
        -------
        None
        """
        # Server's "Why" explanation
        try:
            # Standard ecflow node.get_why() might require a client sync
            # but usually it's available on the node if it was synced.
            why_str = node.get_why()
            if why_str:
                tree.root.add(f"{ICON_REASON} Reason: [italic]{why_str}[/]", expand=True)
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

    def _add_limit_deps(self, parent_ui_node: TreeNode[str], node: Node) -> None:
        """
        Add limit-based dependencies to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        node : Node
            The ecFlow node to inspect.

        Returns
        -------
        None
        """
        inlimits = list(node.inlimits)
        if inlimits:
            limit_node = parent_ui_node.add("Limits")
            for il in inlimits:
                limit_node.add(f"🔒 Limit: {il.name()} (Path: {il.value()})")

    def _parse_expression(self, parent_ui_node: TreeNode[str], expr_str: str, defs: Defs) -> None:
        """
        Parse an ecFlow expression and add it to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        expr_str : str
            The expression string to parse.
        defs : Defs
            The ecFlow definitions for node lookups.

        Returns
        -------
        None
        """
        expr_str = expr_str.strip()
        if not expr_str:
            return

        # Remove outer parentheses if they wrap the whole expression
        while expr_str.startswith("(") and expr_str.endswith(")"):
            depth = 0
            is_pair = True
            for i, char in enumerate(expr_str):
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                if depth == 0 and i < len(expr_str) - 1:
                    is_pair = False
                    break
            if is_pair:
                expr_str = expr_str[1:-1].strip()
            else:
                break

        # Find top-level ' or ' or ' and ' (lowest precedence first)
        for op, label in [(" or ", EXPR_OR_LABEL), (" and ", EXPR_AND_LABEL)]:
            depth = 0
            for i in range(len(expr_str)):
                if expr_str[i] == "(":
                    depth += 1
                elif expr_str[i] == ")":
                    depth -= 1
                elif depth == 0 and expr_str[i : i + len(op)] == op:
                    op_node = parent_ui_node.add(label, expand=True)
                    left = expr_str[:i].strip()
                    right = expr_str[i + len(op) :].strip()
                    self._parse_expression(op_node, left, defs)
                    self._parse_expression(op_node, right, defs)
                    return

        # Leaf node (actual condition)
        # Support various comparisons: ==, !=, <, >, <=, >=
        match = re.search(r"(/[a-zA-Z0-9_/]+)(\s*(==|!=|<=|>=|<|>)\s*(\w+))?", expr_str)
        if match:
            path = match.group(1)
            op = match.group(3) or "=="
            expected_state = match.group(4) or "complete"
            target_node = defs.find_abs_node(path)

            if target_node:
                actual_state = str(target_node.get_state())
                # Basic evaluation logic for common states
                is_met = False
                if op == "==":
                    is_met = actual_state == expected_state
                elif op == "!=":
                    is_met = actual_state != expected_state
                # Other operators are harder to evaluate without state ordering knowledge,
                # but we show the status anyway.

                icon = ICON_MET if is_met else ICON_NOT_MET
                parent_ui_node.add(f"{icon} {path} {op} {actual_state} (Expected: {expected_state})", data=path)
            else:
                parent_ui_node.add(f"{ICON_UNKNOWN} {path} (Not found)")
        else:
            parent_ui_node.add(f"{ICON_NOTE} {expr_str}")

    def _add_time_deps(self, parent_ui_node: TreeNode[str], node: Node) -> None:
        """
        Add time-based dependencies to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        node : Node
            The ecFlow node to inspect.

        Returns
        -------
        None
        """
        for t in node.get_times():
            parent_ui_node.add(f"{ICON_TIME} Time: {t}")
        for d in node.get_dates():
            parent_ui_node.add(f"{ICON_DATE} Date: {d}")
        for c in node.get_crons():
            parent_ui_node.add(f"{ICON_CRON} Cron: {c}")
