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
from qgis.PyQt.QtCore import QCoreApplication, QDateTime
from qgis.PyQt.QtGui import QColor, QAction
from ...core.utils import Feedback
from typing import Optional
from datetime import datetime
from swmm_api import read_inp_file
from ... import global_vars
import os


class ImportExecuteResults(QgsProcessingAlgorithm):
    """
    Class to import ground geometries from another layer.
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

        # reading geodata
        feedback.setProgressText(self.tr('Reading folder...'))
        feedback.setProgress(1)

        self.folder_results_path = self.parameterAsFile(parameters, self.FOLDER_RESULTS, context)
        group_name: str = self.parameterAsString(parameters, self.CUSTOM_NAME, context)
        file_netcdf: str = f'{self.folder_results_path}{os.sep}DrainResults{os.sep}rasters.nc'
        file_inp: str = f'{self.folder_results_path}{os.sep}Iber_SWMM.inp'

        # Check if folder is valid and if NetCDF and INP files exist
        if self.folder_results_path is not None and os.path.exists(self.folder_results_path) and os.path.isdir(self.folder_results_path):
            if os.path.exists(file_netcdf) and os.path.exists(file_netcdf) and os.path.isfile(file_netcdf):
                feedback.setProgressText(self.tr("NetCDF file found."))
            else:
                feedback.pushWarning(self.tr("NetCDF file not found."))
                self.folder_results_path = None
                return {}
            if os.path.exists(file_inp) and os.path.isfile(file_inp):
                feedback.setProgressText(self.tr("INP file found."))
            else:
                feedback.pushWarning(self.tr("INP file not found."))
                self.folder_results_path = None
                return {}
        else:
            feedback.pushWarning(self.tr("This folder is not valid."))
            return {}
        feedback.setProgress(10)

        # Get INP Config
        feedback.setProgressText(self.tr("Getting INP config."))
        feedback.setProgress(11)
        model = read_inp_file(file_inp)
        options = model["OPTIONS"]
        self.start_date = options["START_DATE"]
        self.start_time = options["START_TIME"]
        self.end_date = options["END_DATE"]
        self.end_time = options["END_TIME"]
        self.step_time = options["REPORT_STEP"]
        if self.start_date is None or self.start_time is None or self.step_time is None or self.end_date is None or self.end_time is None:
            feedback.pushWarning(self.tr("Error getting INP config."))
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

        # Set main colors
        main_colors: dict = {0: QColor(0, 0, 255), 0.5: QColor(0, 255, 255), 1: QColor(0, 255, 0), 1.5: QColor(255, 255, 0), 2: QColor(255, 0, 0)}

        # Create color ramp
        color_items = self.createColorRamp(main_colors, 0, 2)

        # Create shader
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader(0, 2)
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

        start_time: QDateTime = QDateTime(self.start_date, self.start_time).addSecs(3600)
        interval_seconds: Optional[int] = None
        if self.step_time is not None:
            interval_seconds = (self.step_time.hour * 60 + self.step_time.minute) * 60 + self.step_time.second

        # Create a time range per band
        ranges: dict = {}
        for i in range(layer.bandCount()):
            end_time = start_time.addSecs(interval_seconds)
            dt_range = QgsDateTimeRange(start_time, end_time)
            ranges[i+1] = dt_range
            start_time = start_time.addSecs(interval_seconds)

        temporal.setFixedRangePerBand(ranges)

    def createColorRamp(self, main_colors: dict, min_val: float, max_val: float, num_steps: int = 20, min_invisible: bool = True):
        """ Creates a color ramp from main colors
                Parameters:
                    main_colors --> Main color references to make the gradient
                    min_val --> Minimum value
                    max_val --> Maximum value
                    num_steps --> Number of ramp values. The more values, more precise color
                    min_invisible --> Boolean to set the minimum value(-9999) invisible
        """

        # Calculate value difference
        step: float = (max_val - min_val) / (num_steps - 1)
        # Create value list
        values: list[float] = [min_val + i * step for i in range(num_steps)]

        # Calculate each value color
        color_items: list[QgsColorRampShader.ColorRampItem] = []
        for val in values:
            # Get parent main colors
            keys: list[float] = sorted(main_colors.keys())
            for i in range(len(keys)-1):
                if keys[i] <= val <= keys[i+1]:
                    ratio = (val - keys[i]) / (keys[i+1] - keys[i])
                    c1 = main_colors[keys[i]]
                    c2 = main_colors[keys[i+1]]

                    # Calculate color
                    r = int(c1.red() + (c2.red() - c1.red()) * ratio)
                    g = int(c1.green() + (c2.green() - c1.green()) * ratio)
                    b = int(c1.blue() + (c2.blue() - c1.blue()) * ratio)

                    color = QColor(r, g, b)
                    break
            else:
                color = QColor(0, 0, 0)  # Default color
            # Store color into color list
            color_items.append(QgsColorRampShader.ColorRampItem(val, color, f"{val}".replace('.', ',')))
        if min_invisible:
            # Set minimum value(-9999) invisible
            color_items.insert(0, QgsColorRampShader.ColorRampItem(-9999.0, QColor(0, 0, 0, 0), "-9999.0"))

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
        frame_duration = QgsInterval((self.step_time.hour * 60 + self.step_time.minute) * 60 + self.step_time.second)
        temporal_controller.setFrameDuration(frame_duration)
        temporal_controller.setFramesPerSecond(1.0)

        # Set navigation mode to Animated for dynamic playback
        temporal_controller.setNavigationMode(QgsTemporalNavigationObject.NavigationMode.Animated)

        # Open temporal controller
        action = self.iface.mainWindow().findChild(QAction, 'mActionTemporalController')
        action.trigger()

    def shortHelpString(self):
        return self.tr("""This tool allows you to import raster results from the results folder created on execute model.\n
        The tool creates a raster layer with a gradient color representation from 0 to 2.\n
        It also configures the QGIS Temporal Controller to display the created raster layer values on its time.\n                       
        You can introduce a custom name for the created layer.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'ImportExecuteResults'

    def displayName(self):
        return self.tr('Import execute results')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportExecuteResults()
