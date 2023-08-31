import qgis
from qgis.processing import alg
from qgis.gui import QgsMapCanvasSnappingUtils, QgsMapCanvas
from qgis.core import (QgsProject, QgsVectorLayer, QgsProcessingContext, QgsPoint,
    QgsPointLocator, QgsPointXY, QgsSnappingConfig, QgsTolerance, QgsFeature,
    QgsGeometry)
from qgis import analysis
from qgis import processing

from qgis.PyQt.QtCore import QPoint

import pandamesh as pm
try:
    import geopandas as gpd
except ImportError:
    pass
import matplotlib.pyplot as plt
import shapely
import shapely.validation
import numpy as np
import json
import time
import sys
#from guppy import hpy
from tqdm import tqdm

@alg(name='check_intersect', label='Hopefully check',
     group='drain_scripts', group_label='Drain')
@alg.input(type=alg.SOURCE, name='INPUT', label='Superficies')
@alg.output(type=alg.VECTOR_LAYER, name='OUTPUT',
           label='Error Polygons')
def triangulate_custom(instance, parameters, context, feedback, inputs):
    """
    Description of the algorithm. (nye)
    """
    source_layer = instance.parameterAsLayer(parameters, "INPUT", context)
    
    geoms = []
    total = source_layer.featureCount()
    for i, feature in enumerate(source_layer.getFeatures()):
        wkt = feature.geometry().asWkt()
        try:
            geoms.append(shapely.wkt.loads(wkt))
        except Exception as e:
            print(e, wkt)
        
        feedback.setProgress(100 * i / total)
    
    data = gpd.GeoDataFrame(geometry=geoms)
    
    data = data.explode(ignore_index=True)
    data["name"] = data.index
    
    # Extract vertices from polygons. Keep information on how to reconstruct the polygon
    points = []
    polygon_index = []
    ring = []
    for i in tqdm(range(len(data)), desc="Polygon -> Vertex"):
        geom: shapely.Polygon = data.geometry.iloc[i]
        for p in geom.exterior.coords:
            points.append(shapely.Point(p))
            polygon_index.append(data.index[i])
            ring.append(-1)

        for n, interior in enumerate(geom.interiors):
            # print(i, interior)
            for p in interior.coords:
                points.append(shapely.Point(p))
                polygon_index.append(data.index[i])
                ring.append(n)

        # exit()

    vertices = gpd.GeoDataFrame(geometry=points, data={
        "polygon": polygon_index,
        "ring": ring,
        "moved": False,
        "anchor": False
    })

    join = vertices.sjoin_nearest(vertices, max_distance=0.5, distance_col="dist", exclusive=True)
    join = join[join["dist"] > 1e-5]

    indices, counts = np.unique(join.index, return_counts=True)
    for i, count in zip(indices, counts):
        if count > 1:
            # assert vertices.loc[i, "anchor"] == False
            entry = join.loc[i]
            other_i = np.array(entry["index_right"])
            vertices.loc[other_i, "anchor"] = True

            vertices.loc[i, "moved"] = True
            vertices.loc[i, "anchor"] = True
            vertices.loc[i, "geometry"] = vertices.loc[other_i[0], "geometry"]

    for i, count in zip(indices, counts):
        if count == 1:
            assert vertices.loc[i, "moved"] == False
            if not vertices.loc[i, "anchor"]:
                entry = join.loc[i]
                other_i = entry["index_right"]

                assert vertices.loc[other_i, "moved"] == False

                vertices.loc[i, "geometry"] = vertices.loc[other_i].geometry
                vertices.loc[i, "moved"] = True
                vertices.loc[i, "anchor"] = True
                vertices.loc[other_i, "anchor"] = True

    # Reconstruct the polygons from the modified vertices
    for polygon_id, group in tqdm(vertices.groupby("polygon"), desc="Vertex -> Polygon"):
        exterior = group[group["ring"] == -1].geometry
        exterior = [(np.round(p.x, 5), np.round(p.y, 5)) for p in exterior]
        
        rings = group[group["ring"] != -1].groupby("ring")
        interiors = [group.geometry for interior_id, group in rings]
        for i in range(len(interiors)):
            interiors[i] = [(np.round(p.x, 5), np.round(p.y, 5)) for p in interiors[i]]

        data.loc[polygon_id, "geometry"] = shapely.Polygon(exterior, interiors)
    
    overlap = data.overlay(data, how="intersection", keep_geom_type=False)
    overlap = overlap.loc[overlap["name_1"] != overlap["name_2"]]
    overlap = overlap.explode()
    overlap = overlap.loc[overlap.geometry.geom_type=='Polygon']
    print(overlap)
    
    layer = QgsVectorLayer("Polygon", "temp", "memory")
    layer.setCrs(source_layer.crs())
    provider = layer.dataProvider()
    for geom in overlap.geometry:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)
    
    layer.updateExtents()
    
    context.temporaryLayerStore().addMapLayer(layer)
    context.addLayerToLoadOnCompletion(layer.id(),QgsProcessingContext.LayerDetails('INTERSECTING',context.project(),'LAYER'))
    
    return {"OUTPUT": layer}