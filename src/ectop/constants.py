# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
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

# --- UI Icons ---
ICON_SERVER = "🌍"
ICON_FAMILY = "📂"
ICON_TASK = "⚙️"
ICON_REASON = "💡"
ICON_MET = "✅"
ICON_NOT_MET = "❌"
ICON_UNKNOWN = "❓"
ICON_NOTE = "📝"
ICON_TIME = "⏳"
ICON_DATE = "📅"
ICON_CRON = "⏰"

# --- Magic Strings ---
LOADING_PLACEHOLDER = "loading..."
INHERITED_VAR_PREFIX = "inh_"
