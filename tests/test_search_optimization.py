# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for SuiteTree search optimization.
"""

from __future__ import annotations

import unittest.mock as mock
import pytest
import ecflow
from textual.app import App
from ectop.widgets.sidebar import SuiteTree

@pytest.mark.asyncio
async def test_search_cache_background_building():
    """
    Test that the search cache is built in the background after update_tree.
    """
    class TestApp(App):
        def compose(self):
            yield SuiteTree("Test")

    app = TestApp()
    async with app.run_test() as pilot:
        tree = app.query_one(SuiteTree)

        # Mock ecFlow Defs and Suites
        mock_defs = mock.MagicMock()

        # Create a mock that definitely has the methods and passes isinstance
        mock_suite = mock.MagicMock(spec=ecflow.Suite)
        # Manually add methods if spec failed to pick them up for some reason
        mock_suite.abs_node_path = mock.MagicMock(return_value="/suite")
        mock_suite.name = mock.MagicMock(return_value="suite")
        mock_suite.get_all_nodes = mock.MagicMock(return_value=[])
        mock_suite.get_state = mock.MagicMock(return_value="unknown")

        mock_defs.suites = [mock_suite]

        # Update tree
        tree.update_tree("localhost", 3141, mock_defs)

        # Wait for worker to complete
        await pilot.pause()

        assert hasattr(tree, "_all_paths_cache")
        assert tree._all_paths_cache == ["/suite"]

@pytest.mark.asyncio
async def test_find_and_select_fallback():
    """
    Test that find_and_select builds the cache if it's missing (fallback).
    """
    class TestApp(App):
        def compose(self):
            yield SuiteTree("Test")

    app = TestApp()
    async with app.run_test() as pilot:
        tree = app.query_one(SuiteTree)

        mock_defs = mock.MagicMock()
        mock_suite = mock.MagicMock(spec=ecflow.Suite)
        mock_suite.abs_node_path = mock.MagicMock(return_value="/suite")
        mock_suite.name = mock.MagicMock(return_value="suite")
        mock_suite.get_all_nodes = mock.MagicMock(return_value=[])
        mock_suite.get_state = mock.MagicMock(return_value="unknown")

        mock_defs.suites = [mock_suite]

        tree.defs = mock_defs
        tree._all_paths_cache = None

        # This should trigger the fallback logic
        found = tree.find_and_select("suite")

        assert found is True
        assert tree._all_paths_cache == ["/suite"]
