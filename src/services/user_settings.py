"""
User settings persistence service.

Stores user preferences in a local JSON file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field


# Default settings file location
SETTINGS_FILE = Path("data/user_settings.json")


@dataclass
class UserSettings:
    """User preferences that persist across sessions."""

    # Unit system: "SI" or "Imperial"
    unit_system: str = "SI"

    # Theme: "light" or "dark"
    theme: str = "light"

    # Report defaults
    report_author: str = ""
    report_company: str = ""
    report_logo_path: str = ""
    include_calc_steps: bool = True
    include_charts: bool = True

    # Display preferences
    decimal_places: int = 4
    show_formula_diagrams: bool = True
    show_examples: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSettings":
        """Create from dictionary."""
        # Only use keys that exist in the dataclass
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class UserSettingsService:
    """Service for loading and saving user settings."""

    _instance: Optional["UserSettingsService"] = None
    _settings: Optional[UserSettings] = None

    def __new__(cls) -> "UserSettingsService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the service."""
        if self._settings is None:
            self._settings = self._load()

    def _load(self) -> UserSettings:
        """Load settings from file."""
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                return UserSettings.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")

        return UserSettings()

    def save(self) -> bool:
        """Save settings to file."""
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    @property
    def settings(self) -> UserSettings:
        """Get current settings."""
        return self._settings

    def update(self, **kwargs) -> None:
        """Update settings with provided values."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return getattr(self._settings, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a specific setting value."""
        if hasattr(self._settings, key):
            setattr(self._settings, key, value)

    def reset(self) -> None:
        """Reset to default settings."""
        self._settings = UserSettings()
        self.save()


# Convenience function
def get_user_settings() -> UserSettingsService:
    """Get the user settings service instance."""
    return UserSettingsService()


__all__ = [
    "UserSettings",
    "UserSettingsService",
    "get_user_settings",
    "SETTINGS_FILE",
]
