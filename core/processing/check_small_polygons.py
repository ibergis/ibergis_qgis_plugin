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
    QgsFields,
    QgsField,
    QgsProcessingParameterNumber,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from ...lib import tools_qgis
from ...core.utils import Feedback
from typing import Optional
import processing


class CheckSmallPolygons(QgsProcessingAlgorithm):
    """
    Class to check small polygons on ground and roof layers.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    SMALL_POLYGONS_LAYER = 'SMALL_POLYGONS_LAYER'
    MIN_AREA = 'MIN_AREA'
    MIN_PERIMAREA = 'MIN_PERIMAREA'

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
            QgsProcessingParameterNumber(
                self.MIN_AREA,
                self.tr('Minimum area (m²)'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=0.1
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MIN_PERIMAREA,
                self.tr('Maximum perimeter/area'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=3000
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.SMALL_POLYGONS_LAYER,
                self.tr('Small polygons layer'),
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
        min_area = self.parameterAsDouble(parameters, self.MIN_AREA, context)
        max_perimarea = self.parameterAsDouble(parameters, self.MIN_PERIMAREA, context)

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

        feedback.setProgressText(self.tr('Checking small polygons...'))
        feedback.setProgress(10)

        # Check small polygons
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

            # Check small polygons
            area = feature.geometry().area()
            perimeter = feature.geometry().length()
            perim_area_ratio = perimeter / area if area > 0 else 0

            if area < min_area:
                new_feature = QgsFeature(fields)
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes([
                    feature['code'],  # or feature['Code'] depending on your input field name
                    self.tr('Small area: {0:.2f} m²').format(area)
                ])
                features_to_add.append(new_feature)
            elif perim_area_ratio > max_perimarea:
                new_feature = QgsFeature(fields)
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes([
                    feature['code'],
                    self.tr('High perimeter/area: {0:.2f}').format(perim_area_ratio)
                ])
                features_to_add.append(new_feature)

        if len(features_to_add) == 0:
            feedback.setProgressText(self.tr('No small polygons found.'))
            feedback.setProgress(100)
            return {}

        # Create feature sink
        feedback.setProgressText(self.tr('Creating result layer...'))
        feedback.setProgress(80)

        (small_polygons_sink, small_polygons_dest_id) = self.parameterAsSink(
            parameters,
            self.SMALL_POLYGONS_LAYER,
            context,
            fields,
            QgsWkbTypes.Polygon,
            QgsProject.instance().crs()
        )

        if small_polygons_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sinks.'))
            return {}

        # Add features to sink
        small_polygons_sink.addFeatures(features_to_add)

        feedback.setProgress(100)
        outputs = {
            self.SMALL_POLYGONS_LAYER: small_polygons_dest_id
        }
        return outputs

    def shortHelpString(self):
        return self.tr("""Checks for small polygons in the ground and roof polygon layers, and outputs a layer with the detected small polygons. 
                            Use this tool to identify and correct potential topological errors in your ground and roof features before further processing or mesh generation.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'CheckSmallPolygons'

    def displayName(self):
        return self.tr('Check Small Polygons')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CheckSmallPolygons()