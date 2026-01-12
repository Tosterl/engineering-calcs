"""
Base calculation framework for Engineering Calculations Database.

This module provides the foundation for all engineering calculations,
including base classes, result containers, and a calculation registry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from src.core.units import Quantity


@dataclass
class Parameter:
    """
    Definition of an input or output parameter for a calculation.

    Attributes:
        name: The parameter name (used as variable name).
        unit: The expected unit string (e.g., 'm', 'Pa', 'dimensionless').
        description: Human-readable description of the parameter.
        default: Optional default value for the parameter.
    """
    name: str
    unit: str
    description: str
    default: Optional[float] = None


# Alias for backwards compatibility
ParameterDefinition = Parameter


@dataclass
class IntermediateStep:
    """
    Represents an intermediate step in a calculation for report generation.

    Attributes:
        description: What this step calculates.
        formula: The formula used (can be LaTeX or plain text).
        result: The result of this step.
        substitution: The formula with values substituted in.
    """
    description: str
    formula: str
    result: Any
    substitution: str = ""


@dataclass
class CalculationResult:
    """
    Container for calculation results including intermediate steps.

    Attributes:
        inputs: Dictionary of input parameter names to Quantity values.
        outputs: Dictionary of output parameter names to Quantity values.
        intermediate_steps: List of intermediate calculation steps.
        timestamp: When the calculation was performed.
        calculation_name: Name of the calculation that produced this result.
        metadata: Additional metadata about the calculation.
    """
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    intermediate_steps: List[IntermediateStep] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    calculation_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_output(self, name: str) -> Any:
        """Get a specific output value by name."""
        return self.outputs.get(name)

    def get_input(self, name: str) -> Any:
        """Get a specific input value by name."""
        return self.inputs.get(name)

    def add_step(self, step: IntermediateStep) -> None:
        """Add an intermediate step to the result."""
        self.intermediate_steps.append(step)


class Calculation(ABC):
    """
    Abstract base class for all engineering calculations.

    Subclasses must implement:
    - name: Class attribute for the calculation name
    - category: Class attribute for the domain category
    - description: Class attribute describing the calculation
    - input_params: Class attribute listing input parameters
    - output_params: Class attribute listing output parameters
    - calculate(): Method that performs the calculation

    Example:
        >>> class MyCalc(Calculation):
        ...     name = "My Calculation"
        ...     category = "General"
        ...     description = "A sample calculation"
        ...     input_params = [
        ...         Parameter("force", "N", "Applied force"),
        ...     ]
        ...     output_params = [
        ...         Parameter("result", "Pa", "Calculated result"),
        ...     ]
        ...     def calculate(self, **inputs) -> CalculationResult:
        ...         # Implementation
        ...         pass
    """

    # Class attributes to be defined by subclasses
    name: str = "Unnamed Calculation"
    category: str = "Uncategorized"
    description: str = ""
    references: List[str] = []
    input_params: List[Parameter] = []
    output_params: List[Parameter] = []

    def __init__(self) -> None:
        """Initialize the calculation."""
        self._intermediate_steps: List[IntermediateStep] = []

    def reset(self) -> None:
        """Clear intermediate steps from previous calculation."""
        self._intermediate_steps = []

    def add_step(
        self,
        description: str,
        formula: str,
        result: Any,
        substitution: str = "",
    ) -> None:
        """
        Add an intermediate calculation step.

        Args:
            description: What this step calculates.
            formula: The formula used (LaTeX or plain text).
            result: The calculated result.
            substitution: The formula with values substituted in.
        """
        step = IntermediateStep(
            description=description,
            formula=formula,
            result=result,
            substitution=substitution,
        )
        self._intermediate_steps.append(step)

    def format_result(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any]
    ) -> CalculationResult:
        """
        Create a CalculationResult with the current intermediate steps.

        Args:
            inputs: Dictionary of input values.
            outputs: Dictionary of output values.

        Returns:
            CalculationResult containing all calculation data.
        """
        return CalculationResult(
            inputs=inputs,
            outputs=outputs,
            intermediate_steps=self._intermediate_steps.copy(),
            calculation_name=self.name,
            metadata={
                "category": self.category,
                "description": self.description,
                "references": self.references
            }
        )

    @abstractmethod
    def calculate(self, **inputs: Any) -> CalculationResult:
        """
        Perform the calculation with the given inputs.

        Args:
            **inputs: Keyword arguments of input Quantity values.

        Returns:
            CalculationResult containing inputs, outputs, and intermediate steps.

        Raises:
            ValidationError: If inputs are invalid.
        """
        pass

    def get_input_param(self, name: str) -> Optional[Parameter]:
        """Get the definition for a specific input parameter."""
        for param in self.input_params:
            if param.name == name:
                return param
        return None

    def get_output_param(self, name: str) -> Optional[Parameter]:
        """Get the definition for a specific output parameter."""
        for param in self.output_params:
            if param.name == name:
                return param
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', category='{self.category}')>"


class CalculationRegistry:
    """
    Registry for discovering and managing available calculations.

    This singleton class maintains a registry of all calculation classes
    and provides methods to discover, retrieve, and instantiate them.
    """

    _instance: Optional[CalculationRegistry] = None
    _calculations: Dict[str, Type[Calculation]] = {}

    def __new__(cls) -> CalculationRegistry:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._calculations = {}
        return cls._instance

    def register(self, calc_class: Type[Calculation]) -> Type[Calculation]:
        """
        Register a calculation class.

        Can be used as a decorator:
            @registry.register
            class MyCalculation(Calculation):
                ...

        Args:
            calc_class: The calculation class to register.

        Returns:
            The same calculation class (for decorator use).
        """
        key = f"{calc_class.category}.{calc_class.name}"
        self._calculations[key] = calc_class
        return calc_class

    def get(self, category: str, name: str) -> Optional[Type[Calculation]]:
        """
        Get a calculation class by category and name.

        Args:
            category: The calculation category.
            name: The calculation name.

        Returns:
            The calculation class, or None if not found.
        """
        key = f"{category}.{name}"
        return self._calculations.get(key)

    def get_by_key(self, key: str) -> Optional[Type[Calculation]]:
        """
        Get a calculation class by its full key.

        Args:
            key: The full key in format "category.name".

        Returns:
            The calculation class, or None if not found.
        """
        return self._calculations.get(key)

    def list_all(self) -> List[Type[Calculation]]:
        """Get all registered calculation classes."""
        return list(self._calculations.values())

    def list_by_category(self, category: str) -> List[Type[Calculation]]:
        """Get all calculation classes in a category."""
        return [
            calc for key, calc in self._calculations.items()
            if key.startswith(f"{category}.")
        ]

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for key in self._calculations.keys():
            category = key.split(".")[0]
            categories.add(category)
        return sorted(list(categories))

    def create(self, category: str, name: str) -> Optional[Calculation]:
        """
        Create an instance of a calculation.

        Args:
            category: The calculation category.
            name: The calculation name.

        Returns:
            An instance of the calculation, or None if not found.
        """
        calc_class = self.get(category, name)
        if calc_class:
            return calc_class()
        return None

    def clear(self) -> None:
        """Clear all registered calculations (mainly for testing)."""
        self._calculations.clear()


# Global registry instance
calculation_registry = CalculationRegistry()


def register(calc_class: Type[Calculation]) -> Type[Calculation]:
    """
    Decorator to register a calculation class with the global registry.

    Example:
        @register
        class MyCalculation(Calculation):
            name = "My Calculation"
            category = "General"
            ...
    """
    return calculation_registry.register(calc_class)


# Alias for backwards compatibility
register_calculation = register


def get_default_registry() -> CalculationRegistry:
    """
    Get the global default calculation registry.

    Returns:
        The singleton CalculationRegistry instance.
    """
    return calculation_registry


def create_calculation(category: str, name: str, **inputs: Any) -> CalculationResult:
    """
    Factory function to create and execute a calculation.

    Args:
        category: The calculation category.
        name: The calculation name.
        **inputs: Input values for the calculation.

    Returns:
        CalculationResult from executing the calculation.

    Raises:
        ValueError: If the calculation is not found.
    """
    calc = calculation_registry.create(category, name)
    if calc is None:
        raise ValueError(f"Calculation not found: {category}.{name}")
    return calc.calculate(**inputs)


# Module exports
__all__ = [
    "Parameter",
    "ParameterDefinition",
    "IntermediateStep",
    "CalculationResult",
    "Calculation",
    "CalculationRegistry",
    "calculation_registry",
    "register",
    "register_calculation",
    "get_default_registry",
    "create_calculation",
]
