# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock ecflow before importing the app
sys.modules["ecflow"] = MagicMock()

from ectop import Ectop  # noqa: E402


def test_app_instantiation():
    """Basic test to check if the App can be instantiated."""
    app = Ectop()
    assert app is not None


@pytest.mark.asyncio
async def test_app_handles_runtime_error():
    """Verify that the app handles a RuntimeError from the client gracefully."""
    # We need to mock the client
    mock_client = MagicMock()
    mock_client.ping.side_effect = RuntimeError("Mock server error")

    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # Mock call_from_thread to avoid thread-check issues in run_test
        app.call_from_thread = lambda callback, *args, **kwargs: callback(*args, **kwargs)

        async with app.run_test() as pilot:
            # In on_mount, _initial_connect is called.
            # We wait for any workers to finish
            await pilot.pause()
            # Check notifications in the app
            assert len(app._notifications) > 0
            notification = list(app._notifications)[0]
            assert "Connection Failed" in str(notification.message)
