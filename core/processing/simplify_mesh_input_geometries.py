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
    QgsProject,
    QgsVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDistance,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
    QgsFeatureSink,
    QgsProcessingParameterFeatureSink,
    QgsFeature
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis
from ...core.utils import Feedback, tools_dr
from ...core.threads import validatemesh
from ... import global_vars
from typing import Optional
import processing


class SimplifyMeshInputGeometries(QgsProcessingAlgorithm):
    """
    Class to simplify mesh input geometries.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    TOLERANCE = 'TOLERANCE'
    PRESERVE_BOUNDARY = 'PRESERVE_BOUNDARY'
    SIMPLIFIED_ROOF_LAYER = 'SIMPLIFIED_ROOF_LAYER'
    SIMPLIFIED_GROUND_LAYER = 'SIMPLIFIED_GROUND_LAYER'

    preserve_boundary: bool = False
    tolerance: float = 1.0
    simplified_layer: QgsVectorLayer = None
    file_source: Optional[QgsVectorLayer] = None
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
        self.addParameter(
            QgsProcessingParameterDistance(
                self.TOLERANCE,
                self.tr('Tolerance'),
                defaultValue=1.0,
                optional=False,
                minValue=0,
                maxValue=10000000.0
            )
        )
        boundary_param = QgsProcessingParameterBoolean(
            self.PRESERVE_BOUNDARY,
            self.tr('Preserve boundary'),
            defaultValue=False
        )
        boundary_param.setHelp(self.tr('When enabled the outside edges of the coverage will be preserved without simplification.'))
        self.addParameter(boundary_param)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.SIMPLIFIED_GROUND_LAYER,
                self.tr('Simplified ground layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.SIMPLIFIED_ROOF_LAYER,
                self.tr('Simplified roof layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """
        self.file_source = None
        self.roof_layer = None
        self.ground_layer = None
        self.bool_selected_features = False
        self.preserve_boundary = False
        self.tolerance = 1.0
        self.simplified_layer = None
        self.validation_layer_intersect = None
        self.validation_layer_vert_edge = None

        # reading geodata
        feedback.setProgressText(self.tr('Merging roof and ground layers...'))
        feedback.setProgress(1)

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        if self.ground_layer is None or self.roof_layer is None:
            feedback.pushWarning(self.tr('Error getting source layers.'))
            return {}

        # Merge roof and ground layers
        input_layer = processing.run("native:mergevectorlayers",
                                     {
                                         'LAYERS': [
                                             self.ground_layer,
                                             self.roof_layer
                                            ],
                                         'CRS': QgsCoordinateReferenceSystem('EPSG:' + str(global_vars.data_epsg)), 'OUTPUT': 'memory:'})
        self.file_source = input_layer['OUTPUT']

        if self.file_source is None:
            feedback.pushWarning(self.tr('Error merging roof and ground layers.'))
            return {}

        feedback.setProgress(12)

        self.preserve_boundary: bool = self.parameterAsBoolean(parameters, self.PRESERVE_BOUNDARY, context)
        self.tolerance: float = self.parameterAsDouble(parameters, self.TOLERANCE, context)

        feedback.setProgressText(self.tr('Simplifying geometries...'))

        # Simplify geometries
        try:
            result = processing.run("native:coveragesimplify", {
                    'INPUT': self.file_source,
                    'TOLERANCE': self.tolerance, 'PRESERVE_BOUNDARY': self.preserve_boundary, 'OUTPUT': 'memory:'})
            self.simplified_layer: QgsVectorLayer = result['OUTPUT']
        except Exception as e:
            feedback.pushWarning(self.tr(f'Error simplifying geometries. {e}'))

        if self.simplified_layer is None:
            feedback.pushWarning(self.tr('Error simplifying geometries.'))
            self._validate_input_layers(feedback)
            return {}

        feedback.setProgress(50)

        # Create feature sinks for roof and ground layers
        (roof_sink, roof_dest_id) = self.parameterAsSink(
            parameters,
            self.SIMPLIFIED_ROOF_LAYER,
            context,
            self.roof_layer.fields(),
            QgsWkbTypes.MultiPolygon,
            self.simplified_layer.crs()
        )

        (ground_sink, ground_dest_id) = self.parameterAsSink(
            parameters,
            self.SIMPLIFIED_GROUND_LAYER,
            context,
            self.ground_layer.fields(),
            QgsWkbTypes.MultiPolygon,
            self.simplified_layer.crs()
        )

        if roof_sink is None or ground_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sinks.'))
            return {}

        # Create dictionaries to store features by code
        roof_features = {}
        ground_features = {}
        for feature in self.roof_layer.getFeatures():
            roof_features[feature['code']] = feature
        for feature in self.ground_layer.getFeatures():
            ground_features[feature['code']] = feature

        # Process features and add to appropriate sink
        total = self.simplified_layer.featureCount()
        for i, feature in enumerate(self.simplified_layer.getFeatures()):
            if feedback.isCanceled():
                break

            if feature['layer'] == self.roof_layer.name():
                new_feature = QgsFeature(self.roof_layer.fields())
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes(roof_features[feature['code']].attributes())
                roof_sink.addFeature(new_feature, QgsFeatureSink.FastInsert)
            elif feature['layer'] == self.ground_layer.name():
                new_feature = QgsFeature(self.ground_layer.fields())
                new_feature.setAttributes(ground_features[feature['code']].attributes())
                new_feature.setGeometry(feature.geometry())
                ground_sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(tools_dr.lerp_progress(i / total * 100, 50, 99))

        feedback.setProgress(100)
        outputs = {
            self.SIMPLIFIED_ROOF_LAYER: roof_dest_id,
            self.SIMPLIFIED_GROUND_LAYER: ground_dest_id
        }
        return outputs

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """ Add validation layers to project """

        # Find group
        group_name = "TEMPORAL"
        group = tools_qgis.find_toc_group(QgsProject.instance().layerTreeRoot(), group_name)
        if group is None:
            QgsProject.instance().layerTreeRoot().addGroup(group_name)
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)

        # Remove only previous validation layers
        project = QgsProject.instance()
        layer_ids = (x.id() for x in project.mapLayersByName("Intersection Errors") + project.mapLayersByName("Vertex-Edge Errors"))
        project.removeMapLayers(layer_ids)

        if self.validation_layer_intersect is not None and self.validation_layer_intersect.featureCount() > 0:
            # Add validation layer
            QgsProject.instance().addMapLayer(self.validation_layer_intersect, False)
            group.addLayer(self.validation_layer_intersect)
            feedback.setProgressText(self.tr('Input layers validated'))
        elif self.validation_layer_vert_edge is not None and self.validation_layer_vert_edge.featureCount() > 0:
            # Add validation layer
            QgsProject.instance().addMapLayer(self.validation_layer_vert_edge, False)
            group.addLayer(self.validation_layer_vert_edge)
            feedback.setProgressText(self.tr('Input layers validated'))

        return {}

    def _validate_input_layers(self, feedback: Feedback):
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

    def get_layer_type(self, layer: QgsVectorLayer) -> Optional[str]:
        for feature in layer.getFeatures():
            return feature['layer']
        return None

    def shortHelpString(self):
        return self.tr("""Simplifies the geometries of ground and roof polygon layers and splits the result back into separate layers, with options to set a tolerance and preserve boundaries. 
                       Only valid geometries are processed, and the operation is optimized for large datasets. 
                       If simplification fails, the tool will attempt to validate the input layers and provide feedback to help diagnose issues. 
                       Use this tool to quickly reduce the complexity of mesh input layers for improved performance and easier processing.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'SimplifyMeshInputGeometries'

    def displayName(self):
        return self.tr('Simplify Mesh Input Geometries')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SimplifyMeshInputGeometries()