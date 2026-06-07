# QGIS AI Agent

A natural language assistant plugin for QGIS that executes spatial analysis operations through conversational commands.

---

## Overview

QGIS AI Agent is a QGIS plugin that lets users perform spatial analysis by typing natural language requests instead of navigating menus, locating algorithms, or writing PyQGIS code by hand. A chat panel inside QGIS interprets each request, decides which spatial operations to run against the currently loaded layers, executes them through the standard QGIS and Processing APIs, and reports the result inline.

The plugin was built to reduce the friction between an analytical question ("how much agricultural land falls inside the flood mask?") and the sequence of clicks, parameter dialogs, and intermediate layers required to answer it. It is aimed at GIS analysts, students, and researchers who already understand the underlying spatial concepts but want a faster way to express common workflows.

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

### Getting an API key

1. Open [https://openrouter.ai](https://openrouter.ai) in a browser.
2. Click **Sign Up** and complete email verification.
3. Open your profile menu and select **API Keys**.
4. Click **New Key**, give it a name such as `qgis-ai-agent`, and click **Create**.
5. Copy the generated key. It is shown only once.

### Setting the API key

1. Click the QGIS AI Agent toolbar button to open the chat panel.
2. Click the settings button in the panel header.
3. Paste the API key into the prompt and click **OK**.

The key is stored in QGIS settings under `qgis_ai_agent/api_key` and is not transmitted anywhere except to the OpenRouter endpoint when answering a request.

---

## Usage

Type a request into the chat panel and press **Enter**. The agent inspects the loaded layers, calls the relevant operations, and replies with a summary of what it did.

### Example commands

Layer management:

- List all layers in the project
- Zoom to the layer named roads
- Hide the layer called streetlights
- Load the file C:\data\boundaries.gpkg

Spatial analysis:

- Create a 500 metre buffer around schools
- Clip parcels by the city boundary
- Compute the spatial join between hospitals and districts
- Dissolve land_use by the column category

Raster operations:

- Calculate NDVI from the red and nir bands
- Compute slope from dem_30m
- Create a hillshade from dem_30m
- Calculate zonal statistics of elevation within watersheds

Styling:

- Apply categorized symbology on land_use by class
- Apply a graduated style on parcels by area
- Change the colour of roads to dark grey

Export:

- Export the buffered layer to GeoJSON at C:\out\buffer.geojson
- Save the attribute table of parcels as CSV
- Export the current map view as a PNG

---

## Supported operations

### Layer management

| Tool | Description |
|------|-------------|
| `get_layers` | List all layers in the current project. |
| `get_attributes` | Return field names of a layer. |
| `get_feature_count` | Return the feature count of a layer. |
| `get_crs` | Return the CRS authid, description, and units of a layer. |
| `add_layer_from_path` | Load a vector or raster file into the project. |
| `remove_layer` | Remove a layer from the project. |
| `rename_layer` | Rename a layer. |
| `toggle_visibility` | Show or hide a layer in the layer tree. |
| `zoom_to_layer` | Zoom the canvas to a layer's extent. |
| `zoom_to_feature` | Zoom the canvas to a single feature by id. |
| `open_attribute_table` | Open the attribute table dialog for a layer. |

### Selection and filtering

| Tool | Description |
|------|-------------|
| `run_query` | Apply a subset string filter using a QGIS expression. |
| `filter_features` | Convenience wrapper around `run_query`. |
| `highlight_features` | Select features that match a QGIS expression. |
| `select_by_attribute` | Select features where a field equals a value. |

### Vector analysis

| Tool | Description |
|------|-------------|
| `buffer_analysis` | Create a buffer around features. |
| `clip_layer` | Clip a vector layer by a mask layer. |
| `intersect_layers` | Geometric intersection of two layers. |
| `union_layers` | Geometric union of two layers. |
| `dissolve_layer` | Dissolve features, optionally by field. |
| `merge_layers` | Merge multiple vector layers into one. |
| `spatial_join` | Join attributes by spatial intersection. |
| `centroid` | Create a centroid layer from a polygon layer. |
| `reproject_layer` | Reproject a layer to a target CRS. |
| `fix_geometries` | Repair invalid geometries. |

### Field calculation

| Tool | Description |
|------|-------------|
| `field_calculator` | Add a field and populate it with a QGIS expression. |
| `calculate_area` | Compute area into an `area` field. |
| `calculate_length` | Compute length into a `length` field. |

### Raster analysis

| Tool | Description |
|------|-------------|
| `calculate_ndvi` | NDVI from red and NIR bands. |
| `calculate_ndwi` | NDWI from green and NIR bands. |
| `calculate_ndre` | NDRE from red edge and NIR bands. |
| `hillshade` | Hillshade from a DEM. |
| `slope_analysis` | Slope from a DEM. |
| `aspect_analysis` | Aspect from a DEM. |
| `zonal_statistics` | Zonal statistics of a raster within polygons. |
| `raster_clip` | Clip a raster by a vector mask. |
| `pan_sharpening` | Pan sharpen a multispectral raster with a panchromatic raster. |

### Image processing

| Tool | Description |
|------|-------------|
| `unsupervised_classification` | K-means classification of a raster. |
| `supervised_classification` | Supervised classification using a training layer. |
| `histogram_equalization` | Per-band histogram equalization. |
| `mosaic_rasters` | Merge multiple rasters into one. |
| `band_composite` | Create an RGB composite from selected bands. |

### Symbology

| Tool | Description |
|------|-------------|
| `apply_categorized_style` | Categorized renderer by unique field values. |
| `apply_graduated_style` | Graduated renderer (quantile, 5 classes). |
| `apply_heatmap_style` | Heatmap renderer for point layers. |
| `change_layer_color` | Set a layer's symbol colour from a hex string. |

### Export

| Tool | Description |
|------|-------------|
| `export_layer` | Export a vector layer to GeoJSON, Shapefile, GeoPackage, KML, or GML. |
| `export_to_csv` | Export a layer to CSV with geometry as WKT. |
| `export_attribute_table` | Export the full attribute table to CSV. |
| `generate_csv` | Export a layer to CSV (Desktop-friendly wrapper). |
| `generate_map_image` | Export the current map canvas as PNG. |
| `print_map` | Export the canvas as PNG, JPG, BMP, or PDF. |
| `generate_report` | Generate a Word (.docx) report on the user's Desktop. |

### Code execution

| Tool | Description |
|------|-------------|
| `execute_qgis_code` | Execute arbitrary PyQGIS code when no dedicated tool applies. |

---

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make focused changes and verify that the plugin still loads in QGIS.
4. Open a pull request describing the change and any testing performed.

For bug reports and feature requests, please use the issue tracker:
[https://github.com/kodeezabdullah/qgis-ai-agent/issues](https://github.com/kodeezabdullah/qgis-ai-agent/issues)

---

## License

This project is released under the GNU General Public License v2.0. See `qgis_ai_agent/LICENSE` for the full text.

---

## Author

kodeezabdullah
Geoinformatics Engineering, NUST IGIS
