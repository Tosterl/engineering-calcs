"""
Unit conversion system for Engineering Calculations Database.

This module provides a comprehensive unit conversion system built on Pint,
with custom engineering unit definitions and helper utilities.
"""

from __future__ import annotations

from functools import total_ordering
from typing import Any, Optional, Union

import pint
from pint import DimensionalityError, UndefinedUnitError


# Initialize the unit registry with default units
_ureg = pint.UnitRegistry()

# Add custom engineering unit definitions
_ureg.define("ksi = 1000 * psi")  # kilopounds per square inch
_ureg.define("ksf = 1000 * pound_force / foot ** 2")  # kilopounds per square foot
_ureg.define("pcf = pound / foot ** 3")  # pounds per cubic foot
_ureg.define("plf = pound_force / foot")  # pounds per linear foot
_ureg.define("klf = 1000 * pound_force / foot")  # kips per linear foot
_ureg.define("kip = 1000 * pound_force")  # kilopound force


def get_registry() -> pint.UnitRegistry:
    """
    Get the shared unit registry instance.

    Returns:
        pint.UnitRegistry: The configured unit registry with custom definitions.
    """
    return _ureg


@total_ordering
class Quantity:
    """
    A wrapper class for Pint quantities with enhanced functionality.

    This class provides unit validation, conversion methods, formatted output,
    and arithmetic operations that preserve units.

    Attributes:
        _quantity: The underlying Pint Quantity object.
        _precision: Default precision for string formatting.
    """

    def __init__(
        self,
        value: Union[float, int, pint.Quantity],
        unit: Optional[str] = None,
        precision: int = 4,
    ) -> None:
        """
        Initialize a Quantity with a value and unit.

        Args:
            value: Numeric value or existing Pint Quantity.
            unit: Unit string (e.g., 'meter', 'psi', 'ksi'). Required if value is numeric.
            precision: Default decimal precision for string output.

        Raises:
            ValueError: If unit is not provided for numeric values.
            UndefinedUnitError: If the unit is not recognized.
        """
        self._precision = precision

        if isinstance(value, pint.Quantity):
            self._quantity = value
        elif unit is None:
            raise ValueError("Unit must be provided for numeric values.")
        else:
            try:
                self._quantity = value * _ureg(unit)
            except UndefinedUnitError as e:
                raise UndefinedUnitError(f"Undefined unit: {unit}") from e

    @property
    def magnitude(self) -> float:
        """Get the numeric magnitude of the quantity."""
        return float(self._quantity.magnitude)

    @property
    def units(self) -> pint.Unit:
        """Get the units of the quantity."""
        return self._quantity.units

    @property
    def unit_string(self) -> str:
        """Get the unit as a string."""
        return str(self._quantity.units)

    @property
    def dimensionality(self) -> str:
        """Get the dimensionality of the quantity."""
        return str(self._quantity.dimensionality)

    @property
    def precision(self) -> int:
        """Get the default precision for string formatting."""
        return self._precision

    @precision.setter
    def precision(self, value: int) -> None:
        """Set the default precision for string formatting."""
        if value < 0:
            raise ValueError("Precision must be non-negative.")
        self._precision = value

    def to(self, target_unit: str) -> Quantity:
        """
        Convert the quantity to a different unit.

        Args:
            target_unit: The target unit string to convert to.

        Returns:
            Quantity: A new Quantity in the target units.

        Raises:
            DimensionalityError: If units are incompatible.
            UndefinedUnitError: If the target unit is not recognized.
        """
        try:
            converted = self._quantity.to(target_unit)
            return Quantity(converted, precision=self._precision)
        except DimensionalityError as e:
            raise DimensionalityError(
                self._quantity.units,
                _ureg(target_unit).units,
                extra_msg=f"Cannot convert from {self.unit_string} to {target_unit}",
            ) from e
        except UndefinedUnitError as e:
            raise UndefinedUnitError(f"Undefined unit: {target_unit}") from e

    def to_base_units(self) -> Quantity:
        """
        Convert the quantity to SI base units.

        Returns:
            Quantity: A new Quantity in base units.
        """
        return Quantity(self._quantity.to_base_units(), precision=self._precision)

    def is_compatible_with(self, other: Union[Quantity, str]) -> bool:
        """
        Check if this quantity is dimensionally compatible with another.

        Args:
            other: Another Quantity or unit string to compare.

        Returns:
            bool: True if units are compatible, False otherwise.
        """
        if isinstance(other, Quantity):
            return self._quantity.is_compatible_with(other._quantity)
        try:
            return self._quantity.is_compatible_with(_ureg(other))
        except UndefinedUnitError:
            return False

    def format(self, precision: Optional[int] = None, unit_format: str = "~P") -> str:
        """
        Format the quantity as a string with configurable precision.

        Args:
            precision: Number of decimal places. Uses default if None.
            unit_format: Pint unit format specifier.
                - "~P" for short pretty format (default)
                - "~" for short format
                - "P" for pretty format
                - "" for default format

        Returns:
            str: Formatted quantity string.
        """
        prec = precision if precision is not None else self._precision
        return f"{self.magnitude:.{prec}f} {self._quantity.units:{unit_format}}"

    def __str__(self) -> str:
        """Return a formatted string representation."""
        return self.format()

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"Quantity({self.magnitude}, '{self.unit_string}', precision={self._precision})"

    def __float__(self) -> float:
        """Return the magnitude as a float."""
        return float(self.magnitude)

    def __int__(self) -> int:
        """Return the magnitude as an integer."""
        return int(self.magnitude)

    # Arithmetic operations
    def __add__(self, other: Union[Quantity, pint.Quantity]) -> Quantity:
        """Add two quantities with compatible units."""
        if isinstance(other, Quantity):
            result = self._quantity + other._quantity
        else:
            result = self._quantity + other
        return Quantity(result, precision=self._precision)

    def __radd__(self, other: Union[Quantity, pint.Quantity]) -> Quantity:
        """Right addition."""
        return self.__add__(other)

    def __sub__(self, other: Union[Quantity, pint.Quantity]) -> Quantity:
        """Subtract two quantities with compatible units."""
        if isinstance(other, Quantity):
            result = self._quantity - other._quantity
        else:
            result = self._quantity - other
        return Quantity(result, precision=self._precision)

    def __rsub__(self, other: Union[Quantity, pint.Quantity]) -> Quantity:
        """Right subtraction."""
        if isinstance(other, Quantity):
            result = other._quantity - self._quantity
        else:
            result = other - self._quantity
        return Quantity(result, precision=self._precision)

    def __mul__(self, other: Union[Quantity, pint.Quantity, float, int]) -> Quantity:
        """Multiply quantity by another quantity or scalar."""
        if isinstance(other, Quantity):
            result = self._quantity * other._quantity
        else:
            result = self._quantity * other
        return Quantity(result, precision=self._precision)

    def __rmul__(self, other: Union[Quantity, pint.Quantity, float, int]) -> Quantity:
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: Union[Quantity, pint.Quantity, float, int]) -> Quantity:
        """Divide quantity by another quantity or scalar."""
        if isinstance(other, Quantity):
            result = self._quantity / other._quantity
        else:
            result = self._quantity / other
        return Quantity(result, precision=self._precision)

    def __rtruediv__(self, other: Union[Quantity, pint.Quantity, float, int]) -> Quantity:
        """Right division."""
        if isinstance(other, Quantity):
            result = other._quantity / self._quantity
        else:
            result = other / self._quantity
        return Quantity(result, precision=self._precision)

    def __pow__(self, exponent: Union[int, float]) -> Quantity:
        """Raise quantity to a power."""
        result = self._quantity**exponent
        return Quantity(result, precision=self._precision)

    def __neg__(self) -> Quantity:
        """Negate the quantity."""
        return Quantity(-self._quantity, precision=self._precision)

    def __pos__(self) -> Quantity:
        """Return positive quantity."""
        return Quantity(+self._quantity, precision=self._precision)

    def __abs__(self) -> Quantity:
        """Return absolute value of quantity."""
        return Quantity(abs(self._quantity), precision=self._precision)

    # Comparison operations
    def __eq__(self, other: Any) -> bool:
        """Check equality with another quantity."""
        if isinstance(other, Quantity):
            return self._quantity == other._quantity
        if isinstance(other, pint.Quantity):
            return self._quantity == other
        return False

    def __lt__(self, other: Union[Quantity, pint.Quantity]) -> bool:
        """Less than comparison."""
        if isinstance(other, Quantity):
            return self._quantity < other._quantity
        return self._quantity < other

    def __hash__(self) -> int:
        """Return hash of the quantity."""
        return hash((self.magnitude, str(self.units)))


# Helper functions
def convert(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a numeric value from one unit to another.

    Args:
        value: The numeric value to convert.
        from_unit: The source unit string.
        to_unit: The target unit string.

    Returns:
        float: The converted numeric value.

    Raises:
        DimensionalityError: If units are incompatible.
        UndefinedUnitError: If either unit is not recognized.

    Example:
        >>> convert(1.0, 'ksi', 'psi')
        1000.0
        >>> convert(144, 'inch**2', 'foot**2')
        1.0
    """
    try:
        quantity = value * _ureg(from_unit)
        converted = quantity.to(to_unit)
        return float(converted.magnitude)
    except UndefinedUnitError as e:
        raise UndefinedUnitError(f"Undefined unit in conversion: {e}") from e
    except DimensionalityError as e:
        raise DimensionalityError(
            _ureg(from_unit).units,
            _ureg(to_unit).units,
            extra_msg=f"Cannot convert from {from_unit} to {to_unit}",
        ) from e


def create_quantity(value: float, unit: str, precision: int = 4) -> Quantity:
    """
    Create a Quantity object with the given value and unit.

    Args:
        value: The numeric value.
        unit: The unit string (e.g., 'meter', 'psi', 'ksi').
        precision: Default precision for string formatting.

    Returns:
        Quantity: A new Quantity object.

    Example:
        >>> q = create_quantity(50, 'ksi')
        >>> str(q)
        '50.0000 ksi'
    """
    return Quantity(value, unit, precision=precision)


def is_compatible(unit1: str, unit2: str) -> bool:
    """
    Check if two units are dimensionally compatible.

    Args:
        unit1: First unit string.
        unit2: Second unit string.

    Returns:
        bool: True if units are compatible (same dimensionality), False otherwise.

    Example:
        >>> is_compatible('ksi', 'MPa')
        True
        >>> is_compatible('meter', 'second')
        False
    """
    try:
        q1 = _ureg(unit1)
        q2 = _ureg(unit2)
        return q1.is_compatible_with(q2)
    except UndefinedUnitError:
        return False


def get_base_units(unit: str) -> str:
    """
    Get the SI base unit representation of a unit.

    Args:
        unit: The unit string to analyze.

    Returns:
        str: The equivalent SI base units.

    Example:
        >>> get_base_units('ksi')
        'kilogram / meter / second ** 2'
        >>> get_base_units('pcf')
        'kilogram / meter ** 3'
    """
    try:
        quantity = 1 * _ureg(unit)
        base = quantity.to_base_units()
        return str(base.units)
    except UndefinedUnitError as e:
        raise UndefinedUnitError(f"Undefined unit: {unit}") from e


def list_compatible_units(unit: str) -> list[str]:
    """
    Get a list of common units compatible with the given unit.

    Args:
        unit: The unit string to find compatible units for.

    Returns:
        list[str]: List of compatible unit names.
    """
    try:
        q = _ureg(unit)
        dimensionality = q.dimensionality

        # Common engineering units by dimensionality
        common_units: dict[str, list[str]] = {
            "[length]": ["meter", "foot", "inch", "millimeter", "centimeter", "yard", "mile"],
            "[mass]": ["kilogram", "gram", "pound", "ton", "tonne"],
            "[time]": ["second", "minute", "hour", "day"],
            "[length] ** 2": ["meter**2", "foot**2", "inch**2", "centimeter**2"],
            "[length] ** 3": ["meter**3", "foot**3", "inch**3", "gallon", "liter"],
            "[mass] / [length] ** 3": ["kilogram/meter**3", "pcf", "gram/centimeter**3"],
            "[mass] / [length] / [time] ** 2": ["pascal", "psi", "ksi", "MPa", "GPa", "bar", "ksf"],
            "[length] * [mass] / [time] ** 2": ["newton", "pound_force", "kip", "kilonewton"],
            "[mass] / [time] ** 2": ["plf", "klf", "newton/meter", "kilonewton/meter"],
        }

        dim_str = str(dimensionality)
        return common_units.get(dim_str, [])
    except UndefinedUnitError:
        return []


# Common unit aliases for convenience
class Units:
    """
    Namespace for commonly used engineering units.

    This class provides convenient access to unit objects without
    needing to use string parsing.
    """

    # Length
    meter = _ureg.meter
    foot = _ureg.foot
    inch = _ureg.inch
    millimeter = _ureg.millimeter
    centimeter = _ureg.centimeter

    # Area
    meter2 = _ureg.meter**2
    foot2 = _ureg.foot**2
    inch2 = _ureg.inch**2

    # Volume
    meter3 = _ureg.meter**3
    foot3 = _ureg.foot**3
    inch3 = _ureg.inch**3
    gallon = _ureg.gallon
    liter = _ureg.liter

    # Mass
    kilogram = _ureg.kilogram
    gram = _ureg.gram
    pound = _ureg.pound

    # Force
    newton = _ureg.newton
    kilonewton = _ureg.kilonewton
    pound_force = _ureg.pound_force
    kip = _ureg.kip

    # Pressure/Stress
    pascal = _ureg.pascal
    kilopascal = _ureg.kilopascal
    megapascal = _ureg.megapascal
    gigapascal = _ureg.gigapascal
    psi = _ureg.psi
    ksi = _ureg.ksi
    ksf = _ureg.ksf
    bar = _ureg.bar

    # Density
    pcf = _ureg.pcf

    # Linear load
    plf = _ureg.plf
    klf = _ureg.klf

    # Time
    second = _ureg.second
    minute = _ureg.minute
    hour = _ureg.hour


# Export commonly used exceptions for convenience
__all__ = [
    "Quantity",
    "Units",
    "get_registry",
    "convert",
    "create_quantity",
    "is_compatible",
    "get_base_units",
    "list_compatible_units",
    "DimensionalityError",
    "UndefinedUnitError",
]
