from unittest.mock import MagicMock, patch

from ectop.widgets.modals.confirm import ConfirmModal
from ectop.widgets.search import SearchBox
from ectop.widgets.statusbar import StatusBar


def test_statusbar_update():
    """Test that the status bar updates its internal state."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    assert sb.server_info == "myhost:1234"
    assert sb.status == "Connected"
    assert sb.last_sync != "Never"

def test_searchbox_cancel():
    """Test that SearchBox cancel clears and hides the box."""
    with patch("textual.widgets.Input.app") as mock_app:
        sb = SearchBox()
        sb.value = "some search"
        sb.add_class("visible")

        sb.action_cancel()

        assert sb.value == ""
        assert "visible" not in sb.classes
        mock_app.set_focus.assert_called_once()

def test_confirm_modal():
    """Test that ConfirmModal calls the callback on confirm."""
    callback = MagicMock()
    with patch("textual.screen.Screen.app") as mock_app:
        modal = ConfirmModal("Are you sure?", callback)

        modal.action_confirm()

        callback.assert_called_once()
        mock_app.pop_screen.assert_called_once()

def test_confirm_modal_close():
    """Test that ConfirmModal does not call callback on close."""
    callback = MagicMock()
    with patch("textual.screen.Screen.app") as mock_app:
        modal = ConfirmModal("Are you sure?", callback)

        modal.action_close()

        callback.assert_not_called()
        mock_app.pop_screen.assert_called_once()
