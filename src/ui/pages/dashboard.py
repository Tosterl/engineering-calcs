"""
Dashboard page for Engineering Calculations Database.

This module provides the main dashboard view with welcome message,
quick search, recent calculations, category cards, and statistics.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, List, Optional

from nicegui import ui
from sqlalchemy import func, select, desc

from src.data.database import get_session
from src.data.models import Calculation, Formula, Project
from src.core.calculations import calculation_registry
from src.services.search_service import SearchService


# Category icons mapping
CATEGORY_ICONS = {
    "Statics": "architecture",
    "Fluids": "water_drop",
    "Thermodynamics": "whatshot",
    "Materials": "construction",
    "Mechanical": "settings",
    "Controls": "tune",
    "Vibrations": "vibration",
}

# Category colors mapping
CATEGORY_COLORS = {
    "Statics": "blue",
    "Fluids": "cyan",
    "Thermodynamics": "orange",
    "Materials": "brown",
    "Mechanical": "grey",
    "Controls": "purple",
    "Vibrations": "green",
}


async def get_statistics() -> dict:
    """Retrieve statistics from the database."""
    stats = {
        "total_calculations": 0,
        "total_projects": 0,
        "total_formulas": 0,
        "calculations_this_week": 0,
    }

    try:
        async with get_session() as session:
            # Total calculations
            result = await session.execute(select(func.count(Calculation.id)))
            stats["total_calculations"] = result.scalar() or 0

            # Total projects
            result = await session.execute(select(func.count(Project.id)))
            stats["total_projects"] = result.scalar() or 0

            # Total formulas
            result = await session.execute(select(func.count(Formula.id)))
            stats["total_formulas"] = result.scalar() or 0

            # Calculations this week
            week_ago = datetime.utcnow() - timedelta(days=7)
            result = await session.execute(
                select(func.count(Calculation.id)).where(
                    Calculation.created_at >= week_ago
                )
            )
            stats["calculations_this_week"] = result.scalar() or 0
    except Exception:
        # If database not initialized, return zeros
        pass

    return stats


async def get_recent_calculations(limit: int = 5) -> List[dict]:
    """Retrieve recent calculations from the database."""
    recent = []

    try:
        async with get_session() as session:
            result = await session.execute(
                select(Calculation, Formula)
                .join(Formula, Calculation.formula_id == Formula.id)
                .order_by(desc(Calculation.created_at))
                .limit(limit)
            )

            for calc, formula in result.all():
                recent.append({
                    "id": calc.id,
                    "formula_name": formula.name,
                    "category": formula.category,
                    "created_at": calc.created_at,
                    "inputs": calc.inputs_json,
                    "outputs": calc.outputs_json,
                })
    except Exception:
        # If database not initialized or empty, return empty list
        pass

    return recent


def create_stat_card(title: str, value: str | int, icon: str, color: str = "primary") -> None:
    """Create a statistics card component."""
    with ui.card().classes("w-full"):
        with ui.row().classes("items-center gap-4"):
            ui.icon(icon, size="lg").classes(f"text-{color}")
            with ui.column().classes("gap-0"):
                ui.label(str(value)).classes("text-2xl font-bold")
                ui.label(title).classes("text-sm text-gray-500")


def create_category_card(
    category: str,
    calc_count: int,
    on_click: Callable[[str], None]
) -> None:
    """Create a category card for quick access."""
    icon = CATEGORY_ICONS.get(category, "calculate")
    color = CATEGORY_COLORS.get(category, "primary")

    with ui.card().classes("cursor-pointer hover:shadow-lg transition-shadow").on(
        "click", lambda: on_click(category)
    ):
        with ui.column().classes("items-center p-4 gap-2"):
            ui.icon(icon, size="xl").classes(f"text-{color}")
            ui.label(category).classes("font-semibold")
            ui.label(f"{calc_count} calculations").classes("text-sm text-gray-500")


def create_recent_calculation_row(
    calc: dict,
    on_view: Callable[[int], None],
    on_rerun: Callable[[int], None]
) -> None:
    """Create a row for a recent calculation."""
    with ui.row().classes("w-full items-center justify-between p-2 hover:bg-gray-50"):
        with ui.column().classes("gap-0"):
            ui.label(calc["formula_name"]).classes("font-medium")
            ui.label(calc["category"]).classes("text-sm text-gray-500")

        with ui.row().classes("gap-2"):
            time_str = calc["created_at"].strftime("%Y-%m-%d %H:%M")
            ui.label(time_str).classes("text-sm text-gray-400 mr-4")

            ui.button(icon="visibility", on_click=lambda c=calc: on_view(c["id"])).props(
                "flat round size=sm"
            ).tooltip("View Details")

            ui.button(icon="replay", on_click=lambda c=calc: on_rerun(c["id"])).props(
                "flat round size=sm"
            ).tooltip("Re-run Calculation")


def dashboard_page(
    navigate_to_calculate: Optional[Callable[[str], None]] = None,
    navigate_to_history: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render the dashboard page.

    Args:
        navigate_to_calculate: Callback to navigate to calculate page with category.
        navigate_to_history: Callback to navigate to history page.
    """
    search_service = SearchService()

    # State for search
    search_query = {"value": ""}
    search_results_container = None

    def handle_search(query: str) -> None:
        """Handle search query."""
        search_query["value"] = query
        if search_results_container:
            search_results_container.clear()

            if query.strip():
                results = search_service.search_calculations(query)
                with search_results_container:
                    if results:
                        with ui.card().classes("w-full"):
                            ui.label("Search Results").classes("font-semibold mb-2")
                            for result in results[:10]:
                                with ui.row().classes(
                                    "w-full items-center justify-between p-2 hover:bg-gray-50 cursor-pointer"
                                ).on("click", lambda r=result: handle_select_calculation(r)):
                                    with ui.column().classes("gap-0"):
                                        ui.label(result.calculation_class.name).classes("font-medium")
                                        ui.label(result.calculation_class.category).classes(
                                            "text-sm text-gray-500"
                                        )
                                    ui.label(f"Match: {result.score:.0%}").classes(
                                        "text-sm text-gray-400"
                                    )
                    else:
                        ui.label("No calculations found").classes("text-gray-500 italic")

    def handle_select_calculation(result) -> None:
        """Handle selection of a search result."""
        if navigate_to_calculate:
            navigate_to_calculate(result.calculation_class.category)

    def handle_category_click(category: str) -> None:
        """Handle category card click."""
        if navigate_to_calculate:
            navigate_to_calculate(category)

    def handle_view_calculation(calc_id: int) -> None:
        """Handle view calculation button."""
        if navigate_to_history:
            navigate_to_history()

    def handle_rerun_calculation(calc_id: int) -> None:
        """Handle re-run calculation button."""
        if navigate_to_calculate:
            navigate_to_calculate("")

    async def load_dashboard_data():
        """Load dashboard data asynchronously."""
        stats = await get_statistics()
        recent = await get_recent_calculations()
        return stats, recent

    # Main layout
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
        # Welcome section
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-1"):
                ui.label("Engineering Calculations Database").classes(
                    "text-3xl font-bold text-primary"
                )
                ui.label("Welcome back! Start a new calculation or review your work.").classes(
                    "text-gray-600"
                )

            ui.icon("engineering", size="4rem").classes("text-primary opacity-50")

        ui.separator()

        # Quick search section
        with ui.card().classes("w-full"):
            ui.label("Quick Search").classes("font-semibold mb-2")
            with ui.row().classes("w-full gap-2"):
                search_input = ui.input(
                    placeholder="Search for calculations, formulas, or categories...",
                ).classes("flex-grow").on(
                    "keyup.enter", lambda e: handle_search(e.sender.value)
                )
                ui.button(
                    "Search",
                    icon="search",
                    on_click=lambda: handle_search(search_input.value)
                ).props("color=primary")

            search_results_container = ui.column().classes("w-full mt-2")

        # Statistics section
        ui.label("Overview").classes("text-xl font-semibold")

        with ui.row().classes("w-full gap-4"):
            with ui.column().classes("flex-1"):
                # Statistics will be loaded asynchronously
                stats_container = ui.column().classes("w-full")

                async def update_stats():
                    stats, _ = await load_dashboard_data()
                    with stats_container:
                        stats_container.clear()
                        with ui.grid(columns=4).classes("w-full gap-4"):
                            create_stat_card(
                                "Total Calculations",
                                stats["total_calculations"],
                                "calculate",
                                "primary"
                            )
                            create_stat_card(
                                "Projects",
                                stats["total_projects"],
                                "folder",
                                "secondary"
                            )
                            create_stat_card(
                                "Available Formulas",
                                len(calculation_registry.list_all()),
                                "functions",
                                "positive"
                            )
                            create_stat_card(
                                "This Week",
                                stats["calculations_this_week"],
                                "trending_up",
                                "info"
                            )

                ui.timer(0.1, update_stats, once=True)

        # Main content grid
        with ui.row().classes("w-full gap-6"):
            # Left column - Recent calculations
            with ui.column().classes("flex-1"):
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between mb-4"):
                        ui.label("Recent Calculations").classes("text-lg font-semibold")
                        if navigate_to_history:
                            ui.button(
                                "View All",
                                icon="arrow_forward",
                                on_click=navigate_to_history
                            ).props("flat")

                    recent_container = ui.column().classes("w-full divide-y")

                    async def update_recent():
                        _, recent = await load_dashboard_data()
                        with recent_container:
                            recent_container.clear()
                            if recent:
                                for calc in recent:
                                    create_recent_calculation_row(
                                        calc,
                                        handle_view_calculation,
                                        handle_rerun_calculation
                                    )
                            else:
                                with ui.column().classes("w-full items-center py-8"):
                                    ui.icon("inbox", size="3rem").classes("text-gray-300")
                                    ui.label("No calculations yet").classes(
                                        "text-gray-500 mt-2"
                                    )
                                    ui.label(
                                        "Start by selecting a category and running a calculation"
                                    ).classes("text-sm text-gray-400")

                    ui.timer(0.1, update_recent, once=True)

            # Right column - Category cards
            with ui.column().classes("w-80"):
                ui.label("Categories").classes("text-lg font-semibold mb-2")

                categories = calculation_registry.get_categories()

                with ui.column().classes("gap-2"):
                    if categories:
                        for category in categories:
                            calcs = calculation_registry.list_by_category(category)
                            create_category_card(
                                category,
                                len(calcs),
                                handle_category_click
                            )
                    else:
                        # Show default categories if none registered
                        default_categories = [
                            "Statics", "Fluids", "Thermodynamics",
                            "Materials", "Mechanical", "Controls", "Vibrations"
                        ]
                        for category in default_categories:
                            create_category_card(
                                category,
                                0,
                                handle_category_click
                            )

        # Quick actions
        with ui.card().classes("w-full"):
            ui.label("Quick Actions").classes("font-semibold mb-2")
            with ui.row().classes("gap-4"):
                ui.button(
                    "New Calculation",
                    icon="add",
                    on_click=lambda: navigate_to_calculate("") if navigate_to_calculate else None
                ).props("color=primary")

                ui.button(
                    "View History",
                    icon="history",
                    on_click=navigate_to_history if navigate_to_history else None
                ).props("color=secondary outline")

                ui.button(
                    "Export Data",
                    icon="download"
                ).props("outline")


# Module exports
__all__ = [
    "dashboard_page",
    "get_statistics",
    "get_recent_calculations",
]
