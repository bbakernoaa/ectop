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


@pytest.mark.asyncio
async def test_app_actions():
    """Verify that app actions (suspend, resume, etc.) correctly call the client."""
    mock_client = MagicMock()
    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # Mock call_from_thread to avoid thread-check issues in run_test
        app.call_from_thread = lambda callback, *args, **kwargs: callback(*args, **kwargs)

        async with app.run_test() as pilot:
            # Mock get_selected_path
            with patch.object(Ectop, "get_selected_path", return_value="/suite/task"):
                # Test Suspend
                app.action_suspend()
                await pilot.pause()
                mock_client.suspend.assert_called_with("/suite/task")

                # Test Resume
                app.action_resume()
                await pilot.pause()
                mock_client.resume.assert_called_with("/suite/task")

                # Test Kill
                app.action_kill()
                await pilot.pause()
                mock_client.kill.assert_called_with("/suite/task")

                # Test Force Complete
                app.action_force()
                await pilot.pause()
                mock_client.force_complete.assert_called_with("/suite/task")
