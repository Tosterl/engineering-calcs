"""SQLAlchemy ORM models for Engineering Calculations Database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Project(Base):
    """Project model for grouping related calculations."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    calculations: Mapped[list["Calculation"]] = relationship(
        "Calculation",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"


class Formula(Base):
    """Formula model for storing engineering formulas."""

    __tablename__ = "formulas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    formula_latex: Mapped[str] = mapped_column(Text, nullable=False)
    variables_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    calculations: Mapped[list["Calculation"]] = relationship(
        "Calculation",
        back_populates="formula",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Formula(id={self.id}, name='{self.name}', category='{self.category}')>"


class Calculation(Base):
    """Calculation model for storing calculation instances."""

    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    formula_id: Mapped[int] = mapped_column(ForeignKey("formulas.id"), nullable=False)
    inputs_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    outputs_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    formula: Mapped["Formula"] = relationship("Formula", back_populates="calculations")
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="calculations"
    )

    def __repr__(self) -> str:
        return f"<Calculation(id={self.id}, formula_id={self.formula_id})>"


class MaterialProperty(Base):
    """MaterialProperty model for storing material data."""

    __tablename__ = "material_properties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    properties_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Material properties: density, yield_strength, tensile_strength, etc."
    )
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<MaterialProperty(id={self.id}, name='{self.name}', category='{self.category}')>"
