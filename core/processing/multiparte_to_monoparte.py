"""
This file is part of IberGIS
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
    QgsWkbTypes,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis
from ...core.utils import Feedback
from typing import Optional
import processing


class MultiparteToMonoparte(QgsProcessingAlgorithm):
    """
    Class to convert multiparte to monoparte.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    CONVERTED_ROOF_LAYER = 'CONVERTED_ROOF_LAYER'
    CONVERTED_GROUND_LAYER = 'CONVERTED_GROUND_LAYER'

    roof_layer: Optional[QgsVectorLayer] = None
    ground_layer: Optional[QgsVectorLayer] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        ground_layer_param = None
        try:
            ground_layer_param = tools_qgis.get_layer_by_tablename('ground')
        except Exception:
            pass
        roof_layer_param = None
        try:
            roof_layer_param = tools_qgis.get_layer_by_tablename('roof')
        except Exception:
            pass

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
            QgsProcessingParameterFeatureSink(
                self.CONVERTED_GROUND_LAYER,
                self.tr('Monoparte ground layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.CONVERTED_ROOF_LAYER,
                self.tr('Monoparte roof layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """
        self.roof_layer = None
        self.ground_layer = None

        # reading geodata
        feedback.setProgress(1)

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        if self.ground_layer is None or self.roof_layer is None:
            feedback.pushWarning(self.tr('Error getting source layers.'))
            return {}

        feedback.setProgressText(self.tr('Converting layers...'))
        feedback.setProgress(5)

        # Convert ground and roof layers to monoparte
        converted_ground = processing.run("native:multiparttosingleparts",
                                      {'INPUT':
                                          self.ground_layer, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        if converted_ground is None:
            feedback.pushWarning(self.tr('Error converting ground layer.'))
            return {}

        converted_roof = processing.run("native:multiparttosingleparts",
                                      {'INPUT':
                                          self.roof_layer, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        if converted_roof is None:
            feedback.pushWarning(self.tr('Error converting roof layer.'))
            return {}

        feedback.setProgressText(self.tr('Converting process finished'))
        feedback.setProgress(80)

        feedback.setProgressText(self.tr('Creating feature sinks...'))

        (roof_sink, roof_dest_id) = self.parameterAsSink(
            parameters,
            self.CONVERTED_ROOF_LAYER,
            context,
            self.roof_layer.fields(),
            QgsWkbTypes.Polygon,
            QgsProject.instance().crs()
        )

        (ground_sink, ground_dest_id) = self.parameterAsSink(
            parameters,
            self.CONVERTED_GROUND_LAYER,
            context,
            self.ground_layer.fields(),
            QgsWkbTypes.Polygon,
            QgsProject.instance().crs()
        )

        if roof_sink is None or ground_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sinks.'))
            return {}

        roof_features = []
        ground_features = []
        for feature in converted_roof.getFeatures():
            new_feature = QgsFeature()
            new_feature.setFields(self.roof_layer.fields())
            for field in self.roof_layer.fields():
                new_feature[field.name()] = feature[field.name()]
            new_feature.setGeometry(feature.geometry())
            roof_features.append(new_feature)
        for feature in converted_ground.getFeatures():
            new_feature = QgsFeature()
            new_feature.setFields(self.ground_layer.fields())
            for field in self.ground_layer.fields():
                new_feature[field.name()] = feature[field.name()]
            new_feature.setGeometry(feature.geometry())
            ground_features.append(new_feature)

        # Add features to sinks
        roof_sink.addFeatures(roof_features)
        ground_sink.addFeatures(ground_features)

        feedback.setProgressText(self.tr('Processing finished'))
        feedback.setProgress(100)
        outputs = {
            self.CONVERTED_ROOF_LAYER: roof_dest_id,
            self.CONVERTED_GROUND_LAYER: ground_dest_id
        }
        return outputs

    def checkParameterValues(self, parameters, context):
        """ Check if parameters are valid """

        error_message = ''
        source_ground_layer: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        source_roof_layer: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)
        target_ground_layer = tools_qgis.get_layer_by_tablename('ground')
        target_roof_layer = tools_qgis.get_layer_by_tablename('roof')

        if source_ground_layer is None or source_roof_layer is None:
            error_message += self.tr('Source layer not found in this schema.\n\n')
        if target_ground_layer is None or target_roof_layer is None:
            error_message += self.tr('Target layer not found in this schema.\n\n')

        if len(error_message) > 0:
            return False, error_message

        # get geometry types
        source_ground_geom_type = QgsWkbTypes.displayString(source_ground_layer.wkbType())
        source_roof_geom_type = QgsWkbTypes.displayString(source_roof_layer.wkbType())

        # check if source layers are multipolygons
        if source_ground_geom_type != 'MultiPolygon':
            error_message += self.tr(f'Source ground layer type is not MultiPolygon. Found: {source_ground_geom_type}\n\n')
        if source_roof_geom_type != 'MultiPolygon':
            error_message += self.tr(f'Source roof layer type is not MultiPolygon. Found: {source_roof_geom_type}\n\n')

        if len(error_message) > 0:
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""Converts the ground and roof source layers to monoparte, and outputs layers with the converted geometry.
                            This tool is useful to convert multiparte layers to monoparte layers, which is required by the mesh generation process.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'MultiparteToMonoparte'

    def displayName(self):
        return self.tr('Multiparte to Monoparte')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return MultiparteToMonoparte()