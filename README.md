# IberGIS - QGIS Plugin

[![Python flake8](https://github.com/ibergis/ibergis_qgis_plugin/actions/workflows/pythonflake8.yml/badge.svg)](https://github.com/ibergis/ibergis_qgis_plugin/actions/workflows/pythonflake8.yml)
[![QGIS](https://img.shields.io/badge/QGIS-3.34+-green.svg?logo=qgis)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python)](https://www.python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A comprehensive QGIS plugin for advanced water management and hydraulic modeling, providing seamless integration with **EPA SWMM** networks and **Iber** sophisticated mesh generation capabilities for flood modeling and urban drainage analysis.

## ✨ Features

- **Advanced Water Network Management**: Plan and control water supply networks efficiently
- **Hydraulic Modeling Integration**: Native EPA SWMM5 support for urban drainage simulation
- **Mesh Generation**: Automatic mesh generation for finite element analysis
- **Flood Modeling**: Comprehensive flood analysis and visualization tools
- **Multi-language Support**: Available in English, Spanish (CR), and Spanish (ES)
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

## 📚 Documentation

- **Wiki**: Comprehensive documentation available at [GitHub Wiki](https://drain-iber.github.io/testing/en/docs/)
- **FAQ**: Common questions and troubleshooting at [GitHub FAQ](https://github.com/ibergis/ibergis_qgis_plugin/wiki/FAQs)
- **API Reference**: Developer documentation for extending functionality

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

- **rasterio**: [rasterio GitHub](https://github.com/rasterio/rasterio)
  Rasterio reads and writes geospatial raster data.
  The rasterio license can be viewed in the [LICENSE](./packages/rasterio/LICENSE.txt) or in their [repository](https://github.com/rasterio/rasterio/blob/main/LICENSE.txt).

- **xarray**: [xarray GitHub](https://github.com/geopandas/geopandas)
  xarray is an open source project and Python package that makes working with labelled multi-dimensional arrays simple, efficient, and fun.
  The geopandas license can be viewed in the [LICENSE](./packages/xarray/LICENSE) or in their [repository](https://github.com/pydata/xarray/blob/main/LICENSE).

- **rioxarray**: [rioxarray GitHub](https://github.com/corteva/rioxarray)
  rioxarray is an extension of rasterio and xarray.
  The rioxarray license can be viewed in the [LICENSE](./packages/rioxarray/LICENSE) or in their [repository](https://github.com/corteva/rioxarray/blob/master/LICENSE).

## 📄 License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See LICENSE file for more information.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## 💬 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check our [Wiki](https://github.com/Giswater/giswater_dbmodel/wiki) for detailed guides
- **Community**: Join discussions in our project forums

---

**Made with ❤️ for the water management community**
