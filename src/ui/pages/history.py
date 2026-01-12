"""
History page for Engineering Calculations Database.

This module provides the calculation history view with filtering,
viewing details, re-running, and deleting saved calculations.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from nicegui import ui
from sqlalchemy import delete, desc, select

from src.data.database import get_session
from src.data.models import Calculation, Formula, Project
from src.core.calculations import calculation_registry
from src.core.units import Quantity


class HistoryState:
    """State management for the history page."""

    def __init__(self):
        self.calculations: List[Dict] = []
        self.selected_calculation: Optional[Dict] = None
        self.filter_category: str = "All"
        self.filter_date_from: Optional[datetime] = None
        self.filter_date_to: Optional[datetime] = None
        self.search_query: str = ""


async def fetch_calculations(
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search_query: Optional[str] = None,
) -> List[Dict]:
    """Fetch calculations from database with filters."""
    calculations = []

    try:
        async with get_session() as session:
            # Build query
            query = (
                select(Calculation, Formula)
                .join(Formula, Calculation.formula_id == Formula.id)
                .order_by(desc(Calculation.created_at))
            )

            # Apply filters
            if category and category != "All":
                query = query.where(Formula.category == category)

            if date_from:
                query = query.where(Calculation.created_at >= date_from)

            if date_to:
                # Add one day to include the entire end date
                query = query.where(Calculation.created_at < date_to + timedelta(days=1))

            result = await session.execute(query)

            for calc, formula in result.all():
                calc_dict = {
                    "id": calc.id,
                    "formula_id": formula.id,
                    "formula_name": formula.name,
                    "category": formula.category,
                    "description": formula.description,
                    "created_at": calc.created_at,
                    "inputs": calc.inputs_json,
                    "outputs": calc.outputs_json,
                    "notes": calc.notes,
                    "project_id": calc.project_id,
                }

                # Apply search filter
                if search_query:
                    search_lower = search_query.lower()
                    if (
                        search_lower not in formula.name.lower()
                        and search_lower not in formula.category.lower()
                        and (not formula.description or search_lower not in formula.description.lower())
                    ):
                        continue

                calculations.append(calc_dict)

    except Exception as e:
        print(f"Error fetching calculations: {e}")

    return calculations


async def delete_calculation(calc_id: int) -> bool:
    """Delete a calculation from the database."""
    try:
        async with get_session() as session:
            await session.execute(
                delete(Calculation).where(Calculation.id == calc_id)
            )
        return True
    except Exception as e:
        print(f"Error deleting calculation: {e}")
        return False


def format_value(value: Dict | float | int | str) -> str:
    """Format a value for display."""
    if isinstance(value, dict):
        magnitude = value.get("magnitude", value.get("value", 0))
        unit = value.get("unit", "")
        if isinstance(magnitude, float):
            return f"{magnitude:.6g} {unit}".strip()
        return f"{magnitude} {unit}".strip()
    elif isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def create_calculation_row(
    calc: Dict,
    state: HistoryState,
    on_view: Callable[[Dict], None],
    on_rerun: Callable[[Dict], None],
    on_delete: Callable[[Dict], None],
) -> None:
    """Create a row for a calculation in the history list."""

    with ui.row().classes(
        "w-full items-center p-3 hover:bg-gray-50 border-b cursor-pointer"
    ):
        # Selection indicator
        with ui.column().classes("w-8"):
            if state.selected_calculation and state.selected_calculation["id"] == calc["id"]:
                ui.icon("check_circle", size="sm").classes("text-primary")

        # Main content (clickable)
        with ui.column().classes("flex-1").on("click", lambda c=calc: on_view(c)):
            ui.label(calc["formula_name"]).classes("font-medium")
            with ui.row().classes("gap-4 text-sm text-gray-500"):
                ui.label(calc["category"])
                ui.label("|")
                ui.label(calc["created_at"].strftime("%Y-%m-%d %H:%M"))

        # Quick output preview
        with ui.column().classes("w-48 text-right"):
            outputs = calc.get("outputs", {})
            if outputs:
                first_output = list(outputs.items())[0]
                name, value = first_output
                ui.label(f"{name}: {format_value(value)}").classes(
                    "text-sm font-mono text-primary"
                )

        # Action buttons
        with ui.row().classes("gap-1"):
            ui.button(
                icon="visibility",
                on_click=lambda c=calc: on_view(c)
            ).props("flat round size=sm").tooltip("View Details")

            ui.button(
                icon="replay",
                on_click=lambda c=calc: on_rerun(c)
            ).props("flat round size=sm").tooltip("Re-run Calculation")

            ui.button(
                icon="delete",
                on_click=lambda c=calc: on_delete(c)
            ).props("flat round size=sm color=negative").tooltip("Delete")


def create_details_panel(
    calc: Dict,
    on_close: Callable[[], None],
    on_rerun: Callable[[Dict], None],
) -> ui.card:
    """Create the details panel for a selected calculation."""

    with ui.card().classes("w-full") as panel:
        # Header
        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.label(calc["formula_name"]).classes("text-xl font-bold text-primary")
            ui.button(icon="close", on_click=on_close).props("flat round")

        # Metadata
        with ui.row().classes("gap-4 mb-4"):
            with ui.row().classes("items-center gap-1"):
                ui.icon("category", size="sm").classes("text-gray-500")
                ui.label(calc["category"]).classes("text-sm")

            with ui.row().classes("items-center gap-1"):
                ui.icon("schedule", size="sm").classes("text-gray-500")
                ui.label(calc["created_at"].strftime("%Y-%m-%d %H:%M:%S")).classes("text-sm")

        if calc.get("description"):
            ui.label(calc["description"]).classes("text-gray-600 mb-4")

        ui.separator()

        # Inputs section
        ui.label("Inputs").classes("text-lg font-semibold mt-4 mb-2")

        with ui.column().classes("w-full gap-2"):
            for name, value in calc.get("inputs", {}).items():
                with ui.row().classes("w-full items-center p-2 bg-gray-50 rounded"):
                    ui.label(name.replace("_", " ").title()).classes("flex-1")
                    ui.label(format_value(value)).classes("font-mono")

        ui.separator().classes("my-4")

        # Outputs section
        ui.label("Results").classes("text-lg font-semibold mb-2")

        with ui.column().classes("w-full gap-2"):
            for name, value in calc.get("outputs", {}).items():
                with ui.row().classes("w-full items-center p-2 bg-blue-50 rounded"):
                    ui.label(name.replace("_", " ").title()).classes("flex-1 font-medium")
                    ui.label(format_value(value)).classes("font-mono text-primary font-bold")

        # Notes section
        if calc.get("notes"):
            ui.separator().classes("my-4")
            ui.label("Notes").classes("text-lg font-semibold mb-2")
            ui.label(calc["notes"]).classes("text-gray-600")

        ui.separator().classes("my-4")

        # Actions
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Re-run Calculation",
                icon="replay",
                on_click=lambda: on_rerun(calc)
            ).props("color=primary")

    return panel


def history_page(
    navigate_to_calculate: Optional[Callable[[str], None]] = None,
    navigate_to_dashboard: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render the history page.

    Args:
        navigate_to_calculate: Callback to navigate to calculate page.
        navigate_to_dashboard: Callback to navigate to dashboard.
    """
    state = HistoryState()

    # Containers for dynamic content
    list_container: Optional[ui.column] = None
    details_container: Optional[ui.column] = None

    async def refresh_list() -> None:
        """Refresh the calculations list."""
        date_from = None
        date_to = None

        # Parse date filters (would need actual date picker values)

        state.calculations = await fetch_calculations(
            category=state.filter_category if state.filter_category != "All" else None,
            date_from=date_from,
            date_to=date_to,
            search_query=state.search_query if state.search_query else None,
        )

        if list_container:
            list_container.clear()
            with list_container:
                if state.calculations:
                    for calc in state.calculations:
                        create_calculation_row(
                            calc,
                            state,
                            on_view,
                            on_rerun,
                            on_delete,
                        )
                else:
                    with ui.column().classes("w-full items-center py-12"):
                        ui.icon("inbox", size="4rem").classes("text-gray-300")
                        ui.label("No calculations found").classes(
                            "text-xl text-gray-500 mt-4"
                        )
                        ui.label("Adjust your filters or run some calculations").classes(
                            "text-gray-400"
                        )

    def on_view(calc: Dict) -> None:
        """Handle view calculation."""
        state.selected_calculation = calc

        if details_container:
            details_container.clear()
            with details_container:
                create_details_panel(calc, on_close_details, on_rerun)

    def on_close_details() -> None:
        """Handle close details panel."""
        state.selected_calculation = None
        if details_container:
            details_container.clear()
            with details_container:
                with ui.column().classes("w-full items-center py-12"):
                    ui.icon("info", size="3rem").classes("text-gray-300")
                    ui.label("Select a calculation to view details").classes(
                        "text-gray-500 mt-4"
                    )

    def on_rerun(calc: Dict) -> None:
        """Handle re-run calculation."""
        if navigate_to_calculate:
            navigate_to_calculate(calc["category"])

    def on_delete(calc: Dict) -> None:
        """Handle delete calculation."""

        async def do_delete():
            with ui.dialog() as dialog, ui.card():
                ui.label("Delete Calculation").classes("text-lg font-bold")
                ui.label(f"Are you sure you want to delete '{calc['formula_name']}'?").classes(
                    "text-gray-600"
                )

                with ui.row().classes("w-full justify-end gap-2 mt-4"):
                    ui.button("Cancel", on_click=dialog.close).props("flat")

                    async def confirm_delete():
                        success = await delete_calculation(calc["id"])
                        if success:
                            ui.notify("Calculation deleted", type="positive")
                            if state.selected_calculation and state.selected_calculation["id"] == calc["id"]:
                                on_close_details()
                            await refresh_list()
                        else:
                            ui.notify("Failed to delete calculation", type="negative")
                        dialog.close()

                    ui.button(
                        "Delete",
                        on_click=confirm_delete
                    ).props("color=negative")

            dialog.open()

        asyncio.create_task(do_delete())

    def on_filter_change() -> None:
        """Handle filter changes."""
        asyncio.create_task(refresh_list())

    def on_search(query: str) -> None:
        """Handle search input."""
        state.search_query = query
        asyncio.create_task(refresh_list())

    # Main layout
    with ui.column().classes("w-full h-full"):
        # Header
        with ui.row().classes("w-full items-center justify-between p-4 border-b"):
            with ui.row().classes("items-center gap-4"):
                if navigate_to_dashboard:
                    ui.button(icon="arrow_back", on_click=navigate_to_dashboard).props(
                        "flat round"
                    ).tooltip("Back to Dashboard")
                ui.label("Calculation History").classes("text-2xl font-bold")

            # Search
            search_input = ui.input(
                placeholder="Search calculations...",
            ).classes("w-64").on(
                "keyup.enter", lambda e: on_search(e.sender.value)
            )
            ui.button(icon="search", on_click=lambda: on_search(search_input.value)).props(
                "flat round"
            )

        # Filters bar
        with ui.row().classes("w-full p-4 gap-4 bg-gray-50 border-b"):
            # Category filter
            with ui.column().classes("gap-1"):
                ui.label("Category").classes("text-sm text-gray-500")
                categories = ["All"] + calculation_registry.get_categories()
                category_select = ui.select(
                    options=categories,
                    value="All",
                    on_change=lambda e: (
                        setattr(state, "filter_category", e.value),
                        on_filter_change()
                    )
                ).classes("w-40")

            # Date range filters
            with ui.column().classes("gap-1"):
                ui.label("From Date").classes("text-sm text-gray-500")
                date_from_input = ui.input(
                    placeholder="YYYY-MM-DD"
                ).classes("w-32")

            with ui.column().classes("gap-1"):
                ui.label("To Date").classes("text-sm text-gray-500")
                date_to_input = ui.input(
                    placeholder="YYYY-MM-DD"
                ).classes("w-32")

            # Apply filters button
            with ui.column().classes("justify-end"):
                ui.button(
                    "Apply Filters",
                    icon="filter_list",
                    on_click=on_filter_change
                ).props("outline")

            # Clear filters
            with ui.column().classes("justify-end"):
                ui.button(
                    "Clear",
                    icon="clear",
                    on_click=lambda: (
                        setattr(state, "filter_category", "All"),
                        setattr(state, "search_query", ""),
                        category_select.set_value("All"),
                        search_input.set_value(""),
                        date_from_input.set_value(""),
                        date_to_input.set_value(""),
                        on_filter_change()
                    )
                ).props("flat")

        # Main content
        with ui.row().classes("flex-1 w-full"):
            # List panel
            with ui.column().classes("flex-1 overflow-y-auto"):
                list_container = ui.column().classes("w-full")

                # Initial loading message
                with list_container:
                    with ui.column().classes("w-full items-center py-12"):
                        ui.spinner(size="lg")
                        ui.label("Loading calculations...").classes("text-gray-500 mt-4")

            # Details panel
            with ui.column().classes("w-96 border-l p-4 overflow-y-auto"):
                details_container = ui.column().classes("w-full")

                with details_container:
                    with ui.column().classes("w-full items-center py-12"):
                        ui.icon("info", size="3rem").classes("text-gray-300")
                        ui.label("Select a calculation to view details").classes(
                            "text-gray-500 mt-4"
                        )

        # Load initial data
        ui.timer(0.1, lambda: asyncio.create_task(refresh_list()), once=True)


# Module exports
__all__ = [
    "history_page",
    "HistoryState",
    "fetch_calculations",
]
