# Engineering Calculations Database

A comprehensive Python application for performing engineering calculations across multiple domains with unit conversion support, interactive visualizations, and professional report generation.

## Description

The Engineering Calculations Database is a full-featured engineering tool that provides standardized calculations for common engineering problems. It combines a modern web interface with powerful computational capabilities, making it suitable for both educational purposes and professional engineering work.

## Features

- **7 Engineering Domains**: Complete calculation modules for:
  - Materials Science
  - Statics
  - Fluid Mechanics
  - Mechanical Engineering
  - Thermodynamics
  - Vibrations
  - Controls Systems

- **Unit Conversion**: Seamless unit handling and conversion powered by Pint, supporting both SI and Imperial units

- **Report Generation**: Export calculation results to professional PDF and Word documents

- **Interactive Visualizations**: Dynamic charts and plots using Plotly for data visualization and analysis

- **Web and Desktop Application**: Built with NiceGUI for a responsive web interface that can also run as a native desktop application

- **SQLite Database**: Persistent storage for saving and retrieving calculations

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd "Engineering Calcs Database"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: GitHub Codespaces (Easiest - No Installation Required)

1. **Push this project to a GitHub repository**
2. **Open in Codespaces**: Click the green "Code" button → "Codespaces" → "Create codespace on main"
3. **Wait for setup**: Dependencies install automatically
4. **Run the app**:
   ```bash
   python -m src.main
   ```
5. **Access the app**: Click the popup or go to the "Ports" tab and click the globe icon for port 8080

### Option 2: Run Locally as Web Application
```bash
python src/main.py
```
Access the application at [http://localhost:8080](http://localhost:8080)

### Option 3: Run as Desktop Application
```bash
python src/main.py --native
```
This launches the application in a native window.

## Project Structure

```
Engineering Calcs Database/
├── src/
│   ├── main.py              # Application entry point
│   ├── calculations/        # Calculation modules by domain
│   │   ├── materials/
│   │   ├── statics/
│   │   ├── fluids/
│   │   ├── mechanical/
│   │   ├── thermo/
│   │   ├── vibrations/
│   │   └── controls/
│   ├── database/            # SQLite database operations
│   ├── reports/             # PDF/Word report generation
│   ├── ui/                  # NiceGUI user interface components
│   └── utils/               # Unit conversion and utilities
├── tests/                   # Test suite
├── data/                    # Database files
├── requirements.txt         # Python dependencies
└── README.md
```

## Available Calculations

### Materials
- Stress-strain analysis
- Material property calculations
- Factor of safety analysis

### Statics
- Force equilibrium
- Moment calculations
- Truss analysis
- Beam reactions

### Fluids
- Pipe flow (Darcy-Weisbach)
- Bernoulli equation
- Reynolds number
- Head loss calculations

### Mechanical
- Gear ratios
- Power transmission
- Efficiency calculations

### Thermodynamics
- Heat transfer
- Thermal expansion
- Ideal gas calculations
- HVAC load analysis

### Vibrations
- Natural frequency
- Damping analysis
- Harmonic response
- Modal analysis

### Controls
- Transfer functions
- PID tuning
- System response analysis
- Stability analysis

## Development

### Running Tests
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src
```

### Adding New Calculations

1. Create a new module in the appropriate domain folder under `src/calculations/`
2. Implement the calculation function with proper unit handling using Pint
3. Add input validation and error handling
4. Create corresponding UI components in `src/ui/`
5. Write unit tests in the `tests/` directory
6. Update the database schema if persistent storage is needed

### Code Style

This project follows PEP 8 guidelines. Format code using:
```bash
black src/
```

## Dependencies

Key libraries used in this project:
- **NiceGUI**: Web and desktop UI framework
- **Pint**: Physical quantities and unit conversion
- **Plotly**: Interactive visualizations
- **ReportLab/python-docx**: PDF and Word document generation
- **SQLite3**: Database operations
- **pytest**: Testing framework

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
