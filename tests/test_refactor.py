# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for refactored logic and new features.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from textual.widgets.tree import TreeNode

from ectop.app import Ectop
from ectop.constants import EXPR_AND_LABEL, EXPR_OR_LABEL
from ectop.widgets.modals.why import WhyInspector
from ectop.widgets.sidebar import SuiteTree


@pytest.fixture
def app() -> Ectop:
    """Create a mock Ectop app."""
    return Ectop()


def test_action_requeue(app: Ectop) -> None:
    """Test action_requeue calls the client."""
    with (
        patch.object(app, "_run_client_command") as mock_run,
        patch.object(app, "get_selected_path", return_value="/s1/t1"),
    ):
        app.action_requeue()
        mock_run.assert_called_once_with("requeue", "/s1/t1")


def test_action_copy_path(app: Ectop) -> None:
    """Test action_copy_path copies to clipboard and notifies the user."""
    # Test with clipboard support
    with patch.object(app, "copy_to_clipboard") as mock_copy, patch.object(app, "notify") as mock_notify, patch.object(
        app, "get_selected_path", return_value="/s1/t1"
    ):
        app.action_copy_path()
        mock_copy.assert_called_once_with("/s1/t1")
        mock_notify.assert_called_once_with("Copied to clipboard: /s1/t1")

    # Test without clipboard support
    mock_app = MagicMock(spec=Ectop)
    # Remove it if it exists on the spec
    if hasattr(mock_app, "copy_to_clipboard"):
        del mock_app.copy_to_clipboard

    mock_app.get_selected_path.return_value = "/s1/t1"
    Ectop.action_copy_path(mock_app)
    mock_app.notify.assert_called_once_with("Node path: /s1/t1")


def test_why_inspector_nested_parsing() -> None:
    """Test WhyInspector handles nested parentheses and operators."""
    mock_client = MagicMock()
    inspector = WhyInspector("/path", mock_client)

    parent_node = MagicMock(spec=TreeNode)
    defs = MagicMock()

    # Mock nodes
    node_a = MagicMock()
    node_a.get_state.return_value = "complete"
    node_b = MagicMock()
    node_b.get_state.return_value = "aborted"

    defs.find_abs_node.side_effect = lambda p: {"/a": node_a, "/b": node_b}.get(p)

    # Complex expression: (a == complete or b == complete) and (a != aborted)
    expr = "((/a == complete) or (/b == complete)) and (/a != aborted)"

    # We need to mock the return value of add to track hierarchy
    and_node = MagicMock(spec=TreeNode)
    or_node = MagicMock(spec=TreeNode)

    def side_effect(label, **kwargs):
        if label == EXPR_AND_LABEL:
            return and_node
        if label == EXPR_OR_LABEL:
            return or_node
        return MagicMock(spec=TreeNode)

    parent_node.add.side_effect = side_effect
    and_node.add.side_effect = side_effect

    inspector._parse_expression(parent_node, expr, defs)

    # Check that AND was added at top level
    parent_node.add.assert_any_call(EXPR_AND_LABEL, expand=True)
    # Check that OR was added under AND
    and_node.add.assert_any_call(EXPR_OR_LABEL, expand=True)


@pytest.mark.asyncio
async def test_suite_tree_select_by_path_worker() -> None:
    """Test SuiteTree.select_by_path uses worker logic."""
    tree = SuiteTree("Test")
    tree.defs = MagicMock()

    # Mock node structure
    suite = MagicMock()
    suite.abs_node_path.return_value = "/s1"
    suite.data = "/s1"
    suite.nodes = []
    tree.defs.suites = [suite]
    tree.defs.find_abs_node.return_value = suite

    with (
        patch.object(type(tree.root), "children", new_callable=PropertyMock) as mock_children,
        patch.object(SuiteTree, "app", new=MagicMock()) as mock_app,
        patch.object(tree, "_load_children"),
        patch.object(tree, "_select_and_reveal"),
    ):
        mock_children.return_value = [suite]

        # We call the logic method directly for synchronous testing
        tree._select_by_path_logic("/s1")

        mock_app.call_from_thread.assert_any_call(tree._select_and_reveal, suite)
