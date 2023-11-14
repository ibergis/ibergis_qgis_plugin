from qgis.core import QgsFeature, QgsVectorLayer, QgsField, QgsGeometry, QgsPointXY, QgsSpatialIndexKDBush
from qgis.PyQt.QtCore import QVariant
from ..utils.feedback import Feedback
from ..utils.meshing_process import layer_to_gdf
from ...ext_libs import geopandas as gpd
from qgis import processing

from typing import Tuple, Optional
import pandas as pd
import shapely
import itertools


def validate_cellsize(layer: QgsVectorLayer, feedback: Feedback) -> Optional[QgsVectorLayer]:
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
        if feedback.isCanceled():
            return
        cellsize = feature["cellsize"]
        if type(cellsize) in [int, float] and cellsize > 0:
            continue
        invalid_feature = QgsFeature(output_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)
    output_layer.commitChanges()

    return output_layer


def validate_intersect(layers_dict: dict, feedback: Feedback) -> Optional[QgsVectorLayer]:
    # Combine ground and roofs layers
    layers = [layers_dict["ground"], layers_dict["roof"]]
    data = pd.concat(map(layer_to_gdf, layers))

    # Get overlap
    data["name"] = data.index
    overlap = data.overlay(data, how="intersection", keep_geom_type=False)
    if feedback.isCanceled():
        return
    overlap = overlap.loc[overlap["name_1"] != overlap["name_2"]]
    overlap = overlap.explode()
    overlap = overlap.loc[overlap.geometry.geom_type=='Polygon'] # Ignore Line overlap
    if feedback.isCanceled():
        return

    # Fill error layer
    output_layer = QgsVectorLayer("Polygon", "Intersection Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
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

def validate_vert_edge(layers_dict: dict, feedback: Feedback) -> Optional[QgsVectorLayer]:
    layers = [layers_dict["ground"], layers_dict["roof"]]
    data = pd.concat(map(layer_to_gdf, layers))

    output_layer = QgsVectorLayer("Point", "Vertex-Edge Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
    provider = output_layer.dataProvider()

    # For each polygon
    for i, row in data.iterrows():
        if feedback.isCanceled():
            return
        geom: shapely.Polygon = row['geometry']

        # Get all neighbor polygons
        neighbors: gpd.GeoDataFrame = data[data.intersects(geom.buffer(1))]
        neighbors = neighbors.drop(i, errors='ignore') # Exclude the current polygon
        
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

def validate_ground_roughness_layer(layer: QgsVectorLayer, feedback: Feedback) -> Optional[QgsVectorLayer]:
    # Create layer
    output_layer = QgsVectorLayer("Polygon", "Invalid Roughness Params", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()

    fid_field = QgsField("fid", QVariant.Int)
    landuse_field = QgsField("landuse", QVariant.Int)
    roughness_field = QgsField("custom_roughness", QVariant.Double)
    provider.addAttributes([fid_field, landuse_field, roughness_field])
    output_layer.updateFields()

    # Fill layer the with errors
    output_layer.startEditing()
    for feature in layer.getFeatures():
        if feedback.isCanceled():
            return
        landuse = feature["landuse"]
        roughness = feature["custom_roughness"]
        if (
            type(landuse) in [int, float] or
            type(roughness) in [int, float] and roughness > 0
        ):
            continue

        invalid_feature = QgsFeature(output_layer.fields())
        attributes = [feature["fid"], feature["landuse"], feature["custom_roughness"]]
        invalid_feature.setAttributes(attributes)
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)
    output_layer.commitChanges()

    return output_layer

def validate_roof_layer(layer: QgsVectorLayer, feedback: Feedback) -> Optional[QgsVectorLayer]:
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
        if feedback.isCanceled():
            return
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


def validate_distance(layer: QgsVectorLayer, feedback: Feedback) -> Optional[QgsVectorLayer]:
    data: gpd.GeoDataFrame = layer_to_gdf(layer)
    vertices = []
    cellsize = []
    for i, row in data.iterrows():
        if feedback.isCanceled():
            return
        geom = row['geometry']
        assert type(geom) == shapely.Polygon, f"{type(geom)}"
        new_verts = list(map(shapely.Point, get_polygon_vertices(geom)))
        vertices += new_verts
        cellsize += [row['cellsize']] * len(new_verts)
    
    vertices_gdf = gpd.GeoDataFrame(geometry=vertices, data={
        'cellsize': cellsize
    })
    vertices_gdf = vertices_gdf.loc[vertices_gdf.groupby("geometry")["cellsize"].idxmin()]

    join = vertices_gdf.sjoin_nearest(
        vertices_gdf, max_distance=max(cellsize), distance_col="dist", exclusive=True
    )
    if feedback.isCanceled():
        return
    join = join[join['dist'] > 1e-5]
    join["cellsize"] = join[['cellsize_left', 'cellsize_right']].max(axis=1)
    join = join[join['dist'] < join["cellsize"]]

    output_layer = QgsVectorLayer("Point", "Close Vertices Warning", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()
    for geom in join['geometry']:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)
    
    output_layer.updateExtents()

    return output_layer


def validate_ground_roughness_coverage(layers_dict: dict, feedback: Feedback) -> Optional[QgsVectorLayer]:
    output_layer: QgsVectorLayer = processing.run("native:difference", {
        'INPUT':layers_dict["ground"],
        'OVERLAY':layers_dict["ground_roughness"],
        'OUTPUT':'TEMPORARY_OUTPUT',
        'GRID_SIZE':None}
    )["OUTPUT"]
    output_layer.setCrs(layers_dict["ground"].crs())

    return output_layer


def validate_input_layers(layers_dict: dict, feedback: Feedback) -> Optional[Tuple[list, list]]:
    error_layers = []
    warning_layers = []

    validations = [
        (warning_layers, validate_distance, layers_dict["ground"]),
        (error_layers, validate_roof_layer, layers_dict["roof"]),
        (error_layers, validate_vert_edge, layers_dict),
        (error_layers, validate_intersect, layers_dict),
        (error_layers, validate_cellsize, layers_dict["ground"]),
        (error_layers, validate_cellsize, layers_dict["roof"]),
        (
            error_layers,
            validate_ground_roughness_layer,
            layers_dict["ground_roughness"],
        ),
        (error_layers, validate_ground_roughness_coverage, layers_dict),
    ]

    for result_list, validation_function, parameters in validations:
        result_layer = validation_function(parameters, feedback)
        if feedback.isCanceled():
            return
        if result_layer.hasFeatures():
            result_list.append(result_layer)
        feedback.setProgress(feedback.progress() + 1)

    return error_layers, warning_layers

def validate_gullies_in_triangles(
    mesh_layer: QgsVectorLayer, gully_layer: QgsVectorLayer
) -> QgsVectorLayer:
    
    # Create layer
    output_layer = QgsVectorLayer("Polygon", "Triangles with more than one gully", "memory")
    output_layer.setCrs(mesh_layer.crs())
    provider = output_layer.dataProvider()
    provider.addAttributes([QgsField("fid", QVariant.Int)])
    output_layer.updateFields()

    # Filter errors
    spatial_index = QgsSpatialIndexKDBush(gully_layer)
    ground_triangles = (
        feature.geometry()
        for feature in mesh_layer.getFeatures()
        if feature["category"] == "ground"
    )
    for triangle in ground_triangles:
        points_in_triangle = [
            index_data
            for index_data in spatial_index.intersects(triangle.boundingBox())
            if triangle.contains(index_data.point())
        ]
        if len(points_in_triangle) >= 2:
            feature = QgsFeature()
            feature.setGeometry(triangle)
            provider.addFeature(feature)

    return output_layer