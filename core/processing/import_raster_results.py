"""
This file is part of IberGIS
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
    QgsDateTimeRange,
    QgsInterval,
    QgsTemporalNavigationObject,
    QgsProcessingParameterBoolean,
    Qgis
)
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QTime, QDate
from qgis.PyQt.QtGui import QAction
from ...core.utils import Feedback
from typing import Optional
from datetime import datetime
from ... import global_vars
import os
from ...lib.tools_gpkgdao import DrGpkgDao
from swmm_api import read_inp_file
import glob
import re
from ...lib import tools_qgis
from ..utils import tools_dr


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
    symbology_mode: str = '0'

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
                    self.tr(f'Import *{file_name.replace(" timeseries", "")}* NetCDF file'),
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
        self.result_options = {}
        self.symbology_mode = None

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
                self.dao.close_db()
                return {}
            if os.path.exists(inp_file) and os.path.isfile(inp_file):
                feedback.setProgressText(self.tr("INP file found."))
            else:
                feedback.pushWarning(self.tr("INP file not found. Using geopackage temporal values."))
                self.from_inp = False
        else:
            feedback.pushWarning(self.tr("This folder is not valid."))
            self.dao.close_db()
            return {}
        feedback.setProgress(10)

        # Get INP Config
        feedback.setProgressText(self.tr("Getting temporal values."))
        feedback.setProgress(11)
        self._get_temporal_values(self.from_inp, inp_file)
        if self.start_date is None or self.start_time is None or self.step_time is None or self.end_date is None or self.end_time is None:
            feedback.pushWarning(self.tr("Error getting temporal values."))
            self.dao.close_db()
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
            self.dao.close_db()
            return {}
        self.dao.close_db()
        return {"Result": True}

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
        if self.folder_results_path is None:
            return {}

        if len(self.layers) == 0:
            feedback.pushWarning(self.tr('No layers to import.'))
            return {}

        # Add layers
        try:
            # Get symbology mode
            sql = "SELECT value FROM config_param_user WHERE parameter = 'raster_results_symbmode'"
            row = global_vars.gpkg_dao_data.get_row(sql)
            if row:
                self.symbology_mode = row[0]
            else:
                self.symbology_mode = '0'

            # Get result options
            self.result_options = tools_dr.get_result_options()

            # Add layers
            for layer in self.layers:
                if layer is None:
                    continue
                QgsProject.instance().addMapLayer(layer, False)
                self.configLayer(layer, feedback, self.symbology_mode)
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

    def configLayer(self, layer: QgsRasterLayer, feedback: Feedback, mode: str = '0'):
        """ Configure style and temporal configuration to layer """

        min_value = 0
        max_value = 2
        layer_name = os.path.basename(layer.source().replace('"', '').split('NETCDF:')[1])
        colorramp = self.result_options[layer_name]['colorramp']

        # Ensure NoData is correctly defined
        provider = layer.dataProvider()
        try:
            for band_index in range(1, layer.bandCount() + 1):
                provider.setNoDataValue(band_index, -9999.0)
        except Exception:
            pass

        if mode == '0':
            provider = layer.dataProvider()
            min_value = provider.bandStatistics(1, Qgis.RasterBandStatistic.All, layer.extent(), 0).minimumValue
            max_value = provider.bandStatistics(1, Qgis.RasterBandStatistic.All, layer.extent(), 0).maximumValue
        elif mode == '1':
            # Get min and max values from all bands
            provider = layer.dataProvider()
            min_value = provider.bandStatistics(1, Qgis.RasterBandStatistic.All, layer.extent(), 0).minimumValue
            max_value = provider.bandStatistics(1, Qgis.RasterBandStatistic.All, layer.extent(), 0).maximumValue
            band_count = layer.bandCount()
            for band in range(1, band_count + 1):
                stats = provider.bandStatistics(band, Qgis.RasterBandStatistic.All, layer.extent(), 0)
                if stats.minimumValue < min_value:
                    min_value = stats.minimumValue
                if stats.maximumValue > max_value:
                    max_value = stats.maximumValue
        elif mode == '2':
            # Get min and max values
            max_value = self.result_options[layer_name]['max']
            min_value = self.result_options[layer_name]['min']
            include_min_value = self.result_options[layer_name]['include']

            if min_value > max_value:
                feedback.pushWarning(self.tr('Inconsistent min and max values. Using default values...'))
                min_value = 0
                max_value = 2
                include_min_value = False

            longest_qgis_step = 0.0000000000000001
            if not include_min_value:
                min_value += longest_qgis_step

        try:
            # Setup symbology
            tools_dr.setup_symbology(layer, min_value, max_value, colorramp)
            # Config temporal
            tools_dr.setup_temporal_properties(layer, self.start_date, self.start_time, self.step_time)
        except Exception:
            pass

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

        if self.symbology_mode == '0':
            # Connect to temporal controller for dynamic updates
            tools_dr.connect_signal(temporal_controller.updateTemporalRange, tools_dr.on_time_changed, 'TemporalController', 'openTemporalLine_updateTemporalRange_on_time_changed')

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
        return self.tr("""Imports raster results from the selected results folder into QGIS, applies a color ramp, and configures the Temporal Controller for time-based visualization. 
                       You can select the layers to import.
                       The results folder is selected in the results button.""")

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