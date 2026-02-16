# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Tests for the Sidebar (SuiteTree) widget.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock, patch

import pytest
from rich.text import Text

from ectop.widgets.sidebar import SuiteTree


@pytest.fixture
def mock_defs() -> MagicMock:
    """
    Create a mock ecFlow definition with some suites.

    Returns
    -------
    MagicMock
        A mock Defs object.
    """
    defs = MagicMock()
    suite1 = MagicMock()
    suite1.name.return_value = "s1"
    suite1.abs_node_path.return_value = "/s1"
    suite1.get_state.return_value = "complete"
    suite1.nodes = []

    suite2 = MagicMock()
    suite2.name.return_value = "s2"
    suite2.abs_node_path.return_value = "/s2"
    suite2.get_state.return_value = "active"

    task2a = MagicMock()
    task2a.name.return_value = "t2a"
    task2a.abs_node_path.return_value = "/s2/t2a"
    task2a.get_state.return_value = "queued"
    task2a.nodes = []

    suite2.nodes = [task2a]
    suite2.get_all_nodes.return_value = [task2a]

    defs.suites = [suite1, suite2]
    defs.find_abs_node.side_effect = lambda p: {"/s1": suite1, "/s2": suite2, "/s2/t2a": task2a}.get(p)

    return defs


def test_update_tree(mock_defs: MagicMock) -> None:
    """
    Test that update_tree clears and repopulates the tree.

    Parameters
    ----------
    mock_defs : MagicMock
        The mock ecFlow definitions.
    """
    tree = SuiteTree("Test")
    tree.clear = MagicMock()
    tree.root = MagicMock()

    # Mock _add_node_to_ui to avoid Textual internals
    with patch.object(SuiteTree, "_add_node_to_ui") as mock_add:
        tree.update_tree("localhost", 3141, mock_defs)

        tree.clear.assert_called_once()
        assert tree.defs == mock_defs
        assert mock_add.call_count == 2  # 2 suites


def test_load_children(mock_defs: MagicMock) -> None:
    """
    Test that _load_children calls the worker.

    Parameters
    ----------
    mock_defs : MagicMock
        The mock ecFlow definitions.
    """
    tree = SuiteTree("Test")
    tree.defs = mock_defs

    ui_node = MagicMock()
    ui_node.data = "/s2"
    placeholder = MagicMock()
    placeholder.label = Text("loading...")
    ui_node.children = [placeholder]

    with patch.object(SuiteTree, "app", new=MagicMock()) as mock_app, patch.object(
        SuiteTree, "_load_children_worker"
    ) as mock_worker:
        # Ensure it looks like it's on the main thread for simpler testing
        import threading

        mock_app._thread_id = threading.get_ident()

        tree._load_children(ui_node)

        placeholder.remove.assert_called_once()
        mock_worker.assert_called_with(ui_node, "/s2")


def test_load_children_worker(mock_defs: MagicMock) -> None:
    """
    Test that the worker correctly schedules node additions.

    Parameters
    ----------
    mock_defs : MagicMock
        The mock ecFlow definitions.
    """
    tree = SuiteTree("Test")
    tree.defs = mock_defs

    ui_node = MagicMock()
    ui_node.data = "/s2"

    mock_app = MagicMock()
    with patch.object(SuiteTree, "app", new=mock_app), patch.object(SuiteTree, "_add_node_to_ui"):
        tree._load_children_worker(ui_node, "/s2")

        # Should have called call_from_thread with _add_node_to_ui and task2a
        mock_app.call_from_thread.assert_called_once()
        args, _ = mock_app.call_from_thread.call_args
        assert args[0] == tree._add_node_to_ui
        assert args[1] == ui_node
        assert args[2].name() == "t2a"


def test_select_by_path(mock_defs: MagicMock) -> None:
    """
    Test that select_by_path expands and selects the correct node.

    Parameters
    ----------
    mock_defs : MagicMock
        The mock ecFlow definitions.
    """
    tree = SuiteTree("Test")
    tree.defs = mock_defs
    tree.root = MagicMock()
    tree.root.data = "/"

    # Mock children of root
    child_s2 = MagicMock()
    child_s2.data = "/s2"
    tree.root.children = [child_s2]

    # Mock children of s2
    child_t2a = MagicMock()
    child_t2a.data = "/s2/t2a"
    child_s2.children = [child_t2a]

    with patch.object(SuiteTree, "app", new=MagicMock()) as mock_app, patch.object(
        SuiteTree, "_load_children"
    ) as mock_load, patch.object(SuiteTree, "_select_and_reveal") as mock_select:
        # Use logic method for synchronous test
        tree._select_by_path_logic("/s2/t2a")

        # Should have called _load_children for root and s2
        assert mock_load.call_count >= 2
        mock_app.call_from_thread.assert_any_call(child_s2.expand)
        mock_app.call_from_thread.assert_called_with(mock_select, child_t2a)


def test_find_and_select_caching(mock_defs: MagicMock) -> None:
    """
    Test that find_and_select uses the path cache.

    Parameters
    ----------
    mock_defs : MagicMock
        The mock ecFlow definitions.
    """
    tree = SuiteTree("Test")
    tree.defs = mock_defs
    with patch.object(SuiteTree, "app", new=MagicMock()):
        tree.root = MagicMock()

        with patch.object(SuiteTree, "cursor_node", new=None), patch.object(
            SuiteTree, "select_by_path"
        ) as mock_select, patch.object(SuiteTree, "_add_node_to_ui"):
            # First call should build cache
            tree.find_and_select("t2a")
            assert hasattr(tree, "_all_paths_cache")
            assert tree._all_paths_cache is not None
            assert "/s2/t2a" in tree._all_paths_cache
            mock_select.assert_called_with("/s2/t2a")

            # Modify defs - but cache should persist until update_tree is called
            tree.defs.suites = []
            mock_select.reset_mock()
            tree.find_and_select("t2a")
            mock_select.assert_called_with("/s2/t2a")  # Still works from cache

            # update_tree should clear cache
            tree.update_tree("localhost", 3141, None)
            assert tree._all_paths_cache is None
