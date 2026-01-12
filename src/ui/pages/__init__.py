"""
UI Pages for Engineering Calculations Database.

This module provides the main page components for the NiceGUI-based
user interface, including dashboard, calculation, history, and settings pages.
"""

from src.ui.pages.dashboard import (
    dashboard_page,
    get_statistics,
    get_recent_calculations,
)
from src.ui.pages.calculate import (
    calculate_page,
    CalculationState,
)
from src.ui.pages.history import (
    history_page,
    HistoryState,
    fetch_calculations,
)
from src.ui.pages.settings import (
    settings_page,
    SettingsState,
    export_data,
    import_data,
)


__all__ = [
    # Dashboard
    "dashboard_page",
    "get_statistics",
    "get_recent_calculations",
    # Calculate
    "calculate_page",
    "CalculationState",
    # History
    "history_page",
    "HistoryState",
    "fetch_calculations",
    # Settings
    "settings_page",
    "SettingsState",
    "export_data",
    "import_data",
]
