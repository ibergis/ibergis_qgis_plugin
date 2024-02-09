from qgis import processing
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

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


def execute_zonal_statistics(vector_layer: QgsVectorLayer, raster_layer: QgsVectorLayer) -> (np.ndarray, np.ndarray, QgsVectorLayer):
    params = {
        "COLUMN_PREFIX": "_",
        "INPUT": vector_layer,
        "INPUT_RASTER": raster_layer,
        "OUTPUT": "TEMPORARY_OUTPUT",
        "RASTER_BAND": 1,
        "STATISTICS": [9],  # majority
    }
    res = processing.run("native:zonalstatisticsfb", params)
    res_layer = res["OUTPUT"]

    n_triangles = res_layer.featureCount()
    fids = np.empty(n_triangles, dtype=np.uint32)
    values = np.empty(n_triangles, dtype=np.float64)

    for i, feature in enumerate(res_layer.getFeatures()):
        fids[i] = feature["fid"]
        values[i] = feature["_majority"]
    
    return fids, values, res_layer


def triangulate_roof(roof_layer: QgsVectorLayer, feedback):
    params = {"INPUT": roof_layer, "OUTPUT": "TEMPORARY_OUTPUT"}
    res = processing.run("3d:tessellate", params)
    if feedback.isCanceled():
        return

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
        vertices_df['z'] = feature["elev"]
        vertices_df["category"] = "roof"

        triangles_df = pd.DataFrame(triangles, columns=['v1', 'v2', 'v3', 'v4'], dtype=np.uint32)
        triangles_df += start_vertex_id
        triangles_df['roughness'] = feature["roughness"]
        triangles_df['roof_id'] = feature["fid"]
        triangles_df["category"] = "roof"

        start_vertex_id += len(vertices)

        vertices_dfs.append(vertices_df)
        triangles_dfs.append(triangles_df)

    vertices_df = pd.concat(vertices_dfs, ignore_index=True)
    triangles_df = pd.concat(triangles_dfs, ignore_index=True)

    return vertices_df, triangles_df
