# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Additional tests to boost coverage and verify new functionality.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from ectop import Ectop
from ectop.widgets.modals.why import WhyInspector


@pytest.mark.asyncio
async def test_app_action_requeue():
    """Verify that action_requeue correctly calls the client."""
    mock_client = MagicMock()
    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # Mock call_from_thread to avoid thread-check issues in run_test
        app.call_from_thread = lambda callback, *args, **kwargs: callback(*args, **kwargs)

        async with app.run_test() as pilot:
            with patch.object(Ectop, "get_selected_path", return_value="/suite/task"):
                app.action_requeue()
                await pilot.pause()
                mock_client.requeue.assert_called_with("/suite/task")


@pytest.mark.asyncio
async def test_app_action_copy_path():
    """Verify that action_copy_path notifies the user."""
    mock_client = MagicMock()
    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # Mock call_from_thread to avoid thread-check issues in run_test
        app.call_from_thread = lambda callback, *args, **kwargs: callback(*args, **kwargs)

        async with app.run_test() as pilot:
            with patch.object(Ectop, "get_selected_path", return_value="/suite/task"):
                app.action_copy_path()
                await pilot.pause()
                assert len(app._notifications) > 0
                notification = list(app._notifications)[-1]
                assert "/suite/task" in str(notification.message)


def test_why_inspector_error_handling():
    """Test error handling logic in WhyInspector._refresh_deps_logic."""
    mock_client = MagicMock()
    inspector = WhyInspector("/node", mock_client)

    with patch.object(WhyInspector, "app", new_callable=PropertyMock) as mock_app:
        app_mock = MagicMock()
        mock_app.return_value = app_mock
        # Mock call_from_thread to execute the callback immediately
        app_mock.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

        tree = MagicMock()
        tree.root = MagicMock()

        # Test RuntimeError
        mock_client.sync_local.side_effect = RuntimeError("Sync failed")
        inspector._refresh_deps_logic(tree)
        assert "Error: Sync failed" in str(tree.root.label)

        # Test generic Exception
        mock_client.sync_local.side_effect = Exception("Unexpected")
        inspector._refresh_deps_logic(tree)
        assert "Unexpected Error: Unexpected" in str(tree.root.label)
