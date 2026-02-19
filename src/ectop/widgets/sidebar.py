# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Sidebar widget for the ecFlow suite tree.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

import threading
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
    ICON_UNKNOWN_STATE,
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
        self.current_filter: str | None = None
        self.filters: list[str | None] = [None, "aborted", "active", "queued", "submitted", "suspended"]

    def update_tree(self, client_host: str, client_port: int, defs: Defs | None) -> None:
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

        filter_str = f" [Filter: {self.current_filter}]" if self.current_filter else ""
        self.root.label = f"{ICON_SERVER} {client_host}:{client_port}{filter_str}"

        # Start background worker for tree population to avoid blocking UI
        self._populate_tree_worker()

        # Trigger background cache building for search
        self._build_all_paths_cache_worker()

    @work(thread=True)
    def _populate_tree_worker(self) -> None:
        """
        Worker to populate the tree root with suites in a background thread.

        Returns
        -------
        None

        Notes
        -----
        This is a background worker that performs recursive filtering.
        """
        if not self.defs:
            return
        for suite in self.defs.suites:
            if self._should_show_node(suite):
                self._safe_call(self._add_node_to_ui, self.root, suite)

    def _should_show_node(self, node: Node) -> bool:
        """
        Determine if a node should be shown based on the current filter.

        Parameters
        ----------
        node : ecflow.Node
            The ecFlow node to check.

        Returns
        -------
        bool
            True if the node or any of its descendants match the filter.
        """
        if not self.current_filter:
            return True

        state = str(node.get_state())
        if state == self.current_filter:
            return True

        if hasattr(node, "nodes"):
            return any(self._should_show_node(child) for child in node.nodes)

        return False

    @work(thread=True)
    def _build_all_paths_cache_worker(self) -> None:
        """
        Worker to build the node path cache in a background thread.

        Returns
        -------
        None

        Notes
        -----
        This cache is used by find_and_select to provide fast search without
        blocking the UI thread on the first search.
        """
        if not self.defs:
            return

        paths: list[str] = []
        for suite in self.defs.suites:
            paths.append(suite.get_abs_node_path())
            for node in suite.get_all_nodes():
                paths.append(node.get_abs_node_path())

        self._all_paths_cache = paths

    def action_cycle_filter(self) -> None:
        """
        Cycle through available status filters and refresh the tree.

        Returns
        -------
        None
        """
        current_idx = self.filters.index(self.current_filter)
        next_idx = (current_idx + 1) % len(self.filters)
        self.current_filter = self.filters[next_idx]

        # We need to refresh the tree from local defs
        if self.defs:
            # Parse host/port from current root label if possible, or just use placeholders
            label_text = str(self.root.label)
            host_port = "Unknown"
            if ":" in label_text:
                parts = label_text.split(" ")
                for p in parts:
                    if ":" in p:
                        host_port = p
                        break

            if ":" in host_port:
                host, port = host_port.split(":", 1)
                # Remove filter suffix from port if present
                if "[" in port:
                    port = port.split("[")[0].strip()
                self.update_tree(host, int(port), self.defs)
            else:
                self.update_tree("Server", 0, self.defs)

        self.app.notify(f"Filter: {self.current_filter or 'All'}")

    def _add_node_to_ui(self, parent_ui_node: TreeNode[str], ecflow_node: Node) -> TreeNode[str]:
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
        icon = STATE_MAP.get(state, ICON_UNKNOWN_STATE)

        is_container = isinstance(ecflow_node, (ecflow.Family, ecflow.Suite))
        type_icon = ICON_FAMILY if is_container else ICON_TASK

        label = Text(f"{icon} {type_icon} {ecflow_node.name()} ")
        label.append(f"[{state}]", style="bold italic")

        new_ui_node = parent_ui_node.add(
            label,
            data=ecflow_node.get_abs_node_path(),
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
            # UI modification must be scheduled on the main thread
            placeholder = ui_node.children[0]
            self._safe_call(placeholder.remove)

            if sync:
                ecflow_node = self.defs.find_abs_node(ui_node.data)
                if ecflow_node and hasattr(ecflow_node, "nodes"):
                    for child in ecflow_node.nodes:
                        self._safe_call(self._add_node_to_ui, ui_node, child)
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
                if self._should_show_node(child):
                    self.app.call_from_thread(self._add_node_to_ui, ui_node, child)

    @work(exclusive=True, thread=True)
    def find_and_select(self, query: str) -> None:
        """
        Find nodes matching query in the ecFlow definitions and select them.

        This handles searching through unloaded parts of the tree in a
        background thread to keep the UI responsive.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        None

        Notes
        -----
        This is a background worker.
        """
        self._find_and_select_logic(query)

    def _find_and_select_logic(self, query: str) -> None:
        """
        The actual search logic split out for testing.

        Parameters
        ----------
        query : str
            The search query.
        """
        if not self.defs:
            return

        query = query.lower()

        # Build or use cached paths
        if not hasattr(self, "_all_paths_cache") or self._all_paths_cache is None:
            # Fallback if cache isn't ready yet (e.g. searching immediately after sync)
            paths: list[str] = []
            for suite in self.defs.suites:
                paths.append(suite.get_abs_node_path())
                for node in suite.get_all_nodes():
                    paths.append(node.get_abs_node_path())
            self._all_paths_cache = paths

        all_paths = self._all_paths_cache

        # Get current cursor state on main thread
        cursor_node = getattr(self, "cursor_node", None)
        current_path = cursor_node.data if cursor_node else None

        start_index = 0
        if current_path and current_path in all_paths:
            try:
                start_index = all_paths.index(current_path) + 1
            except ValueError:
                start_index = 0

        # Search from start_index to end, then wrap around
        found_path = None
        for i in range(len(all_paths)):
            path = all_paths[(start_index + i) % len(all_paths)]
            if query in path.lower():
                found_path = path
                break

        if found_path:
            self._select_by_path_logic(found_path)
        else:
            self._safe_call(self.app.notify, f"No match found for '{query}'", severity="warning")

    def _safe_call(self, callback: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Safely call a UI-related function from either the main thread or a worker.

        Parameters
        ----------
        callback : Any
            The function to call.
        *args : Any
            Positional arguments.
        **kwargs : Any
            Keyword arguments.

        Returns
        -------
        Any
            The result of the call if synchronous, or None if scheduled.
        """
        try:
            # Check if we are on the main thread.
            # Using private access as Textual doesn't provide a public way yet.
            if self.app._thread_id == threading.get_ident():
                return callback(*args, **kwargs)
        except (AttributeError, RuntimeError):
            # App might not be fully initialized in some tests
            pass

        return self.app.call_from_thread(callback, *args, **kwargs)

    @work(thread=True)
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

        Notes
        -----
        This is a background worker to avoid blocking the UI thread when
        loading many nested nodes synchronously.
        """
        self._select_by_path_logic(path)

    def _select_by_path_logic(self, path: str) -> None:
        """
        The actual logic for selecting a node by path.

        Parameters
        ----------
        path : str
            The absolute path of the node to select.

        Returns
        -------
        None

        Notes
        -----
        This method should be called from a background thread as it performs
        synchronous child loading.
        """
        if path == "/":
            self.app.call_from_thread(self.select_node, self.root)
            return

        parts = path.strip("/").split("/")
        current_ui_node = self.root

        current_path = ""
        for part in parts:
            current_path += "/" + part
            # Load children synchronously within the worker thread
            self._load_children(current_ui_node, sync=True)
            self._safe_call(current_ui_node.expand)

            found = False
            for child in current_ui_node.children:
                if child.data == current_path:
                    current_ui_node = child
                    found = True
                    break
            if not found:
                return

        self._safe_call(self._select_and_reveal, current_ui_node)

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
