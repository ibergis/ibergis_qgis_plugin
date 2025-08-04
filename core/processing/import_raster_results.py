"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsLayerTreeLayer,
    QgsProcessingParameterString,
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
    QgsTemporalNavigationObject
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QTimeZone, QTime, QDate
from qgis.PyQt.QtGui import QColor, QAction
from ...core.utils import Feedback
from typing import Optional
from datetime import datetime
from ... import global_vars
import os
from ...lib.tools_gpkgdao import DrGpkgDao


class ImportRasterResults(QgsProcessingAlgorithm):
    """
    Class to import raster results from a model results folder.
    """
    FOLDER_RESULTS = 'FOLDER_RESULTS'
    CUSTOM_NAME = 'CUSTOM_NAME'

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
    folder_results_path: Optional[str] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER_RESULTS,
                self.tr('Results folder'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.CUSTOM_NAME,
                self.tr('Group name. DEFAULT_NAME = "Results - Current_Datetime"'),
                optional=True
            )
        )

    def processAlgorithm(self, parameters, context: QgsProcessingContext, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        self.iface = global_vars.iface
        self.layers = []
        self.dao = global_vars.gpkg_dao_data.clone()

        # reading geodata
        feedback.setProgressText(self.tr('Reading folder...'))
        feedback.setProgress(1)

        self.folder_results_path = self.parameterAsFile(parameters, self.FOLDER_RESULTS, context)
        group_name: str = self.parameterAsString(parameters, self.CUSTOM_NAME, context)
        file_netcdf: str = f'{self.folder_results_path}{os.sep}DrainResults{os.sep}rasters.nc'

        # Check if folder is valid and if NetCDF and INP files exist
        if self.folder_results_path is not None and os.path.exists(self.folder_results_path) and os.path.isdir(self.folder_results_path):
            if os.path.exists(file_netcdf) and os.path.exists(file_netcdf) and os.path.isfile(file_netcdf):
                feedback.setProgressText(self.tr("NetCDF file found."))
            else:
                feedback.pushWarning(self.tr("NetCDF file not found."))
                self.folder_results_path = None
                return {}
        else:
            feedback.pushWarning(self.tr("This folder is not valid."))
            return {}
        feedback.setProgress(10)

        # Get INP Config
        feedback.setProgressText(self.tr("Getting temporal values."))
        feedback.setProgress(11)
        sql = f"SELECT parameter, value FROM config_param_user WHERE parameter IN ('inp_options_start_date', 'inp_options_start_time', 'inp_options_end_date', 'inp_options_end_time', 'inp_options_report_step')"
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
        if self.start_date is None or self.start_time is None or self.step_time is None or self.end_date is None or self.end_time is None:
            feedback.pushWarning(self.tr("Error getting temporal values."))
            return {}

        feedback.setProgressText(self.tr("Importing layers..."))
        feedback.setProgress(15)

        # Set layer names
        layer_names: list[str] = ["Depth", "Velocity"]

        project: QgsProject = QgsProject.instance()

        # Create layer group
        if group_name == "" or group_name is None:
            display_group_name: str = "RESULTS - " + os.path.basename(str(self.folder_results_path))
            group_name = os.path.basename(str(self.folder_results_path))
        else:
            display_group_name = f"RESULTS - {group_name}"
        root: QgsLayerTreeLayer = project.layerTreeRoot()
        self.layers_group = root.insertGroup(0, display_group_name)

        try:
            for layer_name in layer_names:
                # Get layer from netcdf
                layer_uri: str = f'NETCDF:"{file_netcdf}":{layer_name}'

                # Create raster layer
                raster_layer: QgsRasterLayer = QgsRasterLayer(layer_uri, f'{group_name} - {layer_name}')

                # Verify if layer is valid and add it to layers list
                if raster_layer.isValid():
                    self.layers.append(raster_layer)
                else:
                    feedback.pushWarning(self.tr(f'Error on importing layer {layer_name}.'))
        except Exception as e:
            feedback.pushWarning(self.tr(f'Error on importing netCDF. {e}'))
            return {}

        return {"Result": True}

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: Feedback):
        if self.folder_results_path is None:
            return {}

        self.dao.close_db()

        # Add layers
        try:
            first_layer: QgsRasterLayer = None
            for layer in self.layers:
                if first_layer is None:
                    first_layer = layer
                QgsProject.instance().addMapLayer(layer, False)
                self.configLayer(layer, feedback)
                feedback.setProgressText(self.tr(f'Layer {layer.name()} added correctly.'))
                if self.layers_group is not None:
                    self.layers_group.addLayer(layer)
            feedback.setProgressText(self.tr('Configuring temporal line...'))
            self.openTemporalLine(first_layer)
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
        if 'Depth' in layer.name():
            layer_name = 'depth'
        elif 'Velocity' in layer.name():
            layer_name = 'velocity'
        else:
            feedback.pushWarning(self.tr('Error configuring the layer. Wrong name.'))
            return

        sql = f"SELECT parameter, value FROM config_param_user WHERE parameter LIKE 'result_symbology_%_{layer_name}%'"
        result = global_vars.gpkg_dao_data.get_rows(sql)
        if result:
            for row in result:
                parameter, value = row
                if parameter == f'result_symbology_max_{layer_name}':
                    max_value = float(value)
                elif parameter == f'result_symbology_min_{layer_name}':
                    min_value = float(value)
                elif parameter == f'result_symbology_min_{layer_name}_include':
                    include_min_value = True if value == '1' else False
        else:
            feedback.pushWarning(self.tr('Error getting min and max values. Using default values...'))
            min_value = 0
            max_value = 2
            include_min_value = False

        if min_value > max_value:
            feedback.pushWarning(self.tr('Inconsistent min and max values. Using default values...'))
            min_value = 0
            max_value = 2
            include_min_value = False

        if not include_min_value:
            min_value += longest_qgis_step

        # Set main colors
        if layer_name == 'depth':
            # Blue gradient
            main_colors: dict = self._generate_color_map([QColor(205, 233, 249), QColor(137, 201, 246), QColor(74, 166, 232), QColor(30, 118, 193), QColor(8, 56, 130)], min_value, max_value)
        elif layer_name == 'velocity':
            # Multi-color gradient
            main_colors: dict = self._generate_color_map([QColor(0, 0, 255), QColor(0, 255, 255), QColor(0, 255, 0), QColor(255, 255, 0), QColor(255, 0, 0)], min_value, max_value)

        # Create color ramp
        color_items = self.createColorRamp(main_colors, min_value, max_value, longest_qgis_step=longest_qgis_step)

        # Create shader
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader(min_value, max_value)
        color_ramp.setColorRampItemList(color_items)
        color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
        shader.setRasterShaderFunction(color_ramp)

        # Create render
        provider = layer.dataProvider()
        renderer = QgsSingleBandPseudoColorRenderer(provider, 0, shader)

        # Apply render
        layer.setRenderer(renderer)
        layer.triggerRepaint()

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
            # Store color into color list
            color_items.append(QgsColorRampShader.ColorRampItem(val, color, f"{val}".replace('.', ',')))

        if min_invisible:
            # Set minimum value(-9999) invisible
            color_items.insert(0, QgsColorRampShader.ColorRampItem(-9999.0, QColor(0, 0, 0, 0), "-9999.0"))
            color_items.insert(1, QgsColorRampShader.ColorRampItem(min_val - longest_qgis_step, QColor(0, 0, 0, 0), f"{min_val - longest_qgis_step}"))
            # Set maximum value(9999) like the last color
            color_items.append(QgsColorRampShader.ColorRampItem(9999.0, last_color, "9999.0"))

        return color_items

    def openTemporalLine(self, layer: QgsRasterLayer):
        """ Configure and open the QGIS temporal line """

        # Get the temporal controller from the QGIS project
        temporal_controller = self.iface.mapCanvas().temporalController()
        if not temporal_controller:
            return

        # Check if the layer has active temporal properties
        temporal_properties = layer.temporalProperties()
        if not temporal_properties.isActive():
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

    def shortHelpString(self):
        return self.tr("""Imports raster results (such as depth and velocity) from a model results folder into QGIS, applies a color gradient, and configures the Temporal Controller for time-based visualization. 
                       You can optionally set a custom group name for the imported layers.""")

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
