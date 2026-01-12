"""
Vibration analysis calculations for Engineering Calculations Database.

This module provides engineering calculations for mechanical vibrations including:
- Natural frequency (undamped and damped)
- Damping ratio and critical damping
- Logarithmic decrement
- Magnification factor (frequency response)
- Transmissibility
- Rotating imbalance response
- Critical speed of rotating shafts
"""

from __future__ import annotations

import math
from typing import Any, Optional

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


@register
class NaturalFrequency(Calculation):
    """
    Calculate the natural frequency of an undamped single-degree-of-freedom system.

    Formulas:
        omega_n = sqrt(k / m)  [rad/s]
        f_n = omega_n / (2 * pi)  [Hz]

    Where:
        omega_n = natural frequency in rad/s
        f_n = natural frequency in Hz
        k = stiffness (N/m)
        m = mass (kg)
    """

    name = "Natural Frequency"
    category = "Vibrations"
    description = (
        "Calculate the natural frequency of an undamped single-degree-of-freedom "
        "system. omega_n = sqrt(k/m), f_n = omega_n/(2*pi)"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("stiffness", "N/m", "Spring stiffness"),
        Parameter("mass", "kg", "System mass"),
    ]
    output_params = [
        Parameter("natural_freq_rad", "rad/s", "Natural frequency in radians per second"),
        Parameter("natural_freq_hz", "Hz", "Natural frequency in Hertz"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate natural frequency.

        Args:
            stiffness: Spring stiffness as Quantity (N/m).
            mass: System mass as Quantity (kg).

        Returns:
            CalculationResult with natural frequency in rad/s and Hz.
        """
        self.reset()

        stiffness: Quantity = kwargs["stiffness"]
        mass: Quantity = kwargs["mass"]

        inputs = {
            "stiffness": stiffness,
            "mass": mass,
        }

        # Calculate k/m ratio
        k_over_m = stiffness / mass
        self.add_step(
            description="Calculate stiffness to mass ratio",
            formula="k/m",
            result=k_over_m,
            substitution=f"k/m = {stiffness} / {mass} = {k_over_m}",
        )

        # Calculate omega_n = sqrt(k/m)
        # Need to convert to base units and extract magnitude for sqrt
        k_over_m_base = k_over_m.to_base_units()
        omega_n_magnitude = math.sqrt(k_over_m_base.magnitude)
        natural_freq_rad = Quantity(omega_n_magnitude, "rad/s")

        self.add_step(
            description="Calculate natural frequency in rad/s",
            formula="omega_n = sqrt(k/m)",
            result=natural_freq_rad,
            substitution=f"omega_n = sqrt({k_over_m}) = {natural_freq_rad}",
        )

        # Calculate f_n = omega_n / (2*pi)
        natural_freq_hz = Quantity(omega_n_magnitude / (2 * math.pi), "Hz")

        self.add_step(
            description="Calculate natural frequency in Hz",
            formula="f_n = omega_n / (2*pi)",
            result=natural_freq_hz,
            substitution=f"f_n = {natural_freq_rad} / (2*pi) = {natural_freq_hz}",
        )

        outputs = {
            "natural_freq_rad": natural_freq_rad,
            "natural_freq_hz": natural_freq_hz,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class DampingRatio(Calculation):
    """
    Calculate the damping ratio of a viscously damped system.

    Formulas:
        c_c = 2 * sqrt(k * m)  (critical damping)
        zeta = c / c_c = c / (2 * sqrt(k * m))

    Where:
        zeta = damping ratio (dimensionless)
        c = damping coefficient (N*s/m)
        c_c = critical damping coefficient (N*s/m)
        k = stiffness (N/m)
        m = mass (kg)

    Classification:
        zeta < 1: underdamped
        zeta = 1: critically damped
        zeta > 1: overdamped
    """

    name = "Damping Ratio"
    category = "Vibrations"
    description = (
        "Calculate the damping ratio and critical damping coefficient. "
        "zeta = c / (2*sqrt(k*m))"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("damping_coefficient", "N*s/m", "Viscous damping coefficient"),
        Parameter("stiffness", "N/m", "Spring stiffness"),
        Parameter("mass", "kg", "System mass"),
    ]
    output_params = [
        Parameter("damping_ratio", "dimensionless", "Damping ratio (zeta)"),
        Parameter("critical_damping", "N*s/m", "Critical damping coefficient"),
        Parameter("damping_type", "dimensionless", "Damping classification"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate damping ratio.

        Args:
            damping_coefficient: Viscous damping as Quantity (N*s/m).
            stiffness: Spring stiffness as Quantity (N/m).
            mass: System mass as Quantity (kg).

        Returns:
            CalculationResult with damping ratio, critical damping, and damping type.
        """
        self.reset()

        damping_coefficient: Quantity = kwargs["damping_coefficient"]
        stiffness: Quantity = kwargs["stiffness"]
        mass: Quantity = kwargs["mass"]

        inputs = {
            "damping_coefficient": damping_coefficient,
            "stiffness": stiffness,
            "mass": mass,
        }

        # Calculate k*m product
        k_times_m = stiffness * mass
        self.add_step(
            description="Calculate stiffness times mass",
            formula="k * m",
            result=k_times_m,
            substitution=f"k * m = {stiffness} * {mass} = {k_times_m}",
        )

        # Calculate sqrt(k*m)
        k_times_m_base = k_times_m.to_base_units()
        sqrt_km = math.sqrt(k_times_m_base.magnitude)

        self.add_step(
            description="Calculate square root of (k*m)",
            formula="sqrt(k*m)",
            result=sqrt_km,
            substitution=f"sqrt({k_times_m}) = {sqrt_km:.4f} kg/s",
        )

        # Calculate critical damping: c_c = 2*sqrt(k*m)
        critical_damping_magnitude = 2 * sqrt_km
        critical_damping = Quantity(critical_damping_magnitude, "N*s/m")

        self.add_step(
            description="Calculate critical damping coefficient",
            formula="c_c = 2 * sqrt(k * m)",
            result=critical_damping,
            substitution=f"c_c = 2 * {sqrt_km:.4f} = {critical_damping}",
        )

        # Calculate damping ratio: zeta = c / c_c
        c_base = damping_coefficient.to_base_units()
        damping_ratio_magnitude = c_base.magnitude / critical_damping_magnitude
        damping_ratio = Quantity(damping_ratio_magnitude, "dimensionless")

        self.add_step(
            description="Calculate damping ratio",
            formula="zeta = c / c_c",
            result=damping_ratio,
            substitution=f"zeta = {damping_coefficient} / {critical_damping} = {damping_ratio}",
        )

        # Determine damping type
        if damping_ratio_magnitude < 0.999:
            damping_type_str = "underdamped"
        elif damping_ratio_magnitude > 1.001:
            damping_type_str = "overdamped"
        else:
            damping_type_str = "critically damped"

        self.add_step(
            description="Classify damping type",
            formula="zeta < 1: underdamped, zeta = 1: critically damped, zeta > 1: overdamped",
            result=damping_type_str,
            substitution=f"zeta = {damping_ratio_magnitude:.4f} -> {damping_type_str}",
        )

        outputs = {
            "damping_ratio": damping_ratio,
            "critical_damping": critical_damping,
            "damping_type": damping_type_str,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class DampedNaturalFrequency(Calculation):
    """
    Calculate the damped natural frequency of an underdamped system.

    Formula:
        omega_d = omega_n * sqrt(1 - zeta^2)

    Where:
        omega_d = damped natural frequency (rad/s)
        omega_n = undamped natural frequency (rad/s)
        zeta = damping ratio (dimensionless, must be < 1)

    Note: This calculation is only valid for underdamped systems (zeta < 1).
    """

    name = "Damped Natural Frequency"
    category = "Vibrations"
    description = (
        "Calculate the damped natural frequency for an underdamped system. "
        "omega_d = omega_n * sqrt(1 - zeta^2)"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("natural_freq_rad", "rad/s", "Undamped natural frequency"),
        Parameter("damping_ratio", "dimensionless", "Damping ratio (must be < 1)"),
    ]
    output_params = [
        Parameter("damped_freq_rad", "rad/s", "Damped natural frequency in rad/s"),
        Parameter("damped_freq_hz", "Hz", "Damped natural frequency in Hz"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate damped natural frequency.

        Args:
            natural_freq_rad: Undamped natural frequency as Quantity (rad/s).
            damping_ratio: Damping ratio as Quantity (dimensionless).

        Returns:
            CalculationResult with damped natural frequency.

        Raises:
            ValueError: If damping ratio >= 1 (overdamped or critically damped).
        """
        self.reset()

        natural_freq_rad: Quantity = kwargs["natural_freq_rad"]
        damping_ratio: Quantity = kwargs["damping_ratio"]

        inputs = {
            "natural_freq_rad": natural_freq_rad,
            "damping_ratio": damping_ratio,
        }

        # Extract magnitudes
        omega_n = natural_freq_rad.magnitude
        zeta = damping_ratio.magnitude

        # Validate damping ratio
        if zeta >= 1.0:
            raise ValueError(
                f"Damping ratio must be less than 1 for damped natural frequency "
                f"calculation. Got zeta = {zeta}"
            )

        # Calculate 1 - zeta^2
        zeta_squared = zeta ** 2
        one_minus_zeta_sq = 1 - zeta_squared

        self.add_step(
            description="Calculate (1 - zeta^2)",
            formula="1 - zeta^2",
            result=one_minus_zeta_sq,
            substitution=f"1 - ({zeta})^2 = 1 - {zeta_squared:.6f} = {one_minus_zeta_sq:.6f}",
        )

        # Calculate sqrt(1 - zeta^2)
        sqrt_term = math.sqrt(one_minus_zeta_sq)

        self.add_step(
            description="Calculate sqrt(1 - zeta^2)",
            formula="sqrt(1 - zeta^2)",
            result=sqrt_term,
            substitution=f"sqrt({one_minus_zeta_sq:.6f}) = {sqrt_term:.6f}",
        )

        # Calculate omega_d = omega_n * sqrt(1 - zeta^2)
        omega_d = omega_n * sqrt_term
        damped_freq_rad = Quantity(omega_d, "rad/s")

        self.add_step(
            description="Calculate damped natural frequency",
            formula="omega_d = omega_n * sqrt(1 - zeta^2)",
            result=damped_freq_rad,
            substitution=f"omega_d = {natural_freq_rad} * {sqrt_term:.6f} = {damped_freq_rad}",
        )

        # Calculate frequency in Hz
        damped_freq_hz = Quantity(omega_d / (2 * math.pi), "Hz")

        self.add_step(
            description="Convert to Hz",
            formula="f_d = omega_d / (2*pi)",
            result=damped_freq_hz,
            substitution=f"f_d = {damped_freq_rad} / (2*pi) = {damped_freq_hz}",
        )

        outputs = {
            "damped_freq_rad": damped_freq_rad,
            "damped_freq_hz": damped_freq_hz,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class LogarithmicDecrement(Calculation):
    """
    Calculate the logarithmic decrement from consecutive peak amplitudes.

    Formulas:
        delta = ln(x1 / x2)
        zeta = delta / sqrt(4*pi^2 + delta^2)

    Where:
        delta = logarithmic decrement (dimensionless)
        x1 = amplitude of first peak (m)
        x2 = amplitude of second consecutive peak (m)
        zeta = damping ratio (dimensionless)

    Note: x1 and x2 must be consecutive peaks in a free vibration response.
    """

    name = "Logarithmic Decrement"
    category = "Vibrations"
    description = (
        "Calculate the logarithmic decrement and damping ratio from "
        "consecutive peak amplitudes. delta = ln(x1/x2)"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("amplitude_1", "m", "Amplitude of first peak"),
        Parameter("amplitude_2", "m", "Amplitude of second consecutive peak"),
    ]
    output_params = [
        Parameter("log_decrement", "dimensionless", "Logarithmic decrement"),
        Parameter("damping_ratio", "dimensionless", "Calculated damping ratio"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate logarithmic decrement and damping ratio.

        Args:
            amplitude_1: First peak amplitude as Quantity (m).
            amplitude_2: Second consecutive peak amplitude as Quantity (m).

        Returns:
            CalculationResult with logarithmic decrement and damping ratio.

        Raises:
            ValueError: If amplitudes are not positive or x2 >= x1.
        """
        self.reset()

        amplitude_1: Quantity = kwargs["amplitude_1"]
        amplitude_2: Quantity = kwargs["amplitude_2"]

        inputs = {
            "amplitude_1": amplitude_1,
            "amplitude_2": amplitude_2,
        }

        # Extract magnitudes (convert to same units first)
        x1 = amplitude_1.magnitude
        x2 = amplitude_2.to(amplitude_1.unit_string).magnitude

        # Validate amplitudes
        if x1 <= 0 or x2 <= 0:
            raise ValueError("Amplitudes must be positive values")
        if x2 >= x1:
            raise ValueError(
                "First amplitude must be greater than second amplitude for decaying vibration"
            )

        # Calculate amplitude ratio
        ratio = x1 / x2

        self.add_step(
            description="Calculate amplitude ratio",
            formula="x1 / x2",
            result=ratio,
            substitution=f"x1/x2 = {amplitude_1} / {amplitude_2} = {ratio:.6f}",
        )

        # Calculate logarithmic decrement: delta = ln(x1/x2)
        delta = math.log(ratio)
        log_decrement = Quantity(delta, "dimensionless")

        self.add_step(
            description="Calculate logarithmic decrement",
            formula="delta = ln(x1/x2)",
            result=log_decrement,
            substitution=f"delta = ln({ratio:.6f}) = {log_decrement}",
        )

        # Calculate damping ratio: zeta = delta / sqrt(4*pi^2 + delta^2)
        four_pi_sq = 4 * math.pi ** 2
        delta_squared = delta ** 2
        denominator = math.sqrt(four_pi_sq + delta_squared)
        zeta = delta / denominator
        damping_ratio = Quantity(zeta, "dimensionless")

        self.add_step(
            description="Calculate damping ratio from logarithmic decrement",
            formula="zeta = delta / sqrt(4*pi^2 + delta^2)",
            result=damping_ratio,
            substitution=f"zeta = {delta:.6f} / sqrt({four_pi_sq:.4f} + {delta_squared:.6f}) = {damping_ratio}",
        )

        outputs = {
            "log_decrement": log_decrement,
            "damping_ratio": damping_ratio,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class MagnificationFactor(Calculation):
    """
    Calculate the magnification factor (dynamic amplification factor) for forced vibration.

    Formulas:
        M = 1 / sqrt((1 - r^2)^2 + (2*zeta*r)^2)
        phi = atan2(2*zeta*r, 1 - r^2)

    Where:
        M = magnification factor (dimensionless)
        phi = phase angle (rad)
        r = frequency ratio = omega/omega_n (dimensionless)
        zeta = damping ratio (dimensionless)

    The magnification factor represents the ratio of dynamic displacement
    amplitude to static displacement under the same force.
    """

    name = "Magnification Factor"
    category = "Vibrations"
    description = (
        "Calculate the magnification factor and phase angle for forced vibration. "
        "M = 1 / sqrt((1-r^2)^2 + (2*zeta*r)^2)"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("frequency_ratio", "dimensionless", "Frequency ratio (omega/omega_n)"),
        Parameter("damping_ratio", "dimensionless", "Damping ratio"),
    ]
    output_params = [
        Parameter("magnification_factor", "dimensionless", "Magnification factor"),
        Parameter("phase_angle", "rad", "Phase angle"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate magnification factor and phase angle.

        Args:
            frequency_ratio: Frequency ratio as Quantity (dimensionless).
            damping_ratio: Damping ratio as Quantity (dimensionless).

        Returns:
            CalculationResult with magnification factor and phase angle.
        """
        self.reset()

        frequency_ratio: Quantity = kwargs["frequency_ratio"]
        damping_ratio: Quantity = kwargs["damping_ratio"]

        inputs = {
            "frequency_ratio": frequency_ratio,
            "damping_ratio": damping_ratio,
        }

        # Extract magnitudes
        r = frequency_ratio.magnitude
        zeta = damping_ratio.magnitude

        # Calculate (1 - r^2)
        r_squared = r ** 2
        one_minus_r_sq = 1 - r_squared

        self.add_step(
            description="Calculate (1 - r^2)",
            formula="1 - r^2",
            result=one_minus_r_sq,
            substitution=f"1 - ({r})^2 = {one_minus_r_sq:.6f}",
        )

        # Calculate 2*zeta*r
        two_zeta_r = 2 * zeta * r

        self.add_step(
            description="Calculate 2*zeta*r",
            formula="2*zeta*r",
            result=two_zeta_r,
            substitution=f"2 * {zeta} * {r} = {two_zeta_r:.6f}",
        )

        # Calculate denominator: sqrt((1-r^2)^2 + (2*zeta*r)^2)
        term1 = one_minus_r_sq ** 2
        term2 = two_zeta_r ** 2
        denominator = math.sqrt(term1 + term2)

        self.add_step(
            description="Calculate denominator sqrt((1-r^2)^2 + (2*zeta*r)^2)",
            formula="sqrt((1-r^2)^2 + (2*zeta*r)^2)",
            result=denominator,
            substitution=f"sqrt({term1:.6f} + {term2:.6f}) = {denominator:.6f}",
        )

        # Calculate magnification factor: M = 1 / denominator
        M = 1 / denominator if denominator != 0 else float('inf')
        magnification_factor = Quantity(M, "dimensionless")

        self.add_step(
            description="Calculate magnification factor",
            formula="M = 1 / sqrt((1-r^2)^2 + (2*zeta*r)^2)",
            result=magnification_factor,
            substitution=f"M = 1 / {denominator:.6f} = {magnification_factor}",
        )

        # Calculate phase angle: phi = atan2(2*zeta*r, 1 - r^2)
        phi = math.atan2(two_zeta_r, one_minus_r_sq)
        phase_angle = Quantity(phi, "rad")

        self.add_step(
            description="Calculate phase angle",
            formula="phi = atan2(2*zeta*r, 1 - r^2)",
            result=phase_angle,
            substitution=f"phi = atan2({two_zeta_r:.6f}, {one_minus_r_sq:.6f}) = {phase_angle}",
        )

        outputs = {
            "magnification_factor": magnification_factor,
            "phase_angle": phase_angle,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class Transmissibility(Calculation):
    """
    Calculate the force or motion transmissibility.

    Formula:
        TR = sqrt((1 + (2*zeta*r)^2) / ((1-r^2)^2 + (2*zeta*r)^2))

    Where:
        TR = transmissibility (dimensionless)
        r = frequency ratio = omega/omega_n (dimensionless)
        zeta = damping ratio (dimensionless)

    Transmissibility represents the ratio of transmitted force (or motion)
    to applied force (or base motion).
    """

    name = "Transmissibility"
    category = "Vibrations"
    description = (
        "Calculate force or motion transmissibility. "
        "TR = sqrt((1 + (2*zeta*r)^2) / ((1-r^2)^2 + (2*zeta*r)^2))"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("frequency_ratio", "dimensionless", "Frequency ratio (omega/omega_n)"),
        Parameter("damping_ratio", "dimensionless", "Damping ratio"),
    ]
    output_params = [
        Parameter("transmissibility", "dimensionless", "Transmissibility"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate transmissibility.

        Args:
            frequency_ratio: Frequency ratio as Quantity (dimensionless).
            damping_ratio: Damping ratio as Quantity (dimensionless).

        Returns:
            CalculationResult with transmissibility.
        """
        self.reset()

        frequency_ratio: Quantity = kwargs["frequency_ratio"]
        damping_ratio: Quantity = kwargs["damping_ratio"]

        inputs = {
            "frequency_ratio": frequency_ratio,
            "damping_ratio": damping_ratio,
        }

        # Extract magnitudes
        r = frequency_ratio.magnitude
        zeta = damping_ratio.magnitude

        # Calculate common terms
        r_squared = r ** 2
        one_minus_r_sq = 1 - r_squared
        two_zeta_r = 2 * zeta * r
        two_zeta_r_sq = two_zeta_r ** 2

        self.add_step(
            description="Calculate (2*zeta*r)^2",
            formula="(2*zeta*r)^2",
            result=two_zeta_r_sq,
            substitution=f"(2 * {zeta} * {r})^2 = {two_zeta_r_sq:.6f}",
        )

        # Calculate numerator: 1 + (2*zeta*r)^2
        numerator = 1 + two_zeta_r_sq

        self.add_step(
            description="Calculate numerator: 1 + (2*zeta*r)^2",
            formula="1 + (2*zeta*r)^2",
            result=numerator,
            substitution=f"1 + {two_zeta_r_sq:.6f} = {numerator:.6f}",
        )

        # Calculate denominator: (1-r^2)^2 + (2*zeta*r)^2
        denominator = one_minus_r_sq ** 2 + two_zeta_r_sq

        self.add_step(
            description="Calculate denominator: (1-r^2)^2 + (2*zeta*r)^2",
            formula="(1-r^2)^2 + (2*zeta*r)^2",
            result=denominator,
            substitution=f"({one_minus_r_sq:.6f})^2 + {two_zeta_r_sq:.6f} = {denominator:.6f}",
        )

        # Calculate transmissibility: TR = sqrt(numerator / denominator)
        TR = math.sqrt(numerator / denominator) if denominator != 0 else float('inf')
        transmissibility = Quantity(TR, "dimensionless")

        self.add_step(
            description="Calculate transmissibility",
            formula="TR = sqrt((1 + (2*zeta*r)^2) / ((1-r^2)^2 + (2*zeta*r)^2))",
            result=transmissibility,
            substitution=f"TR = sqrt({numerator:.6f} / {denominator:.6f}) = {transmissibility}",
        )

        outputs = {
            "transmissibility": transmissibility,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class RotatingImbalanceResponse(Calculation):
    """
    Calculate the steady-state response amplitude due to rotating imbalance.

    Formula:
        X = (m_u * e * r^2) / (m * sqrt((1-r^2)^2 + (2*zeta*r)^2))

    Where:
        X = displacement amplitude (m)
        m_u = unbalance mass (kg)
        e = eccentricity (m)
        m = total mass of system (kg)
        r = frequency ratio = omega/omega_n (dimensionless)
        zeta = damping ratio (dimensionless)

    The frequency ratio r is calculated from:
        r = omega / omega_n = omega / sqrt(k/m)
    """

    name = "Rotating Imbalance Response"
    category = "Vibrations"
    description = (
        "Calculate steady-state displacement amplitude due to rotating imbalance. "
        "X = (m_u * e * r^2) / (m * sqrt((1-r^2)^2 + (2*zeta*r)^2))"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Engineering Vibration, Inman",
    ]

    input_params = [
        Parameter("unbalance_mass", "kg", "Unbalance mass"),
        Parameter("eccentricity", "m", "Eccentricity of unbalance mass"),
        Parameter("total_mass", "kg", "Total mass of the system"),
        Parameter("stiffness", "N/m", "Spring stiffness"),
        Parameter("operating_freq", "rad/s", "Operating frequency"),
        Parameter("damping_ratio", "dimensionless", "Damping ratio"),
    ]
    output_params = [
        Parameter("displacement_amplitude", "m", "Steady-state displacement amplitude"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate rotating imbalance response.

        Args:
            unbalance_mass: Unbalance mass as Quantity (kg).
            eccentricity: Eccentricity as Quantity (m).
            total_mass: Total system mass as Quantity (kg).
            stiffness: Spring stiffness as Quantity (N/m).
            operating_freq: Operating frequency as Quantity (rad/s).
            damping_ratio: Damping ratio as Quantity (dimensionless).

        Returns:
            CalculationResult with displacement amplitude.
        """
        self.reset()

        unbalance_mass: Quantity = kwargs["unbalance_mass"]
        eccentricity: Quantity = kwargs["eccentricity"]
        total_mass: Quantity = kwargs["total_mass"]
        stiffness: Quantity = kwargs["stiffness"]
        operating_freq: Quantity = kwargs["operating_freq"]
        damping_ratio: Quantity = kwargs["damping_ratio"]

        inputs = {
            "unbalance_mass": unbalance_mass,
            "eccentricity": eccentricity,
            "total_mass": total_mass,
            "stiffness": stiffness,
            "operating_freq": operating_freq,
            "damping_ratio": damping_ratio,
        }

        # Extract magnitudes
        m_u = unbalance_mass.magnitude
        e = eccentricity.magnitude
        m = total_mass.magnitude
        k = stiffness.to_base_units().magnitude
        omega = operating_freq.magnitude
        zeta = damping_ratio.magnitude

        # Calculate natural frequency
        omega_n = math.sqrt(k / m)

        self.add_step(
            description="Calculate natural frequency",
            formula="omega_n = sqrt(k/m)",
            result=omega_n,
            substitution=f"omega_n = sqrt({stiffness}/{total_mass}) = {omega_n:.4f} rad/s",
        )

        # Calculate frequency ratio
        r = omega / omega_n

        self.add_step(
            description="Calculate frequency ratio",
            formula="r = omega / omega_n",
            result=r,
            substitution=f"r = {operating_freq} / {omega_n:.4f} = {r:.6f}",
        )

        # Calculate r^2
        r_squared = r ** 2

        self.add_step(
            description="Calculate r^2",
            formula="r^2",
            result=r_squared,
            substitution=f"r^2 = ({r:.6f})^2 = {r_squared:.6f}",
        )

        # Calculate numerator: m_u * e * r^2
        numerator = m_u * e * r_squared

        self.add_step(
            description="Calculate numerator (m_u * e * r^2)",
            formula="m_u * e * r^2",
            result=numerator,
            substitution=f"{unbalance_mass} * {eccentricity} * {r_squared:.6f} = {numerator:.6f} kg*m",
        )

        # Calculate denominator terms
        one_minus_r_sq = 1 - r_squared
        two_zeta_r = 2 * zeta * r
        denom_sqrt = math.sqrt(one_minus_r_sq ** 2 + two_zeta_r ** 2)
        denominator = m * denom_sqrt

        self.add_step(
            description="Calculate denominator (m * sqrt((1-r^2)^2 + (2*zeta*r)^2))",
            formula="m * sqrt((1-r^2)^2 + (2*zeta*r)^2)",
            result=denominator,
            substitution=f"{total_mass} * sqrt(({one_minus_r_sq:.6f})^2 + ({two_zeta_r:.6f})^2) = {denominator:.6f} kg",
        )

        # Calculate displacement amplitude
        X = numerator / denominator if denominator != 0 else float('inf')
        displacement_amplitude = Quantity(X, "m")

        self.add_step(
            description="Calculate displacement amplitude",
            formula="X = (m_u * e * r^2) / (m * sqrt((1-r^2)^2 + (2*zeta*r)^2))",
            result=displacement_amplitude,
            substitution=f"X = {numerator:.6f} / {denominator:.6f} = {displacement_amplitude}",
        )

        outputs = {
            "displacement_amplitude": displacement_amplitude,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CriticalSpeed(Calculation):
    """
    Calculate the critical speed of a rotating shaft.

    For simple mass on shaft (Method 1):
        omega_cr = sqrt(k/m)
        N_cr = omega_cr * 60 / (2*pi) [rpm]

    For uniform shaft with distributed mass (Method 2):
        k = 48*E*I / L^3 (simply supported)
        I = pi * d^4 / 64 (circular cross-section)
        m = rho * A * L (distributed mass, use equivalent lumped mass)
        omega_cr = sqrt(k / m_eq)

    Where:
        omega_cr = critical speed (rad/s)
        N_cr = critical speed (rpm)
        k = stiffness (N/m)
        m = mass (kg)
        E = elastic modulus (Pa)
        I = moment of inertia (m^4)
        L = shaft length (m)
        d = shaft diameter (m)
        rho = material density (kg/m^3)
    """

    name = "Critical Speed"
    category = "Vibrations"
    description = (
        "Calculate the critical speed of a rotating shaft. "
        "omega_cr = sqrt(k/m), N_cr = omega_cr * 60/(2*pi)"
    )
    references = [
        "Mechanical Vibrations, Rao",
        "Roark's Formulas for Stress and Strain",
    ]

    input_params = [
        Parameter("stiffness", "N/m", "Shaft stiffness (for Method 1)", default=None),
        Parameter("mass", "kg", "Lumped mass (for Method 1)", default=None),
        Parameter("shaft_diameter", "m", "Shaft diameter (for Method 2)", default=None),
        Parameter("length", "m", "Shaft length (for Method 2)", default=None),
        Parameter("elastic_modulus", "Pa", "Elastic modulus (for Method 2)", default=None),
        Parameter("density", "kg/m**3", "Material density (for Method 2)", default=None),
    ]
    output_params = [
        Parameter("critical_speed_rpm", "rpm", "Critical speed in RPM"),
        Parameter("critical_speed_rad", "rad/s", "Critical speed in rad/s"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate critical speed of a rotating shaft.

        Args:
            For Method 1 (simple mass-spring):
                stiffness: Shaft stiffness as Quantity (N/m).
                mass: Lumped mass as Quantity (kg).
            For Method 2 (shaft properties):
                shaft_diameter: Shaft diameter as Quantity (m).
                length: Shaft length as Quantity (m).
                elastic_modulus: Elastic modulus as Quantity (Pa).
                density: Material density as Quantity (kg/m^3).

        Returns:
            CalculationResult with critical speed in rpm and rad/s.

        Raises:
            ValueError: If neither method has complete inputs.
        """
        self.reset()

        stiffness: Optional[Quantity] = kwargs.get("stiffness")
        mass: Optional[Quantity] = kwargs.get("mass")
        shaft_diameter: Optional[Quantity] = kwargs.get("shaft_diameter")
        length: Optional[Quantity] = kwargs.get("length")
        elastic_modulus: Optional[Quantity] = kwargs.get("elastic_modulus")
        density: Optional[Quantity] = kwargs.get("density")

        inputs = {}

        # Determine which method to use
        method_1_complete = stiffness is not None and mass is not None
        method_2_complete = all([
            shaft_diameter is not None,
            length is not None,
            elastic_modulus is not None,
            density is not None,
        ])

        if method_1_complete:
            # Method 1: Simple mass-spring system
            inputs["stiffness"] = stiffness
            inputs["mass"] = mass

            k = stiffness.to_base_units().magnitude
            m = mass.magnitude

            self.add_step(
                description="Using Method 1: Simple mass-spring model",
                formula="omega_cr = sqrt(k/m)",
                result="Direct calculation from stiffness and mass",
                substitution=f"k = {stiffness}, m = {mass}",
            )

        elif method_2_complete:
            # Method 2: Calculate from shaft geometry
            inputs["shaft_diameter"] = shaft_diameter
            inputs["length"] = length
            inputs["elastic_modulus"] = elastic_modulus
            inputs["density"] = density

            d = shaft_diameter.to("m").magnitude
            L = length.to("m").magnitude
            E = elastic_modulus.to_base_units().magnitude
            rho = density.to_base_units().magnitude

            self.add_step(
                description="Using Method 2: Shaft geometry calculation",
                formula="Calculate stiffness and mass from shaft properties",
                result="Simply supported beam with central mass",
                substitution=f"d = {shaft_diameter}, L = {length}, E = {elastic_modulus}, rho = {density}",
            )

            # Calculate moment of inertia: I = pi * d^4 / 64
            I = math.pi * d ** 4 / 64

            self.add_step(
                description="Calculate moment of inertia",
                formula="I = pi * d^4 / 64",
                result=I,
                substitution=f"I = pi * ({d})^4 / 64 = {I:.6e} m^4",
            )

            # Calculate stiffness for simply supported beam: k = 48*E*I / L^3
            k = 48 * E * I / (L ** 3)

            self.add_step(
                description="Calculate shaft stiffness (simply supported, center load)",
                formula="k = 48*E*I / L^3",
                result=k,
                substitution=f"k = 48 * {E:.3e} * {I:.6e} / ({L})^3 = {k:.4e} N/m",
            )

            # Calculate mass: m = rho * A * L (use 0.5 for equivalent lumped mass)
            A = math.pi * d ** 2 / 4
            m = 0.5 * rho * A * L  # Equivalent lumped mass factor for fundamental mode

            self.add_step(
                description="Calculate equivalent lumped mass",
                formula="m_eq = 0.5 * rho * A * L",
                result=m,
                substitution=f"m_eq = 0.5 * {rho} * {A:.6e} * {L} = {m:.4f} kg",
            )

        else:
            raise ValueError(
                "Either provide 'stiffness' and 'mass' (Method 1), OR "
                "'shaft_diameter', 'length', 'elastic_modulus', and 'density' (Method 2)"
            )

        # Calculate k/m ratio
        k_over_m = k / m

        self.add_step(
            description="Calculate stiffness to mass ratio",
            formula="k/m",
            result=k_over_m,
            substitution=f"k/m = {k:.4e} / {m:.4f} = {k_over_m:.4e} (rad/s)^2",
        )

        # Calculate critical speed in rad/s
        omega_cr = math.sqrt(k_over_m)
        critical_speed_rad = Quantity(omega_cr, "rad/s")

        self.add_step(
            description="Calculate critical speed in rad/s",
            formula="omega_cr = sqrt(k/m)",
            result=critical_speed_rad,
            substitution=f"omega_cr = sqrt({k_over_m:.4e}) = {critical_speed_rad}",
        )

        # Convert to RPM: N = omega * 60 / (2*pi)
        N_cr = omega_cr * 60 / (2 * math.pi)
        critical_speed_rpm = Quantity(N_cr, "rpm")

        self.add_step(
            description="Convert to RPM",
            formula="N_cr = omega_cr * 60 / (2*pi)",
            result=critical_speed_rpm,
            substitution=f"N_cr = {omega_cr:.4f} * 60 / (2*pi) = {critical_speed_rpm}",
        )

        outputs = {
            "critical_speed_rpm": critical_speed_rpm,
            "critical_speed_rad": critical_speed_rad,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "NaturalFrequency",
    "DampingRatio",
    "DampedNaturalFrequency",
    "LogarithmicDecrement",
    "MagnificationFactor",
    "Transmissibility",
    "RotatingImbalanceResponse",
    "CriticalSpeed",
]
