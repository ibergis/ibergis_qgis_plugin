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
    QgsGeometry,
    QgsProcessingParameterNumber,
    QgsCoordinateReferenceSystem,
    QgsFields
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis
from ...core.utils import Feedback
from ...core.threads.validatemesh import validate_distance
from typing import Optional
import geopandas as gpd


class CheckCloseVertices(QgsProcessingAlgorithm):
    """
    Class to check close vertices.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    TOLERANCE = 'TOLERANCE'
    CLOSE_VERTICES_LAYER = 'CLOSE_VERTICES_LAYER'

    ground_layer: Optional[QgsVectorLayer] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        ground_layer_param = tools_qgis.get_layer_by_tablename('ground')

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
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=0.00001
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.CLOSE_VERTICES_LAYER,
                self.tr('Close vertices layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """
        self.ground_layer = None

        # reading geodata
        feedback.setProgressText(self.tr('Checking close vertices...'))
        feedback.setProgress(1)

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)

        if self.ground_layer is None:
            feedback.pushWarning(self.tr('Error getting source layer.'))
            return {}

        feedback.setProgressText(self.tr('Checking close vertices...'))
        feedback.setProgress(5)

        close_vertices_layer = validate_distance(self.ground_layer, feedback, self.parameterAsDouble(parameters, self.TOLERANCE, context), use_cellsize=False)
        feedback.setProgress(90)

        if close_vertices_layer is None:
            feedback.pushWarning(self.tr('Error checking close vertices.'))
            return {}
        if close_vertices_layer.featureCount() == 0:
            feedback.pushWarning(self.tr('No close vertices found.'))
            return {}

        # Create error layer
        (close_vertices_sink, close_vertices_dest_id) = self.parameterAsSink(
            parameters,
            self.CLOSE_VERTICES_LAYER,
            context,
            close_vertices_layer.fields(),
            QgsWkbTypes.Point,
            QgsProject.instance().crs()
        )

        if close_vertices_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sink.'))
            return {}

        close_vertices_sink.addFeatures(close_vertices_layer.getFeatures())

        feedback.setProgress(100)
        outputs = {
            self.CLOSE_VERTICES_LAYER: close_vertices_dest_id
        }
        return outputs

    def qgis_layer_to_gdf(self, layer: QgsVectorLayer) -> gpd.GeoDataFrame:
        features = [f for f in layer.getFeatures()]
        if not features:
            return gpd.GeoDataFrame()
        # Extract attribute names
        columns = features[0].fields().names()
        # Build records
        records = []
        for f in features:
            record = {col: f[col] for col in columns}
            record['geometry'] = f.geometry().asWkt()
            records.append(record)
        gdf = gpd.GeoDataFrame(records)
        gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geometry'])
        gdf = gdf.set_geometry('geometry')
        return gdf

    def gdf_to_qgis_layer(self, gdf: gpd.GeoDataFrame, crs: QgsCoordinateReferenceSystem, fields: QgsFields, layer_name: str = "result") -> QgsVectorLayer:
        # Create memory layer
        layer = QgsVectorLayer(f"MultiPolygon?crs={crs}", layer_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        for _, row in gdf.iterrows():
            feat = QgsFeature()
            feat.setFields(fields)
            for col in gdf.columns:
                if col in ['geometry', 'area']:
                    continue
                feat[col] = row[col]  # Do not cast to str
            feat.setGeometry(QgsGeometry.fromWkt(row['geometry'].wkt))
            layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        return layer

    def shortHelpString(self):
        return self.tr("""Checks for vertices in the ground polygon layer that are closer than a specified tolerance, and outputs a layer with the detected close vertices. 
                            Use this tool to identify and correct potential topological errors in your ground features before further processing or mesh generation.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'CheckCloseVertices'

    def displayName(self):
        return self.tr('Check Close Vertices')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CheckCloseVertices()