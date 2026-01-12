"""
Truss analysis calculations for Engineering Calculations Database.

This module provides engineering calculations for truss analysis including:
- Node equilibrium checks
- Member force calculations using method of joints
- Support reactions for simple trusses
- Method of sections analysis
- Member stress calculations
- Deflection using virtual work method
- Euler buckling for compression members
- Truss efficiency calculations

Also includes a TrussGeometry helper class for storing and calculating
truss geometric properties.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.core.calculations import (
    Calculation,
    CalculationResult,
    Parameter,
    register,
)
from src.core.units import Quantity


# =============================================================================
# Helper Class: TrussGeometry
# =============================================================================


@dataclass
class TrussNode:
    """Represents a node in a truss structure."""
    x: float
    y: float
    name: str = ""


@dataclass
class TrussMember:
    """Represents a member connecting two nodes in a truss."""
    start_node_index: int
    end_node_index: int
    name: str = ""


class TrussGeometry:
    """
    Helper class for storing and calculating truss geometric properties.

    This class stores nodes as (x, y) coordinates and members as connections
    between nodes. It provides methods to calculate member lengths and angles.

    Attributes:
        nodes: List of TrussNode objects representing truss joints.
        members: List of TrussMember objects representing truss members.

    Example:
        >>> geom = TrussGeometry()
        >>> geom.add_node(0, 0, "A")
        >>> geom.add_node(3, 0, "B")
        >>> geom.add_node(1.5, 2, "C")
        >>> geom.add_member(0, 1, "AB")  # Bottom chord
        >>> geom.add_member(0, 2, "AC")  # Left diagonal
        >>> geom.add_member(1, 2, "BC")  # Right diagonal
        >>> length = geom.get_member_length(0)  # Length of member AB
        >>> angle = geom.get_member_angle(1)    # Angle of member AC
    """

    def __init__(self) -> None:
        """Initialize an empty truss geometry."""
        self.nodes: List[TrussNode] = []
        self.members: List[TrussMember] = []

    def add_node(self, x: float, y: float, name: str = "") -> int:
        """
        Add a node to the truss geometry.

        Args:
            x: X-coordinate of the node.
            y: Y-coordinate of the node.
            name: Optional name for the node.

        Returns:
            Index of the newly added node.
        """
        node = TrussNode(x=x, y=y, name=name or f"N{len(self.nodes)}")
        self.nodes.append(node)
        return len(self.nodes) - 1

    def add_member(self, start_node_index: int, end_node_index: int, name: str = "") -> int:
        """
        Add a member connecting two nodes.

        Args:
            start_node_index: Index of the starting node.
            end_node_index: Index of the ending node.
            name: Optional name for the member.

        Returns:
            Index of the newly added member.

        Raises:
            IndexError: If node indices are out of range.
        """
        if start_node_index < 0 or start_node_index >= len(self.nodes):
            raise IndexError(f"Start node index {start_node_index} out of range")
        if end_node_index < 0 or end_node_index >= len(self.nodes):
            raise IndexError(f"End node index {end_node_index} out of range")

        member = TrussMember(
            start_node_index=start_node_index,
            end_node_index=end_node_index,
            name=name or f"M{len(self.members)}",
        )
        self.members.append(member)
        return len(self.members) - 1

    def get_node(self, index: int) -> TrussNode:
        """
        Get a node by its index.

        Args:
            index: Index of the node.

        Returns:
            TrussNode at the specified index.
        """
        return self.nodes[index]

    def get_member(self, index: int) -> TrussMember:
        """
        Get a member by its index.

        Args:
            index: Index of the member.

        Returns:
            TrussMember at the specified index.
        """
        return self.members[index]

    def get_member_nodes(self, member_index: int) -> Tuple[TrussNode, TrussNode]:
        """
        Get the start and end nodes of a member.

        Args:
            member_index: Index of the member.

        Returns:
            Tuple of (start_node, end_node).
        """
        member = self.members[member_index]
        return self.nodes[member.start_node_index], self.nodes[member.end_node_index]

    def get_member_length(self, member_index: int) -> float:
        """
        Calculate the length of a member.

        Args:
            member_index: Index of the member.

        Returns:
            Length of the member (same units as node coordinates).
        """
        start_node, end_node = self.get_member_nodes(member_index)
        dx = end_node.x - start_node.x
        dy = end_node.y - start_node.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_member_angle(self, member_index: int) -> float:
        """
        Calculate the angle of a member from horizontal.

        Args:
            member_index: Index of the member.

        Returns:
            Angle in degrees (positive counterclockwise from positive x-axis).
        """
        start_node, end_node = self.get_member_nodes(member_index)
        dx = end_node.x - start_node.x
        dy = end_node.y - start_node.y
        angle_rad = math.atan2(dy, dx)
        return math.degrees(angle_rad)

    def get_all_member_lengths(self) -> List[float]:
        """
        Calculate lengths of all members.

        Returns:
            List of member lengths in order.
        """
        return [self.get_member_length(i) for i in range(len(self.members))]

    def get_all_member_angles(self) -> List[float]:
        """
        Calculate angles of all members from horizontal.

        Returns:
            List of member angles in degrees.
        """
        return [self.get_member_angle(i) for i in range(len(self.members))]

    def get_members_at_node(self, node_index: int) -> List[int]:
        """
        Get indices of all members connected to a node.

        Args:
            node_index: Index of the node.

        Returns:
            List of member indices connected to the node.
        """
        connected = []
        for i, member in enumerate(self.members):
            if member.start_node_index == node_index or member.end_node_index == node_index:
                connected.append(i)
        return connected

    def get_node_coordinates(self, node_index: int) -> Tuple[float, float]:
        """
        Get the coordinates of a node.

        Args:
            node_index: Index of the node.

        Returns:
            Tuple of (x, y) coordinates.
        """
        node = self.nodes[node_index]
        return (node.x, node.y)

    def __repr__(self) -> str:
        return f"TrussGeometry(nodes={len(self.nodes)}, members={len(self.members)})"


# =============================================================================
# Calculation Classes
# =============================================================================


@register
class TrussNodeEquilibrium(Calculation):
    """
    Check equilibrium at a single truss node.

    For a node to be in equilibrium:
        Sum(Fx) = 0
        Sum(Fy) = 0

    This calculation sums all forces in x and y directions and determines
    if the node satisfies equilibrium conditions (within tolerance).
    """

    name = "Truss Node Equilibrium"
    category = "Trusses"
    description = (
        "Check equilibrium at a single truss node by summing forces "
        "in x and y directions. A node is in equilibrium when both sums are zero."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("forces_x", "N", "List of force components in the x-direction"),
        Parameter("forces_y", "N", "List of force components in the y-direction"),
    ]
    output_params = [
        Parameter("sum_fx", "N", "Sum of all forces in x-direction"),
        Parameter("sum_fy", "N", "Sum of all forces in y-direction"),
        Parameter("is_equilibrium", "dimensionless", "Boolean indicating if node is in equilibrium"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Check equilibrium at a truss node.

        Args:
            forces_x: List of x-direction force components as Quantities (N).
            forces_y: List of y-direction force components as Quantities (N).

        Returns:
            CalculationResult with sum of forces and equilibrium status.
        """
        self.reset()

        forces_x: List[Quantity] = kwargs["forces_x"]
        forces_y: List[Quantity] = kwargs["forces_y"]

        inputs = {
            "forces_x": forces_x,
            "forces_y": forces_y,
        }

        # Sum forces in x-direction
        sum_fx = Quantity(0.0, "N")
        for fx in forces_x:
            sum_fx = sum_fx + fx

        force_x_str = " + ".join(str(f) for f in forces_x) if forces_x else "0"
        self.add_step(
            description="Sum forces in x-direction",
            formula="Sum(Fx) = F1x + F2x + ... + Fnx",
            result=sum_fx,
            substitution=f"Sum(Fx) = {force_x_str} = {sum_fx}",
        )

        # Sum forces in y-direction
        sum_fy = Quantity(0.0, "N")
        for fy in forces_y:
            sum_fy = sum_fy + fy

        force_y_str = " + ".join(str(f) for f in forces_y) if forces_y else "0"
        self.add_step(
            description="Sum forces in y-direction",
            formula="Sum(Fy) = F1y + F2y + ... + Fny",
            result=sum_fy,
            substitution=f"Sum(Fy) = {force_y_str} = {sum_fy}",
        )

        # Check equilibrium (tolerance for floating point comparison)
        tolerance = 1e-6
        is_equilibrium = abs(sum_fx.magnitude) < tolerance and abs(sum_fy.magnitude) < tolerance

        self.add_step(
            description="Check equilibrium conditions",
            formula="Equilibrium if Sum(Fx) = 0 AND Sum(Fy) = 0",
            result=is_equilibrium,
            substitution=f"Is equilibrium: {is_equilibrium}",
        )

        outputs = {
            "sum_fx": sum_fx,
            "sum_fy": sum_fy,
            "is_equilibrium": is_equilibrium,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TrussMemberForce(Calculation):
    """
    Calculate force in a truss member using method of joints.

    Given a known force at a node and the angle of a member:
        F_member = F_node / cos(theta) for horizontal component
        F_member = F_node / sin(theta) for vertical component

    Tension is positive, compression is negative.
    """

    name = "Truss Member Force"
    category = "Trusses"
    description = (
        "Calculate the force in a truss member using the method of joints. "
        "Given a node force and member angle, determine axial member force."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("node_force", "N", "Known force at the node (positive away from node)"),
        Parameter("angle_from_horizontal", "deg", "Angle of member from horizontal"),
    ]
    output_params = [
        Parameter("member_force", "N", "Axial force in the member (positive = tension)"),
        Parameter("force_type", "dimensionless", "Type of force: tension or compression"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate member force using method of joints.

        Args:
            node_force: Known force at node as Quantity (N).
            angle_from_horizontal: Member angle as Quantity (deg).

        Returns:
            CalculationResult with member force and force type.
        """
        self.reset()

        node_force: Quantity = kwargs["node_force"]
        angle_from_horizontal: Quantity = kwargs["angle_from_horizontal"]

        inputs = {
            "node_force": node_force,
            "angle_from_horizontal": angle_from_horizontal,
        }

        # Convert angle to radians
        angle_rad = math.radians(angle_from_horizontal.magnitude)

        self.add_step(
            description="Convert angle to radians",
            formula="theta_rad = theta_deg x (pi/180)",
            result=angle_rad,
            substitution=f"theta_rad = {angle_from_horizontal.magnitude} x (pi/180) = {angle_rad:.6f} rad",
        )

        # Calculate member force
        # Using the projection: F_node = F_member * cos(theta) or sin(theta)
        # depending on whether force is horizontal or vertical component
        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)

        # Use the larger component for numerical stability
        if abs(cos_theta) >= abs(sin_theta):
            member_force_magnitude = node_force.magnitude / cos_theta if abs(cos_theta) > 1e-10 else 0
            component_used = "cosine"
        else:
            member_force_magnitude = node_force.magnitude / sin_theta if abs(sin_theta) > 1e-10 else 0
            component_used = "sine"

        member_force = Quantity(member_force_magnitude, "N")

        self.add_step(
            description=f"Calculate member force using {component_used} component",
            formula=f"F_member = F_node / {component_used}(theta)",
            result=member_force,
            substitution=f"F_member = {node_force} / {component_used}({angle_from_horizontal.magnitude}) = {member_force}",
        )

        # Determine force type
        force_type = "tension" if member_force_magnitude >= 0 else "compression"
        member_force = Quantity(abs(member_force_magnitude), "N")

        self.add_step(
            description="Determine force type",
            formula="Positive = tension, Negative = compression",
            result=force_type,
            substitution=f"Force type: {force_type}",
        )

        outputs = {
            "member_force": member_force,
            "force_type": force_type,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class SimpleTrussReactions(Calculation):
    """
    Calculate support reactions for a simple truss.

    Uses equilibrium equations:
        Sum(Fx) = 0
        Sum(Fy) = 0
        Sum(M) = 0

    Supports can be pin (resists x and y) or roller (resists y only).
    """

    name = "Simple Truss Reactions"
    category = "Trusses"
    description = (
        "Calculate support reactions for a simple truss with pin and roller supports. "
        "Uses equilibrium equations to solve for reactions."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("span", "m", "Total span of the truss"),
        Parameter("loads", "N", "List of dictionaries with 'position' (m) and 'magnitude' (N)"),
        Parameter("left_support_type", "dimensionless", "Type of left support: pin or roller"),
        Parameter("right_support_type", "dimensionless", "Type of right support: pin or roller"),
    ]
    output_params = [
        Parameter("left_reaction_x", "N", "Horizontal reaction at left support"),
        Parameter("left_reaction_y", "N", "Vertical reaction at left support"),
        Parameter("right_reaction_y", "N", "Vertical reaction at right support"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate support reactions for a simple truss.

        Args:
            span: Truss span as Quantity (m).
            loads: List of dicts with 'position' and 'magnitude' keys.
            left_support_type: 'pin' or 'roller'.
            right_support_type: 'pin' or 'roller'.

        Returns:
            CalculationResult with support reactions.

        Raises:
            ValueError: If support types are invalid or both are rollers.
        """
        self.reset()

        span: Quantity = kwargs["span"]
        loads: List[Dict[str, Any]] = kwargs["loads"]
        left_support_type: str = kwargs["left_support_type"]
        right_support_type: str = kwargs["right_support_type"]

        inputs = {
            "span": span,
            "loads": loads,
            "left_support_type": left_support_type,
            "right_support_type": right_support_type,
        }

        # Validate support types
        valid_types = ["pin", "roller"]
        if left_support_type not in valid_types:
            raise ValueError(f"Invalid left support type: {left_support_type}. Must be 'pin' or 'roller'.")
        if right_support_type not in valid_types:
            raise ValueError(f"Invalid right support type: {right_support_type}. Must be 'pin' or 'roller'.")
        if left_support_type == "roller" and right_support_type == "roller":
            raise ValueError("Cannot have both supports as rollers - structure is unstable horizontally.")

        # Calculate total vertical load and moment about left support
        total_vertical_load = 0.0
        moment_about_left = 0.0

        for load in loads:
            position = load["position"]
            magnitude = load["magnitude"]

            # Handle both Quantity and numeric types
            pos_val = position.magnitude if isinstance(position, Quantity) else position
            mag_val = magnitude.magnitude if isinstance(magnitude, Quantity) else magnitude

            total_vertical_load += mag_val
            moment_about_left += mag_val * pos_val

        self.add_step(
            description="Calculate total vertical load",
            formula="P_total = Sum(P_i)",
            result=Quantity(total_vertical_load, "N"),
            substitution=f"P_total = {total_vertical_load} N",
        )

        self.add_step(
            description="Calculate moment about left support",
            formula="M_left = Sum(P_i x d_i)",
            result=Quantity(moment_about_left, "N*m"),
            substitution=f"M_left = {moment_about_left} N*m",
        )

        # Calculate right reaction using moment equilibrium about left support
        span_val = span.magnitude if isinstance(span, Quantity) else span
        right_reaction_y_val = moment_about_left / span_val if span_val > 0 else 0

        self.add_step(
            description="Calculate right vertical reaction from moment equilibrium",
            formula="R_right_y = M_left / L",
            result=Quantity(right_reaction_y_val, "N"),
            substitution=f"R_right_y = {moment_about_left} / {span_val} = {right_reaction_y_val} N",
        )

        # Calculate left vertical reaction from force equilibrium
        left_reaction_y_val = total_vertical_load - right_reaction_y_val

        self.add_step(
            description="Calculate left vertical reaction from force equilibrium",
            formula="R_left_y = P_total - R_right_y",
            result=Quantity(left_reaction_y_val, "N"),
            substitution=f"R_left_y = {total_vertical_load} - {right_reaction_y_val} = {left_reaction_y_val} N",
        )

        # Horizontal reaction (only at pin support, assumed no horizontal loads)
        left_reaction_x_val = 0.0

        self.add_step(
            description="Horizontal reaction (assuming no horizontal loads)",
            formula="R_left_x = 0 (no horizontal loads)",
            result=Quantity(left_reaction_x_val, "N"),
            substitution=f"R_left_x = {left_reaction_x_val} N",
        )

        outputs = {
            "left_reaction_x": Quantity(left_reaction_x_val, "N"),
            "left_reaction_y": Quantity(left_reaction_y_val, "N"),
            "right_reaction_y": Quantity(right_reaction_y_val, "N"),
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class MethodOfSections(Calculation):
    """
    Analyze a truss member using method of sections.

    The method of sections involves:
    1. Cutting through the truss to expose the member of interest
    2. Taking moments about a point to solve for unknown forces
    3. Using equilibrium to find member force

    Formula: F_member x moment_arm = Sum(known_moments)
    """

    name = "Method of Sections"
    category = "Trusses"
    description = (
        "Analyze a truss using method of sections. Cut through the truss "
        "and use moment equilibrium to find member forces directly."
    )
    references = ["Engineering Mechanics: Statics, Hibbeler"]

    input_params = [
        Parameter("moment_arm", "m", "Perpendicular distance from moment point to member line of action"),
        Parameter("known_forces", "N", "List of known forces creating moment about the point"),
        Parameter("cut_member_angle", "deg", "Angle of the cut member from horizontal"),
    ]
    output_params = [
        Parameter("member_force", "N", "Calculated force in the member"),
        Parameter("force_type", "dimensionless", "Type of force: tension or compression"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate member force using method of sections.

        Args:
            moment_arm: Perpendicular distance as Quantity (m).
            known_forces: List of known moments/forces as Quantities (N).
            cut_member_angle: Angle of member as Quantity (deg).

        Returns:
            CalculationResult with member force and force type.
        """
        self.reset()

        moment_arm: Quantity = kwargs["moment_arm"]
        known_forces: List[Quantity] = kwargs["known_forces"]
        cut_member_angle: Quantity = kwargs["cut_member_angle"]

        inputs = {
            "moment_arm": moment_arm,
            "known_forces": known_forces,
            "cut_member_angle": cut_member_angle,
        }

        # Sum known forces (assuming they all create moment about the same point)
        total_moment = Quantity(0.0, "N*m")
        for force in known_forces:
            # Assuming forces are given with their moment contribution
            total_moment = total_moment + force * moment_arm

        forces_str = " + ".join(str(f) for f in known_forces) if known_forces else "0"
        self.add_step(
            description="Sum known moments about the point",
            formula="M_total = Sum(F_i x d_i)",
            result=total_moment,
            substitution=f"M_total = ({forces_str}) x {moment_arm} = {total_moment}",
        )

        # Calculate member force from moment equilibrium
        # F_member x moment_arm = total_moment
        moment_arm_val = moment_arm.magnitude
        total_moment_val = total_moment.magnitude

        member_force_val = total_moment_val / moment_arm_val if moment_arm_val > 0 else 0

        self.add_step(
            description="Calculate member force from moment equilibrium",
            formula="F_member = M_total / moment_arm",
            result=Quantity(member_force_val, "N"),
            substitution=f"F_member = {total_moment} / {moment_arm} = {member_force_val} N",
        )

        # Determine force type based on sign
        force_type = "tension" if member_force_val >= 0 else "compression"
        member_force = Quantity(abs(member_force_val), "N")

        self.add_step(
            description="Determine force type",
            formula="Positive assumed tension, negative indicates compression",
            result=force_type,
            substitution=f"Force type: {force_type}",
        )

        outputs = {
            "member_force": member_force,
            "force_type": force_type,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TrussMemberStress(Calculation):
    """
    Calculate axial stress in a truss member.

    Formula: sigma = F / A

    Where:
        sigma = axial stress (Pa)
        F = axial force in member (N)
        A = cross-sectional area (m^2)
    """

    name = "Truss Member Stress"
    category = "Trusses"
    description = (
        "Calculate the axial stress in a truss member. sigma = F / A"
    )
    references = ["Mechanics of Materials, Hibbeler"]

    input_params = [
        Parameter("member_force", "N", "Axial force in the member"),
        Parameter("cross_section_area", "m**2", "Cross-sectional area of the member"),
    ]
    output_params = [
        Parameter("axial_stress", "Pa", "Axial stress in the member"),
        Parameter("is_tension", "dimensionless", "Boolean indicating if member is in tension"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate axial stress in a truss member.

        Args:
            member_force: Axial force as Quantity (N).
            cross_section_area: Area as Quantity (m^2).

        Returns:
            CalculationResult with axial stress and tension indicator.
        """
        self.reset()

        member_force: Quantity = kwargs["member_force"]
        cross_section_area: Quantity = kwargs["cross_section_area"]

        inputs = {
            "member_force": member_force,
            "cross_section_area": cross_section_area,
        }

        # Calculate axial stress: sigma = F / A
        axial_stress = member_force / cross_section_area

        self.add_step(
            description="Calculate axial stress",
            formula="sigma = F / A",
            result=axial_stress,
            substitution=f"sigma = {member_force} / {cross_section_area} = {axial_stress}",
        )

        # Determine if tension or compression
        is_tension = member_force.magnitude >= 0

        self.add_step(
            description="Determine stress type",
            formula="Positive force = tension, Negative force = compression",
            result=is_tension,
            substitution=f"Is tension: {is_tension}",
        )

        outputs = {
            "axial_stress": axial_stress,
            "is_tension": is_tension,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TrussDeflection(Calculation):
    """
    Calculate deflection contribution using virtual work method.

    For a single member, the deflection contribution is:
        delta_i = (F x f x L) / (A x E)

    Where:
        F = actual member force (N)
        f = virtual member force (N) - from unit load at deflection point
        L = member length (m)
        A = cross-sectional area (m^2)
        E = elastic modulus (Pa)

    Total deflection is sum of all member contributions.
    """

    name = "Truss Deflection - Virtual Work"
    category = "Trusses"
    description = (
        "Calculate deflection contribution of a single member using the "
        "virtual work method. delta = (F x f x L) / (A x E)"
    )
    references = ["Structural Analysis, Hibbeler", "Matrix Analysis of Structures, Kassimali"]

    input_params = [
        Parameter("member_force", "N", "Actual axial force in the member"),
        Parameter("virtual_force", "N", "Virtual force in member from unit load"),
        Parameter("member_length", "m", "Length of the member"),
        Parameter("area", "m**2", "Cross-sectional area of the member"),
        Parameter("elastic_modulus", "Pa", "Elastic modulus of member material"),
    ]
    output_params = [
        Parameter("deflection_contribution", "m", "Deflection contribution from this member"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate deflection contribution using virtual work.

        Args:
            member_force: Actual force as Quantity (N).
            virtual_force: Virtual force as Quantity (N).
            member_length: Length as Quantity (m).
            area: Cross-sectional area as Quantity (m^2).
            elastic_modulus: Elastic modulus as Quantity (Pa).

        Returns:
            CalculationResult with deflection contribution.
        """
        self.reset()

        member_force: Quantity = kwargs["member_force"]
        virtual_force: Quantity = kwargs["virtual_force"]
        member_length: Quantity = kwargs["member_length"]
        area: Quantity = kwargs["area"]
        elastic_modulus: Quantity = kwargs["elastic_modulus"]

        inputs = {
            "member_force": member_force,
            "virtual_force": virtual_force,
            "member_length": member_length,
            "area": area,
            "elastic_modulus": elastic_modulus,
        }

        # Calculate numerator: F x f x L
        numerator = member_force * virtual_force * member_length

        self.add_step(
            description="Calculate numerator (F x f x L)",
            formula="Numerator = F x f x L",
            result=numerator,
            substitution=f"Numerator = {member_force} x {virtual_force} x {member_length} = {numerator}",
        )

        # Calculate denominator: A x E
        denominator = area * elastic_modulus

        self.add_step(
            description="Calculate denominator (A x E)",
            formula="Denominator = A x E",
            result=denominator,
            substitution=f"Denominator = {area} x {elastic_modulus} = {denominator}",
        )

        # Calculate deflection contribution
        deflection_contribution = numerator / denominator

        self.add_step(
            description="Calculate deflection contribution",
            formula="delta_i = (F x f x L) / (A x E)",
            result=deflection_contribution,
            substitution=f"delta_i = {numerator} / {denominator} = {deflection_contribution}",
        )

        outputs = {
            "deflection_contribution": deflection_contribution,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class CriticalBucklingLoad(Calculation):
    """
    Calculate Euler critical buckling load for compression members.

    Formula: P_cr = (pi^2 x E x I) / (L_eff)^2

    Where:
        P_cr = critical buckling load (N)
        E = elastic modulus (Pa)
        I = moment of inertia (m^4)
        L_eff = effective length (m)

    The effective length depends on end conditions:
        - Both ends pinned: L_eff = L
        - One end fixed, one end free: L_eff = 2L
        - Both ends fixed: L_eff = 0.5L
        - One end fixed, one end pinned: L_eff = 0.7L
    """

    name = "Critical Buckling Load"
    category = "Trusses"
    description = (
        "Calculate Euler critical buckling load for compression members. "
        "P_cr = (pi^2 x E x I) / L_eff^2"
    )
    references = ["Mechanics of Materials, Hibbeler", "Steel Design, Segui"]

    input_params = [
        Parameter("elastic_modulus", "Pa", "Elastic modulus of member material"),
        Parameter("moment_of_inertia", "m**4", "Minimum moment of inertia of cross-section"),
        Parameter("effective_length", "m", "Effective length of the member"),
    ]
    output_params = [
        Parameter("critical_load", "N", "Euler critical buckling load"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate critical buckling load.

        Args:
            elastic_modulus: E as Quantity (Pa).
            moment_of_inertia: I as Quantity (m^4).
            effective_length: L_eff as Quantity (m).

        Returns:
            CalculationResult with critical buckling load.
        """
        self.reset()

        elastic_modulus: Quantity = kwargs["elastic_modulus"]
        moment_of_inertia: Quantity = kwargs["moment_of_inertia"]
        effective_length: Quantity = kwargs["effective_length"]

        inputs = {
            "elastic_modulus": elastic_modulus,
            "moment_of_inertia": moment_of_inertia,
            "effective_length": effective_length,
        }

        # Calculate pi^2
        pi_squared = math.pi ** 2

        self.add_step(
            description="Calculate pi squared",
            formula="pi^2",
            result=pi_squared,
            substitution=f"pi^2 = {pi_squared:.6f}",
        )

        # Calculate numerator: pi^2 x E x I
        numerator = pi_squared * elastic_modulus * moment_of_inertia

        self.add_step(
            description="Calculate numerator (pi^2 x E x I)",
            formula="Numerator = pi^2 x E x I",
            result=numerator,
            substitution=f"Numerator = {pi_squared:.6f} x {elastic_modulus} x {moment_of_inertia} = {numerator}",
        )

        # Calculate L_eff^2
        length_squared = effective_length ** 2

        self.add_step(
            description="Calculate effective length squared",
            formula="L_eff^2",
            result=length_squared,
            substitution=f"L_eff^2 = ({effective_length})^2 = {length_squared}",
        )

        # Calculate critical load
        critical_load = numerator / length_squared

        self.add_step(
            description="Calculate critical buckling load",
            formula="P_cr = (pi^2 x E x I) / L_eff^2",
            result=critical_load,
            substitution=f"P_cr = {numerator} / {length_squared} = {critical_load}",
        )

        outputs = {
            "critical_load": critical_load,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


@register
class TrussEfficiency(Calculation):
    """
    Calculate overall truss efficiency.

    Efficiency ratio is a measure of how effectively the truss material
    is used to carry load:

    Formula: efficiency = total_load_capacity / total_member_weight

    A higher ratio indicates a more efficient structure that can carry
    more load per unit weight of material.
    """

    name = "Truss Efficiency"
    category = "Trusses"
    description = (
        "Calculate overall truss efficiency as the ratio of load capacity "
        "to total member weight. Higher values indicate better efficiency."
    )
    references = ["Structural Engineering Handbook, Gaylord"]

    input_params = [
        Parameter("total_load_capacity", "N", "Maximum load the truss can carry"),
        Parameter("total_member_weight", "N", "Total weight of all truss members"),
    ]
    output_params = [
        Parameter("efficiency_ratio", "dimensionless", "Ratio of load capacity to weight"),
    ]

    def calculate(self, **kwargs: Any) -> CalculationResult:
        """
        Calculate truss efficiency ratio.

        Args:
            total_load_capacity: Maximum load capacity as Quantity (N).
            total_member_weight: Total member weight as Quantity (N).

        Returns:
            CalculationResult with efficiency ratio.
        """
        self.reset()

        total_load_capacity: Quantity = kwargs["total_load_capacity"]
        total_member_weight: Quantity = kwargs["total_member_weight"]

        inputs = {
            "total_load_capacity": total_load_capacity,
            "total_member_weight": total_member_weight,
        }

        # Calculate efficiency ratio
        efficiency_ratio = total_load_capacity / total_member_weight

        self.add_step(
            description="Calculate efficiency ratio",
            formula="efficiency = P_capacity / W_total",
            result=efficiency_ratio,
            substitution=f"efficiency = {total_load_capacity} / {total_member_weight} = {efficiency_ratio}",
        )

        # Extract dimensionless value
        efficiency_value = efficiency_ratio.magnitude

        self.add_step(
            description="Express as dimensionless ratio",
            formula="Efficiency is dimensionless (force/force)",
            result=efficiency_value,
            substitution=f"Efficiency ratio = {efficiency_value:.4f}",
        )

        outputs = {
            "efficiency_ratio": efficiency_value,
        }

        return self.format_result(inputs=inputs, outputs=outputs)


# Module exports
__all__ = [
    # Helper classes
    "TrussNode",
    "TrussMember",
    "TrussGeometry",
    # Calculation classes
    "TrussNodeEquilibrium",
    "TrussMemberForce",
    "SimpleTrussReactions",
    "MethodOfSections",
    "TrussMemberStress",
    "TrussDeflection",
    "CriticalBucklingLoad",
    "TrussEfficiency",
]
