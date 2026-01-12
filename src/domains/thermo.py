"""
Thermodynamics calculations for Engineering Calculations Database.

This module provides engineering calculations for thermodynamics including:
- Conduction heat transfer (Fourier's Law)
- Convection heat transfer
- Radiation heat transfer (Stefan-Boltzmann)
- Thermal resistance
- Overall heat transfer coefficient
- Carnot efficiency
- Refrigeration coefficient of performance
- Log mean temperature difference (LMTD)
"""

from __future__ import annotations

import math
from typing import Any

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


# Stefan-Boltzmann constant (W/(m^2*K^4))
STEFAN_BOLTZMANN = 5.67e-8


@register
class ConductionHeatTransfer(Calculation):
    """
    Calculate heat transfer rate through conduction using Fourier's Law.

    Formula: Q = k * A * (delta_T / L)

    Where:
        Q = heat transfer rate (W)
        k = thermal conductivity (W/(m*K))
        A = cross-sectional area (m^2)
        delta_T = temperature difference (K)
        L = thickness of material (m)
    """

    name = "Conduction Heat Transfer"
    category = "Thermodynamics"
    description = (
        "Calculate heat transfer rate through conduction using Fourier's Law. "
        "Q = k * A * (delta_T / L)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Fundamentals of Heat and Mass Transfer"]

    input_params = [
        Parameter("thermal_conductivity", "W/(m*K)", "Thermal conductivity of material"),
        Parameter("area", "m**2", "Cross-sectional area perpendicular to heat flow"),
        Parameter("temperature_difference", "K", "Temperature difference across material"),
        Parameter("thickness", "m", "Thickness of material in direction of heat flow"),
    ]
    output_params = [
        Parameter("heat_transfer_rate", "W", "Rate of heat transfer"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate conduction heat transfer rate.

        Args:
            thermal_conductivity: Thermal conductivity as Quantity (W/(m*K)).
            area: Cross-sectional area as Quantity (m^2).
            temperature_difference: Temperature difference as Quantity (K).
            thickness: Material thickness as Quantity (m).

        Returns:
            CalculationResult with heat transfer rate output.
        """
        self.reset()

        thermal_conductivity: Quantity = kwargs["thermal_conductivity"]
        area: Quantity = kwargs["area"]
        temperature_difference: Quantity = kwargs["temperature_difference"]
        thickness: Quantity = kwargs["thickness"]

        inputs = {
            "thermal_conductivity": thermal_conductivity,
            "area": area,
            "temperature_difference": temperature_difference,
            "thickness": thickness,
        }

        # Calculate temperature gradient: delta_T / L
        temp_gradient = temperature_difference / thickness
        self.add_step(
            description="Calculate temperature gradient",
            formula="delta_T / L",
            result=temp_gradient,
            substitution=f"delta_T / L = {temperature_difference} / {thickness} = {temp_gradient}",
        )

        # Calculate heat transfer rate: Q = k * A * (delta_T / L)
        heat_transfer_rate = thermal_conductivity * area * temp_gradient
        self.add_step(
            description="Calculate heat transfer rate using Fourier's Law",
            formula="Q = k * A * (delta_T / L)",
            result=heat_transfer_rate,
            substitution=f"Q = {thermal_conductivity} * {area} * {temp_gradient} = {heat_transfer_rate}",
        )

        outputs = {
            "heat_transfer_rate": heat_transfer_rate,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ConvectionHeatTransfer(Calculation):
    """
    Calculate heat transfer rate through convection.

    Formula: Q = h * A * (Ts - T_inf)

    Where:
        Q = heat transfer rate (W)
        h = convection heat transfer coefficient (W/(m^2*K))
        A = surface area (m^2)
        Ts = surface temperature (K)
        T_inf = fluid temperature (K)
    """

    name = "Convection Heat Transfer"
    category = "Thermodynamics"
    description = (
        "Calculate heat transfer rate through convection. "
        "Q = h * A * (Ts - T_inf)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Fundamentals of Heat and Mass Transfer"]

    input_params = [
        Parameter("convection_coefficient", "W/(m**2*K)", "Convection heat transfer coefficient"),
        Parameter("surface_area", "m**2", "Surface area exposed to fluid"),
        Parameter("surface_temp", "K", "Surface temperature"),
        Parameter("fluid_temp", "K", "Bulk fluid temperature"),
    ]
    output_params = [
        Parameter("heat_transfer_rate", "W", "Rate of heat transfer"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate convection heat transfer rate.

        Args:
            convection_coefficient: Convection coefficient as Quantity (W/(m^2*K)).
            surface_area: Surface area as Quantity (m^2).
            surface_temp: Surface temperature as Quantity (K).
            fluid_temp: Fluid temperature as Quantity (K).

        Returns:
            CalculationResult with heat transfer rate output.
        """
        self.reset()

        convection_coefficient: Quantity = kwargs["convection_coefficient"]
        surface_area: Quantity = kwargs["surface_area"]
        surface_temp: Quantity = kwargs["surface_temp"]
        fluid_temp: Quantity = kwargs["fluid_temp"]

        inputs = {
            "convection_coefficient": convection_coefficient,
            "surface_area": surface_area,
            "surface_temp": surface_temp,
            "fluid_temp": fluid_temp,
        }

        # Calculate temperature difference: Ts - T_inf
        temp_difference = surface_temp - fluid_temp
        self.add_step(
            description="Calculate temperature difference between surface and fluid",
            formula="Ts - T_inf",
            result=temp_difference,
            substitution=f"Ts - T_inf = {surface_temp} - {fluid_temp} = {temp_difference}",
        )

        # Calculate heat transfer rate: Q = h * A * (Ts - T_inf)
        heat_transfer_rate = convection_coefficient * surface_area * temp_difference
        self.add_step(
            description="Calculate heat transfer rate using Newton's law of cooling",
            formula="Q = h * A * (Ts - T_inf)",
            result=heat_transfer_rate,
            substitution=f"Q = {convection_coefficient} * {surface_area} * {temp_difference} = {heat_transfer_rate}",
        )

        outputs = {
            "heat_transfer_rate": heat_transfer_rate,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class RadiationHeatTransfer(Calculation):
    """
    Calculate heat transfer rate through radiation using Stefan-Boltzmann Law.

    Formula: Q = epsilon * sigma * A * (Ts^4 - T_surr^4)

    Where:
        Q = heat transfer rate (W)
        epsilon = emissivity (dimensionless, 0-1)
        sigma = Stefan-Boltzmann constant (5.67e-8 W/(m^2*K^4))
        A = surface area (m^2)
        Ts = surface temperature (K)
        T_surr = surrounding temperature (K)
    """

    name = "Radiation Heat Transfer"
    category = "Thermodynamics"
    description = (
        "Calculate heat transfer rate through radiation using Stefan-Boltzmann Law. "
        "Q = epsilon * sigma * A * (Ts^4 - T_surr^4)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Thermal Radiation Heat Transfer, Siegel & Howell"]

    input_params = [
        Parameter("emissivity", "dimensionless", "Surface emissivity (0-1)"),
        Parameter("surface_area", "m**2", "Radiating surface area"),
        Parameter("surface_temp", "K", "Surface temperature"),
        Parameter("surrounding_temp", "K", "Surrounding temperature"),
    ]
    output_params = [
        Parameter("heat_transfer_rate", "W", "Rate of heat transfer by radiation"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate radiation heat transfer rate.

        Args:
            emissivity: Surface emissivity as Quantity (dimensionless).
            surface_area: Surface area as Quantity (m^2).
            surface_temp: Surface temperature as Quantity (K).
            surrounding_temp: Surrounding temperature as Quantity (K).

        Returns:
            CalculationResult with heat transfer rate output.
        """
        self.reset()

        emissivity: Quantity = kwargs["emissivity"]
        surface_area: Quantity = kwargs["surface_area"]
        surface_temp: Quantity = kwargs["surface_temp"]
        surrounding_temp: Quantity = kwargs["surrounding_temp"]

        inputs = {
            "emissivity": emissivity,
            "surface_area": surface_area,
            "surface_temp": surface_temp,
            "surrounding_temp": surrounding_temp,
        }

        # Validate emissivity is between 0 and 1
        eps_value = emissivity.magnitude
        if eps_value < 0 or eps_value > 1:
            raise ValueError(f"Emissivity must be between 0 and 1, got {eps_value}")

        # Stefan-Boltzmann constant
        sigma = Quantity(STEFAN_BOLTZMANN, "W/(m**2*K**4)")
        self.add_step(
            description="Stefan-Boltzmann constant",
            formula="sigma = 5.67e-8 W/(m^2*K^4)",
            result=sigma,
            substitution=f"sigma = {STEFAN_BOLTZMANN} W/(m^2*K^4)",
        )

        # Calculate T^4 terms
        ts_fourth = surface_temp ** 4
        tsurr_fourth = surrounding_temp ** 4
        self.add_step(
            description="Calculate fourth power of temperatures",
            formula="Ts^4, T_surr^4",
            result=(ts_fourth, tsurr_fourth),
            substitution=f"Ts^4 = ({surface_temp})^4 = {ts_fourth}, T_surr^4 = ({surrounding_temp})^4 = {tsurr_fourth}",
        )

        # Calculate temperature difference term: Ts^4 - T_surr^4
        temp_fourth_diff = ts_fourth - tsurr_fourth
        self.add_step(
            description="Calculate difference of fourth power temperatures",
            formula="Ts^4 - T_surr^4",
            result=temp_fourth_diff,
            substitution=f"Ts^4 - T_surr^4 = {ts_fourth} - {tsurr_fourth} = {temp_fourth_diff}",
        )

        # Calculate heat transfer rate: Q = epsilon * sigma * A * (Ts^4 - T_surr^4)
        heat_transfer_rate = emissivity * sigma * surface_area * temp_fourth_diff
        self.add_step(
            description="Calculate heat transfer rate using Stefan-Boltzmann Law",
            formula="Q = epsilon * sigma * A * (Ts^4 - T_surr^4)",
            result=heat_transfer_rate,
            substitution=f"Q = {emissivity} * {sigma} * {surface_area} * {temp_fourth_diff} = {heat_transfer_rate}",
        )

        outputs = {
            "heat_transfer_rate": heat_transfer_rate,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ThermalResistance(Calculation):
    """
    Calculate thermal resistance for conduction through a plane wall.

    Formula: R = L / (k * A)

    Where:
        R = thermal resistance (K/W)
        L = thickness of material (m)
        k = thermal conductivity (W/(m*K))
        A = cross-sectional area (m^2)
    """

    name = "Thermal Resistance"
    category = "Thermodynamics"
    description = (
        "Calculate thermal resistance for conduction through a plane wall. "
        "R = L / (k * A)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Fundamentals of Heat and Mass Transfer"]

    input_params = [
        Parameter("thickness", "m", "Thickness of material"),
        Parameter("thermal_conductivity", "W/(m*K)", "Thermal conductivity of material"),
        Parameter("area", "m**2", "Cross-sectional area"),
    ]
    output_params = [
        Parameter("thermal_resistance", "K/W", "Thermal resistance"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate thermal resistance.

        Args:
            thickness: Material thickness as Quantity (m).
            thermal_conductivity: Thermal conductivity as Quantity (W/(m*K)).
            area: Cross-sectional area as Quantity (m^2).

        Returns:
            CalculationResult with thermal resistance output.
        """
        self.reset()

        thickness: Quantity = kwargs["thickness"]
        thermal_conductivity: Quantity = kwargs["thermal_conductivity"]
        area: Quantity = kwargs["area"]

        inputs = {
            "thickness": thickness,
            "thermal_conductivity": thermal_conductivity,
            "area": area,
        }

        # Calculate k * A
        k_times_a = thermal_conductivity * area
        self.add_step(
            description="Calculate thermal conductance factor (k * A)",
            formula="k * A",
            result=k_times_a,
            substitution=f"k * A = {thermal_conductivity} * {area} = {k_times_a}",
        )

        # Calculate thermal resistance: R = L / (k * A)
        thermal_resistance = thickness / k_times_a
        self.add_step(
            description="Calculate thermal resistance",
            formula="R = L / (k * A)",
            result=thermal_resistance,
            substitution=f"R = {thickness} / {k_times_a} = {thermal_resistance}",
        )

        outputs = {
            "thermal_resistance": thermal_resistance,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class OverallHeatTransferCoefficient(Calculation):
    """
    Calculate overall heat transfer coefficient for a plane wall with convection on both sides.

    Formula: 1/(U*A) = 1/(h1*A) + L/(k*A) + 1/(h2*A)

    Simplified for uniform area:
        1/U = 1/h1 + L/k + 1/h2

    Where:
        U = overall heat transfer coefficient (W/(m^2*K))
        h1 = inside convection coefficient (W/(m^2*K))
        h2 = outside convection coefficient (W/(m^2*K))
        L = wall thickness (m)
        k = wall thermal conductivity (W/(m*K))
        A = heat transfer area (m^2)
    """

    name = "Overall Heat Transfer Coefficient"
    category = "Thermodynamics"
    description = (
        "Calculate overall heat transfer coefficient for a plane wall. "
        "1/(U*A) = 1/(h1*A) + L/(k*A) + 1/(h2*A)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Heat Exchangers: Selection, Rating, and Thermal Design"]

    input_params = [
        Parameter("h_inside", "W/(m**2*K)", "Inside convection coefficient"),
        Parameter("h_outside", "W/(m**2*K)", "Outside convection coefficient"),
        Parameter("wall_thickness", "m", "Wall thickness"),
        Parameter("wall_conductivity", "W/(m*K)", "Wall thermal conductivity"),
        Parameter("area", "m**2", "Heat transfer area"),
    ]
    output_params = [
        Parameter("overall_coefficient", "W/(m**2*K)", "Overall heat transfer coefficient (U)"),
        Parameter("UA_value", "W/K", "Overall thermal conductance (U*A)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate overall heat transfer coefficient.

        Args:
            h_inside: Inside convection coefficient as Quantity (W/(m^2*K)).
            h_outside: Outside convection coefficient as Quantity (W/(m^2*K)).
            wall_thickness: Wall thickness as Quantity (m).
            wall_conductivity: Wall thermal conductivity as Quantity (W/(m*K)).
            area: Heat transfer area as Quantity (m^2).

        Returns:
            CalculationResult with overall coefficient and UA value.
        """
        self.reset()

        h_inside: Quantity = kwargs["h_inside"]
        h_outside: Quantity = kwargs["h_outside"]
        wall_thickness: Quantity = kwargs["wall_thickness"]
        wall_conductivity: Quantity = kwargs["wall_conductivity"]
        area: Quantity = kwargs["area"]

        inputs = {
            "h_inside": h_inside,
            "h_outside": h_outside,
            "wall_thickness": wall_thickness,
            "wall_conductivity": wall_conductivity,
            "area": area,
        }

        # Calculate inside convection resistance: 1/(h1*A)
        r_conv_inside = Quantity(1.0, "dimensionless") / (h_inside * area)
        self.add_step(
            description="Calculate inside convection resistance",
            formula="R_conv_in = 1 / (h1 * A)",
            result=r_conv_inside,
            substitution=f"R_conv_in = 1 / ({h_inside} * {area}) = {r_conv_inside}",
        )

        # Calculate wall conduction resistance: L/(k*A)
        r_cond_wall = wall_thickness / (wall_conductivity * area)
        self.add_step(
            description="Calculate wall conduction resistance",
            formula="R_cond = L / (k * A)",
            result=r_cond_wall,
            substitution=f"R_cond = {wall_thickness} / ({wall_conductivity} * {area}) = {r_cond_wall}",
        )

        # Calculate outside convection resistance: 1/(h2*A)
        r_conv_outside = Quantity(1.0, "dimensionless") / (h_outside * area)
        self.add_step(
            description="Calculate outside convection resistance",
            formula="R_conv_out = 1 / (h2 * A)",
            result=r_conv_outside,
            substitution=f"R_conv_out = 1 / ({h_outside} * {area}) = {r_conv_outside}",
        )

        # Calculate total resistance: R_total = R_conv_in + R_cond + R_conv_out
        r_total = r_conv_inside + r_cond_wall + r_conv_outside
        self.add_step(
            description="Calculate total thermal resistance",
            formula="R_total = R_conv_in + R_cond + R_conv_out",
            result=r_total,
            substitution=f"R_total = {r_conv_inside} + {r_cond_wall} + {r_conv_outside} = {r_total}",
        )

        # Calculate UA = 1/R_total
        ua_value = Quantity(1.0, "dimensionless") / r_total
        self.add_step(
            description="Calculate overall thermal conductance (UA)",
            formula="UA = 1 / R_total",
            result=ua_value,
            substitution=f"UA = 1 / {r_total} = {ua_value}",
        )

        # Calculate U = UA / A
        overall_coefficient = ua_value / area
        self.add_step(
            description="Calculate overall heat transfer coefficient",
            formula="U = UA / A",
            result=overall_coefficient,
            substitution=f"U = {ua_value} / {area} = {overall_coefficient}",
        )

        outputs = {
            "overall_coefficient": overall_coefficient,
            "UA_value": ua_value,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CarnotEfficiency(Calculation):
    """
    Calculate Carnot efficiency for a heat engine.

    Formula: eta = 1 - Tc/Th

    Where:
        eta = Carnot efficiency (dimensionless)
        Tc = cold reservoir temperature (K)
        Th = hot reservoir temperature (K)

    Note: This represents the maximum theoretical efficiency for any heat engine
    operating between two temperature reservoirs.
    """

    name = "Carnot Efficiency"
    category = "Thermodynamics"
    description = (
        "Calculate Carnot efficiency (maximum theoretical efficiency) for a heat engine. "
        "eta = 1 - Tc/Th"
    )
    references = ["Thermodynamics: An Engineering Approach, Cengel & Boles", "Fundamentals of Engineering Thermodynamics, Moran"]

    input_params = [
        Parameter("hot_temp", "K", "Hot reservoir temperature"),
        Parameter("cold_temp", "K", "Cold reservoir temperature"),
    ]
    output_params = [
        Parameter("efficiency", "dimensionless", "Carnot efficiency (as decimal, multiply by 100 for percentage)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate Carnot efficiency.

        Args:
            hot_temp: Hot reservoir temperature as Quantity (K).
            cold_temp: Cold reservoir temperature as Quantity (K).

        Returns:
            CalculationResult with efficiency output.
        """
        self.reset()

        hot_temp: Quantity = kwargs["hot_temp"]
        cold_temp: Quantity = kwargs["cold_temp"]

        inputs = {
            "hot_temp": hot_temp,
            "cold_temp": cold_temp,
        }

        # Validate temperatures
        th_value = hot_temp.magnitude
        tc_value = cold_temp.magnitude

        if th_value <= 0 or tc_value <= 0:
            raise ValueError("Temperatures must be positive (in Kelvin)")
        if tc_value >= th_value:
            raise ValueError(f"Hot temperature ({th_value} K) must be greater than cold temperature ({tc_value} K)")

        # Calculate temperature ratio: Tc/Th
        temp_ratio = cold_temp / hot_temp
        self.add_step(
            description="Calculate temperature ratio",
            formula="Tc / Th",
            result=temp_ratio,
            substitution=f"Tc / Th = {cold_temp} / {hot_temp} = {temp_ratio}",
        )

        # Calculate Carnot efficiency: eta = 1 - Tc/Th
        efficiency_value = 1.0 - temp_ratio.magnitude
        efficiency = Quantity(efficiency_value, "dimensionless")
        self.add_step(
            description="Calculate Carnot efficiency",
            formula="eta = 1 - Tc/Th",
            result=efficiency,
            substitution=f"eta = 1 - {temp_ratio} = {efficiency} ({efficiency_value * 100:.2f}%)",
        )

        outputs = {
            "efficiency": efficiency,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class RefrigerationCOP(Calculation):
    """
    Calculate ideal coefficient of performance (COP) for a refrigeration cycle.

    Formula: COP = Tc / (Th - Tc)

    Where:
        COP = coefficient of performance (dimensionless)
        Tc = cold reservoir temperature (K)
        Th = hot reservoir temperature (K)

    Note: This represents the maximum theoretical COP for an ideal (Carnot) refrigeration cycle.
    """

    name = "Refrigeration COP"
    category = "Thermodynamics"
    description = (
        "Calculate ideal coefficient of performance (COP) for a refrigeration cycle. "
        "COP = Tc / (Th - Tc)"
    )
    references = ["Thermodynamics: An Engineering Approach, Cengel & Boles", "Refrigeration and Air Conditioning, Stoecker"]

    input_params = [
        Parameter("cold_temp", "K", "Cold reservoir temperature (evaporator)"),
        Parameter("hot_temp", "K", "Hot reservoir temperature (condenser)"),
    ]
    output_params = [
        Parameter("cop_ideal", "dimensionless", "Ideal coefficient of performance"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate ideal refrigeration COP.

        Args:
            cold_temp: Cold reservoir temperature as Quantity (K).
            hot_temp: Hot reservoir temperature as Quantity (K).

        Returns:
            CalculationResult with ideal COP output.
        """
        self.reset()

        cold_temp: Quantity = kwargs["cold_temp"]
        hot_temp: Quantity = kwargs["hot_temp"]

        inputs = {
            "cold_temp": cold_temp,
            "hot_temp": hot_temp,
        }

        # Validate temperatures
        th_value = hot_temp.magnitude
        tc_value = cold_temp.magnitude

        if th_value <= 0 or tc_value <= 0:
            raise ValueError("Temperatures must be positive (in Kelvin)")
        if tc_value >= th_value:
            raise ValueError(f"Hot temperature ({th_value} K) must be greater than cold temperature ({tc_value} K)")

        # Calculate temperature difference: Th - Tc
        temp_difference = hot_temp - cold_temp
        self.add_step(
            description="Calculate temperature difference",
            formula="Th - Tc",
            result=temp_difference,
            substitution=f"Th - Tc = {hot_temp} - {cold_temp} = {temp_difference}",
        )

        # Calculate ideal COP: COP = Tc / (Th - Tc)
        cop_value = tc_value / (th_value - tc_value)
        cop_ideal = Quantity(cop_value, "dimensionless")
        self.add_step(
            description="Calculate ideal coefficient of performance",
            formula="COP = Tc / (Th - Tc)",
            result=cop_ideal,
            substitution=f"COP = {cold_temp} / {temp_difference} = {cop_ideal}",
        )

        outputs = {
            "cop_ideal": cop_ideal,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class LogMeanTempDifference(Calculation):
    """
    Calculate log mean temperature difference (LMTD) for heat exchanger analysis.

    Formula: LMTD = (delta_T1 - delta_T2) / ln(delta_T1 / delta_T2)

    Where:
        LMTD = log mean temperature difference (K)
        delta_T1 = temperature difference at one end of heat exchanger (K)
        delta_T2 = temperature difference at other end of heat exchanger (K)

    Special case: If delta_T1 = delta_T2, LMTD = delta_T1 (to avoid division by zero).
    """

    name = "Log Mean Temperature Difference"
    category = "Thermodynamics"
    description = (
        "Calculate log mean temperature difference (LMTD) for heat exchanger analysis. "
        "LMTD = (delta_T1 - delta_T2) / ln(delta_T1 / delta_T2)"
    )
    references = ["Heat Transfer, Incropera & DeWitt", "Heat Exchangers: Selection, Rating, and Thermal Design"]

    input_params = [
        Parameter("delta_t1", "K", "Temperature difference at one end of heat exchanger"),
        Parameter("delta_t2", "K", "Temperature difference at other end of heat exchanger"),
    ]
    output_params = [
        Parameter("lmtd", "K", "Log mean temperature difference"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate log mean temperature difference.

        Args:
            delta_t1: Temperature difference at one end as Quantity (K).
            delta_t2: Temperature difference at other end as Quantity (K).

        Returns:
            CalculationResult with LMTD output.
        """
        self.reset()

        delta_t1: Quantity = kwargs["delta_t1"]
        delta_t2: Quantity = kwargs["delta_t2"]

        inputs = {
            "delta_t1": delta_t1,
            "delta_t2": delta_t2,
        }

        # Validate temperature differences are positive
        dt1_value = delta_t1.magnitude
        dt2_value = delta_t2.magnitude

        if dt1_value <= 0 or dt2_value <= 0:
            raise ValueError("Temperature differences must be positive")

        # Check for special case where delta_T1 = delta_T2
        if abs(dt1_value - dt2_value) < 1e-10:
            lmtd = delta_t1
            self.add_step(
                description="Special case: delta_T1 equals delta_T2",
                formula="LMTD = delta_T1 (when delta_T1 = delta_T2)",
                result=lmtd,
                substitution=f"LMTD = {delta_t1} (special case)",
            )
        else:
            # Calculate temperature ratio: delta_T1 / delta_T2
            temp_ratio = dt1_value / dt2_value
            self.add_step(
                description="Calculate temperature difference ratio",
                formula="delta_T1 / delta_T2",
                result=temp_ratio,
                substitution=f"delta_T1 / delta_T2 = {dt1_value} / {dt2_value} = {temp_ratio:.6f}",
            )

            # Calculate natural log of ratio
            ln_ratio = math.log(temp_ratio)
            self.add_step(
                description="Calculate natural logarithm of ratio",
                formula="ln(delta_T1 / delta_T2)",
                result=ln_ratio,
                substitution=f"ln({temp_ratio:.6f}) = {ln_ratio:.6f}",
            )

            # Calculate numerator: delta_T1 - delta_T2
            temp_diff = delta_t1 - delta_t2
            self.add_step(
                description="Calculate temperature difference",
                formula="delta_T1 - delta_T2",
                result=temp_diff,
                substitution=f"delta_T1 - delta_T2 = {delta_t1} - {delta_t2} = {temp_diff}",
            )

            # Calculate LMTD: (delta_T1 - delta_T2) / ln(delta_T1 / delta_T2)
            lmtd_value = (dt1_value - dt2_value) / ln_ratio
            lmtd = Quantity(lmtd_value, "K")
            self.add_step(
                description="Calculate log mean temperature difference",
                formula="LMTD = (delta_T1 - delta_T2) / ln(delta_T1 / delta_T2)",
                result=lmtd,
                substitution=f"LMTD = {temp_diff} / {ln_ratio:.6f} = {lmtd}",
            )

        outputs = {
            "lmtd": lmtd,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "ConductionHeatTransfer",
    "ConvectionHeatTransfer",
    "RadiationHeatTransfer",
    "ThermalResistance",
    "OverallHeatTransferCoefficient",
    "CarnotEfficiency",
    "RefrigerationCOP",
    "LogMeanTempDifference",
]
