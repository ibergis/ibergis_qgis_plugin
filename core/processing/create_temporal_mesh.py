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
    QgsVectorLayer,
    QgsApplication,
    QgsTask,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingOutputVectorLayer,
    QgsFeatureSink,
    QgsProcessingUtils,
    QgsProject,
    QgsProcessingParameterBoolean
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis
from ..threads.createmesh import DrCreateMeshTask
from ...core.utils import Feedback
from ... import global_vars
from typing import Optional
from ..threads import validatemesh
import os


class CreateTemporalMesh(QgsProcessingAlgorithm):
    """
    Class to create a temporal mesh.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    TEMPORAL_MESH = 'TEMPORAL_MESH'
    IS_VALID = 'IS_VALID'
    MESH_OUTPUT = 'MESH_OUTPUT'
    VALIDATE_LAYERS = 'VALIDATE_LAYERS'

    roof_layer: Optional[QgsVectorLayer] = None
    ground_layer: Optional[QgsVectorLayer] = None
    validation_layer_intersect: Optional[QgsVectorLayer] = None
    validation_layer_vert_edge: Optional[QgsVectorLayer] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        ground_layer_param = tools_qgis.get_layer_by_tablename('ground')
        roof_layer_param = tools_qgis.get_layer_by_tablename('roof')

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.GROUND_LAYER,
                self.tr('Ground layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=ground_layer_param
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ROOF_LAYER,
                self.tr('Roof layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=roof_layer_param
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.VALIDATE_LAYERS,
                self.tr('Validate layers'),
                defaultValue=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.MESH_OUTPUT,
                self.tr("Simplified Mesh Temp Layer"),
                QgsProcessing.SourceType.VectorPolygon,
                createByDefault=True
            )
        )
        self.addOutput(
            QgsProcessingOutputVectorLayer(
                self.MESH_OUTPUT,
                self.tr("Mesh layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """
        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)
        self.thread_triangulation = None
        self.validation_layer_intersect = None
        self.validation_layer_vert_edge = None
        self.validate_layers = self.parameterAsBoolean(parameters, self.VALIDATE_LAYERS, context)

        if self.ground_layer is None or self.roof_layer is None:
            feedback.pushWarning(self.tr('Error getting source layers.'))
            return {}

        # Validate intersection
        if self.validate_layers:
            self.validation_layer_intersect = validatemesh.validate_intersect_v2(
                {"ground": self.ground_layer}, feedback, False
            )
            if self.validation_layer_intersect is None:
                feedback.pushWarning("Intersection validation layer not found")
                self.validation_layer_intersect = None

            if self.validation_layer_intersect is not None and self.validation_layer_intersect.featureCount() > 0:
                return {}

        # Validate vertex-edge
        if self.validate_layers:
            self.validation_layer_vert_edge = validatemesh.validate_vert_edge_v2(
                {"ground": self.ground_layer}, feedback, False
            )
            if self.validation_layer_vert_edge is None:
                feedback.pushWarning("Vertex-edge validation layer not found")
                self.validation_layer_vert_edge = None

            if self.validation_layer_vert_edge is not None and self.validation_layer_vert_edge.featureCount() > 0:
                return {}

        # Create mesh
        self.thread_triangulation = DrCreateMeshTask(
            "Triangulation",
            execute_validations=[],
            clean_geometries=False,
            clean_tolerance=0.001,
            only_selected_features=False,
            enable_transition=False,
            transition_slope=0.0,
            transition_start=0.0,
            transition_extent=0.0,
            dem_layer=None,
            roughness_layer=None,
            losses_layer=None,
            mesh_name="temporal_mesh",
            point_anchor_layer=None,
            line_anchor_layer=None,
            bridge_layer=None,
            feedback=feedback,
            ground_layer=self.ground_layer,
            roof_layer=self.roof_layer,
            inlet_layer=None,
            temporal_mesh=True,
            temp_layer_name="Simplified Mesh Temp Layer"
        )
        task = self.thread_triangulation

        # Add task to manager and wait for completion
        task_manager = QgsApplication.taskManager()
        task_manager.addTask(task)

        task.waitForFinished(0)

        feedback.setProgress(90)

        if task.status() == QgsTask.Complete and task.temp_layer is not None:
            # Apply QML style to the temporal layer
            qml_path = global_vars.plugin_dir + '/resources/templates/mesh_temp_layer.qml'
            if os.path.exists(qml_path):
                task.temp_layer.loadNamedStyle(qml_path)
                task.temp_layer.triggerRepaint()

            # Create the output layer
            outputs = {}
            if parameters.get(self.MESH_OUTPUT):
                qml_path = global_vars.plugin_dir + '/resources/templates/mesh_temp_layer.qml'
                sink, dest_id = self.parameterAsSink(parameters, self.MESH_OUTPUT, context, task.temp_layer.fields(), task.temp_layer.wkbType(), task.temp_layer.sourceCrs())
                if sink:
                    for feature in task.temp_layer.getFeatures():
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)

                    # Get the output layer from the result
                    output_layer = QgsProcessingUtils.mapLayerFromString(dest_id, context)

                    # Apply QML style to the output layer
                    if output_layer and os.path.exists(qml_path):
                        output_layer.loadNamedStyle(qml_path)
                        output_layer.triggerRepaint()

                    outputs[self.MESH_OUTPUT] = os.path.abspath(dest_id)
            feedback.setProgress(100)
            return outputs
        else:
            feedback.pushWarning(self.tr('Error during mesh creation'))
            feedback.pushWarning(task.exception)
            return {}

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """ Add validation layers to project """

        # Find group
        group_name = "TEMPORAL"
        group = tools_qgis.find_toc_group(QgsProject.instance().layerTreeRoot(), group_name)
        if group is None:
            QgsProject.instance().layerTreeRoot().addGroup(group_name)
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
        else:
            # Remove only previous validation layers
            project = QgsProject.instance()
            layer_ids = (x.id() for x in project.mapLayersByName("Intersection Errors") + project.mapLayersByName("Vertex-Edge Errors"))
            project.removeMapLayers(layer_ids)

        if self.validation_layer_intersect is not None and self.validation_layer_intersect.featureCount() > 0:
            # Add validation layer
            QgsProject.instance().addMapLayer(self.validation_layer_intersect, False)
            group.addLayer(self.validation_layer_intersect)
            feedback.pushWarning(self.tr('Intersection errors found'))
        elif self.validation_layer_vert_edge is not None and self.validation_layer_vert_edge.featureCount() > 0:
            # Add validation layer
            QgsProject.instance().addMapLayer(self.validation_layer_vert_edge, False)
            group.addLayer(self.validation_layer_vert_edge)
            feedback.pushWarning(self.tr('Missing vertices found'))

        return {}

    def validate_input_layers(self, feedback: Feedback):
        """ Validate input layers """
        feedback.setProgressText(self.tr('Validating input layers...'))
        # Validate intersection
        self.validation_layer_intersect = validatemesh.validate_intersect_v2(
            {
                "ground": self.ground_layer,
                "roof": self.roof_layer
            },
            feedback,
            True
        )
        if self.validation_layer_intersect is None:
            feedback.pushWarning("Intersection validation layer not found")
            self.validation_layer_intersect = None

        if self.validation_layer_intersect is not None and self.validation_layer_intersect.featureCount() > 0:
            return

        # Validate vertex-edge
        self.validation_layer_vert_edge = validatemesh.validate_vert_edge_v2(
            {
                "ground": self.ground_layer,
                "roof": self.roof_layer
            },
            feedback,
            True
        )
        if self.validation_layer_vert_edge is None:
            feedback.pushWarning("Vertex-edge validation layer not found")
            self.validation_layer_vert_edge = None

    def shortHelpString(self):
        return self.tr("""Creates a temporary mesh by combining ground and roof polygon layers, suitable for hydrological or spatial analysis.                        
                       Use this tool to quickly generate a mesh for testing or intermediate analysis without altering your original data.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'CreateTemporalMesh'

    def displayName(self):
        return self.tr('Create Temporal Mesh')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateTemporalMesh()