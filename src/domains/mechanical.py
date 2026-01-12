"""
Mechanical design calculations for Engineering Calculations Database.

This module provides engineering calculations for mechanical design including:
- Bolt tensile stress and shear capacity
- Bolt preload calculations
- Torsional stress and shaft twist angle
- Bearing life calculations
- Spring rate and deflection
"""

from __future__ import annotations

from typing import Any, Optional

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


@register
class BoltTensileStress(Calculation):
    """
    Calculate tensile stress in a bolt.

    Formula: sigma = F / A_tensile

    Where:
        sigma = tensile stress (Pa)
        F = tensile load (N)
        A_tensile = tensile stress area of bolt (m^2)
    """

    name = "Bolt Tensile Stress"
    category = "Mechanical"
    description = "Calculate the tensile stress in a bolt. sigma = F / A_tensile"
    references = ["Shigley's Mechanical Engineering Design"]

    input_params = [
        Parameter("tensile_load", "N", "Applied tensile load on the bolt"),
        Parameter("tensile_stress_area", "m**2", "Tensile stress area of the bolt"),
    ]
    output_params = [
        Parameter("tensile_stress", "Pa", "Tensile stress in the bolt"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate bolt tensile stress.

        Args:
            tensile_load: Applied tensile load as Quantity (N).
            tensile_stress_area: Tensile stress area as Quantity (m^2).

        Returns:
            CalculationResult with tensile stress output.
        """
        self.reset()

        tensile_load: Quantity = kwargs["tensile_load"]
        tensile_stress_area: Quantity = kwargs["tensile_stress_area"]

        inputs = {
            "tensile_load": tensile_load,
            "tensile_stress_area": tensile_stress_area,
        }

        # Calculate tensile stress: sigma = F / A_tensile
        tensile_stress = tensile_load / tensile_stress_area

        self.add_step(
            description="Calculate tensile stress using sigma = F / A_tensile",
            formula="sigma = F / A_tensile",
            result=tensile_stress,
            substitution=f"sigma = {tensile_load} / {tensile_stress_area} = {tensile_stress}",
        )

        outputs = {
            "tensile_stress": tensile_stress,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class BoltShearCapacity(Calculation):
    """
    Calculate shear stress in bolted connections.

    Formula: tau = V / (n x A_shear)

    Where:
        tau = shear stress (Pa)
        V = shear load (N)
        n = number of bolts
        A_shear = shear area per bolt (m^2)
    """

    name = "Bolt Shear Capacity"
    category = "Mechanical"
    description = "Calculate shear stress in bolted connections. tau = V / (n x A_shear)"
    references = ["Shigley's Mechanical Engineering Design"]

    input_params = [
        Parameter("shear_load", "N", "Applied shear load on the connection"),
        Parameter("num_bolts", "dimensionless", "Number of bolts in the connection"),
        Parameter("shear_area", "m**2", "Shear area per bolt"),
    ]
    output_params = [
        Parameter("shear_stress", "Pa", "Shear stress in the bolts"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate bolt shear stress.

        Args:
            shear_load: Applied shear load as Quantity (N).
            num_bolts: Number of bolts (int or dimensionless Quantity).
            shear_area: Shear area per bolt as Quantity (m^2).

        Returns:
            CalculationResult with shear stress output.
        """
        self.reset()

        shear_load: Quantity = kwargs["shear_load"]
        num_bolts = kwargs["num_bolts"]
        shear_area: Quantity = kwargs["shear_area"]

        # Handle num_bolts as either int or Quantity
        if isinstance(num_bolts, Quantity):
            n = num_bolts.magnitude
        else:
            n = num_bolts

        inputs = {
            "shear_load": shear_load,
            "num_bolts": num_bolts,
            "shear_area": shear_area,
        }

        # Calculate total shear area: A_total = n x A_shear
        total_shear_area = shear_area * n

        self.add_step(
            description="Calculate total shear area for all bolts",
            formula="A_total = n x A_shear",
            result=total_shear_area,
            substitution=f"A_total = {n} x {shear_area} = {total_shear_area}",
        )

        # Calculate shear stress: tau = V / (n x A_shear)
        shear_stress = shear_load / total_shear_area

        self.add_step(
            description="Calculate shear stress using tau = V / (n x A_shear)",
            formula="tau = V / (n x A_shear)",
            result=shear_stress,
            substitution=f"tau = {shear_load} / {total_shear_area} = {shear_stress}",
        )

        outputs = {
            "shear_stress": shear_stress,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class BoltPreload(Calculation):
    """
    Calculate recommended bolt preload for reused connections.

    Formula: Fi = 0.75 x At x Sp

    Where:
        Fi = initial preload force (N)
        At = tensile stress area (m^2)
        Sp = proof strength of bolt material (Pa)

    The 0.75 factor is recommended for reused connections to account for
    embedment relaxation and other factors that reduce effective preload.
    """

    name = "Bolt Preload"
    category = "Mechanical"
    description = (
        "Calculate recommended bolt preload for reused connections. "
        "Fi = 0.75 x At x Sp"
    )
    references = ["Shigley's Mechanical Engineering Design", "SAE J429"]

    input_params = [
        Parameter("tensile_stress_area", "m**2", "Tensile stress area of the bolt"),
        Parameter("proof_strength", "Pa", "Proof strength of bolt material"),
    ]
    output_params = [
        Parameter("preload_force", "N", "Recommended initial preload force"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate bolt preload.

        Args:
            tensile_stress_area: Tensile stress area as Quantity (m^2).
            proof_strength: Proof strength as Quantity (Pa).

        Returns:
            CalculationResult with preload force output.
        """
        self.reset()

        tensile_stress_area: Quantity = kwargs["tensile_stress_area"]
        proof_strength: Quantity = kwargs["proof_strength"]

        inputs = {
            "tensile_stress_area": tensile_stress_area,
            "proof_strength": proof_strength,
        }

        # Calculate maximum tensile capacity: At x Sp
        max_capacity = tensile_stress_area * proof_strength

        self.add_step(
            description="Calculate maximum tensile capacity at proof strength",
            formula="F_max = At x Sp",
            result=max_capacity,
            substitution=f"F_max = {tensile_stress_area} x {proof_strength} = {max_capacity}",
        )

        # Calculate preload: Fi = 0.75 x At x Sp
        preload_force = max_capacity * 0.75

        self.add_step(
            description="Calculate preload force (75% of proof load for reused connections)",
            formula="Fi = 0.75 x At x Sp",
            result=preload_force,
            substitution=f"Fi = 0.75 x {max_capacity} = {preload_force}",
        )

        outputs = {
            "preload_force": preload_force,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TorsionalStress(Calculation):
    """
    Calculate torsional shear stress in a circular shaft.

    Formula: tau = T x r / J

    Where:
        tau = torsional shear stress (Pa)
        T = applied torque (N*m)
        r = radius at which stress is calculated (m)
        J = polar moment of inertia (m^4)

    Maximum shear stress occurs at the outer surface (r = outer radius).
    """

    name = "Torsional Stress"
    category = "Mechanical"
    description = "Calculate torsional shear stress in a shaft. tau = T x r / J"
    references = ["Shigley's Mechanical Engineering Design", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("torque", "N*m", "Applied torque"),
        Parameter("radius", "m", "Radius at which stress is calculated"),
        Parameter("polar_moment_of_inertia", "m**4", "Polar moment of inertia of cross-section"),
    ]
    output_params = [
        Parameter("shear_stress", "Pa", "Torsional shear stress"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate torsional shear stress.

        Args:
            torque: Applied torque as Quantity (N*m).
            radius: Radius as Quantity (m).
            polar_moment_of_inertia: J as Quantity (m^4).

        Returns:
            CalculationResult with shear stress output.
        """
        self.reset()

        torque: Quantity = kwargs["torque"]
        radius: Quantity = kwargs["radius"]
        polar_moment_of_inertia: Quantity = kwargs["polar_moment_of_inertia"]

        inputs = {
            "torque": torque,
            "radius": radius,
            "polar_moment_of_inertia": polar_moment_of_inertia,
        }

        # Calculate T x r
        torque_times_radius = torque * radius

        self.add_step(
            description="Calculate torque times radius",
            formula="T x r",
            result=torque_times_radius,
            substitution=f"T x r = {torque} x {radius} = {torque_times_radius}",
        )

        # Calculate shear stress: tau = T x r / J
        shear_stress = torque_times_radius / polar_moment_of_inertia

        self.add_step(
            description="Calculate torsional shear stress",
            formula="tau = T x r / J",
            result=shear_stress,
            substitution=f"tau = {torque_times_radius} / {polar_moment_of_inertia} = {shear_stress}",
        )

        outputs = {
            "shear_stress": shear_stress,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ShaftTwistAngle(Calculation):
    """
    Calculate the angle of twist for a shaft under torsion.

    Formula: theta = T x L / (G x J)

    Where:
        theta = angle of twist (radians)
        T = applied torque (N*m)
        L = length of shaft (m)
        G = shear modulus of elasticity (Pa)
        J = polar moment of inertia (m^4)
    """

    name = "Shaft Twist Angle"
    category = "Mechanical"
    description = "Calculate the angle of twist in a shaft. theta = T x L / (G x J)"
    references = ["Shigley's Mechanical Engineering Design", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("torque", "N*m", "Applied torque"),
        Parameter("length", "m", "Length of shaft"),
        Parameter("shear_modulus", "Pa", "Shear modulus of elasticity"),
        Parameter("polar_moment_of_inertia", "m**4", "Polar moment of inertia of cross-section"),
    ]
    output_params = [
        Parameter("twist_angle", "rad", "Angle of twist"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate shaft twist angle.

        Args:
            torque: Applied torque as Quantity (N*m).
            length: Shaft length as Quantity (m).
            shear_modulus: Shear modulus as Quantity (Pa).
            polar_moment_of_inertia: J as Quantity (m^4).

        Returns:
            CalculationResult with twist angle output.
        """
        self.reset()

        torque: Quantity = kwargs["torque"]
        length: Quantity = kwargs["length"]
        shear_modulus: Quantity = kwargs["shear_modulus"]
        polar_moment_of_inertia: Quantity = kwargs["polar_moment_of_inertia"]

        inputs = {
            "torque": torque,
            "length": length,
            "shear_modulus": shear_modulus,
            "polar_moment_of_inertia": polar_moment_of_inertia,
        }

        # Calculate T x L (numerator)
        numerator = torque * length

        self.add_step(
            description="Calculate torque times length",
            formula="T x L",
            result=numerator,
            substitution=f"T x L = {torque} x {length} = {numerator}",
        )

        # Calculate G x J (denominator)
        denominator = shear_modulus * polar_moment_of_inertia

        self.add_step(
            description="Calculate shear modulus times polar moment of inertia",
            formula="G x J",
            result=denominator,
            substitution=f"G x J = {shear_modulus} x {polar_moment_of_inertia} = {denominator}",
        )

        # Calculate twist angle: theta = T x L / (G x J)
        twist_angle = numerator / denominator

        self.add_step(
            description="Calculate angle of twist",
            formula="theta = T x L / (G x J)",
            result=twist_angle,
            substitution=f"theta = {numerator} / {denominator} = {twist_angle}",
        )

        outputs = {
            "twist_angle": twist_angle,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class BearingLife(Calculation):
    """
    Calculate bearing life using the basic rating life equation.

    Formula: L10 = (C / P)^p x 10^6 revolutions

    Where:
        L10 = basic rating life (revolutions)
        C = basic dynamic load rating (N)
        P = equivalent dynamic bearing load (N)
        p = life exponent (3 for ball bearings, 10/3 for roller bearings)

    Optionally calculates life in hours at a given RPM:
        L10h = L10 / (60 x rpm)
    """

    name = "Bearing Life"
    category = "Mechanical"
    description = (
        "Calculate bearing life in revolutions and hours. "
        "L10 = (C/P)^p x 10^6 revolutions"
    )
    references = ["ISO 281", "SKF Bearing Catalog", "Shigley's Mechanical Engineering Design"]

    input_params = [
        Parameter("dynamic_load_rating", "N", "Basic dynamic load rating (C)"),
        Parameter("equivalent_load", "N", "Equivalent dynamic bearing load (P)"),
        Parameter("life_exponent", "dimensionless", "Life exponent (3 for ball, 10/3 for roller)"),
        Parameter("rpm", "1/min", "Rotational speed for life in hours calculation", default=None),
    ]
    output_params = [
        Parameter("bearing_life_revolutions", "dimensionless", "Basic rating life in millions of revolutions"),
        Parameter("bearing_life_hours", "hr", "Basic rating life in hours"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate bearing life.

        Args:
            dynamic_load_rating: C as Quantity (N).
            equivalent_load: P as Quantity (N).
            life_exponent: p (3 for ball bearings, 10/3 for roller).
            rpm: Rotational speed as Quantity (1/min) - optional.

        Returns:
            CalculationResult with bearing life in revolutions and hours.
        """
        self.reset()

        dynamic_load_rating: Quantity = kwargs["dynamic_load_rating"]
        equivalent_load: Quantity = kwargs["equivalent_load"]
        life_exponent = kwargs["life_exponent"]
        rpm: Optional[Quantity] = kwargs.get("rpm")

        # Handle life_exponent as either float or Quantity
        if isinstance(life_exponent, Quantity):
            p = life_exponent.magnitude
        else:
            p = life_exponent

        inputs = {
            "dynamic_load_rating": dynamic_load_rating,
            "equivalent_load": equivalent_load,
            "life_exponent": life_exponent,
        }
        if rpm is not None:
            inputs["rpm"] = rpm

        # Calculate load ratio: C / P
        load_ratio = dynamic_load_rating / equivalent_load

        self.add_step(
            description="Calculate load ratio",
            formula="C / P",
            result=load_ratio,
            substitution=f"C / P = {dynamic_load_rating} / {equivalent_load} = {load_ratio}",
        )

        # Calculate (C / P)^p
        load_ratio_magnitude = load_ratio.magnitude
        ratio_to_power = load_ratio_magnitude ** p

        self.add_step(
            description="Raise load ratio to life exponent",
            formula="(C / P)^p",
            result=ratio_to_power,
            substitution=f"({load_ratio_magnitude:.4f})^{p} = {ratio_to_power:.4f}",
        )

        # Calculate L10 in millions of revolutions
        bearing_life_revolutions = ratio_to_power

        self.add_step(
            description="Calculate basic rating life L10 (millions of revolutions)",
            formula="L10 = (C / P)^p x 10^6 rev",
            result=bearing_life_revolutions,
            substitution=f"L10 = {ratio_to_power:.4f} x 10^6 = {bearing_life_revolutions:.4f} million revolutions",
        )

        # Create dimensionless quantity for output
        bearing_life_revolutions_qty = Quantity(bearing_life_revolutions, "dimensionless")

        # Calculate life in hours if RPM is provided
        if rpm is not None:
            # Handle rpm as Quantity
            if isinstance(rpm, Quantity):
                rpm_value = rpm.magnitude
            else:
                rpm_value = rpm

            # L10h = L10 x 10^6 / (60 x rpm)
            life_hours = (bearing_life_revolutions * 1e6) / (60 * rpm_value)

            self.add_step(
                description="Calculate bearing life in hours",
                formula="L10h = L10 x 10^6 / (60 x rpm)",
                result=life_hours,
                substitution=f"L10h = {bearing_life_revolutions:.4f} x 10^6 / (60 x {rpm_value}) = {life_hours:.2f} hours",
            )

            bearing_life_hours_qty = Quantity(life_hours, "hr")
        else:
            # If no RPM provided, cannot calculate hours
            bearing_life_hours_qty = Quantity(0, "hr")

            self.add_step(
                description="Bearing life in hours requires RPM input",
                formula="L10h = L10 x 10^6 / (60 x rpm)",
                result="N/A - RPM not provided",
                substitution="RPM not provided, hours calculation skipped",
            )

        outputs = {
            "bearing_life_revolutions": bearing_life_revolutions_qty,
            "bearing_life_hours": bearing_life_hours_qty,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SpringRate(Calculation):
    """
    Calculate the spring rate (stiffness) of a helical compression spring.

    Formula: k = G x d^4 / (8 x D^3 x N)

    Where:
        k = spring rate (N/m)
        G = shear modulus of spring material (Pa)
        d = wire diameter (m)
        D = mean coil diameter (m)
        N = number of active coils
    """

    name = "Spring Rate"
    category = "Mechanical"
    description = (
        "Calculate spring rate for a helical compression spring. "
        "k = G x d^4 / (8 x D^3 x N)"
    )
    references = ["Shigley's Mechanical Engineering Design", "Spring Design Manual (SMI)"]

    input_params = [
        Parameter("shear_modulus", "Pa", "Shear modulus of spring material"),
        Parameter("wire_diameter", "m", "Wire diameter"),
        Parameter("mean_coil_diameter", "m", "Mean coil diameter"),
        Parameter("active_coils", "dimensionless", "Number of active coils"),
    ]
    output_params = [
        Parameter("spring_rate", "N/m", "Spring rate (stiffness)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate spring rate.

        Args:
            shear_modulus: G as Quantity (Pa).
            wire_diameter: d as Quantity (m).
            mean_coil_diameter: D as Quantity (m).
            active_coils: N (int or dimensionless Quantity).

        Returns:
            CalculationResult with spring rate output.
        """
        self.reset()

        shear_modulus: Quantity = kwargs["shear_modulus"]
        wire_diameter: Quantity = kwargs["wire_diameter"]
        mean_coil_diameter: Quantity = kwargs["mean_coil_diameter"]
        active_coils = kwargs["active_coils"]

        # Handle active_coils as either int/float or Quantity
        if isinstance(active_coils, Quantity):
            n = active_coils.magnitude
        else:
            n = active_coils

        inputs = {
            "shear_modulus": shear_modulus,
            "wire_diameter": wire_diameter,
            "mean_coil_diameter": mean_coil_diameter,
            "active_coils": active_coils,
        }

        # Calculate d^4
        d_fourth = wire_diameter ** 4

        self.add_step(
            description="Calculate wire diameter to the fourth power",
            formula="d^4",
            result=d_fourth,
            substitution=f"d^4 = ({wire_diameter})^4 = {d_fourth}",
        )

        # Calculate D^3
        D_cubed = mean_coil_diameter ** 3

        self.add_step(
            description="Calculate mean coil diameter cubed",
            formula="D^3",
            result=D_cubed,
            substitution=f"D^3 = ({mean_coil_diameter})^3 = {D_cubed}",
        )

        # Calculate numerator: G x d^4
        numerator = shear_modulus * d_fourth

        self.add_step(
            description="Calculate numerator (G x d^4)",
            formula="G x d^4",
            result=numerator,
            substitution=f"G x d^4 = {shear_modulus} x {d_fourth} = {numerator}",
        )

        # Calculate denominator: 8 x D^3 x N
        denominator = D_cubed * 8 * n

        self.add_step(
            description="Calculate denominator (8 x D^3 x N)",
            formula="8 x D^3 x N",
            result=denominator,
            substitution=f"8 x D^3 x N = 8 x {D_cubed} x {n} = {denominator}",
        )

        # Calculate spring rate: k = G x d^4 / (8 x D^3 x N)
        spring_rate = numerator / denominator

        self.add_step(
            description="Calculate spring rate",
            formula="k = G x d^4 / (8 x D^3 x N)",
            result=spring_rate,
            substitution=f"k = {numerator} / {denominator} = {spring_rate}",
        )

        outputs = {
            "spring_rate": spring_rate,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SpringDeflection(Calculation):
    """
    Calculate deflection of a spring under load.

    Formula: delta = F / k

    Where:
        delta = deflection (m)
        F = applied force (N)
        k = spring rate (N/m)

    This is Hooke's Law for linear springs.
    """

    name = "Spring Deflection"
    category = "Mechanical"
    description = "Calculate spring deflection using Hooke's Law. delta = F / k"
    references = ["Shigley's Mechanical Engineering Design"]

    input_params = [
        Parameter("force", "N", "Applied force on the spring"),
        Parameter("spring_rate", "N/m", "Spring rate (stiffness)"),
    ]
    output_params = [
        Parameter("deflection", "m", "Spring deflection"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate spring deflection.

        Args:
            force: Applied force as Quantity (N).
            spring_rate: Spring rate as Quantity (N/m).

        Returns:
            CalculationResult with deflection output.
        """
        self.reset()

        force: Quantity = kwargs["force"]
        spring_rate: Quantity = kwargs["spring_rate"]

        inputs = {
            "force": force,
            "spring_rate": spring_rate,
        }

        # Calculate deflection: delta = F / k
        deflection = force / spring_rate

        self.add_step(
            description="Calculate spring deflection using Hooke's Law",
            formula="delta = F / k",
            result=deflection,
            substitution=f"delta = {force} / {spring_rate} = {deflection}",
        )

        outputs = {
            "deflection": deflection,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "BoltTensileStress",
    "BoltShearCapacity",
    "BoltPreload",
    "TorsionalStress",
    "ShaftTwistAngle",
    "BearingLife",
    "SpringRate",
    "SpringDeflection",
]
