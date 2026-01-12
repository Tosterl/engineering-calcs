"""
Fatigue Analysis Calculations for Engineering Calculations Database.

This module implements fatigue analysis calculations including stress amplitude,
S-N curve life prediction, cumulative damage models (Miner's rule), and mean
stress correction methods (Goodman, Gerber, Soderberg). All calculations extend
the base Calculation class and use the Quantity class for unit-aware operations.

References:
    - Shigley, J.E., Mischke, C.R. "Mechanical Engineering Design", 9th Ed.
    - Norton, R.L. "Machine Design: An Integrated Approach", 5th Ed.
    - Dowling, N.E. "Mechanical Behavior of Materials", 4th Ed.
"""

from __future__ import annotations

from typing import Any, List

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity
from src.core.validation import (
    PositiveValidator,
    NonZeroValidator,
    RangeValidator,
    ValidationError,
)


@register
class StressAmplitude(Calculation):
    """
    Calculate stress amplitude and related parameters from max/min stress.

    The stress amplitude is half the range of the cyclic stress. This
    calculation also determines the mean stress and stress ratio (R).

    Formulas:
        sigma_a = (sigma_max - sigma_min) / 2
        sigma_m = (sigma_max + sigma_min) / 2
        R = sigma_min / sigma_max

    Where:
        sigma_a = stress amplitude (Pa)
        sigma_m = mean stress (Pa)
        R = stress ratio (dimensionless)
        sigma_max = maximum stress (Pa)
        sigma_min = minimum stress (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Stress Amplitude"
    category = "Fatigue"
    description = (
        "Calculate stress amplitude, mean stress, and stress ratio from "
        "maximum and minimum cyclic stress values."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("max_stress", "Pa", "Maximum stress in the loading cycle"),
        Parameter("min_stress", "Pa", "Minimum stress in the loading cycle"),
    ]
    output_params = [
        Parameter("stress_amplitude", "Pa", "Stress amplitude (half the stress range)"),
        Parameter("mean_stress", "Pa", "Mean stress (average of max and min)"),
        Parameter("stress_ratio", "dimensionless", "Stress ratio R = sigma_min / sigma_max"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate stress amplitude, mean stress, and stress ratio.

        Args:
            max_stress: Maximum stress as Quantity (Pa).
            min_stress: Minimum stress as Quantity (Pa).

        Returns:
            CalculationResult with stress amplitude, mean stress, and stress ratio.

        Raises:
            ValidationError: If max_stress equals zero when calculating stress ratio.
        """
        self.reset()

        max_stress: Quantity = kwargs["max_stress"]
        min_stress: Quantity = kwargs["min_stress"]

        inputs = {
            "max_stress": max_stress,
            "min_stress": min_stress,
        }

        # Convert to consistent units
        sigma_max = max_stress.to("Pa")
        sigma_min = min_stress.to("Pa")

        # Calculate stress amplitude: sigma_a = (sigma_max - sigma_min) / 2
        stress_amplitude = (sigma_max - sigma_min) / 2
        self.add_step(
            description="Calculate stress amplitude",
            formula="sigma_a = (sigma_max - sigma_min) / 2",
            result=stress_amplitude,
            substitution=f"sigma_a = ({sigma_max} - {sigma_min}) / 2 = {stress_amplitude}",
        )

        # Calculate mean stress: sigma_m = (sigma_max + sigma_min) / 2
        mean_stress = (sigma_max + sigma_min) / 2
        self.add_step(
            description="Calculate mean stress",
            formula="sigma_m = (sigma_max + sigma_min) / 2",
            result=mean_stress,
            substitution=f"sigma_m = ({sigma_max} + {sigma_min}) / 2 = {mean_stress}",
        )

        # Calculate stress ratio: R = sigma_min / sigma_max
        nonzero_validator = NonZeroValidator()
        nonzero_validator.validate(sigma_max, "max_stress")

        stress_ratio_value = sigma_min.magnitude / sigma_max.magnitude
        stress_ratio = Quantity(stress_ratio_value, "dimensionless")
        self.add_step(
            description="Calculate stress ratio",
            formula="R = sigma_min / sigma_max",
            result=stress_ratio,
            substitution=f"R = {sigma_min} / {sigma_max} = {stress_ratio}",
        )

        outputs = {
            "stress_amplitude": stress_amplitude,
            "mean_stress": mean_stress,
            "stress_ratio": stress_ratio,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SNCurveLife(Calculation):
    """
    Calculate fatigue life from S-N curve using Basquin's equation.

    Basquin's equation relates stress amplitude to the number of cycles
    to failure for high-cycle fatigue.

    Formula:
        N = (sigma_a / a)^(-1/b)

    Where:
        N = cycles to failure (dimensionless)
        sigma_a = stress amplitude (Pa)
        a = fatigue strength coefficient (Pa)
        b = fatigue strength exponent (dimensionless, typically negative)

    Note: The fatigue strength exponent b is typically negative (e.g., -0.085).
    The formula is often written as sigma_a = a * N^b.

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Dowling, N.E., "Mechanical Behavior of Materials", 4th Ed., Ch. 9
    """

    name = "S-N Curve Life (Basquin)"
    category = "Fatigue"
    description = (
        "Calculate fatigue life (cycles to failure) using Basquin's equation "
        "for high-cycle fatigue analysis."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Dowling, N.E., 'Mechanical Behavior of Materials', 4th Ed., Ch. 9",
    ]

    input_params = [
        Parameter("stress_amplitude", "Pa", "Stress amplitude"),
        Parameter("fatigue_strength_coefficient", "Pa", "Fatigue strength coefficient (a or sigma_f')"),
        Parameter("fatigue_strength_exponent", "dimensionless", "Fatigue strength exponent (b, typically negative)"),
    ]
    output_params = [
        Parameter("cycles_to_failure", "dimensionless", "Number of cycles to failure (N)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate cycles to failure using Basquin's equation.

        Args:
            stress_amplitude: Stress amplitude as Quantity (Pa).
            fatigue_strength_coefficient: Material fatigue strength coefficient as Quantity (Pa).
            fatigue_strength_exponent: Fatigue strength exponent as Quantity (dimensionless).

        Returns:
            CalculationResult with cycles to failure.

        Raises:
            ValidationError: If stress_amplitude or fatigue_strength_coefficient is not positive,
                           or if fatigue_strength_exponent is zero.
        """
        self.reset()

        stress_amplitude: Quantity = kwargs["stress_amplitude"]
        fatigue_strength_coefficient: Quantity = kwargs["fatigue_strength_coefficient"]
        fatigue_strength_exponent: Quantity = kwargs["fatigue_strength_exponent"]

        inputs = {
            "stress_amplitude": stress_amplitude,
            "fatigue_strength_coefficient": fatigue_strength_coefficient,
            "fatigue_strength_exponent": fatigue_strength_exponent,
        }

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(stress_amplitude, "stress_amplitude")
        pos_validator.validate(fatigue_strength_coefficient, "fatigue_strength_coefficient")

        nonzero_validator = NonZeroValidator()
        nonzero_validator.validate(fatigue_strength_exponent, "fatigue_strength_exponent")

        # Convert to consistent units
        sigma_a = stress_amplitude.to("Pa")
        a = fatigue_strength_coefficient.to("Pa")
        b = fatigue_strength_exponent.magnitude

        # Calculate stress ratio
        stress_ratio = sigma_a.magnitude / a.magnitude
        self.add_step(
            description="Calculate stress ratio (sigma_a / a)",
            formula="ratio = sigma_a / a",
            result=Quantity(stress_ratio, "dimensionless"),
            substitution=f"ratio = {sigma_a} / {a} = {stress_ratio:.6g}",
        )

        # Calculate cycles to failure: N = (sigma_a / a)^(-1/b)
        exponent = -1.0 / b
        self.add_step(
            description="Calculate exponent (-1/b)",
            formula="exponent = -1 / b",
            result=Quantity(exponent, "dimensionless"),
            substitution=f"exponent = -1 / {b} = {exponent:.6g}",
        )

        cycles_value = stress_ratio ** exponent
        cycles_to_failure = Quantity(cycles_value, "dimensionless")
        self.add_step(
            description="Calculate cycles to failure using Basquin's equation",
            formula="N = (sigma_a / a)^(-1/b)",
            result=cycles_to_failure,
            substitution=f"N = ({stress_ratio:.6g})^({exponent:.6g}) = {cycles_value:.4g}",
        )

        outputs = {
            "cycles_to_failure": cycles_to_failure,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class MinersRule(Calculation):
    """
    Calculate cumulative fatigue damage using Miner's rule.

    Miner's rule (Palmgren-Miner rule) is a linear cumulative damage
    hypothesis for variable amplitude loading.

    Formula:
        D = Sum(n_i / N_i)

    Where:
        D = cumulative damage fraction (failure when D >= 1)
        n_i = number of cycles at stress level i
        N_i = fatigue life (cycles to failure) at stress level i

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Miner's Rule (Cumulative Damage)"
    category = "Fatigue"
    description = (
        "Calculate cumulative fatigue damage using Miner's linear damage "
        "accumulation rule for variable amplitude loading."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("cycle_counts", "dimensionless", "List of cycle counts at each stress level (n_i)"),
        Parameter("cycles_to_failure", "dimensionless", "List of cycles to failure at each stress level (N_i)"),
    ]
    output_params = [
        Parameter("damage_fraction", "dimensionless", "Cumulative damage fraction (D)"),
        Parameter("remaining_life_fraction", "dimensionless", "Remaining life fraction (1 - D)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate cumulative damage using Miner's rule.

        Args:
            cycle_counts: List of cycle counts at each stress level.
            cycles_to_failure: List of cycles to failure at each stress level.

        Returns:
            CalculationResult with damage fraction and remaining life fraction.

        Raises:
            ValidationError: If list lengths don't match or any cycles_to_failure is not positive.
        """
        self.reset()

        cycle_counts: List = kwargs["cycle_counts"]
        cycles_to_failure: List = kwargs["cycles_to_failure"]

        if len(cycle_counts) != len(cycles_to_failure):
            raise ValidationError(
                "cycle_counts",
                f"length ({len(cycle_counts)}) must match cycles_to_failure length ({len(cycles_to_failure)})"
            )

        inputs = {
            "cycle_counts": cycle_counts,
            "cycles_to_failure": cycles_to_failure,
        }

        # Validate that all cycles_to_failure values are positive
        pos_validator = PositiveValidator()
        for i, n_f in enumerate(cycles_to_failure):
            pos_validator.validate(n_f, f"cycles_to_failure[{i}]")

        # Calculate damage contributions
        total_damage = 0.0
        damage_terms = []

        for i, (n_i, N_i) in enumerate(zip(cycle_counts, cycles_to_failure)):
            # Extract magnitudes
            n_val = n_i.magnitude if hasattr(n_i, 'magnitude') else float(n_i)
            N_val = N_i.magnitude if hasattr(N_i, 'magnitude') else float(N_i)

            damage_i = n_val / N_val
            total_damage += damage_i
            damage_terms.append(f"({n_val:.4g}/{N_val:.4g})")

            self.add_step(
                description=f"Calculate damage contribution for stress level {i + 1}",
                formula="D_i = n_i / N_i",
                result=Quantity(damage_i, "dimensionless"),
                substitution=f"D_{i + 1} = {n_val:.4g} / {N_val:.4g} = {damage_i:.6g}",
            )

        damage_fraction = Quantity(total_damage, "dimensionless")
        self.add_step(
            description="Calculate total cumulative damage",
            formula="D = Sum(n_i / N_i)",
            result=damage_fraction,
            substitution=f"D = {' + '.join(damage_terms)} = {total_damage:.6g}",
        )

        remaining_life = 1.0 - total_damage
        remaining_life_fraction = Quantity(remaining_life, "dimensionless")
        self.add_step(
            description="Calculate remaining life fraction",
            formula="Remaining = 1 - D",
            result=remaining_life_fraction,
            substitution=f"Remaining = 1 - {total_damage:.6g} = {remaining_life:.6g}",
        )

        outputs = {
            "damage_fraction": damage_fraction,
            "remaining_life_fraction": remaining_life_fraction,
        }

        result = self.format_result(inputs=inputs, outputs=outputs)

        # Add warning if damage exceeds 1
        if total_damage >= 1.0:
            result.metadata["warning"] = "WARNING: Cumulative damage >= 1.0 indicates fatigue failure!"
        elif total_damage >= 0.8:
            result.metadata["warning"] = "CAUTION: Cumulative damage approaching failure threshold."

        return result


@register
class GoodmanDiagram(Calculation):
    """
    Calculate fatigue safety factor using the Goodman criterion.

    The Goodman diagram provides a conservative approach to account for
    the effect of mean stress on fatigue life.

    Formula:
        sigma_a / Se + sigma_m / Sut = 1/n

    Solving for n (safety factor):
        n = 1 / (sigma_a / Se + sigma_m / Sut)

    Where:
        n = safety factor (dimensionless)
        sigma_a = stress amplitude (Pa)
        sigma_m = mean stress (Pa)
        Se = endurance limit (Pa)
        Sut = ultimate tensile strength (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Goodman Diagram"
    category = "Fatigue"
    description = (
        "Calculate fatigue safety factor using the modified Goodman criterion "
        "for mean stress effects. Conservative for ductile materials."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("stress_amplitude", "Pa", "Stress amplitude"),
        Parameter("mean_stress", "Pa", "Mean stress"),
        Parameter("endurance_limit", "Pa", "Endurance limit (corrected)"),
        Parameter("ultimate_strength", "Pa", "Ultimate tensile strength"),
    ]
    output_params = [
        Parameter("safety_factor", "dimensionless", "Fatigue safety factor"),
        Parameter("is_safe", "dimensionless", "Boolean indicating if design is safe (n > 1)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate safety factor using Goodman criterion.

        Args:
            stress_amplitude: Stress amplitude as Quantity (Pa).
            mean_stress: Mean stress as Quantity (Pa).
            endurance_limit: Endurance limit as Quantity (Pa).
            ultimate_strength: Ultimate tensile strength as Quantity (Pa).

        Returns:
            CalculationResult with safety factor and safety indication.

        Raises:
            ValidationError: If any strength parameter is not positive.
        """
        self.reset()

        stress_amplitude: Quantity = kwargs["stress_amplitude"]
        mean_stress: Quantity = kwargs["mean_stress"]
        endurance_limit: Quantity = kwargs["endurance_limit"]
        ultimate_strength: Quantity = kwargs["ultimate_strength"]

        inputs = {
            "stress_amplitude": stress_amplitude,
            "mean_stress": mean_stress,
            "endurance_limit": endurance_limit,
            "ultimate_strength": ultimate_strength,
        }

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(endurance_limit, "endurance_limit")
        pos_validator.validate(ultimate_strength, "ultimate_strength")

        # Convert to consistent units
        sigma_a = stress_amplitude.to("Pa")
        sigma_m = mean_stress.to("Pa")
        Se = endurance_limit.to("Pa")
        Sut = ultimate_strength.to("Pa")

        # Calculate amplitude term: sigma_a / Se
        amplitude_term = sigma_a.magnitude / Se.magnitude
        self.add_step(
            description="Calculate amplitude term (sigma_a / Se)",
            formula="amplitude_term = sigma_a / Se",
            result=Quantity(amplitude_term, "dimensionless"),
            substitution=f"amplitude_term = {sigma_a} / {Se} = {amplitude_term:.6g}",
        )

        # Calculate mean term: sigma_m / Sut
        mean_term = sigma_m.magnitude / Sut.magnitude
        self.add_step(
            description="Calculate mean term (sigma_m / Sut)",
            formula="mean_term = sigma_m / Sut",
            result=Quantity(mean_term, "dimensionless"),
            substitution=f"mean_term = {sigma_m} / {Sut} = {mean_term:.6g}",
        )

        # Calculate Goodman sum
        goodman_sum = amplitude_term + mean_term
        self.add_step(
            description="Calculate Goodman sum",
            formula="Goodman_sum = sigma_a/Se + sigma_m/Sut",
            result=Quantity(goodman_sum, "dimensionless"),
            substitution=f"Goodman_sum = {amplitude_term:.6g} + {mean_term:.6g} = {goodman_sum:.6g}",
        )

        # Calculate safety factor: n = 1 / Goodman_sum
        if goodman_sum <= 0:
            raise ValidationError(
                "stress_amplitude",
                "Goodman sum must be positive for valid safety factor calculation"
            )

        n = 1.0 / goodman_sum
        safety_factor = Quantity(n, "dimensionless")
        self.add_step(
            description="Calculate safety factor",
            formula="n = 1 / (sigma_a/Se + sigma_m/Sut)",
            result=safety_factor,
            substitution=f"n = 1 / {goodman_sum:.6g} = {n:.4g}",
        )

        # Determine if safe
        is_safe_value = 1.0 if n > 1.0 else 0.0
        is_safe = Quantity(is_safe_value, "dimensionless")
        self.add_step(
            description="Check if design is safe (n > 1)",
            formula="is_safe = (n > 1)",
            result=is_safe,
            substitution=f"is_safe = ({n:.4g} > 1) = {bool(is_safe_value)}",
        )

        outputs = {
            "safety_factor": safety_factor,
            "is_safe": is_safe,
        }

        result = self.format_result(inputs=inputs, outputs=outputs)

        # Add warning for unsafe design
        if n < 1.0:
            result.metadata["warning"] = "WARNING: Safety factor < 1.0 indicates potential fatigue failure!"
        elif n < 1.5:
            result.metadata["warning"] = "CAUTION: Safety factor < 1.5 may be inadequate for some applications."

        return result


@register
class GerberCriterion(Calculation):
    """
    Calculate fatigue safety factor using the Gerber criterion.

    The Gerber parabola provides a less conservative approach than Goodman
    and often better matches experimental data for ductile materials.

    Formula:
        (sigma_a / Se) + (sigma_m / Sut)^2 = 1/n

    Solving for n:
        n = 1 / [(sigma_a / Se) + (sigma_m / Sut)^2]

    Where:
        n = safety factor (dimensionless)
        sigma_a = stress amplitude (Pa)
        sigma_m = mean stress (Pa)
        Se = endurance limit (Pa)
        Sut = ultimate tensile strength (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Gerber Criterion"
    category = "Fatigue"
    description = (
        "Calculate fatigue safety factor using the Gerber parabolic criterion "
        "for mean stress effects. Less conservative than Goodman."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("stress_amplitude", "Pa", "Stress amplitude"),
        Parameter("mean_stress", "Pa", "Mean stress"),
        Parameter("endurance_limit", "Pa", "Endurance limit (corrected)"),
        Parameter("ultimate_strength", "Pa", "Ultimate tensile strength"),
    ]
    output_params = [
        Parameter("safety_factor", "dimensionless", "Fatigue safety factor"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate safety factor using Gerber criterion.

        Args:
            stress_amplitude: Stress amplitude as Quantity (Pa).
            mean_stress: Mean stress as Quantity (Pa).
            endurance_limit: Endurance limit as Quantity (Pa).
            ultimate_strength: Ultimate tensile strength as Quantity (Pa).

        Returns:
            CalculationResult with safety factor.

        Raises:
            ValidationError: If any strength parameter is not positive.
        """
        self.reset()

        stress_amplitude: Quantity = kwargs["stress_amplitude"]
        mean_stress: Quantity = kwargs["mean_stress"]
        endurance_limit: Quantity = kwargs["endurance_limit"]
        ultimate_strength: Quantity = kwargs["ultimate_strength"]

        inputs = {
            "stress_amplitude": stress_amplitude,
            "mean_stress": mean_stress,
            "endurance_limit": endurance_limit,
            "ultimate_strength": ultimate_strength,
        }

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(endurance_limit, "endurance_limit")
        pos_validator.validate(ultimate_strength, "ultimate_strength")

        # Convert to consistent units
        sigma_a = stress_amplitude.to("Pa")
        sigma_m = mean_stress.to("Pa")
        Se = endurance_limit.to("Pa")
        Sut = ultimate_strength.to("Pa")

        # Calculate amplitude term: sigma_a / Se
        amplitude_term = sigma_a.magnitude / Se.magnitude
        self.add_step(
            description="Calculate amplitude term (sigma_a / Se)",
            formula="amplitude_term = sigma_a / Se",
            result=Quantity(amplitude_term, "dimensionless"),
            substitution=f"amplitude_term = {sigma_a} / {Se} = {amplitude_term:.6g}",
        )

        # Calculate mean term squared: (sigma_m / Sut)^2
        mean_ratio = sigma_m.magnitude / Sut.magnitude
        mean_term_squared = mean_ratio ** 2
        self.add_step(
            description="Calculate mean term squared (sigma_m / Sut)^2",
            formula="mean_term_squared = (sigma_m / Sut)^2",
            result=Quantity(mean_term_squared, "dimensionless"),
            substitution=f"mean_term_squared = ({sigma_m} / {Sut})^2 = {mean_ratio:.6g}^2 = {mean_term_squared:.6g}",
        )

        # Calculate Gerber sum
        gerber_sum = amplitude_term + mean_term_squared
        self.add_step(
            description="Calculate Gerber sum",
            formula="Gerber_sum = sigma_a/Se + (sigma_m/Sut)^2",
            result=Quantity(gerber_sum, "dimensionless"),
            substitution=f"Gerber_sum = {amplitude_term:.6g} + {mean_term_squared:.6g} = {gerber_sum:.6g}",
        )

        # Calculate safety factor: n = 1 / Gerber_sum
        if gerber_sum <= 0:
            raise ValidationError(
                "stress_amplitude",
                "Gerber sum must be positive for valid safety factor calculation"
            )

        n = 1.0 / gerber_sum
        safety_factor = Quantity(n, "dimensionless")
        self.add_step(
            description="Calculate safety factor",
            formula="n = 1 / [sigma_a/Se + (sigma_m/Sut)^2]",
            result=safety_factor,
            substitution=f"n = 1 / {gerber_sum:.6g} = {n:.4g}",
        )

        outputs = {
            "safety_factor": safety_factor,
        }

        result = self.format_result(inputs=inputs, outputs=outputs)

        # Add warning for unsafe design
        if n < 1.0:
            result.metadata["warning"] = "WARNING: Safety factor < 1.0 indicates potential fatigue failure!"
        elif n < 1.5:
            result.metadata["warning"] = "CAUTION: Safety factor < 1.5 may be inadequate for some applications."

        return result


@register
class SoderbergCriterion(Calculation):
    """
    Calculate fatigue safety factor using the Soderberg criterion.

    The Soderberg criterion is the most conservative approach, using
    yield strength instead of ultimate strength for the mean stress term.

    Formula:
        sigma_a / Se + sigma_m / Sy = 1/n

    Solving for n:
        n = 1 / (sigma_a / Se + sigma_m / Sy)

    Where:
        n = safety factor (dimensionless)
        sigma_a = stress amplitude (Pa)
        sigma_m = mean stress (Pa)
        Se = endurance limit (Pa)
        Sy = yield strength (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Soderberg Criterion"
    category = "Fatigue"
    description = (
        "Calculate fatigue safety factor using the Soderberg criterion "
        "for mean stress effects. Most conservative approach using yield strength."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("stress_amplitude", "Pa", "Stress amplitude"),
        Parameter("mean_stress", "Pa", "Mean stress"),
        Parameter("endurance_limit", "Pa", "Endurance limit (corrected)"),
        Parameter("yield_strength", "Pa", "Yield strength"),
    ]
    output_params = [
        Parameter("safety_factor", "dimensionless", "Fatigue safety factor"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate safety factor using Soderberg criterion.

        Args:
            stress_amplitude: Stress amplitude as Quantity (Pa).
            mean_stress: Mean stress as Quantity (Pa).
            endurance_limit: Endurance limit as Quantity (Pa).
            yield_strength: Yield strength as Quantity (Pa).

        Returns:
            CalculationResult with safety factor.

        Raises:
            ValidationError: If any strength parameter is not positive.
        """
        self.reset()

        stress_amplitude: Quantity = kwargs["stress_amplitude"]
        mean_stress: Quantity = kwargs["mean_stress"]
        endurance_limit: Quantity = kwargs["endurance_limit"]
        yield_strength: Quantity = kwargs["yield_strength"]

        inputs = {
            "stress_amplitude": stress_amplitude,
            "mean_stress": mean_stress,
            "endurance_limit": endurance_limit,
            "yield_strength": yield_strength,
        }

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(endurance_limit, "endurance_limit")
        pos_validator.validate(yield_strength, "yield_strength")

        # Convert to consistent units
        sigma_a = stress_amplitude.to("Pa")
        sigma_m = mean_stress.to("Pa")
        Se = endurance_limit.to("Pa")
        Sy = yield_strength.to("Pa")

        # Calculate amplitude term: sigma_a / Se
        amplitude_term = sigma_a.magnitude / Se.magnitude
        self.add_step(
            description="Calculate amplitude term (sigma_a / Se)",
            formula="amplitude_term = sigma_a / Se",
            result=Quantity(amplitude_term, "dimensionless"),
            substitution=f"amplitude_term = {sigma_a} / {Se} = {amplitude_term:.6g}",
        )

        # Calculate mean term: sigma_m / Sy
        mean_term = sigma_m.magnitude / Sy.magnitude
        self.add_step(
            description="Calculate mean term (sigma_m / Sy)",
            formula="mean_term = sigma_m / Sy",
            result=Quantity(mean_term, "dimensionless"),
            substitution=f"mean_term = {sigma_m} / {Sy} = {mean_term:.6g}",
        )

        # Calculate Soderberg sum
        soderberg_sum = amplitude_term + mean_term
        self.add_step(
            description="Calculate Soderberg sum",
            formula="Soderberg_sum = sigma_a/Se + sigma_m/Sy",
            result=Quantity(soderberg_sum, "dimensionless"),
            substitution=f"Soderberg_sum = {amplitude_term:.6g} + {mean_term:.6g} = {soderberg_sum:.6g}",
        )

        # Calculate safety factor: n = 1 / Soderberg_sum
        if soderberg_sum <= 0:
            raise ValidationError(
                "stress_amplitude",
                "Soderberg sum must be positive for valid safety factor calculation"
            )

        n = 1.0 / soderberg_sum
        safety_factor = Quantity(n, "dimensionless")
        self.add_step(
            description="Calculate safety factor",
            formula="n = 1 / (sigma_a/Se + sigma_m/Sy)",
            result=safety_factor,
            substitution=f"n = 1 / {soderberg_sum:.6g} = {n:.4g}",
        )

        outputs = {
            "safety_factor": safety_factor,
        }

        result = self.format_result(inputs=inputs, outputs=outputs)

        # Add warning for unsafe design
        if n < 1.0:
            result.metadata["warning"] = "WARNING: Safety factor < 1.0 indicates potential fatigue failure!"
        elif n < 1.5:
            result.metadata["warning"] = "CAUTION: Safety factor < 1.5 may be inadequate for some applications."

        return result


@register
class EnduranceLimitEstimate(Calculation):
    """
    Estimate the corrected endurance limit for steel.

    The rotating-beam endurance limit is estimated from ultimate tensile
    strength and then corrected using various modification factors.

    Formulas:
        Se' = 0.5 * Sut  (for Sut <= 1400 MPa)
        Se' = 700 MPa    (for Sut > 1400 MPa)
        Se = Se' * ka * kb * kc

    Where:
        Se = corrected endurance limit (Pa)
        Se' = uncorrected endurance limit (Pa)
        Sut = ultimate tensile strength (Pa)
        ka = surface factor (dimensionless)
        kb = size factor (dimensionless)
        kc = reliability factor (dimensionless)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Norton, R.L., "Machine Design", 5th Ed., Ch. 6
    """

    name = "Endurance Limit Estimate"
    category = "Fatigue"
    description = (
        "Estimate the corrected endurance limit for steel using Marin factors "
        "for surface finish, size, and reliability."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Norton, R.L., 'Machine Design', 5th Ed., Ch. 6",
    ]

    input_params = [
        Parameter("ultimate_strength", "Pa", "Ultimate tensile strength"),
        Parameter("surface_factor", "dimensionless", "Surface finish factor (ka)", default=1.0),
        Parameter("size_factor", "dimensionless", "Size factor (kb)", default=1.0),
        Parameter("reliability_factor", "dimensionless", "Reliability factor (kc)", default=1.0),
    ]
    output_params = [
        Parameter("endurance_limit", "Pa", "Corrected endurance limit (Se)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Estimate corrected endurance limit for steel.

        Args:
            ultimate_strength: Ultimate tensile strength as Quantity (Pa).
            surface_factor: Surface finish modification factor (dimensionless).
            size_factor: Size modification factor (dimensionless).
            reliability_factor: Reliability modification factor (dimensionless).

        Returns:
            CalculationResult with corrected endurance limit.

        Raises:
            ValidationError: If ultimate_strength is not positive or factors are not in valid range.
        """
        self.reset()

        ultimate_strength: Quantity = kwargs["ultimate_strength"]
        surface_factor: Quantity = kwargs.get("surface_factor", Quantity(1.0, "dimensionless"))
        size_factor: Quantity = kwargs.get("size_factor", Quantity(1.0, "dimensionless"))
        reliability_factor: Quantity = kwargs.get("reliability_factor", Quantity(1.0, "dimensionless"))

        # Handle raw floats
        if not hasattr(surface_factor, 'magnitude'):
            surface_factor = Quantity(float(surface_factor), "dimensionless")
        if not hasattr(size_factor, 'magnitude'):
            size_factor = Quantity(float(size_factor), "dimensionless")
        if not hasattr(reliability_factor, 'magnitude'):
            reliability_factor = Quantity(float(reliability_factor), "dimensionless")

        inputs = {
            "ultimate_strength": ultimate_strength,
            "surface_factor": surface_factor,
            "size_factor": size_factor,
            "reliability_factor": reliability_factor,
        }

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(ultimate_strength, "ultimate_strength")

        range_validator = RangeValidator(0.0, 1.0)
        range_validator.validate(surface_factor, "surface_factor")
        range_validator.validate(size_factor, "size_factor")
        range_validator.validate(reliability_factor, "reliability_factor")

        # Convert to consistent units
        Sut = ultimate_strength.to("Pa")
        ka = surface_factor.magnitude
        kb = size_factor.magnitude
        kc = reliability_factor.magnitude

        # Calculate uncorrected endurance limit
        # Threshold is 1400 MPa = 1.4e9 Pa
        threshold = 1.4e9  # Pa
        if Sut.magnitude <= threshold:
            Se_prime_value = 0.5 * Sut.magnitude
            self.add_step(
                description="Calculate uncorrected endurance limit (Sut <= 1400 MPa)",
                formula="Se' = 0.5 * Sut",
                result=Quantity(Se_prime_value, "Pa"),
                substitution=f"Se' = 0.5 * {Sut} = {Se_prime_value:.4g} Pa",
            )
        else:
            Se_prime_value = 700e6  # 700 MPa in Pa
            self.add_step(
                description="Calculate uncorrected endurance limit (Sut > 1400 MPa)",
                formula="Se' = 700 MPa (cap for high-strength steel)",
                result=Quantity(Se_prime_value, "Pa"),
                substitution=f"Se' = 700 MPa = {Se_prime_value:.4g} Pa (Sut = {Sut} exceeds 1400 MPa)",
            )

        # Calculate combined modification factor
        combined_factor = ka * kb * kc
        self.add_step(
            description="Calculate combined modification factor",
            formula="k = ka * kb * kc",
            result=Quantity(combined_factor, "dimensionless"),
            substitution=f"k = {ka:.4g} * {kb:.4g} * {kc:.4g} = {combined_factor:.4g}",
        )

        # Calculate corrected endurance limit
        Se_value = Se_prime_value * combined_factor
        endurance_limit = Quantity(Se_value, "Pa")
        self.add_step(
            description="Calculate corrected endurance limit",
            formula="Se = Se' * ka * kb * kc",
            result=endurance_limit,
            substitution=f"Se = {Se_prime_value:.4g} * {combined_factor:.4g} = {Se_value:.4g} Pa",
        )

        outputs = {
            "endurance_limit": endurance_limit,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class StressConcentrationFatigue(Calculation):
    """
    Calculate fatigue stress concentration factor from geometric stress
    concentration and notch sensitivity.

    The fatigue stress concentration factor (Kf) is less than the geometric
    factor (Kt) due to the notch sensitivity of the material.

    Formula:
        Kf = 1 + q * (Kt - 1)

    Where:
        Kf = fatigue stress concentration factor (dimensionless)
        Kt = geometric stress concentration factor (dimensionless)
        q = notch sensitivity (dimensionless, 0 <= q <= 1)

    Note:
        - When q = 0, Kf = 1 (full notch insensitivity)
        - When q = 1, Kf = Kt (full notch sensitivity)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 6
        - Peterson, R.E., "Stress Concentration Factors", 2nd Ed.
    """

    name = "Fatigue Stress Concentration Factor"
    category = "Fatigue"
    description = (
        "Calculate the fatigue stress concentration factor (Kf) from geometric "
        "stress concentration factor (Kt) and notch sensitivity (q)."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 6",
        "Peterson, R.E., 'Stress Concentration Factors', 2nd Ed.",
    ]

    input_params = [
        Parameter("stress_concentration_factor", "dimensionless", "Geometric stress concentration factor (Kt)"),
        Parameter("notch_sensitivity", "dimensionless", "Notch sensitivity (q, range 0 to 1)"),
    ]
    output_params = [
        Parameter("fatigue_stress_concentration", "dimensionless", "Fatigue stress concentration factor (Kf)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate fatigue stress concentration factor.

        Args:
            stress_concentration_factor: Geometric Kt as Quantity (dimensionless).
            notch_sensitivity: Notch sensitivity q as Quantity (dimensionless).

        Returns:
            CalculationResult with fatigue stress concentration factor.

        Raises:
            ValidationError: If notch_sensitivity is not in range [0, 1] or Kt < 1.
        """
        self.reset()

        stress_concentration_factor: Quantity = kwargs["stress_concentration_factor"]
        notch_sensitivity: Quantity = kwargs["notch_sensitivity"]

        inputs = {
            "stress_concentration_factor": stress_concentration_factor,
            "notch_sensitivity": notch_sensitivity,
        }

        # Validate inputs
        range_validator_q = RangeValidator(0.0, 1.0)
        range_validator_q.validate(notch_sensitivity, "notch_sensitivity")

        range_validator_kt = RangeValidator(1.0, None)
        range_validator_kt.validate(stress_concentration_factor, "stress_concentration_factor")

        # Extract magnitudes
        Kt = stress_concentration_factor.magnitude
        q = notch_sensitivity.magnitude

        # Calculate (Kt - 1)
        kt_minus_1 = Kt - 1.0
        self.add_step(
            description="Calculate (Kt - 1)",
            formula="(Kt - 1)",
            result=Quantity(kt_minus_1, "dimensionless"),
            substitution=f"(Kt - 1) = ({Kt:.4g} - 1) = {kt_minus_1:.4g}",
        )

        # Calculate q * (Kt - 1)
        q_term = q * kt_minus_1
        self.add_step(
            description="Calculate q * (Kt - 1)",
            formula="q * (Kt - 1)",
            result=Quantity(q_term, "dimensionless"),
            substitution=f"q * (Kt - 1) = {q:.4g} * {kt_minus_1:.4g} = {q_term:.4g}",
        )

        # Calculate Kf = 1 + q * (Kt - 1)
        Kf_value = 1.0 + q_term
        fatigue_stress_concentration = Quantity(Kf_value, "dimensionless")
        self.add_step(
            description="Calculate fatigue stress concentration factor",
            formula="Kf = 1 + q * (Kt - 1)",
            result=fatigue_stress_concentration,
            substitution=f"Kf = 1 + {q_term:.4g} = {Kf_value:.4g}",
        )

        outputs = {
            "fatigue_stress_concentration": fatigue_stress_concentration,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "StressAmplitude",
    "SNCurveLife",
    "MinersRule",
    "GoodmanDiagram",
    "GerberCriterion",
    "SoderbergCriterion",
    "EnduranceLimitEstimate",
    "StressConcentrationFatigue",
]
