# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Sidebar widget for the ecFlow suite tree.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from typing import TYPE_CHECKING, Any

import ecflow
from rich.text import Text
from textual import work
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from ectop.constants import (
    ICON_FAMILY,
    ICON_SERVER,
    ICON_TASK,
    LOADING_PLACEHOLDER,
    STATE_MAP,
)

if TYPE_CHECKING:
    from ecflow import Defs, Node


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

        Returns
        -------
        None
        """
        super().__init__(*args, **kwargs)
        self.defs: Defs | None = None

    def update_tree(self, client_host: str, client_port: int, defs: "Defs | None") -> None:
        """
        Rebuild the tree from ecFlow definitions using lazy loading.

        Parameters
        ----------
        client_host : str
            The hostname of the ecFlow server.
        client_port : int
            The port of the ecFlow server.
        defs : ecflow.Defs | None
            The ecFlow definitions to display.

        Returns
        -------
        None

        Notes
        -----
        This method is typically called from the main thread after a sync.
        """
        self.defs = defs
        self._all_paths_cache: list[str] | None = None
        self.clear()
        if not defs:
            self.root.label = "Server Empty"
            return

        self.root.label = f"{ICON_SERVER} {client_host}:{client_port}"
        for suite in defs.suites:
            self._add_node_to_ui(self.root, suite)

    def _add_node_to_ui(self, parent_ui_node: TreeNode[str], ecflow_node: "Node") -> TreeNode[str]:
        """
        Add a single ecflow node to the UI tree.

        Parameters
        ----------
        parent_ui_node : TreeNode[str]
            The parent node in the Textual tree.
        ecflow_node : ecflow.Node
            The ecFlow node to add.

        Returns
        -------
        TreeNode[str]
            The newly created UI node.
        """
        state = str(ecflow_node.get_state())
        icon = STATE_MAP.get(state, "⚪")

        is_container = isinstance(ecflow_node, ecflow.Family | ecflow.Suite)
        type_icon = ICON_FAMILY if is_container else ICON_TASK

        label = Text(f"{icon} {type_icon} {ecflow_node.name()} ")
        label.append(f"[{state}]", style="bold italic")

        new_ui_node = parent_ui_node.add(
            label,
            data=ecflow_node.abs_node_path(),
            expand=False,
        )

        # If it's a container and has children, add a placeholder for lazy loading
        if is_container and hasattr(ecflow_node, "nodes"):
            # Use a more efficient check for presence of children than len(list(...))
            has_children = False
            try:
                # Check if there is at least one child
                next(iter(ecflow_node.nodes))
                has_children = True
            except (StopIteration, RuntimeError):
                pass

            if has_children:
                new_ui_node.add(LOADING_PLACEHOLDER, allow_expand=False)

        return new_ui_node

    def on_tree_node_expanded(self, event: Tree.NodeExpanded[str]) -> None:
        """
        Handle node expansion to load children on demand.

        Parameters
        ----------
        event : Tree.NodeExpanded[str]
            The expansion event.

        Returns
        -------
        None
        """
        node = event.node
        self._load_children(node)

    def _load_children(self, ui_node: TreeNode[str], sync: bool = False) -> None:
        """
        Load children for a UI node if they haven't been loaded yet.

        Parameters
        ----------
        ui_node : TreeNode[str]
            The UI node to load children for.
        sync : bool, optional
            Whether to load children synchronously, by default False.

        Returns
        -------
        None

        Raises
        ------
        None

        Notes
        -----
        Uses `_load_children_worker` for async loading.
        """
        if not ui_node.data or not self.defs:
            return

        # Check if we have the placeholder
        if len(ui_node.children) == 1 and str(ui_node.children[0].label) == LOADING_PLACEHOLDER:
            ui_node.children[0].remove()
            if sync:
                ecflow_node = self.defs.find_abs_node(ui_node.data)
                if ecflow_node and hasattr(ecflow_node, "nodes"):
                    for child in ecflow_node.nodes:
                        self._add_node_to_ui(ui_node, child)
            else:
                self._load_children_worker(ui_node, ui_node.data)

    @work(thread=True)
    def _load_children_worker(self, ui_node: TreeNode[str], node_path: str) -> None:
        """
        Worker to load children nodes in a background thread.

        Parameters
        ----------
        ui_node : TreeNode[str]
            The UI node to populate.
        node_path : str
            The absolute path of the ecFlow node.

        Returns
        -------
        None

        Notes
        -----
        UI updates are scheduled back to the main thread using `call_from_thread`.
        """
        if not self.defs:
            return

        ecflow_node = self.defs.find_abs_node(node_path)
        if ecflow_node and hasattr(ecflow_node, "nodes"):
            for child in ecflow_node.nodes:
                self.app.call_from_thread(self._add_node_to_ui, ui_node, child)

    def find_and_select(self, query: str) -> bool:
        """
        Find nodes matching query in the ecFlow definitions and select them.

        This handles searching through unloaded parts of the tree.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        bool
            True if a match was found and selected, False otherwise.
        """
        if not self.defs:
            return False

        query = query.lower()

        # Build or use cached paths
        if not hasattr(self, "_all_paths_cache") or self._all_paths_cache is None:
            self._all_paths_cache = []
            for suite in self.defs.suites:
                self._all_paths_cache.append(suite.abs_node_path())
                for node in suite.get_all_nodes():
                    self._all_paths_cache.append(node.abs_node_path())

        all_paths = self._all_paths_cache

        # Start from current cursor if possible
        current_path = self.cursor_node.data if self.cursor_node else None
        start_index = 0
        if current_path and current_path in all_paths:
            try:
                start_index = all_paths.index(current_path) + 1
            except ValueError:
                start_index = 0

        # Search from start_index to end, then wrap around
        for i in range(len(all_paths)):
            path = all_paths[(start_index + i) % len(all_paths)]
            if query in path.lower():
                self.select_by_path(path)
                return True
        return False

    def select_by_path(self, path: str) -> None:
        """
        Select a node by its absolute ecFlow path, expanding parents as needed.

        Parameters
        ----------
        path : str
            The absolute path of the node to select.

        Returns
        -------
        None
        """
        if path == "/":
            self.select_node(self.root)
            return

        parts = path.strip("/").split("/")
        current_ui_node = self.root

        current_path = ""
        for part in parts:
            current_path += "/" + part
            # Load children synchronously to ensure they are available for selection
            self._load_children(current_ui_node, sync=True)
            current_ui_node.expand()

            found = False
            for child in current_ui_node.children:
                if child.data == current_path:
                    current_ui_node = child
                    found = True
                    break
            if not found:
                return

        self._select_and_reveal(current_ui_node)

    def _select_and_reveal(self, node: TreeNode[str]) -> None:
        """
        Select a node and expand all its parents.

        Parameters
        ----------
        node : TreeNode[str]
            The node to select and reveal.

        Returns
        -------
        None
        """
        self.select_node(node)
        parent = node.parent
        while parent:
            parent.expand()
            parent = parent.parent
        self.scroll_to_node(node)
