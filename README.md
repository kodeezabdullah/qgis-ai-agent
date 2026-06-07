# QGIS AI Agent

A natural language assistant plugin for QGIS that executes spatial analysis operations through conversational commands.

---

## Overview

QGIS AI Agent is a QGIS plugin that lets users perform spatial analysis by typing natural language requests instead of navigating menus, locating algorithms, or writing PyQGIS code by hand. A chat panel inside QGIS interprets each request, decides which spatial operations to run against the currently loaded layers, executes them through the standard QGIS and Processing APIs, and reports the result inline.

The plugin was built to reduce the friction between an analytical question and the sequence of clicks, parameter dialogs, and intermediate layers required to answer it. It is aimed at GIS analysts, students, and researchers who already understand the underlying spatial concepts but want a faster way to express common workflows.

The implementation is intentionally extensible: every supported operation is a single Python function registered with a schema, and the agent can also write and execute its own PyQGIS code when no registered tool matches the request.

---

## Features

- More than 50 built-in QGIS operations
- Natural language to spatial query conversion
- Vector and raster analysis
- Image processing including NDVI, NDWI, NDRE, hillshade, slope, aspect, and unsupervised classification
- File reading for PDF, Word, CSV, and Excel attachments
- Report and CSV generation
- Conversation memory across messages within a session
- Multi-model fallback chain using free OpenRouter models
- Self-executing PyQGIS code for operations not covered by a dedicated tool
- Dockable chat panel built on QWebEngineView

---

## Requirements

- QGIS 3.0 or higher
- OpenRouter API key (free tier available)
- Internet connection

---

## Installation

### From source

1. Download or clone this repository.
2. Copy the `qgis_ai_agent` folder into your QGIS plugins directory:
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS.
4. Open **Plugins -> Manage and Install Plugins -> Installed** and enable **QGIS AI Agent**.

### Dependencies

The plugin works out of the box for spatial operations. Optional file features (PDF, Word, Excel, CSV reading and Word report generation) require additional packages. Install them once from the **OSGeo4W Shell** (Windows) or your QGIS Python environment:

```
python -m pip install pypdf python-docx openpyxl pandas
```

---

## Configuration

### Getting a Free API Key

1. Go to https://openrouter.ai
2. Click Sign Up and create an account
3. Navigate to API Keys section
4. Click New Key, name it "qgis-ai-agent"
5. Copy the generated key immediately

### Setting the API Key

1. Open QGIS AI Agent from the Plugins menu or toolbar
2. Click the Settings icon in the top right of the panel
3. Paste your OpenRouter API key
4. Click OK

## Usage

Type natural language commands in the input box. Examples:

### Layer Management
- "List all layers in the project"
- "Add layer from C:/data/roads.shp"
- "Remove the buffer layer"
- "Zoom to the countries layer"

### Spatial Analysis
- "Create a 500m buffer around the roads layer"
- "Clip the buildings layer by the study area"
- "Calculate area of all features in the parcels layer"
- "Filter features where population is greater than 1000"

### Raster Analysis
- "Calculate NDVI using red and NIR bands"
- "Generate hillshade from the DEM layer"
- "Calculate slope from the elevation layer"

### Styling
- "Apply categorized style to countries layer by name field"
- "Change the roads layer color to red"
- "Make fill transparent with 2px blue outline"

### Export
- "Export the results layer to GeoJSON"
- "Generate a Word report about the countries layer"
- "Export attribute table to CSV"

## Supported Models

The plugin uses OpenRouter API with automatic fallback:

| Model | Type |
|-------|------|
| moonshotai/kimi-k2.6 | Free |
| openai/gpt-oss-120b | Free |
| openai/gpt-oss-20b | Free |
| meta-llama/llama-3.3-70b-instruct | Free |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

GPL-2.0. See LICENSE file for details.

## Author

kodeezabdullah  
Geoinformatics Engineering, NUST IGIS
