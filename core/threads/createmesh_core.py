import processing
from qgis.core import QgsField, QgsGeometry, QgsVectorLayer, QgsRasterLayer, QgsFeedback, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest

from typing import Optional
import numpy as np
import pandas as pd


def feature_to_layer(feature, crs):
    layer = QgsVectorLayer("MultiPolygon", "temp", "memory")
    layer.startEditing()
    layer.setCrs(crs)
    for field in feature.fields():
        layer.addAttribute(QgsField(field))
    layer.addFeature(feature)
    layer.commitChanges()
    layer.updateExtents()
    return layer


def execute_ground_zonal_statistics(vector_layer: QgsVectorLayer, raster_layer: QgsRasterLayer) -> tuple[np.ndarray, np.ndarray]:
    ground_triangles = processing.run("native:extractbyattribute", {
        'INPUT': vector_layer,
        'FIELD': 'category',
        'OPERATOR': 0,      # equals
        'VALUE': 'ground',
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })["OUTPUT"]

    result_layer = processing.run("native:zonalstatisticsfb", {
        "COLUMN_PREFIX": "_",
        "INPUT": ground_triangles,
        "INPUT_RASTER": raster_layer,
        "OUTPUT": "TEMPORARY_OUTPUT",
        "RASTER_BAND": 1,
        "STATISTICS": [9],  # majority
    })["OUTPUT"]

    n_triangles = result_layer.featureCount()
    fids = np.empty(n_triangles, dtype=np.uint32)
    values = np.empty(n_triangles, dtype=np.float64)

    for i, feature in enumerate(result_layer.getFeatures()):
        fids[i] = feature["fid"]
        values[i] = feature["_majority"]

    return fids, values


def triangulate_roof(
    roof_layer: QgsVectorLayer,
    only_selected: bool,
    feedback: QgsFeedback
) -> Optional[tuple[pd.DataFrame, pd.DataFrame]]:
# processing.run("3d:tessellate", {'INPUT':QgsProcessingFeatureSourceDefinition('Z:/sample2/sample2.gpkg|layername=roof', selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),'OUTPUT':'TEMPORARY_OUTPUT'})
    res = processing.run("3d:tessellate", {
        "INPUT": QgsProcessingFeatureSourceDefinition(
            roof_layer.source(),
            selectedFeaturesOnly=only_selected,
            featureLimit=-1,
            geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
        ),
        "OUTPUT": "TEMPORARY_OUTPUT"
    })
    if feedback.isCanceled():
        return None

    start_vertex_id = 0
    vertices_dfs = []
    triangles_dfs = []
    for feature in res["OUTPUT"].getFeatures():
        geom: QgsGeometry = feature.geometry()
        geom.normalize()

        vertices = [(v.x(), v.y()) for v in geom.vertices()]
        triangles = [
            [vertices.index((v.x(), v.y())) for v in polygon.vertices()]
            for polygon in geom.asGeometryCollection()
        ]

        vertices_df = pd.DataFrame(vertices, columns=['x', 'y'])
        vertices_df['z'] = 0
        vertices_df["category"] = "roof"

        triangles_df = pd.DataFrame(triangles, columns=['v1', 'v2', 'v3', 'v4'], dtype=np.uint32)
        triangles_df += start_vertex_id
        triangles_df['roughness'] = feature["roughness"]
        triangles_df['roof_id'] = feature["fid"]
        triangles_df["category"] = "roof"

        start_vertex_id += len(vertices)

        vertices_dfs.append(vertices_df)
        triangles_dfs.append(triangles_df)

    vertices_df = pd.concat(vertices_dfs, ignore_index=True) if len(vertices_dfs) > 0 else pd.DataFrame()
    triangles_df = pd.concat(triangles_dfs, ignore_index=True) if len(triangles_dfs) > 0 else pd.DataFrame()

    return vertices_df, triangles_df
