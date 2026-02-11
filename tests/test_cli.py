# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import os
from unittest.mock import MagicMock, patch

from ectop.cli import main


def test_cli_args():
    """Test that CLI arguments are correctly passed to the App."""
    with patch("argparse.ArgumentParser.parse_args") as mock_args:
        mock_args.return_value = MagicMock(host="otherhost", port=9999, refresh=5.0)
        with patch("ectop.cli.Ectop") as mock_app:
            main()
            mock_app.assert_called_once_with(host="otherhost", port=9999, refresh_interval=5.0)
            mock_app.return_value.run.assert_called_once()


def test_cli_env_vars():
    """Test that environment variables are used as defaults in CLI."""
    with patch.dict(os.environ, {"ECF_HOST": "envhost", "ECF_PORT": "8888", "ECTOP_REFRESH": "3.0"}):
        # We need to let argparse run normally to see if it picks up defaults from os.environ
        # but we don't want it to actually parse sys.argv
        with patch("sys.argv", ["ectop"]):
            with patch("ectop.cli.Ectop") as mock_app:
                main()
                mock_app.assert_called_once_with(host="envhost", port=8888, refresh_interval=3.0)
