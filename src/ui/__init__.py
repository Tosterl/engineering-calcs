"""
UI module for Engineering Calculations Database.

This module provides the NiceGUI-based user interface including
the main application, pages, and reusable components.
"""

from src.ui.app import (
    create_app,
    AppState,
    state,
    CALCULATION_CATEGORIES,
)

from src.ui.pages import (
    dashboard_page,
    calculate_page,
    history_page,
    settings_page,
    CalculationState,
    HistoryState,
    SettingsState,
)


__all__ = [
    # Main app
    "create_app",
    "AppState",
    "state",
    "CALCULATION_CATEGORIES",
    # Pages
    "dashboard_page",
    "calculate_page",
    "history_page",
    "settings_page",
    # State classes
    "CalculationState",
    "HistoryState",
    "SettingsState",
]
