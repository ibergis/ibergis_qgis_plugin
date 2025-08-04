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
    QgsCoordinateReferenceSystem,
    QgsFields
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis
from ...core.utils import  Feedback, tools_dr
from typing import Optional
import processing
import geopandas as gpd
import os
import tempfile

class FixIntersections(QgsProcessingAlgorithm):
    """
    Class to fix intersections on ground and roof layers.
    """
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    FIXED_ROOF_LAYER = 'FIXED_ROOF_LAYER'
    FIXED_GROUND_LAYER = 'FIXED_GROUND_LAYER'

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
            QgsProcessingParameterFeatureSink(
                self.FIXED_GROUND_LAYER,
                self.tr('Fixed intersections ground layer'),
                type=QgsProcessing.SourceType.TypeVectorPolygon
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FIXED_ROOF_LAYER,
                self.tr('Fixed intersections roof layer'),
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
        feedback.setProgressText(self.tr('Cleaning intersections...'))
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
                                      {'LAYERS':[
                                          self.ground_layer,
                                          self.roof_layer
                                          ],
                                          'CRS':QgsProject.instance().crs(),'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        if merged_layer is None:
            feedback.pushWarning(self.tr('Error merging layers.'))
            return {}
        merged_layer.dataProvider().deleteAttributes([0])
        merged_layer.updateFields()

        feedback.setProgressText(self.tr('Spliting multipolygons into single polygons...'))
        feedback.setProgress(20)

        tmp_gpkg = tempfile.mktemp(suffix=".gpkg", prefix="splited_layer_")
        splited_layer = processing.run("native:multiparttosingleparts", {'INPUT':merged_layer,'OUTPUT':tmp_gpkg})['OUTPUT']
        if splited_layer is None:
            feedback.pushWarning(self.tr('Error splitting multipolygons into single polygons.'))
            # Clean up temporary file
            if os.path.exists(tmp_gpkg):
                try:
                    os.remove(tmp_gpkg)
                except OSError:
                    pass
            return {}

        if feedback.isCanceled():
            # Clean up temporary file
            if os.path.exists(tmp_gpkg):
                try:
                    os.remove(tmp_gpkg)
                except OSError:
                    pass
            return {}

        feedback.setProgressText(self.tr('Cleaning intersections...'))
        feedback.setProgress(20)

        # Clean intersections
        cleaned_layer_result = processing.run("grass:v.clean", {
            'input': tmp_gpkg,
            'type':[0,1,2,3,4,5,6],'tool':[0],'threshold':'','-b':False,'-c':False,'output':'TEMPORARY_OUTPUT',
            'error':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001,
            'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':False})
        if cleaned_layer_result is None:
            feedback.pushWarning(self.tr('Error cleaning intersections.'))
            # Clean up temporary file
            if os.path.exists(tmp_gpkg):
                try:
                    os.remove(tmp_gpkg)
                except OSError:
                    pass
            return {}
        cleaned_layer = QgsVectorLayer(cleaned_layer_result['output'], 'cleaned_layer', 'ogr')

        if feedback.isCanceled():
            return {}

        feedback.setProgressText(self.tr('Merging features...'))
        feedback.setProgress(35)

        # Build spatial index for cleaned_layer
        if cleaned_layer.featureCount() == 0:
            feedback.pushWarning(self.tr('No features in cleaned layer.'))
            return {}

        # Convert QGIS layers to GeoDataFrames
        cleaned_gdf = self.qgis_layer_to_gdf(cleaned_layer)

        # Build spatial index for fast neighbor search
        cleaned_gdf['area'] = cleaned_gdf.geometry.area
        mask = cleaned_gdf.geometry.duplicated(keep='first')
        duplicated_geometries = cleaned_gdf[cleaned_gdf.geometry.duplicated(keep=False) & ~mask]

        processing_features = 1

        for idx, intersection in duplicated_geometries.iterrows():
            feedback.setProgress(tools_dr.lerp_progress(processing_features/len(duplicated_geometries)*100, 35, 90))
            processing_features += 1

            # Get all duplicated features
            duplicated_siblings = cleaned_gdf[cleaned_gdf.geometry.geom_equals_exact(intersection.geometry, 0)]

            if feedback.isCanceled():
                return {}

            # Find neighbors (touching polygons, not itself)
            unique_layers = duplicated_siblings['layer'].unique()
            if len(unique_layers) == 1:
                neighbors = cleaned_gdf[
                (cleaned_gdf.geometry.touches(intersection.geometry)) &
                (cleaned_gdf.index != intersection.name) & (intersection.layer == cleaned_gdf.layer)
                ]
            else:
                neighbors = cleaned_gdf[
                (cleaned_gdf.geometry.touches(intersection.geometry)) &
                (cleaned_gdf.index != intersection.name)
                ]
            if neighbors.empty:
                # Drop duplicates
                for _, sibling in duplicated_siblings.iterrows():
                    if sibling.name == intersection.name:
                        continue
                    cleaned_gdf = cleaned_gdf.drop(sibling.name)
                print(f'Dropped duplicates')
                continue
            # Calculate shared perimeter with each neighbor
            max_shared_length = 0
            best_neighbor = None
            for n_idx, n_row in neighbors.iterrows():
                if feedback.isCanceled():
                    return {}
                if n_row.geometry in duplicated_geometries.geometry:
                    continue
                shared = intersection.geometry.boundary.intersection(n_row.geometry.boundary)
                shared_length = shared.length
                if shared_length > max_shared_length:
                    max_shared_length = shared_length
                    best_neighbor = n_row

            if best_neighbor is None:
                feedback.pushWarning(self.tr('No neighbor with shared perimeter found for polygon {0}').format(intersection.code))
                # Drop duplicates
                for _, sibling in duplicated_siblings.iterrows():
                    if sibling.name == intersection.name:
                        continue
                    cleaned_gdf = cleaned_gdf.drop(sibling.name)
                print(f'Dropped duplicates')
                continue

            # Merge geometries
            merged_geom = best_neighbor.geometry.union(intersection.geometry)
            # Update geometry in cleaned_gdf
            cleaned_gdf.at[best_neighbor.name, 'geometry'] = merged_geom

            # Drop duplicates
            for _, sibling in duplicated_siblings.iterrows():
                cleaned_gdf = cleaned_gdf.drop(sibling.name)

        print('Updated features: ', processing_features, '/', len(duplicated_geometries))

        cleaned_layer = self.gdf_to_qgis_layer(cleaned_gdf, QgsProject.instance().crs(), cleaned_layer.fields(), 'cleaned_layer')

        # Split cleaned_layer into roof and ground layers
        feedback.setProgressText(self.tr('Splitting layer into roof and ground layers...'))
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
        for feature in cleaned_layer.getFeatures():
            if feature['layer'] == self.roof_layer.name():
                layer = self.roof_layer
            elif feature['layer'] == self.ground_layer.name():
                layer = self.ground_layer
            new_feature = QgsFeature()
            new_feature.setFields(layer.fields())
            for field in layer.fields():
                if field.name() == 'fid':
                    if layer == self.roof_layer:
                        new_feature[field.name()] = len(roof_features)+1
                    elif layer == self.ground_layer:
                        new_feature[field.name()] = len(ground_features)+1
                    continue
                if field.name() == 'code':
                    if layer == self.roof_layer:
                        new_feature[field.name()] = f'RF{len(roof_features)+1}'
                    elif layer == self.ground_layer:
                        new_feature[field.name()] = f'GR{len(ground_features)+1}'
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

        # Clean up temporary file
        if os.path.exists(tmp_gpkg):
            try:
                os.remove(tmp_gpkg)
            except OSError:
                pass  # Ignore errors if file cannot be removed

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
                if col in ['geometry', 'area']:
                    continue
                feat[col] = row[col]  # Do not cast to str
            feat.setGeometry(QgsGeometry.fromWkt(row['geometry'].wkt))
            layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        return layer

    def shortHelpString(self):
        return self.tr("""Fixes the intersections of the ground and roof polygon layers, and outputs both layers with the fixed intersections.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'FixIntersections'

    def displayName(self):
        return self.tr('Fix Intersections')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FixIntersections()