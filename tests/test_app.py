import sys
from unittest.mock import MagicMock

# Mock ecflow before importing the app
sys.modules["ecflow"] = MagicMock()

from ectop import Ectop  # noqa: E402


def test_app_instantiation():
    """Basic test to check if the App can be instantiated."""
    app = Ectop()
    assert app is not None
