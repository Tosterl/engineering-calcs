"""
Reusable output components for Engineering Calculations Database UI.

This module provides NiceGUI components for displaying calculation results
including result cards, tables, and formula rendering with LaTeX support.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from nicegui import ui

from src.core.units import Quantity


class ResultStatus(Enum):
    """Status indicators for result values."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class ResultCard:
    """
    Component for displaying a single calculation result.

    Shows a value with unit, label/description, and optional status icon.

    Attributes:
        label: Description label for the result.
        value: The result value (Quantity or numeric).
        unit: Unit string (optional if value is Quantity).
        status: Optional status indicator.
    """

    # Status configuration for icons and colors
    STATUS_CONFIG: Dict[ResultStatus, Dict[str, str]] = {
        ResultStatus.OK: {
            "icon": "check_circle",
            "color": "text-green-600",
            "bg": "bg-green-50",
        },
        ResultStatus.WARNING: {
            "icon": "warning",
            "color": "text-amber-600",
            "bg": "bg-amber-50",
        },
        ResultStatus.ERROR: {
            "icon": "error",
            "color": "text-red-600",
            "bg": "bg-red-50",
        },
        ResultStatus.INFO: {
            "icon": "info",
            "color": "text-blue-600",
            "bg": "bg-blue-50",
        },
    }

    def __init__(
        self,
        label: str,
        value: Union[Quantity, float, int, str],
        unit: Optional[str] = None,
        status: Optional[ResultStatus] = None,
        precision: int = 4,
        description: Optional[str] = None,
    ) -> None:
        """
        Initialize a ResultCard component.

        Args:
            label: Display label for the result.
            value: Result value (Quantity, numeric, or string).
            unit: Unit string (used only if value is not a Quantity).
            status: Optional status indicator (OK, WARNING, ERROR, INFO).
            precision: Decimal precision for numeric display.
            description: Optional additional description text.
        """
        self.label = label
        self._value = value
        self._unit = unit
        self._status = status
        self._precision = precision
        self._description = description

        # UI element references
        self._card: Optional[ui.card] = None
        self._value_label: Optional[ui.label] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        # Determine background color based on status
        bg_class = ""
        if self._status and self._status in self.STATUS_CONFIG:
            bg_class = self.STATUS_CONFIG[self._status]["bg"]

        with ui.card().classes(f"w-full {bg_class}") as card:
            self._card = card

            with ui.row().classes("items-center justify-between w-full"):
                # Label and value section
                with ui.column().classes("gap-1"):
                    ui.label(self.label).classes("text-subtitle2 text-gray-600")

                    with ui.row().classes("items-baseline gap-2"):
                        value_str = self._format_value()
                        self._value_label = ui.label(value_str).classes(
                            "text-h5 font-bold"
                        )

                        unit_str = self._get_unit_string()
                        if unit_str:
                            ui.label(unit_str).classes("text-subtitle1 text-gray-500")

                    if self._description:
                        ui.label(self._description).classes(
                            "text-caption text-gray-500"
                        )

                # Status icon
                if self._status and self._status in self.STATUS_CONFIG:
                    config = self.STATUS_CONFIG[self._status]
                    ui.icon(config["icon"]).classes(f"text-3xl {config['color']}")

    def _format_value(self) -> str:
        """Format the value for display."""
        if isinstance(self._value, Quantity):
            return f"{self._value.magnitude:.{self._precision}g}"
        elif isinstance(self._value, (int, float)):
            return f"{self._value:.{self._precision}g}"
        return str(self._value)

    def _get_unit_string(self) -> str:
        """Get the unit string for display."""
        if isinstance(self._value, Quantity):
            return self._value.unit_string
        return self._unit or ""

    @property
    def value(self) -> Union[Quantity, float, int, str]:
        """Get the current value."""
        return self._value

    @value.setter
    def value(self, new_value: Union[Quantity, float, int, str]) -> None:
        """Set a new value and update display."""
        self._value = new_value
        if self._value_label:
            self._value_label.text = self._format_value()

    @property
    def status(self) -> Optional[ResultStatus]:
        """Get the current status."""
        return self._status

    def set_status(self, status: Optional[ResultStatus]) -> None:
        """
        Set a new status and rebuild the card.

        Args:
            status: New status indicator.
        """
        self._status = status
        # Rebuild is needed for status change as it affects styling
        if self._card:
            self._card.clear()
            self._build()


class ResultsTable:
    """
    Component for displaying multiple results in a table format.

    Shows results with Parameter, Value, and Unit columns.

    Attributes:
        results: List of result dictionaries or Quantities.
    """

    def __init__(
        self,
        results: Optional[List[Dict[str, Any]]] = None,
        title: Optional[str] = None,
        precision: int = 4,
    ) -> None:
        """
        Initialize a ResultsTable component.

        Args:
            results: List of result dictionaries with keys:
                     'name', 'value', 'unit' (or 'quantity' as Quantity object).
            title: Optional table title.
            precision: Decimal precision for numeric display.
        """
        self._results = results or []
        self._title = title
        self._precision = precision

        # UI element references
        self._container: Optional[ui.column] = None
        self._table: Optional[ui.table] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.column().classes("w-full") as container:
            self._container = container

            if self._title:
                ui.label(self._title).classes("text-h6 font-medium mb-2")

            # Define table columns
            columns = [
                {"name": "parameter", "label": "Parameter", "field": "parameter", "align": "left"},
                {"name": "value", "label": "Value", "field": "value", "align": "right"},
                {"name": "unit", "label": "Unit", "field": "unit", "align": "left"},
            ]

            # Format rows from results
            rows = self._format_rows()

            self._table = ui.table(
                columns=columns,
                rows=rows,
                row_key="parameter",
            ).classes("w-full")

    def _format_rows(self) -> List[Dict[str, str]]:
        """Format results into table rows."""
        rows = []
        for result in self._results:
            row = {}

            # Get parameter name
            row["parameter"] = result.get("name", result.get("parameter", "Unknown"))

            # Get value and unit
            if "quantity" in result and isinstance(result["quantity"], Quantity):
                quantity = result["quantity"]
                row["value"] = f"{quantity.magnitude:.{self._precision}g}"
                row["unit"] = quantity.unit_string
            else:
                value = result.get("value", "")
                if isinstance(value, (int, float)):
                    row["value"] = f"{value:.{self._precision}g}"
                else:
                    row["value"] = str(value)
                row["unit"] = result.get("unit", "")

            rows.append(row)

        return rows

    def set_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Update the table with new results.

        Args:
            results: New list of result dictionaries.
        """
        self._results = results
        if self._table:
            self._table.rows = self._format_rows()
            self._table.update()

    def add_result(
        self,
        name: str,
        value: Union[Quantity, float, int, str],
        unit: Optional[str] = None,
    ) -> None:
        """
        Add a single result to the table.

        Args:
            name: Parameter name.
            value: Result value.
            unit: Unit string (optional if value is Quantity).
        """
        if isinstance(value, Quantity):
            self._results.append({"name": name, "quantity": value})
        else:
            self._results.append({"name": name, "value": value, "unit": unit or ""})

        if self._table:
            self._table.rows = self._format_rows()
            self._table.update()

    def clear(self) -> None:
        """Clear all results from the table."""
        self._results = []
        if self._table:
            self._table.rows = []
            self._table.update()

    @classmethod
    def from_calculation_result(
        cls,
        outputs: Dict[str, Quantity],
        title: Optional[str] = None,
        precision: int = 4,
    ) -> ResultsTable:
        """
        Create a ResultsTable from calculation outputs.

        Args:
            outputs: Dictionary mapping output names to Quantity values.
            title: Optional table title.
            precision: Decimal precision for display.

        Returns:
            New ResultsTable instance.
        """
        results = [
            {"name": name.replace("_", " ").title(), "quantity": quantity}
            for name, quantity in outputs.items()
        ]
        return cls(results=results, title=title, precision=precision)


class FormulaDisplay:
    """
    Component for rendering LaTeX formulas using MathJax.

    Uses ui.html() to render LaTeX formulas with MathJax CDN.

    Attributes:
        latex_formula: LaTeX formula string to render.
    """

    # MathJax CDN script (loaded once per page)
    MATHJAX_SCRIPT = """
    <script>
        if (!window.MathJax) {
            window.MathJax = {
                tex: {
                    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
                },
                svg: {
                    fontCache: 'global'
                }
            };
        }
    </script>
    <script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
    </script>
    """

    _mathjax_loaded: bool = False

    def __init__(
        self,
        latex_formula: str,
        display_mode: bool = True,
        label: Optional[str] = None,
    ) -> None:
        """
        Initialize a FormulaDisplay component.

        Args:
            latex_formula: LaTeX formula string (without delimiters).
            display_mode: If True, render as display math (centered).
                         If False, render as inline math.
            label: Optional label to show above the formula.
        """
        self._formula = latex_formula
        self._display_mode = display_mode
        self._label = label

        # UI element references
        self._container: Optional[ui.column] = None
        self._formula_element: Optional[ui.html] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.column().classes("w-full") as container:
            self._container = container

            # Load MathJax if not already loaded
            if not FormulaDisplay._mathjax_loaded:
                ui.html(self.MATHJAX_SCRIPT)
                FormulaDisplay._mathjax_loaded = True

            # Optional label
            if self._label:
                ui.label(self._label).classes("text-subtitle2 text-gray-600 mb-2")

            # Render formula
            formula_html = self._render_formula()
            self._formula_element = ui.html(formula_html).classes(
                "text-center" if self._display_mode else ""
            )

    def _render_formula(self) -> str:
        """Render the LaTeX formula as HTML."""
        # Escape backslashes for HTML
        escaped_formula = self._formula.replace("\\", "\\\\")

        if self._display_mode:
            return f"""
            <div class="formula-display" style="font-size: 1.2em; padding: 1em 0;">
                \\[{escaped_formula}\\]
            </div>
            """
        else:
            return f"""
            <span class="formula-inline">
                \\({escaped_formula}\\)
            </span>
            """

    @property
    def formula(self) -> str:
        """Get the current LaTeX formula."""
        return self._formula

    @formula.setter
    def formula(self, new_formula: str) -> None:
        """Set a new formula and update display."""
        self._formula = new_formula
        if self._formula_element:
            self._formula_element.content = self._render_formula()
            # Trigger MathJax to re-render
            ui.run_javascript("if(window.MathJax){MathJax.typesetPromise();}")

    def set_formula(self, latex_formula: str) -> None:
        """
        Update the displayed formula.

        Args:
            latex_formula: New LaTeX formula string.
        """
        self.formula = latex_formula

    @classmethod
    def create_equation(
        cls,
        lhs: str,
        rhs: str,
        label: Optional[str] = None,
    ) -> FormulaDisplay:
        """
        Create a FormulaDisplay for an equation.

        Args:
            lhs: Left-hand side of the equation.
            rhs: Right-hand side of the equation.
            label: Optional label.

        Returns:
            New FormulaDisplay instance.
        """
        formula = f"{lhs} = {rhs}"
        return cls(latex_formula=formula, display_mode=True, label=label)


class FormulaCard:
    """
    Component combining a formula with its description and variables.

    Provides a complete formula display with context.
    """

    def __init__(
        self,
        title: str,
        latex_formula: str,
        description: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize a FormulaCard component.

        Args:
            title: Title of the formula (e.g., "Axial Stress").
            latex_formula: LaTeX formula string.
            description: Optional description of the formula.
            variables: Optional dict mapping variable symbols to descriptions.
        """
        self._title = title
        self._formula = latex_formula
        self._description = description
        self._variables = variables or {}

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.card().classes("w-full"):
            # Title
            ui.label(self._title).classes("text-h6 font-medium")

            # Description
            if self._description:
                ui.label(self._description).classes("text-body2 text-gray-600 mt-1")

            # Formula
            ui.separator().classes("my-3")
            FormulaDisplay(self._formula, display_mode=True)

            # Variables legend
            if self._variables:
                ui.separator().classes("my-3")
                ui.label("Where:").classes("text-subtitle2 font-medium")

                with ui.column().classes("gap-1 mt-2"):
                    for symbol, desc in self._variables.items():
                        with ui.row().classes("items-center gap-2"):
                            # Render variable symbol as inline math
                            ui.html(f"\\({symbol}\\)").classes("font-medium")
                            ui.label(f"= {desc}").classes("text-body2 text-gray-600")


# Module exports
__all__ = [
    "ResultStatus",
    "ResultCard",
    "ResultsTable",
    "FormulaDisplay",
    "FormulaCard",
]
