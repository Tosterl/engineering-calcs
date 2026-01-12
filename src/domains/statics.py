"""
Statics calculations for Engineering Calculations Database.

This module provides engineering calculations for statics analysis including:
- Moment calculations
- Beam reactions (simply supported and cantilever)
- Bending moment and shear force analysis
- Section properties (section modulus, moment of inertia, centroid)
"""

from __future__ import annotations

from typing import Any, List, Optional

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


@register
class MomentAboutPoint(Calculation):
    """
    Calculate moment about a point.

    Formula: M = F x d

    Where:
        M = moment (N*m)
        F = force (N)
        d = perpendicular distance from force to point (m)
    """

    name = "Moment About Point"
    category = "Statics"
    description = "Calculate the moment created by a force about a point. M = F x d"
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("force", "N", "Applied force"),
        Parameter("distance", "m", "Perpendicular distance from force to point"),
    ]
    output_params = [
        Parameter("moment", "N*m", "Resulting moment about the point"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate moment about a point.

        Args:
            force: Applied force as Quantity (N).
            distance: Perpendicular distance as Quantity (m).

        Returns:
            CalculationResult with moment output.
        """
        self.reset()

        force: Quantity = kwargs["force"]
        distance: Quantity = kwargs["distance"]

        # Store inputs
        inputs = {
            "force": force,
            "distance": distance,
        }

        # Calculate moment: M = F x d
        moment = force * distance

        # Add intermediate step
        self.add_step(
            description="Calculate moment using M = F x d",
            formula="M = F x d",
            result=moment,
            substitution=f"M = {force} x {distance} = {moment}",
        )

        outputs = {
            "moment": moment,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SimplySupportedBeamReactions(Calculation):
    """
    Calculate reactions for a simply supported beam.

    For point load at position 'a' from left support:
        R_A = P * (L - a) / L
        R_B = P * a / L

    For uniformly distributed load:
        R_A = R_B = w * L / 2
    """

    name = "Simply Supported Beam Reactions"
    category = "Statics"
    description = (
        "Calculate support reactions for a simply supported beam with either "
        "a point load or uniformly distributed load."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("beam_length", "m", "Total length of the beam"),
        Parameter("total_load", "N", "Point load magnitude (for point load case)", default=None),
        Parameter("load_position", "m", "Distance from left support to point load", default=None),
        Parameter("distributed_load", "N/m", "Uniformly distributed load (for distributed case)", default=None),
    ]
    output_params = [
        Parameter("reaction_a", "N", "Reaction force at left support (A)"),
        Parameter("reaction_b", "N", "Reaction force at right support (B)"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate beam reactions.

        Args:
            beam_length: Beam length as Quantity (m).
            total_load: Point load as Quantity (N) - optional.
            load_position: Distance to point load as Quantity (m) - optional.
            distributed_load: UDL as Quantity (N/m) - optional.

        Returns:
            CalculationResult with reaction forces.

        Raises:
            ValueError: If neither point load nor distributed load is provided.
        """
        self.reset()

        beam_length: Quantity = kwargs["beam_length"]
        total_load: Optional[Quantity] = kwargs.get("total_load")
        load_position: Optional[Quantity] = kwargs.get("load_position")
        distributed_load: Optional[Quantity] = kwargs.get("distributed_load")

        inputs = {"beam_length": beam_length}

        if distributed_load is not None:
            # Uniformly distributed load case
            inputs["distributed_load"] = distributed_load

            # Calculate total load from distributed load
            total_distributed = distributed_load * beam_length
            self.add_step(
                description="Calculate total load from distributed load",
                formula="W = w x L",
                result=total_distributed,
                substitution=f"W = {distributed_load} x {beam_length} = {total_distributed}",
            )

            # For symmetric UDL, reactions are equal
            reaction_a = total_distributed / 2
            reaction_b = total_distributed / 2

            self.add_step(
                description="Calculate reaction at support A (symmetry)",
                formula="R_A = W / 2",
                result=reaction_a,
                substitution=f"R_A = {total_distributed} / 2 = {reaction_a}",
            )

            self.add_step(
                description="Calculate reaction at support B (symmetry)",
                formula="R_B = W / 2",
                result=reaction_b,
                substitution=f"R_B = {total_distributed} / 2 = {reaction_b}",
            )

        elif total_load is not None and load_position is not None:
            # Point load case
            inputs["total_load"] = total_load
            inputs["load_position"] = load_position

            # R_A = P * (L - a) / L
            distance_to_b = beam_length - load_position
            self.add_step(
                description="Calculate distance from load to right support",
                formula="b = L - a",
                result=distance_to_b,
                substitution=f"b = {beam_length} - {load_position} = {distance_to_b}",
            )

            reaction_a = total_load * distance_to_b / beam_length
            self.add_step(
                description="Calculate reaction at support A using moment equilibrium about B",
                formula="R_A = P x (L - a) / L",
                result=reaction_a,
                substitution=f"R_A = {total_load} x {distance_to_b} / {beam_length} = {reaction_a}",
            )

            # R_B = P * a / L
            reaction_b = total_load * load_position / beam_length
            self.add_step(
                description="Calculate reaction at support B using moment equilibrium about A",
                formula="R_B = P x a / L",
                result=reaction_b,
                substitution=f"R_B = {total_load} x {load_position} / {beam_length} = {reaction_b}",
            )

        else:
            raise ValueError(
                "Either 'distributed_load' OR both 'total_load' and 'load_position' must be provided"
            )

        outputs = {
            "reaction_a": reaction_a,
            "reaction_b": reaction_b,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CantileverBeamReaction(Calculation):
    """
    Calculate fixed-end reactions for a cantilever beam with a point load.

    For point load P at distance 'a' from fixed support:
        Reaction Force: R = P
        Reaction Moment: M = P x a
    """

    name = "Cantilever Beam Reaction"
    category = "Statics"
    description = (
        "Calculate the reaction force and moment at the fixed end of a "
        "cantilever beam subjected to a point load."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("point_load", "N", "Point load magnitude"),
        Parameter("distance_from_support", "m", "Distance from fixed support to point load"),
    ]
    output_params = [
        Parameter("reaction_force", "N", "Reaction force at fixed support"),
        Parameter("reaction_moment", "N*m", "Reaction moment at fixed support"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate cantilever beam reactions.

        Args:
            point_load: Point load as Quantity (N).
            distance_from_support: Distance to load as Quantity (m).

        Returns:
            CalculationResult with reaction force and moment.
        """
        self.reset()

        point_load: Quantity = kwargs["point_load"]
        distance_from_support: Quantity = kwargs["distance_from_support"]

        inputs = {
            "point_load": point_load,
            "distance_from_support": distance_from_support,
        }

        # Reaction force equals the applied load (force equilibrium)
        reaction_force = point_load
        self.add_step(
            description="Calculate reaction force from force equilibrium",
            formula="R = P",
            result=reaction_force,
            substitution=f"R = {point_load} = {reaction_force}",
        )

        # Reaction moment: M = P x a
        reaction_moment = point_load * distance_from_support
        self.add_step(
            description="Calculate reaction moment from moment equilibrium",
            formula="M = P x a",
            result=reaction_moment,
            substitution=f"M = {point_load} x {distance_from_support} = {reaction_moment}",
        )

        outputs = {
            "reaction_force": reaction_force,
            "reaction_moment": reaction_moment,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class BendingMoment(Calculation):
    """
    Calculate maximum bending moment for a simply supported beam with uniform load.

    Formula: M_max = (w x L^2) / 8

    The maximum moment occurs at the center of the span (L/2).
    """

    name = "Bending Moment - Simply Supported Uniform Load"
    category = "Statics"
    description = (
        "Calculate the maximum bending moment for a simply supported beam "
        "with uniformly distributed load. M = (w x L^2) / 8"
    )
    references = ["AISC Steel Construction Manual", "Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("distributed_load", "N/m", "Uniformly distributed load"),
        Parameter("span_length", "m", "Span length of the beam"),
    ]
    output_params = [
        Parameter("max_moment", "N*m", "Maximum bending moment"),
        Parameter("moment_location", "m", "Location of maximum moment from left support"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate maximum bending moment.

        Args:
            distributed_load: UDL as Quantity (N/m).
            span_length: Span length as Quantity (m).

        Returns:
            CalculationResult with maximum moment and its location.
        """
        self.reset()

        distributed_load: Quantity = kwargs["distributed_load"]
        span_length: Quantity = kwargs["span_length"]

        inputs = {
            "distributed_load": distributed_load,
            "span_length": span_length,
        }

        # Calculate L^2
        span_squared = span_length ** 2
        self.add_step(
            description="Calculate span length squared",
            formula="L^2",
            result=span_squared,
            substitution=f"L^2 = ({span_length})^2 = {span_squared}",
        )

        # Calculate w x L^2
        numerator = distributed_load * span_squared
        self.add_step(
            description="Calculate numerator (w x L^2)",
            formula="w x L^2",
            result=numerator,
            substitution=f"w x L^2 = {distributed_load} x {span_squared} = {numerator}",
        )

        # Calculate M_max = (w x L^2) / 8
        max_moment = numerator / 8
        self.add_step(
            description="Calculate maximum bending moment",
            formula="M_max = (w x L^2) / 8",
            result=max_moment,
            substitution=f"M_max = {numerator} / 8 = {max_moment}",
        )

        # Location of maximum moment is at midspan
        moment_location = span_length / 2
        self.add_step(
            description="Maximum moment occurs at midspan",
            formula="x_max = L / 2",
            result=moment_location,
            substitution=f"x_max = {span_length} / 2 = {moment_location}",
        )

        outputs = {
            "max_moment": max_moment,
            "moment_location": moment_location,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class ShearForce(Calculation):
    """
    Calculate shear force at a point along a simply supported beam with uniform load.

    For a simply supported beam with UDL w and span L:
        V(x) = w*L/2 - w*x = w*(L/2 - x)

    Where x is measured from the left support.
    """

    name = "Shear Force - Simply Supported Uniform Load"
    category = "Statics"
    description = (
        "Calculate the shear force at any position along a simply supported "
        "beam with uniformly distributed load."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("distributed_load", "N/m", "Uniformly distributed load"),
        Parameter("span_length", "m", "Span length of the beam"),
        Parameter("position", "m", "Position from left support where shear is calculated"),
    ]
    output_params = [
        Parameter("shear_force", "N", "Shear force at the specified position"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate shear force at a position.

        Args:
            distributed_load: UDL as Quantity (N/m).
            span_length: Span length as Quantity (m).
            position: Position from left support as Quantity (m).

        Returns:
            CalculationResult with shear force.
        """
        self.reset()

        distributed_load: Quantity = kwargs["distributed_load"]
        span_length: Quantity = kwargs["span_length"]
        position: Quantity = kwargs["position"]

        inputs = {
            "distributed_load": distributed_load,
            "span_length": span_length,
            "position": position,
        }

        # Calculate reaction at left support (for symmetric loading)
        reaction_a = distributed_load * span_length / 2
        self.add_step(
            description="Calculate reaction at left support",
            formula="R_A = w x L / 2",
            result=reaction_a,
            substitution=f"R_A = {distributed_load} x {span_length} / 2 = {reaction_a}",
        )

        # Calculate load to the left of the section
        load_left = distributed_load * position
        self.add_step(
            description="Calculate distributed load from left support to position x",
            formula="Load_left = w x x",
            result=load_left,
            substitution=f"Load_left = {distributed_load} x {position} = {load_left}",
        )

        # Calculate shear force: V = R_A - w*x
        shear_force = reaction_a - load_left
        self.add_step(
            description="Calculate shear force at position x",
            formula="V(x) = R_A - w x x",
            result=shear_force,
            substitution=f"V({position}) = {reaction_a} - {load_left} = {shear_force}",
        )

        outputs = {
            "shear_force": shear_force,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SectionModulus(Calculation):
    """
    Calculate section modulus from moment of inertia and distance to extreme fiber.

    Formula: S = I / c

    Where:
        S = section modulus (m^3)
        I = moment of inertia (m^4)
        c = distance from neutral axis to extreme fiber (m)
    """

    name = "Section Modulus"
    category = "Statics"
    description = (
        "Calculate the section modulus of a cross-section. S = I / c"
    )
    references = ["AISC Steel Construction Manual", "Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("moment_of_inertia", "m**4", "Moment of inertia about the neutral axis"),
        Parameter("distance_to_extreme_fiber", "m", "Distance from neutral axis to extreme fiber"),
    ]
    output_params = [
        Parameter("section_modulus", "m**3", "Section modulus"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate section modulus.

        Args:
            moment_of_inertia: I as Quantity (m^4).
            distance_to_extreme_fiber: c as Quantity (m).

        Returns:
            CalculationResult with section modulus.
        """
        self.reset()

        moment_of_inertia: Quantity = kwargs["moment_of_inertia"]
        distance_to_extreme_fiber: Quantity = kwargs["distance_to_extreme_fiber"]

        inputs = {
            "moment_of_inertia": moment_of_inertia,
            "distance_to_extreme_fiber": distance_to_extreme_fiber,
        }

        # Calculate S = I / c
        section_modulus = moment_of_inertia / distance_to_extreme_fiber
        self.add_step(
            description="Calculate section modulus",
            formula="S = I / c",
            result=section_modulus,
            substitution=f"S = {moment_of_inertia} / {distance_to_extreme_fiber} = {section_modulus}",
        )

        outputs = {
            "section_modulus": section_modulus,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class MomentOfInertiaRectangle(Calculation):
    """
    Calculate moment of inertia for a rectangular cross-section.

    Formula: I = (b x h^3) / 12

    Where:
        I = moment of inertia about the centroidal axis (m^4)
        b = base width (m)
        h = height (m)

    The axis is parallel to the base and passes through the centroid.
    """

    name = "Moment of Inertia - Rectangle"
    category = "Statics"
    description = (
        "Calculate the moment of inertia for a rectangular cross-section "
        "about its centroidal axis parallel to the base. I = bh^3/12"
    )
    references = ["Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("base", "m", "Base width of rectangle"),
        Parameter("height", "m", "Height of rectangle"),
    ]
    output_params = [
        Parameter("moment_of_inertia", "m**4", "Moment of inertia about centroidal axis"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate moment of inertia for a rectangle.

        Args:
            base: Base width as Quantity (m).
            height: Height as Quantity (m).

        Returns:
            CalculationResult with moment of inertia.
        """
        self.reset()

        base: Quantity = kwargs["base"]
        height: Quantity = kwargs["height"]

        inputs = {
            "base": base,
            "height": height,
        }

        # Calculate h^3
        height_cubed = height ** 3
        self.add_step(
            description="Calculate height cubed",
            formula="h^3",
            result=height_cubed,
            substitution=f"h^3 = ({height})^3 = {height_cubed}",
        )

        # Calculate b x h^3
        numerator = base * height_cubed
        self.add_step(
            description="Calculate numerator (b x h^3)",
            formula="b x h^3",
            result=numerator,
            substitution=f"b x h^3 = {base} x {height_cubed} = {numerator}",
        )

        # Calculate I = (b x h^3) / 12
        moment_of_inertia = numerator / 12
        self.add_step(
            description="Calculate moment of inertia",
            formula="I = (b x h^3) / 12",
            result=moment_of_inertia,
            substitution=f"I = {numerator} / 12 = {moment_of_inertia}",
        )

        outputs = {
            "moment_of_inertia": moment_of_inertia,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CentroidComposite(Calculation):
    """
    Calculate the centroid of a composite shape.

    Formula: y_bar = Sum(A_i x y_i) / Sum(A_i)

    Where:
        y_bar = y-coordinate of composite centroid
        A_i = area of each component
        y_i = y-coordinate of each component's centroid
    """

    name = "Centroid - Composite Shape"
    category = "Statics"
    description = (
        "Calculate the centroid y-coordinate of a composite shape from "
        "individual component areas and their centroid positions."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("areas", "m**2", "List of component areas"),
        Parameter("y_positions", "m", "List of y-coordinates of component centroids"),
    ]
    output_params = [
        Parameter("centroid_y", "m", "Y-coordinate of composite centroid"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate centroid of a composite shape.

        Args:
            areas: List of component areas as Quantities (m^2).
            y_positions: List of y-coordinates as Quantities (m).

        Returns:
            CalculationResult with centroid y-coordinate.

        Raises:
            ValueError: If areas and y_positions have different lengths.
        """
        self.reset()

        areas: List[Quantity] = kwargs["areas"]
        y_positions: List[Quantity] = kwargs["y_positions"]

        if len(areas) != len(y_positions):
            raise ValueError(
                f"Number of areas ({len(areas)}) must match number of y_positions ({len(y_positions)})"
            )

        inputs = {
            "areas": areas,
            "y_positions": y_positions,
        }

        # Calculate total area
        total_area = areas[0]
        for area in areas[1:]:
            total_area = total_area + area

        self.add_step(
            description="Calculate total area",
            formula="A_total = Sum(A_i)",
            result=total_area,
            substitution=f"A_total = {' + '.join(str(a) for a in areas)} = {total_area}",
        )

        # Calculate sum of A_i x y_i (first moment of area)
        first_moment = areas[0] * y_positions[0]
        for area, y_pos in zip(areas[1:], y_positions[1:]):
            first_moment = first_moment + (area * y_pos)

        moment_terms = [f"({a} x {y})" for a, y in zip(areas, y_positions)]
        self.add_step(
            description="Calculate first moment of area (sum of A_i x y_i)",
            formula="Q = Sum(A_i x y_i)",
            result=first_moment,
            substitution=f"Q = {' + '.join(moment_terms)} = {first_moment}",
        )

        # Calculate centroid y-coordinate
        centroid_y = first_moment / total_area
        self.add_step(
            description="Calculate centroid y-coordinate",
            formula="y_bar = Sum(A_i x y_i) / Sum(A_i)",
            result=centroid_y,
            substitution=f"y_bar = {first_moment} / {total_area} = {centroid_y}",
        )

        outputs = {
            "centroid_y": centroid_y,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    "MomentAboutPoint",
    "SimplySupportedBeamReactions",
    "CantileverBeamReaction",
    "BendingMoment",
    "ShearForce",
    "SectionModulus",
    "MomentOfInertiaRectangle",
    "CentroidComposite",
]
