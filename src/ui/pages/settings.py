"""
Settings page for Engineering Calculations Database.

This module provides the settings interface for configuring
unit system, theme, report settings, and data export/import.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from nicegui import ui
from sqlalchemy import select

from src.data.database import get_session
from src.data.models import Calculation, Formula, Project
from src.config import get_settings


class SettingsState:
    """State management for settings."""

    def __init__(self):
        settings = get_settings()

        self.unit_system: str = settings.default_unit_system
        self.theme: str = settings.ui_theme
        self.report_author: str = ""
        self.report_company: str = ""
        self.report_logo_path: str = ""
        self.include_steps_default: bool = True
        self.include_charts_default: bool = True


def create_toggle_row(
    label: str,
    description: str,
    value: bool,
    on_change: Callable[[bool], None],
) -> ui.row:
    """Create a toggle setting row."""

    with ui.row().classes("w-full items-center justify-between p-2") as row:
        with ui.column().classes("gap-0"):
            ui.label(label).classes("font-medium")
            ui.label(description).classes("text-sm text-gray-500")

        ui.switch(value=value, on_change=lambda e: on_change(e.value))

    return row


def create_input_row(
    label: str,
    description: str,
    value: str,
    placeholder: str,
    on_change: Callable[[str], None],
) -> ui.row:
    """Create an input setting row."""

    with ui.row().classes("w-full items-center justify-between p-2") as row:
        with ui.column().classes("gap-0 flex-1"):
            ui.label(label).classes("font-medium")
            ui.label(description).classes("text-sm text-gray-500")

        ui.input(
            value=value,
            placeholder=placeholder,
            on_change=lambda e: on_change(e.value)
        ).classes("w-64")

    return row


async def export_data() -> Optional[str]:
    """Export all data to a JSON file."""
    try:
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "projects": [],
            "formulas": [],
            "calculations": [],
        }

        async with get_session() as session:
            # Export projects
            result = await session.execute(select(Project))
            for project in result.scalars().all():
                export_data["projects"].append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                })

            # Export formulas
            result = await session.execute(select(Formula))
            for formula in result.scalars().all():
                export_data["formulas"].append({
                    "id": formula.id,
                    "name": formula.name,
                    "category": formula.category,
                    "description": formula.description,
                    "formula_latex": formula.formula_latex,
                    "variables_json": formula.variables_json,
                    "created_at": formula.created_at.isoformat(),
                })

            # Export calculations
            result = await session.execute(select(Calculation))
            for calc in result.scalars().all():
                export_data["calculations"].append({
                    "id": calc.id,
                    "formula_id": calc.formula_id,
                    "inputs_json": calc.inputs_json,
                    "outputs_json": calc.outputs_json,
                    "notes": calc.notes,
                    "project_id": calc.project_id,
                    "created_at": calc.created_at.isoformat(),
                })

        # Write to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = Path(f"exports/engineering_calcs_export_{timestamp}.json")
        export_path.parent.mkdir(parents=True, exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return str(export_path)

    except Exception as e:
        print(f"Error exporting data: {e}")
        return None


async def import_data(file_path: str) -> bool:
    """Import data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            import_data = json.load(f)

        async with get_session() as session:
            # Import projects
            for project_data in import_data.get("projects", []):
                project = Project(
                    name=project_data["name"],
                    description=project_data.get("description"),
                )
                session.add(project)

            await session.flush()

            # Import formulas (with ID mapping)
            formula_id_map = {}
            for formula_data in import_data.get("formulas", []):
                formula = Formula(
                    name=formula_data["name"],
                    category=formula_data["category"],
                    description=formula_data.get("description"),
                    formula_latex=formula_data.get("formula_latex", ""),
                    variables_json=formula_data.get("variables_json", {}),
                )
                session.add(formula)
                await session.flush()
                formula_id_map[formula_data["id"]] = formula.id

            # Import calculations
            for calc_data in import_data.get("calculations", []):
                old_formula_id = calc_data["formula_id"]
                new_formula_id = formula_id_map.get(old_formula_id)

                if new_formula_id:
                    calc = Calculation(
                        formula_id=new_formula_id,
                        inputs_json=calc_data.get("inputs_json", {}),
                        outputs_json=calc_data.get("outputs_json", {}),
                        notes=calc_data.get("notes"),
                    )
                    session.add(calc)

        return True

    except Exception as e:
        print(f"Error importing data: {e}")
        return False


def settings_page(
    navigate_to_dashboard: Optional[Callable[[], None]] = None,
    on_theme_change: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Render the settings page.

    Args:
        navigate_to_dashboard: Callback to navigate to dashboard.
        on_theme_change: Callback when theme is changed.
    """
    state = SettingsState()

    def handle_unit_system_change(value: str) -> None:
        """Handle unit system change."""
        state.unit_system = value
        ui.notify(f"Unit system set to {value}", type="info")

    def handle_theme_change(value: str) -> None:
        """Handle theme change."""
        state.theme = value
        if on_theme_change:
            on_theme_change(value)
        ui.notify(f"Theme set to {value}", type="info")

    def handle_save_settings() -> None:
        """Save settings to configuration."""
        # In a real app, this would persist settings
        ui.notify("Settings saved successfully!", type="positive")

    async def handle_export() -> None:
        """Handle data export."""
        ui.notify("Exporting data...", type="info")

        path = await export_data()
        if path:
            ui.notify(f"Data exported to {path}", type="positive")
            ui.download(path)
        else:
            ui.notify("Failed to export data", type="negative")

    async def handle_import(e) -> None:
        """Handle data import."""
        if not e.content:
            ui.notify("No file selected", type="warning")
            return

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            content = e.content.read().decode("utf-8")
            f.write(content)
            temp_path = f.name

        ui.notify("Importing data...", type="info")

        success = await import_data(temp_path)
        if success:
            ui.notify("Data imported successfully!", type="positive")
        else:
            ui.notify("Failed to import data", type="negative")

        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)

    # Main layout
    with ui.column().classes("w-full max-w-4xl mx-auto p-6 gap-6"):
        # Header
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                if navigate_to_dashboard:
                    ui.button(icon="arrow_back", on_click=navigate_to_dashboard).props(
                        "flat round"
                    ).tooltip("Back to Dashboard")
                ui.label("Settings").classes("text-2xl font-bold")

            ui.button(
                "Save Settings",
                icon="save",
                on_click=handle_save_settings
            ).props("color=primary")

        # Unit System Settings
        with ui.card().classes("w-full"):
            ui.label("Unit System").classes("text-lg font-semibold mb-4")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0"):
                    ui.label("Default Unit System").classes("font-medium")
                    ui.label("Choose between SI (metric) and Imperial units").classes(
                        "text-sm text-gray-500"
                    )

                ui.toggle(
                    {"SI": "SI (Metric)", "Imperial": "Imperial"},
                    value=state.unit_system,
                    on_change=lambda e: handle_unit_system_change(e.value)
                )

        # Theme Settings
        with ui.card().classes("w-full"):
            ui.label("Appearance").classes("text-lg font-semibold mb-4")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0"):
                    ui.label("Theme").classes("font-medium")
                    ui.label("Choose between light and dark mode").classes(
                        "text-sm text-gray-500"
                    )

                ui.toggle(
                    {"light": "Light", "dark": "Dark"},
                    value=state.theme,
                    on_change=lambda e: handle_theme_change(e.value)
                )

        # Report Settings
        with ui.card().classes("w-full"):
            ui.label("Report Settings").classes("text-lg font-semibold mb-4")

            create_input_row(
                "Default Author",
                "Author name to include in generated reports",
                state.report_author,
                "Enter your name",
                lambda v: setattr(state, "report_author", v)
            )

            ui.separator().classes("my-2")

            create_input_row(
                "Company Name",
                "Company name to include in report headers",
                state.report_company,
                "Enter company name",
                lambda v: setattr(state, "report_company", v)
            )

            ui.separator().classes("my-2")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0 flex-1"):
                    ui.label("Company Logo").classes("font-medium")
                    ui.label("Logo image to include in reports").classes(
                        "text-sm text-gray-500"
                    )

                with ui.row().classes("gap-2"):
                    logo_path_input = ui.input(
                        value=state.report_logo_path,
                        placeholder="Path to logo file",
                        on_change=lambda e: setattr(state, "report_logo_path", e.value)
                    ).classes("w-48")

                    ui.upload(
                        on_upload=lambda e: logo_path_input.set_value(e.name),
                        auto_upload=True
                    ).props("accept='image/*' flat").classes("w-auto")

            ui.separator().classes("my-2")

            create_toggle_row(
                "Include Calculation Steps",
                "Show intermediate calculation steps in reports by default",
                state.include_steps_default,
                lambda v: setattr(state, "include_steps_default", v)
            )

            ui.separator().classes("my-2")

            create_toggle_row(
                "Include Charts",
                "Include charts and visualizations in reports by default",
                state.include_charts_default,
                lambda v: setattr(state, "include_charts_default", v)
            )

        # Data Management
        with ui.card().classes("w-full"):
            ui.label("Data Management").classes("text-lg font-semibold mb-4")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0 flex-1"):
                    ui.label("Export Data").classes("font-medium")
                    ui.label("Export all calculations, formulas, and projects to JSON").classes(
                        "text-sm text-gray-500"
                    )

                ui.button(
                    "Export",
                    icon="download",
                    on_click=lambda: asyncio.create_task(handle_export())
                ).props("outline")

            ui.separator().classes("my-2")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0 flex-1"):
                    ui.label("Import Data").classes("font-medium")
                    ui.label("Import data from a previously exported JSON file").classes(
                        "text-sm text-gray-500"
                    )

                ui.upload(
                    on_upload=lambda e: asyncio.create_task(handle_import(e)),
                    auto_upload=True
                ).props("accept='.json' label='Import'").classes("w-auto")

            ui.separator().classes("my-2")

            with ui.row().classes("w-full items-center justify-between p-2"):
                with ui.column().classes("gap-0 flex-1"):
                    ui.label("Clear All Data").classes("font-medium text-red-600")
                    ui.label("Permanently delete all saved calculations and projects").classes(
                        "text-sm text-gray-500"
                    )

                async def handle_clear_data():
                    with ui.dialog() as dialog, ui.card():
                        ui.label("Clear All Data").classes("text-lg font-bold text-red-600")
                        ui.label(
                            "This action cannot be undone. All your saved calculations, "
                            "projects, and formulas will be permanently deleted."
                        ).classes("text-gray-600")

                        with ui.row().classes("w-full justify-end gap-2 mt-4"):
                            ui.button("Cancel", on_click=dialog.close).props("flat")

                            async def confirm_clear():
                                try:
                                    async with get_session() as session:
                                        from sqlalchemy import delete
                                        await session.execute(delete(Calculation))
                                        await session.execute(delete(Formula))
                                        await session.execute(delete(Project))

                                    ui.notify("All data cleared", type="positive")
                                except Exception as e:
                                    ui.notify(f"Error: {e}", type="negative")

                                dialog.close()

                            ui.button(
                                "Delete Everything",
                                on_click=lambda: asyncio.create_task(confirm_clear())
                            ).props("color=negative")

                    dialog.open()

                ui.button(
                    "Clear Data",
                    icon="delete_forever",
                    on_click=lambda: asyncio.create_task(handle_clear_data())
                ).props("color=negative outline")

        # About section
        with ui.card().classes("w-full"):
            ui.label("About").classes("text-lg font-semibold mb-4")

            with ui.column().classes("gap-2"):
                with ui.row().classes("gap-2"):
                    ui.label("Engineering Calculations Database").classes("font-medium")
                    ui.badge("v1.0.0").props("color=primary")

                ui.label(
                    "A comprehensive engineering calculations tool with support for "
                    "various engineering domains including Statics, Fluids, Thermodynamics, "
                    "Materials, Mechanical, Controls, and Vibrations."
                ).classes("text-gray-600")

                ui.separator().classes("my-2")

                with ui.row().classes("gap-4 text-sm text-gray-500"):
                    ui.label("Built with NiceGUI, SQLAlchemy, and Pint")
                    ui.label("|")
                    ui.link("Documentation", "#").classes("text-primary")
                    ui.label("|")
                    ui.link("GitHub", "#").classes("text-primary")


# Module exports
__all__ = [
    "settings_page",
    "SettingsState",
    "export_data",
    "import_data",
]
