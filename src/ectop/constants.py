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
TREE_FILTERS: list[str | None] = [None, "aborted", "active", "queued", "submitted", "suspended"]
"""Available status filters for the suite tree."""

LOADING_PLACEHOLDER = "loading..."
"""Placeholder text for lazy-loaded tree nodes."""
INHERITED_VAR_PREFIX = "inh_"
"""Prefix for inherited variable keys in the VariableTweaker."""
SYNTAX_THEME = "monokai"
"""Default theme for syntax highlighting."""
DEFAULT_SHELL = "bash"
"""Default shell for script execution."""
DEFAULT_EDITOR = "vi"
"""Default editor for script editing."""

# --- Status & Error Messages ---
ERROR_CONNECTION_FAILED = "Connection Failed"
"""Standard error message for connection failures."""
STATUS_SYNC_ERROR = "Sync Error"
"""Standard status message for synchronization errors."""

# --- UI Theme Colors ---
COLOR_BG = "#1a1b26"
COLOR_SIDEBAR_BG = "#16161e"
COLOR_CONTENT_BG = "#24283b"
COLOR_BORDER = "#565f89"
COLOR_TEXT = "#a9b1d6"
COLOR_TEXT_HIGHLIGHT = "#c0caf5"
COLOR_STATUS_BAR_BG = "#16161e"
COLOR_HEADER_BG = "#565f89"
