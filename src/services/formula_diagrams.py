"""
Formula diagrams and visual aids service.

Provides SVG diagrams and examples for engineering calculations.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
from dataclasses import dataclass


@dataclass
class FormulaExample:
    """An example calculation with inputs and expected outputs."""
    description: str
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    notes: str = ""


@dataclass
class FormulaDiagram:
    """Diagram and examples for a formula."""
    svg_diagram: str  # SVG markup
    description: str
    variables: Dict[str, str]  # variable name -> description
    examples: List[FormulaExample]


class FormulaDiagramService:
    """Service providing visual aids for engineering formulas."""

    @staticmethod
    def get_axial_stress_diagram() -> FormulaDiagram:
        """Axial stress diagram: σ = F/A"""
        svg = '''
        <svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Bar -->
            <rect x="50" y="70" width="200" height="60" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

            <!-- Force arrows -->
            <line x1="10" y1="100" x2="50" y2="100" stroke="#d32f2f" stroke-width="3" marker-end="url(#arrowhead)"/>
            <line x1="290" y1="100" x2="250" y2="100" stroke="#d32f2f" stroke-width="3" marker-end="url(#arrowhead)"/>

            <!-- Labels -->
            <text x="20" y="85" font-size="14" fill="#d32f2f" font-weight="bold">F</text>
            <text x="270" y="85" font-size="14" fill="#d32f2f" font-weight="bold">F</text>
            <text x="140" y="105" font-size="14" fill="#1976d2" font-weight="bold">A</text>

            <!-- Cross-section indicator -->
            <line x1="150" y1="65" x2="150" y2="135" stroke="#666" stroke-width="1" stroke-dasharray="5,5"/>
            <text x="155" y="150" font-size="12" fill="#666">Cross-section</text>

            <!-- Formula -->
            <text x="300" y="90" font-size="16" fill="#333" font-weight="bold">σ = F/A</text>
            <text x="300" y="115" font-size="12" fill="#666">Axial Stress</text>

            <!-- Arrow marker definition -->
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#d32f2f"/>
                </marker>
            </defs>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="Axial stress occurs when a force is applied perpendicular to a cross-section.",
            variables={
                "σ": "Axial stress (Pa or psi)",
                "F": "Applied force (N or lbf)",
                "A": "Cross-sectional area (m² or in²)"
            },
            examples=[
                FormulaExample(
                    description="Steel rod under tension",
                    inputs={"force": "50000 N", "area": "0.001 m²"},
                    expected_outputs={"stress": "50 MPa"},
                    notes="Typical for a 35mm diameter steel rod"
                ),
                FormulaExample(
                    description="Concrete column",
                    inputs={"force": "500000 N", "area": "0.09 m²"},
                    expected_outputs={"stress": "5.56 MPa"},
                    notes="300mm x 300mm column"
                )
            ]
        )

    @staticmethod
    def get_bending_moment_diagram() -> FormulaDiagram:
        """Simply supported beam with uniform load."""
        svg = '''
        <svg viewBox="0 0 450 220" width="450" height="220" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Beam -->
            <rect x="50" y="80" width="300" height="20" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

            <!-- Distributed load arrows -->
            <g fill="#d32f2f">
                <line x1="70" y1="30" x2="70" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="110" y1="30" x2="110" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="150" y1="30" x2="150" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="190" y1="30" x2="190" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="230" y1="30" x2="230" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="270" y1="30" x2="270" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="310" y1="30" x2="310" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <line x1="330" y1="30" x2="330" y2="80" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead2)"/>
                <rect x="60" y="20" width="280" height="10" fill="#ffcdd2"/>
            </g>
            <text x="180" y="15" font-size="12" fill="#d32f2f" font-weight="bold">w (N/m)</text>

            <!-- Pin support (left) -->
            <polygon points="50,100 40,120 60,120" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
            <line x1="35" y1="125" x2="65" y2="125" stroke="#2e7d32" stroke-width="2"/>

            <!-- Roller support (right) -->
            <polygon points="350,100 340,115 360,115" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
            <circle cx="350" cy="120" r="5" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
            <line x1="335" y1="128" x2="365" y2="128" stroke="#2e7d32" stroke-width="2"/>

            <!-- Span dimension -->
            <line x1="50" y1="145" x2="350" y2="145" stroke="#666" stroke-width="1"/>
            <line x1="50" y1="140" x2="50" y2="150" stroke="#666" stroke-width="1"/>
            <line x1="350" y1="140" x2="350" y2="150" stroke="#666" stroke-width="1"/>
            <text x="190" y="160" font-size="12" fill="#666">L (span)</text>

            <!-- Moment diagram (parabola) -->
            <path d="M 50 200 Q 200 170 350 200" fill="none" stroke="#9c27b0" stroke-width="2"/>
            <text x="180" y="180" font-size="12" fill="#9c27b0">M_max = wL²/8</text>

            <!-- Formula box -->
            <rect x="370" y="60" width="75" height="60" fill="#fff" stroke="#ccc" stroke-width="1"/>
            <text x="380" y="85" font-size="14" fill="#333" font-weight="bold">M = wL²/8</text>
            <text x="380" y="105" font-size="10" fill="#666">at midspan</text>

            <!-- Arrow marker -->
            <defs>
                <marker id="arrowhead2" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#d32f2f"/>
                </marker>
            </defs>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="Maximum bending moment for a simply supported beam with uniformly distributed load.",
            variables={
                "M": "Maximum bending moment (N·m)",
                "w": "Distributed load (N/m)",
                "L": "Span length (m)"
            },
            examples=[
                FormulaExample(
                    description="Floor beam with uniform load",
                    inputs={"distributed_load": "5000 N/m", "span_length": "6 m"},
                    expected_outputs={"max_moment": "22500 N·m"},
                    notes="Typical residential floor beam"
                ),
                FormulaExample(
                    description="Bridge deck beam",
                    inputs={"distributed_load": "20000 N/m", "span_length": "10 m"},
                    expected_outputs={"max_moment": "250000 N·m"},
                    notes="Highway bridge beam section"
                )
            ]
        )

    @staticmethod
    def get_pipe_flow_diagram() -> FormulaDiagram:
        """Pipe flow with Reynolds number."""
        svg = '''
        <svg viewBox="0 0 450 180" width="450" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Pipe outline -->
            <rect x="30" y="50" width="300" height="80" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="5"/>
            <rect x="40" y="60" width="280" height="60" fill="#bbdefb" stroke="none"/>

            <!-- Flow arrows -->
            <g fill="#1565c0">
                <path d="M 60 90 L 90 90 L 85 80 M 90 90 L 85 100" stroke="#1565c0" stroke-width="2" fill="none"/>
                <path d="M 130 90 L 160 90 L 155 80 M 160 90 L 155 100" stroke="#1565c0" stroke-width="2" fill="none"/>
                <path d="M 200 90 L 230 90 L 225 80 M 230 90 L 225 100" stroke="#1565c0" stroke-width="2" fill="none"/>
                <path d="M 270 90 L 300 90 L 295 80 M 300 90 L 295 100" stroke="#1565c0" stroke-width="2" fill="none"/>
            </g>
            <text x="170" y="95" font-size="14" fill="#0d47a1" font-weight="bold">V</text>

            <!-- Diameter indicator -->
            <line x1="345" y1="50" x2="345" y2="130" stroke="#666" stroke-width="1"/>
            <line x1="340" y1="50" x2="350" y2="50" stroke="#666" stroke-width="1"/>
            <line x1="340" y1="130" x2="350" y2="130" stroke="#666" stroke-width="1"/>
            <text x="355" y="95" font-size="12" fill="#666">D</text>

            <!-- Flow regime indicator -->
            <text x="30" y="160" font-size="11" fill="#666">Re &lt; 2300: Laminar</text>
            <text x="150" y="160" font-size="11" fill="#666">2300 &lt; Re &lt; 4000: Transition</text>
            <text x="310" y="160" font-size="11" fill="#666">Re &gt; 4000: Turbulent</text>

            <!-- Formula box -->
            <rect x="350" y="40" width="95" height="70" fill="#fff" stroke="#ccc" stroke-width="1"/>
            <text x="360" y="60" font-size="12" fill="#333" font-weight="bold">Re = ρVD/μ</text>
            <text x="360" y="80" font-size="10" fill="#666">ρ = density</text>
            <text x="360" y="95" font-size="10" fill="#666">μ = viscosity</text>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="Reynolds number determines flow regime in pipes and ducts.",
            variables={
                "Re": "Reynolds number (dimensionless)",
                "ρ": "Fluid density (kg/m³)",
                "V": "Flow velocity (m/s)",
                "D": "Pipe diameter (m)",
                "μ": "Dynamic viscosity (Pa·s)"
            },
            examples=[
                FormulaExample(
                    description="Water in household pipe",
                    inputs={"density": "1000 kg/m³", "velocity": "1.5 m/s", "diameter": "0.02 m", "viscosity": "0.001 Pa·s"},
                    expected_outputs={"reynolds_number": "30000", "flow_regime": "Turbulent"},
                    notes="Typical 3/4 inch copper pipe"
                ),
                FormulaExample(
                    description="Oil in industrial pipe",
                    inputs={"density": "900 kg/m³", "velocity": "0.5 m/s", "diameter": "0.1 m", "viscosity": "0.1 Pa·s"},
                    expected_outputs={"reynolds_number": "450", "flow_regime": "Laminar"},
                    notes="Heavy oil in process piping"
                )
            ]
        )

    @staticmethod
    def get_truss_diagram() -> FormulaDiagram:
        """Simple truss structure."""
        svg = '''
        <svg viewBox="0 0 450 200" width="450" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Truss members -->
            <g stroke="#1976d2" stroke-width="3" fill="none">
                <!-- Bottom chord -->
                <line x1="50" y1="150" x2="200" y2="150"/>
                <line x1="200" y1="150" x2="350" y2="150"/>

                <!-- Top chord / diagonals -->
                <line x1="50" y1="150" x2="200" y2="50"/>
                <line x1="200" y1="50" x2="350" y2="150"/>

                <!-- Vertical -->
                <line x1="200" y1="50" x2="200" y2="150"/>
            </g>

            <!-- Nodes -->
            <g fill="#1976d2">
                <circle cx="50" cy="150" r="6"/>
                <circle cx="200" cy="150" r="6"/>
                <circle cx="350" cy="150" r="6"/>
                <circle cx="200" cy="50" r="6"/>
            </g>

            <!-- Node labels -->
            <text x="40" y="175" font-size="12" fill="#333">A</text>
            <text x="195" y="175" font-size="12" fill="#333">B</text>
            <text x="355" y="155" font-size="12" fill="#333">C</text>
            <text x="205" y="45" font-size="12" fill="#333">D</text>

            <!-- Applied load -->
            <line x1="200" y1="10" x2="200" y2="45" stroke="#d32f2f" stroke-width="2" marker-end="url(#arrowhead3)"/>
            <text x="210" y="25" font-size="12" fill="#d32f2f" font-weight="bold">P</text>

            <!-- Supports -->
            <polygon points="50,150 40,170 60,170" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
            <polygon points="350,150 340,165 360,165" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
            <circle cx="350" cy="168" r="4" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>

            <!-- Member force labels -->
            <text x="100" y="95" font-size="10" fill="#d32f2f">T (tension)</text>
            <text x="260" y="95" font-size="10" fill="#d32f2f">T (tension)</text>
            <text x="100" y="145" font-size="10" fill="#0d47a1">C (compression)</text>
            <text x="260" y="145" font-size="10" fill="#0d47a1">C (compression)</text>
            <text x="205" y="105" font-size="10" fill="#d32f2f">T</text>

            <!-- Arrow marker -->
            <defs>
                <marker id="arrowhead3" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#d32f2f"/>
                </marker>
            </defs>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="Simple triangular truss showing tension (T) and compression (C) members.",
            variables={
                "P": "Applied load at joint (N)",
                "T": "Tension force in member (N)",
                "C": "Compression force in member (N)"
            },
            examples=[
                FormulaExample(
                    description="Roof truss under point load",
                    inputs={"load": "10000 N", "span": "6 m", "height": "2 m"},
                    expected_outputs={"diagonal_force": "7906 N (tension)", "bottom_chord": "7500 N (compression)"},
                    notes="Use method of joints at each node"
                )
            ]
        )

    @staticmethod
    def get_fatigue_sn_diagram() -> FormulaDiagram:
        """S-N curve for fatigue analysis."""
        svg = '''
        <svg viewBox="0 0 450 220" width="450" height="220" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Axes -->
            <line x1="60" y1="180" x2="400" y2="180" stroke="#333" stroke-width="2"/>
            <line x1="60" y1="180" x2="60" y2="30" stroke="#333" stroke-width="2"/>

            <!-- Axis labels -->
            <text x="220" y="210" font-size="12" fill="#333">Log(N) - Cycles to Failure</text>
            <text x="20" y="110" font-size="12" fill="#333" transform="rotate(-90, 20, 110)">Stress Amplitude (σa)</text>

            <!-- S-N curve -->
            <path d="M 80 50 Q 150 70 200 100 Q 280 140 380 160" fill="none" stroke="#1976d2" stroke-width="3"/>

            <!-- Endurance limit line -->
            <line x1="280" y1="160" x2="400" y2="160" stroke="#4caf50" stroke-width="2" stroke-dasharray="5,5"/>
            <text x="310" y="155" font-size="10" fill="#4caf50">Endurance Limit (Se)</text>

            <!-- Key points -->
            <circle cx="80" cy="50" r="4" fill="#d32f2f"/>
            <text x="85" y="45" font-size="10" fill="#d32f2f">Sut</text>

            <circle cx="200" cy="100" r="4" fill="#ff9800"/>
            <text x="205" y="95" font-size="10" fill="#ff9800">10³ cycles</text>

            <circle cx="280" cy="140" r="4" fill="#4caf50"/>
            <text x="250" y="135" font-size="10" fill="#4caf50">10⁶ cycles</text>

            <!-- Formula box -->
            <rect x="300" y="40" width="140" height="50" fill="#fff" stroke="#ccc" stroke-width="1"/>
            <text x="310" y="60" font-size="11" fill="#333" font-weight="bold">N = (σa/a)^(-1/b)</text>
            <text x="310" y="80" font-size="10" fill="#666">Basquin Equation</text>

            <!-- Grid lines -->
            <g stroke="#eee" stroke-width="1">
                <line x1="140" y1="180" x2="140" y2="30"/>
                <line x1="220" y1="180" x2="220" y2="30"/>
                <line x1="300" y1="180" x2="300" y2="30"/>
                <line x1="60" y1="130" x2="400" y2="130"/>
                <line x1="60" y1="80" x2="400" y2="80"/>
            </g>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="S-N curve (Wöhler curve) shows relationship between stress amplitude and fatigue life.",
            variables={
                "N": "Number of cycles to failure",
                "σa": "Stress amplitude (Pa)",
                "a": "Fatigue strength coefficient",
                "b": "Fatigue strength exponent (typically -0.05 to -0.12)",
                "Se": "Endurance limit (stress below which infinite life)"
            },
            examples=[
                FormulaExample(
                    description="Steel shaft under cyclic loading",
                    inputs={"stress_amplitude": "200 MPa", "fatigue_coefficient": "1000 MPa", "fatigue_exponent": "-0.1"},
                    expected_outputs={"cycles_to_failure": "~100,000 cycles"},
                    notes="For AISI 1045 steel"
                )
            ]
        )

    @staticmethod
    def get_cross_section_i_beam_diagram() -> FormulaDiagram:
        """I-beam cross section."""
        svg = '''
        <svg viewBox="0 0 350 250" width="350" height="250" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- I-beam cross section -->
            <g transform="translate(50, 20)">
                <!-- Top flange -->
                <rect x="0" y="0" width="150" height="20" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

                <!-- Web -->
                <rect x="60" y="20" width="30" height="120" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

                <!-- Bottom flange -->
                <rect x="0" y="140" width="150" height="20" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            </g>

            <!-- Dimension lines -->
            <!-- Width (bf) -->
            <line x1="50" y1="195" x2="200" y2="195" stroke="#666" stroke-width="1"/>
            <line x1="50" y1="190" x2="50" y2="200" stroke="#666" stroke-width="1"/>
            <line x1="200" y1="190" x2="200" y2="200" stroke="#666" stroke-width="1"/>
            <text x="115" y="210" font-size="11" fill="#666">bf</text>

            <!-- Height (d) -->
            <line x1="220" y1="20" x2="220" y2="180" stroke="#666" stroke-width="1"/>
            <line x1="215" y1="20" x2="225" y2="20" stroke="#666" stroke-width="1"/>
            <line x1="215" y1="180" x2="225" y2="180" stroke="#666" stroke-width="1"/>
            <text x="230" y="105" font-size="11" fill="#666">d</text>

            <!-- Flange thickness (tf) -->
            <line x1="205" y1="20" x2="205" y2="40" stroke="#d32f2f" stroke-width="1"/>
            <text x="208" y="35" font-size="10" fill="#d32f2f">tf</text>

            <!-- Web thickness (tw) -->
            <line x1="110" y1="85" x2="140" y2="85" stroke="#d32f2f" stroke-width="1"/>
            <text x="145" y="90" font-size="10" fill="#d32f2f">tw</text>

            <!-- Centroid -->
            <circle cx="125" cy="100" r="3" fill="#4caf50"/>
            <text x="130" y="105" font-size="10" fill="#4caf50">C</text>

            <!-- Neutral axis -->
            <line x1="40" y1="100" x2="210" y2="100" stroke="#4caf50" stroke-width="1" stroke-dasharray="5,3"/>

            <!-- Formulas -->
            <text x="250" y="40" font-size="11" fill="#333" font-weight="bold">Key Properties:</text>
            <text x="250" y="60" font-size="10" fill="#666">A = 2·bf·tf + d·tw</text>
            <text x="250" y="80" font-size="10" fill="#666">Ix = (bf·d³)/12 - ...</text>
            <text x="250" y="100" font-size="10" fill="#666">Sx = Ix / (d/2)</text>
            <text x="250" y="120" font-size="10" fill="#666">rx = √(Ix/A)</text>
        </svg>
        '''

        return FormulaDiagram(
            svg_diagram=svg,
            description="I-beam (wide flange) cross-section showing key dimensions for calculating section properties.",
            variables={
                "d": "Total depth (m)",
                "bf": "Flange width (m)",
                "tf": "Flange thickness (m)",
                "tw": "Web thickness (m)",
                "A": "Cross-sectional area (m²)",
                "Ix": "Moment of inertia about x-axis (m⁴)",
                "Sx": "Section modulus (m³)"
            },
            examples=[
                FormulaExample(
                    description="W12x26 Steel beam",
                    inputs={"total_height": "0.310 m", "flange_width": "0.165 m", "flange_thickness": "0.0095 m", "web_thickness": "0.0058 m"},
                    expected_outputs={"area": "0.00494 m²", "Ix": "8.49e-5 m⁴"},
                    notes="Common structural steel section"
                )
            ]
        )

    @staticmethod
    def get_shear_stress_diagram() -> FormulaDiagram:
        """Shear stress diagram."""
        svg = '''
        <svg viewBox="0 0 400 180" width="400" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Block -->
            <rect x="100" y="50" width="150" height="80" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

            <!-- Shear force arrows -->
            <line x1="100" y1="30" x2="250" y2="30" stroke="#d32f2f" stroke-width="2"/>
            <polygon points="250,30 240,25 240,35" fill="#d32f2f"/>
            <text x="170" y="22" font-size="12" fill="#d32f2f" font-weight="bold">V</text>

            <line x1="250" y1="150" x2="100" y2="150" stroke="#d32f2f" stroke-width="2"/>
            <polygon points="100,150 110,145 110,155" fill="#d32f2f"/>
            <text x="170" y="168" font-size="12" fill="#d32f2f" font-weight="bold">V</text>

            <!-- Shear plane -->
            <line x1="100" y1="90" x2="250" y2="90" stroke="#4caf50" stroke-width="2" stroke-dasharray="5,3"/>
            <text x="260" y="95" font-size="11" fill="#4caf50">Shear plane (A)</text>

            <!-- Formula -->
            <text x="300" y="60" font-size="14" fill="#333" font-weight="bold">τ = V/A</text>
            <text x="300" y="80" font-size="11" fill="#666">Shear Stress</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Shear stress occurs when forces act parallel to a surface.",
            variables={"τ": "Shear stress (Pa)", "V": "Shear force (N)", "A": "Shear area (m²)"},
            examples=[
                FormulaExample(
                    description="Bolt in single shear",
                    inputs={"shear_force": "20000 N", "area": "0.000314 m²"},
                    expected_outputs={"shear_stress": "63.7 MPa"},
                    notes="20mm diameter bolt"
                )
            ]
        )

    @staticmethod
    def get_spring_diagram() -> FormulaDiagram:
        """Spring force-deflection diagram."""
        svg = '''
        <svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Fixed support -->
            <rect x="50" y="40" width="20" height="120" fill="#666"/>
            <line x1="50" y1="40" x2="30" y2="60" stroke="#666" stroke-width="2"/>
            <line x1="50" y1="60" x2="30" y2="80" stroke="#666" stroke-width="2"/>
            <line x1="50" y1="80" x2="30" y2="100" stroke="#666" stroke-width="2"/>
            <line x1="50" y1="100" x2="30" y2="120" stroke="#666" stroke-width="2"/>
            <line x1="50" y1="120" x2="30" y2="140" stroke="#666" stroke-width="2"/>
            <line x1="50" y1="140" x2="30" y2="160" stroke="#666" stroke-width="2"/>

            <!-- Spring coils -->
            <path d="M 70 100 L 90 80 L 110 120 L 130 80 L 150 120 L 170 80 L 190 120 L 210 80 L 230 120 L 250 100"
                  fill="none" stroke="#1976d2" stroke-width="3"/>

            <!-- Mass/block -->
            <rect x="250" y="80" width="40" height="40" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

            <!-- Force arrow -->
            <line x1="330" y1="100" x2="295" y2="100" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="295,100 305,95 305,105" fill="#d32f2f"/>
            <text x="335" y="105" font-size="14" fill="#d32f2f" font-weight="bold">F</text>

            <!-- Deflection indicator -->
            <line x1="270" y1="140" x2="270" y2="170" stroke="#4caf50" stroke-width="1"/>
            <line x1="270" y1="170" x2="320" y2="170" stroke="#4caf50" stroke-width="1"/>
            <line x1="320" y1="165" x2="320" y2="175" stroke="#4caf50" stroke-width="1"/>
            <text x="285" y="185" font-size="11" fill="#4caf50">δ</text>

            <!-- Formula -->
            <text x="100" y="180" font-size="14" fill="#333" font-weight="bold">F = kδ  →  k = F/δ</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Hooke's Law: Spring force is proportional to displacement.",
            variables={"F": "Applied force (N)", "k": "Spring rate/stiffness (N/m)", "δ": "Deflection (m)"},
            examples=[
                FormulaExample(
                    description="Automotive suspension spring",
                    inputs={"force": "5000 N", "spring_rate": "50000 N/m"},
                    expected_outputs={"deflection": "0.1 m (100mm)"},
                    notes="Typical car spring"
                )
            ]
        )

    @staticmethod
    def get_heat_conduction_diagram() -> FormulaDiagram:
        """Heat conduction through a wall."""
        svg = '''
        <svg viewBox="0 0 450 200" width="450" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Wall -->
            <rect x="150" y="30" width="80" height="140" fill="#ffcc80" stroke="#ef6c00" stroke-width="2"/>

            <!-- Hot side -->
            <text x="60" y="100" font-size="14" fill="#d32f2f" font-weight="bold">T₁ (hot)</text>
            <g fill="#d32f2f">
                <line x1="120" y1="60" x2="150" y2="60" stroke="#d32f2f" stroke-width="2"/>
                <line x1="120" y1="100" x2="150" y2="100" stroke="#d32f2f" stroke-width="2"/>
                <line x1="120" y1="140" x2="150" y2="140" stroke="#d32f2f" stroke-width="2"/>
            </g>

            <!-- Cold side -->
            <text x="260" y="100" font-size="14" fill="#1976d2" font-weight="bold">T₂ (cold)</text>
            <g fill="#1976d2">
                <line x1="230" y1="60" x2="260" y2="60" stroke="#1976d2" stroke-width="2"/>
                <line x1="230" y1="100" x2="260" y2="100" stroke="#1976d2" stroke-width="2"/>
                <line x1="230" y1="140" x2="260" y2="140" stroke="#1976d2" stroke-width="2"/>
            </g>

            <!-- Heat flow arrow -->
            <line x1="170" y1="100" x2="210" y2="100" stroke="#ff5722" stroke-width="3"/>
            <polygon points="210,100 200,95 200,105" fill="#ff5722"/>
            <text x="180" y="90" font-size="12" fill="#ff5722" font-weight="bold">Q</text>

            <!-- Thickness -->
            <line x1="150" y1="185" x2="230" y2="185" stroke="#666" stroke-width="1"/>
            <line x1="150" y1="180" x2="150" y2="190" stroke="#666" stroke-width="1"/>
            <line x1="230" y1="180" x2="230" y2="190" stroke="#666" stroke-width="1"/>
            <text x="185" y="198" font-size="11" fill="#666">L</text>

            <!-- Area indicator -->
            <text x="175" y="25" font-size="11" fill="#666">Area = A</text>

            <!-- Formula -->
            <text x="300" y="70" font-size="13" fill="#333" font-weight="bold">Q = kA(T₁-T₂)/L</text>
            <text x="300" y="90" font-size="11" fill="#666">Fourier's Law</text>
            <text x="300" y="115" font-size="10" fill="#666">k = conductivity</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Heat conduction through a solid material (Fourier's Law).",
            variables={
                "Q": "Heat transfer rate (W)",
                "k": "Thermal conductivity (W/m·K)",
                "A": "Cross-sectional area (m²)",
                "T₁-T₂": "Temperature difference (K)",
                "L": "Thickness (m)"
            },
            examples=[
                FormulaExample(
                    description="Heat loss through wall",
                    inputs={"conductivity": "0.5 W/m·K", "area": "10 m²", "temp_diff": "20 K", "thickness": "0.2 m"},
                    expected_outputs={"heat_transfer": "500 W"},
                    notes="Brick wall"
                )
            ]
        )

    @staticmethod
    def get_rectangular_section_diagram() -> FormulaDiagram:
        """Rectangular cross section."""
        svg = '''
        <svg viewBox="0 0 350 220" width="350" height="220" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <!-- Rectangle -->
            <rect x="80" y="40" width="120" height="140" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>

            <!-- Width dimension -->
            <line x1="80" y1="195" x2="200" y2="195" stroke="#666" stroke-width="1"/>
            <line x1="80" y1="190" x2="80" y2="200" stroke="#666" stroke-width="1"/>
            <line x1="200" y1="190" x2="200" y2="200" stroke="#666" stroke-width="1"/>
            <text x="135" y="212" font-size="12" fill="#666">b</text>

            <!-- Height dimension -->
            <line x1="215" y1="40" x2="215" y2="180" stroke="#666" stroke-width="1"/>
            <line x1="210" y1="40" x2="220" y2="40" stroke="#666" stroke-width="1"/>
            <line x1="210" y1="180" x2="220" y2="180" stroke="#666" stroke-width="1"/>
            <text x="225" y="115" font-size="12" fill="#666">h</text>

            <!-- Centroid -->
            <circle cx="140" cy="110" r="4" fill="#4caf50"/>
            <text x="145" y="108" font-size="10" fill="#4caf50">C</text>

            <!-- Axes -->
            <line x1="50" y1="110" x2="230" y2="110" stroke="#4caf50" stroke-width="1" stroke-dasharray="5,3"/>
            <line x1="140" y1="20" x2="140" y2="200" stroke="#9c27b0" stroke-width="1" stroke-dasharray="5,3"/>
            <text x="232" y="108" font-size="10" fill="#4caf50">x</text>
            <text x="143" y="18" font-size="10" fill="#9c27b0">y</text>

            <!-- Formulas -->
            <text x="250" y="50" font-size="11" fill="#333" font-weight="bold">Properties:</text>
            <text x="250" y="70" font-size="10" fill="#666">A = b × h</text>
            <text x="250" y="90" font-size="10" fill="#666">Ix = bh³/12</text>
            <text x="250" y="110" font-size="10" fill="#666">Iy = hb³/12</text>
            <text x="250" y="130" font-size="10" fill="#666">Sx = bh²/6</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Rectangular cross-section properties.",
            variables={
                "b": "Width (m)",
                "h": "Height (m)",
                "A": "Area (m²)",
                "Ix": "Moment of inertia about x-axis (m⁴)",
                "Sx": "Section modulus (m³)"
            },
            examples=[
                FormulaExample(
                    description="Timber beam",
                    inputs={"width": "0.1 m", "height": "0.2 m"},
                    expected_outputs={"area": "0.02 m²", "Ix": "6.67e-5 m⁴"},
                    notes="100mm x 200mm timber"
                )
            ]
        )

    @staticmethod
    def get_step_response_diagram() -> FormulaDiagram:
        """Control system step response."""
        svg = '''
        <svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <line x1="40" y1="170" x2="380" y2="170" stroke="#333" stroke-width="2"/>
            <line x1="40" y1="170" x2="40" y2="20" stroke="#333" stroke-width="2"/>
            <text x="200" y="195" font-size="11" fill="#333">Time (t)</text>
            <text x="15" y="100" font-size="11" fill="#333">y(t)</text>
            <line x1="40" y1="50" x2="380" y2="50" stroke="#4caf50" stroke-width="1" stroke-dasharray="5,3"/>
            <text x="385" y="55" font-size="10" fill="#4caf50">Final value</text>
            <path d="M 40 170 L 60 170 Q 100 30 160 60 Q 200 80 240 48 Q 280 40 320 50 L 380 50" fill="none" stroke="#1976d2" stroke-width="2"/>
            <circle cx="200" cy="40" r="3" fill="#d32f2f"/>
            <text x="205" y="35" font-size="9" fill="#d32f2f">Overshoot</text>
            <line x1="160" y1="50" x2="160" y2="170" stroke="#ff9800" stroke-width="1" stroke-dasharray="3,3"/>
            <text x="145" y="185" font-size="9" fill="#ff9800">Rise time</text>
            <text x="300" y="130" font-size="11" fill="#333" font-weight="bold">G(s) = ωn²/(s²+2ζωns+ωn²)</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Second-order system step response showing overshoot and settling time.",
            variables={"ζ": "Damping ratio", "ωn": "Natural frequency (rad/s)", "tr": "Rise time (s)", "ts": "Settling time (s)", "Mp": "Peak overshoot (%)"},
            examples=[FormulaExample(description="Motor position control", inputs={"damping_ratio": "0.5", "natural_freq": "10 rad/s"}, expected_outputs={"overshoot": "16.3%", "settling_time": "0.8 s"}, notes="Underdamped response")]
        )

    @staticmethod
    def get_pid_diagram() -> FormulaDiagram:
        """PID controller block diagram."""
        svg = '''
        <svg viewBox="0 0 450 180" width="450" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <circle cx="60" cy="90" r="15" fill="none" stroke="#333" stroke-width="2"/>
            <text x="55" y="95" font-size="14" fill="#333">Σ</text>
            <line x1="20" y1="90" x2="45" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
            <text x="25" y="80" font-size="10" fill="#333">r(t)</text>
            <rect x="100" y="70" width="80" height="40" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <text x="115" y="95" font-size="12" fill="#1976d2" font-weight="bold">PID</text>
            <line x1="75" y1="90" x2="100" y2="90" stroke="#333" stroke-width="2"/>
            <text x="80" y="80" font-size="10" fill="#333">e(t)</text>
            <rect x="220" y="70" width="80" height="40" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
            <text x="235" y="95" font-size="12" fill="#ff9800" font-weight="bold">Plant</text>
            <line x1="180" y1="90" x2="220" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
            <text x="185" y="80" font-size="10" fill="#333">u(t)</text>
            <line x1="300" y1="90" x2="400" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
            <text x="380" y="80" font-size="10" fill="#333">y(t)</text>
            <line x1="350" y1="90" x2="350" y2="150" stroke="#333" stroke-width="2"/>
            <line x1="350" y1="150" x2="60" y2="150" stroke="#333" stroke-width="2"/>
            <line x1="60" y1="150" x2="60" y2="105" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
            <text x="55" y="118" font-size="10" fill="#333">-</text>
            <text x="120" y="160" font-size="10" fill="#666">u = Kp·e + Ki∫e·dt + Kd·de/dt</text>
            <defs><marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker></defs>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="PID controller with proportional, integral, and derivative actions.",
            variables={"Kp": "Proportional gain", "Ki": "Integral gain", "Kd": "Derivative gain", "e(t)": "Error signal", "u(t)": "Control output"},
            examples=[FormulaExample(description="Temperature control", inputs={"Kp": "2.0", "Ki": "0.5", "Kd": "0.1"}, expected_outputs={"response": "Fast settling, minimal overshoot"}, notes="Ziegler-Nichols tuned")]
        )

    @staticmethod
    def get_vibration_diagram() -> FormulaDiagram:
        """Mass-spring-damper system."""
        svg = '''
        <svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <rect x="30" y="20" width="20" height="160" fill="#666"/>
            <path d="M 50 60 L 70 50 L 90 70 L 110 50 L 130 70 L 150 50 L 170 70 L 190 60" fill="none" stroke="#1976d2" stroke-width="3"/>
            <text x="110" y="40" font-size="11" fill="#1976d2">k</text>
            <rect x="60" y="120" width="120" height="30" fill="#ffcc80" stroke="#ef6c00" stroke-width="2"/>
            <line x1="120" y1="150" x2="120" y2="180" stroke="#ef6c00" stroke-width="2"/>
            <text x="125" y="170" font-size="11" fill="#ef6c00">c</text>
            <rect x="190" y="40" width="60" height="80" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <text x="210" y="85" font-size="14" fill="#1976d2" font-weight="bold">m</text>
            <line x1="280" y1="80" x2="320" y2="80" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="320,80 310,75 310,85" fill="#d32f2f"/>
            <text x="325" y="85" font-size="12" fill="#d32f2f">F(t)</text>
            <line x1="220" y1="130" x2="220" y2="170" stroke="#4caf50" stroke-width="1"/>
            <line x1="220" y1="170" x2="260" y2="170" stroke="#4caf50" stroke-width="1"/>
            <text x="235" y="185" font-size="10" fill="#4caf50">x(t)</text>
            <text x="270" y="150" font-size="10" fill="#333">mẍ + cẋ + kx = F(t)</text>
            <text x="270" y="170" font-size="10" fill="#666">ωn = √(k/m)</text>
            <text x="270" y="185" font-size="10" fill="#666">ζ = c/(2√km)</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Single degree of freedom mass-spring-damper vibration system.",
            variables={"m": "Mass (kg)", "k": "Spring stiffness (N/m)", "c": "Damping coefficient (N·s/m)", "ωn": "Natural frequency (rad/s)", "ζ": "Damping ratio"},
            examples=[FormulaExample(description="Vehicle suspension", inputs={"mass": "400 kg", "stiffness": "40000 N/m", "damping": "4000 N·s/m"}, expected_outputs={"natural_freq": "10 rad/s", "damping_ratio": "0.5"}, notes="Quarter-car model")]
        )

    @staticmethod
    def get_torsion_diagram() -> FormulaDiagram:
        """Torsion in a shaft."""
        svg = '''
        <svg viewBox="0 0 400 180" width="400" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <ellipse cx="80" cy="90" rx="15" ry="40" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <rect x="80" y="50" width="200" height="80" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <ellipse cx="280" cy="90" rx="15" ry="40" fill="#bbdefb" stroke="#1976d2" stroke-width="2"/>
            <path d="M 60 60 A 30 30 0 0 1 60 120" fill="none" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="60,120 55,108 68,115" fill="#d32f2f"/>
            <text x="35" y="95" font-size="14" fill="#d32f2f" font-weight="bold">T</text>
            <path d="M 300 120 A 30 30 0 0 1 300 60" fill="none" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="300,60 305,72 292,65" fill="#d32f2f"/>
            <text x="310" y="95" font-size="14" fill="#d32f2f" font-weight="bold">T</text>
            <line x1="80" y1="150" x2="280" y2="150" stroke="#666" stroke-width="1"/>
            <text x="175" y="165" font-size="11" fill="#666">L</text>
            <text x="175" y="95" font-size="11" fill="#1976d2">r</text>
            <text x="320" y="50" font-size="11" fill="#333" font-weight="bold">τ = Tr/J</text>
            <text x="320" y="70" font-size="10" fill="#666">θ = TL/GJ</text>
            <text x="320" y="90" font-size="10" fill="#666">J = πd⁴/32</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Torsional stress and angle of twist in a circular shaft.",
            variables={"τ": "Shear stress (Pa)", "T": "Torque (N·m)", "r": "Radius (m)", "J": "Polar moment of inertia (m⁴)", "θ": "Angle of twist (rad)", "G": "Shear modulus (Pa)"},
            examples=[FormulaExample(description="Drive shaft", inputs={"torque": "500 N·m", "diameter": "0.05 m", "length": "1 m"}, expected_outputs={"max_stress": "81.5 MPa", "twist_angle": "0.012 rad"}, notes="Steel shaft, G=80 GPa")]
        )

    @staticmethod
    def get_bolt_diagram() -> FormulaDiagram:
        """Bolted connection."""
        svg = '''
        <svg viewBox="0 0 380 200" width="380" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <rect x="100" y="40" width="150" height="30" fill="#ccc" stroke="#666" stroke-width="2"/>
            <rect x="100" y="70" width="150" height="30" fill="#ddd" stroke="#666" stroke-width="2"/>
            <rect x="165" y="20" width="20" height="100" fill="#1976d2" stroke="#0d47a1" stroke-width="2"/>
            <polygon points="175,20 160,5 190,5" fill="#1976d2" stroke="#0d47a1" stroke-width="2"/>
            <rect x="160" y="120" width="30" height="12" fill="#1976d2" stroke="#0d47a1" stroke-width="2"/>
            <line x1="175" y1="140" x2="175" y2="180" stroke="#d32f2f" stroke-width="2"/>
            <polygon points="175,180 170,165 180,165" fill="#d32f2f"/>
            <text x="180" y="175" font-size="12" fill="#d32f2f">F</text>
            <text x="200" y="55" font-size="10" fill="#666">Plate 1</text>
            <text x="200" y="85" font-size="10" fill="#666">Plate 2</text>
            <text x="260" y="50" font-size="11" fill="#333" font-weight="bold">σ = F/At</text>
            <text x="260" y="70" font-size="10" fill="#666">At = tensile area</text>
            <text x="260" y="90" font-size="11" fill="#333" font-weight="bold">τ = F/As</text>
            <text x="260" y="110" font-size="10" fill="#666">As = shear area</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Bolted joint showing tensile and shear loading.",
            variables={"σ": "Tensile stress (Pa)", "τ": "Shear stress (Pa)", "F": "Applied force (N)", "At": "Tensile stress area (m²)", "As": "Shear area (m²)"},
            examples=[FormulaExample(description="M12 bolt in tension", inputs={"force": "30000 N", "tensile_area": "84.3 mm²"}, expected_outputs={"tensile_stress": "356 MPa"}, notes="Grade 8.8 bolt")]
        )

    @staticmethod
    def get_cantilever_diagram() -> FormulaDiagram:
        """Cantilever beam."""
        svg = '''
        <svg viewBox="0 0 400 180" width="400" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <rect x="30" y="40" width="25" height="100" fill="#666"/>
            <line x1="30" y1="40" x2="10" y2="60" stroke="#666" stroke-width="2"/>
            <line x1="30" y1="60" x2="10" y2="80" stroke="#666" stroke-width="2"/>
            <line x1="30" y1="80" x2="10" y2="100" stroke="#666" stroke-width="2"/>
            <line x1="30" y1="100" x2="10" y2="120" stroke="#666" stroke-width="2"/>
            <line x1="30" y1="120" x2="10" y2="140" stroke="#666" stroke-width="2"/>
            <rect x="55" y="80" width="250" height="20" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <line x1="305" y1="105" x2="305" y2="155" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="305,155 300,140 310,140" fill="#d32f2f"/>
            <text x="310" y="140" font-size="14" fill="#d32f2f" font-weight="bold">P</text>
            <line x1="55" y1="115" x2="305" y2="115" stroke="#666" stroke-width="1"/>
            <text x="175" y="130" font-size="11" fill="#666">L</text>
            <path d="M 55 90 Q 180 92 305 110" fill="none" stroke="#4caf50" stroke-width="2" stroke-dasharray="5,3"/>
            <text x="180" y="75" font-size="10" fill="#4caf50">Deflected shape</text>
            <text x="320" y="60" font-size="10" fill="#333" font-weight="bold">δmax = PL³/3EI</text>
            <text x="320" y="80" font-size="10" fill="#333" font-weight="bold">Mmax = PL</text>
            <text x="320" y="100" font-size="10" fill="#666">at fixed end</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Cantilever beam with point load at free end.",
            variables={"P": "Point load (N)", "L": "Length (m)", "E": "Elastic modulus (Pa)", "I": "Moment of inertia (m⁴)", "δ": "Deflection (m)", "M": "Bending moment (N·m)"},
            examples=[FormulaExample(description="Diving board", inputs={"load": "800 N", "length": "3 m", "EI": "50000 N·m²"}, expected_outputs={"max_deflection": "0.144 m", "max_moment": "2400 N·m"}, notes="Person at end of board")]
        )

    @staticmethod
    def get_convection_diagram() -> FormulaDiagram:
        """Convection heat transfer."""
        svg = '''
        <svg viewBox="0 0 400 180" width="400" height="180" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <rect x="50" y="40" width="30" height="100" fill="#ff8a65" stroke="#e64a19" stroke-width="2"/>
            <text x="55" y="95" font-size="12" fill="#fff" font-weight="bold">Ts</text>
            <g fill="#64b5f6">
                <path d="M 100 50 Q 120 45 140 55 Q 160 65 180 55" fill="none" stroke="#1976d2" stroke-width="2"/>
                <path d="M 100 80 Q 120 75 140 85 Q 160 95 180 85" fill="none" stroke="#1976d2" stroke-width="2"/>
                <path d="M 100 110 Q 120 105 140 115 Q 160 125 180 115" fill="none" stroke="#1976d2" stroke-width="2"/>
            </g>
            <text x="130" y="145" font-size="11" fill="#1976d2">Fluid flow, T∞</text>
            <line x1="65" y1="90" x2="95" y2="90" stroke="#d32f2f" stroke-width="3"/>
            <polygon points="95,90 85,85 85,95" fill="#d32f2f"/>
            <text x="70" y="80" font-size="12" fill="#d32f2f" font-weight="bold">Q</text>
            <text x="220" y="50" font-size="12" fill="#333" font-weight="bold">Q = hA(Ts - T∞)</text>
            <text x="220" y="75" font-size="10" fill="#666">h = convection coefficient</text>
            <text x="220" y="95" font-size="10" fill="#666">A = surface area</text>
            <text x="220" y="115" font-size="10" fill="#666">Ts = surface temp</text>
            <text x="220" y="135" font-size="10" fill="#666">T∞ = fluid temp</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Convective heat transfer from a surface to a moving fluid.",
            variables={"Q": "Heat transfer rate (W)", "h": "Convection coefficient (W/m²·K)", "A": "Surface area (m²)", "Ts": "Surface temperature (K)", "T∞": "Fluid temperature (K)"},
            examples=[FormulaExample(description="Heated plate in air", inputs={"h": "25 W/m²·K", "area": "0.5 m²", "Ts": "80°C", "T∞": "20°C"}, expected_outputs={"heat_transfer": "750 W"}, notes="Natural convection")]
        )

    @staticmethod
    def get_circular_section_diagram() -> FormulaDiagram:
        """Circular cross section."""
        svg = '''
        <svg viewBox="0 0 350 200" width="350" height="200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
            <circle cx="120" cy="100" r="60" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
            <circle cx="120" cy="100" r="3" fill="#4caf50"/>
            <text x="125" y="98" font-size="10" fill="#4caf50">C</text>
            <line x1="120" y1="100" x2="180" y2="100" stroke="#d32f2f" stroke-width="2"/>
            <text x="145" y="95" font-size="12" fill="#d32f2f">r</text>
            <line x1="120" y1="40" x2="120" y2="160" stroke="#666" stroke-width="1" stroke-dasharray="3,3"/>
            <line x1="60" y1="100" x2="180" y2="100" stroke="#666" stroke-width="1" stroke-dasharray="3,3"/>
            <line x1="185" y1="40" x2="185" y2="160" stroke="#666" stroke-width="1"/>
            <text x="190" y="105" font-size="11" fill="#666">d</text>
            <text x="220" y="50" font-size="11" fill="#333" font-weight="bold">Properties:</text>
            <text x="220" y="70" font-size="10" fill="#666">A = πr² = πd²/4</text>
            <text x="220" y="90" font-size="10" fill="#666">I = πr⁴/4 = πd⁴/64</text>
            <text x="220" y="110" font-size="10" fill="#666">J = πr⁴/2 = πd⁴/32</text>
            <text x="220" y="130" font-size="10" fill="#666">S = πr³/4 = πd³/32</text>
        </svg>
        '''
        return FormulaDiagram(
            svg_diagram=svg,
            description="Solid circular cross-section properties.",
            variables={"r": "Radius (m)", "d": "Diameter (m)", "A": "Area (m²)", "I": "Moment of inertia (m⁴)", "J": "Polar moment of inertia (m⁴)", "S": "Section modulus (m³)"},
            examples=[FormulaExample(description="Steel rod", inputs={"diameter": "0.05 m"}, expected_outputs={"area": "0.00196 m²", "I": "3.07e-7 m⁴"}, notes="50mm diameter solid rod")]
        )

    @classmethod
    def get_diagram(cls, calculation_name: str) -> Optional[FormulaDiagram]:
        """Get diagram for a specific calculation by name."""
        diagrams = {
            # Materials (7)
            "AxialStress": cls.get_axial_stress_diagram,
            "ShearStress": cls.get_shear_stress_diagram,
            "Strain": cls.get_axial_stress_diagram,
            "HookesLaw": cls.get_axial_stress_diagram,
            "ThermalStress": cls.get_axial_stress_diagram,
            "VonMisesStress": cls.get_axial_stress_diagram,
            "FactorOfSafety": cls.get_axial_stress_diagram,

            # Statics (8)
            "MomentAboutPoint": cls.get_bending_moment_diagram,
            "SimplySupportedBeamReactions": cls.get_bending_moment_diagram,
            "CantileverBeamReaction": cls.get_cantilever_diagram,
            "BendingMoment": cls.get_bending_moment_diagram,
            "ShearForce": cls.get_bending_moment_diagram,
            "SectionModulus": cls.get_rectangular_section_diagram,
            "MomentOfInertiaRectangle": cls.get_rectangular_section_diagram,
            "CentroidComposite": cls.get_rectangular_section_diagram,

            # Fluids (8)
            "FlowRate": cls.get_pipe_flow_diagram,
            "ReynoldsNumber": cls.get_pipe_flow_diagram,
            "BernoulliEquation": cls.get_pipe_flow_diagram,
            "DarcyWeisbachHeadLoss": cls.get_pipe_flow_diagram,
            "FrictionFactor": cls.get_pipe_flow_diagram,
            "PipePressureDrop": cls.get_pipe_flow_diagram,
            "PumpPower": cls.get_pipe_flow_diagram,
            "HydraulicDiameter": cls.get_pipe_flow_diagram,

            # Trusses (8)
            "TrussNodeEquilibrium": cls.get_truss_diagram,
            "TrussMemberForce": cls.get_truss_diagram,
            "SimpleTrussReactions": cls.get_truss_diagram,
            "MethodOfSections": cls.get_truss_diagram,
            "TrussMemberStress": cls.get_truss_diagram,
            "TrussDeflection": cls.get_truss_diagram,
            "CriticalBucklingLoad": cls.get_truss_diagram,
            "TrussEfficiency": cls.get_truss_diagram,

            # Fatigue (8)
            "StressAmplitude": cls.get_fatigue_sn_diagram,
            "SNCurveLife": cls.get_fatigue_sn_diagram,
            "MinersRule": cls.get_fatigue_sn_diagram,
            "GoodmanDiagram": cls.get_fatigue_sn_diagram,
            "GerberCriterion": cls.get_fatigue_sn_diagram,
            "SoderbergCriterion": cls.get_fatigue_sn_diagram,
            "EnduranceLimitEstimate": cls.get_fatigue_sn_diagram,
            "StressConcentrationFatigue": cls.get_fatigue_sn_diagram,

            # Cross Sections (8)
            "RectangularSection": cls.get_rectangular_section_diagram,
            "CircularSection": cls.get_circular_section_diagram,
            "HollowCircularSection": cls.get_circular_section_diagram,
            "IBeamSection": cls.get_cross_section_i_beam_diagram,
            "CChannelSection": cls.get_cross_section_i_beam_diagram,
            "HollowRectangularSection": cls.get_rectangular_section_diagram,
            "TBeamSection": cls.get_cross_section_i_beam_diagram,
            "AngleSection": cls.get_rectangular_section_diagram,

            # Mechanical (8)
            "BoltTensileStress": cls.get_bolt_diagram,
            "BoltShearCapacity": cls.get_bolt_diagram,
            "BoltPreload": cls.get_bolt_diagram,
            "TorsionalStress": cls.get_torsion_diagram,
            "ShaftTwistAngle": cls.get_torsion_diagram,
            "BearingLife": cls.get_bolt_diagram,
            "SpringRate": cls.get_spring_diagram,
            "SpringDeflection": cls.get_spring_diagram,

            # Thermo (8)
            "ConductionHeatTransfer": cls.get_heat_conduction_diagram,
            "ConvectionHeatTransfer": cls.get_convection_diagram,
            "RadiationHeatTransfer": cls.get_convection_diagram,
            "ThermalResistance": cls.get_heat_conduction_diagram,
            "OverallHeatTransferCoefficient": cls.get_heat_conduction_diagram,
            "CarnotEfficiency": cls.get_heat_conduction_diagram,
            "RefrigerationCOP": cls.get_heat_conduction_diagram,
            "LogMeanTempDifference": cls.get_heat_conduction_diagram,

            # Controls (8)
            "FirstOrderResponse": cls.get_step_response_diagram,
            "SecondOrderResponse": cls.get_step_response_diagram,
            "SettlingTime": cls.get_step_response_diagram,
            "PercentOvershoot": cls.get_step_response_diagram,
            "ZieglerNicholsTuning": cls.get_pid_diagram,
            "PIDControllerOutput": cls.get_pid_diagram,
            "GainMargin": cls.get_pid_diagram,
            "PhaseMargin": cls.get_pid_diagram,

            # Vibrations (8)
            "NaturalFrequency": cls.get_vibration_diagram,
            "DampingRatio": cls.get_vibration_diagram,
            "DampedNaturalFrequency": cls.get_vibration_diagram,
            "LogarithmicDecrement": cls.get_vibration_diagram,
            "MagnificationFactor": cls.get_vibration_diagram,
            "Transmissibility": cls.get_vibration_diagram,
            "RotatingImbalanceResponse": cls.get_vibration_diagram,
            "CriticalSpeed": cls.get_vibration_diagram,
        }

        factory = diagrams.get(calculation_name)
        if factory:
            return factory()
        return None

    @classmethod
    def get_all_diagrams(cls) -> Dict[str, FormulaDiagram]:
        """Get all available diagrams."""
        return {
            "AxialStress": cls.get_axial_stress_diagram(),
            "BendingMoment": cls.get_bending_moment_diagram(),
            "ReynoldsNumber": cls.get_pipe_flow_diagram(),
            "Truss": cls.get_truss_diagram(),
            "SNCurve": cls.get_fatigue_sn_diagram(),
            "IBeamSection": cls.get_cross_section_i_beam_diagram(),
        }


__all__ = [
    "FormulaDiagram",
    "FormulaExample",
    "FormulaDiagramService",
]
