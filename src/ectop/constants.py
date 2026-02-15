# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Constants for the ectop application.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

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
ICON_UNKNOWN_STATE = "⚪"

# --- Variable Types ---
VAR_TYPE_USER = "User"
VAR_TYPE_GENERATED = "Generated"
VAR_TYPE_INHERITED = "Inherited"

# --- Expression Labels ---
EXPR_OR_LABEL = "OR (Any must be true)"
EXPR_AND_LABEL = "AND (All must be true)"

# --- Magic Strings ---
LOADING_PLACEHOLDER = "loading..."
INHERITED_VAR_PREFIX = "inh_"
