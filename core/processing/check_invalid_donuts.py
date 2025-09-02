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
    QgsWkbTypes,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
    QgsFields,
    QgsField,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from ...lib import tools_qgis
from ...core.utils import Feedback
from typing import Optional
import processing


class CheckInvalidDonuts(QgsProcessingAlgorithm):
    """
    Class to check invalid donuts on ground and roof layers.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    INVALID_DONUTS_LAYER = 'INVALID_DONUTS_LAYER'

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
                self.INVALID_DONUTS_LAYER,
                self.tr('Invalid donuts layer'),
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
        feedback.setProgressText(self.tr('Reading data...'))
        feedback.setProgress(1)

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        if self.ground_layer is None or self.roof_layer is None:
            feedback.pushWarning(self.tr('Error getting source layers.'))
            return {}

        feedback.setProgressText(self.tr('Merging layers...'))
        feedback.setProgress(5)

        # Merge layers
        merged_layer = processing.run("native:mergevectorlayers",
                                      {'LAYERS': [
                                          self.ground_layer,
                                          self.roof_layer
                                          ],
                                          'CRS': QgsProject.instance().crs(), 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        if merged_layer is None:
            feedback.pushWarning(self.tr('Error merging layers.'))
            return {}
        merged_layer.dataProvider().deleteAttributes([0])
        merged_layer.updateFields()

        feedback.setProgressText(self.tr('Checking invalid donuts...'))
        feedback.setProgress(10)

        # Check invalid donuts
        i = 0
        step_size = 100
        total_features = merged_layer.featureCount()
        fields = QgsFields()
        fields.append(QgsField('Code', QVariant.String))
        fields.append(QgsField('Exception', QVariant.String))
        features_to_add = []
        for feature in merged_layer.getFeatures():
            # Update progress
            if i % step_size == 0:
                progress = min(99, int((i / total_features) * 100))
                feedback.setProgress(progress)
            i += 1

            # Check for ring self-intersection using QGIS geometry validity
            geom = feature.geometry()
            if not geom.isGeosValid():
                reason = geom.lastError() if hasattr(geom, 'lastError') else self.tr('Invalid geometry')
                print(f"Reason: {reason}")
                if 'Ring self-intersection' in reason or 'Self-intersection' in reason or 'ring self-intersection' in reason or 'self-intersection' in reason:
                    new_feature = QgsFeature(fields)
                    new_feature.setGeometry(geom)
                    new_feature.setAttributes([
                        feature['code'],
                        reason
                    ])
                    features_to_add.append(new_feature)
                    continue

        if len(features_to_add) == 0:
            feedback.setProgressText(self.tr('No invalid donuts found.'))
            feedback.setProgress(100)
            return {}

        # Create feature sink
        feedback.setProgressText(self.tr('Creating result layer...'))
        feedback.setProgress(80)

        (invalid_donuts_sink, invalid_donuts_dest_id) = self.parameterAsSink(
            parameters,
            self.INVALID_DONUTS_LAYER,
            context,
            fields,
            QgsWkbTypes.MultiPolygon,
            QgsProject.instance().crs()
        )

        if invalid_donuts_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sinks.'))
            return {}

        # Add features to sink
        invalid_donuts_sink.addFeatures(features_to_add)

        feedback.setProgress(100)
        outputs = {
            self.INVALID_DONUTS_LAYER: invalid_donuts_dest_id
        }
        return outputs

    def shortHelpString(self):
        return self.tr("""Checks for invalid donuts in the ground and roof polygon layers, and outputs a layer with the detected invalid polygons. 
                            Use this tool to identify and correct potential topological errors in your ground and roof features before further processing or mesh generation.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'CheckInvalidDonuts'

    def displayName(self):
        return self.tr('Check Invalid Donuts')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CheckInvalidDonuts()