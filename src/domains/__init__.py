"""
Engineering calculation domain modules.

Each module contains calculations for a specific engineering domain.
All calculations are automatically registered with the CalculationRegistry on import.
"""

from src.domains import (
    controls,
    cross_sections,
    fatigue,
    fluids,
    materials,
    mechanical,
    statics,
    thermo,
    trusses,
    vibrations,
)

__all__ = [
    "controls",
    "cross_sections",
    "fatigue",
    "fluids",
    "materials",
    "mechanical",
    "statics",
    "thermo",
    "trusses",
    "vibrations",
]
