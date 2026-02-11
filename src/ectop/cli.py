# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
CLI entry point for ectop.
"""

import argparse
import os

from ectop.app import Ectop


def main() -> None:
    """
    Run the ectop application.

    Parses command-line arguments and environment variables for server configuration.
    """
    parser = argparse.ArgumentParser(description="ectop — High-performance TUI for ECMWF ecFlow")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("ECF_HOST", "localhost"),
        help="ecFlow server hostname (default: localhost or ECF_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ECF_PORT", 3141)),
        help="ecFlow server port (default: 3141 or ECF_PORT)",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=float(os.environ.get("ECTOP_REFRESH", 2.0)),
        help="Automatic refresh interval in seconds (default: 2.0 or ECTOP_REFRESH)",
    )

    args = parser.parse_args()

    app = Ectop(host=args.host, port=args.port, refresh_interval=args.refresh)
    app.run()


if __name__ == "__main__":
    main()
