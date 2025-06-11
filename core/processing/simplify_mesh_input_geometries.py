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
    QgsGeometry
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ...core.utils import tools_dr, Feedback
from ... import global_vars
from typing import Optional
import os
import processing


class SimplifyMeshInputGeometries(QgsProcessingAlgorithm):
    """
    Class to simplify mesh input geometries.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    TOLERANCE = 'TOLERANCE'
    PRESERVE_BOUNDARY = 'PRESERVE_BOUNDARY'
    BOOL_SELECTED_FEATURES = 'BOOL_SELECTED_FEATURES'
    bool_selected_features: bool = False
    preserve_boundary : bool = False
    overwrite_source_layers : bool = False
    tolerance : float = 1.0
    simplified_layer : QgsVectorLayer = None

    dao: Optional[DrGpkgDao] = None
    file_source: Optional[QgsVectorLayer] = None
    roof_layer: Optional[QgsVectorLayer] = None
    ground_layer: Optional[QgsVectorLayer] = None

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

        # reading geodata
        feedback.setProgressText(self.tr('Merging roof and ground layers...'))
        feedback.setProgress(1)

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        if self.ground_layer is None or self.roof_layer is None:
            feedback.reportError(self.tr('Error getting source layers.'))
            return {}

        # Merge roof and ground layers
        input_layer = processing.run("native:mergevectorlayers",
                                     {
                                         'LAYERS':[
                                             self.ground_layer,
                                             self.roof_layer
                                            ],
                                         'CRS':QgsCoordinateReferenceSystem('EPSG:'+str(global_vars.data_epsg)),'OUTPUT':'memory:'})
        self.file_source = input_layer['OUTPUT']

        if self.file_source is None:
            feedback.reportError(self.tr('Error merging roof and ground layers.'))
            return {}

        feedback.setProgress(12)

        self.bool_selected_features: bool = self.parameterAsBoolean(parameters, self.BOOL_SELECTED_FEATURES, context)
        self.preserve_boundary : bool = self.parameterAsBoolean(parameters, self.PRESERVE_BOUNDARY, context)
        self.tolerance : float = self.parameterAsDouble(parameters, self.TOLERANCE, context)

        feedback.setProgressText(self.tr('Simplifying geometries...'))

        # Simplify geometries
        if self.bool_selected_features:
            result = processing.run("native:coveragesimplify",{
                    'INPUT': QgsProcessingFeatureSourceDefinition(self.file_source.source(),
                                            selectedFeaturesOnly=True, featureLimit=-1,
                                            geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'TOLERANCE': self.tolerance,'PRESERVE_BOUNDARY': self.preserve_boundary, 'OUTPUT':'memory:'})
        else:
            result = processing.run("native:coveragesimplify",{
                    'INPUT': self.file_source,
                    'TOLERANCE': self.tolerance,'PRESERVE_BOUNDARY': self.preserve_boundary, 'OUTPUT':'memory:'})
        self.simplified_layer : QgsVectorLayer = result['OUTPUT']

        if self.simplified_layer is None:
            feedback.reportError(self.tr('Error simplifying geometries.'))
            return {}

        feedback.setProgress(50)

        return {}

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """  """
        self.dao = global_vars.gpkg_dao_data

        feedback.setProgressText(self.tr('Splitting simplified layer into roof and ground layers...'))
        feedback.setProgress(75)

        # Split simplified layer into roof and ground layers
        result = processing.run("native:splitvectorlayer", {
            'INPUT': self.simplified_layer,
            'FIELD':'layer','PREFIX_FIELD':True,'FILE_TYPE':0, 'OUTPUT':'TEMPORARY_OUTPUT'})

        layer1: QgsVectorLayer = QgsVectorLayer(result['OUTPUT_LAYERS'][0], 'layer1', 'ogr')
        layer2: QgsVectorLayer = QgsVectorLayer(result['OUTPUT_LAYERS'][1], 'layer2', 'ogr')
        layer1_type: Optional[str] = self.get_layer_type(layer1)
        layer2_type: Optional[str] = self.get_layer_type(layer2)

        if layer1_type is None or layer2_type is None:
            feedback.reportError(self.tr('Error getting layer type.'))
            return {}

        if layer1_type == self.roof_layer.name():
            roof_simplified_layer = layer1
            ground_simplified_layer = layer2
        elif layer1_type == self.ground_layer.name():
            roof_simplified_layer = layer2
            ground_simplified_layer = layer1

        # Create temporal layers
        temporal_roof_layer = QgsVectorLayer("MultiPolygon", 'temporal_simplified_roof_layer', 'memory')
        temporal_roof_layer.setCrs(self.simplified_layer.crs())
        temporal_roof_layer.dataProvider().addAttributes(self.roof_layer.fields())
        temporal_roof_layer.updateFields()
        temporal_ground_layer = QgsVectorLayer("MultiPolygon", 'temporal_simplified_ground_layer', 'memory')
        temporal_ground_layer.setCrs(self.simplified_layer.crs())
        temporal_ground_layer.dataProvider().addAttributes(self.ground_layer.fields())
        temporal_roof_layer.updateFields()

        if temporal_roof_layer is None or temporal_ground_layer is None:
            feedback.reportError(self.tr('Error getting source layers.'))
            return {}

        feedback.setProgressText(self.tr('Deleting features from source layers...'))
        feedback.setProgress(80)

        # Save simplified geometries into dictionaries
        roof_simplified_dict: dict[str, QgsGeometry] = {}
        for feature in roof_simplified_layer.getFeatures():
            roof_simplified_dict[feature['code']] = feature.geometry()
        ground_simplified_dict: dict[str, QgsGeometry] = {}
        for feature in ground_simplified_layer.getFeatures():
            ground_simplified_dict[feature['code']] = feature.geometry()

        # Start editing
        temporal_roof_layer.startEditing()
        temporal_ground_layer.startEditing()

        # Set batch size
        batch_size = 5000

        # Process roof features in batches
        feedback.setProgressText(self.tr('Processing roof features...'))
        roof_features = list(self.roof_layer.getFeatures())
        for i in range(0, len(roof_features), batch_size):
            batch = roof_features[i:i + batch_size]
            batch_to_add = []
            for feature in batch:
                if feature['code'] in roof_simplified_dict:
                    feature.setGeometry(roof_simplified_dict[feature['code']])
                    batch_to_add.append(feature)

            if batch_to_add:
                temporal_roof_layer.addFeatures(batch_to_add)
                feedback.setProgressText(self.tr(f"Inserted {len(batch_to_add)} features into roof layer"))
                temporal_roof_layer.commitChanges()
                QApplication.processEvents()
                temporal_roof_layer.startEditing()

        # Process ground features in batches
        feedback.setProgressText(self.tr('Processing ground features...'))
        ground_features = list(self.ground_layer.getFeatures())
        for i in range(0, len(ground_features), batch_size):
            batch = ground_features[i:i + batch_size]
            batch_to_add = []
            for feature in batch:
                if feature['code'] in ground_simplified_dict:
                    feature.setGeometry(ground_simplified_dict[feature['code']])
                    batch_to_add.append(feature)

            if batch_to_add:
                temporal_ground_layer.addFeatures(batch_to_add)
                feedback.setProgressText(self.tr(f"Inserted {len(batch_to_add)} features into ground layer"))
                temporal_ground_layer.commitChanges()
                QApplication.processEvents()
                temporal_ground_layer.startEditing()

        # Final commit for any remaining changes
        temporal_roof_layer.commitChanges()
        temporal_ground_layer.commitChanges()

        feedback.setProgressText(self.tr('Simplified geometries have been processed in batches...'))
        feedback.setProgress(90)

        # Add temporal layers to project
        group_name = "TEMPORAL"
        group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
        if group is None:
            QgsProject.instance().layerTreeRoot().addGroup(group_name)
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
        QgsProject.instance().addMapLayer(temporal_roof_layer, False)
        QgsProject.instance().addMapLayer(temporal_ground_layer, False)
        group.addLayer(temporal_roof_layer)
        group.addLayer(temporal_ground_layer)

        feedback.setProgress(100)
        return {}

    def get_layer_type(self, layer: QgsVectorLayer) -> Optional[str]:
        for feature in layer.getFeatures():
            return feature['layer']
        return None

    def shortHelpString(self):
        return self.tr("""This tool allows you to simplify the input geometries of the mesh.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'SimplifyMeshInputGeometries'

    def displayName(self):
        return self.tr('Simplify mesh input geometries')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SimplifyMeshInputGeometries()