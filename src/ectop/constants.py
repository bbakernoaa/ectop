# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
"""
Constants for the ectop application.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

# --- State Icons ---
STATE_MAP: dict[str, str] = {
    "unknown": "⚪",
    "complete": "🟢",
    "queued": "🔵",
    "aborted": "🔴",
    "submitted": "🟡",
    "active": "🔥",
    "suspended": "🟠",
}

# --- Default Connection Settings ---
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3141
DEFAULT_REFRESH_INTERVAL = 2.0
