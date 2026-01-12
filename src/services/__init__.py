"""
Services module for Engineering Calculations Database.

This module provides various services for searching, reporting,
visualization, and managing engineering calculations.
"""

from src.services.chart_service import ChartService, DARK_THEME, LIGHT_THEME
from src.services.report_service import ReportOptions, ReportService
from src.services.search_service import SearchResult, SearchService
from src.services.truss_visualization import (
    TrussVisualization,
    TENSION_COLOR,
    COMPRESSION_COLOR,
    ZERO_FORCE_COLOR,
    REACTION_COLOR,
    LOAD_COLOR,
)
from src.services.user_settings import (
    UserSettings,
    UserSettingsService,
    get_user_settings,
)
from src.services.formula_diagrams import (
    FormulaDiagram,
    FormulaExample,
    FormulaDiagramService,
)

__all__ = [
    "ChartService",
    "DARK_THEME",
    "LIGHT_THEME",
    "ReportOptions",
    "ReportService",
    "SearchResult",
    "SearchService",
    "TrussVisualization",
    "TENSION_COLOR",
    "COMPRESSION_COLOR",
    "ZERO_FORCE_COLOR",
    "REACTION_COLOR",
    "LOAD_COLOR",
    "UserSettings",
    "UserSettingsService",
    "get_user_settings",
    "FormulaDiagram",
    "FormulaExample",
    "FormulaDiagramService",
]
