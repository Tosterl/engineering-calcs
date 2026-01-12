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
        <svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
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
        <svg viewBox="0 0 450 220" xmlns="http://www.w3.org/2000/svg">
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
        <svg viewBox="0 0 450 180" xmlns="http://www.w3.org/2000/svg">
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
        <svg viewBox="0 0 450 200" xmlns="http://www.w3.org/2000/svg">
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
        <svg viewBox="0 0 450 220" xmlns="http://www.w3.org/2000/svg">
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
        <svg viewBox="0 0 350 250" xmlns="http://www.w3.org/2000/svg">
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

    @classmethod
    def get_diagram(cls, calculation_name: str) -> Optional[FormulaDiagram]:
        """Get diagram for a specific calculation by name."""
        diagrams = {
            "AxialStress": cls.get_axial_stress_diagram,
            "BendingMoment": cls.get_bending_moment_diagram,
            "ReynoldsNumber": cls.get_pipe_flow_diagram,
            "SimpleTrussReactions": cls.get_truss_diagram,
            "TrussMemberForce": cls.get_truss_diagram,
            "SNCurveLife": cls.get_fatigue_sn_diagram,
            "IBeamSection": cls.get_cross_section_i_beam_diagram,
            # Add more mappings as needed
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
