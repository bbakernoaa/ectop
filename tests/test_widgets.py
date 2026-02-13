# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
from unittest.mock import MagicMock, patch

from textual.widgets import RichLog, Static

from ectop.widgets.content import MainContent
from ectop.widgets.modals.confirm import ConfirmModal
from ectop.widgets.search import SearchBox
from ectop.widgets.statusbar import StatusBar


def test_statusbar_update() -> None:
    """Test that the status bar updates its internal state."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    assert sb.server_info == "myhost:1234"
    assert sb.status == "Connected"
    assert sb.last_sync != "Never"


def test_searchbox_cancel() -> None:
    """Test that SearchBox cancel clears and hides the box."""
    with patch("textual.widgets.Input.app") as mock_app:
        sb = SearchBox()
        sb.value = "some search"
        sb.add_class("visible")

        sb.action_cancel()

        assert sb.value == ""
        assert "visible" not in sb.classes
        mock_app.set_focus.assert_called_once()


def test_confirm_modal() -> None:
    """Test that ConfirmModal calls the callback on confirm."""
    callback = MagicMock()
    with patch("textual.screen.Screen.app") as mock_app:
        modal = ConfirmModal("Are you sure?", callback)

        modal.action_confirm()

        callback.assert_called_once()
        mock_app.pop_screen.assert_called_once()


def test_confirm_modal_close() -> None:
    """Test that ConfirmModal does not call callback on close."""
    callback = MagicMock()
    with patch("textual.screen.Screen.app") as mock_app:
        modal = ConfirmModal("Are you sure?", callback)

        modal.action_close()

        callback.assert_not_called()
        mock_app.pop_screen.assert_called_once()


def test_main_content_updates() -> None:
    """
    Test that MainContent updates its tabs correctly.

    Returns
    -------
    None
    """
    mc = MainContent()
    mock_log = MagicMock(spec=RichLog)
    mock_script = MagicMock(spec=Static)
    mock_job = MagicMock(spec=Static)

    def mock_query_one(selector, *args):
        if selector == "#log_output":
            return mock_log
        if selector == "#view_script":
            return mock_script
        if selector == "#view_job":
            return mock_job
        return MagicMock()

    mc.query_one = MagicMock(side_effect=mock_query_one)

    # Test script update
    mc.update_script("echo hello")
    mock_script.update.assert_called_once()

    # Test job update
    mc.update_job("echo job")
    mock_job.update.assert_called_once()

    # Test show error on Static
    mc.show_error("#view_script", "Error message")
    mock_script.update.assert_called_with("[italic red]Error message[/]")

    # Test show error on RichLog
    mc.show_error("#log_output", "Log error")
    mock_log.write.assert_called_with("[italic red]Log error[/]")
