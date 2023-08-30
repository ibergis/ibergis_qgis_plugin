from qgis.processing import alg
from qgis.core import (
    QgsVectorLayer,
    QgsProcessingContext,
    QgsPointXY,
    QgsFeature,
    QgsGeometry,
    QgsField,
)

from qgis.PyQt.QtCore import QVariant

import pandamesh as pm

import geopandas as gpd
import shapely
import numpy as np
import time
import gmsh

# From pandamesh
def get_vertices():
    # getNodes returns: node_tags, coord, parametric_coord
    _, vertices, _ = gmsh.model.mesh.getNodes()
    # Return x and y
    return vertices.reshape((-1, 3))[:, :2]


# From pandamesh
def get_faces():
    element_types, _, node_tags = gmsh.model.mesh.getElements()
    tags = {etype: tags for etype, tags in zip(element_types, node_tags)}
    _TRIANGLE = 2
    _QUAD = 3
    _FILL_VALUE = 0
    # Combine triangle and quad faces if the mesh is heterogenous
    if _TRIANGLE in tags and _QUAD in tags:
        triangle_faces = tags[_TRIANGLE].reshape((-1, 3))
        quad_faces = tags[_QUAD].reshape((-1, 4))
        n_triangle = triangle_faces.shape[0]
        n_quad = quad_faces.shape[0]
        faces = np.full((n_triangle + n_quad, 4), _FILL_VALUE)
        faces[:n_triangle, :3] = triangle_faces
        faces[n_triangle:, :] = quad_faces
    elif _QUAD in tags:
        faces = tags[_QUAD].reshape((-1, 4))
    elif _TRIANGLE in tags:
        faces = tags[_TRIANGLE].reshape((-1, 3))
    else:
        raise ValueError("No triangles or quads in mesh")
    # convert to 0-based index
    return faces - 1


def clean_geometries(gdf: gpd.GeoDataFrame, feedback):
    data = gdf.copy()

    # Extract vertices from polygons. Keep information on how to reconstruct the polygon
    points = []
    polygon_index = []
    ring = []
    # for i in tqdm(range(len(data)), desc="Polygon -> Vertex"):
    for i in range(len(data)):
        if feedback.isCanceled():
            return {}
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

    vertices = gpd.GeoDataFrame(
        geometry=points,
        data={"polygon": polygon_index, "ring": ring, "moved": False, "anchor": False},
    )

    join = vertices.sjoin_nearest(
        vertices, max_distance=0.5, distance_col="dist", exclusive=True
    )
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
    # for polygon_id, group in tqdm(vertices.groupby("polygon"), desc="Vertex -> Polygon"):
    for polygon_id, group in vertices.groupby("polygon"):
        exterior = group[group["ring"] == -1].geometry
        exterior = [(np.round(p.x, 5), np.round(p.y, 5)) for p in exterior]

        rings = group[group["ring"] != -1].groupby("ring")
        interiors = [group.geometry for interior_id, group in rings]
        for i in range(len(interiors)):
            interiors[i] = [(np.round(p.x, 5), np.round(p.y, 5)) for p in interiors[i]]
            if feedback.isCanceled():
                return {}

        data.loc[polygon_id, "geometry"] = shapely.Polygon(exterior, interiors)

    data.geometry = data.geometry.buffer(0)
    data = data[~data.is_empty]
    return data


def layer_to_gdf(layer, feedback):
    geoms = []
    sizes = []
    total = layer.featureCount()
    for i, feature in enumerate(layer.getFeatures()):
        wkt = feature.geometry().asWkt()
        try:
            geoms.append(shapely.wkt.loads(wkt))
        except Exception as e:
            print(e, wkt)
        sizes.append(feature["cellsize"])

        feedback.setProgress(100 * i / total)
        if feedback.isCanceled():
            return {}

    gdf = gpd.GeoDataFrame(geometry=geoms, data={"cellsize": sizes})
    gdf = gdf.explode(ignore_index=True)

    return gdf


# 2D algorithms: https://gmsh.info/doc/texinfo/gmsh.html#Mesh-options
ALGORITHMS = {
    "MeshAdapt": 1,
    "Automatic": 2,
    "Initial mesh only": 3,
    "Delaunay": 5,
    "Frontal-Delaunay": 6,
    "BAMG": 7,
    "Frontal-Delaunay for Quads": 8,
    "Packing of Parallelograms": 9,
    "Quasi-structured Quad": 11,
}


def triangulate_custom(
    source_layer,
    line_anchor_layer=None,
    point_anchor_layer=None,
    algorithm=ALGORITHMS["Frontal-Delaunay"],
    enable_transition=True,
    transition_slope=0.5,
    transition_start=0,
    transition_extent=20,
    feedback=None,
):
    """
    Create the mesh for Iber.
    """

    start = time.time()
    print("Getting data... ", end="")

    data = layer_to_gdf(source_layer, feedback)

    line_anchors = None
    if line_anchor_layer is not None:
        line_anchors = layer_to_gdf(line_anchor_layer, feedback)
    else:
        line_anchors = gpd.GeoDataFrame(
            geometry=[], data={"cellsize": []}, crs=data.crs
        )

    point_anchors = None
    if point_anchor_layer is not None:
        point_anchors = layer_to_gdf(point_anchor_layer, feedback)
    else:
        point_anchors = gpd.GeoDataFrame(
            geometry=[], data={"cellsize": []}, crs=data.crs
        )
    print(f"Done! {time.time() - start}s")

    start = time.time()
    print("Cleaning polygons... ", end="")
    data = clean_geometries(data, feedback)
    print(f"Done! {time.time() - start}s")

    # start = time.time()
    # print("Initializing messher... ", end='')
    try:
        gmsh.finalize()
    except Exception:
        pass

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)

    pm.common.check_geodataframe(data)
    pm.gmsh_geometry.add_geometry(
        data,
        line_anchors,
        point_anchors,
    )

    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", True)
    gmsh.option.setNumber("Mesh.Algorithm", algorithm)

    start = time.time()
    print("Generating Mesh (1/2)... ", end="")
    gmsh.model.mesh.generate(dim=2)
    print(f"Done! {time.time() - start}s")

    if enable_transition:
        start = time.time()
        print("Creating fields... ", end="")
        threshold_ids = []
        for cellsize, features in data.groupby("cellsize"):
            surfaces = features["__polygon_id"]

            dist_field_id = gmsh.model.mesh.field.add("Distance")
            gmsh.model.mesh.field.setNumbers(dist_field_id, "SurfacesList", surfaces)
            gmsh.model.mesh.field.setNumber(dist_field_id, "Sampling", 50)

            thresh_field_id = gmsh.model.mesh.field.add("Threshold")
            gmsh.model.mesh.field.setNumber(thresh_field_id, "InField", dist_field_id)
            gmsh.model.mesh.field.setNumber(
                thresh_field_id, "DistMin", transition_start
            )
            gmsh.model.mesh.field.setNumber(
                thresh_field_id, "DistMax", transition_start + transition_extent
            )
            gmsh.model.mesh.field.setNumber(thresh_field_id, "SizeMin", cellsize)
            gmsh.model.mesh.field.setNumber(
                thresh_field_id,
                "SizeMax",
                cellsize + transition_slope * transition_extent,
            )
            gmsh.model.mesh.field.setNumber(thresh_field_id, "StopAtDistMax", 1)

            const_field_id = gmsh.model.mesh.field.add("Constant")
            gmsh.model.mesh.field.setNumber(const_field_id, "VIn", cellsize)
            gmsh.model.mesh.field.setNumber(const_field_id, "VOut", 1e22)
            gmsh.model.mesh.field.setNumber(const_field_id, "IncludeBoundary", 1)
            gmsh.model.mesh.field.setNumbers(const_field_id, "SurfacesList", surfaces)

            min_field_id = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(
                min_field_id, "FieldsList", [thresh_field_id, const_field_id]
            )
            threshold_ids.append(min_field_id)

        min_field_id = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(min_field_id, "FieldsList", threshold_ids)
        gmsh.model.mesh.field.setAsBackgroundMesh(min_field_id)

        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        print(f"Done! {time.time() - start}s")

        start = time.time()
        print("Generating Mesh (2/2)... ", end="")
        # vertices, triangles = mesher.generate()
        gmsh.model.mesh.generate(dim=2)
        print(f"Done! {time.time() - start}s")
    else:
        print("Skipping step (2/2)")

    start = time.time()
    print("Cleaning up... ", end="")
    # cleaning up of mesh in order to obtain unique elements and nodes
    gmsh.model.mesh.removeDuplicateElements()
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.model.mesh.renumberElements()
    gmsh.model.mesh.renumberNodes()
    print(f"Done! {time.time() - start}s")

    vertices = get_vertices()
    triangles = get_faces()

    print("Done :)")
    # gmsh.fltk.run()

    start = time.time()
    print("Creating temp layer... ", end="")
    poly_layer = QgsVectorLayer("Polygon", "temp", "memory")
    poly_layer.setCrs(source_layer.crs())
    provider = poly_layer.dataProvider()
    provider.addAttributes(
        [
            QgsField("fid", QVariant.Int),
            QgsField("sector_id", QVariant.Int),
            QgsField("scenario_id", QVariant.Int),
            QgsField("vertex_id1", QVariant.Int),
            QgsField("vertex_id2", QVariant.Int),
            QgsField("vertex_id3", QVariant.Int),
            QgsField("vertex_id4", QVariant.Int),
        ]
    )
    poly_layer.updateFields()
    for i, tri in enumerate(triangles):
        if feedback.isCanceled():
            return {}
        feature = QgsFeature()
        feature.setGeometry(
            QgsGeometry.fromPolygonXY(
                [[QgsPointXY(vertices[vert][0], vertices[vert][1]) for vert in tri]]
            )
        )
        feature.setAttributes(
            [
                i + 1,
                1,
                1,
                int(tri[0]) + 1,
                int(tri[1]) + 1,
                int(tri[2]) + 1,
                int(tri[0]) + 1,
            ]
        )
        provider.addFeature(feature)

    # for f in layer.getFeatures():
    #    print("Feature:", f.id(), f.attributes(), f.geometry())
    poly_layer.updateExtents()

    print(f"Done! {time.time() - start}s")

    return poly_layer


@alg(
    name="triangulate_process",
    label="Hopefully triangulate",
    group="drain_scripts",
    group_label="Drain",
)
# 'INPUT' is the recommended name for the main input parameter
@alg.input(type=alg.VECTOR_LAYER, name="INPUT", label="Superficies")
@alg.input(
    type=alg.VECTOR_LAYER, name="LINE_ANCHOR", label="Line Anchors", optional=True
)
@alg.input(
    type=alg.VECTOR_LAYER, name="POINT_ANCHOR", label="Point Anchors", optional=True
)
@alg.input(
    type=alg.ENUM,
    name="ALGORITHM",
    label="Algorithm",
    options=ALGORITHMS.keys(),
    default=4,
)
@alg.input(
    type=alg.BOOL, name="ENABLE_TRANSITION", label="Fancy Transition", default=True
)
@alg.input(
    type=alg.DISTANCE, name="TRANSITION_SLOPE", label="Transition Slope", default=0.5
)
@alg.input(
    type=alg.DISTANCE,
    name="TRANSITION_START",
    label="Transition Start Distance",
    default=0,
)
@alg.input(
    type=alg.DISTANCE, name="TRANSITION_EXTENT", label="Transition Extent", default=20
)
# 'OUTPUT' is the recommended name for the main output parameter
@alg.output(type=alg.VECTOR_LAYER, name="OUTPUT", label="Mesh")
def triangulate_process(instance, parameters, context, feedback, inputs):
    """
    Create the mesh for Iber.
    """

    print(parameters)
    source_layer = instance.parameterAsLayer(parameters, "INPUT", context)
    line_anchor_layer = instance.parameterAsLayer(parameters, "LINE_ANCHOR", context)
    point_anchor_layer = instance.parameterAsLayer(parameters, "POINT_ANCHOR", context)
    algorithm = list(ALGORITHMS.values())[parameters["ALGORITHM"]]
    enable_transition = parameters["ENABLE_TRANSITION"]
    transition_slope = parameters["TRANSITION_SLOPE"]
    transition_start = parameters["TRANSITION_START"]
    transition_extent = parameters["TRANSITION_EXTENT"]
    poly_layer = triangulate_custom(
        source_layer,
        line_anchor_layer,
        point_anchor_layer,
        algorithm,
        enable_transition,
        transition_slope,
        transition_start,
        transition_extent,
        feedback,
    )
    context.temporaryLayerStore().addMapLayer(poly_layer)
    context.addLayerToLoadOnCompletion(
        poly_layer.id(),
        QgsProcessingContext.LayerDetails("MESH_OUTPUT", context.project(), "LAYER"),
    )
    return {"OUTPUT": poly_layer}
