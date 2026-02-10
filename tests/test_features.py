from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from ectop.app import Ectop
from ectop.widgets.content import MainContent  # noqa: E402
from ectop.widgets.sidebar import SuiteTree  # noqa: E402


@pytest.fixture
def app():
    return Ectop()


def test_app_bindings(app):
    bindings = {b.key: b.action for b in app.BINDINGS}
    assert "/" in bindings
    assert "w" in bindings
    assert "e" in bindings
    assert "t" in bindings
    assert "v" in bindings


def test_search_logic():
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
    tree.root = MagicMock()
    tree.root.descendants = [node1, node2]

    # Mock methods used in find_and_select
    tree.select_node = MagicMock()
    tree.scroll_to_node = MagicMock()

    # We need to manually call the method since it's an instance method
    with patch.object(SuiteTree, "cursor_node", new_callable=PropertyMock) as mock_cursor:
        mock_cursor.return_value = None
        assert SuiteTree.find_and_select(tree, "post") is True
    tree.select_node.assert_called_with(node2)


def test_live_log_update():
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


def test_why_inspector_parsing():
    from ectop.widgets.modals.why import WhyInspector

    client = MagicMock()
    inspector = WhyInspector("/path/to/node", client)

    parent_ui_node = MagicMock()
    defs = MagicMock()

    # Test 'and' splitting
    inspector._parse_expression(parent_ui_node, "(/a == complete) and (/b == complete)", defs)
    parent_ui_node.add.assert_any_call("AND (All must be true)", expand=True)


def test_variable_tweaker_refresh():
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
