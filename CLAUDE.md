```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

## Project Overview

Everify (E-Verify) is an enterprise-grade web verification automation system designed for automated entity research, web scraping, screenshot capture, and professional report generation with time-watermarks. It supports both CLI and web UI modes with full feature parity.

## Key Commands

### Development Environment
```bash
# Install dependencies (requires uv package manager)
uv sync

# Install Playwright browser drivers
uv run python -m playwright install

# Run the application
uv run everify                    # Unified entry point with mode selection
uv run everify-web                # Web UI mode (direct)
uv run everify-cli                # CLI mode (direct)
uv run python src/everify/entrypoints/entrypoints.py --mode=web  # Web via entrypoint
uv run python src/everify/entrypoints/entrypoints.py --mode=cli  # CLI via entrypoint
uv run python web/app.py            # Flask app directly (backward compatibility)

# Run tests
uv run python -m pytest tests/ -v
```

## Project Structure

```
Everify-project/
├── src/everify/                # Core application source
│   ├── main.py                 # CLI application entry point
│   ├── web.py                  # Web application entry point (Flask app)
│   ├── entrypoints/            # Unified entry point module
│   │   ├── entrypoints.py      # Main entry point with mode selection
│   │   └── __init__.py         # Package configuration
│   ├── common/                 # Common utilities (previously utils/)
│   │   └── file.py             # File operations utility
│   ├── core/                   # Business logic layer
│   │   ├── services/           # Core services (5 main services)
│   │   │   ├── entity_manager.py        # Entity input, validation, batch loading
│   │   │   ├── template_manager.py      # Loads default + user templates
│   │   │   ├── url_generator.py         # Creates concrete URLs from templates
│   │   │   ├── verify_service.py        # Async browser automation
│   │   │   └── report_generator.py      # Generates watermarked Word reports
│   │   ├── operations/         # Operation patterns (command pattern)
│   │   │   ├── base_operation.py           # Base operation class
│   │   │   ├── auto_verify_operation.py    # Auto-verification operations
│   │   │   ├── manual_screenshot_operation.py  # Manual screenshot insertion
│   │   │   ├── search_engine_query_operation.py  # Search engine queries
│   │   │   └── operation_factory.py        # Operation factory
│   │   ├── base/               # Low-level engines
│   │   │   ├── browser.py   # Playwright-powered browser automation
│   │   │   ├── document.py  # Word document generation (python-docx)
│   │   │   └── image.py     # Pillow-based image processing
│   │   ├── utils/              # Core utilities and config
│   │   │   ├── config.py    # AppConfig and VerifyTemplate
│   │   │   └── logger.py    # Logging setup
│   │   └── data/               # Default templates
│   │       └── templates.json  # Pre-configured verification templates
│   └── __init__.py             # Package configuration
├── web/                        # Web frontend resources (backward compatibility)
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── integrity_check.html  # Integrity check page
│   │   ├── bribery_check.html    # Bribery check page
│   │   └── admin_templates.html  # Template management page
│   ├── static/                 # Static assets (css, js)
│   └── app.py                  # Backward compatibility file (imports from everify.web)
├── tests/                      # Test suite (currently empty)
├── output/                     # Runtime output directory
│   ├── reports/                # Generated Word reports
│   ├── screenshots/            # Captured screenshots
│   ├── temp/                   # Temporary files
│   └── logs/                   # Log files
├── start_app.bat               # Easy Windows startup script
├── pyproject.toml              # Project configuration
├── uv.lock                     # uv dependency lock file
├── user_templates.json         # User-customized verification templates
└── README.md                   # Full documentation
```

## Core Services

### Service Layer (`core/services/`)
- `entity_manager.py`: Collects, manages, and validates entity information from user input or files
- `template_manager.py`: Loads default + user templates, interactive template selection, template management
- `url_generator.py`: Creates concrete URLs from templates and entity names
- `verify_service.py`: Async browser automation with concurrent verification using Playwright
- `report_generator.py`: Generates watermarked Word reports with screenshots using python-docx

### Base Engines (`core/base/`)
- `browser.py`: Playwright-powered browser automation with headless support
- `document.py`: Word document generation with formatting and sectioning
- `image.py`: Pillow-based image processing and watermarking

## Data Models & Operations (`core/operations/`)
Implements command pattern for different operation types:
- `base_operation.py`: Base operation class with execute() method
- `auto_verify_operation.py`: Auto-verification operations
- `manual_screenshot_operation.py`: Manual screenshot insertion
- `search_engine_query_operation.py`: Search engine queries
- `operation_factory.py`: Operation factory for creating operation instances

## Common Utilities (`common/`)
- `file.py`: General file operations utility (clean_filename, validate_url, etc.)

## Configuration

### Environment Variables (.env)
```
# Browser configuration
BROWSER_HEADLESS=True
BROWSER_VIEWPORT=1920x1080
BROWSER_TIMEOUT=30000
BROWSER_SLOW_MO=0

# Watermark configuration
WATERMARK_TEXT=%Y-%m-%d %H:%M:%S
WATERMARK_FONT_SIZE=24
WATERMARK_COLOR=#808080
WATERMARK_OPACITY=0.5

# Output path configuration
OUTPUT_DIR=output
REPORTS_DIR=output/reports
SCREENSHOTS_DIR=output/screenshots
TEMP_DIR=output/temp

# Report configuration
REPORT_TITLE=诚信核查报告
REPORT_FOOTER=Everify 网页核查自动化系统
```

### Verification Templates
Templates are stored in `src/everify/core/data/templates.json` (default) and `user_templates.json` (custom). Each template has:
- `name`: Template name
- `description`: Template description
- `url_pattern`: URL with `{}` as entity name placeholder
- `category`: Classification (automated/manual/custom)
- `InsertContext`: Report section title

## Web UI Features

The Flask web application (http://127.0.0.1:5000) provides:
- **Entity Input**: Single or bulk entity entry
- **Template Management**: Add/Edit/Delete verification templates
- **Verification Execution**: Run automated checks with progress tracking
- **Report Preview**: Download and preview generated reports
- **Search Integration**: Search engine queries for additional context

## API Endpoints

```
/api/entities/validate          # POST: Validate entity list
/api/entities/save             # POST: Save entities to session
/api/templates                 # GET: Get all templates
/api/templates/categories      # GET: Get template categories
/api/templates/user            # POST: Add user template
/api/templates/user/<name>     # PUT: Update user template
/api/templates/user/<name>     # DELETE: Delete user template
/api/verify/start              # POST: Start automated verification
/api/bribery-verify/start      # POST: Start bribery check
/api/manual-verify/start       # POST: Start manual verification
/api/folder/open               # POST: Open report folder
```

## Web Application Flow

```
Integrity Check Workflow:
┌─────────────────────────────────────────────────────────┐
│ Step 1: Entity Input                                    │
│ - Enter entities (single or bulk)                       │
│ - Real-time validation                                 │
│ - Store in session['entities']                          │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│ Step 2: Template Selection                              │
│ - Load and display all templates                        │
│ - Filter by category                                    │
│ - Store selected in session['selected_templates']       │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│ Step 3: Automated Verification                          │
│ - Create AutoVerifyOperation via OperationFactory       │
│ - Execute async verification with Playwright            │
│ - Generate reports with screenshots                     │
│ - Store report paths in session['report_paths']         │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│ Step 4: Manual Verification                              │
│ - Insert manual screenshots into existing reports       │
│ - Process images from screenshots directory             │
│ - Update reports with manual verification content       │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│ Step 5: Results & Download                              │
│ - Display generated reports                             │
│ - Download individual reports                            │
│ - Open report folder                                    │
└─────────────────────────────────────────────────────────┘
```

## Testing Structure

Tests are located in `tests/` directory:
- `test_template_manager.py`: Tests for template management (load, save, delete, categories)

## Technical Stack

| Category               | Technologies                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| Core Language           | Python 3.10.19+                                                           |
| Browser Automation     | Playwright                                                                 |
| Document Processing   | python-docx                                                                 |
| Image Processing      | Pillow (PIL)                                                               |
| Data Validation       | Pydantic                                                                   |
| Web Framework         | Flask                                                                      |
| Package Manager       | uv                                                                         |
| Concurrency           | asyncio                                                                     |
| Configuration         | python-dotenv                                                               |

## Key Features

✅ **Dual Interface**: Command-line and web UI with full feature parity
✅ **Async Automation**: Concurrent web scraping with Playwright
✅ **Template-Driven**: Configurable verification templates
✅ **Watermarked Reports**: Professional DOCX reports with timestamps
✅ **Flexible Input**: Single entity or bulk batch processing
✅ **Search Integration**: Automated search engine queries
✅ **Customizable Templates**: Add/edit/delete user verification templates
✅ **Cross-Platform**: Windows, macOS, Linux compatible

## Import Path Conventions

After the directory reorganization, please use the following import paths:

```python
# Common utilities (previously from utils.file)
from everify.common.file import clean_filename, validate_url

# Core operations (previously from core.models)
from everify.core.operations.operation_factory import OperationFactory
from everify.core.operations.base_operation import OperationResult

# Core services
from everify.core.services.entity_manager import EntityManager
from everify.core.services.template_manager import TemplateManager

# Core utilities
from everify.core.utils.config import AppConfig, VerifyTemplate
from everify.core.utils import logger

# Base engines
from everify.core.base.browser import PlaywrightBrowser
from everify.core.base.document import DocxDocumentEngine
from everify.core.base.image import PillowImageEngine
```

## Program Entry Points

Everify provides a unified entry point architecture with mode selection:

### Primary Entry Points (Package Scripts)
- **`everify`**: Unified entry point with interactive mode selection
  - Module: `everify.entrypoints.entrypoints:main`
  - File: `src/everify/entrypoints/entrypoints.py`
  - Provides mode selection (Web UI or CLI) on startup
  - Supports command-line arguments: `--mode`, `--port`, `--host`, `--verbose`

- **`everify-web`**: Direct Web interface mode
  - Module: `everify.entrypoints.entrypoints:main` (with mode=web)
  - File: `src/everify/entrypoints/entrypoints.py`
  - Launches Flask web server on http://localhost:5000
  - Automatically opens browser on startup

- **`everify-cli`**: Direct Command-line interface (CLI) mode
  - Module: `everify.entrypoints.entrypoints:main` (with mode=cli)
  - File: `src/everify/entrypoints/entrypoints.py`
  - Provides interactive command-line workflow with menu-based operations

### Secondary Entry Points
- **`web/app.py`**: Backward compatibility entry point
  - Simply imports and delegates to `everify.web`
  - Maintained for existing users and documentation

### Importing as Library
```python
# Import the Flask app for embedding or testing
from everify.web import app

# Import CLI main function for programmatic invocation
from everify.main import main

# Import unified entry point
from everify.entrypoints.entrypoints import main
```

## Recent Changes

### Directory Reorganization
- `src/everify/utils/` → `src/everify/common/` (to avoid confusion with `core/utils/`)
- `src/everify/core/models/` → `src/everify/core/operations/` (more accurately reflects command pattern implementation)

### Entry Point Organization
- Web application entry moved from `web/app.py` to `src/everify/web.py`
- `web/app.py` maintained as backward compatibility wrapper
- `pyproject.toml` updated with correct script references
- All entry points now consistently located in `src/everify/` package

## Key Classes and Methods

### EntityManager (entity_manager.py)
```python
class EntityManager:
    @staticmethod
    def get_entities_from_input() -> List[str]:
        """Get entities from command-line input (enter # to stop)"""

    @staticmethod
    def validate_entities(entities: List[str]) -> List[str]:
        """Validate and clean entity list"""

    @staticmethod
    def load_entities_from_file(file_path: str) -> List[str]:
        """Load entities from a text file"""
```

### TemplateManager (template_manager.py)
```python
class TemplateManager:
    def load_templates(self) -> Dict[str, VerifyTemplate]:
        """Load all templates (default + user)"""

    def save_user_template(self, name: str, template: VerifyTemplate) -> bool:
        """Save a user-customized template"""

    def delete_user_template(self, name: str) -> bool:
        """Delete a user-customized template"""

    def get_templates_by_category(self, category: str) -> Dict[str, VerifyTemplate]:
        """Get templates by category"""

    def select_templates_interactively(self) -> Dict[str, VerifyTemplate]:
        """Interactive template selection"""

    def search_templates(self, keyword: str) -> Dict[str, VerifyTemplate]:
        """Search templates by keyword"""
```

### VerifyTemplate (config.py)
```python
class VerifyTemplate(BaseModel):
    name: str
    description: str
    url_pattern: str
    category: str
    InsertContext: str
```
