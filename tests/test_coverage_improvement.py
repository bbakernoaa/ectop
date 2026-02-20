# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Improved test coverage for ectop components.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from ectop.app import Ectop
from ectop.widgets.modals.variables import VariableTweaker
from ectop.widgets.sidebar import SuiteTree


@pytest.mark.asyncio
async def test_variable_tweaker_refresh_logic() -> None:
    """
    Test the refresh logic of VariableTweaker.

    Returns
    -------
    None
    """
    mock_client = MagicMock()
    tweaker = VariableTweaker("/node/path", mock_client)

    mock_app = MagicMock()
    # Execute call_from_thread immediately for testing
    mock_app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

    with patch.object(VariableTweaker, "app", new_callable=PropertyMock) as mock_app_prop:
        mock_app_prop.return_value = mock_app

        mock_node = MagicMock()
        mock_var = MagicMock()
        mock_var.name.return_value = "MYVAR"
        mock_var.value.return_value = "MYVAL"

        mock_node.variables = [mock_var]
        mock_node.get_generated_variables.return_value = []
        mock_node.get_parent.return_value = None

        mock_defs = MagicMock()
        mock_defs.find_abs_node.return_value = mock_node
        mock_client.get_defs.return_value = mock_defs

        with patch.object(tweaker, "query_one") as mock_query:
            mock_table = MagicMock()
            mock_query.return_value = mock_table

            tweaker._refresh_vars_logic()

            mock_table.clear.assert_called_once()
            mock_table.add_row.assert_any_call("MYVAR", "MYVAL", "User", key="MYVAR")


@pytest.mark.asyncio
async def test_variable_tweaker_add_logic() -> None:
    """
    Test the addition logic of VariableTweaker.

    Returns
    -------
    None
    """
    mock_client = MagicMock()
    tweaker = VariableTweaker("/node/path", mock_client)

    mock_app = MagicMock()
    mock_app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

    with patch.object(VariableTweaker, "app", new_callable=PropertyMock) as mock_app_prop:
        mock_app_prop.return_value = mock_app

        # Test successful addition
        with patch.object(tweaker, "query_one") as mock_query:
            mock_input = MagicMock()
            mock_query.return_value = mock_input

            tweaker._submit_variable_logic("NEW_VAR=NEW_VAL")
            mock_client.alter.assert_any_call("/node/path", "add_variable", "NEW_VAR", "NEW_VAL")

        # Test invalid format
        with patch.object(tweaker, "query_one") as mock_query:
            tweaker._submit_variable_logic("INVALID_FORMAT")
            mock_app.notify.assert_any_call("Use name=value format to add", severity="warning")


@pytest.mark.asyncio
async def test_variable_tweaker_delete_logic() -> None:
    """
    Test the deletion logic of VariableTweaker.

    Returns
    -------
    None
    """
    mock_client = MagicMock()
    tweaker = VariableTweaker("/node/path", mock_client)

    mock_app = MagicMock()
    mock_app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

    with patch.object(VariableTweaker, "app", new_callable=PropertyMock) as mock_app_prop:
        mock_app_prop.return_value = mock_app

        # Test successful deletion
        tweaker._delete_variable_logic("VAR_TO_DELETE")
        mock_client.alter.assert_called_with("/node/path", "delete_variable", "VAR_TO_DELETE")

        # Test inherited deletion (should fail)
        from ectop.constants import INHERITED_VAR_PREFIX

        tweaker._delete_variable_logic(f"{INHERITED_VAR_PREFIX}VAR")
        mock_app.notify.assert_any_call("Cannot delete inherited variables", severity="error")


@pytest.mark.asyncio
async def test_variable_tweaker_error_handling() -> None:
    """
    Test error handling in VariableTweaker logic.

    Returns
    -------
    None
    """
    mock_client = MagicMock()
    tweaker = VariableTweaker("/node/path", mock_client)

    mock_app = MagicMock()
    mock_app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

    with patch.object(VariableTweaker, "app", new_callable=PropertyMock) as mock_app_prop:
        mock_app_prop.return_value = mock_app

        # RuntimeError in sync
        mock_client.sync_local.side_effect = RuntimeError("Sync Error")
        tweaker._refresh_vars_logic()
        mock_app.notify.assert_any_call("Error fetching variables: Sync Error", severity="error")

        # RuntimeError in alter
        mock_client.alter.side_effect = RuntimeError("Alter Error")
        tweaker._submit_variable_logic("VAR=VAL")
        mock_app.notify.assert_any_call("Error: Alter Error", severity="error")


@pytest.mark.asyncio
async def test_suite_tree_filter_logic() -> None:
    """
    Test filtering logic in SuiteTree.

    Returns
    -------
    None
    """
    tree = SuiteTree("Root")
    mock_node = MagicMock()
    mock_node.get_state.return_value = "aborted"

    # current_filter is None -> should show
    tree.current_filter = None
    assert tree._should_show_node(mock_node) is True

    # current_filter matches -> should show
    tree.current_filter = "aborted"
    assert tree._should_show_node(mock_node) is True

    # current_filter doesn't match -> should NOT show
    tree.current_filter = "active"
    assert tree._should_show_node(mock_node) is False


@pytest.mark.asyncio
async def test_app_server_actions() -> None:
    """
    Test server restart and halt actions in Ectop app.

    Returns
    -------
    None
    """
    mock_client = MagicMock()
    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # Mock call_from_thread to avoid thread-check issues in run_test
        app.call_from_thread = lambda callback, *args, **kwargs: callback(*args, **kwargs)

        async with app.run_test() as pilot:
            # Test Restart
            with patch.object(Ectop, "action_refresh") as mock_refresh:
                app.action_restart_server()
                await pilot.pause()
                mock_client.restart_server.assert_called_once()
                mock_refresh.assert_called_once()

            # Test Halt
            with patch.object(Ectop, "action_refresh") as mock_refresh:
                app.action_halt_server()
                await pilot.pause()
                mock_client.halt_server.assert_called_once()
                mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_app_error_notifications() -> None:
    """
    Test that app notifies on connection errors.

    Returns
    -------
    None
    """
    with patch("ectop.app.EcflowClient", side_effect=RuntimeError("Connection Refused")):
        app = Ectop()
        app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

        async with app.run_test() as pilot:
            with patch.object(app, "notify") as mock_notify:
                app._initial_connect()
                await pilot.pause()
                # Initial connect failure notification
                mock_notify.assert_called_with("Connection Failed: Connection Refused", severity="error", timeout=10)
