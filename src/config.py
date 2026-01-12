"""Configuration module for Engineering Calculations Database.

This module provides application configuration using Pydantic Settings,
supporting environment variables with the ENGCALC_ prefix.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for Engineering Calculations Database.

    Settings can be configured via environment variables with the ENGCALC_ prefix.
    For example, ENGCALC_DATABASE_PATH will set the database_path value.

    Attributes:
        database_path: Path to the SQLite database file.
        default_unit_system: Default unit system for calculations ("SI" or "Imperial").
        report_output_dir: Directory where generated reports will be saved.
        ui_theme: User interface theme ("light" or "dark").
        app_title: Title displayed in the application.
    """

    model_config = SettingsConfigDict(
        env_prefix="ENGCALC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_path: Path = Path("data/engineering.db")
    default_unit_system: Literal["SI", "Imperial"] = "SI"
    report_output_dir: Path = Path("reports")
    ui_theme: Literal["light", "dark"] = "light"
    app_title: str = "Engineering Calculations Database"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance.

    This function returns a cached Settings instance, ensuring that settings
    are only loaded once from environment variables and configuration files.

    Returns:
        Settings: The application settings instance.

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_title)
        Engineering Calculations Database
    """
    return Settings()
