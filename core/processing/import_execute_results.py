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
    QgsDateTimeRange
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime
from ...core.utils import Feedback
from typing import Optional
from datetime import datetime
from swmm_api import read_inp_file
import os


class ImportExecuteResults(QgsProcessingAlgorithm):
    """
    Class to import ground geometries from another layer.
    """
    FOLDER_RESULTS = 'FOLDER_RESULTS'
    CUSTOM_NAME = 'CUSTOM_NAME'

    # Layer params
    layers: list[QgsRasterLayer] = list()
    layers_group: Optional[QgsLayerTreeGroup] = None

    # Temporal params
    start_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_date: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_time: Optional[datetime] = None



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

        # reading geodata
        feedback.setProgressText(self.tr('Reading folder...'))
        feedback.setProgress(1)

        folder_results: str = self.parameterAsFile(parameters, self.FOLDER_RESULTS, context)
        group_name: str = self.parameterAsString(parameters, self.CUSTOM_NAME, context)
        file_netcdf: str = f'{folder_results}{os.sep}Results{os.sep}rasters.nc'
        file_inp: str = f'{folder_results}{os.sep}Iber_SWMM.inp'

        if os.path.exists(folder_results) and os.path.isdir(folder_results):
            if os.path.exists(file_netcdf) and os.path.exists(file_netcdf) and os.path.isfile(file_netcdf):
                feedback.setProgressText(self.tr(f"NetCDF file found."))
            else:
                feedback.reportError(self.tr(f"NetCDF file not found."))
                return {}
            if os.path.exists(file_inp) and os.path.isfile(file_inp):
                feedback.setProgressText(self.tr(f"INP file found."))
            else:
                feedback.reportError(self.tr(f"INP file not found."))
                return {}
        else:
            feedback.reportError(self.tr(f"This folder is not valid."))
            return {}
        feedback.setProgress(10)

        # Get INP Config
        feedback.setProgressText(self.tr(f"Getting INP config."))
        feedback.setProgress(11)
        model = read_inp_file(file_inp)
        options = model["OPTIONS"]
        self.start_date = options["START_DATE"]
        self.start_time = options["START_TIME"]
        self.end_date = options["END_DATE"]
        self.end_time = options["END_TIME"]
        self.step_time = options["REPORT_STEP"]
        if self.start_date is None or self.start_time is None or self.step_time is None or self.end_date is None or self.end_time is None:
            feedback.reportError(self.tr(f"Error getting INP config."))
            return {}

        feedback.setProgressText(self.tr(f"Importing layers..."))
        feedback.setProgress(15)

        # Set layer names
        layer_names: list[str] = ["Depth", "Velocity", "Velocity_x", "Velocity_y"]

        project: QgsProject = QgsProject.instance()

        # Create layer group
        if group_name == "" or group_name is None:
            group_name: str = "Results - " + datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        root: QgsLayerTreeLayer = project.layerTreeRoot()
        self.layers_group = root.addGroup(group_name)

        for layer_name in layer_names:
            # Get layer from netcdf
            layer_uri: str = f'NETCDF:"{file_netcdf}":{layer_name}'

            # Create raster layer
            raster_layer: QgsRasterLayer = QgsRasterLayer(layer_uri, layer_name)

            # Verify if layer is valid and add it to layers list
            if raster_layer.isValid():
                self.layers.append(raster_layer)
            else:
                feedback.reportError(self.tr(f'Error on importing layer {layer_name}.'))

        return {}

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: Feedback):
        # Add layers
        for layer in self.layers:
            QgsProject.instance().addMapLayer(layer, False)
            self.configLayer(layer, feedback)
            feedback.setProgressText(self.tr(f'Layer {layer.name()} added correctly.'))
            if self.layers_group is not None:
                self.layers_group.addLayer(layer)
        feedback.setProgressText(self.tr(f"Importing process finished."))
        feedback.setProgress(100)

        return {}

    def configLayer(self, layer: QgsRasterLayer, feedback: Feedback):
        """ Method to configure the raster layer. Setting its style and temporal configuration """
        # Load style
        if os.path.exists(f'C:{os.sep}Users{os.sep}Usuario{os.sep}Documents{os.sep}_DRAIN{os.sep}blues_2.qml'): #TODO set plugin path when the styles have made
            layer.loadNamedStyle(f'C:{os.sep}Users{os.sep}Usuario{os.sep}Documents{os.sep}_DRAIN{os.sep}blues_2.qml')
            feedback.setProgressText(self.tr(f"Style QML found."))
        else:
            feedback.reportError(self.tr(f'Style QML not found.'))

        # Config temporal
        temporal: QgsRasterLayerTemporalProperties = layer.temporalProperties()
        temporal.setIsActive(True)
        temporal.setMode(Qgis.RasterTemporalMode.FixedRangePerBand)

        start_time: QDateTime = QDateTime(self.start_date, self.start_time)
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

    def shortHelpString(self):
        return self.tr("""WIP Process""")

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
