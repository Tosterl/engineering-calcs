"""
Input validation framework for Engineering Calculations Database.

This module provides a comprehensive validation system for engineering calculations,
including numeric validators, unit dimension validators, and a decorator for
automatic parameter validation.
"""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union
import inspect


class ValidationError(Exception):
    """
    Custom exception for validation errors.

    Attributes:
        field_name: The name of the field that failed validation.
        message: A descriptive error message.
    """

    def __init__(self, field_name: str, message: str) -> None:
        """
        Initialize a ValidationError.

        Args:
            field_name: The name of the parameter or field that failed validation.
            message: A descriptive message explaining the validation failure.
        """
        self.field_name = field_name
        self.message = message
        super().__init__(f"Parameter '{field_name}' {message}")

    def __str__(self) -> str:
        return f"Parameter '{self.field_name}' {self.message}"

    def __repr__(self) -> str:
        return f"ValidationError(field_name={self.field_name!r}, message={self.message!r})"


# =============================================================================
# Base Validator Class
# =============================================================================

class Validator(ABC):
    """
    Abstract base class for all validators.

    Validators check that values meet certain criteria and raise ValidationError
    if they do not.
    """

    @abstractmethod
    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate a value.

        Args:
            value: The value to validate.
            field_name: The name of the field being validated (for error messages).

        Raises:
            ValidationError: If the value fails validation.
        """
        pass

    def __call__(self, value: Any, field_name: str) -> None:
        """Allow validators to be called directly."""
        self.validate(value, field_name)


# =============================================================================
# Numeric Validators
# =============================================================================

class PositiveValidator(Validator):
    """
    Validator that ensures a value is strictly positive (> 0).

    Example:
        >>> validator = PositiveValidator()
        >>> validator.validate(5.0, 'force')  # OK
        >>> validator.validate(-5.0, 'force')  # Raises ValidationError
    """

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a value is positive.

        Args:
            value: The numeric value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is not positive.
        """
        # Extract numeric value if it's a quantity with units
        numeric_value = self._extract_magnitude(value)

        if numeric_value <= 0:
            raise ValidationError(
                field_name,
                f"must be positive, got {numeric_value}"
            )

    def _extract_magnitude(self, value: Any) -> float:
        """Extract the numeric magnitude from a value, handling unit quantities."""
        if hasattr(value, 'magnitude'):
            return float(value.magnitude)
        return float(value)


class NonNegativeValidator(Validator):
    """
    Validator that ensures a value is non-negative (>= 0).

    Example:
        >>> validator = NonNegativeValidator()
        >>> validator.validate(0.0, 'length')  # OK
        >>> validator.validate(5.0, 'length')  # OK
        >>> validator.validate(-1.0, 'length')  # Raises ValidationError
    """

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a value is non-negative.

        Args:
            value: The numeric value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is negative.
        """
        numeric_value = self._extract_magnitude(value)

        if numeric_value < 0:
            raise ValidationError(
                field_name,
                f"must be non-negative, got {numeric_value}"
            )

    def _extract_magnitude(self, value: Any) -> float:
        """Extract the numeric magnitude from a value, handling unit quantities."""
        if hasattr(value, 'magnitude'):
            return float(value.magnitude)
        return float(value)


class RangeValidator(Validator):
    """
    Validator that ensures a value falls within a specified range.

    The range is inclusive on both ends: min_val <= value <= max_val.

    Example:
        >>> validator = RangeValidator(0, 100)
        >>> validator.validate(50, 'percentage')  # OK
        >>> validator.validate(150, 'percentage')  # Raises ValidationError
    """

    def __init__(
        self,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> None:
        """
        Initialize a RangeValidator.

        Args:
            min_val: The minimum allowed value (inclusive). None means no lower bound.
            max_val: The maximum allowed value (inclusive). None means no upper bound.

        Raises:
            ValueError: If min_val > max_val when both are specified.
        """
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError(
                f"min_val ({min_val}) cannot be greater than max_val ({max_val})"
            )
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a value is within the specified range.

        Args:
            value: The numeric value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is outside the allowed range.
        """
        numeric_value = self._extract_magnitude(value)

        if self.min_val is not None and numeric_value < self.min_val:
            raise ValidationError(
                field_name,
                f"must be >= {self.min_val}, got {numeric_value}"
            )

        if self.max_val is not None and numeric_value > self.max_val:
            raise ValidationError(
                field_name,
                f"must be <= {self.max_val}, got {numeric_value}"
            )

    def _extract_magnitude(self, value: Any) -> float:
        """Extract the numeric magnitude from a value, handling unit quantities."""
        if hasattr(value, 'magnitude'):
            return float(value.magnitude)
        return float(value)


class NonZeroValidator(Validator):
    """
    Validator that ensures a value is not zero.

    Useful for values that will be used as divisors or in logarithms.

    Example:
        >>> validator = NonZeroValidator()
        >>> validator.validate(5.0, 'divisor')  # OK
        >>> validator.validate(-3.0, 'divisor')  # OK
        >>> validator.validate(0.0, 'divisor')  # Raises ValidationError
    """

    def __init__(self, tolerance: float = 1e-10) -> None:
        """
        Initialize a NonZeroValidator.

        Args:
            tolerance: Values with absolute value less than this are considered zero.
        """
        self.tolerance = tolerance

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a value is not zero.

        Args:
            value: The numeric value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is zero (within tolerance).
        """
        numeric_value = self._extract_magnitude(value)

        if abs(numeric_value) < self.tolerance:
            raise ValidationError(
                field_name,
                f"must not be zero, got {numeric_value}"
            )

    def _extract_magnitude(self, value: Any) -> float:
        """Extract the numeric magnitude from a value, handling unit quantities."""
        if hasattr(value, 'magnitude'):
            return float(value.magnitude)
        return float(value)


# =============================================================================
# Unit Dimension Validators
# =============================================================================

class DimensionValidator(Validator):
    """
    Validator that checks if a unit quantity has the correct dimension.

    This validator works with Pint quantities to ensure that values have
    the expected physical dimensions (length, pressure, force, etc.).

    Example:
        >>> from pint import UnitRegistry
        >>> ureg = UnitRegistry()
        >>> validator = DimensionValidator('[length]')
        >>> validator.validate(5 * ureg.meter, 'distance')  # OK
        >>> validator.validate(5 * ureg.second, 'distance')  # Raises ValidationError
    """

    # Common dimension aliases for user convenience
    DIMENSION_ALIASES: Dict[str, str] = {
        'length': '[length]',
        'mass': '[mass]',
        'time': '[time]',
        'temperature': '[temperature]',
        'pressure': '[mass] / [length] / [time] ** 2',
        'stress': '[mass] / [length] / [time] ** 2',
        'force': '[length] * [mass] / [time] ** 2',
        'area': '[length] ** 2',
        'volume': '[length] ** 3',
        'velocity': '[length] / [time]',
        'acceleration': '[length] / [time] ** 2',
        'density': '[mass] / [length] ** 3',
        'energy': '[length] ** 2 * [mass] / [time] ** 2',
        'power': '[length] ** 2 * [mass] / [time] ** 3',
        'moment': '[length] ** 2 * [mass] / [time] ** 2',
        'torque': '[length] ** 2 * [mass] / [time] ** 2',
        'angular_velocity': '1 / [time]',
        'frequency': '1 / [time]',
        'dimensionless': 'dimensionless',
    }

    def __init__(self, expected_dimension: str) -> None:
        """
        Initialize a DimensionValidator.

        Args:
            expected_dimension: The expected dimension string. Can be either a
                Pint dimension string like '[length]' or an alias like 'length'.
        """
        # Resolve aliases to actual dimension strings
        self.expected_dimension = self.DIMENSION_ALIASES.get(
            expected_dimension.lower(),
            expected_dimension
        )
        self._display_dimension = expected_dimension

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a quantity has the expected dimension.

        Args:
            value: A Pint quantity to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value has incorrect dimensions or is not a quantity.
        """
        # Check if value has units (Pint quantity)
        if not hasattr(value, 'dimensionality'):
            raise ValidationError(
                field_name,
                f"must be a quantity with units, got {type(value).__name__}"
            )

        # Get the actual dimensionality
        actual_dim = str(value.dimensionality)

        # Handle dimensionless check
        if self.expected_dimension == 'dimensionless':
            if value.dimensionless:
                return
            raise ValidationError(
                field_name,
                f"must be dimensionless, got dimension {actual_dim}"
            )

        # Check dimensionality compatibility
        # We need to check if the dimensions match
        try:
            # Try to convert to a base unit of the expected dimension
            # This is a compatibility check
            if not self._check_dimension_match(value):
                raise ValidationError(
                    field_name,
                    f"must have dimension '{self._display_dimension}', "
                    f"got dimension {actual_dim}"
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                field_name,
                f"must have dimension '{self._display_dimension}', "
                f"got dimension {actual_dim}"
            )

    def _check_dimension_match(self, value: Any) -> bool:
        """
        Check if a value's dimension matches the expected dimension.

        Args:
            value: A Pint quantity.

        Returns:
            True if dimensions match, False otherwise.
        """
        # Get the string representation of the value's dimensionality
        actual_dim = str(value.dimensionality)

        # Normalize dimension strings for comparison
        expected_normalized = self._normalize_dimension(self.expected_dimension)
        actual_normalized = self._normalize_dimension(actual_dim)

        return expected_normalized == actual_normalized

    def _normalize_dimension(self, dim_str: str) -> str:
        """
        Normalize a dimension string for comparison.

        Args:
            dim_str: A dimension string like '[length] ** 2'.

        Returns:
            A normalized version of the dimension string.
        """
        # Remove spaces and normalize formatting
        return dim_str.replace(' ', '').lower()


# =============================================================================
# Validation Decorator
# =============================================================================

def validate(*validators: Tuple[str, Validator]) -> Callable:
    """
    Decorator for validating function inputs based on parameter annotations.

    This decorator validates function arguments before the function is called.
    Validators are specified as tuples of (parameter_name, validator).

    Example:
        >>> @validate(
        ...     ('force', PositiveValidator()),
        ...     ('length', PositiveValidator()),
        ...     ('force', DimensionValidator('force'))
        ... )
        ... def calculate_stress(force, area):
        ...     return force / area

    Args:
        *validators: Tuples of (parameter_name, validator) to apply.

    Returns:
        A decorator that validates inputs before calling the function.
    """
    def decorator(func: Callable) -> Callable:
        # Get the function signature for parameter mapping
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Map positional args to parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments

            # Apply each validator
            for param_name, validator in validators:
                if param_name in all_args:
                    value = all_args[param_name]
                    validator.validate(value, param_name)

            return func(*args, **kwargs)

        # Store validators on the wrapper for introspection
        wrapper._validators = validators

        return wrapper

    return decorator


# =============================================================================
# Helper Functions
# =============================================================================

def validate_positive(value: Any, name: str) -> None:
    """
    Validate that a value is positive.

    This is a convenience function for one-off validations.

    Args:
        value: The numeric value to validate.
        name: The name of the parameter (for error messages).

    Raises:
        ValidationError: If the value is not positive.

    Example:
        >>> validate_positive(5.0, 'force')  # OK
        >>> validate_positive(-5.0, 'force')
        ValidationError: Parameter 'force' must be positive, got -5.0
    """
    validator = PositiveValidator()
    validator.validate(value, name)


def validate_non_negative(value: Any, name: str) -> None:
    """
    Validate that a value is non-negative.

    Args:
        value: The numeric value to validate.
        name: The name of the parameter (for error messages).

    Raises:
        ValidationError: If the value is negative.

    Example:
        >>> validate_non_negative(0.0, 'length')  # OK
        >>> validate_non_negative(-1.0, 'length')
        ValidationError: Parameter 'length' must be non-negative, got -1.0
    """
    validator = NonNegativeValidator()
    validator.validate(value, name)


def validate_non_zero(value: Any, name: str, tolerance: float = 1e-10) -> None:
    """
    Validate that a value is not zero.

    Args:
        value: The numeric value to validate.
        name: The name of the parameter (for error messages).
        tolerance: Values with absolute value less than this are considered zero.

    Raises:
        ValidationError: If the value is zero.

    Example:
        >>> validate_non_zero(5.0, 'divisor')  # OK
        >>> validate_non_zero(0.0, 'divisor')
        ValidationError: Parameter 'divisor' must not be zero, got 0.0
    """
    validator = NonZeroValidator(tolerance)
    validator.validate(value, name)


def validate_range(
    value: Any,
    min_val: Optional[float],
    max_val: Optional[float],
    name: str
) -> None:
    """
    Validate that a value falls within a specified range.

    Args:
        value: The numeric value to validate.
        min_val: The minimum allowed value (inclusive). None means no lower bound.
        max_val: The maximum allowed value (inclusive). None means no upper bound.
        name: The name of the parameter (for error messages).

    Raises:
        ValidationError: If the value is outside the allowed range.

    Example:
        >>> validate_range(50, 0, 100, 'percentage')  # OK
        >>> validate_range(150, 0, 100, 'percentage')
        ValidationError: Parameter 'percentage' must be <= 100, got 150
    """
    validator = RangeValidator(min_val, max_val)
    validator.validate(value, name)


def validate_unit_dimension(
    quantity: Any,
    expected_dimension: str,
    name: str
) -> None:
    """
    Validate that a quantity has the expected physical dimension.

    This function validates that a Pint quantity has the correct physical
    dimensions (e.g., length, pressure, force).

    Args:
        quantity: A Pint quantity to validate.
        expected_dimension: The expected dimension. Can be a Pint dimension
            string like '[length]' or an alias like 'length', 'pressure',
            'force', etc.
        name: The name of the parameter (for error messages).

    Raises:
        ValidationError: If the quantity has incorrect dimensions.

    Example:
        >>> from pint import UnitRegistry
        >>> ureg = UnitRegistry()
        >>> validate_unit_dimension(5 * ureg.meter, 'length', 'distance')  # OK
        >>> validate_unit_dimension(5 * ureg.second, 'length', 'distance')
        ValidationError: Parameter 'distance' must have dimension 'length', got dimension [time]
    """
    validator = DimensionValidator(expected_dimension)
    validator.validate(quantity, name)


# =============================================================================
# Composite Validators
# =============================================================================

class CompositeValidator(Validator):
    """
    A validator that combines multiple validators.

    All validators must pass for the value to be considered valid.

    Example:
        >>> validator = CompositeValidator([
        ...     PositiveValidator(),
        ...     RangeValidator(max_val=100)
        ... ])
        >>> validator.validate(50, 'value')  # OK
        >>> validator.validate(-5, 'value')  # Raises ValidationError
    """

    def __init__(self, validators: list) -> None:
        """
        Initialize a CompositeValidator.

        Args:
            validators: A list of Validator instances to apply.
        """
        self.validators = validators

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate a value against all contained validators.

        Args:
            value: The value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If any validator fails.
        """
        for validator in self.validators:
            validator.validate(value, field_name)


class OptionalValidator(Validator):
    """
    A validator that allows None values but validates non-None values.

    Example:
        >>> validator = OptionalValidator(PositiveValidator())
        >>> validator.validate(None, 'optional_force')  # OK
        >>> validator.validate(5.0, 'optional_force')  # OK
        >>> validator.validate(-5.0, 'optional_force')  # Raises ValidationError
    """

    def __init__(self, inner_validator: Validator) -> None:
        """
        Initialize an OptionalValidator.

        Args:
            inner_validator: The validator to apply to non-None values.
        """
        self.inner_validator = inner_validator

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate a value, allowing None.

        Args:
            value: The value to validate (can be None).
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is not None and fails validation.
        """
        if value is not None:
            self.inner_validator.validate(value, field_name)


# =============================================================================
# Type Validators
# =============================================================================

class TypeValidator(Validator):
    """
    Validator that checks if a value is of the expected type.

    Example:
        >>> validator = TypeValidator(float, int)
        >>> validator.validate(5.0, 'value')  # OK
        >>> validator.validate(5, 'value')  # OK
        >>> validator.validate('5', 'value')  # Raises ValidationError
    """

    def __init__(self, *expected_types: Type) -> None:
        """
        Initialize a TypeValidator.

        Args:
            *expected_types: The types that the value can be.
        """
        self.expected_types = expected_types

    def validate(self, value: Any, field_name: str) -> None:
        """
        Validate that a value is of the expected type.

        Args:
            value: The value to validate.
            field_name: The name of the field being validated.

        Raises:
            ValidationError: If the value is not of an expected type.
        """
        # Handle Pint quantities - check the magnitude type
        if hasattr(value, 'magnitude'):
            actual_value = value.magnitude
        else:
            actual_value = value

        if not isinstance(actual_value, self.expected_types):
            type_names = ', '.join(t.__name__ for t in self.expected_types)
            raise ValidationError(
                field_name,
                f"must be of type {type_names}, got {type(actual_value).__name__}"
            )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Exception
    'ValidationError',

    # Base class
    'Validator',

    # Numeric validators
    'PositiveValidator',
    'NonNegativeValidator',
    'RangeValidator',
    'NonZeroValidator',

    # Dimension validators
    'DimensionValidator',

    # Composite validators
    'CompositeValidator',
    'OptionalValidator',

    # Type validators
    'TypeValidator',

    # Decorator
    'validate',

    # Helper functions
    'validate_positive',
    'validate_non_negative',
    'validate_non_zero',
    'validate_range',
    'validate_unit_dimension',
]
