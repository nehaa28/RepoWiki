# Open Source Dependencies Verification

All dependencies used in ProjWiki are open source and properly licensed:

## Core Dependencies

1. **requests** (Apache 2.0)
   - HTTP client for SAP AI Core API calls
   - https://github.com/psf/requests

2. **networkx** (BSD 3-Clause)
   - Graph analysis for dependency mapping
   - https://github.com/networkx/networkx

3. **Jinja2** (BSD 3-Clause)
   - HTML template engine
   - https://github.com/pallets/jinja

## CLI & Display

4. **click** (BSD 3-Clause)
   - Command-line interface framework
   - https://github.com/pallets/click

5. **rich** (MIT)
   - Terminal formatting and progress bars
   - https://github.com/Textualize/rich

## Utilities

6. **pyyaml** (MIT)
   - YAML parsing
   - https://github.com/yaml/pyyaml

## Built-in Python Modules (No External Dependencies)

- **ast** - Abstract Syntax Tree parsing (Python built-in)
- **pathlib** - Path manipulation (Python built-in)
- **json** - JSON handling (Python built-in)

## Diagram Generation

- **PlantUML** - Text-based diagram format (no library needed)
  - Saves .puml text files
  - Optional rendering with PlantUML jar (GPL/Apache dual license)
  - Can also use online renderer: http://www.plantuml.com/plantuml/

## AI Integration

- **SAP AI Core** - REST API integration
  - Uses standard OAuth2 authentication
  - No proprietary SDK required
  - Uses only open source HTTP client (requests)

## Summary

✅ **All dependencies are open source**
✅ **No proprietary or closed-source libraries**
✅ **All licenses are permissive (BSD, MIT, Apache)**
✅ **Total dependencies: 6 PyPI packages + Python built-ins**
