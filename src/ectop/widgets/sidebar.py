"""
Sidebar widget for the ecFlow suite tree.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from typing import Any

import ecflow
from rich.text import Text
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from ectop.client import STATE_MAP


class SuiteTree(Tree[str]):
    """
    A tree widget to display ecFlow suites and nodes.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the SuiteTree.

        Parameters
        ----------
        *args : Any
            Positional arguments for the Tree widget.
        **kwargs : Any
            Keyword arguments for the Tree widget.
        """
        super().__init__(*args, **kwargs)

    def update_tree(self, client_host: str, client_port: int, defs: ecflow.Defs | None) -> None:
        """
        Rebuild the tree from ecFlow definitions.

        Parameters
        ----------
        client_host : str
            The hostname of the ecFlow server.
        client_port : int
            The port of the ecFlow server.
        defs : ecflow.Defs | None
            The ecFlow definitions to display.
        """
        self.clear()
        if not defs:
            self.root.label = "Server Empty"
            return

        self.root.label = f"🌍 {client_host}:{client_port}"
        for suite in defs.suites:
            self._populate_tree(self.root, suite)

    def _populate_tree(self, parent_ui_node: TreeNode[str], ecflow_node: ecflow.Node) -> None:
        """
        Recursively add ecflow nodes to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        ecflow_node : ecflow.Node
            The ecFlow node to add.
        """
        state = str(ecflow_node.get_state())
        icon = STATE_MAP.get(state, "⚪")

        # Family and Suite have 'nodes' attribute, Task doesn't.
        # However, they all inherit from ecflow.Node.
        is_family = isinstance(ecflow_node, (ecflow.Family, ecflow.Suite))
        type_icon = "📂" if is_family else "⚙️"

        label = Text(f"{icon} {type_icon} {ecflow_node.name()} ")
        label.append(f"[{state}]", style="bold italic")

        new_ui_node = parent_ui_node.add(
            label,
            data=ecflow_node.abs_node_path(),
            expand=False,
        )

        if hasattr(ecflow_node, "nodes"):
            for child in ecflow_node.nodes:
                self._populate_tree(new_ui_node, child)

    def find_and_select(self, query: str) -> bool:
        """
        Find nodes matching query and select the next one.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        bool
            True if a match was found and selected, False otherwise.
        """
        query = query.lower()
        all_nodes = list(self.root.descendants)

        # Start from current cursor if possible
        start_index = 0
        if self.cursor_node in all_nodes:
            start_index = all_nodes.index(self.cursor_node) + 1

        # Search from start_index to end, then wrap around
        for i in range(len(all_nodes)):
            node = all_nodes[(start_index + i) % len(all_nodes)]
            if query in str(node.label).lower() or (node.data and query in node.data.lower()):
                self._select_and_reveal(node)
                return True
        return False

    def _select_and_reveal(self, node: TreeNode[str]) -> None:
        """
        Select a node and expand all its parents.

        Parameters
        ----------
        node : TreeNode[str]
            The node to select and reveal.
        """
        self.select_node(node)
        parent = node.parent
        while parent:
            parent.expand()
            parent = parent.parent
        self.scroll_to_node(node)
