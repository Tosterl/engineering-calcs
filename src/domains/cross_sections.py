"""
Cross-sectional properties calculations for Engineering Calculations Database.

This module provides engineering calculations for various cross-section types including:
- Rectangular sections (solid)
- Circular sections (solid)
- Hollow circular sections (pipes/tubes)
- I-beam sections (wide flange)
- C-channel sections
- Hollow rectangular sections (box/tube)
- T-beam sections
- Angle sections (L-shaped)

Key properties calculated:
- Area (A)
- Moment of inertia (I, Ix, Iy)
- Section modulus (S, Sx, Sy)
- Radius of gyration (r, rx, ry)
- Polar moment of inertia (J)
- Centroid locations
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


@register
class RectangularSection(Calculation):
    """
    Calculate cross-sectional properties for a solid rectangular section.

    Properties calculated:
        - Area: A = b * h
        - Moment of inertia about x-axis: Ix = (b * h^3) / 12
        - Moment of inertia about y-axis: Iy = (h * b^3) / 12
        - Section modulus about x-axis: Sx = Ix / (h/2)
        - Section modulus about y-axis: Sy = Iy / (b/2)
        - Radius of gyration about x-axis: rx = sqrt(Ix / A)
        - Radius of gyration about y-axis: ry = sqrt(Iy / A)

    Where b is width and h is height.
    """

    name = "Rectangular Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a solid rectangular section "
        "including area, moments of inertia, section moduli, and radii of gyration."
    )
    references = ["Mechanics of Materials, Hibbeler", "AISC Steel Construction Manual"]

    input_params = [
        Parameter("width", "m", "Width of the rectangular section (b)"),
        Parameter("height", "m", "Height of the rectangular section (h)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("Ix", "m**4", "Moment of inertia about x-axis (horizontal centroidal axis)"),
        Parameter("Iy", "m**4", "Moment of inertia about y-axis (vertical centroidal axis)"),
        Parameter("Sx", "m**3", "Section modulus about x-axis"),
        Parameter("Sy", "m**3", "Section modulus about y-axis"),
        Parameter("rx", "m", "Radius of gyration about x-axis"),
        Parameter("ry", "m", "Radius of gyration about y-axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate rectangular section properties.

        Args:
            width: Width of section as Quantity (m).
            height: Height of section as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        width: Quantity = kwargs["width"]
        height: Quantity = kwargs["height"]

        inputs = {
            "width": width,
            "height": height,
        }

        # Calculate area: A = b * h
        area = width * height
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = b * h",
            result=area,
            substitution=f"A = {width} * {height} = {area}",
        )

        # Calculate Ix: Ix = (b * h^3) / 12
        height_cubed = height ** 3
        Ix = (width * height_cubed) / 12
        self.add_step(
            description="Calculate moment of inertia about x-axis",
            formula="Ix = (b * h^3) / 12",
            result=Ix,
            substitution=f"Ix = ({width} * {height}^3) / 12 = {Ix}",
        )

        # Calculate Iy: Iy = (h * b^3) / 12
        width_cubed = width ** 3
        Iy = (height * width_cubed) / 12
        self.add_step(
            description="Calculate moment of inertia about y-axis",
            formula="Iy = (h * b^3) / 12",
            result=Iy,
            substitution=f"Iy = ({height} * {width}^3) / 12 = {Iy}",
        )

        # Calculate Sx: Sx = Ix / (h/2)
        c_x = height / 2
        Sx = Ix / c_x
        self.add_step(
            description="Calculate section modulus about x-axis",
            formula="Sx = Ix / (h/2)",
            result=Sx,
            substitution=f"Sx = {Ix} / {c_x} = {Sx}",
        )

        # Calculate Sy: Sy = Iy / (b/2)
        c_y = width / 2
        Sy = Iy / c_y
        self.add_step(
            description="Calculate section modulus about y-axis",
            formula="Sy = Iy / (b/2)",
            result=Sy,
            substitution=f"Sy = {Iy} / {c_y} = {Sy}",
        )

        # Calculate rx: rx = sqrt(Ix / A)
        rx_squared = Ix / area
        rx = rx_squared ** 0.5
        self.add_step(
            description="Calculate radius of gyration about x-axis",
            formula="rx = sqrt(Ix / A)",
            result=rx,
            substitution=f"rx = sqrt({Ix} / {area}) = {rx}",
        )

        # Calculate ry: ry = sqrt(Iy / A)
        ry_squared = Iy / area
        ry = ry_squared ** 0.5
        self.add_step(
            description="Calculate radius of gyration about y-axis",
            formula="ry = sqrt(Iy / A)",
            result=ry,
            substitution=f"ry = sqrt({Iy} / {area}) = {ry}",
        )

        outputs = {
            "area": area,
            "Ix": Ix,
            "Iy": Iy,
            "Sx": Sx,
            "Sy": Sy,
            "rx": rx,
            "ry": ry,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CircularSection(Calculation):
    """
    Calculate cross-sectional properties for a solid circular section.

    Properties calculated:
        - Area: A = pi * d^2 / 4
        - Moment of inertia: I = pi * d^4 / 64
        - Section modulus: S = pi * d^3 / 32
        - Radius of gyration: r = d / 4
        - Polar moment of inertia: J = pi * d^4 / 32

    Where d is the diameter.
    """

    name = "Circular Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a solid circular section "
        "including area, moment of inertia, section modulus, radius of gyration, "
        "and polar moment of inertia."
    )
    references = ["Mechanics of Materials, Hibbeler", "Roark's Formulas for Stress and Strain"]

    input_params = [
        Parameter("diameter", "m", "Diameter of the circular section"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("I", "m**4", "Moment of inertia (same for all centroidal axes)"),
        Parameter("S", "m**3", "Section modulus"),
        Parameter("r", "m", "Radius of gyration"),
        Parameter("J", "m**4", "Polar moment of inertia"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate circular section properties.

        Args:
            diameter: Diameter of section as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        diameter: Quantity = kwargs["diameter"]

        inputs = {
            "diameter": diameter,
        }

        # Calculate area: A = pi * d^2 / 4
        d_squared = diameter ** 2
        area = d_squared * (math.pi / 4)
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = pi * d^2 / 4",
            result=area,
            substitution=f"A = pi * {diameter}^2 / 4 = {area}",
        )

        # Calculate I: I = pi * d^4 / 64
        d_fourth = diameter ** 4
        I = d_fourth * (math.pi / 64)
        self.add_step(
            description="Calculate moment of inertia",
            formula="I = pi * d^4 / 64",
            result=I,
            substitution=f"I = pi * {diameter}^4 / 64 = {I}",
        )

        # Calculate S: S = pi * d^3 / 32
        d_cubed = diameter ** 3
        S = d_cubed * (math.pi / 32)
        self.add_step(
            description="Calculate section modulus",
            formula="S = pi * d^3 / 32",
            result=S,
            substitution=f"S = pi * {diameter}^3 / 32 = {S}",
        )

        # Calculate r: r = d / 4
        r = diameter / 4
        self.add_step(
            description="Calculate radius of gyration",
            formula="r = d / 4",
            result=r,
            substitution=f"r = {diameter} / 4 = {r}",
        )

        # Calculate J: J = pi * d^4 / 32
        J = d_fourth * (math.pi / 32)
        self.add_step(
            description="Calculate polar moment of inertia",
            formula="J = pi * d^4 / 32",
            result=J,
            substitution=f"J = pi * {diameter}^4 / 32 = {J}",
        )

        outputs = {
            "area": area,
            "I": I,
            "S": S,
            "r": r,
            "J": J,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class HollowCircularSection(Calculation):
    """
    Calculate cross-sectional properties for a hollow circular section (pipe/tube).

    Properties calculated:
        - Wall thickness: t = (do - di) / 2
        - Area: A = pi * (do^2 - di^2) / 4
        - Moment of inertia: I = pi * (do^4 - di^4) / 64
        - Section modulus: S = I / (do/2)
        - Radius of gyration: r = sqrt(I / A)
        - Polar moment of inertia: J = pi * (do^4 - di^4) / 32

    Where do is outer diameter and di is inner diameter.
    """

    name = "Hollow Circular Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a hollow circular section (pipe/tube) "
        "including area, moment of inertia, section modulus, radius of gyration, "
        "polar moment of inertia, and wall thickness."
    )
    references = ["Mechanics of Materials, Hibbeler", "Roark's Formulas for Stress and Strain"]

    input_params = [
        Parameter("outer_diameter", "m", "Outer diameter of the section"),
        Parameter("inner_diameter", "m", "Inner diameter of the section"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("I", "m**4", "Moment of inertia (same for all centroidal axes)"),
        Parameter("S", "m**3", "Section modulus"),
        Parameter("r", "m", "Radius of gyration"),
        Parameter("J", "m**4", "Polar moment of inertia"),
        Parameter("wall_thickness", "m", "Wall thickness"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate hollow circular section properties.

        Args:
            outer_diameter: Outer diameter as Quantity (m).
            inner_diameter: Inner diameter as Quantity (m).

        Returns:
            CalculationResult with all section properties.

        Raises:
            ValueError: If inner diameter is greater than or equal to outer diameter.
        """
        self.reset()

        outer_diameter: Quantity = kwargs["outer_diameter"]
        inner_diameter: Quantity = kwargs["inner_diameter"]

        # Validate dimensions
        if inner_diameter.magnitude >= outer_diameter.magnitude:
            raise ValueError(
                f"Inner diameter ({inner_diameter}) must be less than outer diameter ({outer_diameter})"
            )

        inputs = {
            "outer_diameter": outer_diameter,
            "inner_diameter": inner_diameter,
        }

        # Calculate wall thickness: t = (do - di) / 2
        wall_thickness = (outer_diameter - inner_diameter) / 2
        self.add_step(
            description="Calculate wall thickness",
            formula="t = (do - di) / 2",
            result=wall_thickness,
            substitution=f"t = ({outer_diameter} - {inner_diameter}) / 2 = {wall_thickness}",
        )

        # Calculate area: A = pi * (do^2 - di^2) / 4
        do_squared = outer_diameter ** 2
        di_squared = inner_diameter ** 2
        area = (do_squared - di_squared) * (math.pi / 4)
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = pi * (do^2 - di^2) / 4",
            result=area,
            substitution=f"A = pi * ({outer_diameter}^2 - {inner_diameter}^2) / 4 = {area}",
        )

        # Calculate I: I = pi * (do^4 - di^4) / 64
        do_fourth = outer_diameter ** 4
        di_fourth = inner_diameter ** 4
        I = (do_fourth - di_fourth) * (math.pi / 64)
        self.add_step(
            description="Calculate moment of inertia",
            formula="I = pi * (do^4 - di^4) / 64",
            result=I,
            substitution=f"I = pi * ({outer_diameter}^4 - {inner_diameter}^4) / 64 = {I}",
        )

        # Calculate S: S = I / (do/2)
        c = outer_diameter / 2
        S = I / c
        self.add_step(
            description="Calculate section modulus",
            formula="S = I / (do/2)",
            result=S,
            substitution=f"S = {I} / {c} = {S}",
        )

        # Calculate r: r = sqrt(I / A)
        r_squared = I / area
        r = r_squared ** 0.5
        self.add_step(
            description="Calculate radius of gyration",
            formula="r = sqrt(I / A)",
            result=r,
            substitution=f"r = sqrt({I} / {area}) = {r}",
        )

        # Calculate J: J = pi * (do^4 - di^4) / 32
        J = (do_fourth - di_fourth) * (math.pi / 32)
        self.add_step(
            description="Calculate polar moment of inertia",
            formula="J = pi * (do^4 - di^4) / 32",
            result=J,
            substitution=f"J = pi * ({outer_diameter}^4 - {inner_diameter}^4) / 32 = {J}",
        )

        outputs = {
            "area": area,
            "I": I,
            "S": S,
            "r": r,
            "J": J,
            "wall_thickness": wall_thickness,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class IBeamSection(Calculation):
    """
    Calculate cross-sectional properties for an I-beam (wide flange) section.

    The I-beam consists of:
        - Two flanges (top and bottom) with width bf and thickness tf
        - A web with height hw = H - 2*tf and thickness tw

    Properties calculated:
        - Area: A = 2*bf*tf + (H - 2*tf)*tw
        - Ix: About horizontal centroidal axis
        - Iy: About vertical centroidal axis
        - Sx, Sy: Section moduli
        - rx, ry: Radii of gyration
    """

    name = "I-Beam Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for an I-beam (wide flange) section "
        "including area, moments of inertia, section moduli, and radii of gyration."
    )
    references = ["AISC Steel Construction Manual", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("total_height", "m", "Total height of the I-beam (H)"),
        Parameter("flange_width", "m", "Width of the flanges (bf)"),
        Parameter("flange_thickness", "m", "Thickness of the flanges (tf)"),
        Parameter("web_thickness", "m", "Thickness of the web (tw)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("Ix", "m**4", "Moment of inertia about x-axis (strong axis)"),
        Parameter("Iy", "m**4", "Moment of inertia about y-axis (weak axis)"),
        Parameter("Sx", "m**3", "Section modulus about x-axis"),
        Parameter("Sy", "m**3", "Section modulus about y-axis"),
        Parameter("rx", "m", "Radius of gyration about x-axis"),
        Parameter("ry", "m", "Radius of gyration about y-axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate I-beam section properties.

        Args:
            total_height: Total height of I-beam as Quantity (m).
            flange_width: Flange width as Quantity (m).
            flange_thickness: Flange thickness as Quantity (m).
            web_thickness: Web thickness as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        total_height: Quantity = kwargs["total_height"]
        flange_width: Quantity = kwargs["flange_width"]
        flange_thickness: Quantity = kwargs["flange_thickness"]
        web_thickness: Quantity = kwargs["web_thickness"]

        inputs = {
            "total_height": total_height,
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_thickness": web_thickness,
        }

        # Calculate web height
        web_height = total_height - (flange_thickness * 2)
        self.add_step(
            description="Calculate web height",
            formula="hw = H - 2*tf",
            result=web_height,
            substitution=f"hw = {total_height} - 2*{flange_thickness} = {web_height}",
        )

        # Calculate area: A = 2*bf*tf + hw*tw
        flange_area = flange_width * flange_thickness * 2
        web_area = web_height * web_thickness
        area = flange_area + web_area
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = 2*bf*tf + hw*tw",
            result=area,
            substitution=f"A = 2*{flange_width}*{flange_thickness} + {web_height}*{web_thickness} = {area}",
        )

        # Calculate Ix using parallel axis theorem
        # Ix = Ix_web + 2*(Ix_flange + A_flange * d^2)
        # where d is distance from flange centroid to section centroid

        # Web contribution: Ix_web = tw * hw^3 / 12
        hw_cubed = web_height ** 3
        Ix_web = (web_thickness * hw_cubed) / 12

        # Flange contribution: Ix_flange = bf * tf^3 / 12 + bf*tf * d^2
        # d = (H - tf) / 2 = distance from centroid of flange to centroid of section
        tf_cubed = flange_thickness ** 3
        Ix_flange_self = (flange_width * tf_cubed) / 12
        d_flange = (total_height - flange_thickness) / 2
        d_squared = d_flange ** 2
        A_flange = flange_width * flange_thickness
        Ix_flange_transfer = A_flange * d_squared
        Ix_flanges = (Ix_flange_self + Ix_flange_transfer) * 2

        Ix = Ix_web + Ix_flanges
        self.add_step(
            description="Calculate moment of inertia about x-axis",
            formula="Ix = tw*hw^3/12 + 2*(bf*tf^3/12 + bf*tf*d^2)",
            result=Ix,
            substitution=f"Ix = {Ix_web} + 2*({Ix_flange_self} + {Ix_flange_transfer}) = {Ix}",
        )

        # Calculate Iy
        # Iy = 2*(tf * bf^3 / 12) + hw * tw^3 / 12
        bf_cubed = flange_width ** 3
        Iy_flanges = (flange_thickness * bf_cubed) / 12 * 2
        tw_cubed = web_thickness ** 3
        Iy_web = (web_height * tw_cubed) / 12
        Iy = Iy_flanges + Iy_web
        self.add_step(
            description="Calculate moment of inertia about y-axis",
            formula="Iy = 2*(tf*bf^3/12) + hw*tw^3/12",
            result=Iy,
            substitution=f"Iy = 2*{(flange_thickness * bf_cubed) / 12} + {Iy_web} = {Iy}",
        )

        # Calculate Sx: Sx = Ix / (H/2)
        c_x = total_height / 2
        Sx = Ix / c_x
        self.add_step(
            description="Calculate section modulus about x-axis",
            formula="Sx = Ix / (H/2)",
            result=Sx,
            substitution=f"Sx = {Ix} / {c_x} = {Sx}",
        )

        # Calculate Sy: Sy = Iy / (bf/2)
        c_y = flange_width / 2
        Sy = Iy / c_y
        self.add_step(
            description="Calculate section modulus about y-axis",
            formula="Sy = Iy / (bf/2)",
            result=Sy,
            substitution=f"Sy = {Iy} / {c_y} = {Sy}",
        )

        # Calculate rx: rx = sqrt(Ix / A)
        rx_squared = Ix / area
        rx = rx_squared ** 0.5
        self.add_step(
            description="Calculate radius of gyration about x-axis",
            formula="rx = sqrt(Ix / A)",
            result=rx,
            substitution=f"rx = sqrt({Ix} / {area}) = {rx}",
        )

        # Calculate ry: ry = sqrt(Iy / A)
        ry_squared = Iy / area
        ry = ry_squared ** 0.5
        self.add_step(
            description="Calculate radius of gyration about y-axis",
            formula="ry = sqrt(Iy / A)",
            result=ry,
            substitution=f"ry = sqrt({Iy} / {area}) = {ry}",
        )

        outputs = {
            "area": area,
            "Ix": Ix,
            "Iy": Iy,
            "Sx": Sx,
            "Sy": Sy,
            "rx": rx,
            "ry": ry,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CChannelSection(Calculation):
    """
    Calculate cross-sectional properties for a C-channel section.

    The C-channel consists of:
        - A web with height H and thickness tw
        - Two flanges extending from one side with width bf and thickness tf

    Properties calculated:
        - Area
        - Ix: Moment of inertia about horizontal centroidal axis
        - Iy: Moment of inertia about vertical centroidal axis
        - centroid_x: Distance from back of web to centroid
        - Sx: Section modulus about x-axis
    """

    name = "C-Channel Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a C-channel section "
        "including area, moments of inertia, centroid location, and section modulus."
    )
    references = ["AISC Steel Construction Manual", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("height", "m", "Total height of the channel (H)"),
        Parameter("flange_width", "m", "Width of the flanges (bf)"),
        Parameter("flange_thickness", "m", "Thickness of the flanges (tf)"),
        Parameter("web_thickness", "m", "Thickness of the web (tw)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("Ix", "m**4", "Moment of inertia about x-axis"),
        Parameter("Iy", "m**4", "Moment of inertia about y-axis"),
        Parameter("centroid_x", "m", "Distance from back of web to centroid"),
        Parameter("Sx", "m**3", "Section modulus about x-axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate C-channel section properties.

        Args:
            height: Total height as Quantity (m).
            flange_width: Flange width as Quantity (m).
            flange_thickness: Flange thickness as Quantity (m).
            web_thickness: Web thickness as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        height: Quantity = kwargs["height"]
        flange_width: Quantity = kwargs["flange_width"]
        flange_thickness: Quantity = kwargs["flange_thickness"]
        web_thickness: Quantity = kwargs["web_thickness"]

        inputs = {
            "height": height,
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_thickness": web_thickness,
        }

        # Calculate web height (clear height between flanges)
        web_height = height - (flange_thickness * 2)
        self.add_step(
            description="Calculate web clear height",
            formula="hw = H - 2*tf",
            result=web_height,
            substitution=f"hw = {height} - 2*{flange_thickness} = {web_height}",
        )

        # Calculate area: A = H*tw + 2*(bf - tw)*tf
        web_area = height * web_thickness
        flange_extension = flange_width - web_thickness
        flange_area = flange_extension * flange_thickness * 2
        area = web_area + flange_area
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = H*tw + 2*(bf - tw)*tf",
            result=area,
            substitution=f"A = {height}*{web_thickness} + 2*({flange_width} - {web_thickness})*{flange_thickness} = {area}",
        )

        # Calculate centroid x-coordinate from back of web
        # Using first moment of area
        # Web centroid at tw/2, flange centroid at (tw + (bf-tw)/2) = (tw + bf)/2 - tw/2 = bf/2
        web_x = web_thickness / 2
        flange_x = web_thickness + flange_extension / 2

        first_moment = web_area * web_x + flange_area * flange_x
        centroid_x = first_moment / area
        self.add_step(
            description="Calculate centroid x-coordinate from back of web",
            formula="x_bar = (A_web * x_web + A_flanges * x_flanges) / A",
            result=centroid_x,
            substitution=f"x_bar = ({web_area}*{web_x} + {flange_area}*{flange_x}) / {area} = {centroid_x}",
        )

        # Calculate Ix about centroidal x-axis (horizontal)
        # Ix_web = tw * H^3 / 12
        H_cubed = height ** 3
        Ix_web = (web_thickness * H_cubed) / 12

        # Each flange: Ix_flange = (bf-tw)*tf^3/12 + (bf-tw)*tf * d^2
        # d = H/2 - tf/2 = distance from section centroid to flange centroid
        tf_cubed = flange_thickness ** 3
        Ix_flange_self = (flange_extension * tf_cubed) / 12
        d_flange_y = (height - flange_thickness) / 2
        A_flange_single = flange_extension * flange_thickness
        Ix_flange_transfer = A_flange_single * (d_flange_y ** 2)
        Ix_flanges = (Ix_flange_self + Ix_flange_transfer) * 2

        Ix = Ix_web + Ix_flanges
        self.add_step(
            description="Calculate moment of inertia about x-axis",
            formula="Ix = tw*H^3/12 + 2*[(bf-tw)*tf^3/12 + (bf-tw)*tf*d^2]",
            result=Ix,
            substitution=f"Ix = {Ix_web} + 2*({Ix_flange_self} + {Ix_flange_transfer}) = {Ix}",
        )

        # Calculate Iy about centroidal y-axis (vertical through centroid)
        # Using parallel axis theorem for each component

        # Web: Iy_web = H*tw^3/12 + H*tw*(x_bar - tw/2)^2
        tw_cubed = web_thickness ** 3
        Iy_web_self = (height * tw_cubed) / 12
        d_web = centroid_x - web_x
        Iy_web_transfer = web_area * (d_web ** 2)
        Iy_web = Iy_web_self + Iy_web_transfer

        # Flanges: Iy_flange = tf*(bf-tw)^3/12 + tf*(bf-tw)*(x_flange - x_bar)^2
        flange_ext_cubed = flange_extension ** 3
        Iy_flange_self = (flange_thickness * flange_ext_cubed) / 12
        d_flange_x = flange_x - centroid_x
        Iy_flange_transfer = A_flange_single * (d_flange_x ** 2)
        Iy_flanges = (Iy_flange_self + Iy_flange_transfer) * 2

        Iy = Iy_web + Iy_flanges
        self.add_step(
            description="Calculate moment of inertia about y-axis",
            formula="Iy = Iy_web + Iy_flanges (using parallel axis theorem)",
            result=Iy,
            substitution=f"Iy = {Iy_web} + {Iy_flanges} = {Iy}",
        )

        # Calculate Sx: Sx = Ix / (H/2)
        c_x = height / 2
        Sx = Ix / c_x
        self.add_step(
            description="Calculate section modulus about x-axis",
            formula="Sx = Ix / (H/2)",
            result=Sx,
            substitution=f"Sx = {Ix} / {c_x} = {Sx}",
        )

        outputs = {
            "area": area,
            "Ix": Ix,
            "Iy": Iy,
            "centroid_x": centroid_x,
            "Sx": Sx,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class HollowRectangularSection(Calculation):
    """
    Calculate cross-sectional properties for a hollow rectangular (box/tube) section.

    Properties calculated:
        - Area: A = outer_area - inner_area
        - Ix: Moment of inertia about x-axis
        - Iy: Moment of inertia about y-axis
        - Sx, Sy: Section moduli
    """

    name = "Hollow Rectangular Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a hollow rectangular (box/tube) section "
        "including area, moments of inertia, and section moduli."
    )
    references = ["Mechanics of Materials, Hibbeler", "AISC Steel Construction Manual"]

    input_params = [
        Parameter("outer_width", "m", "Outer width of the section (B)"),
        Parameter("outer_height", "m", "Outer height of the section (H)"),
        Parameter("wall_thickness", "m", "Wall thickness (t)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("Ix", "m**4", "Moment of inertia about x-axis"),
        Parameter("Iy", "m**4", "Moment of inertia about y-axis"),
        Parameter("Sx", "m**3", "Section modulus about x-axis"),
        Parameter("Sy", "m**3", "Section modulus about y-axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate hollow rectangular section properties.

        Args:
            outer_width: Outer width as Quantity (m).
            outer_height: Outer height as Quantity (m).
            wall_thickness: Wall thickness as Quantity (m).

        Returns:
            CalculationResult with all section properties.

        Raises:
            ValueError: If wall thickness is too large for the section dimensions.
        """
        self.reset()

        outer_width: Quantity = kwargs["outer_width"]
        outer_height: Quantity = kwargs["outer_height"]
        wall_thickness: Quantity = kwargs["wall_thickness"]

        # Validate dimensions
        min_dimension = min(outer_width.magnitude, outer_height.magnitude)
        if wall_thickness.magnitude * 2 >= min_dimension:
            raise ValueError(
                f"Wall thickness ({wall_thickness}) is too large for section dimensions"
            )

        inputs = {
            "outer_width": outer_width,
            "outer_height": outer_height,
            "wall_thickness": wall_thickness,
        }

        # Calculate inner dimensions
        inner_width = outer_width - (wall_thickness * 2)
        inner_height = outer_height - (wall_thickness * 2)
        self.add_step(
            description="Calculate inner dimensions",
            formula="b_inner = B - 2t, h_inner = H - 2t",
            result=f"b_inner = {inner_width}, h_inner = {inner_height}",
            substitution=f"b_inner = {outer_width} - 2*{wall_thickness} = {inner_width}",
        )

        # Calculate area: A = B*H - b_inner*h_inner
        outer_area = outer_width * outer_height
        inner_area = inner_width * inner_height
        area = outer_area - inner_area
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = B*H - b_inner*h_inner",
            result=area,
            substitution=f"A = {outer_area} - {inner_area} = {area}",
        )

        # Calculate Ix: Ix = (B*H^3 - b_inner*h_inner^3) / 12
        H_cubed = outer_height ** 3
        h_inner_cubed = inner_height ** 3
        Ix = (outer_width * H_cubed - inner_width * h_inner_cubed) / 12
        self.add_step(
            description="Calculate moment of inertia about x-axis",
            formula="Ix = (B*H^3 - b_inner*h_inner^3) / 12",
            result=Ix,
            substitution=f"Ix = ({outer_width}*{outer_height}^3 - {inner_width}*{inner_height}^3) / 12 = {Ix}",
        )

        # Calculate Iy: Iy = (H*B^3 - h_inner*b_inner^3) / 12
        B_cubed = outer_width ** 3
        b_inner_cubed = inner_width ** 3
        Iy = (outer_height * B_cubed - inner_height * b_inner_cubed) / 12
        self.add_step(
            description="Calculate moment of inertia about y-axis",
            formula="Iy = (H*B^3 - h_inner*b_inner^3) / 12",
            result=Iy,
            substitution=f"Iy = ({outer_height}*{outer_width}^3 - {inner_height}*{inner_width}^3) / 12 = {Iy}",
        )

        # Calculate Sx: Sx = Ix / (H/2)
        c_x = outer_height / 2
        Sx = Ix / c_x
        self.add_step(
            description="Calculate section modulus about x-axis",
            formula="Sx = Ix / (H/2)",
            result=Sx,
            substitution=f"Sx = {Ix} / {c_x} = {Sx}",
        )

        # Calculate Sy: Sy = Iy / (B/2)
        c_y = outer_width / 2
        Sy = Iy / c_y
        self.add_step(
            description="Calculate section modulus about y-axis",
            formula="Sy = Iy / (B/2)",
            result=Sy,
            substitution=f"Sy = {Iy} / {c_y} = {Sy}",
        )

        outputs = {
            "area": area,
            "Ix": Ix,
            "Iy": Iy,
            "Sx": Sx,
            "Sy": Sy,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TBeamSection(Calculation):
    """
    Calculate cross-sectional properties for a T-beam section.

    The T-beam consists of:
        - A flange (top) with width bf and thickness tf
        - A web (stem) with height hw and thickness tw

    Properties calculated:
        - Area
        - centroid_y: Distance from bottom to centroid
        - Ix: Moment of inertia about centroidal x-axis
        - Sx_top: Section modulus to top fiber
        - Sx_bottom: Section modulus to bottom fiber
    """

    name = "T-Beam Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for a T-beam section "
        "including area, centroid location, moment of inertia, and section moduli."
    )
    references = ["Mechanics of Materials, Hibbeler", "Reinforced Concrete Design"]

    input_params = [
        Parameter("flange_width", "m", "Width of the flange (bf)"),
        Parameter("flange_thickness", "m", "Thickness of the flange (tf)"),
        Parameter("web_height", "m", "Height of the web/stem (hw)"),
        Parameter("web_thickness", "m", "Thickness of the web/stem (tw)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("centroid_y", "m", "Distance from bottom of web to centroid"),
        Parameter("Ix", "m**4", "Moment of inertia about centroidal x-axis"),
        Parameter("Sx_top", "m**3", "Section modulus to top fiber"),
        Parameter("Sx_bottom", "m**3", "Section modulus to bottom fiber"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate T-beam section properties.

        Args:
            flange_width: Flange width as Quantity (m).
            flange_thickness: Flange thickness as Quantity (m).
            web_height: Web height as Quantity (m).
            web_thickness: Web thickness as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        flange_width: Quantity = kwargs["flange_width"]
        flange_thickness: Quantity = kwargs["flange_thickness"]
        web_height: Quantity = kwargs["web_height"]
        web_thickness: Quantity = kwargs["web_thickness"]

        inputs = {
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_height": web_height,
            "web_thickness": web_thickness,
        }

        # Total height
        total_height = web_height + flange_thickness
        self.add_step(
            description="Calculate total height",
            formula="H = hw + tf",
            result=total_height,
            substitution=f"H = {web_height} + {flange_thickness} = {total_height}",
        )

        # Calculate areas
        web_area = web_height * web_thickness
        flange_area = flange_width * flange_thickness
        area = web_area + flange_area
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = hw*tw + bf*tf",
            result=area,
            substitution=f"A = {web_height}*{web_thickness} + {flange_width}*{flange_thickness} = {area}",
        )

        # Calculate centroid y-coordinate from bottom
        # Web centroid at hw/2, flange centroid at hw + tf/2
        web_y = web_height / 2
        flange_y = web_height + flange_thickness / 2

        first_moment = web_area * web_y + flange_area * flange_y
        centroid_y = first_moment / area
        self.add_step(
            description="Calculate centroid y-coordinate from bottom",
            formula="y_bar = (A_web*y_web + A_flange*y_flange) / A",
            result=centroid_y,
            substitution=f"y_bar = ({web_area}*{web_y} + {flange_area}*{flange_y}) / {area} = {centroid_y}",
        )

        # Calculate Ix about centroidal axis using parallel axis theorem
        # Web: Ix_web = tw*hw^3/12 + tw*hw*(y_bar - hw/2)^2
        hw_cubed = web_height ** 3
        Ix_web_self = (web_thickness * hw_cubed) / 12
        d_web = centroid_y - web_y
        Ix_web_transfer = web_area * (d_web ** 2)
        Ix_web = Ix_web_self + Ix_web_transfer

        # Flange: Ix_flange = bf*tf^3/12 + bf*tf*(y_flange - y_bar)^2
        tf_cubed = flange_thickness ** 3
        Ix_flange_self = (flange_width * tf_cubed) / 12
        d_flange = flange_y - centroid_y
        Ix_flange_transfer = flange_area * (d_flange ** 2)
        Ix_flange = Ix_flange_self + Ix_flange_transfer

        Ix = Ix_web + Ix_flange
        self.add_step(
            description="Calculate moment of inertia about centroidal x-axis",
            formula="Ix = Ix_web + Ix_flange (using parallel axis theorem)",
            result=Ix,
            substitution=f"Ix = ({Ix_web_self} + {Ix_web_transfer}) + ({Ix_flange_self} + {Ix_flange_transfer}) = {Ix}",
        )

        # Calculate Sx_top: Distance from centroid to top fiber
        c_top = total_height - centroid_y
        Sx_top = Ix / c_top
        self.add_step(
            description="Calculate section modulus to top fiber",
            formula="Sx_top = Ix / c_top",
            result=Sx_top,
            substitution=f"Sx_top = {Ix} / {c_top} = {Sx_top}",
        )

        # Calculate Sx_bottom: Distance from centroid to bottom fiber
        c_bottom = centroid_y
        Sx_bottom = Ix / c_bottom
        self.add_step(
            description="Calculate section modulus to bottom fiber",
            formula="Sx_bottom = Ix / c_bottom",
            result=Sx_bottom,
            substitution=f"Sx_bottom = {Ix} / {c_bottom} = {Sx_bottom}",
        )

        outputs = {
            "area": area,
            "centroid_y": centroid_y,
            "Ix": Ix,
            "Sx_top": Sx_top,
            "Sx_bottom": Sx_bottom,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class AngleSection(Calculation):
    """
    Calculate cross-sectional properties for an angle (L-shaped) section.

    The angle consists of two legs:
        - Leg 1 (vertical) with length L1 and thickness t
        - Leg 2 (horizontal) with length L2 and thickness t

    Properties calculated:
        - Area
        - centroid_x: Distance from left edge to centroid
        - centroid_y: Distance from bottom edge to centroid
        - Ix: Moment of inertia about centroidal x-axis
        - Iy: Moment of inertia about centroidal y-axis
    """

    name = "Angle Section"
    category = "Cross Sections"
    description = (
        "Calculate cross-sectional properties for an angle (L-shaped) section "
        "including area, centroid location, and moments of inertia."
    )
    references = ["AISC Steel Construction Manual", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("leg1_length", "m", "Length of vertical leg (L1)"),
        Parameter("leg2_length", "m", "Length of horizontal leg (L2)"),
        Parameter("thickness", "m", "Thickness of both legs (t)"),
    ]
    output_params = [
        Parameter("area", "m**2", "Cross-sectional area"),
        Parameter("centroid_x", "m", "Distance from left edge to centroid"),
        Parameter("centroid_y", "m", "Distance from bottom edge to centroid"),
        Parameter("Ix", "m**4", "Moment of inertia about centroidal x-axis"),
        Parameter("Iy", "m**4", "Moment of inertia about centroidal y-axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate angle section properties.

        Args:
            leg1_length: Vertical leg length as Quantity (m).
            leg2_length: Horizontal leg length as Quantity (m).
            thickness: Leg thickness as Quantity (m).

        Returns:
            CalculationResult with all section properties.
        """
        self.reset()

        leg1_length: Quantity = kwargs["leg1_length"]  # Vertical leg
        leg2_length: Quantity = kwargs["leg2_length"]  # Horizontal leg
        thickness: Quantity = kwargs["thickness"]

        inputs = {
            "leg1_length": leg1_length,
            "leg2_length": leg2_length,
            "thickness": thickness,
        }

        # Model as two rectangles:
        # Rect 1 (vertical leg): width = t, height = L1
        # Rect 2 (horizontal leg, excluding overlap): width = L2 - t, height = t

        # Areas
        A1 = thickness * leg1_length  # Vertical leg area
        A2 = (leg2_length - thickness) * thickness  # Horizontal leg area (excluding overlap)
        area = A1 + A2
        self.add_step(
            description="Calculate cross-sectional area",
            formula="A = t*L1 + (L2-t)*t",
            result=area,
            substitution=f"A = {thickness}*{leg1_length} + ({leg2_length}-{thickness})*{thickness} = {area}",
        )

        # Centroids of each rectangle
        # Rect 1: centroid at (t/2, L1/2) from origin at bottom-left
        x1 = thickness / 2
        y1 = leg1_length / 2

        # Rect 2: centroid at (t + (L2-t)/2, t/2) = ((L2+t)/2, t/2)
        x2 = thickness + (leg2_length - thickness) / 2
        y2 = thickness / 2

        # Composite centroid
        centroid_x = (A1 * x1 + A2 * x2) / area
        centroid_y = (A1 * y1 + A2 * y2) / area
        self.add_step(
            description="Calculate centroid x-coordinate from left edge",
            formula="x_bar = (A1*x1 + A2*x2) / A",
            result=centroid_x,
            substitution=f"x_bar = ({A1}*{x1} + {A2}*{x2}) / {area} = {centroid_x}",
        )
        self.add_step(
            description="Calculate centroid y-coordinate from bottom edge",
            formula="y_bar = (A1*y1 + A2*y2) / A",
            result=centroid_y,
            substitution=f"y_bar = ({A1}*{y1} + {A2}*{y2}) / {area} = {centroid_y}",
        )

        # Calculate Ix about centroidal x-axis using parallel axis theorem
        # Rect 1: Ix1 = t*L1^3/12 + A1*(y1 - y_bar)^2
        L1_cubed = leg1_length ** 3
        Ix1_self = (thickness * L1_cubed) / 12
        d1_y = y1 - centroid_y
        Ix1_transfer = A1 * (d1_y ** 2)
        Ix1 = Ix1_self + Ix1_transfer

        # Rect 2: Ix2 = (L2-t)*t^3/12 + A2*(y2 - y_bar)^2
        t_cubed = thickness ** 3
        Ix2_self = ((leg2_length - thickness) * t_cubed) / 12
        d2_y = y2 - centroid_y
        Ix2_transfer = A2 * (d2_y ** 2)
        Ix2 = Ix2_self + Ix2_transfer

        Ix = Ix1 + Ix2
        self.add_step(
            description="Calculate moment of inertia about centroidal x-axis",
            formula="Ix = Ix1 + Ix2 (using parallel axis theorem)",
            result=Ix,
            substitution=f"Ix = ({Ix1_self} + {Ix1_transfer}) + ({Ix2_self} + {Ix2_transfer}) = {Ix}",
        )

        # Calculate Iy about centroidal y-axis using parallel axis theorem
        # Rect 1: Iy1 = L1*t^3/12 + A1*(x1 - x_bar)^2
        Iy1_self = (leg1_length * t_cubed) / 12
        d1_x = x1 - centroid_x
        Iy1_transfer = A1 * (d1_x ** 2)
        Iy1 = Iy1_self + Iy1_transfer

        # Rect 2: Iy2 = t*(L2-t)^3/12 + A2*(x2 - x_bar)^2
        L2_minus_t_cubed = (leg2_length - thickness) ** 3
        Iy2_self = (thickness * L2_minus_t_cubed) / 12
        d2_x = x2 - centroid_x
        Iy2_transfer = A2 * (d2_x ** 2)
        Iy2 = Iy2_self + Iy2_transfer

        Iy = Iy1 + Iy2
        self.add_step(
            description="Calculate moment of inertia about centroidal y-axis",
            formula="Iy = Iy1 + Iy2 (using parallel axis theorem)",
            result=Iy,
            substitution=f"Iy = ({Iy1_self} + {Iy1_transfer}) + ({Iy2_self} + {Iy2_transfer}) = {Iy}",
        )

        outputs = {
            "area": area,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "Ix": Ix,
            "Iy": Iy,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "RectangularSection",
    "CircularSection",
    "HollowCircularSection",
    "IBeamSection",
    "CChannelSection",
    "HollowRectangularSection",
    "TBeamSection",
    "AngleSection",
]
