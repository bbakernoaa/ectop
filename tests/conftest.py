# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import sys
from unittest.mock import MagicMock

# Mock ecflow globally
sys.modules["ecflow"] = MagicMock()


# Mock textual.work to be a no-op decorator for all tests
def mock_work(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return lambda f: f


import textual  # noqa: E402, I001

textual.work = mock_work
