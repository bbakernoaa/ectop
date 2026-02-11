# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Tests for Modal widgets (VariableTweaker, WhyInspector).

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from unittest.mock import MagicMock, patch

import pytest
from ectop.widgets.modals.variables import VariableTweaker
from ectop.widgets.modals.why import WhyInspector


@pytest.fixture
def mock_client() -> MagicMock:
    """
    Create a mock EcflowClient.

    Returns
    -------
    MagicMock
        A mock EcflowClient object.
    """
    return MagicMock()


def test_variable_tweaker_inherited_logic(mock_client: MagicMock) -> None:
    """
    Test that VariableTweaker correctly identifies inherited variables.

    Parameters
    ----------
    mock_client : MagicMock
        The mock EcflowClient.
    """
    tweaker = VariableTweaker("/s1/f1/t1", mock_client)
    tweaker.call_from_thread = lambda f, *args, **kwargs: f(*args, **kwargs)

    with patch.object(VariableTweaker, "app", new=MagicMock()):
        # Mock node structure
        task = MagicMock()
        task.name.return_value = "t1"
        task.variables = []
        task.generated_variables = []

        family = MagicMock()
        family.name.return_value = "f1"
        var_f = MagicMock()
        var_f.name.return_value = "F_VAR"
        var_f.value.return_value = "F_VAL"
        family.variables = [var_f]

        task.parent = family
        family.parent = None

        mock_client.get_defs.return_value.find_abs_node.return_value = task

        with patch.object(VariableTweaker, "query_one") as mock_query:
            table = MagicMock()
            mock_query.return_value = table

            tweaker.refresh_vars()

            # Should have one row for inherited variable
            table.add_row.assert_called_once_with("F_VAR", "F_VAL", "Inherited (f1)", key="inh_F_VAR")


def test_why_inspector_expression_parsing(mock_client: MagicMock) -> None:
    """
    Test that WhyInspector correctly parses complex trigger expressions.

    Parameters
    ----------
    mock_client : MagicMock
        The mock EcflowClient.
    """
    inspector = WhyInspector("/path", mock_client)

    parent_node = MagicMock()
    defs = MagicMock()

    # Mock nodes in defs
    node_a = MagicMock()
    node_a.get_state.return_value = "complete"
    node_b = MagicMock()
    node_b.get_state.return_value = "active"

    defs.find_abs_node.side_effect = lambda p: {"/suite/a": node_a, "/suite/b": node_b}.get(p)

    # Test AND expression
    inspector._parse_expression(parent_node, "(/suite/a == complete) and (/suite/b == complete)", defs)

    # Check that AND node was added
    parent_node.add.assert_any_call("AND (All must be true)", expand=True)

    # Test OR expression
    parent_node.reset_mock()
    inspector._parse_expression(parent_node, "(/suite/a == active) or (/suite/b == active)", defs)
    parent_node.add.assert_any_call("OR (Any must be true)", expand=True)
