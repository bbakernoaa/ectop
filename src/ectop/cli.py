"""
CLI entry point for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from ectop.app import Ectop


def main() -> None:
    """Run the ectop application."""
    Ectop().run()


if __name__ == "__main__":
    main()
