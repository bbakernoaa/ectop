# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
CLI entry point for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

import argparse
import os

from ectop.app import Ectop
from ectop.constants import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_REFRESH_INTERVAL


def main() -> None:
    """
    Run the ectop application.

    Parses command-line arguments and environment variables for server configuration.
    """
    parser = argparse.ArgumentParser(description="ectop — High-performance TUI for ECMWF ecFlow")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("ECF_HOST", DEFAULT_HOST),
        help=f"ecFlow server hostname (default: {DEFAULT_HOST} or ECF_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ECF_PORT", DEFAULT_PORT)),
        help=f"ecFlow server port (default: {DEFAULT_PORT} or ECF_PORT)",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=float(os.environ.get("ECTOP_REFRESH", DEFAULT_REFRESH_INTERVAL)),
        help=f"Automatic refresh interval in seconds (default: {DEFAULT_REFRESH_INTERVAL} or ECTOP_REFRESH)",
    )

    args = parser.parse_args()

    app = Ectop(host=args.host, port=args.port, refresh_interval=args.refresh)
    app.run()


if __name__ == "__main__":
    main()
