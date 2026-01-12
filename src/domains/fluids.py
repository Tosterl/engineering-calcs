"""
Fluid dynamics calculations for Engineering Calculations Database.

This module provides engineering calculations for fluid dynamics including:
- Flow rate (continuity equation)
- Reynolds number
- Bernoulli's equation
- Darcy-Weisbach head loss
- Friction factor (Colebrook equation)
- Pipe pressure drop
- Pump power
- Hydraulic diameter
"""

from __future__ import annotations

import math
from typing import Any

from scipy.optimize import fsolve

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


# Gravitational acceleration constant (m/s^2)
GRAVITY = 9.80665


@register
class FlowRate(Calculation):
    """
    Calculate volumetric flow rate using the continuity equation.

    Formula: Q = V x A

    Where:
        Q = volumetric flow rate (m^3/s)
        V = fluid velocity (m/s)
        A = cross-sectional area of pipe (m^2)
    """

    name = "Flow Rate"
    category = "Fluids"
    description = "Calculate volumetric flow rate using continuity equation. Q = V x A"
    references = ["Fluid Mechanics, White", "Engineering Fluid Mechanics, Crowe et al."]

    input_params = [
        Parameter("velocity", "m/s", "Fluid velocity"),
        Parameter("pipe_area", "m**2", "Cross-sectional area of pipe"),
    ]
    output_params = [
        Parameter("flow_rate", "m**3/s", "Volumetric flow rate"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate volumetric flow rate.

        Args:
            velocity: Fluid velocity as Quantity (m/s).
            pipe_area: Cross-sectional area as Quantity (m^2).

        Returns:
            CalculationResult with flow rate output.
        """
        self.reset()

        velocity: Quantity = kwargs["velocity"]
        pipe_area: Quantity = kwargs["pipe_area"]

        inputs = {
            "velocity": velocity,
            "pipe_area": pipe_area,
        }

        # Calculate flow rate: Q = V x A
        flow_rate = velocity * pipe_area

        self.add_step(
            description="Calculate volumetric flow rate using continuity equation",
            formula="Q = V x A",
            result=flow_rate,
            substitution=f"Q = {velocity} x {pipe_area} = {flow_rate}",
        )

        outputs = {
            "flow_rate": flow_rate,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ReynoldsNumber(Calculation):
    """
    Calculate Reynolds number to determine flow regime.

    Formula: Re = (rho x V x D) / mu

    Where:
        Re = Reynolds number (dimensionless)
        rho = fluid density (kg/m^3)
        V = fluid velocity (m/s)
        D = characteristic diameter (m)
        mu = dynamic viscosity (Pa*s)

    Flow regimes:
        - Re < 2300: Laminar flow
        - 2300 <= Re <= 4000: Transitional flow
        - Re > 4000: Turbulent flow
    """

    name = "Reynolds Number"
    category = "Fluids"
    description = (
        "Calculate Reynolds number and determine flow regime. "
        "Re = (rho x V x D) / mu"
    )
    references = ["Fluid Mechanics, White", "Engineering Fluid Mechanics, Crowe et al."]

    input_params = [
        Parameter("density", "kg/m**3", "Fluid density"),
        Parameter("velocity", "m/s", "Fluid velocity"),
        Parameter("diameter", "m", "Characteristic diameter (pipe inner diameter)"),
        Parameter("dynamic_viscosity", "Pa*s", "Dynamic viscosity of fluid"),
    ]
    output_params = [
        Parameter("reynolds_number", "dimensionless", "Reynolds number"),
        Parameter("flow_regime", "dimensionless", "Flow regime classification"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate Reynolds number and determine flow regime.

        Args:
            density: Fluid density as Quantity (kg/m^3).
            velocity: Fluid velocity as Quantity (m/s).
            diameter: Characteristic diameter as Quantity (m).
            dynamic_viscosity: Dynamic viscosity as Quantity (Pa*s).

        Returns:
            CalculationResult with Reynolds number and flow regime.
        """
        self.reset()

        density: Quantity = kwargs["density"]
        velocity: Quantity = kwargs["velocity"]
        diameter: Quantity = kwargs["diameter"]
        dynamic_viscosity: Quantity = kwargs["dynamic_viscosity"]

        inputs = {
            "density": density,
            "velocity": velocity,
            "diameter": diameter,
            "dynamic_viscosity": dynamic_viscosity,
        }

        # Calculate numerator: rho x V x D
        numerator = density * velocity * diameter
        self.add_step(
            description="Calculate numerator (rho x V x D)",
            formula="rho x V x D",
            result=numerator,
            substitution=f"rho x V x D = {density} x {velocity} x {diameter} = {numerator}",
        )

        # Calculate Reynolds number: Re = (rho x V x D) / mu
        reynolds_number = numerator / dynamic_viscosity
        self.add_step(
            description="Calculate Reynolds number",
            formula="Re = (rho x V x D) / mu",
            result=reynolds_number,
            substitution=f"Re = {numerator} / {dynamic_viscosity} = {reynolds_number}",
        )

        # Determine flow regime
        re_value = reynolds_number.magnitude
        if re_value < 2300:
            flow_regime = "laminar"
            regime_description = "Laminar flow (Re < 2300)"
        elif re_value <= 4000:
            flow_regime = "transitional"
            regime_description = "Transitional flow (2300 <= Re <= 4000)"
        else:
            flow_regime = "turbulent"
            regime_description = "Turbulent flow (Re > 4000)"

        self.add_step(
            description="Determine flow regime based on Reynolds number",
            formula="Re < 2300: Laminar, 2300 <= Re <= 4000: Transitional, Re > 4000: Turbulent",
            result=flow_regime,
            substitution=f"Re = {re_value:.2f} -> {regime_description}",
        )

        outputs = {
            "reynolds_number": reynolds_number,
            "flow_regime": flow_regime,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class BernoulliEquation(Calculation):
    """
    Apply Bernoulli's equation to find pressure at point 2.

    Formula: P1 + (1/2)*rho*V1^2 + rho*g*h1 = P2 + (1/2)*rho*V2^2 + rho*g*h2

    Solving for P2:
        P2 = P1 + (1/2)*rho*(V1^2 - V2^2) + rho*g*(h1 - h2)

    Where:
        P = pressure (Pa)
        rho = fluid density (kg/m^3)
        V = fluid velocity (m/s)
        g = gravitational acceleration (9.80665 m/s^2)
        h = elevation (m)
    """

    name = "Bernoulli Equation"
    category = "Fluids"
    description = (
        "Apply Bernoulli's equation to calculate pressure at a second point. "
        "P1 + (1/2)*rho*V1^2 + rho*g*h1 = P2 + (1/2)*rho*V2^2 + rho*g*h2"
    )
    references = ["Fluid Mechanics, White", "Fundamentals of Fluid Mechanics, Munson"]

    input_params = [
        Parameter("pressure_1", "Pa", "Pressure at point 1"),
        Parameter("velocity_1", "m/s", "Velocity at point 1"),
        Parameter("height_1", "m", "Elevation at point 1"),
        Parameter("velocity_2", "m/s", "Velocity at point 2"),
        Parameter("height_2", "m", "Elevation at point 2"),
        Parameter("density", "kg/m**3", "Fluid density"),
    ]
    output_params = [
        Parameter("pressure_2", "Pa", "Pressure at point 2"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate pressure at point 2 using Bernoulli's equation.

        Args:
            pressure_1: Pressure at point 1 as Quantity (Pa).
            velocity_1: Velocity at point 1 as Quantity (m/s).
            height_1: Elevation at point 1 as Quantity (m).
            velocity_2: Velocity at point 2 as Quantity (m/s).
            height_2: Elevation at point 2 as Quantity (m).
            density: Fluid density as Quantity (kg/m^3).

        Returns:
            CalculationResult with pressure at point 2.
        """
        self.reset()

        pressure_1: Quantity = kwargs["pressure_1"]
        velocity_1: Quantity = kwargs["velocity_1"]
        height_1: Quantity = kwargs["height_1"]
        velocity_2: Quantity = kwargs["velocity_2"]
        height_2: Quantity = kwargs["height_2"]
        density: Quantity = kwargs["density"]

        inputs = {
            "pressure_1": pressure_1,
            "velocity_1": velocity_1,
            "height_1": height_1,
            "velocity_2": velocity_2,
            "height_2": height_2,
            "density": density,
        }

        # Create gravity quantity
        g = Quantity(GRAVITY, "m/s**2")

        # Calculate velocity term: (1/2)*rho*(V1^2 - V2^2)
        v1_squared = velocity_1 ** 2
        v2_squared = velocity_2 ** 2
        self.add_step(
            description="Calculate velocity squared terms",
            formula="V1^2, V2^2",
            result=(v1_squared, v2_squared),
            substitution=f"V1^2 = ({velocity_1})^2 = {v1_squared}, V2^2 = ({velocity_2})^2 = {v2_squared}",
        )

        velocity_difference = v1_squared - v2_squared
        dynamic_pressure_term = density * velocity_difference * Quantity(0.5, "dimensionless")
        self.add_step(
            description="Calculate dynamic pressure difference",
            formula="(1/2) x rho x (V1^2 - V2^2)",
            result=dynamic_pressure_term,
            substitution=f"(1/2) x {density} x ({v1_squared} - {v2_squared}) = {dynamic_pressure_term}",
        )

        # Calculate elevation term: rho*g*(h1 - h2)
        height_difference = height_1 - height_2
        elevation_term = density * g * height_difference
        self.add_step(
            description="Calculate hydrostatic pressure difference",
            formula="rho x g x (h1 - h2)",
            result=elevation_term,
            substitution=f"{density} x {g} x ({height_1} - {height_2}) = {elevation_term}",
        )

        # Calculate P2 = P1 + dynamic_pressure_term + elevation_term
        pressure_2 = pressure_1 + dynamic_pressure_term + elevation_term
        self.add_step(
            description="Calculate pressure at point 2",
            formula="P2 = P1 + (1/2)*rho*(V1^2 - V2^2) + rho*g*(h1 - h2)",
            result=pressure_2,
            substitution=f"P2 = {pressure_1} + {dynamic_pressure_term} + {elevation_term} = {pressure_2}",
        )

        outputs = {
            "pressure_2": pressure_2,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class DarcyWeisbachHeadLoss(Calculation):
    """
    Calculate head loss due to friction using Darcy-Weisbach equation.

    Formula: hf = f x (L/D) x (V^2 / (2*g))

    Where:
        hf = head loss due to friction (m)
        f = Darcy friction factor (dimensionless)
        L = pipe length (m)
        D = pipe diameter (m)
        V = fluid velocity (m/s)
        g = gravitational acceleration (9.80665 m/s^2)
    """

    name = "Darcy-Weisbach Head Loss"
    category = "Fluids"
    description = (
        "Calculate head loss due to friction in a pipe. "
        "hf = f x (L/D) x (V^2 / (2*g))"
    )
    references = ["Fluid Mechanics, White", "Cameron Hydraulic Data"]

    input_params = [
        Parameter("friction_factor", "dimensionless", "Darcy friction factor"),
        Parameter("length", "m", "Pipe length"),
        Parameter("diameter", "m", "Pipe inner diameter"),
        Parameter("velocity", "m/s", "Fluid velocity"),
    ]
    output_params = [
        Parameter("head_loss", "m", "Head loss due to friction"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate head loss using Darcy-Weisbach equation.

        Args:
            friction_factor: Darcy friction factor as Quantity (dimensionless).
            length: Pipe length as Quantity (m).
            diameter: Pipe diameter as Quantity (m).
            velocity: Fluid velocity as Quantity (m/s).

        Returns:
            CalculationResult with head loss.
        """
        self.reset()

        friction_factor: Quantity = kwargs["friction_factor"]
        length: Quantity = kwargs["length"]
        diameter: Quantity = kwargs["diameter"]
        velocity: Quantity = kwargs["velocity"]

        inputs = {
            "friction_factor": friction_factor,
            "length": length,
            "diameter": diameter,
            "velocity": velocity,
        }

        # Create gravity quantity
        g = Quantity(GRAVITY, "m/s**2")

        # Calculate L/D ratio
        length_diameter_ratio = length / diameter
        self.add_step(
            description="Calculate length-to-diameter ratio",
            formula="L/D",
            result=length_diameter_ratio,
            substitution=f"L/D = {length} / {diameter} = {length_diameter_ratio}",
        )

        # Calculate velocity head: V^2 / (2*g)
        v_squared = velocity ** 2
        velocity_head = v_squared / (Quantity(2.0, "dimensionless") * g)
        self.add_step(
            description="Calculate velocity head",
            formula="V^2 / (2*g)",
            result=velocity_head,
            substitution=f"V^2 / (2*g) = ({velocity})^2 / (2 x {g}) = {velocity_head}",
        )

        # Calculate head loss: hf = f x (L/D) x (V^2 / (2*g))
        head_loss = friction_factor * length_diameter_ratio * velocity_head
        self.add_step(
            description="Calculate head loss using Darcy-Weisbach equation",
            formula="hf = f x (L/D) x (V^2 / (2*g))",
            result=head_loss,
            substitution=f"hf = {friction_factor} x {length_diameter_ratio} x {velocity_head} = {head_loss}",
        )

        outputs = {
            "head_loss": head_loss,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class FrictionFactor(Calculation):
    """
    Calculate Darcy friction factor using the Colebrook equation.

    The Colebrook equation (for turbulent flow):
        1/sqrt(f) = -2*log10((e/D)/3.7 + 2.51/(Re*sqrt(f)))

    Where:
        f = Darcy friction factor (dimensionless)
        e/D = relative roughness (dimensionless)
        Re = Reynolds number (dimensionless)

    This is an implicit equation that requires iterative solution.
    For laminar flow (Re < 2300): f = 64/Re
    """

    name = "Friction Factor"
    category = "Fluids"
    description = (
        "Calculate Darcy friction factor using the Colebrook equation (iterative solver). "
        "For laminar flow: f = 64/Re"
    )
    references = ["Fluid Mechanics, White", "Moody Diagram", "Colebrook (1939)"]

    input_params = [
        Parameter("reynolds_number", "dimensionless", "Reynolds number"),
        Parameter("relative_roughness", "dimensionless", "Relative pipe roughness (e/D)"),
    ]
    output_params = [
        Parameter("friction_factor", "dimensionless", "Darcy friction factor"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate Darcy friction factor.

        Args:
            reynolds_number: Reynolds number as Quantity (dimensionless).
            relative_roughness: Relative roughness (e/D) as Quantity (dimensionless).

        Returns:
            CalculationResult with friction factor.
        """
        self.reset()

        reynolds_number: Quantity = kwargs["reynolds_number"]
        relative_roughness: Quantity = kwargs["relative_roughness"]

        inputs = {
            "reynolds_number": reynolds_number,
            "relative_roughness": relative_roughness,
        }

        re_value = reynolds_number.magnitude
        e_d = relative_roughness.magnitude

        if re_value < 2300:
            # Laminar flow: f = 64/Re
            f_value = 64.0 / re_value
            self.add_step(
                description="Laminar flow detected (Re < 2300), using laminar friction factor",
                formula="f = 64 / Re",
                result=f_value,
                substitution=f"f = 64 / {re_value:.2f} = {f_value:.6f}",
            )
        else:
            # Turbulent flow: solve Colebrook equation iteratively
            self.add_step(
                description="Turbulent flow detected (Re >= 2300), solving Colebrook equation",
                formula="1/sqrt(f) = -2*log10((e/D)/3.7 + 2.51/(Re*sqrt(f)))",
                result="Iterative solution required",
                substitution=f"Re = {re_value:.2f}, e/D = {e_d:.6f}",
            )

            def colebrook_equation(f: float) -> float:
                """Colebrook equation rearranged to find root."""
                if f <= 0:
                    return float('inf')
                sqrt_f = math.sqrt(f)
                lhs = 1.0 / sqrt_f
                rhs = -2.0 * math.log10(e_d / 3.7 + 2.51 / (re_value * sqrt_f))
                return lhs - rhs

            # Initial guess using Swamee-Jain approximation
            if e_d > 0:
                f_initial = 0.25 / (math.log10(e_d / 3.7 + 5.74 / (re_value ** 0.9))) ** 2
            else:
                # Smooth pipe approximation
                f_initial = 0.316 / (re_value ** 0.25)

            self.add_step(
                description="Calculate initial guess using Swamee-Jain approximation",
                formula="f_initial = 0.25 / [log10(e/D/3.7 + 5.74/Re^0.9)]^2",
                result=f_initial,
                substitution=f"f_initial = {f_initial:.6f}",
            )

            # Solve using scipy.optimize.fsolve
            solution = fsolve(colebrook_equation, f_initial, full_output=True)
            f_value = float(solution[0][0])

            self.add_step(
                description="Solve Colebrook equation iteratively",
                formula="fsolve(1/sqrt(f) + 2*log10((e/D)/3.7 + 2.51/(Re*sqrt(f))) = 0)",
                result=f_value,
                substitution=f"f = {f_value:.6f}",
            )

        friction_factor = Quantity(f_value, "dimensionless")

        outputs = {
            "friction_factor": friction_factor,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class PipePressureDrop(Calculation):
    """
    Calculate pressure drop from head loss.

    Formula: delta_P = rho x g x hf

    Where:
        delta_P = pressure drop (Pa)
        rho = fluid density (kg/m^3)
        g = gravitational acceleration (9.80665 m/s^2)
        hf = head loss (m)
    """

    name = "Pipe Pressure Drop"
    category = "Fluids"
    description = "Calculate pressure drop from head loss. delta_P = rho x g x hf"
    references = ["Fluid Mechanics, White", "Cameron Hydraulic Data"]

    input_params = [
        Parameter("density", "kg/m**3", "Fluid density"),
        Parameter("head_loss", "m", "Head loss"),
    ]
    output_params = [
        Parameter("pressure_drop", "Pa", "Pressure drop"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate pressure drop from head loss.

        Args:
            density: Fluid density as Quantity (kg/m^3).
            head_loss: Head loss as Quantity (m).

        Returns:
            CalculationResult with pressure drop.
        """
        self.reset()

        density: Quantity = kwargs["density"]
        head_loss: Quantity = kwargs["head_loss"]

        inputs = {
            "density": density,
            "head_loss": head_loss,
        }

        # Create gravity quantity
        g = Quantity(GRAVITY, "m/s**2")

        # Calculate rho x g
        rho_g = density * g
        self.add_step(
            description="Calculate specific weight (rho x g)",
            formula="gamma = rho x g",
            result=rho_g,
            substitution=f"gamma = {density} x {g} = {rho_g}",
        )

        # Calculate pressure drop: delta_P = rho x g x hf
        pressure_drop = rho_g * head_loss
        self.add_step(
            description="Calculate pressure drop",
            formula="delta_P = rho x g x hf",
            result=pressure_drop,
            substitution=f"delta_P = {rho_g} x {head_loss} = {pressure_drop}",
        )

        outputs = {
            "pressure_drop": pressure_drop,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class PumpPower(Calculation):
    """
    Calculate hydraulic power required by a pump.

    Formula: P = (rho x g x Q x H) / eta

    Where:
        P = pump power (W)
        rho = fluid density (kg/m^3)
        g = gravitational acceleration (9.80665 m/s^2)
        Q = volumetric flow rate (m^3/s)
        H = total head (m)
        eta = pump efficiency (dimensionless, 0-1)
    """

    name = "Pump Power"
    category = "Fluids"
    description = (
        "Calculate hydraulic power required by a pump. "
        "P = (rho x g x Q x H) / eta"
    )
    references = ["Pump Handbook, Karassik et al.", "Cameron Hydraulic Data"]

    input_params = [
        Parameter("density", "kg/m**3", "Fluid density"),
        Parameter("flow_rate", "m**3/s", "Volumetric flow rate"),
        Parameter("head", "m", "Total head (pump head)"),
        Parameter("efficiency", "dimensionless", "Pump efficiency (0-1)"),
    ]
    output_params = [
        Parameter("power", "W", "Required pump power"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate pump power.

        Args:
            density: Fluid density as Quantity (kg/m^3).
            flow_rate: Volumetric flow rate as Quantity (m^3/s).
            head: Total head as Quantity (m).
            efficiency: Pump efficiency as Quantity (dimensionless, 0-1).

        Returns:
            CalculationResult with pump power.
        """
        self.reset()

        density: Quantity = kwargs["density"]
        flow_rate: Quantity = kwargs["flow_rate"]
        head: Quantity = kwargs["head"]
        efficiency: Quantity = kwargs["efficiency"]

        inputs = {
            "density": density,
            "flow_rate": flow_rate,
            "head": head,
            "efficiency": efficiency,
        }

        # Validate efficiency is between 0 and 1
        eta_value = efficiency.magnitude
        if eta_value <= 0 or eta_value > 1:
            raise ValueError(f"Efficiency must be between 0 (exclusive) and 1 (inclusive), got {eta_value}")

        # Create gravity quantity
        g = Quantity(GRAVITY, "m/s**2")

        # Calculate hydraulic power: P_hydraulic = rho x g x Q x H
        hydraulic_power = density * g * flow_rate * head
        self.add_step(
            description="Calculate hydraulic power",
            formula="P_hydraulic = rho x g x Q x H",
            result=hydraulic_power,
            substitution=f"P_hydraulic = {density} x {g} x {flow_rate} x {head} = {hydraulic_power}",
        )

        # Calculate required pump power: P = P_hydraulic / eta
        power = hydraulic_power / efficiency
        self.add_step(
            description="Calculate required pump power (accounting for efficiency)",
            formula="P = P_hydraulic / eta",
            result=power,
            substitution=f"P = {hydraulic_power} / {efficiency} = {power}",
        )

        outputs = {
            "power": power,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class HydraulicDiameter(Calculation):
    """
    Calculate hydraulic diameter for non-circular ducts.

    Formula: Dh = 4*A / P

    Where:
        Dh = hydraulic diameter (m)
        A = cross-sectional area (m^2)
        P = wetted perimeter (m)

    The hydraulic diameter is used to generalize calculations
    for non-circular cross-sections to use the same formulas
    as circular pipes.
    """

    name = "Hydraulic Diameter"
    category = "Fluids"
    description = (
        "Calculate hydraulic diameter for non-circular ducts. "
        "Dh = 4*A / P"
    )
    references = ["Fluid Mechanics, White", "ASHRAE Handbook"]

    input_params = [
        Parameter("cross_section_area", "m**2", "Cross-sectional flow area"),
        Parameter("wetted_perimeter", "m", "Wetted perimeter"),
    ]
    output_params = [
        Parameter("hydraulic_diameter", "m", "Hydraulic diameter"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate hydraulic diameter.

        Args:
            cross_section_area: Cross-sectional area as Quantity (m^2).
            wetted_perimeter: Wetted perimeter as Quantity (m).

        Returns:
            CalculationResult with hydraulic diameter.
        """
        self.reset()

        cross_section_area: Quantity = kwargs["cross_section_area"]
        wetted_perimeter: Quantity = kwargs["wetted_perimeter"]

        inputs = {
            "cross_section_area": cross_section_area,
            "wetted_perimeter": wetted_perimeter,
        }

        # Calculate 4*A
        four_times_area = Quantity(4.0, "dimensionless") * cross_section_area
        self.add_step(
            description="Calculate numerator (4 x A)",
            formula="4 x A",
            result=four_times_area,
            substitution=f"4 x A = 4 x {cross_section_area} = {four_times_area}",
        )

        # Calculate hydraulic diameter: Dh = 4*A / P
        hydraulic_diameter = four_times_area / wetted_perimeter
        self.add_step(
            description="Calculate hydraulic diameter",
            formula="Dh = 4*A / P",
            result=hydraulic_diameter,
            substitution=f"Dh = {four_times_area} / {wetted_perimeter} = {hydraulic_diameter}",
        )

        outputs = {
            "hydraulic_diameter": hydraulic_diameter,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "FlowRate",
    "ReynoldsNumber",
    "BernoulliEquation",
    "DarcyWeisbachHeadLoss",
    "FrictionFactor",
    "PipePressureDrop",
    "PumpPower",
    "HydraulicDiameter",
]
