# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for Ectop action methods.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ectop.app import Ectop


@pytest.fixture
def app() -> Ectop:
    """Create an Ectop app instance with mocked components."""
    app = Ectop(host="localhost", port=3141)
    app.ecflow_client = MagicMock()
    return app


def test_action_restart_server(app: Ectop) -> None:
    """Test action_restart_server calls client and refresh."""
    with patch.object(app, "action_refresh") as mock_refresh, patch.object(app, "call_from_thread") as mock_call:
        app.action_restart_server()
        app.ecflow_client.restart_server.assert_called_once()
        mock_refresh.assert_called_once()
        mock_call.assert_called()


def test_action_halt_server(app: Ectop) -> None:
    """Test action_halt_server calls client and refresh."""
    with patch.object(app, "action_refresh") as mock_refresh, patch.object(app, "call_from_thread") as mock_call:
        app.action_halt_server()
        app.ecflow_client.halt_server.assert_called_once()
        mock_refresh.assert_called_once()
        mock_call.assert_called()


@pytest.mark.asyncio
async def test_action_refresh_logic(app: Ectop) -> None:
    """Test the logic inside action_refresh."""
    # We need to mock query_one for tree and status_bar
    mock_tree = MagicMock()
    mock_sb = MagicMock()

    def side_effect(selector, type=None):
        if "#suite_tree" in selector:
            return mock_tree
        if "#status_bar" in selector:
            return mock_sb
        return MagicMock()

    with patch.object(app, "query_one", side_effect=side_effect), patch.object(app, "call_from_thread") as mock_call:
        app.ecflow_client.get_defs.return_value.get_server_state.return_value = "RUNNING"
        app.ecflow_client.server_version.return_value = "5.11.4"

        app.action_refresh()

        app.ecflow_client.sync_local.assert_called_once()
        # Verify version was fetched
        app.ecflow_client.server_version.assert_called_once()
        # Verify status_bar update was called via call_from_thread
        # We check the arguments passed to call_from_thread
        calls = [c.args for c in mock_call.call_args_list]
        # One of the calls should be status_bar.update_status
        assert any(mock_sb.update_status in call for call in calls)
