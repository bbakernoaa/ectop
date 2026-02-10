import ecflow
from rich.text import Text
from textual.widgets import Tree

from ecflowtui.client import STATE_MAP


class SuiteTree(Tree):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_tree(self, client_host, client_port, defs):
        self.clear()
        if not defs:
            self.root.label = "Server Empty"
            return

        self.root.label = f"🌍 {client_host}:{client_port}"
        for suite in defs.suites:
            self._populate_tree(self.root, suite)

    def _populate_tree(self, parent_ui_node, ecflow_node):
        """Recursively add ecflow nodes to the UI tree."""
        state = str(ecflow_node.get_state())
        icon = STATE_MAP.get(state, "⚪")

        is_family = isinstance(ecflow_node, ecflow.Family | ecflow.Suite)
        type_icon = "📂" if is_family else "⚙️"

        label = Text(f"{icon} {type_icon} {ecflow_node.name()} ")
        label.append(f"[{state}]", style="bold italic")

        new_ui_node = parent_ui_node.add(
            label,
            data=ecflow_node.get_abs_node_path(),
            expand=False,
        )

        if hasattr(ecflow_node, "nodes"):
            for child in ecflow_node.nodes:
                self._populate_tree(new_ui_node, child)

    def find_and_select(self, query, start_node=None):
        """Find nodes matching query and select the next one."""
        query = query.lower()

        all_nodes = []
        def collect_nodes(node):
            for child in node.children:
                all_nodes.append(child)
                collect_nodes(child)

        collect_nodes(self.root)

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

    def _select_and_reveal(self, node):
        """Select a node and expand all its parents."""
        self.select_node(node)
        parent = node.parent
        while parent:
            parent.expand()
            parent = parent.parent
        self.scroll_to_node(node)
