# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Tests for newly added features in ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock

import pytest

from ectop.app import Ectop, EctopCommands
from ectop.widgets.content import MainContent
from ectop.widgets.sidebar import SuiteTree
from ectop.widgets.statusbar import StatusBar


def test_status_bar_update() -> None:
    """Test that the status bar updates its internal state correctly."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    assert sb.server_info == "myhost:1234"
    assert sb.status == "Connected"
    assert sb.last_sync != "Never"


def test_status_bar_render() -> None:
    """Test that the status bar renders correctly."""
    sb = StatusBar()
    sb.update_status("myhost", 1234, "Connected")
    rendered = sb.render()
    assert "myhost:1234" in str(rendered)
    assert "Connected" in str(rendered)


@pytest.mark.asyncio
async def test_ectop_commands_provider() -> None:
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


def test_suite_tree_filtering() -> None:
    """Test SuiteTree filtering logic."""
    tree = SuiteTree("Test")
    mock_defs = MagicMock()

    # Mock node structure
    suite = MagicMock()
    suite.get_state.return_value = "complete"

    task1 = MagicMock()
    task1.get_state.return_value = "aborted"
    task1.nodes = []

    suite.nodes = [task1]
    mock_defs.suites = [suite]

    tree.defs = mock_defs

    # Test _should_show_node
    tree.current_filter = "aborted"
    assert tree._should_show_node(task1) is True
    assert tree._should_show_node(suite) is True  # Should show because child matches

    tree.current_filter = "active"
    assert tree._should_show_node(task1) is False
    assert tree._should_show_node(suite) is False


def test_main_content_search_toggle() -> None:
    """Test MainContent search toggle."""
    mc = MainContent()
    # We need to compose to have access to widgets
    from textual.app import App

    class DummyApp(App):
        def compose(self):
            yield mc

    # Manual trigger of action_search (it usually works through binding)
    # But mc is not fully mounted yet in a unit test without async app.run_test()
    # Let's mock query_one
    mc.query_one = MagicMock()
    search_input = MagicMock()
    search_input.classes = ["hidden"]
    mc.query_one.return_value = search_input

    mc.action_search()
    search_input.remove_class.assert_called_with("hidden")
    search_input.focus.assert_called()
