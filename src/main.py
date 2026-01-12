"""Main application entry point for Engineering Calculations Database.

This module initializes the database, registers all domain calculations,
and starts the NiceGUI web application.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import NoReturn

# Import database initialization
from src.data.database import init_db

# Import all domain modules to register their calculations
# Each module registers its calculations with the CalculationRegistry on import
from src.domains import (
    controls,
    fluids,
    materials,
    mechanical,
    statics,
    thermo,
    vibrations,
)

# Import the UI application factory
from src.ui.app import create_app


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the application.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Engineering Calculations Database - A comprehensive tool for engineering calculations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address to bind the server to (use 0.0.0.0 for cloud/codespaces)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port number for the server",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    parser.add_argument(
        "--native",
        action="store_true",
        help="Run as a native desktop application",
    )

    return parser.parse_args()


async def initialize_database() -> None:
    """Initialize the database asynchronously.

    This creates all necessary tables if they don't exist.
    """
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")


def main() -> NoReturn:
    """Main entry point for the application.

    Parses arguments, initializes the database, and starts the NiceGUI app.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Initialize the database before starting the app
    asyncio.run(initialize_database())

    # Log registered domain modules (for debugging)
    print("Registered domain modules:")
    print(f"  - Materials: {materials.__name__}")
    print(f"  - Statics: {statics.__name__}")
    print(f"  - Fluids: {fluids.__name__}")
    print(f"  - Mechanical: {mechanical.__name__}")
    print(f"  - Thermodynamics: {thermo.__name__}")
    print(f"  - Vibrations: {vibrations.__name__}")
    print(f"  - Controls: {controls.__name__}")

    # Start the NiceGUI application
    print(f"\nStarting Engineering Calculations Database...")
    print(f"Server: http://{args.host}:{args.port}")

    if args.native:
        # Run as native desktop application
        from nicegui import native, ui
        from src.ui.app import startup

        # Register startup handler for database
        from nicegui import app
        app.on_startup(startup)

        ui.run(
            host=args.host,
            port=args.port,
            reload=args.reload,
            native=True,
            title="Engineering Calculations Database",
            favicon="calculator",
        )
    else:
        # Run as web application
        create_app(
            host=args.host,
            port=args.port,
            reload=args.reload,
        )

    # This line is reached when the application exits
    sys.exit(0)


if __name__ == "__main__":
    main()
