# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import asyncio
import sys
from unittest.mock import MagicMock

"""
Script to capture TUI screenshots for documentation.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

# Create a more complete mock for ecflow to allow running without the real library
mock_ecflow = MagicMock()
sys.modules["ecflow"] = mock_ecflow


class Node:
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent

    def name(self):
        return self._name

    def get_state(self):
        return "active"

    def is_suspended(self):
        return False

    def abs_node_path(self):
        if self._parent:
            return f"{self._parent.abs_node_path()}/{self._name}"
        return f"/{self._name}"


class Task(Node):
    pass


class Family(Node):
    def __init__(self, name, parent=None, children=None):
        super().__init__(name, parent)
        self.nodes = children or []
        for child in self.nodes:
            child._parent = self


class Suite(Family):
    def abs_node_path(self):
        return f"/{self._name}"


class Defs:
    def __init__(self, suites=None):
        self.suites = suites or []

    def find_abs_node(self, path):
        # Very simple mock implementation
        if path == "/tutorial":
            return self.suites[0]
        if path == "/tutorial/ingest":
            return self.suites[0].nodes[0]
        return None


mock_ecflow.Node = Node
mock_ecflow.Task = Task
mock_ecflow.Family = Family
mock_ecflow.Suite = Suite
mock_ecflow.Defs = Defs

from ectop.app import Ectop  # noqa: E402


async def capture_screenshot():
    app = Ectop()

    # Mock the ecflow client
    mock_client = MagicMock()
    app.ecflow_client = mock_client

    # Create a mock Defs
    s1 = Suite("tutorial")
    f1 = Family("ingest", parent=s1)
    t1 = Task("get_data", parent=f1)
    t2 = Task("process_data", parent=f1)
    f1.nodes = [t1, t2]
    s1.nodes = [f1]
    defs = Defs([s1])

    # Mock sync_local and get_defs
    mock_client.get_defs.return_value = defs
    mock_client.host = "localhost"
    mock_client.port = 3141

    async with app.run_test(size=(100, 30)):
        await asyncio.sleep(0.1)
        # Manually trigger tree update since initial_connect might have failed/not run
        tree = app.query_one("#suite_tree")
        tree.update_tree("localhost", 3141, defs)
        tree.root.expand()
        tree.root.children[0].expand()  # tutorial
        tree.root.children[0].children[0].expand()  # ingest
        await asyncio.sleep(0.1)

        # Take screenshot
        app.save_screenshot("docs/assets/main_view.svg")
        print("Screenshot saved to docs/assets/main_view.svg")


if __name__ == "__main__":
    asyncio.run(capture_screenshot())
