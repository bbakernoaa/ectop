# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Tests for various features of ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from ectop.app import Ectop
from ectop.widgets.content import MainContent
from ectop.widgets.sidebar import SuiteTree


@pytest.fixture
def app() -> Ectop:
    """
    Fixture for the Ectop application.

    Returns
    -------
    Ectop
        The application instance.
    """
    return Ectop()


def test_app_bindings(app: Ectop) -> None:
    """
    Test that the application has the expected key bindings.

    Parameters
    ----------
    app : Ectop
        The application instance.
    """
    bindings = {b.key: b.action for b in app.BINDINGS}
    assert "/" in bindings
    assert "w" in bindings
    assert "e" in bindings
    assert "t" in bindings
    assert "v" in bindings


def test_search_logic() -> None:
    """Test the search logic in SuiteTree."""
    # Create mock nodes
    node1 = MagicMock()
    node1.label = "task1"
    node1.data = "/suite/task1"
    node1.parent = None

    node2 = MagicMock()
    node2.label = "post_proc"
    node2.data = "/suite/post_proc"
    node2.parent = None

    # Test substring match
    # We use __new__ to avoid calling __init__ which triggers Textual internals
    tree = SuiteTree.__new__(SuiteTree)
    tree.defs = MagicMock()
    tree.root = MagicMock()
    tree.root.descendants = [node1, node2]

    # Mock methods used in find_and_select
    tree.select_node = MagicMock()
    tree.scroll_to_node = MagicMock()

    # We need to manually call the method since it's an instance method
    with patch.object(SuiteTree, "cursor_node", new_callable=PropertyMock) as mock_cursor, patch.object(
        SuiteTree, "app", new=MagicMock()
    ):
        mock_cursor.return_value = None
        # Mocking the definition walk
        suite = MagicMock()
        suite.abs_node_path.return_value = "/suite"
        node1_ecf = MagicMock()
        node1_ecf.abs_node_path.return_value = "/suite/task1"
        node2_ecf = MagicMock()
        node2_ecf.abs_node_path.return_value = "/suite/post_proc"
        suite.get_all_nodes.return_value = [node1_ecf, node2_ecf]
        tree.defs.suites = [suite]

        # In the refactored find_and_select, it calls _select_by_path_logic
        tree._select_by_path_logic = MagicMock()

        SuiteTree.find_and_select(tree, "post")
        tree._select_by_path_logic.assert_called_with("/suite/post_proc")


def test_live_log_update() -> None:
    """Test the live log update mechanism in MainContent."""
    content_area = MainContent()
    # Mock the RichLog widget
    rich_log = MagicMock()
    content_area.query_one = MagicMock(return_value=rich_log)

    content_area.update_log("initial content")
    assert content_area.last_log_size == len("initial content")
    rich_log.write.assert_called_with("initial content")

    content_area.update_log("initial content added more", append=True)
    rich_log.write.assert_called_with(" added more")
    assert content_area.last_log_size == len("initial content added more")


def test_why_inspector_parsing() -> None:
    """Test trigger expression parsing in WhyInspector."""
    from ectop.widgets.modals.why import WhyInspector

    client = MagicMock()
    inspector = WhyInspector("/path/to/node", client)

    parent_ui_node = MagicMock()
    defs = MagicMock()

    # Test 'and' splitting
    inspector._parse_expression(parent_ui_node, "(/a == complete) and (/b == complete)", defs)
    parent_ui_node.add.assert_any_call("AND (All must be true)", expand=True)


def test_variable_tweaker_refresh() -> None:
    """Test variable refresh logic in VariableTweaker."""
    from ectop.widgets.modals.variables import VariableTweaker

    client = MagicMock()
    tweaker = VariableTweaker("/path/to/node", client)

    table = MagicMock()
    tweaker.query_one = MagicMock(return_value=table)
    # Mock app and call_from_thread
    with patch.object(VariableTweaker, "app", new_callable=PropertyMock) as mock_app:
        mock_app.return_value = MagicMock()
        tweaker.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

        node = MagicMock()
        var1 = MagicMock()
        var1.name.return_value = "VAR1"
        var1.value.return_value = "VAL1"
        node.variables = [var1]
        node.generated_variables = []
        node.parent = None

        client.get_defs.return_value.find_abs_node.return_value = node

        tweaker.refresh_vars()
        table.add_row.assert_any_call("VAR1", "VAL1", "User", key="VAR1")
