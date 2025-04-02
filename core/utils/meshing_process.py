from qgis.processing import alg
from qgis.core import (
    QgsVectorLayer,
    QgsProcessingContext,
    QgsFeature,
    QgsField,
    QgsTriangle,
    QgsProject,
    QgsPoint,
    QgsFeedback
)

from qgis.PyQt.QtCore import QVariant

from ..utils import Feedback, mesh_parser
import shapely
import shapely.wkt
import numpy as np
import time
import geopandas as gpd
import pandas as pd
from typing import Optional, Iterable
from pathlib import Path
from ... import global_vars

try:
    from packages.gmsh import gmsh
    import pandamesh.common
    import pandamesh.gmsh_geometry

    # From pandamesh
    def get_vertices():
        # getNodes returns: node_tags, coord, parametric_coord
        vertices: np.ndarray
        _, vertices, _ = gmsh.model.mesh.getNodes() # type: ignore
        # Return x and y
        return vertices.reshape((-1, 3))[:, :2]

    # From pandamesh
    def get_faces():
        element_types: np.ndarray
        node_tags: np.ndarray
        element_types, _, node_tags = gmsh.model.mesh.getElements() # type: ignore
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

    def clean_geometries(
            gdf: gpd.GeoDataFrame, tolerance: float, feedback: QgsFeedback
        ) -> Optional[gpd.GeoDataFrame]:
        data: gpd.GeoDataFrame = gdf.copy() # type: ignore

        # Extract vertices from polygons. Keep information on how to reconstruct the polygon
        points = []
        polygon_index = []
        ring = []
        for i in range(len(data)):
            if feedback.isCanceled():
                return None
            geom: shapely.Polygon = data.geometry.iloc[i]
            for p in geom.exterior.coords:
                points.append(shapely.Point(p))
                polygon_index.append(data.index[i])
                ring.append(-1)

            for n, interior in enumerate(geom.interiors):
                for p in interior.coords:
                    points.append(shapely.Point(p))
                    polygon_index.append(data.index[i])
                    ring.append(n)

        vertices = gpd.GeoDataFrame(
            geometry=points,
            data={
                "polygon": polygon_index,
                "ring": ring,
                "moved": False,
                "anchor": False,
            },
        ) # type: ignore

        join: gpd.GeoDataFrame = vertices.sjoin_nearest(
            vertices, max_distance=tolerance, distance_col="dist", exclusive=True
        )
        join = join[join["dist"] > 1e-5] # type: ignore

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
                if not vertices.loc[i, "anchor"]:
                    entry = join.loc[i]
                    other_i = entry["index_right"]

                    vertices.loc[i, "geometry"] = vertices.loc[other_i].geometry
                    vertices.loc[i, "moved"] = True
                    vertices.loc[i, "anchor"] = True
                    vertices.loc[other_i, "anchor"] = True

        # Reconstruct the polygons from the modified vertices
        for polygon_id, group in vertices.groupby("polygon"):
            exterior = group[group["ring"] == -1].geometry
            exterior = [(np.round(p.x, 5), np.round(p.y, 5)) for p in exterior]

            rings = group[group["ring"] != -1].groupby("ring")
            interiors: list[Iterable] = [group.geometry for interior_id, group in rings]
            for i in range(len(interiors)):
                interiors[i] = [
                    (np.round(p.x, 5), np.round(p.y, 5)) for p in interiors[i]
                ]
                if feedback.isCanceled():
                    return None

            data.loc[polygon_id, "geometry"] = shapely.Polygon(exterior, interiors)

        data.geometry = data.geometry.buffer(0)
        data = data[~data.is_empty] # type: ignore
        return data

    def layer_to_gdf(layer: QgsVectorLayer, fields: list = []) -> gpd.GeoDataFrame:
        geoms = []

        data: dict[str, list] = {}
        for field in fields:
            field_index = layer.fields().indexFromName(field)
            if field_index == -1:
                raise ValueError(f"Layer `{layer.name()}` has no field `{field}`")
            data[field] = []
        
        for feature in layer.getFeatures():
            wkt = feature.geometry().asWkt()
            try:
                geoms.append(shapely.wkt.loads(wkt))
            except Exception as e:
                print(e, wkt)

            for field in fields:
                val = feature[field]
                data[field].append(val if val else None)

        gdf = gpd.GeoDataFrame(geometry=geoms, data=data) # type: ignore
        gdf: gpd.GeoDataFrame = gdf.explode(ignore_index=True) # type: ignore
        gdf["geometry"] = gdf["geometry"].normalize() # type: ignore

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
        source_layer: QgsVectorLayer,
        extra_fields: list[str] = [],
        line_anchor_layer: Optional[QgsVectorLayer] = None,
        point_anchor_layer: Optional[QgsVectorLayer] = None,
        do_clean_up: bool = True,
        clean_tolerance: float = 0.5,
        algorithm: int = ALGORITHMS["Frontal-Delaunay"],
        enable_transition: bool = True,
        transition_slope: float = 0.5,
        transition_start: float = 0,
        transition_extent: float = 20,
        feedback: Optional[QgsFeedback] = None,
    ):
        """
        Create the mesh for Iber.
        """

        start = time.time()
        print("Getting data... ", end="")

        fields = ["cellsize"]
        data = layer_to_gdf(source_layer, fields + extra_fields)

        line_anchors = None
        if line_anchor_layer is not None:
            line_anchors = layer_to_gdf(line_anchor_layer, fields)
        else:
            line_anchors = gpd.GeoDataFrame(
                geometry=[], data={"cellsize": []}, crs=data.crs
            ) # type: ignore

        point_anchors = None
        if point_anchor_layer is not None:
            point_anchors = layer_to_gdf(point_anchor_layer, fields)
        else:
            point_anchors = gpd.GeoDataFrame(
                geometry=[], data={"cellsize": []}, crs=data.crs
            ) # type: ignore
        print(f"Done! {time.time() - start}s")

        if do_clean_up:
            start = time.time()
            print("Cleaning polygons... ", end="")
            data = clean_geometries(data, clean_tolerance, feedback)
            print(f"Done! {time.time() - start}s")

        if (
            (feedback is not None and feedback.isCanceled()) or
            data is None
        ):
            return None

        try:
            gmsh.finalize()
        except Exception:
            pass

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 0)

        pandamesh.common.check_geodataframe(data)
        pandamesh.gmsh_geometry.add_geometry(
            data,
            line_anchors,
            point_anchors,
        )

        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", True)
        gmsh.option.setNumber("Mesh.Algorithm", algorithm)

        if feedback is not None:
            feedback.setProgress(10)

        start = time.time()
        print("Generating Mesh (1/2)... ", end="")
        gmsh.model.mesh.generate(dim=2)
        print(f"Done! {time.time() - start}s")

        if feedback is not None:
            feedback.setProgress(50)

        if enable_transition:
            start = time.time()
            print("Creating fields... ", end="")
            threshold_ids = []
            for cellsize, features in data.groupby("cellsize"):
                surfaces = features["__polygon_id"]

                dist_field_id = gmsh.model.mesh.field.add("Distance")
                gmsh.model.mesh.field.setNumbers(
                    dist_field_id, "SurfacesList", surfaces
                )
                gmsh.model.mesh.field.setNumber(dist_field_id, "Sampling", 50)

                thresh_field_id = gmsh.model.mesh.field.add("Threshold")
                gmsh.model.mesh.field.setNumber(
                    thresh_field_id, "InField", dist_field_id
                )
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
                gmsh.model.mesh.field.setNumbers(
                    const_field_id, "SurfacesList", surfaces
                )

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

        if feedback is not None:
            feedback.setProgress(95)

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

        extra_data = {
            field: np.empty(len(triangles), dtype=np.object_)
            for field in extra_fields
        }

        start = 0
        for i, feature in data.iterrows():
            element_types, element_tags, _ = gmsh.model.mesh.getElements(2, feature["__polygon_id"])
            _TRIANGLE = 2
            # List of triangles in the polygon
            tri = element_tags[np.where(element_types == _TRIANGLE)[0][0]]
            for field in extra_fields:
                extra_data[field][start : start + len(tri)] = feature[field]
            start += len(tri)

        if feedback is not None:
            feedback.setProgress(100)

        return triangles, vertices, extra_data

except ImportError:

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

    def triangulate_custom(*args):
        pass


import shapely

def create_temp_mesh_layer(mesh: mesh_parser.Mesh, feedback: Optional[Feedback] = None) -> QgsVectorLayer:
    c1 = mesh.vertices.loc[mesh.polygons["v1"], ['x', 'y', 'z']]
    c2 = mesh.vertices.loc[mesh.polygons["v2"], ['x', 'y', 'z']]
    c3 = mesh.vertices.loc[mesh.polygons["v3"], ['x', 'y', 'z']]

    c1.columns = ["x1", "y1", "z1"]
    c2.columns = ["x2", "y2", "z2"]
    c3.columns = ["x3", "y3", "z3"]

    c1.index = mesh.polygons.index
    c2.index = mesh.polygons.index
    c3.index = mesh.polygons.index

    optmized_df = pd.concat([mesh.polygons, c1, c2, c3], axis=1)

    v1x = optmized_df['x2'] - optmized_df['x1']
    v1y = optmized_df['y2'] - optmized_df['y1']
    v2x = optmized_df['x3'] - optmized_df['x1']
    v2y = optmized_df['y3'] - optmized_df['y1']

    det = v1x * v2y - v1y * v2x
    optmized_df['is_ccw'] = det > 0

    def get_feature(row):
        geom = QgsTriangle(
            QgsPoint(row.x1, row.y1, row.z1),
            QgsPoint(row.x2, row.y2, row.z2),
            QgsPoint(row.x3, row.y3, row.z3),
        )
        feature = QgsFeature()
        feature.setGeometry(geom)
        feature.setAttributes([
            row.Index,
            row.category,
            row.v1, row.v2, row.v3, row.v4,
            row.roughness,
            row.scs_cn,
            row.is_ccw
        ])
        return feature

    features = map(get_feature, optmized_df.itertuples())

    layer = QgsVectorLayer("Polygon", "Mesh Temp Layer", "memory")
    layer.setCrs(QgsProject.instance().crs())
    provider = layer.dataProvider()
    fields = [
        QgsField("fid", QVariant.Int),
        QgsField("category", QVariant.String),
        QgsField("vertex_id1", QVariant.Int),
        QgsField("vertex_id2", QVariant.Int),
        QgsField("vertex_id3", QVariant.Int),
        QgsField("vertex_id4", QVariant.Int),
        QgsField("roughness", QVariant.Double),
        QgsField("scs_cn", QVariant.Double),
        QgsField("is_ccw", QVariant.Bool),
    ]
    provider.addAttributes(fields)
    layer.updateFields()

    provider.addFeatures(features)

    layer.updateExtents()

    # Set the style of the layer
    relative_style_path = "resources/templates/mesh_temp_layer.qml"
    style_path = Path(global_vars.plugin_dir) / relative_style_path
    layer.loadNamedStyle(str(style_path))
    layer.triggerRepaint()

    return layer



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
