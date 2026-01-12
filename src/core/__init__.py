"""
Core module for Engineering Calculations Database.

This module provides the foundational components for engineering calculations:
- Unit conversion and quantity handling (units.py)
- Input validation framework (validation.py)
- Base calculation framework (calculations.py)
"""

from .calculations import (
    Calculation,
    CalculationRegistry,
    CalculationResult,
    Parameter,
    create_calculation,
    get_default_registry,
    register,
)
from .units import (
    DimensionalityError,
    Quantity,
    UndefinedUnitError,
    Units,
    convert,
    create_quantity,
    get_base_units,
    get_registry,
    is_compatible,
    list_compatible_units,
)
from .validation import (
    CompositeValidator,
    DimensionValidator,
    NonNegativeValidator,
    NonZeroValidator,
    OptionalValidator,
    PositiveValidator,
    RangeValidator,
    TypeValidator,
    ValidationError,
    Validator,
    validate,
    validate_non_negative,
    validate_non_zero,
    validate_positive,
    validate_range,
    validate_unit_dimension,
)

__all__ = [
    # Calculations
    "Calculation",
    "CalculationRegistry",
    "CalculationResult",
    "Parameter",
    "create_calculation",
    "get_default_registry",
    "register",
    # Units
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
    # Validation
    "ValidationError",
    "Validator",
    "PositiveValidator",
    "NonNegativeValidator",
    "RangeValidator",
    "NonZeroValidator",
    "DimensionValidator",
    "CompositeValidator",
    "OptionalValidator",
    "TypeValidator",
    "validate",
    "validate_positive",
    "validate_non_negative",
    "validate_non_zero",
    "validate_range",
    "validate_unit_dimension",
]
