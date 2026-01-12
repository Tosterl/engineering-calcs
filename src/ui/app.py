"""Main NiceGUI application for Engineering Calculations Database.

This module provides the main user interface using NiceGUI framework,
including navigation, routing, and responsive layout components.
"""

from __future__ import annotations

from typing import Callable, Optional

from nicegui import app, ui

from src.config import get_settings
from src.data.database import init_db
from src.ui.pages.dashboard import dashboard_page as render_dashboard
from src.ui.pages.calculate import calculate_page as render_calculate
from src.ui.pages.history import history_page as render_history
from src.ui.pages.settings import settings_page as render_settings


# Calculation categories mapped to their display names and icons
CALCULATION_CATEGORIES = {
    "statics": {"name": "Statics", "icon": "architecture"},
    "fluids": {"name": "Fluids", "icon": "water_drop"},
    "thermo": {"name": "Thermodynamics", "icon": "whatshot"},
    "materials": {"name": "Materials", "icon": "construction"},
    "mechanical": {"name": "Mechanical", "icon": "settings"},
    "controls": {"name": "Controls", "icon": "tune"},
    "vibrations": {"name": "Vibrations", "icon": "vibration"},
}


class AppState:
    """Application state management for UI components."""

    def __init__(self) -> None:
        """Initialize application state."""
        self.search_query: str = ""
        self.dark_mode: bool = get_settings().ui_theme == "dark"
        self.drawer_open: bool = True


# Global app state instance
state = AppState()


def create_header(drawer: ui.left_drawer) -> None:
    """Create the application header with title and navigation.

    Args:
        drawer: The left drawer instance to toggle.
    """
    settings = get_settings()

    with ui.header().classes("bg-primary items-center justify-between px-4"):
        # Left section: Menu button and title
        with ui.row().classes("items-center gap-4"):
            ui.button(
                icon="menu",
                on_click=lambda: drawer.toggle(),
            ).props("flat dense round color=white")

            ui.label(settings.app_title).classes(
                "text-h6 text-white font-bold hidden sm:block"
            )
            # Shorter title for mobile
            ui.label("Eng Calcs").classes(
                "text-h6 text-white font-bold sm:hidden"
            )

        # Right section: Theme toggle and settings
        with ui.row().classes("items-center gap-2"):
            ui.button(
                icon="dark_mode" if not state.dark_mode else "light_mode",
                on_click=toggle_dark_mode,
            ).props("flat dense round color=white").tooltip(
                "Toggle Dark Mode"
            )

            ui.button(
                icon="settings",
                on_click=lambda: ui.navigate.to("/settings"),
            ).props("flat dense round color=white").tooltip("Settings")


def create_sidebar() -> ui.left_drawer:
    """Create the left sidebar navigation drawer.

    Returns:
        The left drawer UI element.
    """
    drawer = ui.left_drawer(value=state.drawer_open).classes(
        "bg-gray-100 dark:bg-gray-800"
    ).props("width=280 breakpoint=800")

    with drawer:
        with ui.column().classes("w-full p-4 gap-2"):
            # Navigation header
            ui.label("Navigation").classes(
                "text-overline text-gray-600 dark:text-gray-400 mb-2"
            )

            # Dashboard link
            create_nav_item(
                label="Dashboard",
                icon="dashboard",
                route="/",
            )

            # Calculate link
            create_nav_item(
                label="New Calculation",
                icon="calculate",
                route="/calculate",
            )

            # Calculations section
            ui.separator().classes("my-2")
            ui.label("Categories").classes(
                "text-overline text-gray-600 dark:text-gray-400 mt-2 mb-2"
            )

            # Category navigation items
            for category_key, category_info in CALCULATION_CATEGORIES.items():
                create_nav_item(
                    label=category_info["name"],
                    icon=category_info["icon"],
                    route=f"/calculate/{category_key}",
                )

            # Tools section
            ui.separator().classes("my-2")
            ui.label("Tools").classes(
                "text-overline text-gray-600 dark:text-gray-400 mt-2 mb-2"
            )

            create_nav_item(
                label="History",
                icon="history",
                route="/history",
            )

            create_nav_item(
                label="Settings",
                icon="settings",
                route="/settings",
            )

    return drawer


def create_nav_item(label: str, icon: str, route: str) -> None:
    """Create a navigation item button.

    Args:
        label: Display text for the navigation item.
        icon: Material icon name.
        route: Target route when clicked.
    """
    with ui.button(on_click=lambda: ui.navigate.to(route)).classes(
        "w-full justify-start"
    ).props("flat align=left"):
        ui.icon(icon).classes("mr-2")
        ui.label(label)


def create_footer() -> None:
    """Create the application footer with status information."""
    settings = get_settings()

    with ui.footer().classes(
        "bg-gray-200 dark:bg-gray-900 text-gray-600 dark:text-gray-400"
    ):
        with ui.row().classes("w-full items-center justify-between px-4 py-2"):
            ui.label(f"Unit System: {settings.default_unit_system}").classes(
                "text-caption"
            )
            ui.label("Engineering Calculations Database v1.0.0").classes(
                "text-caption hidden md:block"
            )
            ui.label("Ready").classes("text-caption")


def toggle_dark_mode() -> None:
    """Toggle between light and dark mode."""
    state.dark_mode = not state.dark_mode
    ui.dark_mode().set_value(state.dark_mode)


def handle_theme_change(theme: str) -> None:
    """Handle theme change from settings.

    Args:
        theme: The new theme value ('light' or 'dark').
    """
    state.dark_mode = theme == "dark"
    ui.dark_mode().set_value(state.dark_mode)


@ui.page("/")
def dashboard_page() -> None:
    """Dashboard page showing overview and quick access to calculations."""
    # Initialize dark mode
    ui.dark_mode().set_value(state.dark_mode)

    drawer = create_sidebar()
    create_header(drawer)

    with ui.column().classes("w-full min-h-screen"):
        render_dashboard(
            navigate_to_calculate=lambda cat: ui.navigate.to(
                f"/calculate/{cat}" if cat else "/calculate"
            ),
            navigate_to_history=lambda: ui.navigate.to("/history"),
        )

    create_footer()


@ui.page("/calculate")
def calculation_page_default() -> None:
    """Calculation page without a pre-selected category."""
    # Initialize dark mode
    ui.dark_mode().set_value(state.dark_mode)

    drawer = create_sidebar()
    create_header(drawer)

    with ui.column().classes("w-full min-h-screen"):
        render_calculate(
            initial_category=None,
            navigate_to_dashboard=lambda: ui.navigate.to("/"),
        )

    create_footer()


@ui.page("/calculate/{category}")
def calculation_page(category: str) -> None:
    """Calculation page for a specific category.

    Args:
        category: The calculation category slug.
    """
    # Initialize dark mode
    ui.dark_mode().set_value(state.dark_mode)

    drawer = create_sidebar()
    create_header(drawer)

    # Map category slug to display name
    category_info = CALCULATION_CATEGORIES.get(category)
    category_name = category_info["name"] if category_info else category.title()

    with ui.column().classes("w-full min-h-screen"):
        render_calculate(
            initial_category=category_name,
            navigate_to_dashboard=lambda: ui.navigate.to("/"),
        )

    create_footer()


@ui.page("/history")
def history_page() -> None:
    """Saved calculations history page."""
    # Initialize dark mode
    ui.dark_mode().set_value(state.dark_mode)

    drawer = create_sidebar()
    create_header(drawer)

    with ui.column().classes("w-full min-h-screen"):
        render_history(
            navigate_to_calculate=lambda cat: ui.navigate.to(
                f"/calculate/{cat}" if cat else "/calculate"
            ),
            navigate_to_dashboard=lambda: ui.navigate.to("/"),
        )

    create_footer()


@ui.page("/settings")
def settings_page() -> None:
    """Application settings page."""
    # Initialize dark mode
    ui.dark_mode().set_value(state.dark_mode)

    drawer = create_sidebar()
    create_header(drawer)

    with ui.column().classes("w-full min-h-screen"):
        render_settings(
            navigate_to_dashboard=lambda: ui.navigate.to("/"),
            on_theme_change=handle_theme_change,
        )

    create_footer()


async def startup() -> None:
    """Application startup handler - initializes database."""
    await init_db()


def create_app(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    title: Optional[str] = None,
) -> None:
    """Create and configure the NiceGUI application.

    This function sets up the NiceGUI application with all routes,
    styling, and configuration.

    Args:
        host: Host address to bind the server to.
        port: Port number for the server.
        reload: Enable auto-reload for development.
        title: Custom application title (overrides config).

    Example:
        >>> from src.ui.app import create_app
        >>> create_app(host="0.0.0.0", port=8080)
    """
    settings = get_settings()

    # Set application title
    app_title = title or settings.app_title

    # Configure dark mode based on settings
    state.dark_mode = settings.ui_theme == "dark"

    # Register startup handler
    app.on_startup(startup)

    # Add custom CSS for responsive design (shared=True for use with @ui.page)
    ui.add_head_html("""
        <style>
            /* Responsive adjustments */
            @media (max-width: 600px) {
                .q-page-container {
                    padding: 8px !important;
                }
            }

            /* Smooth transitions */
            .q-card {
                transition: box-shadow 0.3s ease;
            }

            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: #f1f1f1;
            }

            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }

            /* Dark mode scrollbar */
            .dark ::-webkit-scrollbar-track {
                background: #333;
            }

            .dark ::-webkit-scrollbar-thumb {
                background: #666;
            }

            .dark ::-webkit-scrollbar-thumb:hover {
                background: #888;
            }
        </style>
    """, shared=True)

    # Run the application
    ui.run(
        host=host,
        port=port,
        reload=reload,
        title=app_title,
        favicon="calculator",
    )


# Module exports
__all__ = [
    "create_app",
    "AppState",
    "state",
    "CALCULATION_CATEGORIES",
    "dashboard_page",
    "calculation_page",
    "calculation_page_default",
    "history_page",
    "settings_page",
]
