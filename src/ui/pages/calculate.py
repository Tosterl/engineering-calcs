"""
Calculate page for Engineering Calculations Database.

This module provides the calculation interface with category browser,
input forms, calculation execution, and result display.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from nicegui import ui

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    calculation_registry,
)
from src.core.units import Quantity
from src.data.database import get_session
from src.data.models import Calculation as CalculationModel
from src.data.models import Formula
from src.services.report_service import ReportService
from src.config import get_settings


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


class CalculationState:
    """State management for the calculation page."""

    def __init__(self):
        self.selected_category: Optional[str] = None
        self.selected_calculation: Optional[Type[Calculation]] = None
        self.calculation_instance: Optional[Calculation] = None
        self.input_values: Dict[str, Any] = {}
        self.result: Optional[CalculationResult] = None
        self.unit_system: str = "SI"
        self.input_fields: Dict[str, ui.input] = {}


def create_category_list(
    state: CalculationState,
    on_category_select: Callable[[str], None],
    on_calc_select: Callable[[Type[Calculation]], None],
) -> ui.column:
    """Create the category browser sidebar."""

    with ui.column().classes("w-full") as sidebar:
        ui.label("Categories").classes("text-lg font-semibold mb-2")

        categories = calculation_registry.get_categories()

        for category in categories:
            icon = CATEGORY_ICONS.get(category, "calculate")
            calcs = calculation_registry.list_by_category(category)

            with ui.expansion(category, icon=icon).classes("w-full") as exp:
                for calc_class in calcs:
                    with ui.row().classes(
                        "w-full p-2 hover:bg-gray-100 cursor-pointer rounded"
                    ).on("click", lambda c=calc_class: on_calc_select(c)):
                        ui.icon("functions", size="sm").classes("text-gray-500")
                        ui.label(calc_class.name).classes("text-sm")

        if not categories:
            ui.label("No calculations available").classes("text-gray-500 italic")

    return sidebar


def create_input_form(
    calculation_class: Type[Calculation],
    state: CalculationState,
    on_calculate: Callable[[], None],
) -> ui.card:
    """Create the input form for a calculation."""

    state.input_fields = {}

    with ui.card().classes("w-full") as form_card:
        # Calculation header
        ui.label(calculation_class.name).classes("text-xl font-bold text-primary")
        ui.label(calculation_class.description).classes("text-gray-600 mb-4")

        # Formula display (if available)
        if hasattr(calculation_class, 'references') and calculation_class.references:
            with ui.expansion("References", icon="book").classes("w-full mb-4"):
                for ref in calculation_class.references:
                    ui.label(f"- {ref}").classes("text-sm text-gray-600")

        ui.separator()
        ui.label("Input Parameters").classes("text-lg font-semibold mt-4 mb-2")

        # Create input fields for each parameter
        with ui.column().classes("w-full gap-4"):
            for param in calculation_class.input_params:
                with ui.row().classes("w-full items-center gap-4"):
                    # Parameter info
                    with ui.column().classes("flex-1 gap-0"):
                        ui.label(param.name.replace("_", " ").title()).classes("font-medium")
                        ui.label(param.description).classes("text-sm text-gray-500")

                    # Input field with unit
                    with ui.row().classes("items-center gap-2"):
                        default_val = str(param.default) if param.default is not None else ""
                        input_field = ui.input(
                            label=f"Value",
                            value=default_val,
                            validation={"Required": lambda v: v.strip() != ""},
                        ).classes("w-32")

                        ui.label(param.unit).classes("text-gray-500 w-20")

                        state.input_fields[param.name] = input_field

        ui.separator().classes("my-4")

        # Calculate button
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Clear",
                icon="clear",
                on_click=lambda: clear_inputs(state)
            ).props("outline")

            ui.button(
                "Calculate",
                icon="calculate",
                on_click=on_calculate
            ).props("color=primary")

    return form_card


def clear_inputs(state: CalculationState) -> None:
    """Clear all input fields."""
    for field in state.input_fields.values():
        field.value = ""
    state.result = None


def create_results_display(
    result: CalculationResult,
    state: CalculationState,
    on_save: Callable[[], None],
    on_generate_report: Callable[[str], None],
) -> ui.card:
    """Create the results display section."""

    with ui.card().classes("w-full") as results_card:
        ui.label("Results").classes("text-xl font-bold text-primary mb-4")

        # Output values table
        with ui.column().classes("w-full gap-2"):
            for name, value in result.outputs.items():
                with ui.row().classes("w-full items-center p-2 bg-gray-50 rounded"):
                    ui.label(name.replace("_", " ").title()).classes(
                        "flex-1 font-medium"
                    )

                    if isinstance(value, Quantity):
                        formatted = f"{value.magnitude:.6g} {value.unit_string}"
                    else:
                        formatted = f"{value:.6g}" if isinstance(value, float) else str(value)

                    ui.label(formatted).classes("text-lg font-bold text-primary")

        ui.separator().classes("my-4")

        # Intermediate steps (expandable)
        if result.intermediate_steps:
            with ui.expansion("Calculation Steps", icon="list").classes("w-full"):
                for i, step in enumerate(result.intermediate_steps, 1):
                    with ui.card().classes("w-full mb-2"):
                        ui.label(f"Step {i}: {step.description}").classes("font-medium")

                        if step.formula:
                            with ui.row().classes("items-center gap-2 mt-2"):
                                ui.icon("functions", size="sm").classes("text-gray-500")
                                ui.label(step.formula).classes("font-mono text-sm")

                        if step.substitution:
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("arrow_forward", size="sm").classes("text-gray-500")
                                ui.label(step.substitution).classes("font-mono text-sm")

                        result_str = (
                            f"{step.result.magnitude:.6g} {step.result.unit_string}"
                            if isinstance(step.result, Quantity)
                            else str(step.result)
                        )
                        ui.label(f"= {result_str}").classes(
                            "font-mono text-sm text-primary font-bold mt-1"
                        )

        ui.separator().classes("my-4")

        # Action buttons
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Save Calculation",
                icon="save",
                on_click=on_save
            ).props("color=positive")

            # Report generation dropdown
            with ui.dropdown_button("Generate Report", icon="description").props(
                "color=secondary"
            ):
                ui.item(
                    "PDF Report",
                    on_click=lambda: on_generate_report("pdf")
                )
                ui.item(
                    "Word Document",
                    on_click=lambda: on_generate_report("docx")
                )

    return results_card


async def save_calculation(
    state: CalculationState,
    result: CalculationResult
) -> bool:
    """Save the calculation to the database."""
    try:
        async with get_session() as session:
            # First, check if formula exists or create it
            from sqlalchemy import select

            formula_query = select(Formula).where(
                Formula.name == state.selected_calculation.name,
                Formula.category == state.selected_calculation.category
            )
            existing = await session.execute(formula_query)
            formula = existing.scalar_one_or_none()

            if not formula:
                # Create the formula
                formula = Formula(
                    name=state.selected_calculation.name,
                    category=state.selected_calculation.category,
                    description=state.selected_calculation.description,
                    formula_latex="",  # Could be enhanced to include actual LaTeX
                    variables_json={
                        "inputs": [
                            {"name": p.name, "unit": p.unit, "description": p.description}
                            for p in state.selected_calculation.input_params
                        ],
                        "outputs": [
                            {"name": p.name, "unit": p.unit, "description": p.description}
                            for p in state.selected_calculation.output_params
                        ]
                    }
                )
                session.add(formula)
                await session.flush()

            # Prepare input/output JSON
            inputs_json = {}
            for name, value in result.inputs.items():
                if isinstance(value, Quantity):
                    inputs_json[name] = {
                        "magnitude": value.magnitude,
                        "unit": value.unit_string
                    }
                else:
                    inputs_json[name] = value

            outputs_json = {}
            for name, value in result.outputs.items():
                if isinstance(value, Quantity):
                    outputs_json[name] = {
                        "magnitude": value.magnitude,
                        "unit": value.unit_string
                    }
                else:
                    outputs_json[name] = value

            # Create the calculation record
            calculation = CalculationModel(
                formula_id=formula.id,
                inputs_json=inputs_json,
                outputs_json=outputs_json,
                notes="",
            )
            session.add(calculation)

        return True
    except Exception as e:
        print(f"Error saving calculation: {e}")
        return False


def generate_report(
    result: CalculationResult,
    format_type: str,
    state: CalculationState
) -> Optional[str]:
    """Generate a report in the specified format."""
    settings = get_settings()

    # Ensure output directory exists
    output_dir = Path(settings.report_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    calc_name = state.selected_calculation.name.replace(" ", "_")

    if format_type == "pdf":
        filename = f"{calc_name}_{timestamp}.pdf"
    else:
        filename = f"{calc_name}_{timestamp}.docx"

    output_path = output_dir / filename

    try:
        report_service = ReportService()
        options = {
            "title": f"Engineering Calculation: {state.selected_calculation.name}",
            "project_name": "Engineering Calculations Database",
            "author": "Engineer",
            "include_steps": True,
            "include_charts": True,
        }

        if format_type == "pdf":
            report_service.generate_pdf(result, str(output_path), options)
        else:
            report_service.generate_word(result, str(output_path), options)

        return str(output_path)
    except Exception as e:
        print(f"Error generating report: {e}")
        return None


def calculate_page(
    initial_category: Optional[str] = None,
    navigate_to_dashboard: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render the calculation page.

    Args:
        initial_category: Optional category to pre-select.
        navigate_to_dashboard: Callback to navigate back to dashboard.
    """
    state = CalculationState()
    state.selected_category = initial_category

    # Containers for dynamic content
    calc_details_container: Optional[ui.column] = None
    results_container: Optional[ui.column] = None

    def on_category_select(category: str) -> None:
        """Handle category selection."""
        state.selected_category = category

    def on_calc_select(calc_class: Type[Calculation]) -> None:
        """Handle calculation selection."""
        state.selected_calculation = calc_class
        state.calculation_instance = calc_class()
        state.result = None
        state.input_values = {}

        # Update the calculation details container
        if calc_details_container:
            calc_details_container.clear()
            with calc_details_container:
                create_input_form(calc_class, state, on_calculate)

    def on_calculate() -> None:
        """Handle calculate button click."""
        if not state.selected_calculation or not state.calculation_instance:
            ui.notify("Please select a calculation first", type="warning")
            return

        # Collect input values
        try:
            inputs = {}
            for param in state.selected_calculation.input_params:
                field = state.input_fields.get(param.name)
                if field and field.value:
                    try:
                        value = float(field.value)
                        # Create Quantity with the parameter's unit
                        inputs[param.name] = Quantity(value, param.unit)
                    except ValueError:
                        ui.notify(f"Invalid value for {param.name}", type="negative")
                        return
                elif param.default is not None:
                    inputs[param.name] = Quantity(param.default, param.unit)
                else:
                    ui.notify(f"Please provide a value for {param.name}", type="warning")
                    return

            # Perform the calculation
            result = state.calculation_instance.calculate(**inputs)
            state.result = result

            # Update results container
            if results_container:
                results_container.clear()
                with results_container:
                    create_results_display(
                        result,
                        state,
                        on_save,
                        on_generate_report
                    )

            ui.notify("Calculation completed successfully!", type="positive")

        except Exception as e:
            ui.notify(f"Calculation error: {str(e)}", type="negative")

    def on_save() -> None:
        """Handle save calculation button."""
        if not state.result:
            ui.notify("No calculation result to save", type="warning")
            return

        async def do_save():
            success = await save_calculation(state, state.result)
            if success:
                ui.notify("Calculation saved successfully!", type="positive")
            else:
                ui.notify("Failed to save calculation", type="negative")

        asyncio.create_task(do_save())

    def on_generate_report(format_type: str) -> None:
        """Handle report generation."""
        if not state.result:
            ui.notify("No calculation result for report", type="warning")
            return

        output_path = generate_report(state.result, format_type, state)
        if output_path:
            ui.notify(f"Report generated: {output_path}", type="positive")
            # Offer download
            ui.download(output_path)
        else:
            ui.notify("Failed to generate report", type="negative")

    # Main layout
    with ui.row().classes("w-full h-full"):
        # Left sidebar - Category browser
        with ui.column().classes("w-64 h-full border-r p-4 overflow-y-auto"):
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label("Calculations").classes("text-xl font-bold")
                if navigate_to_dashboard:
                    ui.button(icon="home", on_click=navigate_to_dashboard).props(
                        "flat round"
                    ).tooltip("Back to Dashboard")

            create_category_list(state, on_category_select, on_calc_select)

        # Main content area
        with ui.column().classes("flex-1 h-full p-6 overflow-y-auto"):
            # Calculation details
            calc_details_container = ui.column().classes("w-full max-w-3xl mx-auto")

            with calc_details_container:
                # Initial empty state
                with ui.card().classes("w-full"):
                    with ui.column().classes("items-center py-12"):
                        ui.icon("calculate", size="4rem").classes("text-gray-300")
                        ui.label("Select a Calculation").classes(
                            "text-xl font-semibold text-gray-500 mt-4"
                        )
                        ui.label(
                            "Choose a category and calculation from the sidebar to get started"
                        ).classes("text-gray-400")

            # Results section
            results_container = ui.column().classes("w-full max-w-3xl mx-auto mt-6")


# Module exports
__all__ = [
    "calculate_page",
    "CalculationState",
]
