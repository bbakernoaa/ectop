# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock ecflow before importing EcflowClient
if "ecflow" not in sys.modules:
    sys.modules["ecflow"] = MagicMock()

from ectop.client import EcflowClient  # noqa: E402


def test_client_init():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient("myhost", 1234)
        mock_client.assert_called_with("myhost", 1234)
        assert client.host == "myhost"
        assert client.port == 1234


def test_client_init_failure():
    with patch("ectop.client.ecflow.Client", side_effect=RuntimeError("Init failed")):
        with pytest.raises(RuntimeError, match="Failed to initialize ecFlow client"):
            EcflowClient("badhost", 1234)


def test_client_ping_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.ping()
        mock_client.return_value.ping.assert_called_once()


def test_client_ping_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.ping.side_effect = RuntimeError("Connection refused")
        with pytest.raises(RuntimeError, match="Failed to ping ecFlow server"):
            client.ping()


def test_client_sync_local_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.sync_local()
        mock_client.return_value.sync_local.assert_called_once()


def test_client_sync_local_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.sync_local.side_effect = RuntimeError("Sync error")
        with pytest.raises(RuntimeError, match="Failed to sync with ecFlow server"):
            client.sync_local()


def test_client_get_defs():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_defs = MagicMock()
        mock_client.return_value.get_defs.return_value = mock_defs
        assert client.get_defs() == mock_defs


def test_client_file_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.file.return_value = "file content"
        assert client.file("/path", "jobout") == "file content"
        mock_client.return_value.file.assert_called_with("/path", "jobout")


def test_client_file_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.file.side_effect = RuntimeError("File not found")
        with pytest.raises(RuntimeError, match="Failed to retrieve jobout for /path"):
            client.file("/path", "jobout")


def test_client_suspend_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.suspend("/path")
        mock_client.return_value.suspend.assert_called_with("/path")


def test_client_suspend_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.suspend.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to suspend /path"):
            client.suspend("/path")


def test_client_resume_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.resume("/path")
        mock_client.return_value.resume.assert_called_with("/path")


def test_client_resume_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.resume.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to resume /path"):
            client.resume("/path")


def test_client_kill_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.kill("/path")
        mock_client.return_value.kill.assert_called_with("/path")


def test_client_kill_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.kill.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to kill /path"):
            client.kill("/path")


def test_client_force_complete_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.force_complete("/path")
        mock_client.return_value.force_complete.assert_called_with("/path")


def test_client_force_complete_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.force_complete.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to force complete /path"):
            client.force_complete("/path")


def test_client_alter_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.alter("/path", "change", "var", "val")
        mock_client.return_value.alter.assert_called_with("/path", "change", "var", "val")


def test_client_alter_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.alter.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to alter /path"):
            client.alter("/path", "change", "var", "val")


def test_client_requeue_success():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        client.requeue("/path")
        mock_client.return_value.requeue.assert_called_with("/path")


def test_client_requeue_failure():
    with patch("ectop.client.ecflow.Client") as mock_client:
        client = EcflowClient()
        mock_client.return_value.requeue.side_effect = RuntimeError("Error")
        with pytest.raises(RuntimeError, match="Failed to requeue /path"):
            client.requeue("/path")
