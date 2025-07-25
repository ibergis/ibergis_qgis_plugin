from qgis.core import (
    QgsFeature,
    QgsVectorLayer,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsSpatialIndexKDBush,
    QgsRasterLayer,
)
from qgis.PyQt.QtCore import QVariant
from ..utils.feedback import Feedback
from ..utils.meshing_process import layer_to_gdf
from qgis import processing
from ..utils import tools_dr

from typing import Tuple, Optional
import geopandas as gpd
import pandas as pd
import shapely
import itertools
import time
import numpy as np


def validate_cellsize(
    layer: QgsVectorLayer, feedback: Feedback
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating cellsize for {layer.name()}")
    feedback.setProgress(1)

    # Create layer
    layer_name = f"{layer.name()}: Invalid cellsize"
    output_layer = QgsVectorLayer("Polygon", layer_name, "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()
    fid_field = QgsField("fid", QVariant.Int)
    cellsize_field = QgsField("cellsize", QVariant.Double)
    provider.addAttributes([fid_field, cellsize_field])
    output_layer.updateFields()

    # Calculate step size for progress updates
    total_features = layer.featureCount()
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Fill layer with cellsize errors
    output_layer.startEditing()
    for i, feature in enumerate(layer.getFeatures()):
        if feedback.isCanceled():
            return

        # Update progress in steps
        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

        cellsize = feature["cellsize"]
        if type(cellsize) in [int, float] and cellsize > 0:
            continue
        invalid_feature = QgsFeature(output_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)
    output_layer.commitChanges()

    feedback.setProgressText(f"Validated cellsize for {layer.name()}")
    feedback.setProgress(100)

    return output_layer


def validate_intersect(
    layers_dict: dict, feedback: Feedback
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating intersections for {layers_dict['ground'].name()}")
    feedback.setProgress(1)

    layers = [layers_dict["ground"]]
    data = pd.concat(map(layer_to_gdf, layers))

    # Calculate total features across all layers
    total_features = sum(layer.featureCount() for layer in layers)
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Get overlap
    data["name"] = data.index
    overlap = data.overlay(data, how="intersection", keep_geom_type=False)
    if feedback.isCanceled():
        return
    overlap = overlap.loc[overlap["name_1"] != overlap["name_2"]]
    overlap = overlap.explode()
    overlap = overlap.loc[
        (overlap.geometry.geom_type == "Polygon") & (overlap.geometry.area > 0.0000001)
    ]  # Ignore Line overlap
    if feedback.isCanceled():
        return

    # Fill error layer
    output_layer = QgsVectorLayer("Polygon", "Intersection Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
    provider = output_layer.dataProvider()
    for i, geom in enumerate(overlap.geometry):
        if feedback.isCanceled():
            return

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)

    output_layer.updateExtents()

    feedback.setProgressText(f"Validated intersections for {layers_dict['ground'].name()}")
    feedback.setProgress(100)
    return output_layer


def validate_intersect_v2(
    layers_dict: dict, feedback: Feedback, include_roof: bool = True
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating intersections for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(1)

    layers: list[QgsVectorLayer] = [layers_dict["ground"]]
    if include_roof:
        layers.append(layers_dict["roof"])

    gdfs = []
    for layer in layers:
        gdf = layer_to_gdf(layer, ["code"])
        gdf["layer"] = layer.name()
        gdfs.append(gdf)

    data: gpd.GeoDataFrame = pd.concat(gdfs, ignore_index=True)

    # Calculate total features across all layers
    total_features = sum(layer.featureCount() for layer in layers)
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Get overlap
    data["name"] = data.index
    overlap = data.overlay(data, how="intersection", keep_geom_type=False)
    if feedback.isCanceled():
        return
    overlap = overlap.loc[overlap["name_1"] != overlap["name_2"]]
    overlap = overlap.explode()
    overlap = overlap.loc[
        (overlap.geometry.geom_type == "Polygon") & (overlap.geometry.area > 0.0000001)
    ]  # Ignore Line overlap
    if feedback.isCanceled():
        return

    # Fill error layer
    output_layer = QgsVectorLayer("Polygon", "Intersection Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
    provider = output_layer.dataProvider()
    for i, geom in enumerate(overlap.geometry):
        if feedback.isCanceled():
            return

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)

    output_layer.updateExtents()

    feedback.setProgressText(f"Validated intersections for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(100)
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


def validate_vert_edge_v2(
    layers_dict: dict, feedback: Feedback, include_roof: bool = False
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating vertex-edge for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = sum(layer.featureCount() for layer in layers_dict.values())
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Step 1: Prepare data with spatial indexing
    layers = [layers_dict["ground"]]
    if include_roof:
        layers.append(layers_dict["roof"])

    gdfs = []
    for layer in layers:
        gdf = layer_to_gdf(layer, ["code"])
        gdf["layer"] = layer.name()
        gdfs.append(gdf)

    data = pd.concat(gdfs, ignore_index=True)

    # Extract vertices and create spatial index
    data["vertices"] = data.geometry.apply(
        lambda geom: [shapely.Point(c) for c in shapely.get_coordinates(geom, include_z=False)]
    )

    all_vertices = np.concatenate(data["vertices"].values)
    vertex_tree = shapely.STRtree(all_vertices)

    # Create polygon STRtree for neighbor detection
    polygon_tree = shapely.STRtree(data.geometry.values)

    # Prepare output layer
    output_layer = QgsVectorLayer("Point", "Vertex-Edge Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
    provider = output_layer.dataProvider()
    provider.addAttributes([
        QgsField("polygon_code", QVariant.String),
        QgsField("layer", QVariant.String)
    ])
    output_layer.updateFields()

    # Step 2: Vectorized neighbor checks
    features = []
    i: int = 0
    for idx, row in data.iterrows():
        if feedback.isCanceled():
            return None

        vertices = row["vertices"]
        if not vertices:
            continue

        # Find nearby polygons (within 0.1 buffer)
        nearby_idxs = polygon_tree.query(
            row.geometry.buffer(0.1),
            predicate="intersects"
        )
        nearby = data.iloc[nearby_idxs]
        nearby = nearby[nearby.index != idx]  # Exclude self

        if nearby.empty:
            continue

        # Check each vertex against nearby polygons
        for vertex in vertices:
            # Step 3: Check polygon proximity
            close_polygons = nearby[
                shapely.distance(vertex, nearby.geometry) < 0.000001
            ]
            if close_polygons.empty:
                continue

            # Step 4: Check vertex proximity using spatial index
            candidate_idxs = vertex_tree.query(vertex.buffer(0.000001), predicate="contains")
            nearby_vertices = all_vertices[candidate_idxs]

            for _, poly in close_polygons.iterrows():
                # Find vertices belonging to this polygon
                poly_verts = set(poly["vertices"])
                has_close_vertex = any(
                    v in poly_verts and shapely.distance(vertex, v) < 0.000001
                    for v in nearby_vertices
                )

                if not has_close_vertex:
                    feat = QgsFeature()
                    feat.setFields(output_layer.fields())
                    feat.setAttributes([poly["code"], poly["layer"]])
                    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(vertex.x, vertex.y)))
                    features.append(feat)
                    break  # Only flag once per vertex

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

        i += 1

    # Remove duplicates: same geometry, code, and layer
    unique = set()
    deduped_features = []
    if features:
        for feat in features:
            geom = feat.geometry().asPoint()
            code = feat["polygon_code"]
            layer_name = feat["layer"]
            key = (geom.x(), geom.y(), code, layer_name)
            if key not in unique:
                unique.add(key)
                deduped_features.append(feat)

    if deduped_features:
        provider.addFeatures(deduped_features)
    output_layer.updateExtents()

    feedback.setProgressText(f"Validated vertex-edge for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(100)
    return output_layer


def validate_vert_edge(
    layers_dict: dict, feedback: Feedback, include_roof: bool = False
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating vertex-edge for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = sum(layer.featureCount() for layer in layers_dict.values())
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    layers: list[QgsVectorLayer] = [layers_dict["ground"]]
    if include_roof:
        layers.append(layers_dict["roof"])

    gdfs = []
    for layer in layers:
        gdf = layer_to_gdf(layer, ["code"])
        gdf["layer"] = layer.name()
        gdfs.append(gdf)

    data: gpd.GeoDataFrame = pd.concat(gdfs, ignore_index=True)

    output_layer = QgsVectorLayer("Point", "Vertex-Edge Errors", "memory")
    output_layer.setCrs(layers_dict["ground"].crs())
    provider = output_layer.dataProvider()
    assert provider is not None, "Provider is None"

    provider.addAttributes([
        QgsField("polygon_code", QVariant.String),
        QgsField("layer", QVariant.String)
    ])
    output_layer.updateFields()

    # For each polygon
    i: int = 0
    for row in data.itertuples():
        if feedback.isCanceled():
            return
        geom: shapely.Polygon = row.geometry

        # Get all neighbor polygons
        neighbors: gpd.GeoDataFrame = data[data.intersects(geom.buffer(1))]
        neighbors = neighbors.drop(row.Index, errors="ignore")  # Exclude the current polygon

        # For each vertex in the current polygon
        for p in get_polygon_vertices(geom):
            # If the distance from the vertex to the neigbours polygon is small
            # and the distance from the vertex to the neighbors vertices is big
            # we have detected an error point

            for neighbour in neighbors.itertuples():
                neigh_poly = neighbour.geometry
                dist_to_poly = shapely.distance(shapely.Point(p), neigh_poly)
                if dist_to_poly < 0.1:
                    vertices = shapely.MultiPoint(
                        [
                            shapely.Point(*coords)
                            for coords in get_polygon_vertices(neigh_poly)
                        ]
                    )
                    dist_to_verts = shapely.distance(shapely.Point(p), vertices)
                    if dist_to_verts > 0.1:
                        feature = QgsFeature()
                        feature.setAttributes([
                            neighbour.code,
                            neighbour.layer
                        ])
                        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(*p)))
                        provider.addFeature(feature)
                        break

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

        i += 1

    output_layer.updateExtents()

    feedback.setProgressText(f"Validated vertex-edge for {list(layer.name() for layer in layers_dict.values())}")
    feedback.setProgress(100)
    return output_layer


def validate_ground_layer(
    layer: QgsVectorLayer, feedback: Feedback
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating ground layer for {layer.name()}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = layer.featureCount()
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

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
    for i, feature in enumerate(layer.getFeatures()):
        if feedback.isCanceled():
            return
        landuse = feature["landuse"]
        roughness = feature["custom_roughness"]
        if (
            landuse or
            (roughness and roughness > 0)
        ):
            continue

        invalid_feature = QgsFeature(output_layer.fields())
        attributes = [feature["fid"], feature["landuse"], feature["custom_roughness"]]
        invalid_feature.setAttributes(attributes)
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

    output_layer.commitChanges()

    feedback.setProgressText(f"Validated ground layer for {layer.name()}")
    feedback.setProgress(100)

    return output_layer


def validate_roof_layer(
    layer: QgsVectorLayer, feedback: Feedback
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating roof layer for {layer.name()}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = layer.featureCount()
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Create layer
    output_layer = QgsVectorLayer("Polygon", "Invalid Roof Params", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()

    fid_field = QgsField("fid", QVariant.Int)
    roughness_field = QgsField("roughness", QVariant.String)
    provider.addAttributes([fid_field, roughness_field])
    output_layer.updateFields()

    # Fill layer the with errors
    output_layer.startEditing()
    for i, feature in enumerate(layer.getFeatures()):
        if feedback.isCanceled():
            return
        roughness = feature["roughness"]
        if (
            type(roughness) in [int, float]
        ):
            continue

        invalid_feature = QgsFeature(output_layer.fields())
        invalid_feature.setAttributes(
            [feature["fid"], f'Invalid roughness: {feature["roughness"]}']
        )
        invalid_feature.setGeometry(feature.geometry())
        output_layer.addFeature(invalid_feature)

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

    output_layer.commitChanges()

    feedback.setProgressText(f"Validated roof layer for {layer.name()}")
    feedback.setProgress(100)

    return output_layer


def validate_distance(
    layer: QgsVectorLayer, feedback: Feedback, tolerance: float = 0.00001, use_cellsize: bool = True
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating distance for {layer.name()}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = layer.featureCount()
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    data: gpd.GeoDataFrame = layer_to_gdf(layer, ["cellsize"])
    vertices = []
    cellsize = []
    for row in data.itertuples():
        if feedback.isCanceled():
            return
        geom = row.geometry
        assert type(geom) == shapely.Polygon, f"{type(geom)}"
        new_verts = list(map(shapely.Point, get_polygon_vertices(geom)))
        vertices += new_verts
        cellsize += [row.cellsize] * len(new_verts)

    vertices_gdf = gpd.GeoDataFrame(geometry=vertices, data={"cellsize": cellsize})
    vertices_gdf = vertices_gdf.loc[
        vertices_gdf.groupby("geometry")["cellsize"].idxmin()
    ]

    if use_cellsize:
        max_dist = max(cellsize)
    else:
        max_dist = tolerance

    join = vertices_gdf.sjoin_nearest(
        vertices_gdf, max_distance=max_dist, distance_col="dist", exclusive=True
    )
    if feedback.isCanceled():
        return
    join = join[join["dist"] < tolerance]
    if use_cellsize:
        join["cellsize"] = join[["cellsize_left", "cellsize_right"]].max(axis=1)
        join = join[join["dist"] < join["cellsize"]]

    output_layer = QgsVectorLayer("Point", "Close Vertices Warning", "memory")
    output_layer.setCrs(layer.crs())
    provider = output_layer.dataProvider()
    for i, geom in enumerate(join["geometry"]):
        if feedback.isCanceled():
            return

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(geom.wkt))
        provider.addFeature(feature)

    output_layer.updateExtents()

    feedback.setProgressText(f"Validated distance for {layer.name()}")
    feedback.setProgress(100)

    return output_layer


def validate_validity(
    layer: QgsVectorLayer, feedback: Feedback
) -> Tuple[QgsVectorLayer, QgsVectorLayer]:
    output = processing.run(
        "qgis:checkvalidity",
        {
            "INPUT_LAYER": layer,
            "VALID_OUTPUT": "TEMPORARY_OUTPUT",
            "INVALID_OUTPUT": "TEMPORARY_OUTPUT",
            "ERROR_OUTPUT": "TEMPORARY_OUTPUT",
        },
    )

    invalid: QgsVectorLayer = output["INVALID_OUTPUT"]
    invalid.setName(f"'{layer.name()}' Invalid Output")
    invalid.setCrs(layer.crs())

    error: QgsVectorLayer = output["ERROR_OUTPUT"]
    error.setName(f"'{layer.name()}' Error Output")
    error.setCrs(layer.crs())

    return invalid, error


def validate_null_geometry(
    layer: QgsVectorLayer, feedback: Feedback
) -> Optional[QgsVectorLayer]:
    feedback.setProgressText(f"Validating null geometry for {layer.name()}")
    feedback.setProgress(1)

    # Calculate total features across all layers
    total_features = layer.featureCount()
    step_size = max(1, total_features // 100)  # Update progress every ~1% or at least every feature

    # Fill error layer
    output_layer = QgsVectorLayer(
        "Polygon", f"'{layer.name()}' Null Geometry", "memory"
    )
    output_layer.setCrs(layer.crs())
    attributes = layer.dataProvider().fields().toList()
    provider = output_layer.dataProvider()
    provider.addAttributes(attributes)
    for i, feature in enumerate(layer.getFeatures()):
        if not feature.hasGeometry():
            provider.addFeature(feature)

        if i % step_size == 0:
            progress = min(99, int((i / total_features) * 100))
            feedback.setProgress(progress)

    output_layer.updateExtents()

    feedback.setProgressText(f"Validated null geometry for {layer.name()}")
    feedback.setProgress(100)

    return output_layer


def validate_dem_coverage(layers_dict: dict, feedback: Feedback) -> QgsVectorLayer:
    if layers_dict["dem"] == None:
        return QgsVectorLayer("Polygon", "Empty", "memory")

    dem: QgsRasterLayer = layers_dict["dem"]
    raster_pixel_size = max(dem.rasterUnitsPerPixelX(), dem.rasterUnitsPerPixelY())
    ground = layers_dict["ground"]
    mask = processing.run(
        "native:buffer",
        {
            "INPUT": ground,
            "DISTANCE": raster_pixel_size * 2,
            "SEGMENTS": 5,
            "END_CAP_STYLE": 0,
            "JOIN_STYLE": 0,
            "MITER_LIMIT": 2,
            "DISSOLVE": False,
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]
    cliped_raster = processing.run(
        "gdal:cliprasterbymasklayer",
        {"INPUT": dem, "MASK": mask, "OUTPUT": "TEMPORARY_OUTPUT"},
    )["OUTPUT"]
    polygon = processing.run(
        "native:pixelstopolygons",
        {
            "INPUT_RASTER": cliped_raster,
            "RASTER_BAND": 1,
            "FIELD_NAME": "VALUE",
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]
    diff = processing.run(
        "native:difference",
        {"INPUT": ground, "OVERLAY": polygon, "OUTPUT": "TEMPORARY_OUTPUT"},
    )["OUTPUT"]
    diff.setCrs(ground.crs())
    diff.setName("Raster Ground Coverage Error")

    return diff


# The correct execution of each group of validation operations depends on
# the successful completion of certain operations in the previous group.
_validation_steps = [
    # First group
    {
        "check_null_geometries_ground": {
            "name": "Ground Null Geometry",
            "type": "error",
            "function": validate_null_geometry,
            "layer": "ground",
        },
        "check_null_geometries_roof": {
            "name": "Roof Null Geometry",
            "type": "error",
            "function": validate_null_geometry,
            "layer": "roof",
        },
        "check_geometry_validity_ground": {
            "name": "Ground Geometry Validity",
            "type": "error",
            "function": validate_validity,
            "layer": "ground",
        },
        "check_geometry_validity_roof": {
            "name": "Roof Geometry Validity",
            "type": "error",
            "function": validate_validity,
            "layer": "roof",
        },
        "check_cellsizes_ground": {
            "name": "Ground Invalid Cellsizes",
            "type": "error",
            "function": validate_cellsize,
            "layer": "ground",
        },
        "check_groundroughness_params": {
            "name": "Ground Roughness Invalid Parameters",
            "type": "error",
            "function": validate_ground_layer,
            "layer": "ground",
        },
        "check_roof_params": {
            "name": "Roof Invalid Parameters",
            "type": "error",
            "function": validate_roof_layer,
            "layer": "roof",
        },
    },
    # Second group
    {
        "check_short_edges": {
            "name": "Short Edges",
            "type": "warning",
            "function": validate_distance,
            "layer": "ground",
        },
        "check_dem_coverage": {
            "name": "DEM Coverage",
            "type": "error",
            "function": validate_dem_coverage,
            "layer": None,
        },
        # "check_missing_vertices": {
        #     "name": "Missing Vertices",
        #     "type": "error",
        #     "function": validate_vert_edge,
        #     "layer": None,
        # },
        "check_missing_vertices": {
            "name": "Missing Vertices",
            "type": "error",
            "function": validate_vert_edge_v2,
            "layer": ["ground"],
        },
        "check_intersections": {
            "name": "Intersections",
            "type": "error",
            "function": validate_intersect_v2,
            "layer": ["ground", "roof"],
        },
    },
]


def validations_dict():
    val_list = {
        val_id: {"name": validation["name"], "layer": validation["layer"]}
        for group in _validation_steps
        for val_id, validation in group.items()
    }
    return val_list


def validate_input_layers(
    layers_dict: dict, validation_list: list, feedback: Feedback
) -> Optional[Tuple[list, list]]:
    error_layers = []
    warning_layers = []

    i = 0
    feedback.setProgressText(f"Validations ({len(validation_list)})")
    for validations in _validation_steps:
        for val_id, validation in validations.items():
            if val_id not in validation_list:
                continue

            feedback.setProgressText(f"Validating ({i + 1}/{len(validation_list)})")
            i += 1

            parameter = (
                layers_dict
                if validation["layer"] is None
                else {layer: layers_dict[layer] for layer in validation["layer"]}
                if isinstance(validation["layer"], list)
                else layers_dict[validation["layer"]]
            )

            start = time.time()
            print(f"Executing '{validation['name']}' validation... ", end="")
            result_layers = validation["function"](parameter, feedback)
            print(f"Done! {time.time() - start}s")

            if type(result_layers) not in (tuple, list):
                result_layers = [result_layers]

            if feedback.isCanceled():
                return

            for layer in result_layers:
                if layer.hasFeatures():
                    if validation["type"] == "error":
                        error_layers.append(layer)
                    else:
                        warning_layers.append(layer)

        if error_layers:
            feedback.setProgressText(f"Errors ({len(error_layers)})")
            return error_layers, warning_layers
    return error_layers, warning_layers


def validate_inlets_in_triangles(
    mesh_layer: QgsVectorLayer, inlet_layer: QgsVectorLayer
) -> QgsVectorLayer:

    # Create layer
    output_layer = QgsVectorLayer(
        "Polygon", "Triangles with more than one inlet", "memory"
    )
    output_layer.setCrs(mesh_layer.crs())
    provider = output_layer.dataProvider()
    provider.addAttributes([QgsField("fid", QVariant.Int)])
    output_layer.updateFields()

    if inlet_layer.featureCount() == 0:
        return output_layer

    # Filter errors
    spatial_index = QgsSpatialIndexKDBush(inlet_layer)
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
