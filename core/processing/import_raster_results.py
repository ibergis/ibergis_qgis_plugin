"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsLayerTreeLayer,
    QgsProject,
    QgsRasterLayer,
    QgsLayerTreeGroup,
    QgsProcessingContext,
    QgsRasterLayerTemporalProperties,
    Qgis,
    QgsDateTimeRange,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsInterval,
    QgsTemporalNavigationObject,
    QgsMapLayerStyle,
    QgsProcessingParameterBoolean
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QTimeZone, QTime, QDate
from qgis.PyQt.QtGui import QColor, QAction
from ...core.utils import Feedback
from typing import Optional
from datetime import datetime
from ... import global_vars
import os
import numpy as np
from ...lib.tools_gpkgdao import DrGpkgDao
from swmm_api import read_inp_file
import glob
import re
from ...lib import tools_qgis


class ImportRasterResults(QgsProcessingAlgorithm):
    """
    Class to import raster results from a model results folder.
    """

    # Layer params
    layers: list[QgsRasterLayer] = []
    layers_group: Optional[QgsLayerTreeGroup] = None

    # Temporal params
    start_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_date: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_time: Optional[datetime] = None

    iface = global_vars.iface
    dao: Optional[DrGpkgDao] = None
    from_inp: bool = True
    detected_files: list[str] = []
    folder_results_path: Optional[str] = None
    result_options: dict = {}

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        self.folder_results_path = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{tools_qgis.get_project_variable('project_results_folder')}")
        if self.folder_results_path is None or not os.path.exists(self.folder_results_path) or not os.path.isdir(self.folder_results_path):
            return
        # Auto-detect all NetCDF files
        self.detected_files = self.detect_netcdf_files(f'{self.folder_results_path}{os.sep}IberGisResults')
        if len(self.detected_files) == 0:
            return
        for file in self.detected_files:
            file_name = self.transform_layer_name(file)
            self.addParameter(
                QgsProcessingParameterBoolean(
                    file,
                    self.tr(f'Import *{file_name}* NetCDF file'),
                    defaultValue=True
                )
            )

    def processAlgorithm(self, parameters, context: QgsProcessingContext, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        self.iface = global_vars.iface
        self.layers = []
        self.dao = global_vars.gpkg_dao_data.clone()
        self.from_inp: bool = True

        # Apply parameters
        filtered_files = []
        for file in self.detected_files:
            if self.parameterAsBoolean(parameters, file, context):
                filtered_files.append(file)
        self.detected_files = filtered_files

        # reading geodata
        feedback.setProgressText(self.tr('Reading folder...'))
        feedback.setProgress(1)

        folder_netcdf: str = f'{self.folder_results_path}{os.sep}IberGisResults'
        inp_file: str = f'{self.folder_results_path}{os.sep}Iber_SWMM.inp'

        # Check if folder is valid and if NetCDF and INP files exist
        if self.folder_results_path is not None and os.path.exists(self.folder_results_path) and os.path.isdir(self.folder_results_path):
            if os.path.exists(folder_netcdf) and os.path.isdir(folder_netcdf):
                feedback.setProgressText(self.tr("NetCDF folder found."))
            else:
                feedback.pushWarning(self.tr("NetCDF folder not found."))
                return {}
            if os.path.exists(inp_file) and os.path.isfile(inp_file):
                feedback.setProgressText(self.tr("INP file found."))
            else:
                feedback.pushWarning(self.tr("INP file not found. Using geopackage temporal values."))
                self.from_inp = False
        else:
            feedback.pushWarning(self.tr("This folder is not valid."))
            return {}
        feedback.setProgress(10)

        # Get result options
        self._get_result_options()

        # Get INP Config
        feedback.setProgressText(self.tr("Getting temporal values."))
        feedback.setProgress(11)
        self._get_temporal_values(self.from_inp, inp_file)
        if self.start_date is None or self.start_time is None or self.step_time is None or self.end_date is None or self.end_time is None:
            feedback.pushWarning(self.tr("Error getting temporal values."))
            return {}

        feedback.setProgressText(self.tr("Importing layers..."))
        feedback.setProgress(15)

        project: QgsProject = QgsProject.instance()

        # Create layer group
        display_group_name: str = "RESULTS - " + os.path.basename(str(self.folder_results_path))
        group_name = os.path.basename(str(self.folder_results_path))
        root: QgsLayerTreeLayer = project.layerTreeRoot()
        self.layers_group = root.insertGroup(0, display_group_name)

        try:
            for layer_name in self.detected_files:
                # Get netcdf file
                netcdf_file: str = f'{folder_netcdf}{os.sep}{layer_name}.nc'
                if not os.path.exists(netcdf_file) or not os.path.isfile(netcdf_file):
                    feedback.pushWarning(self.tr(f'Skipping {layer_name} layer. File not found.'))
                    continue

                # Get layer from netcdf
                layer_uri: str = f'NETCDF:"{netcdf_file}"'

                layer_name = self.transform_layer_name(layer_name)

                # Create raster layer
                raster_layer: QgsRasterLayer = QgsRasterLayer(layer_uri, f'{group_name} - {layer_name}')
                raster_layer.setCrs(QgsProject.instance().crs())

                # Verify if layer is valid and add it to layers list
                if raster_layer.isValid():
                    self.layers.append(raster_layer)
                else:
                    feedback.pushWarning(self.tr(f'Error on importing layer {layer_name}.'))
        except Exception as e:
            feedback.pushWarning(self.tr(f'Error on importing netCDF. {e}'))
            return {}

        return {"Result": True}

    def _get_result_options(self):
        """ Get result options """

        file_names: dict = {
            'depth': 'Depth timeseries',
            'energy': 'Energy timeseries',
            'froude': 'Froude timeseries',
            'hazard_aca': 'Hazard ACA timeseries',
            'infiltration_rate': 'Infiltration Rate timeseries',
            'local_time_step': 'Local Time Step timeseries',
            'max_depth': 'MAX Depth timeseries',
            'max_hazard_aca': 'MAX Hazard ACA timeseries',
            'max_local_time_step': 'MAX Local Time Step timeseries',
            'max_severe_hazard': 'MAX Severe Hazard RD9-2008 timeseries',
            'max_specific_discharge': 'MAX Spec Discharge timeseries',
            'max_velocity': 'MAX Velocity timeseries',
            'max_water_elevation': 'MAX Water Elevation timeseries',
            'rain_depth': 'Rain Depth timeseries',
            'severe_hazard': 'Severe Hazard RD9-2008 timeseries',
            'specific_discharge_x': 'Specific Discharge x timeseries',
            'specific_discharge_y': 'Specific Discharge y timeseries',
            'velocity_x': 'Velocity x timeseries',
            'velocity_y': 'Velocity y timeseries',
            'velocity': 'Velocity timeseries',
            'water_elevation': 'Water Elevation timeseries',
            'water_permanence': 'Water Permanence timeseries'
        }

        sql = "SELECT parameter, value FROM config_param_user WHERE parameter LIKE 'result_symbology_%'"
        result = self.dao.get_rows(sql)
        if result:
            for row in result:
                parameter, value = row
                # Parse parameter name: result_symbology_{property}_{layer_name}
                parts = parameter.replace('result_symbology_', '').split('_', 1)
                if len(parts) < 2:
                    continue

                property_name = parts[0]  # 'min', 'max', 'include'
                layer_option_name = parts[1]  # 'depth', 'velocity', etc.
                if layer_option_name.endswith('_include'):
                    layer_name = file_names[layer_option_name.replace('_include', '')]
                else:
                    layer_name = file_names[layer_option_name]

                # Initialize layer dict if it doesn't exist
                if layer_name not in self.result_options:
                    self.result_options[layer_name] = {
                        'min': 0.0,
                        'max': 2.0,
                        'include': False,
                        'colorramp': '0'  # default
                    }

                # Set the property value
                if property_name == 'min':
                    if layer_option_name.endswith('_include'):
                        self.result_options[layer_name]['include'] = True if value == '1' else False
                        continue
                    self.result_options[layer_name]['min'] = float(value)
                elif property_name == 'max':
                    self.result_options[layer_name]['max'] = float(value)
                elif property_name == 'colorramp':
                    self.result_options[layer_name]['colorramp'] = value

    def _get_temporal_values(self, from_inp: bool = True, inp_file: Optional[str] = None):
        """ Get temporal values from INP file or geopackage """

        if from_inp:
            inp_data = read_inp_file(inp_file)
            options = inp_data['OPTIONS']
            self.start_date = QDate.fromString(options['START_DATE'].strftime("%Y-%m-%d"), 'yyyy-MM-dd')
            self.start_time = QTime.fromString(options['START_TIME'].strftime("%H:%M:%S"), 'hh:mm:ss')
            self.end_date = QDate.fromString(options['END_DATE'].strftime("%Y-%m-%d"), 'yyyy-MM-dd')
            self.end_time = QTime.fromString(options['END_TIME'].strftime("%H:%M:%S"), 'hh:mm:ss')
            self.step_time = QTime.fromString(options['REPORT_STEP'].strftime("%H:%M:%S"), 'hh:mm:ss')
            return

        sql = "SELECT parameter, value FROM config_param_user WHERE parameter IN ('inp_options_start_date', 'inp_options_start_time', 'inp_options_end_date', 'inp_options_end_time', 'inp_options_report_step')"
        result = self.dao.get_rows(sql)
        if result:
            for row in result:
                parameter, value = row
                if parameter == 'inp_options_start_date':
                    self.start_date = QDate.fromString(value, 'yyyy-MM-dd')
                elif parameter == 'inp_options_start_time':
                    self.start_time = QTime.fromString(value, 'hh:mm:ss')
                elif parameter == 'inp_options_end_date':
                    self.end_date = QDate.fromString(value, 'yyyy-MM-dd')
                elif parameter == 'inp_options_end_time':
                    self.end_time = QTime.fromString(value, 'hh:mm:ss')
                elif parameter == 'inp_options_report_step':
                    self.step_time = QTime.fromString(value, 'hh:mm:ss')

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: Feedback):
        self.dao.close_db()

        if self.folder_results_path is None:
            return {}

        if len(self.layers) == 0:
            feedback.pushWarning(self.tr('No layers to import.'))
            return {}

        # Add layers
        try:
            for layer in self.layers:
                if layer is None:
                    continue
                QgsProject.instance().addMapLayer(layer, False)
                self.configLayer(layer, feedback)
                feedback.setProgressText(self.tr(f'Layer {layer.name()} added correctly.'))
                if self.layers_group is not None:
                    self.layers_group.addLayer(layer)
            feedback.setProgressText(self.tr('Configuring temporal line...'))
            self.openTemporalLine()
            feedback.setProgressText(self.tr('Importing process finished.'))
            feedback.setProgress(100)
            self.layers = []
        except Exception as e:
            feedback.pushWarning(self.tr(f'Error on importing layers. {e}'))
            return {}
        return {"Result": True}

    def configLayer(self, layer: QgsRasterLayer, feedback: Feedback):
        """ Configure style and temporal configuration to layer """

        min_value = 0
        max_value = 2
        include_min_value = False
        longest_qgis_step = 0.0000000000000001

        # Get min and max values
        layer_name = layer.name().split('-')[1].strip()
        max_value = self.result_options[layer_name]['max']
        min_value = self.result_options[layer_name]['min']
        include_min_value = self.result_options[layer_name]['include']
        colorramp = self.result_options[layer_name]['colorramp']

        if min_value > max_value:
            feedback.pushWarning(self.tr('Inconsistent min and max values. Using default values...'))
            min_value = 0
            max_value = 2
            include_min_value = False

        if not include_min_value:
            min_value += longest_qgis_step

        colorramps: dict = {
            '0': self._generate_color_map([QColor(0, 0, 255), QColor(0, 255, 255), QColor(0, 255, 0), QColor(255, 255, 0), QColor(255, 0, 0)], min_value, max_value),
            '1': self._generate_color_map([QColor(205, 233, 249), QColor(137, 201, 246), QColor(74, 166, 232), QColor(30, 118, 193), QColor(8, 56, 130)], min_value, max_value),
        }

        # Set main colors
        main_colors: dict = colorramps[colorramp]

        # Create color ramp
        color_items = self.createColorRamp(main_colors, min_value, max_value, longest_qgis_step=longest_qgis_step)

        # Create shader
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setMinimumValue(min_value)
        color_ramp.setMaximumValue(max_value)
        color_ramp.setColorRampItemList(color_items)
        color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
        shader.setRasterShaderFunction(color_ramp)

        # Create render
        provider = layer.dataProvider()

        # Ensure NoData is correctly defined
        try:
            for band_index in range(1, layer.bandCount() + 1):
                provider.setNoDataValue(band_index, -9999.0)
        except Exception:
            pass

        # Use 1-based band index and persist explicit classification range
        renderer = QgsSingleBandPseudoColorRenderer(provider, 1, shader)
        try:
            renderer.setClassificationMin(min_value)
            renderer.setClassificationMax(max_value)
        except Exception:
            pass

        # Apply render
        layer.setRenderer(renderer)
        layer.triggerRepaint()

        # Persist style into project
        try:
            style = QgsMapLayerStyle()
            style.readFromLayer(layer)
            style_name = f"Auto-{layer.name()}"
            sm = layer.styleManager()
            if style_name in sm.styles():
                sm.removeStyle(style_name)
            sm.addStyle(style_name, style)
            sm.setCurrentStyle(style_name)
        except Exception:
            pass

        try:
            # Config temporal
            temporal: QgsRasterLayerTemporalProperties = layer.temporalProperties()
            temporal.setIsActive(True)
            temporal.setMode(Qgis.RasterTemporalMode.FixedRangePerBand)

            start_time: QDateTime = QDateTime(self.start_date, self.start_time, QTimeZone.utc())

            interval_seconds: Optional[int] = None
            if self.step_time is not None:
                interval_seconds = (self.step_time.hour() * 60 + self.step_time.minute()) * 60 + self.step_time.second()

            # Create a time range per band
            ranges: dict = {}
            for i in range(layer.bandCount()):
                end_time = start_time.addSecs(interval_seconds)
                dt_range = QgsDateTimeRange(start_time, end_time)
                ranges[i + 1] = dt_range
                start_time = start_time.addSecs(interval_seconds)

            temporal.setFixedRangePerBand(ranges)
        except Exception:
            pass

    def _generate_color_map(self, colors: list[QColor], min_val: float, max_val: float) -> dict:
        """ Generates a color map from a list of colors and a minimum and maximum value """
        steps = np.linspace(min_val, max_val, num=len(colors))
        return {step: color for step, color in zip(steps, colors)}

    def createColorRamp(self, main_colors: dict, min_val: float, max_val: float, num_steps: int = 20, min_invisible: bool = True, longest_qgis_step: float = 0.0000000000000001):
        """ Creates a color ramp from main colors
                Parameters:
                    main_colors --> Main color references to make the gradient
                    min_val --> Minimum value
                    max_val --> Maximum value
                    num_steps --> Number of ramp values. The more values, more precise color
                    min_invisible --> Boolean to set the minimum value(-9999) invisible
                    longest_qgis_step --> Longest step of QGIS
        """

        # Calculate value difference
        step: float = (max_val - min_val) / (num_steps - 1)
        # Create value list
        values: list[float] = [min_val + i * step for i in range(num_steps)]

        # Calculate each value color
        color_items: list[QgsColorRampShader.ColorRampItem] = []
        last_color: QColor = QColor(0, 0, 0)  # Default color for edge cases

        for val in values:
            # Get parent main colors
            keys: list[float] = sorted(main_colors.keys())
            color = QColor(0, 0, 0)  # Default color

            for i in range(len(keys) - 1):
                if keys[i] <= val <= keys[i + 1]:
                    ratio = (val - keys[i]) / (keys[i + 1] - keys[i])
                    c1 = main_colors[keys[i]]
                    c2 = main_colors[keys[i + 1]]

                    # Calculate color
                    r = int(c1.red() + (c2.red() - c1.red()) * ratio)
                    g = int(c1.green() + (c2.green() - c1.green()) * ratio)
                    b = int(c1.blue() + (c2.blue() - c1.blue()) * ratio)

                    color = QColor(r, g, b)
                    break
            else:
                color = QColor(0, 0, 0)  # Default color

            last_color = color  # Store the last calculated color
            # Store color into color list, enforce dot decimal to avoid NaN on reload
            color_items.append(QgsColorRampShader.ColorRampItem(val, color, f"{val:.6g}"))

        if min_invisible:
            # Set minimum value(-9999) invisible
            color_items.insert(0, QgsColorRampShader.ColorRampItem(-9999.0, QColor(0, 0, 0, 0), "-9999"))
            color_items.insert(1, QgsColorRampShader.ColorRampItem(min_val - longest_qgis_step, QColor(0, 0, 0, 0), f"{(min_val - longest_qgis_step):.10g}"))
            # Set maximum value(9999) like the last color
            color_items.append(QgsColorRampShader.ColorRampItem(9999.0, last_color, "9999.0"))

        return color_items

    def openTemporalLine(self):
        """ Configure and open the QGIS temporal line """

        # Get the temporal controller from the QGIS project
        temporal_controller = self.iface.mapCanvas().temporalController()
        if not temporal_controller:
            return

        # Close the temporal controller if it's open
        action = self.iface.mainWindow().findChild(QAction, 'mActionTemporalController')
        if action.isChecked():
            action.trigger()

        if None in (self.start_date, self.end_date):
            return
        min_time: QDateTime = QDateTime(self.start_date, self.start_time)
        max_time: QDateTime = QDateTime(self.end_date, self.end_time)
        temporal_controller.setTemporalExtents(QgsDateTimeRange(min_time, max_time))

        # Set frame duration using QgsInterval for 1 second
        if self.step_time is None:
            return
        frame_duration = QgsInterval((self.step_time.hour() * 60 + self.step_time.minute()) * 60 + self.step_time.second())
        temporal_controller.setFrameDuration(frame_duration)
        temporal_controller.setFramesPerSecond(1.0)

        # Set navigation mode to Animated for dynamic playback
        temporal_controller.setNavigationMode(QgsTemporalNavigationObject.NavigationMode.Animated)

        # Open temporal controller
        action = self.iface.mainWindow().findChild(QAction, 'mActionTemporalController')
        action.trigger()

    def detect_netcdf_files(self, folder_netcdf: str) -> list[str]:
        """
        Detect all NetCDF files in the results folder and extract variable names.
        
        Returns a list of variable names (without .nc extension).
        """
        if not os.path.exists(folder_netcdf) or not os.path.isdir(folder_netcdf):
            return []

        netcdf_files = glob.glob(os.path.join(folder_netcdf, "*.nc"))

        variable_names = []
        for filepath in netcdf_files:
            filename = os.path.basename(filepath)
            # Remove .nc extension to get variable name
            var_name = os.path.splitext(filename)[0]
            variable_names.append(var_name)

        return sorted(variable_names)

    def transform_layer_name(self, layer_name: str) -> str:
        """ Transform layer name """
        # Remove the underscores at the end of the layer name
        layer_name = re.sub(r'_{1,}$', '', layer_name)
        # Replace underscores between letters with a space
        layer_name = re.sub(r'_{1,}(?=[a-zA-Z])', ' ', layer_name)
        return layer_name

    def shortHelpString(self):
        return self.tr("""Imports raster results from a results folder into QGIS, applies a color ramp, and configures the Temporal Controller for time-based visualization. 
                       You can select the layers to import.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'ImportRasterResults'

    def displayName(self):
        return self.tr('Import Raster Results')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportRasterResults()
