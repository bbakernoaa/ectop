from unittest.mock import MagicMock
from datetime import datetime
from ectop.widgets.statusbar import StatusBar
from ectop.app import Ectop, EctopCommands
from textual.command import Hit
import pytest

def test_status_bar_update():
    """Test that the status bar updates its internal state correctly."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    assert sb.server_info == "myhost:1234"
    assert sb.status == "Connected"
    assert sb.last_sync != "Never"

def test_status_bar_render():
    """Test that the status bar renders correctly."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    rendered = sb.render()
    assert "myhost:1234" in str(rendered)
    assert "Connected" in str(rendered)

@pytest.mark.asyncio
async def test_ectop_commands_provider():
    """Test the EctopCommands provider yields hits."""
    app = Ectop()
    # Mock some basic app properties/methods needed by the provider
    app.action_refresh = MagicMock()

    provider = EctopCommands(app)

    # We need to mock the matcher
    matcher = MagicMock()
    matcher.match.return_value = 1.0
    matcher.highlight.return_value = "Refresh Tree"
    provider.matcher = MagicMock(return_value=matcher)

    hits = []
    async for hit in provider.search("refresh"):
        hits.append(hit)

    assert len(hits) > 0
    assert any(h.match_display == "Refresh Tree" for h in hits)
