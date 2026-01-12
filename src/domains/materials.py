"""
Strength and Materials Calculations for Engineering Calculations Database.

This module implements fundamental strength of materials calculations including
stress, strain, and failure criteria calculations. All calculations extend the
base Calculation class and use the Quantity class for unit-aware operations.

References:
    - Beer, F.P., Johnston, E.R., et al. "Mechanics of Materials", 7th Ed.
    - Hibbeler, R.C. "Mechanics of Materials", 10th Ed.
    - Shigley, J.E., Mischke, C.R. "Mechanical Engineering Design", 9th Ed.
"""

from __future__ import annotations

import math
from typing import List

from src.core.calculations import (
    Calculation,
    CalculationResult,
    ParameterDefinition,
    register_calculation,
)
from src.core.units import Quantity
from src.core.validation import (
    PositiveValidator,
    NonZeroValidator,
    ValidationError,
)


@register_calculation
class AxialStress(Calculation):
    """
    Calculate axial (normal) stress from force and cross-sectional area.

    The axial stress is the internal force per unit area acting perpendicular
    to the cross-section. This is the fundamental stress calculation for
    members under tension or compression.

    Formula:
        sigma = F / A

    Where:
        sigma = Axial stress (Pa)
        F = Applied force (N)
        A = Cross-sectional area (m^2)

    References:
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 1
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 1.2
    """

    name = "Axial Stress"
    category = "Materials"
    description = (
        "Calculates the axial (normal) stress in a member subjected to "
        "an axial force. Stress equals force divided by cross-sectional area."
    )
    references = [
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 1",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 1.2",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="force",
            unit="N",
            description="Applied axial force (tension positive, compression negative)",
        ),
        ParameterDefinition(
            name="area",
            unit="m**2",
            description="Cross-sectional area perpendicular to the force",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="stress",
            unit="Pa",
            description="Resulting axial stress (tension positive, compression negative)",
        ),
    ]

    def calculate(self, force: Quantity, area: Quantity) -> CalculationResult:
        """
        Calculate axial stress from force and area.

        Args:
            force: Applied axial force (N). Positive for tension, negative for compression.
            area: Cross-sectional area (m^2). Must be positive.

        Returns:
            CalculationResult containing the calculated stress and intermediate steps.

        Raises:
            ValidationError: If area is not positive.
        """
        self._clear_steps()

        # Validate inputs
        validator = PositiveValidator()
        validator.validate(area, "area")

        # Convert to base units for calculation
        force_n = force.to("N")
        area_m2 = area.to("m**2")

        # Calculate stress
        stress_value = force_n.magnitude / area_m2.magnitude
        stress = Quantity(stress_value, "Pa")

        # Record intermediate step
        self._add_step(
            description="Calculate axial stress using sigma = F / A",
            formula=r"\sigma = \frac{F}{A}",
            inputs={
                "F": f"{force_n.magnitude:.4g} N",
                "A": f"{area_m2.magnitude:.4g} m^2",
            },
            result=stress,
            result_name="sigma",
        )

        # Create and return result
        return self._create_result(
            inputs={"force": force, "area": area},
            outputs={"stress": stress},
        )


@register_calculation
class ShearStress(Calculation):
    """
    Calculate shear stress from shear force and area.

    Shear stress is the component of stress coplanar with the cross-section,
    resulting from forces applied parallel to the surface.

    Formula:
        tau = V / A

    Where:
        tau = Shear stress (Pa)
        V = Shear force (N)
        A = Area over which shear acts (m^2)

    References:
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 1
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 1.5
    """

    name = "Shear Stress"
    category = "Materials"
    description = (
        "Calculates the average shear stress acting on a cross-section. "
        "Shear stress equals shear force divided by the shear area."
    )
    references = [
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 1",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 1.5",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="shear_force",
            unit="N",
            description="Applied shear force",
        ),
        ParameterDefinition(
            name="area",
            unit="m**2",
            description="Area over which the shear force acts",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="shear_stress",
            unit="Pa",
            description="Resulting average shear stress",
        ),
    ]

    def calculate(self, shear_force: Quantity, area: Quantity) -> CalculationResult:
        """
        Calculate shear stress from shear force and area.

        Args:
            shear_force: Applied shear force (N).
            area: Area over which shear acts (m^2). Must be positive.

        Returns:
            CalculationResult containing the calculated shear stress.

        Raises:
            ValidationError: If area is not positive.
        """
        self._clear_steps()

        # Validate inputs
        validator = PositiveValidator()
        validator.validate(area, "area")

        # Convert to base units
        force_n = shear_force.to("N")
        area_m2 = area.to("m**2")

        # Calculate shear stress
        shear_stress_value = abs(force_n.magnitude) / area_m2.magnitude
        shear_stress = Quantity(shear_stress_value, "Pa")

        # Record intermediate step
        self._add_step(
            description="Calculate shear stress using tau = V / A",
            formula=r"\tau = \frac{V}{A}",
            inputs={
                "V": f"{force_n.magnitude:.4g} N",
                "A": f"{area_m2.magnitude:.4g} m^2",
            },
            result=shear_stress,
            result_name="tau",
        )

        return self._create_result(
            inputs={"shear_force": shear_force, "area": area},
            outputs={"shear_stress": shear_stress},
        )


@register_calculation
class Strain(Calculation):
    """
    Calculate engineering strain from deformation and original length.

    Engineering strain (also called nominal strain or Cauchy strain) is the
    ratio of the change in length to the original length.

    Formula:
        epsilon = delta_L / L

    Where:
        epsilon = Strain (dimensionless)
        delta_L = Change in length (m)
        L = Original length (m)

    References:
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 2
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 2.2
    """

    name = "Strain"
    category = "Materials"
    description = (
        "Calculates engineering strain from the change in length and "
        "original length. Strain is a dimensionless quantity."
    )
    references = [
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 2",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 2.2",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="change_in_length",
            unit="m",
            description="Change in length (elongation positive, contraction negative)",
        ),
        ParameterDefinition(
            name="original_length",
            unit="m",
            description="Original (undeformed) length",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="strain",
            unit="dimensionless",
            description="Engineering strain (elongation positive)",
        ),
    ]

    def calculate(
        self, change_in_length: Quantity, original_length: Quantity
    ) -> CalculationResult:
        """
        Calculate strain from change in length and original length.

        Args:
            change_in_length: Change in length (m). Positive for elongation.
            original_length: Original length (m). Must be positive.

        Returns:
            CalculationResult containing the calculated strain.

        Raises:
            ValidationError: If original_length is not positive.
        """
        self._clear_steps()

        # Validate inputs
        validator = PositiveValidator()
        validator.validate(original_length, "original_length")

        # Convert to same units for calculation
        delta_l = change_in_length.to("m")
        length = original_length.to("m")

        # Calculate strain
        strain_value = delta_l.magnitude / length.magnitude
        strain = Quantity(strain_value, "dimensionless")

        # Record intermediate step
        self._add_step(
            description="Calculate strain using epsilon = delta_L / L",
            formula=r"\varepsilon = \frac{\Delta L}{L}",
            inputs={
                "delta_L": f"{delta_l.magnitude:.4g} m",
                "L": f"{length.magnitude:.4g} m",
            },
            result=strain,
            result_name="epsilon",
        )

        return self._create_result(
            inputs={"change_in_length": change_in_length, "original_length": original_length},
            outputs={"strain": strain},
        )


@register_calculation
class HookesLaw(Calculation):
    """
    Calculate stress from elastic modulus and strain using Hooke's Law.

    Hooke's Law describes the linear relationship between stress and strain
    in the elastic region of a material's stress-strain curve.

    Formula:
        sigma = E * epsilon

    Where:
        sigma = Stress (Pa)
        E = Elastic modulus / Young's modulus (Pa)
        epsilon = Strain (dimensionless)

    References:
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 2
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 3.1
    """

    name = "Hooke's Law"
    category = "Materials"
    description = (
        "Calculates stress from elastic modulus and strain using Hooke's Law. "
        "Valid only in the linear elastic region of the material."
    )
    references = [
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 2",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 3.1",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="elastic_modulus",
            unit="Pa",
            description="Elastic modulus (Young's modulus) of the material",
        ),
        ParameterDefinition(
            name="strain",
            unit="dimensionless",
            description="Engineering strain",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="stress",
            unit="Pa",
            description="Resulting stress",
        ),
    ]

    def calculate(
        self, elastic_modulus: Quantity, strain: Quantity
    ) -> CalculationResult:
        """
        Calculate stress from elastic modulus and strain.

        Args:
            elastic_modulus: Young's modulus (Pa). Must be positive.
            strain: Engineering strain (dimensionless).

        Returns:
            CalculationResult containing the calculated stress.

        Raises:
            ValidationError: If elastic_modulus is not positive.
        """
        self._clear_steps()

        # Validate inputs
        validator = PositiveValidator()
        validator.validate(elastic_modulus, "elastic_modulus")

        # Get values in consistent units
        E = elastic_modulus.to("Pa")
        eps = strain.magnitude  # Strain is dimensionless

        # Calculate stress
        stress_value = E.magnitude * eps
        stress = Quantity(stress_value, "Pa")

        # Record intermediate step
        self._add_step(
            description="Calculate stress using Hooke's Law: sigma = E * epsilon",
            formula=r"\sigma = E \cdot \varepsilon",
            inputs={
                "E": f"{E.magnitude:.4g} Pa",
                "epsilon": f"{eps:.6g}",
            },
            result=stress,
            result_name="sigma",
        )

        return self._create_result(
            inputs={"elastic_modulus": elastic_modulus, "strain": strain},
            outputs={"stress": stress},
        )


@register_calculation
class ThermalStress(Calculation):
    """
    Calculate thermal stress from temperature change in a constrained member.

    When a material is constrained from expanding or contracting freely,
    a change in temperature induces thermal stress.

    Formula:
        sigma = E * alpha * delta_T

    Where:
        sigma = Thermal stress (Pa)
        E = Elastic modulus (Pa)
        alpha = Coefficient of thermal expansion (1/K)
        delta_T = Temperature change (K)

    References:
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 2
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 4.6
    """

    name = "Thermal Stress"
    category = "Materials"
    description = (
        "Calculates the thermal stress induced in a fully constrained member "
        "due to temperature change. Assumes complete constraint."
    )
    references = [
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 2",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 4.6",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="elastic_modulus",
            unit="Pa",
            description="Elastic modulus (Young's modulus) of the material",
        ),
        ParameterDefinition(
            name="thermal_coefficient",
            unit="1/K",
            description="Coefficient of thermal expansion",
        ),
        ParameterDefinition(
            name="temperature_change",
            unit="K",
            description="Change in temperature (positive for heating)",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="stress",
            unit="Pa",
            description="Resulting thermal stress (compressive for heating if constrained)",
        ),
    ]

    def calculate(
        self,
        elastic_modulus: Quantity,
        thermal_coefficient: Quantity,
        temperature_change: Quantity,
    ) -> CalculationResult:
        """
        Calculate thermal stress in a constrained member.

        Args:
            elastic_modulus: Young's modulus (Pa). Must be positive.
            thermal_coefficient: Coefficient of thermal expansion (1/K). Must be positive.
            temperature_change: Temperature change (K or degC).

        Returns:
            CalculationResult containing the calculated thermal stress.

        Raises:
            ValidationError: If elastic_modulus or thermal_coefficient is not positive.
        """
        self._clear_steps()

        # Validate inputs
        validator = PositiveValidator()
        validator.validate(elastic_modulus, "elastic_modulus")
        validator.validate(thermal_coefficient, "thermal_coefficient")

        # Get values in consistent units
        E = elastic_modulus.to("Pa")
        alpha = thermal_coefficient.to("1/K")
        delta_T = temperature_change.to("K")

        # Calculate thermal stress
        # Note: For a heated constrained member, stress is compressive (negative)
        # The formula gives magnitude; sign depends on constraint type
        stress_value = E.magnitude * alpha.magnitude * delta_T.magnitude
        stress = Quantity(stress_value, "Pa")

        # Record intermediate steps
        self._add_step(
            description="Calculate thermal strain: epsilon_T = alpha * delta_T",
            formula=r"\varepsilon_T = \alpha \cdot \Delta T",
            inputs={
                "alpha": f"{alpha.magnitude:.4g} 1/K",
                "delta_T": f"{delta_T.magnitude:.4g} K",
            },
            result=Quantity(alpha.magnitude * delta_T.magnitude, "dimensionless"),
            result_name="epsilon_T",
        )

        self._add_step(
            description="Calculate thermal stress: sigma = E * epsilon_T",
            formula=r"\sigma = E \cdot \varepsilon_T = E \cdot \alpha \cdot \Delta T",
            inputs={
                "E": f"{E.magnitude:.4g} Pa",
                "epsilon_T": f"{alpha.magnitude * delta_T.magnitude:.6g}",
            },
            result=stress,
            result_name="sigma",
        )

        return self._create_result(
            inputs={
                "elastic_modulus": elastic_modulus,
                "thermal_coefficient": thermal_coefficient,
                "temperature_change": temperature_change,
            },
            outputs={"stress": stress},
        )


@register_calculation
class FactorOfSafety(Calculation):
    """
    Calculate the factor of safety for a structural member.

    The factor of safety (FoS) is the ratio of the allowable (or yield) stress
    to the actual working stress. A FoS greater than 1 indicates a safe design.

    Formula:
        FoS = sigma_allowable / sigma_actual

    Where:
        FoS = Factor of safety (dimensionless)
        sigma_allowable = Allowable or yield stress (Pa)
        sigma_actual = Actual working stress (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 1
        - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Section 1.7
    """

    name = "Factor of Safety"
    category = "Materials"
    description = (
        "Calculates the factor of safety as the ratio of allowable stress "
        "to actual stress. FoS > 1 indicates the design is safe."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 1",
        "Hibbeler, R.C. 'Mechanics of Materials', 10th Ed., Section 1.7",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="allowable_stress",
            unit="Pa",
            description="Allowable stress (or yield stress) of the material",
        ),
        ParameterDefinition(
            name="actual_stress",
            unit="Pa",
            description="Actual working stress in the member",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="factor_of_safety",
            unit="dimensionless",
            description="Factor of safety (FoS > 1 is safe)",
        ),
    ]

    def calculate(
        self, allowable_stress: Quantity, actual_stress: Quantity
    ) -> CalculationResult:
        """
        Calculate the factor of safety.

        Args:
            allowable_stress: Allowable or yield stress (Pa). Must be positive.
            actual_stress: Actual working stress (Pa). Must be non-zero.

        Returns:
            CalculationResult containing the calculated factor of safety.

        Raises:
            ValidationError: If allowable_stress is not positive or actual_stress is zero.
        """
        self._clear_steps()

        # Validate inputs
        pos_validator = PositiveValidator()
        pos_validator.validate(allowable_stress, "allowable_stress")

        nonzero_validator = NonZeroValidator()
        nonzero_validator.validate(actual_stress, "actual_stress")

        # Get values in consistent units
        sigma_allow = allowable_stress.to("Pa")
        sigma_actual = actual_stress.to("Pa")

        # Calculate factor of safety (use absolute value of actual stress)
        fos_value = sigma_allow.magnitude / abs(sigma_actual.magnitude)
        factor_of_safety = Quantity(fos_value, "dimensionless")

        # Record intermediate step
        self._add_step(
            description="Calculate factor of safety: FoS = sigma_allowable / sigma_actual",
            formula=r"FoS = \frac{\sigma_{allowable}}{\sigma_{actual}}",
            inputs={
                "sigma_allowable": f"{sigma_allow.magnitude:.4g} Pa",
                "sigma_actual": f"{sigma_actual.magnitude:.4g} Pa",
            },
            result=factor_of_safety,
            result_name="FoS",
        )

        # Add note about safety
        note = None
        if fos_value < 1.0:
            note = "WARNING: Factor of safety < 1.0 indicates potential failure!"
        elif fos_value < 1.5:
            note = "CAUTION: Factor of safety < 1.5 may be inadequate for some applications."

        result = self._create_result(
            inputs={"allowable_stress": allowable_stress, "actual_stress": actual_stress},
            outputs={"factor_of_safety": factor_of_safety},
        )
        if note:
            result.metadata["warning"] = note

        return result


@register_calculation
class VonMisesStress(Calculation):
    """
    Calculate the von Mises equivalent stress for plane stress conditions.

    The von Mises stress (also called equivalent stress) is used to predict
    yielding of ductile materials under complex loading conditions.

    Formula (2D plane stress):
        sigma_vm = sqrt(sigma_x^2 - sigma_x*sigma_y + sigma_y^2 + 3*tau^2)

    Where:
        sigma_vm = Von Mises equivalent stress (Pa)
        sigma_x = Normal stress in x-direction (Pa)
        sigma_y = Normal stress in y-direction (Pa)
        tau = Shear stress (Pa)

    References:
        - Shigley, J.E., Mischke, C.R., "Mechanical Engineering Design", 9th Ed., Ch. 5
        - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 7
    """

    name = "Von Mises Stress"
    category = "Materials"
    description = (
        "Calculates the von Mises equivalent stress for 2D plane stress "
        "conditions. Used to predict yielding under complex loading."
    )
    references = [
        "Shigley, Mischke, 'Mechanical Engineering Design', 9th Ed., Ch. 5",
        "Beer, Johnston, et al. 'Mechanics of Materials', 7th Ed., Ch. 7",
    ]

    input_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="stress_x",
            unit="Pa",
            description="Normal stress in x-direction",
        ),
        ParameterDefinition(
            name="stress_y",
            unit="Pa",
            description="Normal stress in y-direction",
        ),
        ParameterDefinition(
            name="shear_stress",
            unit="Pa",
            description="Shear stress (tau_xy)",
        ),
    ]

    output_definitions: List[ParameterDefinition] = [
        ParameterDefinition(
            name="von_mises_stress",
            unit="Pa",
            description="Von Mises equivalent stress",
        ),
    ]

    def calculate(
        self, stress_x: Quantity, stress_y: Quantity, shear_stress: Quantity
    ) -> CalculationResult:
        """
        Calculate the von Mises equivalent stress.

        Args:
            stress_x: Normal stress in x-direction (Pa).
            stress_y: Normal stress in y-direction (Pa).
            shear_stress: Shear stress (Pa).

        Returns:
            CalculationResult containing the von Mises stress.
        """
        self._clear_steps()

        # Get values in consistent units
        sigma_x = stress_x.to("Pa")
        sigma_y = stress_y.to("Pa")
        tau = shear_stress.to("Pa")

        # Extract magnitudes
        sx = sigma_x.magnitude
        sy = sigma_y.magnitude
        t = tau.magnitude

        # Calculate intermediate terms
        term1 = sx**2
        term2 = -sx * sy
        term3 = sy**2
        term4 = 3 * t**2

        # Record intermediate step for the squared terms
        self._add_step(
            description="Calculate stress squared terms",
            formula=r"\sigma_x^2 = {:.4g}, \quad -\sigma_x \sigma_y = {:.4g}, \quad \sigma_y^2 = {:.4g}, \quad 3\tau^2 = {:.4g}".format(
                term1, term2, term3, term4
            ),
            inputs={
                "sigma_x": f"{sx:.4g} Pa",
                "sigma_y": f"{sy:.4g} Pa",
                "tau": f"{t:.4g} Pa",
            },
            result=Quantity(term1 + term2 + term3 + term4, "Pa**2"),
            result_name="sum_terms",
        )

        # Calculate von Mises stress
        vm_squared = term1 + term2 + term3 + term4
        vm_value = math.sqrt(vm_squared)
        von_mises_stress = Quantity(vm_value, "Pa")

        # Record final step
        self._add_step(
            description="Calculate von Mises stress",
            formula=r"\sigma_{vm} = \sqrt{\sigma_x^2 - \sigma_x \sigma_y + \sigma_y^2 + 3\tau^2}",
            inputs={
                "sigma_x": f"{sx:.4g} Pa",
                "sigma_y": f"{sy:.4g} Pa",
                "tau": f"{t:.4g} Pa",
            },
            result=von_mises_stress,
            result_name="sigma_vm",
        )

        return self._create_result(
            inputs={
                "stress_x": stress_x,
                "stress_y": stress_y,
                "shear_stress": shear_stress,
            },
            outputs={"von_mises_stress": von_mises_stress},
        )


# Module exports
__all__ = [
    "AxialStress",
    "ShearStress",
    "Strain",
    "HookesLaw",
    "ThermalStress",
    "FactorOfSafety",
    "VonMisesStress",
]
