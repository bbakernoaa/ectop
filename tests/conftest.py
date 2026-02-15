# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
import sys
from unittest.mock import MagicMock

# Create dummy types for ecflow classes so isinstance() works
class MockNode:
    def abs_node_path(self) -> str: return ""
    def get_state(self) -> str: return ""
    def name(self) -> str: return ""
    def get_all_nodes(self) -> list: return []

class MockFamily(MockNode):
    def __init__(self):
        self.nodes = []

class MockSuite(MockNode):
    def __init__(self):
        self.suites = []
        self.nodes = []

# Mock ecflow globally
mock_ecflow = MagicMock()
mock_ecflow.Node = MockNode
mock_ecflow.Family = MockFamily
mock_ecflow.Suite = MockSuite
sys.modules["ecflow"] = mock_ecflow


# Mock textual.work to be a no-op decorator for all tests
def mock_work(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return lambda f: f


import textual  # noqa: E402, I001

textual.work = mock_work
