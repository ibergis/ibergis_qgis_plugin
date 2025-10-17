# IberGIS - QGIS Plugin

[![Python flake8](https://github.com/ibergis/ibergis_qgis_plugin/actions/workflows/pythonflake8.yml/badge.svg)](https://github.com/ibergis/ibergis_qgis_plugin/actions/workflows/pythonflake8.yml)
[![QGIS](https://img.shields.io/badge/QGIS-3.34+-green.svg?logo=qgis)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python)](https://www.python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A QGIS plugin for advanced water management and hydraulic modeling in urban environments based on the integration of EPA SWMM (1D) and Iber (2D) models for flood modelling and urban drainage analysis.

## ✨ Features

- **Advanced Water Network Management**: Plan and control water supply networks efficiently
- **Hydraulic Modeling Integration**: Native EPA SWMM5 support for urban drainage simulation
- **Mesh Generation**: Automatic mesh generation for finite element analysis
- **Flood Modeling**: Comprehensive flood analysis and visualization tools
- **Multi-language Support**: Available in English, Spanish (ES), and Spanish (CR)
- **Cross-platform**: Works on Windows and Linux systems

## 📋 Requirements

### System Requirements
- **QGIS 3.x**: Geographic Information System software
- **Python 3.9+**: Required for plugin functionality
- **matplotlib**: Python library for plotting (may need manual installation for non-standalone QGIS)

### Platform-Specific Requirements

**Windows**: All required packages are bundled with the plugin. If you have gmsh, pandamesh, geopandas, or triangle packages already installed in your QGIS Python instance, you may have to uninstall them first.
- Open Python console on QGIS
- Type `!pip uninstall gmsh pandamesh geopandas triangle`

**Linux**: Install Python dependencies manually:
```bash
pip install -r requirements.txt
```

## 🚀 Installation

### Method 1: QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Navigate to `Plugins` → `Manage and Install Plugins`
3. Search for "IberGIS"
4. Click `Install Plugin`

### Method 2: Manual Installation
1. Download the latest release from the repository
2. Extract the plugin to your QGIS plugins directory:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in `Plugins` → `Manage and Install Plugins`

## 🧪 Testing

### Sample Data
The plugin includes comprehensive sample datasets located in the `resources/example/` directory:
- **Sample GPKG**: Geospatial database with example geometries
- **Full Project Example**: Complete results calculated from the sample GPKG
- **SWMM Input Files**: Pre-configured `.inp` files for testing
- **Mesh Examples**: Sample mesh data for validation
- **QGIS Projects**: Ready-to-use project files

### Running Tests
1. Install flake8:
   ```bash
   pip install flake8
   ```
2. Run flake8 from the plugin root directory:
   ```bash
   flake8 .
   ```

## 🔍 Troubleshooting

### Mesh Creation Issues
If you encounter problems creating a mesh, try uninstalling potentially conflicting packages from the OSGeo shell (you may need to run with administrator privileges):

**Windows**:
1. Open OSGeo4W Shell (`osgeo4w.bat`)
2. Run:
   ```bash
   pip uninstall gmsh pandamesh geopandas triangle
   ```

**Linux**:
1. Open your OSGeo shell
2. Run:
   ```bash
   pip uninstall gmsh pandamesh geopandas triangle
   ```

After uninstalling them, restart QGIS. The plugin will use its bundled versions of these packages.

### IberGIS Simulation Issues
If you encounter problems running simulations, use the **Check Project** button to validate your project. Review any errors or warnings that appear, as they typically indicate configuration or data model issues that need to be addressed before running the simulation.

## 📚 Documentation

- **Wiki**: Comprehensive documentation available at [GitHub Wiki](https://drain-iber.github.io/testing/en/docs/)
- **FAQ**: Common questions and troubleshooting at [GitHub FAQ](https://github.com/ibergis/ibergis_qgis_plugin/wiki/FAQs)

## 🌍 Translations

IberGIS includes a comprehensive multi-language system with AI-powered translation support. The plugin currently supports three language variants:

### Available Languages

| Language | Code | Completion | Strings |
|----------|------|------------|---------|
| **English (US)** | `en_US` | 100% | 2,781 |
| **Spanish (Spain)** | `es_Es` | ~99.6% | 2,769 |
| **Spanish (Costa Rica)** | `es_Cr` | ~99.6% | 2,769 |

### How It Works

The translation system operates across three main components:

1. **Python Code Messages**: Translatable strings in the Python source code are extracted and stored in Qt `.ts` (Translation Source) files located in the `i18n/` directory. These files are then compiled into `.qm` (Qt Message) binary files that QGIS loads at runtime.

2. **UI Interface Elements**: User interface elements defined in `.ui` files (Qt Designer forms) are also included in the translation files. This ensures that dialogs, buttons, labels, and menus are translated consistently.

3. **Database Content**: The plugin uses a GeoPackage database (`core/i18n/ibergis_i18n.gpkg`) to store translations for dynamic content like tooltips, field names, and form configurations. This allows for runtime translation of database-driven UI elements.

### Translation Workflow

The translation process is managed through specialized tools in the `core/i18n/` directory:

- **`i18n_generator.py`**: Generates `.ts` and `.qm` translation files from the codebase and databases
- **`i18n_manager.py`**: Manages translation databases and syncs translations across components
- **`schema_i18n_update.py`**: Updates project database schemas with translated content

Admin users can access translation management tools through the plugin's admin interface to generate new translations or update existing ones for additional languages.

## 🔧 Development

### Project Structure
```
ibergis_qgis_plugin/
├── core/               # Core functionality
│   ├── ui/             # User interface components
│   └── processing/     # Processing algorithms
├── resources/          # Sample data and templates
├── packages/           # Bundled dependencies
└── dbmodel/            # Database schemas and functions
```

### Versioning
- **Major**: New architecture with significant changes (breaking compatibility)
- **Minor**: New features and bug fixes (backward compatible)
- **Patch**: Bug fixes and minor improvements (backward compatible)

## 📦 Third-Party Libraries

IberGIS uses the following third-party libraries:

- **swmm-api**: [swmm-api GitLab](https://gitlab.com/markuspichler/swmm_api)
  swmm-api provides a Pythonic interface to the EPA SWMM5 software, enabling advanced scripting, simulation control, and access to simulation results.
  The license and further details can be found in the [LICENSE](./packages/swmm_api/LICENSE) or in their [repository](https://gitlab.com/markuspichler/swmm_api/-/blob/master/LICENSE).

- **tqdm**: [tqdm GitHub](https://github.com/tqdm/tqdm)
  tqdm is a fast, extensible progress bar library for Python, supporting console, GUI, and notebook environments.
  The tqdm license can be viewed in the [LICENSE](./packages/tqdm/LICENCE) or in their [repository](https://github.com/tqdm/tqdm/blob/master/LICENCE).

- **gmsh**: [gmsh GitLab](https://gitlab.onelab.info/gmsh/gmsh/-/tree/gmsh_4_11_1?ref_type=tags)
  gmsh is an automatic three-dimensional finite element mesh generator with built-in pre- and post-processing facilities.
  The gmsh license can be viewed in the [LICENSE](./packages/gmsh/LICENCE) or in their [repository](https://gitlab.onelab.info/gmsh/gmsh/-/blob/gmsh_4_11_1/LICENSE.txt?ref_type=tags).

- **openpyxl**: [openpyxl Github](https://foss.heptapod.net/openpyxl/openpyxl/-/tree/3.1.2?ref_type=tags)
  openpyxl is a Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files.
  The openpyxl license can be viewed in the [LICENSE](./packages/openpyxl/LICENCE) or in their [repository](https://foss.heptapod.net/openpyxl/openpyxl/-/blob/3.1.2/LICENCE.rst?ref_type=tags).

- **pandamesh**: [pandamesh Github](https://github.com/Deltares/pandamesh/tree/main)
  pandamesh translates geospatial vector data (points, lines, or polygons) to unstructured meshes.
  The pandamesh license can be viewed in the [LICENSE](./packages/pandamesh/LICENCE) or in their [repository](https://github.com/Deltares/pandamesh/blob/main/LICENSE).

- **xlsxwriter**: [xlsxwriter Github](https://github.com/jmcnamara/XlsxWriter/tree/RELEASE_3.1.9)
  xlsxwriter is a Python module for writing files in the Excel 2007+ XLSX file format.
  The xlsxwriter license can be viewed in the [LICENSE](./packages/xlsxwriter/LICENCE) or in their [repository](https://github.com/jmcnamara/XlsxWriter/blob/RELEASE_3.1.9/LICENSE.txt).

- **geopandas**: [geopandas GitHub](https://github.com/geopandas/geopandas)
  geopandas extends the datatypes used by pandas to allow spatial operations on geometric types.
  The geopandas license can be viewed in the [LICENSE](./packages/geopandas/LICENSE.txt) or in their [repository](https://github.com/geopandas/geopandas/blob/main/LICENSE.txt).

## 📄 License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See LICENSE file for more information.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## 💬 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check our [Wiki](https://drain-iber.github.io/testing/en/docs/index.html) for detailed guides
- **Community**: Join discussions in our project forums

---

**Made with ❤️ for the water management community**
