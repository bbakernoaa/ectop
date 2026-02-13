# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for script editing features in the Ectop application.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from ectop.app import Ectop


@pytest.fixture
def mock_app() -> Ectop:
    """
    Fixture for the Ectop application with a mocked ecflow client.

    Returns
    -------
    Ectop
        The application instance with a mock client.
    """
    app = Ectop()
    app.ecflow_client = MagicMock()
    app.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)
    return app


@pytest.mark.asyncio
async def test_action_edit_script_no_selection(mock_app: Ectop) -> None:
    """
    Test action_edit_script when no node is selected.

    Parameters
    ----------
    mock_app : Ectop
        The mocked application instance.
    """
    with patch.object(mock_app, "get_selected_path", return_value=None), patch.object(mock_app, "notify") as mock_notify:
        mock_app.action_edit_script()
        mock_notify.assert_called_with("No node selected", severity="warning")


@pytest.mark.asyncio
async def test_action_edit_script_success(mock_app: Ectop) -> None:
    """
    Test the full script editing flow.

    Parameters
    ----------
    mock_app : Ectop
        The mocked application instance.
    """
    node_path = "/suite/task"
    old_content = "old content"

    mock_app.ecflow_client.file.return_value = old_content

    with patch.object(mock_app, "get_selected_path", return_value=node_path), patch(
        "tempfile.NamedTemporaryFile"
    ) as mock_temp, patch.object(mock_app, "_run_editor") as mock_run_editor:
        # Setup mock temp file
        mock_file = MagicMock()
        mock_temp.return_value.__enter__.return_value = mock_file
        mock_file.name = "/tmp/fake.ecf"

        mock_app.action_edit_script()

        mock_app.ecflow_client.file.assert_called_with(node_path, "script")
        mock_file.write.assert_called_with(old_content)
        mock_run_editor.assert_called_with("/tmp/fake.ecf", node_path, old_content)


@pytest.mark.asyncio
async def test_finish_edit_updates_server(mock_app: Ectop) -> None:
    """
    Test that _finish_edit updates the server if content changed.

    Parameters
    ----------
    mock_app : Ectop
        The mocked application instance.
    """
    node_path = "/suite/task"
    old_content = "old content"
    new_content = "new content"
    temp_path = "/tmp/fake.ecf"

    with patch("builtins.open", mock_open(read_data=new_content)), patch("os.path.exists", return_value=True), patch(
        "os.unlink"
    ) as mock_unlink, patch.object(mock_app, "_prompt_requeue") as mock_prompt:
        mock_app._finish_edit(temp_path, node_path, old_content)

        mock_app.ecflow_client.alter.assert_called_with(node_path, "change", "script", new_content)
        mock_unlink.assert_called_with(temp_path)
        mock_prompt.assert_called_with(node_path)


@pytest.mark.asyncio
async def test_finish_edit_no_change(mock_app: Ectop) -> None:
    """
    Test that _finish_edit does nothing if content did not change.

    Parameters
    ----------
    mock_app : Ectop
        The mocked application instance.
    """
    node_path = "/suite/task"
    content = "same content"
    temp_path = "/tmp/fake.ecf"

    with patch("builtins.open", mock_open(read_data=content)), patch("os.path.exists", return_value=True), patch(
        "os.unlink"
    ), patch.object(mock_app, "notify") as mock_notify:
        mock_app._finish_edit(temp_path, node_path, content)

        mock_app.ecflow_client.alter.assert_not_called()
        mock_notify.assert_called_with("No changes detected")
