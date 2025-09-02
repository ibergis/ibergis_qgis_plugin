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
from ...core.utils import Feedback, tools_dr
from typing import Optional
import processing
import geopandas as gpd
import pandas as pd


class FixSmallPolygons(QgsProcessingAlgorithm):
    """
    Class to fix small polygons on ground and roof layers.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    MIN_AREA = 'MIN_AREA'
    MIN_PERIMAREA = 'MIN_PERIMAREA'
    FIXED_ROOF_LAYER = 'FIXED_ROOF_LAYER'
    FIXED_GROUND_LAYER = 'FIXED_GROUND_LAYER'

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
                self.FIXED_GROUND_LAYER,
                self.tr('Fixed small polygons ground layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FIXED_ROOF_LAYER,
                self.tr('Fixed small polygons roof layer'),
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
        gdf = self.qgis_layer_to_gdf(merged_layer)
        gdf['area'] = gdf.geometry.area
        gdf['perimeter'] = gdf.geometry.length
        small_area_gdf = gdf[gdf['area'] < min_area]
        large_perimarea_gdf = gdf[gdf['perimeter'] / gdf['area'] > max_perimarea]
        small_gdf = pd.concat([small_area_gdf, large_perimarea_gdf]).drop_duplicates(subset='code')

        processing_features = 1
        for index, row in small_gdf.iterrows():
            feedback.setProgress(tools_dr.lerp_progress(processing_features / len(small_gdf) * 100, 10, 90))
            processing_features += 1
            if feedback.isCanceled():
                return {}

            neighbors = gdf[gdf.geometry.touches(row.geometry)]
            if neighbors.empty:
                feedback.pushWarning(self.tr('No neighbors found for polygon {0}').format(row.code))
                continue

            # Calculate shared perimeter with each neighbor
            max_shared_length = 0
            best_neighbor = None
            for n_idx, n_row in neighbors.iterrows():
                if feedback.isCanceled():
                    return {}
                if n_row.code in small_gdf.code:
                    continue
                shared = row.geometry.boundary.intersection(n_row.geometry.boundary)
                shared_length = shared.length
                if shared_length > max_shared_length:
                    max_shared_length = shared_length
                    best_neighbor = n_row

            if best_neighbor is None:
                feedback.pushWarning(self.tr('No neighbor with shared perimeter found for polygon {0}').format(row.code))
                continue

            merged_geom = best_neighbor.geometry.union(row.geometry)
            gdf.at[best_neighbor.name, 'geometry'] = merged_geom
            idx = gdf.index[gdf['code'] == row['code']][0]
            gdf = gdf.drop(idx)

        fixed_layer = self.gdf_to_qgis_layer(gdf, QgsProject.instance().crs(), merged_layer.fields(), 'fixed_layer')

        # Create feature sink
        feedback.setProgressText(self.tr('Creating result layer...'))
        feedback.setProgress(90)

        # Create feature sinks for roof and ground layers
        (roof_sink, roof_dest_id) = self.parameterAsSink(
            parameters,
            self.FIXED_ROOF_LAYER,
            context,
            self.roof_layer.fields(),
            QgsWkbTypes.MultiPolygon,
            QgsProject.instance().crs()
        )

        (ground_sink, ground_dest_id) = self.parameterAsSink(
            parameters,
            self.FIXED_GROUND_LAYER,
            context,
            self.ground_layer.fields(),
            QgsWkbTypes.MultiPolygon,
            QgsProject.instance().crs()
        )

        if roof_sink is None or ground_sink is None:
            feedback.pushWarning(self.tr('Error creating feature sinks.'))
            return {}

        # Create lists to store features by code
        roof_features = []
        ground_features = []
        for feature in fixed_layer.getFeatures():
            if feature['layer'] == self.roof_layer.name():
                layer = self.roof_layer
            elif feature['layer'] == self.ground_layer.name():
                layer = self.ground_layer
            new_feature = QgsFeature()
            new_feature.setFields(layer.fields())
            for field in layer.fields():
                if field.name() == 'fid':
                    if layer == self.roof_layer:
                        new_feature[field.name()] = len(roof_features) + 1
                    elif layer == self.ground_layer:
                        new_feature[field.name()] = len(ground_features) + 1
                    continue
                if field.name() == 'code':
                    if layer == self.roof_layer:
                        new_feature[field.name()] = f'RF{len(roof_features) + 1}'
                    elif layer == self.ground_layer:
                        new_feature[field.name()] = f'GR{len(ground_features) + 1}'
                    continue
                new_feature[field.name()] = feature[field.name()]
            new_feature.setGeometry(feature.geometry())
            if layer == self.roof_layer:
                roof_features.append(new_feature)
            elif layer == self.ground_layer:
                ground_features.append(new_feature)

        # Add features to sinks
        roof_sink.addFeatures(roof_features)
        ground_sink.addFeatures(ground_features)

        feedback.setProgress(100)
        outputs = {
            self.FIXED_ROOF_LAYER: roof_dest_id,
            self.FIXED_GROUND_LAYER: ground_dest_id
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
                if col in ['geometry', 'area', 'perimeter']:
                    continue
                feat[col] = row[col]  # Do not cast to str
            feat.setGeometry(QgsGeometry.fromWkt(row['geometry'].wkt))
            layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        return layer

    def shortHelpString(self):
        return self.tr("""Fixes the small polygons in the ground and roof polygon layers, and outputs both layers with the fixed small polygons.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'FixSmallPolygons'

    def displayName(self):
        return self.tr('Fix Small Polygons')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FixSmallPolygons()