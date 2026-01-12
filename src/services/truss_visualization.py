"""
Truss visualization service for Engineering Calculations Database.

This module provides visualization functionality for truss structures using Plotly,
creating interactive diagrams for structural analysis including:
- Basic truss geometry diagrams
- Force diagrams with color-coded tension/compression
- Deflected shape visualization
- Reaction and load diagrams with support symbols

References:
    - Plotly Python Documentation: https://plotly.com/python/
    - Hibbeler, R.C., "Structural Analysis", 10th Ed.
    - Kassimali, A., "Structural Analysis", 6th Ed.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import plotly.graph_objects as go

from src.domains.trusses import TrussGeometry


# Default styling constants for consistent appearance
LIGHT_THEME = {
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "font_color": "#2c3e50",
    "gridcolor": "#ecf0f1",
    "linecolor": "#bdc3c7",
    "primary_color": "#3498db",
    "secondary_color": "#e74c3c",
    "tertiary_color": "#2ecc71",
    "accent_color": "#9b59b6",
}

DARK_THEME = {
    "paper_bgcolor": "#1a1a2e",
    "plot_bgcolor": "#16213e",
    "font_color": "#eaeaea",
    "gridcolor": "#2d3436",
    "linecolor": "#636e72",
    "primary_color": "#00d9ff",
    "secondary_color": "#ff6b6b",
    "tertiary_color": "#4ecdc4",
    "accent_color": "#a29bfe",
}

# Force visualization colors
TENSION_COLOR = "#3498db"  # Blue for tension (positive)
COMPRESSION_COLOR = "#e74c3c"  # Red for compression (negative)
ZERO_FORCE_COLOR = "#95a5a6"  # Gray for zero force
REACTION_COLOR = "#2ecc71"  # Green for reactions
LOAD_COLOR = "#e74c3c"  # Red for applied loads
ORIGINAL_SHAPE_COLOR = "#95a5a6"  # Gray for original shape
DEFLECTED_SHAPE_COLOR = "#3498db"  # Blue for deflected shape


class TrussVisualization:
    """
    Service class for creating truss structure visualizations using Plotly.

    This class provides methods for creating various types of truss diagrams
    commonly used in structural analysis. All diagrams follow a consistent
    styling scheme and are fully interactive.

    Attributes:
        default_width: Default chart width in pixels.
        default_height: Default chart height in pixels.
        default_font_family: Font family for all text elements.
        dark_mode: Whether to use dark theme.

    Example:
        >>> from src.domains.trusses import TrussGeometry
        >>> geom = TrussGeometry()
        >>> geom.add_node(0, 0, "A")
        >>> geom.add_node(3, 0, "B")
        >>> geom.add_node(1.5, 2, "C")
        >>> geom.add_member(0, 1, "AB")
        >>> geom.add_member(0, 2, "AC")
        >>> geom.add_member(1, 2, "BC")
        >>> viz = TrussVisualization()
        >>> fig = viz.create_truss_diagram(geom, title="Simple Truss")
        >>> fig.show()
    """

    def __init__(
        self,
        default_width: int = 800,
        default_height: int = 600,
        default_font_family: str = "Arial, sans-serif",
        dark_mode: bool = False,
    ) -> None:
        """
        Initialize the TrussVisualization service.

        Args:
            default_width: Default chart width in pixels.
            default_height: Default chart height in pixels.
            default_font_family: Font family for all text elements.
            dark_mode: Whether to use dark theme.
        """
        self.default_width = default_width
        self.default_height = default_height
        self.default_font_family = default_font_family
        self.dark_mode = dark_mode

    def _get_theme(self) -> Dict[str, str]:
        """Get the current theme dictionary."""
        return DARK_THEME if self.dark_mode else LIGHT_THEME

    def create_truss_diagram(
        self,
        geometry: TrussGeometry,
        title: str = "Truss Diagram",
    ) -> go.Figure:
        """
        Create a basic truss diagram showing nodes and members.

        This method creates an interactive diagram displaying:
        - Nodes as labeled circles
        - Members as lines connecting nodes
        - Node coordinates shown on hover
        - Grid and axis labels in meters

        Args:
            geometry: TrussGeometry object containing nodes and members.
            title: Title for the diagram.

        Returns:
            A Plotly Figure object containing the truss diagram.

        Example:
            >>> geom = TrussGeometry()
            >>> geom.add_node(0, 0, "A")
            >>> geom.add_node(4, 0, "B")
            >>> geom.add_node(2, 3, "C")
            >>> geom.add_member(0, 1)
            >>> geom.add_member(0, 2)
            >>> geom.add_member(1, 2)
            >>> viz = TrussVisualization()
            >>> fig = viz.create_truss_diagram(geom)
        """
        theme = self._get_theme()
        fig = go.Figure()

        # Draw members as lines
        for i, member in enumerate(geometry.members):
            start_node = geometry.nodes[member.start_node_index]
            end_node = geometry.nodes[member.end_node_index]

            fig.add_trace(
                go.Scatter(
                    x=[start_node.x, end_node.x],
                    y=[start_node.y, end_node.y],
                    mode="lines",
                    name=member.name or f"Member {i}",
                    line=dict(color=theme["primary_color"], width=3),
                    hoverinfo="text",
                    hovertext=f"{member.name or f'Member {i}'}<br>"
                              f"Length: {geometry.get_member_length(i):.3f} m",
                    showlegend=False,
                )
            )

        # Draw nodes as circles with labels
        node_x = [node.x for node in geometry.nodes]
        node_y = [node.y for node in geometry.nodes]
        node_labels = [node.name for node in geometry.nodes]
        hover_text = [
            f"Node: {node.name}<br>x: {node.x:.3f} m<br>y: {node.y:.3f} m"
            for node in geometry.nodes
        ]

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                name="Nodes",
                marker=dict(
                    size=20,
                    color=theme["paper_bgcolor"],
                    line=dict(color=theme["primary_color"], width=2),
                ),
                text=node_labels,
                textposition="top center",
                textfont=dict(size=12, color=theme["font_color"]),
                hoverinfo="text",
                hovertext=hover_text,
            )
        )

        # Apply layout
        self._apply_layout(fig, title, geometry)

        return fig

    def create_force_diagram(
        self,
        geometry: TrussGeometry,
        member_forces: Dict[int, float],
        title: str = "Force Diagram",
    ) -> go.Figure:
        """
        Create a force diagram with color-coded members based on force values.

        This method creates a diagram where:
        - Members in tension (positive force) are colored blue
        - Members in compression (negative force) are colored red
        - Members with zero force are colored gray
        - Line thickness is proportional to force magnitude
        - Force values are shown on hover

        Args:
            geometry: TrussGeometry object containing nodes and members.
            member_forces: Dictionary mapping member index to force value (N).
                          Positive values indicate tension, negative indicate compression.
            title: Title for the diagram.

        Returns:
            A Plotly Figure object containing the force diagram.

        Example:
            >>> geom = TrussGeometry()
            >>> geom.add_node(0, 0, "A")
            >>> geom.add_node(4, 0, "B")
            >>> geom.add_node(2, 3, "C")
            >>> geom.add_member(0, 1)  # Member 0
            >>> geom.add_member(0, 2)  # Member 1
            >>> geom.add_member(1, 2)  # Member 2
            >>> forces = {0: 10000, 1: -5000, 2: -5000}  # N
            >>> viz = TrussVisualization()
            >>> fig = viz.create_force_diagram(geom, forces)
        """
        theme = self._get_theme()
        fig = go.Figure()

        # Find maximum force magnitude for scaling line widths
        force_values = list(member_forces.values())
        max_force = max(abs(f) for f in force_values) if force_values else 1.0

        # Draw members with force-based coloring
        for i, member in enumerate(geometry.members):
            start_node = geometry.nodes[member.start_node_index]
            end_node = geometry.nodes[member.end_node_index]

            force = member_forces.get(i, 0.0)
            color = self._get_force_color(force)
            width = self._scale_line_width(force, max_force)

            # Determine force type for display
            if force > 0:
                force_type = "Tension"
            elif force < 0:
                force_type = "Compression"
            else:
                force_type = "Zero Force"

            fig.add_trace(
                go.Scatter(
                    x=[start_node.x, end_node.x],
                    y=[start_node.y, end_node.y],
                    mode="lines",
                    name=member.name or f"Member {i}",
                    line=dict(color=color, width=width),
                    hoverinfo="text",
                    hovertext=f"{member.name or f'Member {i}'}<br>"
                              f"Force: {force:.2f} N<br>"
                              f"Type: {force_type}",
                    showlegend=False,
                )
            )

        # Draw nodes
        node_x = [node.x for node in geometry.nodes]
        node_y = [node.y for node in geometry.nodes]
        node_labels = [node.name for node in geometry.nodes]
        hover_text = [
            f"Node: {node.name}<br>x: {node.x:.3f} m<br>y: {node.y:.3f} m"
            for node in geometry.nodes
        ]

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                name="Nodes",
                marker=dict(
                    size=16,
                    color=theme["paper_bgcolor"],
                    line=dict(color=theme["linecolor"], width=2),
                ),
                text=node_labels,
                textposition="top center",
                textfont=dict(size=12, color=theme["font_color"]),
                hoverinfo="text",
                hovertext=hover_text,
            )
        )

        # Add legend for force types
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Tension (+)",
                line=dict(color=TENSION_COLOR, width=4),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Compression (-)",
                line=dict(color=COMPRESSION_COLOR, width=4),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Zero Force",
                line=dict(color=ZERO_FORCE_COLOR, width=2),
            )
        )

        # Apply layout
        self._apply_layout(fig, title, geometry, show_legend=True)

        return fig

    def create_deflected_shape(
        self,
        geometry: TrussGeometry,
        node_displacements: Dict[int, Tuple[float, float]],
        scale: float = 100.0,
        title: str = "Deflected Shape",
    ) -> go.Figure:
        """
        Create a deflected shape diagram showing original and displaced positions.

        This method creates a diagram displaying:
        - Original truss shape in gray dashed lines
        - Deflected shape in solid color
        - Displacements scaled for visibility
        - Displacement values shown on hover

        Args:
            geometry: TrussGeometry object containing nodes and members.
            node_displacements: Dictionary mapping node index to displacement tuple (dx, dy) in meters.
            scale: Scale factor for displacement visualization (default: 100).
            title: Title for the diagram.

        Returns:
            A Plotly Figure object containing the deflected shape diagram.

        Example:
            >>> geom = TrussGeometry()
            >>> geom.add_node(0, 0, "A")
            >>> geom.add_node(4, 0, "B")
            >>> geom.add_node(2, 3, "C")
            >>> geom.add_member(0, 1)
            >>> geom.add_member(0, 2)
            >>> geom.add_member(1, 2)
            >>> displacements = {0: (0, 0), 1: (0, 0), 2: (0.001, -0.002)}
            >>> viz = TrussVisualization()
            >>> fig = viz.create_deflected_shape(geom, displacements, scale=500)
        """
        theme = self._get_theme()
        fig = go.Figure()

        # Draw original shape (gray dashed lines)
        for i, member in enumerate(geometry.members):
            start_node = geometry.nodes[member.start_node_index]
            end_node = geometry.nodes[member.end_node_index]

            fig.add_trace(
                go.Scatter(
                    x=[start_node.x, end_node.x],
                    y=[start_node.y, end_node.y],
                    mode="lines",
                    name=f"Original {member.name}" if i == 0 else None,
                    line=dict(color=ORIGINAL_SHAPE_COLOR, width=2, dash="dash"),
                    hoverinfo="skip",
                    showlegend=(i == 0),
                    legendgroup="original",
                )
            )

        # Draw deflected shape (solid color)
        for i, member in enumerate(geometry.members):
            start_node = geometry.nodes[member.start_node_index]
            end_node = geometry.nodes[member.end_node_index]

            # Get displacements (default to zero if not provided)
            dx1, dy1 = node_displacements.get(member.start_node_index, (0.0, 0.0))
            dx2, dy2 = node_displacements.get(member.end_node_index, (0.0, 0.0))

            # Apply scaled displacements
            deflected_x1 = start_node.x + dx1 * scale
            deflected_y1 = start_node.y + dy1 * scale
            deflected_x2 = end_node.x + dx2 * scale
            deflected_y2 = end_node.y + dy2 * scale

            fig.add_trace(
                go.Scatter(
                    x=[deflected_x1, deflected_x2],
                    y=[deflected_y1, deflected_y2],
                    mode="lines",
                    name=f"Deflected {member.name}" if i == 0 else None,
                    line=dict(color=DEFLECTED_SHAPE_COLOR, width=3),
                    hoverinfo="text",
                    hovertext=f"{member.name or f'Member {i}'} (Deflected)",
                    showlegend=(i == 0),
                    legendgroup="deflected",
                )
            )

        # Draw original nodes
        original_x = [node.x for node in geometry.nodes]
        original_y = [node.y for node in geometry.nodes]

        fig.add_trace(
            go.Scatter(
                x=original_x,
                y=original_y,
                mode="markers",
                name="Original Position",
                marker=dict(
                    size=12,
                    color=ORIGINAL_SHAPE_COLOR,
                    symbol="circle-open",
                    line=dict(width=2),
                ),
                hoverinfo="skip",
            )
        )

        # Draw deflected nodes with displacement info
        deflected_x = []
        deflected_y = []
        hover_text = []
        node_labels = []

        for i, node in enumerate(geometry.nodes):
            dx, dy = node_displacements.get(i, (0.0, 0.0))
            deflected_x.append(node.x + dx * scale)
            deflected_y.append(node.y + dy * scale)
            node_labels.append(node.name)

            # Calculate total displacement magnitude
            total_disp = math.sqrt(dx ** 2 + dy ** 2)

            hover_text.append(
                f"Node: {node.name}<br>"
                f"Original: ({node.x:.3f}, {node.y:.3f}) m<br>"
                f"dx: {dx * 1000:.4f} mm<br>"
                f"dy: {dy * 1000:.4f} mm<br>"
                f"Total: {total_disp * 1000:.4f} mm<br>"
                f"(Scale: {scale}x)"
            )

        fig.add_trace(
            go.Scatter(
                x=deflected_x,
                y=deflected_y,
                mode="markers+text",
                name="Deflected Position",
                marker=dict(
                    size=16,
                    color=DEFLECTED_SHAPE_COLOR,
                    line=dict(color=theme["linecolor"], width=2),
                ),
                text=node_labels,
                textposition="top center",
                textfont=dict(size=12, color=theme["font_color"]),
                hoverinfo="text",
                hovertext=hover_text,
            )
        )

        # Apply layout with scale annotation
        self._apply_layout(fig, f"{title} (Scale: {scale}x)", geometry, show_legend=True)

        return fig

    def create_reaction_diagram(
        self,
        geometry: TrussGeometry,
        reactions: Dict[int, Tuple[float, float]],
        loads: Dict[int, Tuple[float, float]],
        title: str = "Reactions & Loads",
    ) -> go.Figure:
        """
        Create a diagram showing truss structure with reaction and load arrows.

        This method creates a diagram displaying:
        - Truss structure with nodes and members
        - Support symbols (triangles for pins, circles for rollers)
        - Reaction arrows in green
        - Load arrows in red
        - Arrow lengths proportional to force magnitude

        Args:
            geometry: TrussGeometry object containing nodes and members.
            reactions: Dictionary mapping node index to reaction tuple (Rx, Ry) in N.
            loads: Dictionary mapping node index to load tuple (Fx, Fy) in N.
            title: Title for the diagram.

        Returns:
            A Plotly Figure object containing the reaction diagram.

        Example:
            >>> geom = TrussGeometry()
            >>> geom.add_node(0, 0, "A")
            >>> geom.add_node(4, 0, "B")
            >>> geom.add_node(2, 3, "C")
            >>> geom.add_member(0, 1)
            >>> geom.add_member(0, 2)
            >>> geom.add_member(1, 2)
            >>> reactions = {0: (0, 5000), 1: (0, 5000)}  # N
            >>> loads = {2: (0, -10000)}  # N
            >>> viz = TrussVisualization()
            >>> fig = viz.create_reaction_diagram(geom, reactions, loads)
        """
        theme = self._get_theme()
        fig = go.Figure()

        # Draw members
        for i, member in enumerate(geometry.members):
            start_node = geometry.nodes[member.start_node_index]
            end_node = geometry.nodes[member.end_node_index]

            fig.add_trace(
                go.Scatter(
                    x=[start_node.x, end_node.x],
                    y=[start_node.y, end_node.y],
                    mode="lines",
                    line=dict(color=theme["primary_color"], width=3),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Calculate arrow scale based on maximum force magnitude
        all_forces = []
        for rx, ry in reactions.values():
            all_forces.extend([abs(rx), abs(ry)])
        for fx, fy in loads.values():
            all_forces.extend([abs(fx), abs(fy)])

        max_force = max(all_forces) if all_forces else 1.0

        # Get geometry bounds for arrow scaling
        x_coords = [node.x for node in geometry.nodes]
        y_coords = [node.y for node in geometry.nodes]
        x_range = max(x_coords) - min(x_coords) if x_coords else 1.0
        y_range = max(y_coords) - min(y_coords) if y_coords else 1.0
        geom_scale = max(x_range, y_range)

        # Arrow length scale factor (max arrow = 30% of geometry size)
        arrow_scale = 0.3 * geom_scale / max_force if max_force > 0 else 0.1

        # Draw load arrows (red)
        for node_idx, (fx, fy) in loads.items():
            if abs(fx) > 1e-10 or abs(fy) > 1e-10:
                node = geometry.nodes[node_idx]

                # Arrow starts away from node, points to node
                arrow_dx = fx * arrow_scale
                arrow_dy = fy * arrow_scale

                start_x = node.x - arrow_dx
                start_y = node.y - arrow_dy
                end_x = node.x
                end_y = node.y

                force_mag = math.sqrt(fx ** 2 + fy ** 2)

                self._draw_arrow(
                    fig,
                    start=(start_x, start_y),
                    end=(end_x, end_y),
                    color=LOAD_COLOR,
                    label=f"Load at {node.name}<br>Fx: {fx:.2f} N<br>Fy: {fy:.2f} N<br>|F|: {force_mag:.2f} N",
                )

        # Draw reaction arrows (green)
        for node_idx, (rx, ry) in reactions.items():
            if abs(rx) > 1e-10 or abs(ry) > 1e-10:
                node = geometry.nodes[node_idx]

                # Arrow starts at node, points away in direction of reaction
                arrow_dx = rx * arrow_scale
                arrow_dy = ry * arrow_scale

                start_x = node.x
                start_y = node.y
                end_x = node.x + arrow_dx
                end_y = node.y + arrow_dy

                force_mag = math.sqrt(rx ** 2 + ry ** 2)

                self._draw_arrow(
                    fig,
                    start=(start_x, start_y),
                    end=(end_x, end_y),
                    color=REACTION_COLOR,
                    label=f"Reaction at {node.name}<br>Rx: {rx:.2f} N<br>Ry: {ry:.2f} N<br>|R|: {force_mag:.2f} N",
                )

        # Draw nodes
        node_x = [node.x for node in geometry.nodes]
        node_y = [node.y for node in geometry.nodes]
        node_labels = [node.name for node in geometry.nodes]

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                name="Nodes",
                marker=dict(
                    size=16,
                    color=theme["paper_bgcolor"],
                    line=dict(color=theme["primary_color"], width=2),
                ),
                text=node_labels,
                textposition="top center",
                textfont=dict(size=12, color=theme["font_color"]),
                hoverinfo="skip",
            )
        )

        # Add legend entries
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Applied Loads",
                line=dict(color=LOAD_COLOR, width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Reactions",
                line=dict(color=REACTION_COLOR, width=3),
            )
        )

        # Apply layout
        self._apply_layout(fig, title, geometry, show_legend=True, extra_margin=0.4)

        return fig

    def add_supports(
        self,
        fig: go.Figure,
        geometry: TrussGeometry,
        pin_nodes: List[int],
        roller_nodes: List[int],
    ) -> go.Figure:
        """
        Add support symbols to an existing figure.

        This method adds standard structural support symbols:
        - Pin supports: Triangular symbols (fixed in x and y)
        - Roller supports: Circle symbols (fixed in y only, free in x)

        Args:
            fig: Existing Plotly Figure to add supports to.
            geometry: TrussGeometry object containing nodes.
            pin_nodes: List of node indices with pin supports.
            roller_nodes: List of node indices with roller supports.

        Returns:
            The modified Plotly Figure with support symbols added.

        Example:
            >>> geom = TrussGeometry()
            >>> geom.add_node(0, 0, "A")
            >>> geom.add_node(4, 0, "B")
            >>> geom.add_node(2, 3, "C")
            >>> geom.add_member(0, 1)
            >>> geom.add_member(0, 2)
            >>> geom.add_member(1, 2)
            >>> viz = TrussVisualization()
            >>> fig = viz.create_truss_diagram(geom)
            >>> fig = viz.add_supports(fig, geom, pin_nodes=[0], roller_nodes=[1])
        """
        theme = self._get_theme()

        # Calculate support symbol size based on geometry
        x_coords = [node.x for node in geometry.nodes]
        y_coords = [node.y for node in geometry.nodes]
        x_range = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 1.0
        y_range = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 1.0
        symbol_size = min(x_range, y_range) * 0.08

        # Draw pin supports (triangles)
        for node_idx in pin_nodes:
            node = geometry.nodes[node_idx]

            # Triangle vertices below the node
            triangle_x = [
                node.x,
                node.x - symbol_size / 2,
                node.x + symbol_size / 2,
                node.x,
            ]
            triangle_y = [
                node.y,
                node.y - symbol_size,
                node.y - symbol_size,
                node.y,
            ]

            fig.add_trace(
                go.Scatter(
                    x=triangle_x,
                    y=triangle_y,
                    mode="lines",
                    fill="toself",
                    fillcolor=theme["tertiary_color"],
                    line=dict(color=theme["tertiary_color"], width=2),
                    name=f"Pin Support ({node.name})",
                    hoverinfo="text",
                    hovertext=f"Pin Support at {node.name}<br>Fixed: x, y",
                    showlegend=False,
                )
            )

            # Ground line (hatching indication)
            ground_x = [node.x - symbol_size * 0.8, node.x + symbol_size * 0.8]
            ground_y = [node.y - symbol_size * 1.1, node.y - symbol_size * 1.1]

            fig.add_trace(
                go.Scatter(
                    x=ground_x,
                    y=ground_y,
                    mode="lines",
                    line=dict(color=theme["linecolor"], width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Draw roller supports (triangle with circle)
        for node_idx in roller_nodes:
            node = geometry.nodes[node_idx]

            # Triangle vertices below the node
            triangle_x = [
                node.x,
                node.x - symbol_size / 2,
                node.x + symbol_size / 2,
                node.x,
            ]
            triangle_y = [
                node.y,
                node.y - symbol_size * 0.7,
                node.y - symbol_size * 0.7,
                node.y,
            ]

            fig.add_trace(
                go.Scatter(
                    x=triangle_x,
                    y=triangle_y,
                    mode="lines",
                    fill="toself",
                    fillcolor=theme["accent_color"],
                    line=dict(color=theme["accent_color"], width=2),
                    name=f"Roller Support ({node.name})",
                    hoverinfo="text",
                    hovertext=f"Roller Support at {node.name}<br>Fixed: y<br>Free: x",
                    showlegend=False,
                )
            )

            # Draw roller circle
            circle_radius = symbol_size * 0.15
            circle_y_center = node.y - symbol_size * 0.7 - circle_radius * 1.5

            # Generate circle points
            theta = [2 * math.pi * i / 20 for i in range(21)]
            circle_x = [node.x + circle_radius * math.cos(t) for t in theta]
            circle_y = [circle_y_center + circle_radius * math.sin(t) for t in theta]

            fig.add_trace(
                go.Scatter(
                    x=circle_x,
                    y=circle_y,
                    mode="lines",
                    fill="toself",
                    fillcolor=theme["paper_bgcolor"],
                    line=dict(color=theme["accent_color"], width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

            # Ground line
            ground_x = [node.x - symbol_size * 0.8, node.x + symbol_size * 0.8]
            ground_y = [
                circle_y_center - circle_radius * 1.5,
                circle_y_center - circle_radius * 1.5,
            ]

            fig.add_trace(
                go.Scatter(
                    x=ground_x,
                    y=ground_y,
                    mode="lines",
                    line=dict(color=theme["linecolor"], width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        return fig

    def _draw_arrow(
        self,
        fig: go.Figure,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str,
        label: str,
    ) -> None:
        """
        Draw an arrow on the figure.

        Args:
            fig: Plotly Figure to draw on.
            start: Starting point (x, y) of the arrow.
            end: Ending point (x, y) of the arrow (arrow head location).
            color: Color of the arrow.
            label: Hover label for the arrow.
        """
        x1, y1 = start
        x2, y2 = end

        # Calculate arrow properties
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx ** 2 + dy ** 2)

        if length < 1e-10:
            return

        # Unit vector
        ux = dx / length
        uy = dy / length

        # Perpendicular vector for arrow head
        px = -uy
        py = ux

        # Arrow head size (proportional to length)
        head_size = min(length * 0.2, 0.15)

        # Arrow head points
        head_x1 = x2 - head_size * ux + head_size * 0.5 * px
        head_y1 = y2 - head_size * uy + head_size * 0.5 * py
        head_x2 = x2 - head_size * ux - head_size * 0.5 * px
        head_y2 = y2 - head_size * uy - head_size * 0.5 * py

        # Draw arrow line
        fig.add_trace(
            go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                line=dict(color=color, width=3),
                hoverinfo="text",
                hovertext=label,
                showlegend=False,
            )
        )

        # Draw arrow head
        fig.add_trace(
            go.Scatter(
                x=[head_x1, x2, head_x2],
                y=[head_y1, y2, head_y2],
                mode="lines",
                fill="toself",
                fillcolor=color,
                line=dict(color=color, width=2),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    def _get_force_color(self, force_value: float) -> str:
        """
        Get the color for a member based on its force value.

        Args:
            force_value: Force value in N. Positive = tension, negative = compression.

        Returns:
            Color string for the force visualization.
        """
        tolerance = 1e-6

        if force_value > tolerance:
            return TENSION_COLOR
        elif force_value < -tolerance:
            return COMPRESSION_COLOR
        else:
            return ZERO_FORCE_COLOR

    def _scale_line_width(
        self,
        force_value: float,
        max_force: float,
        min_width: float = 2.0,
        max_width: float = 10.0,
    ) -> float:
        """
        Scale line width based on force magnitude.

        Args:
            force_value: Force value in N.
            max_force: Maximum force magnitude for scaling reference.
            min_width: Minimum line width in pixels.
            max_width: Maximum line width in pixels.

        Returns:
            Scaled line width in pixels.
        """
        if max_force < 1e-10:
            return min_width

        # Linear scaling based on absolute force value
        ratio = abs(force_value) / max_force
        return min_width + ratio * (max_width - min_width)

    def _apply_layout(
        self,
        fig: go.Figure,
        title: str,
        geometry: TrussGeometry,
        show_legend: bool = False,
        extra_margin: float = 0.2,
    ) -> None:
        """
        Apply consistent layout styling to a figure.

        Args:
            fig: Plotly Figure to style.
            title: Title for the figure.
            geometry: TrussGeometry for determining axis ranges.
            show_legend: Whether to show the legend.
            extra_margin: Extra margin as fraction of range for axis limits.
        """
        theme = self._get_theme()

        # Calculate axis ranges with margin
        x_coords = [node.x for node in geometry.nodes]
        y_coords = [node.y for node in geometry.nodes]

        if x_coords and y_coords:
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            x_range = x_max - x_min if x_max > x_min else 1.0
            y_range = y_max - y_min if y_max > y_min else 1.0

            x_margin = x_range * extra_margin
            y_margin = y_range * extra_margin

            x_axis_range = [x_min - x_margin, x_max + x_margin]
            y_axis_range = [y_min - y_margin, y_max + y_margin]
        else:
            x_axis_range = [-1, 1]
            y_axis_range = [-1, 1]

        fig.update_layout(
            title=dict(text=title, font=dict(size=18)),
            xaxis=dict(
                title="x (m)",
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
                range=x_axis_range,
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                title="y (m)",
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
                range=y_axis_range,
            ),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height,
            showlegend=show_legend,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(255,255,255,0.8)" if not self.dark_mode else "rgba(0,0,0,0.5)",
            ),
            hovermode="closest",
        )


# Module exports
__all__ = [
    "TrussVisualization",
    "LIGHT_THEME",
    "DARK_THEME",
    "TENSION_COLOR",
    "COMPRESSION_COLOR",
    "ZERO_FORCE_COLOR",
    "REACTION_COLOR",
    "LOAD_COLOR",
]
