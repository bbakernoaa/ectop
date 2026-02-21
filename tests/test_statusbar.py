# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for the StatusBar widget.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from ectop.constants import COLOR_STATUS_HALTED
from ectop.widgets.statusbar import StatusBar


def test_statusbar_initial_state() -> None:
    """Test initial state of StatusBar."""
    bar = StatusBar()
    assert bar.server_info == "Disconnected"
    assert bar.status == "Unknown"
    assert bar.server_version == "Unknown"
    assert bar.last_sync == "Never"


def test_statusbar_update() -> None:
    """Test updating StatusBar values."""
    bar = StatusBar()
    bar.update_status("test-host", 1234, "RUNNING", "5.11.4")
    assert bar.server_info == "test-host:1234"
    assert bar.status == "RUNNING"
    assert bar.server_version == "5.11.4"
    assert bar.last_sync != "Never"


def test_statusbar_render_colors() -> None:
    """Test rendering colors for different statuses."""
    bar = StatusBar()

    # RUNNING -> green
    bar.update_status("h", 1, "RUNNING")
    rendered = bar.render()
    # Find the status part in Text
    # Text.assemble usage makes it a bit tricky to find by index,
    # but we can check if the color is present in the spans.
    assert any(span.style == "green" for span in rendered.spans)

    # HALTED -> COLOR_STATUS_HALTED
    bar.update_status("h", 1, "HALTED")
    rendered = bar.render()
    assert any(span.style == COLOR_STATUS_HALTED for span in rendered.spans)

    # Error/Other -> red (default)
    bar.update_status("h", 1, "CRITICAL ERROR")
    rendered = bar.render()
    assert any(span.style == "red" for span in rendered.spans)


def test_statusbar_version_display() -> None:
    """Test that version is included in render."""
    bar = StatusBar()
    bar.update_status("h", 1, "RUNNING", "v5.8.4")
    rendered = bar.render()
    assert "v5.8.4" in rendered.plain
