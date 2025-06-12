"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsFeature,
    QgsProcessingParameterDefinition,
    QgsProject,
    QgsVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingFeatureSourceDefinition,
    QgsFeatureRequest,
    QgsProcessingParameterDistance,
    QgsProcessingParameterFeatureSink,
    QgsCoordinateReferenceSystem,
    QgsUnitTypes,
    QgsGeometry,
    QgsRasterLayer,
    QgsApplication,
    QgsProcessingParameterRasterLayer,
    QgsTask
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ..threads.createmesh import DrCreateMeshTask
from ...core.utils import tools_dr, Feedback
from ... import global_vars
from typing import Optional
import os
import processing


class CreateTemporalMesh(QgsProcessingAlgorithm):
    """
    Class to create a temporal mesh.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    RASTER_LAYER = 'RASTER_LAYER'
    dao: Optional[DrGpkgDao] = None
    roof_layer: Optional[QgsVectorLayer] = None
    ground_layer: Optional[QgsVectorLayer] = None
    raster_layer: Optional[QgsRasterLayer] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        ground_layer_param = tools_qgis.get_layer_by_tablename('ground')
        roof_layer_param = tools_qgis.get_layer_by_tablename('roof')

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GROUND_LAYER,
                self.tr('Ground layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=ground_layer_param
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.ROOF_LAYER,
                self.tr('Roof layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=roof_layer_param
            )
        )

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """
        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)
        self.thread_triangulation = None

        if self.ground_layer is None or self.roof_layer is None:
            feedback.reportError(self.tr('Error getting source layers.'))
            return {}

        # Create mesh
        self.thread_triangulation = DrCreateMeshTask(
            "Triangulation",
            execute_validations = [],
            clean_geometries = False,
            clean_tolerance = 0.001,
            only_selected_features = False,
            enable_transition = False,
            transition_slope = 0.0,
            transition_start = 0.0,
            transition_extent = 0.0,
            dem_layer=None,
            roughness_layer = None,
            losses_layer = None,
            mesh_name = "temporal_mesh",
            point_anchor_layer=None,
            line_anchor_layer=None,
            bridge_layer=None,
            feedback=feedback,
            ground_layer=self.ground_layer,
            roof_layer=self.roof_layer,
            inlet_layer=None,
            temporal_mesh=True
        )
        task = self.thread_triangulation

        # Add task to manager and wait for completion
        task_manager = QgsApplication.taskManager()
        task_manager.addTask(task)

        task.waitForFinished()

        if task.status() == QgsTask.Complete:
            feedback.setProgress(100)
            return {}
        else:
            feedback.pushWarning(self.tr('Error during mesh creation'))
            return {}

    def shortHelpString(self):
        return self.tr("""Creates a temporary mesh by combining ground and roof polygon layers, suitable for hydrological or spatial analysis.                        
                       Use this tool to quickly generate a mesh for testing or intermediate analysis without altering your original data.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'CreateTemporalMesh'

    def displayName(self):
        return self.tr('Create temporal mesh')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateTemporalMesh()