from qgis.core import QgsFeature, QgsVectorLayer, QgsField, QgsGeometry, QgsPointXY
from qgis.PyQt.QtCore import QVariant
from ..utils.meshing_process import layer_to_gdf
from ...ext_libs import geopandas as gpd

from typing import Tuple
import pandas as pd
import shapely
import itertools
import time


def validate_cellsize(layer: QgsVectorLayer) -> QgsVectorLayer:
    # Create layer
    layer_name = f"{layer.name()}: Invalid cellsize"
    output_layer = QgsVectorLayer("Polygon", layer_name, "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()
    fid_field = QgsField("fid", QVariant.Int)
    cellsize_field = QgsField("cellsize", QVariant.Double)
    provider.addAttributes([fid_field, cellsize_field])
    output_layer.updateFields()

    # Fill layer with cellsize errors
    output_layer.startEditing()
    for feature in layer.getFeatures():
        cellsize = feature["cellsize"]
        if type(cellsize) in [int, float] and cellsize > 0:
            continue
        invalid_feature = QgsFeature(output_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)
    output_layer.commitChanges()

    return output_layer


def validate_intersect(layers_dict: dict) -> QgsVectorLayer:
    # Combine ground and roofs layers
    data = pd.concat(map(layer_to_gdf, layers_dict.values()))

    # Get overlap
    data["name"] = data.index
    overlap = data.overlay(data, how="intersection", keep_geom_type=False)
    overlap = overlap.loc[overlap["name_1"] != overlap["name_2"]]
    overlap = overlap.explode()
    overlap = overlap.loc[overlap.geometry.geom_type=='Polygon'] # Ignore Line overlap

    # Fill error layer
    output_layer = QgsVectorLayer("Polygon", "Intersection Errors", "memory")
    output_layer.setCrs(list(layers_dict.values())[0].crs())
    provider = output_layer.dataProvider()
    for geom in overlap.geometry:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)
    
    output_layer.updateExtents()
    return output_layer


def get_polygon_vertices(geom: shapely.Polygon) -> list:
    assert type(geom) == shapely.Polygon
    rings = [geom.exterior.coords]
    rings += [interior.coords for interior in geom.interiors]
    return list(itertools.chain(*rings))

def get_multipolygon_vertices(geom: shapely.MultiPolygon) -> list:
    assert type(geom) == shapely.MultiPolygon
    verts = []
    for poly in geom.geoms:
        verts += get_polygon_vertices(poly)
    return verts

def validate_vert_edge(layers_dict: dict) -> QgsVectorLayer:
    data = pd.concat(map(layer_to_gdf, layers_dict.values()))

    output_layer = QgsVectorLayer("Point", "Vertex-Edge Errors", "memory")
    output_layer.setCrs(list(layers_dict.values())[0].crs())
    provider = output_layer.dataProvider()

    # For each polygon
    for i, row in data.iterrows():
        geom: shapely.Polygon = row['geometry']

        # Get all neighbor polygons
        neighbors: gpd.GeoDataFrame = data[data.intersects(geom.buffer(1))]
        neighbors = neighbors.drop(i) # Exclude the current polygon
        
        # For each vertex in the current polygon
        for p in get_polygon_vertices(geom):
            # If the distance from the vertex to the neigbours polygon is small
            # and the distance from the vertex to the neighbors vertices is big
            # we have detected an error point

            for poly in neighbors['geometry']:
                dist_to_poly = shapely.distance(shapely.Point(p), poly)
                if dist_to_poly < 0.1:
                    vertices = shapely.MultiPoint([
                        shapely.Point(*coords)
                        for coords in get_polygon_vertices(poly)
                    ])
                    dist_to_verts = shapely.distance(shapely.Point(p), vertices)
                    if dist_to_verts > 0.1:
                        feature = QgsFeature()
                        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(*p)))
                        provider.addFeature(feature)
                        break
        
    output_layer.updateExtents()
    
    return output_layer


def validate_roof_layer(layer: QgsVectorLayer):
    # Create layer
    output_layer = QgsVectorLayer("Polygon", "Invalid Roof Params", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()

    fid_field = QgsField("fid", QVariant.Int)
    roughness_field = QgsField("roughness", QVariant.Double)
    elev_field = QgsField("elev", QVariant.Double)
    provider.addAttributes([fid_field, roughness_field, elev_field])
    output_layer.updateFields()

    # Fill layer the with errors
    output_layer.startEditing()
    for feature in layer.getFeatures():
        roughness = feature["roughness"]
        elev = feature["elev"]
        if (
            type(roughness) in [int, float] and roughness >= 0 and
            type(elev) in [int, float]
        ):
            continue

        invalid_feature = QgsFeature(output_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["roughness"], feature["elev"]])
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)
    output_layer.commitChanges()

    return output_layer


def validate_distance(layer: QgsVectorLayer) -> QgsVectorLayer:
    data: gpd.GeoDataFrame = layer_to_gdf(layer)
    vertices = []
    cellsize = []
    for i, row in data.iterrows():
        geom = row['geometry']
        assert type(geom) == shapely.Polygon, f"{type(geom)}"
        new_verts = list(map(shapely.Point, get_polygon_vertices(geom)))
        vertices += new_verts
        cellsize += [row['cellsize']] * len(new_verts)
    
    vertices_gdf = gpd.GeoDataFrame(geometry=vertices, data={
        'cellsize': cellsize
    })
    join = vertices_gdf.sjoin_nearest(
        vertices_gdf, max_distance=max(cellsize), distance_col="dist", exclusive=True
    )
    join = join[join['dist'] > 1e-5]
    join = join[join['dist'] < join["cellsize_left"]]

    output_layer = QgsVectorLayer("Point", "Close Vertices Warning", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()
    for geom in join.geometry:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)
    
    output_layer.updateExtents()

    return output_layer


def validate_input_layers(layers_dict: dict) -> Tuple[list, list]:
    error_layers = []
    warning_layers = []

    small_vertex_distance_layer = validate_distance(layers_dict["ground"])
    if small_vertex_distance_layer.hasFeatures():
        warning_layers.append(small_vertex_distance_layer)

    # Validate ground layer
    roof_attrs_layer = validate_roof_layer(layers_dict["roof"])
    if roof_attrs_layer.hasFeatures():
        error_layers.append(roof_attrs_layer)

    # Validate vert-edge
    start = time.time()
    vert_edge_layer = validate_vert_edge(layers_dict)
    print(f"{time.time() - start} to vert-edge")
    if vert_edge_layer.hasFeatures():
        error_layers.append(vert_edge_layer)

    # Validate intersections
    intersect_layer = validate_intersect(layers_dict)
    if intersect_layer.hasFeatures():
        error_layers.append(intersect_layer)

    # Validate ground layer
    ground_cellsize_layer = validate_cellsize(layers_dict["ground"])
    if ground_cellsize_layer.hasFeatures():
        error_layers.append(ground_cellsize_layer)

    # Validate roof layer
    roof_cellsize_layer = validate_cellsize(layers_dict["roof"])
    if roof_cellsize_layer.hasFeatures():
        error_layers.append(roof_cellsize_layer)

    return error_layers, warning_layers
