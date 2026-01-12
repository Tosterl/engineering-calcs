"""
Visualization service for Engineering Calculations Database.

This module provides chart and plotting functionality using Plotly for
creating interactive visualizations of engineering calculations. It supports
various chart types commonly used in engineering analysis including:
- Line charts for parametric studies
- Bar charts for value comparisons
- Scatter plots for data visualization
- Mohr's circle for stress analysis
- Shear and moment diagrams for beam analysis
- Bode plots for frequency response analysis

References:
    - Plotly Python Documentation: https://plotly.com/python/
    - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed.
    - Ogata, K., "Modern Control Engineering", 5th Ed.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Optional, Sequence, Union

import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


class ChartService:
    """
    Service class for creating engineering visualizations using Plotly.

    This class provides methods for creating various types of charts commonly
    used in engineering analysis. All charts follow a consistent styling scheme
    and can be exported to various image formats.

    Attributes:
        default_width: Default chart width in pixels.
        default_height: Default chart height in pixels.
        default_font_family: Font family for all text elements.

    Example:
        >>> service = ChartService()
        >>> fig = service.create_line_chart(
        ...     x_data=[0, 1, 2, 3, 4],
        ...     y_data=[0, 1, 4, 9, 16],
        ...     x_label="Time (s)",
        ...     y_label="Displacement (m)",
        ...     title="Position vs Time"
        ... )
        >>> fig.show()
    """

    def __init__(
        self,
        default_width: int = 800,
        default_height: int = 500,
        default_font_family: str = "Arial, sans-serif",
    ) -> None:
        """
        Initialize the ChartService.

        Args:
            default_width: Default chart width in pixels.
            default_height: Default chart height in pixels.
            default_font_family: Font family for all text elements.
        """
        self.default_width = default_width
        self.default_height = default_height
        self.default_font_family = default_font_family

    def create_line_chart(
        self,
        x_data: Sequence[float],
        y_data: Sequence[float],
        x_label: str,
        y_label: str,
        title: str,
        line_name: Optional[str] = None,
        show_markers: bool = True,
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a line chart for parametric studies.

        This method creates a line chart suitable for visualizing relationships
        between variables, commonly used in parametric studies and trend analysis.

        Args:
            x_data: Sequence of x-axis values.
            y_data: Sequence of y-axis values.
            x_label: Label for the x-axis.
            y_label: Label for the y-axis.
            title: Chart title.
            line_name: Name for the line trace (appears in legend).
            show_markers: Whether to show data point markers.
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the line chart.

        Example:
            >>> service = ChartService()
            >>> x = [0, 1, 2, 3, 4, 5]
            >>> y = [0, 2.5, 5, 7.5, 10, 12.5]
            >>> fig = service.create_line_chart(
            ...     x_data=x,
            ...     y_data=y,
            ...     x_label="Force (kN)",
            ...     y_label="Deflection (mm)",
            ...     title="Load-Deflection Curve"
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        mode = "lines+markers" if show_markers else "lines"

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=list(x_data),
                y=list(y_data),
                mode=mode,
                name=line_name or y_label,
                line=dict(color=theme["primary_color"], width=2),
                marker=dict(size=8, color=theme["primary_color"]),
            )
        )

        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(
                title=x_label,
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            yaxis=dict(
                title=y_label,
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height,
            showlegend=line_name is not None,
        )

        return self.apply_theme(fig, dark_mode)

    def create_bar_chart(
        self,
        categories: Sequence[str],
        values: Sequence[float],
        title: str,
        y_label: str,
        bar_colors: Optional[Sequence[str]] = None,
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a bar chart for comparing values.

        This method creates a bar chart suitable for comparing discrete values
        across different categories, such as stress comparisons or material
        property comparisons.

        Args:
            categories: Sequence of category names for the x-axis.
            values: Sequence of values corresponding to each category.
            title: Chart title.
            y_label: Label for the y-axis.
            bar_colors: Optional sequence of colors for each bar.
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the bar chart.

        Example:
            >>> service = ChartService()
            >>> categories = ["Steel", "Aluminum", "Titanium"]
            >>> values = [200, 70, 116]
            >>> fig = service.create_bar_chart(
            ...     categories=categories,
            ...     values=values,
            ...     title="Elastic Modulus Comparison",
            ...     y_label="E (GPa)"
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        if bar_colors is None:
            bar_colors = [theme["primary_color"]] * len(categories)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=list(categories),
                y=list(values),
                marker_color=list(bar_colors),
                text=[f"{v:.2f}" for v in values],
                textposition="auto",
            )
        )

        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(
                title="",
                showgrid=False,
                linecolor=theme["linecolor"],
            ),
            yaxis=dict(
                title=y_label,
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height,
        )

        return self.apply_theme(fig, dark_mode)

    def create_scatter_plot(
        self,
        x_data: Sequence[float],
        y_data: Sequence[float],
        x_label: str,
        y_label: str,
        title: str,
        point_labels: Optional[Sequence[str]] = None,
        marker_size: int = 10,
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a scatter plot for data visualization.

        This method creates a scatter plot suitable for visualizing relationships
        between two variables without implying a functional relationship.

        Args:
            x_data: Sequence of x-axis values.
            y_data: Sequence of y-axis values.
            x_label: Label for the x-axis.
            y_label: Label for the y-axis.
            title: Chart title.
            point_labels: Optional labels for each data point (hover text).
            marker_size: Size of the markers in pixels.
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the scatter plot.

        Example:
            >>> service = ChartService()
            >>> x = [1.2, 2.5, 3.1, 4.0, 5.2]
            >>> y = [2.3, 4.1, 5.8, 8.2, 10.1]
            >>> fig = service.create_scatter_plot(
            ...     x_data=x,
            ...     y_data=y,
            ...     x_label="Strain (%)",
            ...     y_label="Stress (MPa)",
            ...     title="Experimental Stress-Strain Data"
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=list(x_data),
                y=list(y_data),
                mode="markers",
                marker=dict(
                    size=marker_size,
                    color=theme["primary_color"],
                    line=dict(width=1, color=theme["linecolor"]),
                ),
                text=list(point_labels) if point_labels else None,
                hoverinfo="text+x+y" if point_labels else "x+y",
            )
        )

        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(
                title=x_label,
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            yaxis=dict(
                title=y_label,
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height,
        )

        return self.apply_theme(fig, dark_mode)

    def create_mohr_circle(
        self,
        sigma_x: float,
        sigma_y: float,
        tau_xy: float,
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a Mohr's circle diagram for stress analysis.

        This method creates a Mohr's circle visualization showing the state
        of stress at a point. The circle displays:
        - Normal stresses on the x-axis
        - Shear stresses on the y-axis
        - Principal stresses (sigma_1, sigma_2)
        - Maximum shear stress (tau_max)
        - Current stress state point

        The Mohr's circle equations:
            Center: C = (sigma_x + sigma_y) / 2
            Radius: R = sqrt(((sigma_x - sigma_y) / 2)^2 + tau_xy^2)
            Principal stresses: sigma_1,2 = C +/- R
            Maximum shear: tau_max = R

        Args:
            sigma_x: Normal stress in x-direction (same units throughout).
            sigma_y: Normal stress in y-direction.
            tau_xy: Shear stress on xy-plane.
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the Mohr's circle diagram.

        References:
            - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 7
            - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Ch. 9

        Example:
            >>> service = ChartService()
            >>> fig = service.create_mohr_circle(
            ...     sigma_x=80,  # MPa
            ...     sigma_y=-40,  # MPa
            ...     tau_xy=25,  # MPa
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        # Calculate Mohr's circle parameters
        center = (sigma_x + sigma_y) / 2
        radius = math.sqrt(((sigma_x - sigma_y) / 2) ** 2 + tau_xy ** 2)

        # Principal stresses
        sigma_1 = center + radius  # Maximum principal stress
        sigma_2 = center - radius  # Minimum principal stress

        # Maximum shear stress
        tau_max = radius

        # Calculate angle to principal plane (in radians)
        if sigma_x != sigma_y:
            theta_p = 0.5 * math.atan2(2 * tau_xy, sigma_x - sigma_y)
        else:
            theta_p = math.pi / 4 if tau_xy > 0 else -math.pi / 4

        # Generate circle points
        num_points = 100
        theta = [2 * math.pi * i / num_points for i in range(num_points + 1)]
        circle_x = [center + radius * math.cos(t) for t in theta]
        circle_y = [radius * math.sin(t) for t in theta]

        fig = go.Figure()

        # Draw the Mohr's circle
        fig.add_trace(
            go.Scatter(
                x=circle_x,
                y=circle_y,
                mode="lines",
                name="Mohr's Circle",
                line=dict(color=theme["primary_color"], width=2),
            )
        )

        # Draw horizontal axis through center
        axis_margin = radius * 0.3
        fig.add_trace(
            go.Scatter(
                x=[sigma_2 - axis_margin, sigma_1 + axis_margin],
                y=[0, 0],
                mode="lines",
                name="Normal Stress Axis",
                line=dict(color=theme["linecolor"], width=1, dash="dash"),
                showlegend=False,
            )
        )

        # Draw vertical axis through center
        fig.add_trace(
            go.Scatter(
                x=[center, center],
                y=[-tau_max - axis_margin, tau_max + axis_margin],
                mode="lines",
                name="Shear Stress Axis",
                line=dict(color=theme["linecolor"], width=1, dash="dash"),
                showlegend=False,
            )
        )

        # Mark the center
        fig.add_trace(
            go.Scatter(
                x=[center],
                y=[0],
                mode="markers+text",
                name=f"Center C = {center:.2f}",
                marker=dict(size=10, color=theme["accent_color"], symbol="cross"),
                text=[f"C ({center:.2f}, 0)"],
                textposition="bottom center",
            )
        )

        # Mark principal stresses (sigma_1, sigma_2)
        fig.add_trace(
            go.Scatter(
                x=[sigma_1, sigma_2],
                y=[0, 0],
                mode="markers+text",
                name="Principal Stresses",
                marker=dict(size=12, color=theme["secondary_color"], symbol="diamond"),
                text=[f"<b>sigma_1</b><br>{sigma_1:.2f}", f"<b>sigma_2</b><br>{sigma_2:.2f}"],
                textposition=["top right", "top left"],
            )
        )

        # Mark maximum shear stress points
        fig.add_trace(
            go.Scatter(
                x=[center, center],
                y=[tau_max, -tau_max],
                mode="markers+text",
                name=f"Max Shear = {tau_max:.2f}",
                marker=dict(size=12, color=theme["tertiary_color"], symbol="star"),
                text=[f"tau_max<br>{tau_max:.2f}", f"-tau_max<br>{-tau_max:.2f}"],
                textposition=["top center", "bottom center"],
            )
        )

        # Mark current stress state point (sigma_x, tau_xy)
        fig.add_trace(
            go.Scatter(
                x=[sigma_x],
                y=[tau_xy],
                mode="markers+text",
                name=f"Stress State ({sigma_x:.2f}, {tau_xy:.2f})",
                marker=dict(size=14, color=theme["primary_color"], symbol="circle"),
                text=[f"X-face<br>({sigma_x:.2f}, {tau_xy:.2f})"],
                textposition="top right",
            )
        )

        # Mark conjugate point (sigma_y, -tau_xy)
        fig.add_trace(
            go.Scatter(
                x=[sigma_y],
                y=[-tau_xy],
                mode="markers+text",
                name=f"Conjugate ({sigma_y:.2f}, {-tau_xy:.2f})",
                marker=dict(size=14, color=theme["primary_color"], symbol="circle-open"),
                text=[f"Y-face<br>({sigma_y:.2f}, {-tau_xy:.2f})"],
                textposition="bottom left",
            )
        )

        # Draw line connecting stress state points (diameter)
        fig.add_trace(
            go.Scatter(
                x=[sigma_x, sigma_y],
                y=[tau_xy, -tau_xy],
                mode="lines",
                name="Diameter",
                line=dict(color=theme["primary_color"], width=1, dash="dot"),
                showlegend=False,
            )
        )

        # Add annotations for principal angle
        theta_p_deg = math.degrees(theta_p)

        fig.update_layout(
            title=dict(
                text=(
                    f"Mohr's Circle<br>"
                    f"<sup>sigma_1 = {sigma_1:.2f}, sigma_2 = {sigma_2:.2f}, "
                    f"tau_max = {tau_max:.2f}, theta_p = {theta_p_deg:.1f} deg</sup>"
                ),
                font=dict(size=16),
            ),
            xaxis=dict(
                title="Normal Stress (sigma)",
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                title="Shear Stress (tau)",
                showgrid=True,
                gridcolor=theme["gridcolor"],
                linecolor=theme["linecolor"],
                zeroline=True,
                zerolinecolor=theme["linecolor"],
            ),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_width,  # Square aspect ratio
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(255,255,255,0.8)" if not dark_mode else "rgba(0,0,0,0.5)",
            ),
        )

        return self.apply_theme(fig, dark_mode)

    def create_shear_moment_diagram(
        self,
        positions: Sequence[float],
        shear_values: Sequence[float],
        moment_values: Sequence[float],
        beam_length: float,
        position_unit: str = "m",
        shear_unit: str = "kN",
        moment_unit: str = "kN-m",
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a shear and moment diagram for beam analysis.

        This method creates a dual-subplot figure with:
        - Top subplot: Shear force diagram (V)
        - Bottom subplot: Bending moment diagram (M)

        Both diagrams include zero reference lines and are aligned for
        easy interpretation.

        Args:
            positions: Sequence of positions along the beam.
            shear_values: Sequence of shear force values at each position.
            moment_values: Sequence of bending moment values at each position.
            beam_length: Total length of the beam.
            position_unit: Unit for position (default: "m").
            shear_unit: Unit for shear force (default: "kN").
            moment_unit: Unit for bending moment (default: "kN-m").
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the shear and moment diagrams.

        References:
            - Hibbeler, R.C., "Mechanics of Materials", 10th Ed., Ch. 6
            - Beer, F.P., Johnston, E.R., "Mechanics of Materials", 7th Ed., Ch. 5

        Example:
            >>> service = ChartService()
            >>> # Simply supported beam with point load at center
            >>> positions = [0, 2.5, 2.5, 5]
            >>> shear = [25, 25, -25, -25]  # kN
            >>> moment = [0, 62.5, 62.5, 0]  # kN-m
            >>> fig = service.create_shear_moment_diagram(
            ...     positions=positions,
            ...     shear_values=shear,
            ...     moment_values=moment,
            ...     beam_length=5.0
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        # Create subplot figure with shared x-axis
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            subplot_titles=("Shear Force Diagram (V)", "Bending Moment Diagram (M)"),
        )

        # Shear force diagram (top)
        fig.add_trace(
            go.Scatter(
                x=list(positions),
                y=list(shear_values),
                mode="lines",
                name="Shear Force",
                line=dict(color=theme["primary_color"], width=2),
                fill="tozeroy",
                fillcolor=f"rgba({int(theme['primary_color'][1:3], 16)}, "
                f"{int(theme['primary_color'][3:5], 16)}, "
                f"{int(theme['primary_color'][5:7], 16)}, 0.3)",
            ),
            row=1,
            col=1,
        )

        # Zero line for shear diagram
        fig.add_trace(
            go.Scatter(
                x=[0, beam_length],
                y=[0, 0],
                mode="lines",
                name="Zero (V)",
                line=dict(color=theme["linecolor"], width=1, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Bending moment diagram (bottom)
        fig.add_trace(
            go.Scatter(
                x=list(positions),
                y=list(moment_values),
                mode="lines",
                name="Bending Moment",
                line=dict(color=theme["secondary_color"], width=2),
                fill="tozeroy",
                fillcolor=f"rgba({int(theme['secondary_color'][1:3], 16)}, "
                f"{int(theme['secondary_color'][3:5], 16)}, "
                f"{int(theme['secondary_color'][5:7], 16)}, 0.3)",
            ),
            row=2,
            col=1,
        )

        # Zero line for moment diagram
        fig.add_trace(
            go.Scatter(
                x=[0, beam_length],
                y=[0, 0],
                mode="lines",
                name="Zero (M)",
                line=dict(color=theme["linecolor"], width=1, dash="dash"),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Find max values for annotations
        max_shear = max(abs(v) for v in shear_values)
        max_moment = max(abs(v) for v in moment_values)
        max_shear_idx = next(i for i, v in enumerate(shear_values) if abs(v) == max_shear)
        max_moment_idx = next(i for i, v in enumerate(moment_values) if abs(v) == max_moment)

        # Add annotation for max shear
        fig.add_annotation(
            x=positions[max_shear_idx],
            y=shear_values[max_shear_idx],
            text=f"V_max = {shear_values[max_shear_idx]:.2f} {shear_unit}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=theme["primary_color"],
            row=1,
            col=1,
        )

        # Add annotation for max moment
        fig.add_annotation(
            x=positions[max_moment_idx],
            y=moment_values[max_moment_idx],
            text=f"M_max = {moment_values[max_moment_idx]:.2f} {moment_unit}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=theme["secondary_color"],
            row=2,
            col=1,
        )

        # Update layout
        fig.update_layout(
            title=dict(text="Shear and Moment Diagrams", font=dict(size=16)),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height + 200,  # Taller for two subplots
            showlegend=True,
            legend=dict(x=0.02, y=0.98),
        )

        # Update axes
        fig.update_xaxes(
            title_text=f"Position ({position_unit})",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=2,
            col=1,
        )

        fig.update_yaxes(
            title_text=f"V ({shear_unit})",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=1,
            col=1,
        )

        fig.update_yaxes(
            title_text=f"M ({moment_unit})",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=2,
            col=1,
        )

        # Update subplot title colors
        for annotation in fig.layout.annotations:
            annotation.font.color = theme["font_color"]

        return self.apply_theme(fig, dark_mode)

    def create_bode_plot(
        self,
        frequencies: Sequence[float],
        magnitudes: Sequence[float],
        phases: Sequence[float],
        frequency_unit: str = "rad/s",
        dark_mode: bool = False,
    ) -> go.Figure:
        """
        Create a Bode plot for frequency response analysis.

        This method creates a dual-subplot figure with:
        - Top subplot: Magnitude plot (dB) vs frequency (log scale)
        - Bottom subplot: Phase plot (degrees) vs frequency (log scale)

        The Bode plot is essential for analyzing system stability and
        frequency response characteristics in control systems.

        Args:
            frequencies: Sequence of frequency values.
            magnitudes: Sequence of magnitude values in decibels (dB).
            phases: Sequence of phase values in degrees.
            frequency_unit: Unit for frequency (default: "rad/s").
            dark_mode: Whether to use dark theme.

        Returns:
            A Plotly Figure object containing the Bode plot.

        References:
            - Ogata, K., "Modern Control Engineering", 5th Ed., Ch. 8
            - Franklin, G.F., "Feedback Control of Dynamic Systems", 7th Ed., Ch. 6

        Example:
            >>> service = ChartService()
            >>> import numpy as np
            >>> # First-order system: G(s) = 1/(s+1)
            >>> freq = np.logspace(-2, 2, 100)
            >>> mag = -20 * np.log10(np.sqrt(1 + freq**2))  # dB
            >>> phase = -np.degrees(np.arctan(freq))  # degrees
            >>> fig = service.create_bode_plot(
            ...     frequencies=freq,
            ...     magnitudes=mag,
            ...     phases=phase
            ... )
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        # Create subplot figure with shared x-axis (log scale)
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            subplot_titles=("Magnitude", "Phase"),
        )

        # Magnitude plot (top)
        fig.add_trace(
            go.Scatter(
                x=list(frequencies),
                y=list(magnitudes),
                mode="lines",
                name="Magnitude",
                line=dict(color=theme["primary_color"], width=2),
            ),
            row=1,
            col=1,
        )

        # 0 dB reference line
        fig.add_trace(
            go.Scatter(
                x=[min(frequencies), max(frequencies)],
                y=[0, 0],
                mode="lines",
                name="0 dB",
                line=dict(color=theme["linecolor"], width=1, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Phase plot (bottom)
        fig.add_trace(
            go.Scatter(
                x=list(frequencies),
                y=list(phases),
                mode="lines",
                name="Phase",
                line=dict(color=theme["secondary_color"], width=2),
            ),
            row=2,
            col=1,
        )

        # -180 degree reference line (phase crossover)
        fig.add_trace(
            go.Scatter(
                x=[min(frequencies), max(frequencies)],
                y=[-180, -180],
                mode="lines",
                name="-180 deg",
                line=dict(color=theme["tertiary_color"], width=1, dash="dash"),
                showlegend=True,
            ),
            row=2,
            col=1,
        )

        # -90 degree reference line
        fig.add_trace(
            go.Scatter(
                x=[min(frequencies), max(frequencies)],
                y=[-90, -90],
                mode="lines",
                name="-90 deg",
                line=dict(color=theme["linecolor"], width=1, dash="dot"),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Find gain crossover frequency (where magnitude = 0 dB)
        gain_crossover_freq = None
        for i in range(len(magnitudes) - 1):
            if (magnitudes[i] >= 0 and magnitudes[i + 1] < 0) or (
                magnitudes[i] <= 0 and magnitudes[i + 1] > 0
            ):
                # Linear interpolation to find crossover
                gain_crossover_freq = frequencies[i] + (
                    frequencies[i + 1] - frequencies[i]
                ) * abs(magnitudes[i]) / abs(magnitudes[i + 1] - magnitudes[i])
                break

        # Find phase crossover frequency (where phase = -180 deg)
        phase_crossover_freq = None
        for i in range(len(phases) - 1):
            if (phases[i] >= -180 and phases[i + 1] < -180) or (
                phases[i] <= -180 and phases[i + 1] > -180
            ):
                # Linear interpolation to find crossover
                phase_crossover_freq = frequencies[i] + (
                    frequencies[i + 1] - frequencies[i]
                ) * abs(phases[i] + 180) / abs(phases[i + 1] - phases[i])
                break

        # Add marker for gain crossover if found
        if gain_crossover_freq is not None:
            # Interpolate phase at gain crossover
            phase_at_gc = None
            for i in range(len(frequencies) - 1):
                if frequencies[i] <= gain_crossover_freq <= frequencies[i + 1]:
                    t = (gain_crossover_freq - frequencies[i]) / (
                        frequencies[i + 1] - frequencies[i]
                    )
                    phase_at_gc = phases[i] + t * (phases[i + 1] - phases[i])
                    break

            fig.add_trace(
                go.Scatter(
                    x=[gain_crossover_freq],
                    y=[0],
                    mode="markers",
                    name=f"Gain Crossover",
                    marker=dict(size=12, color=theme["accent_color"], symbol="diamond"),
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

            if phase_at_gc is not None:
                fig.add_annotation(
                    x=math.log10(gain_crossover_freq),
                    y=0,
                    text=f"w_gc = {gain_crossover_freq:.2f}<br>PM = {180 + phase_at_gc:.1f} deg",
                    showarrow=True,
                    arrowhead=2,
                    xref="x",
                    yref="y",
                    row=1,
                    col=1,
                )

        # Update layout
        fig.update_layout(
            title=dict(text="Bode Plot", font=dict(size=16)),
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
            width=self.default_width,
            height=self.default_height + 200,  # Taller for two subplots
            showlegend=True,
            legend=dict(x=0.02, y=0.98),
        )

        # Update x-axes to log scale
        fig.update_xaxes(
            type="log",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=1,
            col=1,
        )

        fig.update_xaxes(
            title_text=f"Frequency ({frequency_unit})",
            type="log",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=2,
            col=1,
        )

        # Update y-axes
        fig.update_yaxes(
            title_text="Magnitude (dB)",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=1,
            col=1,
        )

        fig.update_yaxes(
            title_text="Phase (deg)",
            showgrid=True,
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
            row=2,
            col=1,
        )

        # Update subplot title colors
        for annotation in fig.layout.annotations:
            annotation.font.color = theme["font_color"]

        return self.apply_theme(fig, dark_mode)

    def apply_theme(self, fig: go.Figure, dark_mode: bool = False) -> go.Figure:
        """
        Apply consistent theme styling to a figure.

        This method applies the selected theme (light or dark) to an existing
        figure, ensuring consistent appearance across all charts.

        Args:
            fig: The Plotly Figure to style.
            dark_mode: Whether to use dark theme.

        Returns:
            The styled Plotly Figure.

        Example:
            >>> service = ChartService()
            >>> fig = go.Figure()
            >>> fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
            >>> styled_fig = service.apply_theme(fig, dark_mode=True)
        """
        theme = DARK_THEME if dark_mode else LIGHT_THEME

        fig.update_layout(
            font=dict(family=self.default_font_family, color=theme["font_color"]),
            paper_bgcolor=theme["paper_bgcolor"],
            plot_bgcolor=theme["plot_bgcolor"],
        )

        # Update all x and y axes
        fig.update_xaxes(
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
        )

        fig.update_yaxes(
            gridcolor=theme["gridcolor"],
            linecolor=theme["linecolor"],
        )

        return fig

    def export_to_image(
        self,
        fig: go.Figure,
        path: Union[str, Path],
        format: str = "png",
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: float = 2.0,
    ) -> None:
        """
        Export a figure to an image file.

        This method exports a Plotly figure to various image formats including
        PNG, JPEG, SVG, PDF, and WebP. The export uses the kaleido engine for
        high-quality static image generation.

        Args:
            fig: The Plotly Figure to export.
            path: File path for the exported image.
            format: Image format ("png", "jpeg", "svg", "pdf", "webp").
            width: Image width in pixels (uses figure width if not specified).
            height: Image height in pixels (uses figure height if not specified).
            scale: Scale factor for resolution (default: 2.0 for high DPI).

        Raises:
            ValueError: If an unsupported format is specified.
            ImportError: If kaleido is not installed.

        Example:
            >>> service = ChartService()
            >>> fig = service.create_line_chart(
            ...     x_data=[1, 2, 3],
            ...     y_data=[1, 4, 9],
            ...     x_label="X",
            ...     y_label="Y",
            ...     title="Example"
            ... )
            >>> service.export_to_image(fig, "chart.png")
        """
        valid_formats = {"png", "jpeg", "jpg", "svg", "pdf", "webp"}
        format_lower = format.lower()

        if format_lower not in valid_formats:
            raise ValueError(
                f"Unsupported format '{format}'. Supported formats: {valid_formats}"
            )

        # Normalize jpg to jpeg
        if format_lower == "jpg":
            format_lower = "jpeg"

        path = Path(path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Use figure dimensions if not specified
        export_width = width or self.default_width
        export_height = height or self.default_height

        fig.write_image(
            str(path),
            format=format_lower,
            width=export_width,
            height=export_height,
            scale=scale,
        )


# Module exports
__all__ = [
    "ChartService",
    "LIGHT_THEME",
    "DARK_THEME",
]
