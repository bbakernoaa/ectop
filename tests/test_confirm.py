# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Tests for ConfirmModal widget.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock, patch

from ectop.widgets.modals.confirm import ConfirmModal


def test_confirm_modal_init() -> None:
    """
    Test that ConfirmModal initializes with correct message and callback.
    """
    callback = MagicMock()
    message = "Are you sure?"
    modal = ConfirmModal(message, callback)
    assert modal.message == message
    assert modal.callback == callback


def test_confirm_modal_confirm_action() -> None:
    """
    Test that the confirm action triggers the callback and pops the screen.
    """
    callback = MagicMock()
    modal = ConfirmModal("Test", callback)
    mock_app = MagicMock()

    with patch.object(ConfirmModal, "app", new=mock_app):
        modal.action_confirm()

    callback.assert_called_once()
    mock_app.pop_screen.assert_called_once()


def test_confirm_modal_close_action() -> None:
    """
    Test that the close action pops the screen without triggering the callback.
    """
    callback = MagicMock()
    modal = ConfirmModal("Test", callback)
    mock_app = MagicMock()

    with patch.object(ConfirmModal, "app", new=mock_app):
        modal.action_close()

    callback.assert_not_called()
    mock_app.pop_screen.assert_called_once()


def test_confirm_modal_button_press_yes() -> None:
    """
    Test that pressing the 'yes' button triggers the confirm action.
    """
    callback = MagicMock()
    modal = ConfirmModal("Test", callback)

    event = MagicMock()
    event.button.id = "yes_btn"

    with patch.object(ConfirmModal, "action_confirm") as mock_confirm:
        modal.on_button_pressed(event)
        mock_confirm.assert_called_once()


def test_confirm_modal_button_press_no() -> None:
    """
    Test that pressing any other button triggers the close action.
    """
    callback = MagicMock()
    modal = ConfirmModal("Test", callback)

    event = MagicMock()
    event.button.id = "no_btn"

    with patch.object(ConfirmModal, "action_close") as mock_close:
        modal.on_button_pressed(event)
        mock_close.assert_called_once()
