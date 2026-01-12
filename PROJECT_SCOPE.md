# Engineering Calculations Database - Project Scope

## Overview

### Project Goals
Build a comprehensive engineering calculations tool that provides:
- A searchable database of engineering formulas and calculations
- Automatic unit conversion and validation
- Professional report generation (PDF/Word)
- Data visualization (graphs, diagrams)
- Cross-platform access (web browser + desktop application)

### Target Domains
1. **Strengths & Materials** - Stress, strain, material properties, failure criteria
2. **Statics** - Forces, moments, equilibrium, trusses, beams
3. **Fluid Dynamics** - Flow rates, pressure drop, Reynolds number, pipe sizing
4. **Mechanical Design** - Fasteners, bearings, shafts, gears, springs
5. **Thermodynamics** - Heat transfer, cycles, efficiency, psychrometrics
6. **Vibrations** - Natural frequency, damping, resonance, modal analysis
7. **Modeling & Controls** - Transfer functions, PID, stability analysis

### Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core application |
| Web Framework | FastAPI | REST API backend |
| Desktop/Web UI | NiceGUI | Single codebase for web + desktop |
| Database | SQLite | Local calculation storage |
| Units | Pint | Unit conversion & validation |
| Math | NumPy, SciPy | Numerical calculations |
| Visualization | Plotly | Interactive charts & graphs |
| Reports | ReportLab, python-docx | PDF/Word generation |
| Packaging | PyInstaller | Desktop executable |

---

## Architecture

### High-Level Design
```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│                 (NiceGUI - Web & Desktop)                   │
├─────────────────────────────────────────────────────────────┤
│                      API Layer (FastAPI)                    │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Calculation │    Units     │   Reports    │ Visualization │
│    Engine    │   Service    │   Service    │    Service    │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                    Data Layer (SQLite)                      │
│         Formulas │ Calculations │ Projects │ Settings       │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure
```
engineering-calcs/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── units.py            # Unit conversion service
│   │   ├── calculations.py     # Base calculation classes
│   │   └── validation.py       # Input validation
│   ├── domains/
│   │   ├── __init__.py
│   │   ├── materials.py        # Strengths & materials calcs
│   │   ├── statics.py          # Statics calculations
│   │   ├── fluids.py           # Fluid dynamics calcs
│   │   ├── mechanical.py       # Mechanical design calcs
│   │   ├── thermo.py           # Thermodynamics calcs
│   │   ├── vibrations.py       # Vibration analysis calcs
│   │   └── controls.py         # Modeling & controls calcs
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py         # Database connection & ORM
│   │   ├── models.py           # Data models (SQLAlchemy)
│   │   └── repositories.py     # Data access patterns
│   ├── services/
│   │   ├── __init__.py
│   │   ├── report_service.py   # PDF/Word generation
│   │   ├── chart_service.py    # Visualization generation
│   │   └── search_service.py   # Formula/calc search
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI routes
│   └── ui/
│       ├── __init__.py
│       ├── app.py              # NiceGUI main app
│       ├── pages/              # UI pages
│       └── components/         # Reusable UI components
├── data/
│   ├── formulas.json           # Built-in formula definitions
│   ├── materials.json          # Material property database
│   └── engineering.db          # SQLite database (generated)
├── tests/
│   ├── __init__.py
│   ├── test_units.py
│   ├── test_calculations.py
│   └── test_domains/
├── docs/
│   └── formulas/               # Formula documentation
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Development Phases

### Phase 1: Foundation (Data Models & Core Logic)
Build the fundamental infrastructure that all features depend on.

### Phase 2: Calculation Engine
Implement the core calculation framework and domain-specific formulas.

### Phase 3: Services Layer
Build report generation, visualization, and search capabilities.

### Phase 4: User Interface
Create the web/desktop interface using NiceGUI.

### Phase 5: Integration & Polish
Connect all components, add quality-of-life features.

### Phase 6: Packaging & Deployment
Create distributable packages for desktop and web deployment.

---

## Task Checklist

### Phase 1: Foundation

#### 1.1 Project Setup
- [ ] **1.1.1** Create project directory structure
- [ ] **1.1.2** Initialize Python virtual environment
- [ ] **1.1.3** Create `pyproject.toml` with project metadata
- [ ] **1.1.4** Create `requirements.txt` with dependencies:
  - fastapi, uvicorn
  - nicegui
  - sqlalchemy, aiosqlite
  - pint
  - numpy, scipy
  - plotly
  - reportlab, python-docx
  - pytest
- [ ] **1.1.5** Install dependencies and verify imports
- [ ] **1.1.6** Create basic `src/__init__.py` files
- [ ] **1.1.7** Set up `.gitignore` for Python projects

**Acceptance Criteria:** `python -c "import fastapi, nicegui, pint, numpy"` runs without error

#### 1.2 Configuration System
- [ ] **1.2.1** Create `src/config.py` with Pydantic settings
- [ ] **1.2.2** Define configuration for:
  - Database path
  - Default units system (SI/Imperial)
  - Report output directory
  - UI theme settings
- [ ] **1.2.3** Support environment variables override
- [ ] **1.2.4** Create default config file template

**Acceptance Criteria:** Config loads from file/env, provides typed access to settings

#### 1.3 Unit Conversion System
- [ ] **1.3.1** Create `src/core/units.py`
- [ ] **1.3.2** Initialize Pint unit registry with engineering units
- [ ] **1.3.3** Add custom unit definitions (if needed):
  - ksi (kilopounds per square inch)
  - Engineering-specific abbreviations
- [ ] **1.3.4** Create `Quantity` wrapper class with:
  - Unit validation
  - Conversion methods
  - String formatting options
- [ ] **1.3.5** Implement unit-aware arithmetic operations
- [ ] **1.3.6** Create unit compatibility checking function
- [ ] **1.3.7** Write unit tests for conversions

**Acceptance Criteria:** `convert(100, 'psi', 'MPa')` returns correct value with units

#### 1.4 Database Layer
- [ ] **1.4.1** Create `src/data/database.py` with async SQLite connection
- [ ] **1.4.2** Create `src/data/models.py` with SQLAlchemy models:
  - `Formula` - stored formula definitions
  - `Calculation` - saved calculation instances
  - `Project` - group calculations by project
  - `MaterialProperty` - material database entries
- [ ] **1.4.3** Define relationships between models
- [ ] **1.4.4** Create database initialization function
- [ ] **1.4.5** Create `src/data/repositories.py` with CRUD operations
- [ ] **1.4.6** Write migration/schema creation script
- [ ] **1.4.7** Write tests for database operations

**Acceptance Criteria:** Can create, read, update, delete records; database persists between runs

#### 1.5 Input Validation
- [ ] **1.5.1** Create `src/core/validation.py`
- [ ] **1.5.2** Implement numeric range validators
- [ ] **1.5.3** Implement unit dimension validators
- [ ] **1.5.4** Create validation decorator for calculation functions
- [ ] **1.5.5** Define common validation rules (positive, non-zero, etc.)
- [ ] **1.5.6** Create meaningful error messages
- [ ] **1.5.7** Write validation tests

**Acceptance Criteria:** Invalid inputs raise descriptive `ValidationError`

---

### Phase 2: Calculation Engine

#### 2.1 Base Calculation Framework
- [ ] **2.1.1** Create `src/core/calculations.py`
- [ ] **2.1.2** Define `Calculation` base class with:
  - Input parameter definitions (name, unit, description)
  - Output definitions
  - `calculate()` method signature
  - Metadata (name, category, description, references)
- [ ] **2.1.3** Create `CalculationResult` class with:
  - Input values (with units)
  - Output values (with units)
  - Intermediate steps (for reports)
  - Timestamp
- [ ] **2.1.4** Implement calculation registry (discover all calcs)
- [ ] **2.1.5** Create calculation factory function
- [ ] **2.1.6** Write framework tests

**Acceptance Criteria:** Can define a calculation class, execute it, get typed results

#### 2.2 Materials & Strength Calculations
- [ ] **2.2.1** Create `src/domains/materials.py`
- [ ] **2.2.2** Implement calculations:
  - Axial stress (σ = F/A)
  - Shear stress (τ = V/A)
  - Strain (ε = ΔL/L)
  - Hooke's Law (σ = Eε)
  - Poisson's ratio effects
  - Thermal stress
  - Factor of safety
- [ ] **2.2.3** Implement failure criteria:
  - Maximum stress theory
  - Von Mises stress
  - Mohr's Circle calculations
- [ ] **2.2.4** Create material property lookup
- [ ] **2.2.5** Write comprehensive tests
- [ ] **2.2.6** Add formula documentation

**Acceptance Criteria:** All material calculations pass validation; results match textbook examples

#### 2.3 Statics Calculations
- [ ] **2.3.1** Create `src/domains/statics.py`
- [ ] **2.3.2** Implement force/moment calculations:
  - Force resultants
  - Moment about a point
  - Couple calculations
  - Equilibrium checks
- [ ] **2.3.3** Implement beam analysis:
  - Simply supported beam reactions
  - Cantilever beam reactions
  - Shear force at point
  - Bending moment at point
  - Section modulus
- [ ] **2.3.4** Implement centroid calculations:
  - Composite shapes
  - Moment of inertia
  - Parallel axis theorem
- [ ] **2.3.5** Write tests with known solutions
- [ ] **2.3.6** Add formula documentation

**Acceptance Criteria:** Beam calculations match reference solutions within 0.1%

#### 2.4 Fluid Dynamics Calculations
- [ ] **2.4.1** Create `src/domains/fluids.py`
- [ ] **2.4.2** Implement basic flow calculations:
  - Continuity equation (Q = VA)
  - Reynolds number
  - Bernoulli's equation
  - Head loss (Darcy-Weisbach)
  - Minor losses
- [ ] **2.4.3** Implement pipe sizing:
  - Friction factor (Moody diagram / Colebrook)
  - Pipe flow calculator
  - Pressure drop in pipes
- [ ] **2.4.4** Implement pump calculations:
  - Total dynamic head
  - Pump power
  - NPSH calculations
- [ ] **2.4.5** Add fluid property lookup (water, air, common fluids)
- [ ] **2.4.6** Write comprehensive tests
- [ ] **2.4.7** Add formula documentation

**Acceptance Criteria:** Pipe sizing matches hydraulic references; friction factor accurate to 1%

#### 2.5 Mechanical Design Calculations
- [ ] **2.5.1** Create `src/domains/mechanical.py`
- [ ] **2.5.2** Implement fastener calculations:
  - Bolt tensile stress
  - Bolt shear capacity
  - Thread stripping
  - Joint stiffness
  - Preload calculations
- [ ] **2.5.3** Implement shaft design:
  - Torsional stress
  - Combined loading
  - Shaft deflection
  - Critical speed
- [ ] **2.5.4** Implement bearing calculations:
  - Bearing life (L10)
  - Dynamic load rating
  - Static load rating
- [ ] **2.5.5** Implement spring calculations:
  - Spring rate
  - Deflection
  - Spring stress
- [ ] **2.5.6** Write tests
- [ ] **2.5.7** Add formula documentation

**Acceptance Criteria:** Fastener calculations match Machinery's Handbook values

#### 2.6 Thermodynamics Calculations
- [ ] **2.6.1** Create `src/domains/thermo.py`
- [ ] **2.6.2** Implement heat transfer:
  - Conduction (Fourier's Law)
  - Convection
  - Radiation (Stefan-Boltzmann)
  - Thermal resistance networks
  - Overall heat transfer coefficient
- [ ] **2.6.3** Implement thermodynamic cycles:
  - Carnot efficiency
  - Rankine cycle basics
  - Refrigeration COP
- [ ] **2.6.4** Implement psychrometrics:
  - Humidity ratio
  - Dew point
  - Wet bulb temperature
- [ ] **2.6.5** Write tests
- [ ] **2.6.6** Add formula documentation

**Acceptance Criteria:** Heat transfer calculations within 1% of reference values

#### 2.7 Vibrations Calculations
- [ ] **2.7.1** Create `src/domains/vibrations.py`
- [ ] **2.7.2** Implement SDOF systems:
  - Natural frequency
  - Damping ratio
  - Damped frequency
  - Logarithmic decrement
- [ ] **2.7.3** Implement forced vibration:
  - Magnification factor
  - Phase angle
  - Transmissibility
- [ ] **2.7.4** Implement rotating machinery:
  - Imbalance response
  - Critical speed
  - Bearing stiffness effects
- [ ] **2.7.5** Write tests
- [ ] **2.7.6** Add formula documentation

**Acceptance Criteria:** Natural frequency calculations match analytical solutions

#### 2.8 Modeling & Controls Calculations
- [ ] **2.8.1** Create `src/domains/controls.py`
- [ ] **2.8.2** Implement transfer functions:
  - First order system response
  - Second order system response
  - Time constant
  - Settling time
  - Overshoot
- [ ] **2.8.3** Implement PID calculations:
  - Ziegler-Nichols tuning
  - Cohen-Coon tuning
  - PID response simulation
- [ ] **2.8.4** Implement stability analysis:
  - Gain margin
  - Phase margin
  - Routh-Hurwitz criteria
- [ ] **2.8.5** Write tests
- [ ] **2.8.6** Add formula documentation

**Acceptance Criteria:** Step response calculations match control theory references

---

### Phase 3: Services Layer

#### 3.1 Search Service
- [ ] **3.1.1** Create `src/services/search_service.py`
- [ ] **3.1.2** Implement formula search by:
  - Name (fuzzy matching)
  - Category/domain
  - Keywords
  - Variable names
- [ ] **3.1.3** Implement saved calculation search
- [ ] **3.1.4** Add search result ranking
- [ ] **3.1.5** Write tests

**Acceptance Criteria:** Searching "stress" returns all stress-related calculations

#### 3.2 Visualization Service
- [ ] **3.2.1** Create `src/services/chart_service.py`
- [ ] **3.2.2** Implement chart types:
  - Line plots (parametric studies)
  - Bar charts (comparisons)
  - Scatter plots
  - Mohr's circle diagram
  - Shear/moment diagrams
- [ ] **3.2.3** Create consistent styling/themes
- [ ] **3.2.4** Implement interactive Plotly charts
- [ ] **3.2.5** Add export to PNG/SVG
- [ ] **3.2.6** Write tests

**Acceptance Criteria:** Can generate interactive chart from calculation results

#### 3.3 Report Service
- [ ] **3.3.1** Create `src/services/report_service.py`
- [ ] **3.3.2** Design report template structure:
  - Header (title, date, project)
  - Input parameters table
  - Calculation steps (show formulas)
  - Results summary
  - Charts/diagrams
  - References
- [ ] **3.3.3** Implement PDF generation (ReportLab)
- [ ] **3.3.4** Implement Word generation (python-docx)
- [ ] **3.3.5** Add LaTeX equation rendering for PDFs
- [ ] **3.3.6** Create professional formatting/styling
- [ ] **3.3.7** Write tests

**Acceptance Criteria:** Generate professional PDF with formulas, tables, and charts

---

### Phase 4: User Interface

#### 4.1 UI Foundation
- [ ] **4.1.1** Create `src/ui/app.py` with NiceGUI setup
- [ ] **4.1.2** Define application layout:
  - Sidebar navigation
  - Header with search
  - Main content area
  - Footer with status
- [ ] **4.1.3** Create color theme (light/dark)
- [ ] **4.1.4** Set up page routing
- [ ] **4.1.5** Create responsive layout
- [ ] **4.1.6** Test basic navigation

**Acceptance Criteria:** App launches, pages navigate correctly

#### 4.2 Reusable Components
- [ ] **4.2.1** Create `src/ui/components/`
- [ ] **4.2.2** Create input components:
  - Numeric input with unit selector
  - Material selector dropdown
  - Parameter group container
- [ ] **4.2.3** Create output components:
  - Result card (value + unit)
  - Results table
  - Status indicators
- [ ] **4.2.4** Create chart component wrapper
- [ ] **4.2.5** Create formula display component (rendered math)
- [ ] **4.2.6** Test all components

**Acceptance Criteria:** Components render correctly, emit proper events

#### 4.3 Dashboard Page
- [ ] **4.3.1** Create `src/ui/pages/dashboard.py`
- [ ] **4.3.2** Show recent calculations
- [ ] **4.3.3** Show quick-access favorites
- [ ] **4.3.4** Show projects overview
- [ ] **4.3.5** Add quick search
- [ ] **4.3.6** Test dashboard functionality

**Acceptance Criteria:** Dashboard shows relevant data, quick actions work

#### 4.4 Calculation Pages
- [ ] **4.4.1** Create `src/ui/pages/calculate.py` base page
- [ ] **4.4.2** Create category browser (tree/list view)
- [ ] **4.4.3** Create calculation form generator:
  - Read calculation metadata
  - Generate input fields automatically
  - Show formula/description
- [ ] **4.4.4** Create results display:
  - Output values
  - Intermediate steps
  - Visualization (if applicable)
- [ ] **4.4.5** Add save calculation button
- [ ] **4.4.6** Add generate report button
- [ ] **4.4.7** Test calculation workflow

**Acceptance Criteria:** Can browse, select, execute, and save any calculation

#### 4.5 Search Page
- [ ] **4.5.1** Create `src/ui/pages/search.py`
- [ ] **4.5.2** Add search input with filters
- [ ] **4.5.3** Display search results with preview
- [ ] **4.5.4** Add click-to-navigate to calculation
- [ ] **4.5.5** Test search functionality

**Acceptance Criteria:** Search finds relevant calculations quickly

#### 4.6 History & Projects Page
- [ ] **4.6.1** Create `src/ui/pages/history.py`
- [ ] **4.6.2** List saved calculations (sortable, filterable)
- [ ] **4.6.3** Add project organization
- [ ] **4.6.4** Enable re-run saved calculation
- [ ] **4.6.5** Enable delete/archive
- [ ] **4.6.6** Test history features

**Acceptance Criteria:** Can view, organize, re-run past calculations

#### 4.7 Settings Page
- [ ] **4.7.1** Create `src/ui/pages/settings.py`
- [ ] **4.7.2** Add unit system preference (SI/Imperial)
- [ ] **4.7.3** Add report settings (header, logo)
- [ ] **4.7.4** Add theme toggle
- [ ] **4.7.5** Add export/import data
- [ ] **4.7.6** Test settings persistence

**Acceptance Criteria:** Settings save and apply correctly

---

### Phase 5: Integration & Polish

#### 5.1 API Layer
- [ ] **5.1.1** Create `src/api/routes.py` with FastAPI
- [ ] **5.1.2** Implement endpoints:
  - GET /calculations - list available
  - POST /calculate - execute calculation
  - GET /history - saved calculations
  - POST /reports - generate report
- [ ] **5.1.3** Add request validation
- [ ] **5.1.4** Add error handling
- [ ] **5.1.5** Write API tests

**Acceptance Criteria:** API endpoints work correctly, return proper errors

#### 5.2 Integration Testing
- [ ] **5.2.1** Create end-to-end test suite
- [ ] **5.2.2** Test complete workflows:
  - Search → Calculate → Save → Report
  - Create project → Add calculations → Export
- [ ] **5.2.3** Test unit conversions throughout
- [ ] **5.2.4** Test error handling paths
- [ ] **5.2.5** Fix any integration bugs

**Acceptance Criteria:** All E2E tests pass

#### 5.3 Polish & UX
- [ ] **5.3.1** Add loading indicators
- [ ] **5.3.2** Add success/error notifications
- [ ] **5.3.3** Add keyboard shortcuts
- [ ] **5.3.4** Improve error messages
- [ ] **5.3.5** Add tooltips/help text
- [ ] **5.3.6** Performance optimization
- [ ] **5.3.7** User testing and feedback

**Acceptance Criteria:** App feels responsive and professional

---

### Phase 6: Packaging & Deployment

#### 6.1 Desktop Packaging
- [ ] **6.1.1** Configure PyInstaller spec file
- [ ] **6.1.2** Bundle all dependencies
- [ ] **6.1.3** Create Windows executable
- [ ] **6.1.4** Add application icon
- [ ] **6.1.5** Test on clean Windows machine
- [ ] **6.1.6** Create installer (optional)

**Acceptance Criteria:** .exe runs on Windows without Python installed

#### 6.2 Documentation
- [ ] **6.2.1** Write README with setup instructions
- [ ] **6.2.2** Document all calculation formulas
- [ ] **6.2.3** Create user guide
- [ ] **6.2.4** Add inline code documentation

**Acceptance Criteria:** New user can set up and use the application from docs

#### 6.3 Data & Formulas
- [ ] **6.3.1** Compile material properties database
- [ ] **6.3.2** Add standard material library (steel, aluminum, etc.)
- [ ] **6.3.3** Add fluid properties library
- [ ] **6.3.4** Verify all formula accuracy
- [ ] **6.3.5** Add reference citations

**Acceptance Criteria:** Material database covers common engineering materials

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1.1 - 1.5 | Foundation (setup, units, database, validation) |
| 2 | 2.1 - 2.8 | Calculation Engine (7 engineering domains) |
| 3 | 3.1 - 3.3 | Services (search, charts, reports) |
| 4 | 4.1 - 4.7 | User Interface (NiceGUI pages) |
| 5 | 5.1 - 5.3 | Integration & Polish |
| 6 | 6.1 - 6.3 | Packaging & Documentation |

**Total Tasks:** ~120 individual items

---

## Quick Reference: Running the Project

```bash
# Development
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py

# Desktop build
pyinstaller engineering-calcs.spec

# Run tests
pytest tests/
```

---

## Notes

- Start with Phase 1 completely before moving on
- Each calculation should have a test with known values
- Keep UI simple initially; add features incrementally
- Commit after each completed task
- Track issues/improvements as they arise
