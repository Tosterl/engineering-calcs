"""
Reusable input components for Engineering Calculations Database UI.

This module provides NiceGUI components for engineering input including
quantity inputs with unit selection, material selectors, and parameter groups.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from nicegui import ui

from src.core.calculations import Parameter
from src.core.units import Quantity, list_compatible_units


class QuantityInput:
    """
    Custom component for entering values with engineering units.

    Combines a number input field with a unit selector dropdown that
    shows compatible units based on the default unit's dimensionality.

    Attributes:
        label: Display label for the input.
        default_unit: The default/initial unit string.
        value: Current numeric value.
        on_change: Callback function when value or unit changes.
    """

    def __init__(
        self,
        label: str,
        default_unit: str,
        value: Optional[float] = None,
        on_change: Optional[Callable[[Quantity], None]] = None,
    ) -> None:
        """
        Initialize a QuantityInput component.

        Args:
            label: Display label for the input field.
            default_unit: Initial unit string (e.g., 'meter', 'psi', 'kN').
            value: Initial numeric value (default: None).
            on_change: Callback invoked when value or unit changes.
                       Receives the new Quantity object.
        """
        self.label = label
        self.default_unit = default_unit
        self._value: Optional[float] = value
        self._unit: str = default_unit
        self._on_change = on_change
        self._compatible_units: List[str] = list_compatible_units(default_unit)

        # Ensure default unit is in compatible units list
        if self._compatible_units and default_unit not in self._compatible_units:
            self._compatible_units.insert(0, default_unit)
        elif not self._compatible_units:
            self._compatible_units = [default_unit]

        # UI element references
        self._number_input: Optional[ui.number] = None
        self._unit_select: Optional[ui.select] = None
        self._container: Optional[ui.row] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.row().classes("items-end gap-2") as container:
            self._container = container

            # Number input field
            self._number_input = ui.number(
                label=self.label,
                value=self._value,
                on_change=self._handle_value_change,
            ).classes("w-32")

            # Unit selector dropdown
            self._unit_select = ui.select(
                options=self._compatible_units,
                value=self._unit,
                on_change=self._handle_unit_change,
            ).classes("w-28").props("dense")

    def _handle_value_change(self, event: Any) -> None:
        """Handle changes to the numeric value."""
        self._value = event.value
        self._notify_change()

    def _handle_unit_change(self, event: Any) -> None:
        """Handle changes to the selected unit."""
        self._unit = event.value
        self._notify_change()

    def _notify_change(self) -> None:
        """Notify the callback of value/unit changes."""
        if self._on_change and self._value is not None:
            try:
                quantity = Quantity(self._value, self._unit)
                self._on_change(quantity)
            except Exception:
                # Invalid quantity, don't notify
                pass

    @property
    def value(self) -> Optional[float]:
        """Get the current numeric value."""
        return self._value

    @value.setter
    def value(self, new_value: Optional[float]) -> None:
        """Set the numeric value."""
        self._value = new_value
        if self._number_input:
            self._number_input.value = new_value
        self._notify_change()

    @property
    def unit(self) -> str:
        """Get the currently selected unit."""
        return self._unit

    @unit.setter
    def unit(self, new_unit: str) -> None:
        """Set the selected unit."""
        self._unit = new_unit
        if self._unit_select and new_unit in self._compatible_units:
            self._unit_select.value = new_unit
        self._notify_change()

    def get_quantity(self) -> Optional[Quantity]:
        """
        Get the current value as a Quantity object.

        Returns:
            Quantity object if value is valid, None otherwise.
        """
        if self._value is not None:
            try:
                return Quantity(self._value, self._unit)
            except Exception:
                return None
        return None

    def set_quantity(self, quantity: Quantity) -> None:
        """
        Set the input from a Quantity object.

        Args:
            quantity: Quantity object to set value and unit from.
        """
        self._value = quantity.magnitude
        target_unit = quantity.unit_string

        # If the unit is compatible, use it; otherwise convert
        if target_unit in self._compatible_units:
            self._unit = target_unit
        else:
            # Try to find a compatible unit and convert
            if self._compatible_units:
                self._unit = self._compatible_units[0]
                try:
                    converted = quantity.to(self._unit)
                    self._value = converted.magnitude
                except Exception:
                    pass

        # Update UI elements
        if self._number_input:
            self._number_input.value = self._value
        if self._unit_select:
            self._unit_select.value = self._unit

    def set_error(self, message: Optional[str] = None) -> None:
        """
        Set or clear an error state on the input.

        Args:
            message: Error message to display, or None to clear.
        """
        if self._number_input:
            if message:
                self._number_input.props(f'error error-message="{message}"')
            else:
                self._number_input.props(remove="error error-message")

    def disable(self, disabled: bool = True) -> None:
        """
        Enable or disable the input.

        Args:
            disabled: True to disable, False to enable.
        """
        if self._number_input:
            self._number_input.disable() if disabled else self._number_input.enable()
        if self._unit_select:
            self._unit_select.disable() if disabled else self._unit_select.enable()


class MaterialSelector:
    """
    Dropdown component for selecting materials from a database.

    Shows material properties when a material is selected.

    Attributes:
        label: Display label for the selector.
        on_change: Callback when selection changes.
    """

    # Default materials with common engineering properties
    # In production, this would be loaded from the database
    DEFAULT_MATERIALS: Dict[str, Dict[str, Any]] = {
        "Steel (ASTM A36)": {
            "category": "Steel",
            "density": {"value": 7850, "unit": "kg/m**3"},
            "yield_strength": {"value": 250, "unit": "MPa"},
            "tensile_strength": {"value": 400, "unit": "MPa"},
            "elastic_modulus": {"value": 200, "unit": "GPa"},
            "poissons_ratio": 0.26,
        },
        "Steel (ASTM A992)": {
            "category": "Steel",
            "density": {"value": 7850, "unit": "kg/m**3"},
            "yield_strength": {"value": 345, "unit": "MPa"},
            "tensile_strength": {"value": 450, "unit": "MPa"},
            "elastic_modulus": {"value": 200, "unit": "GPa"},
            "poissons_ratio": 0.26,
        },
        "Aluminum 6061-T6": {
            "category": "Aluminum",
            "density": {"value": 2700, "unit": "kg/m**3"},
            "yield_strength": {"value": 276, "unit": "MPa"},
            "tensile_strength": {"value": 310, "unit": "MPa"},
            "elastic_modulus": {"value": 68.9, "unit": "GPa"},
            "poissons_ratio": 0.33,
        },
        "Stainless Steel 304": {
            "category": "Stainless Steel",
            "density": {"value": 8000, "unit": "kg/m**3"},
            "yield_strength": {"value": 215, "unit": "MPa"},
            "tensile_strength": {"value": 505, "unit": "MPa"},
            "elastic_modulus": {"value": 193, "unit": "GPa"},
            "poissons_ratio": 0.29,
        },
        "Concrete (f'c = 28 MPa)": {
            "category": "Concrete",
            "density": {"value": 2400, "unit": "kg/m**3"},
            "compressive_strength": {"value": 28, "unit": "MPa"},
            "elastic_modulus": {"value": 25, "unit": "GPa"},
            "poissons_ratio": 0.20,
        },
        "Copper (Annealed)": {
            "category": "Copper",
            "density": {"value": 8960, "unit": "kg/m**3"},
            "yield_strength": {"value": 70, "unit": "MPa"},
            "tensile_strength": {"value": 220, "unit": "MPa"},
            "elastic_modulus": {"value": 110, "unit": "GPa"},
            "poissons_ratio": 0.34,
        },
        "Titanium (Grade 5)": {
            "category": "Titanium",
            "density": {"value": 4430, "unit": "kg/m**3"},
            "yield_strength": {"value": 880, "unit": "MPa"},
            "tensile_strength": {"value": 950, "unit": "MPa"},
            "elastic_modulus": {"value": 114, "unit": "GPa"},
            "poissons_ratio": 0.34,
        },
    }

    def __init__(
        self,
        label: str = "Material",
        on_change: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        materials: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize a MaterialSelector component.

        Args:
            label: Display label for the selector.
            on_change: Callback invoked when selection changes.
                       Receives (material_name, properties_dict).
            materials: Optional custom materials dictionary.
                       Uses DEFAULT_MATERIALS if not provided.
        """
        self.label = label
        self._on_change = on_change
        self._materials = materials or self.DEFAULT_MATERIALS
        self._selected: Optional[str] = None
        self._properties: Dict[str, Any] = {}

        # UI element references
        self._select: Optional[ui.select] = None
        self._properties_card: Optional[ui.card] = None
        self._properties_container: Optional[ui.column] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.column().classes("gap-2 w-full"):
            # Material selector dropdown
            self._select = ui.select(
                options=list(self._materials.keys()),
                label=self.label,
                on_change=self._handle_selection_change,
                with_input=True,
            ).classes("w-full")

            # Properties display card (hidden initially)
            with ui.card().classes("w-full").bind_visibility_from(
                self, "_selected", backward=lambda x: x is not None
            ) as card:
                self._properties_card = card
                ui.label("Material Properties").classes("text-subtitle1 font-medium")
                self._properties_container = ui.column().classes("gap-1")

    def _handle_selection_change(self, event: Any) -> None:
        """Handle material selection changes."""
        material_name = event.value
        self._selected = material_name
        self._properties = self._materials.get(material_name, {})

        # Update properties display
        self._update_properties_display()

        # Notify callback
        if self._on_change and material_name:
            self._on_change(material_name, self._properties)

    def _update_properties_display(self) -> None:
        """Update the properties card display."""
        if not self._properties_container:
            return

        self._properties_container.clear()

        with self._properties_container:
            for prop_name, prop_value in self._properties.items():
                if prop_name == "category":
                    continue

                # Format property name for display
                display_name = prop_name.replace("_", " ").title()

                # Format value with unit if applicable
                if isinstance(prop_value, dict) and "value" in prop_value:
                    value_str = f"{prop_value['value']} {prop_value.get('unit', '')}"
                else:
                    value_str = str(prop_value)

                with ui.row().classes("justify-between w-full"):
                    ui.label(f"{display_name}:").classes("text-gray-600")
                    ui.label(value_str).classes("font-medium")

    @property
    def selected_material(self) -> Optional[str]:
        """Get the currently selected material name."""
        return self._selected

    @property
    def properties(self) -> Dict[str, Any]:
        """Get the properties of the selected material."""
        return self._properties

    def get_property(self, property_name: str) -> Optional[Any]:
        """
        Get a specific property value.

        Args:
            property_name: Name of the property to retrieve.

        Returns:
            Property value, or None if not found.
        """
        return self._properties.get(property_name)

    def get_property_as_quantity(self, property_name: str) -> Optional[Quantity]:
        """
        Get a property value as a Quantity object.

        Args:
            property_name: Name of the property to retrieve.

        Returns:
            Quantity object if the property has value and unit, None otherwise.
        """
        prop = self._properties.get(property_name)
        if isinstance(prop, dict) and "value" in prop and "unit" in prop:
            try:
                return Quantity(prop["value"], prop["unit"])
            except Exception:
                return None
        return None

    def set_selection(self, material_name: str) -> None:
        """
        Set the selected material programmatically.

        Args:
            material_name: Name of the material to select.
        """
        if material_name in self._materials:
            self._selected = material_name
            self._properties = self._materials[material_name]
            if self._select:
                self._select.value = material_name
            self._update_properties_display()

    def add_material(self, name: str, properties: Dict[str, Any]) -> None:
        """
        Add a material to the selector options.

        Args:
            name: Material name.
            properties: Dictionary of material properties.
        """
        self._materials[name] = properties
        if self._select:
            self._select.options = list(self._materials.keys())

    def disable(self, disabled: bool = True) -> None:
        """
        Enable or disable the selector.

        Args:
            disabled: True to disable, False to enable.
        """
        if self._select:
            self._select.disable() if disabled else self._select.enable()


class ParameterGroup:
    """
    Container component for grouping related inputs in a card.

    Manages multiple QuantityInputs based on Parameter definitions.

    Attributes:
        title: Card title.
        parameters: List of Parameter objects defining inputs.
    """

    def __init__(
        self,
        title: str,
        parameters: List[Parameter],
        on_change: Optional[Callable[[Dict[str, Quantity]], None]] = None,
    ) -> None:
        """
        Initialize a ParameterGroup component.

        Args:
            title: Title displayed on the card.
            parameters: List of Parameter objects defining the inputs.
            on_change: Callback invoked when any input changes.
                       Receives a dict mapping parameter names to Quantities.
        """
        self.title = title
        self._parameters = parameters
        self._on_change = on_change
        self._inputs: Dict[str, QuantityInput] = {}
        self._card: Optional[ui.card] = None

        # Build the component
        self._build()

    def _build(self) -> None:
        """Build the component UI elements."""
        with ui.card().classes("w-full") as card:
            self._card = card

            # Card header with title
            ui.label(self.title).classes("text-h6 font-medium mb-4")

            # Create inputs for each parameter
            with ui.column().classes("gap-4 w-full"):
                for param in self._parameters:
                    quantity_input = QuantityInput(
                        label=param.description or param.name,
                        default_unit=param.unit,
                        value=param.default,
                        on_change=lambda q, name=param.name: self._handle_input_change(
                            name, q
                        ),
                    )
                    self._inputs[param.name] = quantity_input

    def _handle_input_change(self, param_name: str, quantity: Quantity) -> None:
        """Handle changes to individual inputs."""
        if self._on_change:
            # Collect all current values
            values = self.get_values()
            self._on_change(values)

    def get_values(self) -> Dict[str, Optional[Quantity]]:
        """
        Get all current input values as Quantity objects.

        Returns:
            Dictionary mapping parameter names to Quantity objects.
        """
        return {
            name: inp.get_quantity()
            for name, inp in self._inputs.items()
        }

    def set_values(self, values: Dict[str, Quantity]) -> None:
        """
        Set input values from a dictionary.

        Args:
            values: Dictionary mapping parameter names to Quantity objects.
        """
        for name, quantity in values.items():
            if name in self._inputs:
                self._inputs[name].set_quantity(quantity)

    def get_input(self, param_name: str) -> Optional[QuantityInput]:
        """
        Get a specific QuantityInput by parameter name.

        Args:
            param_name: Name of the parameter.

        Returns:
            QuantityInput component, or None if not found.
        """
        return self._inputs.get(param_name)

    def validate(self) -> Dict[str, Optional[str]]:
        """
        Validate all inputs.

        Returns:
            Dictionary mapping parameter names to error messages.
            Empty dict if all valid.
        """
        errors: Dict[str, Optional[str]] = {}
        for name, inp in self._inputs.items():
            if inp.value is None:
                errors[name] = "Value required"
                inp.set_error("Value required")
            else:
                inp.set_error(None)
        return {k: v for k, v in errors.items() if v is not None}

    def clear_errors(self) -> None:
        """Clear all error states from inputs."""
        for inp in self._inputs.values():
            inp.set_error(None)

    def reset(self) -> None:
        """Reset all inputs to their default values."""
        for param in self._parameters:
            if param.name in self._inputs:
                self._inputs[param.name].value = param.default

    def disable(self, disabled: bool = True) -> None:
        """
        Enable or disable all inputs.

        Args:
            disabled: True to disable, False to enable.
        """
        for inp in self._inputs.values():
            inp.disable(disabled)


# Module exports
__all__ = [
    "QuantityInput",
    "MaterialSelector",
    "ParameterGroup",
]
