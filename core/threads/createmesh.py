import traceback

from geopandas import gpd
from qgis.core import (
    QgsCoordinateTransform,
    QgsFeedback,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProcessingFeatureSourceDefinition,
)
from qgis.utils import iface
import shapely

from . import createmesh_core as core
from .validatemesh import validate_input_layers, validate_inlets_in_triangles
from .task import DrTask
from ..utils import mesh_parser
from ..utils.meshing_process import triangulate_custom, create_temp_mesh_layer, layer_to_gdf
from ... import global_vars
from ...lib import tools_qgis, tools_qt

from typing import Union, Literal, Optional
import time
import numpy as np
import pandas as pd
import processing
import bisect


class DrCreateMeshTask(DrTask):
    def __init__(
        self,
        description,
        execute_validations: list[str],
        clean_geometries: bool,
        clean_tolerance: float,
        only_selected_features: bool,
        enable_transition: bool,
        transition_slope: float,
        transition_start: float,
        transition_extent: float,
        dem_layer: Union[QgsRasterLayer, None],
        roughness_layer: Union[QgsRasterLayer, Literal["ground_layer"], None],
        losses_layer: Union[QgsRasterLayer, Literal["ground_layer"], None],
        mesh_name: str,
        point_anchor_layer: QgsVectorLayer,
        line_anchor_layer: QgsVectorLayer,
        bridge_layer: QgsVectorLayer,
        feedback: QgsFeedback,
        ground_layer: QgsVectorLayer,
        roof_layer: QgsVectorLayer,
        inlet_layer: QgsVectorLayer,
        temporal_mesh: bool,
        temp_layer_name: str
    ):
        super().__init__(description)
        self.execute_validations = execute_validations
        self.clean_geometries = clean_geometries
        self.clean_tolerance = clean_tolerance
        self.only_selected_features = only_selected_features
        self.enable_transition = enable_transition
        self.transition_slope = transition_slope
        self.transition_start = transition_start
        self.transition_extent = transition_extent
        self.dem_layer = dem_layer
        self.roughness_layer: Union[QgsRasterLayer, Literal["ground_layer"], None] = roughness_layer
        self.losses_layer: Union[QgsRasterLayer, Literal["ground_layer"], None] = losses_layer
        self.mesh_name = mesh_name
        self.feedback = feedback
        self.point_anchor_layer = point_anchor_layer
        self.line_anchor_layer = line_anchor_layer
        self.bridge_layer = bridge_layer
        self.error_layers = None
        self.warning_layers = None
        self.ground_layer = ground_layer
        self.roof_layer = roof_layer
        self.inlet_layer = inlet_layer
        self.temporal_mesh = temporal_mesh
        self.temp_layer: Optional[QgsVectorLayer] = None
        self.temp_layer_name = temp_layer_name

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self) -> bool:
        super().run()
        try:
            self.feedback.setProgressText("Starting process!")
            self.temp_layer = None

            if not self.temporal_mesh:
                # Remove previous temp layers
                project = QgsProject.instance()
                layer_ids = (x.id() for x in project.mapLayersByName("Mesh Temp Layer"))
                project.removeMapLayers(layer_ids)
                group_name = "MESH INPUTS ERRORS & WARNINGS"
                temp_group = tools_qgis.find_toc_group(project.layerTreeRoot(), group_name)
                if temp_group is not None:
                    project.removeMapLayers(temp_group.findLayerIds())

            # Load input layers
            self.dao = global_vars.gpkg_dao_data.clone()
            db_path = self.dao.db_filepath.replace('\\', '/')
            path = f"{db_path}|layername="

            layers: dict[str, Union[QgsVectorLayer, QgsRasterLayer]] = {}

            layers = {
                "ground": self.ground_layer,
                "roof": self.roof_layer,
                "inlet": self.inlet_layer,
                # "bridge": self.bridge_layer,
                # "mesh_anchor_points": self.point_anchor_layer
            }

            layers["dem"] = self.dem_layer

            # Validate missing ground roughness values
            if self.roughness_layer == "ground_layer":
                rows = self.dao.get_rows(
                    "SELECT fid FROM ground WHERE landuse IS NULL AND custom_roughness IS NULL"
                )
                if rows is not None and len(rows) > 0:
                    self.message = "Roughness information missing in following objects in Ground layer: "
                    self.message += ", ".join(str(row["fid"]) for row in rows)
                    self.message += ". Review your data and try again."
                    return False

            # Validate that ground layer bbox is inside landuse bbox
            if isinstance(self.roughness_layer, QgsRasterLayer):
                lu_extent = self.roughness_layer.extent()
                gr_extent = layers["ground"].extent()
                if not lu_extent.contains(gr_extent):
                    self.message = "The selected landuse layer does not contains the area of Ground layer."
                    return False

            # Validate landuses roughness values
            if self.roughness_layer is not None:
                print("Validating landuses... ", end="")
                start = time.time()

                rows = self.dao.get_rows("SELECT id, idval, manning FROM cat_landuses")
                landuses_df = pd.DataFrame(
                    rows, columns=["id", "idval", "manning"]
                ).set_index("id")
                missing_roughness = []

                if self.roughness_layer == "ground_layer":
                    rows = self.dao.get_rows(
                        "SELECT DISTINCT landuse FROM ground WHERE landuse IS NOT NULL AND custom_roughness IS NULL"
                    )
                    used_landuses = [] if rows is None else [row[0] for row in rows]

                    missing_roughness = [
                        l
                        for l in used_landuses
                        if l not in landuses_df["idval"].values
                        or landuses_df[landuses_df["idval"] == l]["manning"]
                        .isna()
                        .any()
                    ]
                else:
                    rows = self.roughness_layer.height()
                    cols = self.roughness_layer.width()
                    provider = self.roughness_layer.dataProvider()
                    bl = provider.block(1, provider.extent(), cols, rows)
                    unique_values = set(
                        [bl.value(r, c) for r in range(rows) for c in range(cols)]
                    )
                    used_landuses = {int(x) for x in unique_values if x != 255}
                    missing_roughness = [
                        str(l)
                        for l in used_landuses
                        if l not in landuses_df.index
                        or np.isnan(landuses_df.loc[l, "manning"])
                    ]

                print(f"Done! {time.time() - start}s")

                if missing_roughness:
                    self.message = "The following landuses are used, but don't have a value for roughness: "
                    self.message += f"{', '.join(missing_roughness)}. "
                    self.message += (
                        "Please, verify the 'cat_landuses' table and try again."
                    )
                    return False

            # Validate missing ground losses values
            if self.losses_layer == "ground_layer":
                rows = self.dao.get_rows(
                    "SELECT fid FROM ground WHERE scs_cn IS NULL"
                )
                if len(rows):
                    self.message = "Losses information ('scs_cn' column) missing in following objects in Ground layer: "
                    self.message += ", ".join(str(row["fid"]) for row in rows)
                    self.message += ". Review your data and try again."
                    return False

            # Validate that ground layer bbox is inside landuse bbox
            if isinstance(self.losses_layer, QgsRasterLayer):
                ll_extent = self.losses_layer.extent()
                gr_extent = layers["ground"].extent()
                if not ll_extent.contains(gr_extent):
                    self.message = "The selected losses layer does not contains the area of Ground layer."
                    return False

            self.feedback.setProgress(5)

            # Validate inputs
            if self.execute_validations:
                self.feedback.setProgressText("Validating inputs...")
                validation_layers = validate_input_layers(
                    layers, self.execute_validations, self.feedback
                )
                if self.feedback.isCanceled() or validation_layers is None:
                    self.message = "Task canceled."
                    return False

                self.error_layers, self.warning_layers = validation_layers

                if self.error_layers:
                    self.message = "There are errors in input data. Please, check the error layers."
                    self.feedback.setProgress(100)
                    return False

            point_anchors = None
            line_anchors = None
            bridge_layer = self.bridge_layer
            complete_line_anchors = None

            if not self.temporal_mesh:
                # Create anchor GeoDataFrames
                print("Creating anchor GeoDataFrames... ", end="")
                start = time.time()

                point_anchor_layer = self.point_anchor_layer
                line_anchor_layer = self.line_anchor_layer

                if self.only_selected_features:
                    point_anchor_layer = processing.run(
                        "native:intersection",
                        {
                            'INPUT': self.point_anchor_layer,
                            'OVERLAY': QgsProcessingFeatureSourceDefinition(
                                layers["ground"].source(),
                                selectedFeaturesOnly=True,
                            ),
                            'OUTPUT':'TEMPORARY_OUTPUT',
                        }
                    )['OUTPUT']

                    line_anchor_layer = processing.run(
                        "native:intersection",
                        {
                            'INPUT': self.line_anchor_layer,
                            'OVERLAY': QgsProcessingFeatureSourceDefinition(
                                layers["ground"].source(),
                                selectedFeaturesOnly=True,
                            ),
                            'OUTPUT':'TEMPORARY_OUTPUT',
                        }
                    )['OUTPUT']

                    bridge_layer = processing.run(
                        "native:intersection",
                        {
                            'INPUT': self.bridge_layer,
                            'OVERLAY': QgsProcessingFeatureSourceDefinition(
                                layers["ground"].source(),
                                selectedFeaturesOnly=True,
                            ),
                            'OUTPUT':'TEMPORARY_OUTPUT',
                        }
                    )['OUTPUT']

                point_anchors = layer_to_gdf(
                    point_anchor_layer,
                    ["cellsize", "z_value"],
                )

                line_anchors = layer_to_gdf(
                    line_anchor_layer,
                    ["cellsize"],
                )

                complete_line_anchors = self._create_line_anchors_gdf(line_anchors, bridge_layer)

                print(f"Done! {time.time() - start}s")

            # Create mesh
            self.feedback.setProgressText("Creating ground mesh...")
            self.feedback.setProgress(15)
            gt_feedback = QgsFeedback()
            gt_progress = lambda x: self.feedback.setProgress(x / 100 * (30 - 15) + 15)
            gt_feedback.progressChanged.connect(gt_progress)

            ground_triangulation_result = triangulate_custom(
                layers["ground"],
                ["custom_roughness", "landuse", "scs_cn"],
                point_anchors=point_anchors,
                line_anchors=complete_line_anchors,
                do_clean_up=self.clean_geometries,
                only_selected_features=self.only_selected_features,
                clean_tolerance=self.clean_tolerance,
                enable_transition=self.enable_transition,
                transition_slope=self.transition_slope,
                transition_start=self.transition_start,
                transition_extent=self.transition_extent,
                feedback=gt_feedback,
            )
            if self.feedback.isCanceled() or ground_triangulation_result is None:
                self.message = "Task canceled."
                return False

            triangles, vertices, extra_data = ground_triangulation_result

            # Triangles
            ground_triangles_df = pd.DataFrame(triangles, columns=["v1", "v2", "v3"], dtype=np.uint32)
            ground_triangles_df["v4"] = ground_triangles_df["v1"]
            ground_triangles_df["category"] = "ground"
            ground_triangles_df["landuse"] = extra_data["landuse"]
            ground_triangles_df["custom_roughness"] = extra_data["custom_roughness"]
            ground_triangles_df["scs_cn"] = extra_data["scs_cn"]

            # Get ground roughness
            roughness_from_raster = False
            if self.roughness_layer is None:  # Fill with zeros
                ground_triangles_df["roughness"] = 0
            elif self.roughness_layer == "ground_layer":  # From ground layer
                print("Getting roughness from ground layer... ", end="")
                start = time.time()

                def get_roughness(row):
                    custom_roughness = row["custom_roughness"]
                    if custom_roughness is None or np.isnan(custom_roughness):
                        return landuses_df.loc[landuses_df['idval'] == row["landuse"], 'manning'].values[0]
                    else:
                        return row["custom_roughness"]

                # TODO: Try to not use apply
                # ground_triangles_df["roughness"] = ground_triangles_df["custom_roughness"].fillna()
                ground_triangles_df["roughness"] = ground_triangles_df.apply(get_roughness, axis=1)
                print(f"Done! {time.time() - start}s")
            else:  # From raster layer
                ground_triangles_df["roughness"] = np.nan
                roughness_from_raster = True

            ground_triangles_df = ground_triangles_df.drop(columns=["landuse", "custom_roughness"])

            # Get ground losses
            losses_from_raster = False
            losses_data = {}
            if self.losses_layer is None:
                losses_data = {"method": 0}
            else:
                rows = self.dao.get_rows("""
                    SELECT parameter, value 
                    FROM config_param_user 
                    WHERE parameter IN [
                        'options_losses_method',
                        'options_losses_scs_cn_multiplier',
                        'options_losses_scs_ia_coefficient',
                        'options_losses_starttime'
                    ]
                """)
                params = {}
                if rows is not None:
                    params = {row["parameter"]: row["value"] for row in rows}

                cn_mult = params.get("options_losses_scs_cn_multiplier") or -9999
                ia_coef = params.get("options_losses_scs_ia_coefficient") or -9999
                new_var = params.get("options_losses_starttime") or -9999
                losses_data = {
                    "method": 2,
                    "cn_multiplier": cn_mult,
                    "ia_coefficient": ia_coef,
                    "start_time": new_var,
                }

                if self.losses_layer == "ground_layer":  # From ground layer
                    pass  # already calculated
                else:  # From raster layer
                    losses_from_raster = True

            # Vertices
            ground_vertices_df = pd.DataFrame(vertices, columns=["x", "y"])
            ground_vertices_df["category"] = "ground"

            # Get z-values from DEM
            if self.dem_layer is None:
                ground_vertices_df["z"] = 0
            else:
                print("Getting z-values from DEM... ", end="")
                start = time.time()

                ground_crs = layers["ground"].crs()
                dem_crs = self.dem_layer.crs()
                qct = QgsCoordinateTransform(ground_crs, dem_crs, QgsProject.instance())

                def get_z(x, y):
                    point = qct.transform(QgsPointXY(x, y))
                    val, res = self.dem_layer.dataProvider().sample(point, 1)
                    return val if res else 0

                ground_vertices_df["z"] = ground_vertices_df.apply(lambda row: get_z(row["x"], row["y"]), axis=1)

                print(f"Done! {time.time() - start}s")

            if not self.temporal_mesh:
                print(f"Setting z-values from anchors... ", end="")
                start = time.time()

                # Get z-values from point anchors
                for _, anchor in point_anchors.iterrows():
                    x, y = anchor.geometry.x, anchor.geometry.y
                    mask = (ground_vertices_df["x"] == x) & (ground_vertices_df["y"] == y)
                    ground_vertices_df.loc[mask, "z"] = anchor["z_value"]

                # Get z-values from line anchors
                for _, line in line_anchors.iterrows():
                    line_geom = line.geometry.buffer(0.01)  # Buffer to avoid precision issues with the intersect
                    ground_vertices_geom = gpd.GeoSeries(
                        [shapely.Point(xy) for xy in zip(ground_vertices_df["x"], ground_vertices_df["y"])],
                        crs=line_anchors.crs
                    )
                    mask = ground_vertices_geom.intersects(line_geom)
                    points = ground_vertices_df[mask] # Get points inside the line anchor
                    points = gpd.GeoDataFrame(points, geometry=ground_vertices_geom[mask], crs=line_anchors.crs)

                    # Ignoring the z value, get the distance along the line, then interpolate the z value
                    line_2d = shapely.force_2d(line.geometry)

                    # TODO: If the line vertex z value is 0, set its value to the z value of the point directly below it.
                    # this way we can have lines with values set and unset at the same time and it will work properly
                    def interpolate_z(row):
                        p = row["geometry"]
                        dist = line_2d.project(p)
                        anchor_z = line.geometry.interpolate(dist).z
                        if anchor_z != 0:
                            return anchor_z
                        else:
                            return row["z"]

                    z_values = points.apply(interpolate_z, axis=1)

                    ground_vertices_df.loc[points.index, "z"] = z_values

                print(f"Done! {time.time() - start}s")

            print("Triangulating Roofs... ", end="")
            start = time.time()
            self.feedback.setProgressText("Creating roof mesh...")
            self.feedback.setProgress(30)
            roof_triangulation_result = core.triangulate_roof(layers["roof"], self.only_selected_features, self.feedback)

            if self.feedback.isCanceled() or roof_triangulation_result is None:
                self.message = "Task canceled."
                return False

            roof_vertices_df, roof_triangles_df = roof_triangulation_result

            if not roof_vertices_df.empty and not roof_triangles_df.empty:
                roof_triangles_df["v1"] += len(ground_vertices_df)
                roof_triangles_df["v2"] += len(ground_vertices_df)
                roof_triangles_df["v3"] += len(ground_vertices_df)
                roof_triangles_df["v4"] += len(ground_vertices_df)

            # To avoid changing the type of the column when concatenating,
            # if not, the nan's change the datatype of the column to object
            ground_triangles_df["roof_id"] = -1

            print(f"Done! {time.time() - start}s")

            vertices_df = pd.concat([ground_vertices_df, roof_vertices_df], ignore_index=True)
            triangles_df = pd.concat([ground_triangles_df, roof_triangles_df], ignore_index=True)

            vertices_df.index += 1
            triangles_df.index += 1
            triangles_df["v1"] += 1
            triangles_df["v2"] += 1
            triangles_df["v3"] += 1
            triangles_df["v4"] += 1

            triangles_df["v2"], triangles_df["v3"] = triangles_df["v3"], triangles_df["v2"]

            # Get roofs
            print("Creating roofs DataFrame... ", end="")
            start = time.time()

            self.feedback.setProgressText("Getting roof data...")
            rows = self.dao.get_rows("""
                SELECT 
                    code, fid, slope, width, roughness, isconnected,
                    outlet_code, outlet_vol, street_vol, infiltr_vol
                FROM roof
            """)

            roofs_df = pd.DataFrame(rows, columns=[
                "code", "fid", "slope", "width", "roughness", "isconnected",
                "outlet_code", "outlet_vol", "street_vol", "infiltr_vol"
            ])
            if not roofs_df.empty:
                roofs_df["name"] = roofs_df["code"].combine_first(roofs_df["fid"])
                roofs_df.index = roofs_df["fid"]  # type: ignore

            print(f"Done! {time.time() - start}s")

            bridges_df: pd.DataFrame = pd.DataFrame()
            if bridge_layer is not None:
                print("Creating bridges DataFrame... ", end="")
                start = time.time()
                bridges_df = self._create_bridges_df(triangles_df, vertices_df, bridge_layer)
                print(f"Done! {time.time() - start}s")

            self.mesh = mesh_parser.Mesh(
                polygons=triangles_df,
                vertices=vertices_df,
                roofs=roofs_df,
                losses=losses_data,
                boundary_conditions={},
                bridges=bridges_df
            )

            # Create temp layer
            self.feedback.setProgressText("Creating temp layer for visualization...")
            start = time.time()
            print("Creating temp layer... ", end="")
            temp_layer = create_temp_mesh_layer(self.mesh, layer_name=self.temp_layer_name)
            print(f"Done! {time.time() - start}s")

            if roughness_from_raster:
                self.feedback.setProgressText("Getting ground roughness from raster...")
                print("Getting ground roughness from raster... ", end="")
                start = time.time()

                fids, landuses = core.execute_ground_zonal_statistics(temp_layer, self.roughness_layer)
                roughness = landuses_df.loc[landuses, "manning"].values
                triangles_df.loc[fids, "roughness"] = roughness

                print(f"Done! {time.time() - start}s")

            if losses_from_raster:
                self.feedback.setProgressText("Getting ground losses from raster...")
                print("Getting ground losses from raster... ", end="")
                start = time.time()

                fids, scs_cn = core.execute_ground_zonal_statistics(temp_layer, self.roughness_layer)
                triangles_df.loc[fids, "scs_cn"] = scs_cn

                print(f"Done! {time.time() - start}s")

            if losses_from_raster or roughness_from_raster:
                self.feedback.setProgressText("Refreshing temp layer...")
                start = time.time()
                print("Recreating temp layer... ", end="")
                temp_layer = create_temp_mesh_layer(self.mesh, layer_name=self.temp_layer_name)
                print(f"Done! {time.time() - start}s")

            if not self.temporal_mesh:
                # Delete old mesh
                self.feedback.setProgressText("Saving mesh to GPKG file...")
                self.dao.execute_sql(f"""
                    DELETE FROM cat_file
                    WHERE name = '{self.mesh_name}'
                """)

                print("Dumping mesh data... ", end="")
                start = time.time()
                mesh_str, roof_str, losses_str, bridges_str = mesh_parser.dumps(self.mesh)
                print(f"Done! {time.time() - start}s")

                self.dao.execute_sql(f"""
                    INSERT INTO cat_file (name, iber2d, roof, losses, bridge)
                    VALUES ('{self.mesh_name}', '{mesh_str}', '{roof_str}', '{losses_str}', '{bridges_str}')
                """)

            self.feedback.setProgress(80)

            self.temp_layer = temp_layer

            if self.inlet_layer is not None:
                # Check for triangles with more than one inlet
                inlet_warning = validate_inlets_in_triangles(temp_layer, layers["inlet"])
                if inlet_warning.hasFeatures():
                    group_name = "MESH INPUTS ERRORS & WARNINGS"
                    tools_qt.add_layer_to_toc(inlet_warning, group_name, create_groups=True)
                    project.layerTreeRoot().removeChildrenGroupWithoutLayers()
                    iface.layerTreeView().model().sourceModel().modelReset.emit()

                # Refresh TOC
                iface.layerTreeView().model().sourceModel().modelReset.emit()

            self.message = "Process finished!!!"
            if not self.temporal_mesh:
                self.feedback.setProgress(100)
            return True
        except Exception:
            self.exception = traceback.format_exc()
            self.message = (
                "Task failed. See the Log Messages Panel for more information."
            )
            self.temp_layer = None
            return False

    def _create_line_anchors_gdf(self, line_anchors: gpd.GeoDataFrame, bridge_layer: QgsVectorLayer) -> gpd.GeoDataFrame:
        line_anchors = line_anchors.copy()
        line_anchors["geometry"] = line_anchors["geometry"].force_2d()

        bridges = layer_to_gdf(
            bridge_layer,
            ["code"],
            do_normalize=False
        )

        if len(bridges) == 0:
            print("No bridges found in the bridge layer.")
            return line_anchors

        rows = self.dao.get_rows(f"""
            SELECT bridge_code, distance
            FROM bridge_value
            ORDER BY distance
        """)
        distances = pd.DataFrame(rows, columns=["bridge_code", "distance"])
        # Normalize distances by bridge length
        for value in distances.itertuples():
            bridge = self.dao.get_row(f"SELECT length FROM bridge WHERE code = '{value.bridge_code}'")
            if bridge is not None:
                distances.loc[value.Index, "distance"] = round(value.distance / bridge[0], 3)
        distances = distances.set_index("bridge_code")
        distances = distances.groupby("bridge_code")["distance"].apply(list)

        bridges.set_index("code", inplace=True)

        bridges["distance"] = bridges.index.map(distances)

        def make_bridge(row):
            line: shapely.LineString = row["geometry"]
            total_length = line.length

            distances = set()

            db_distances = row["distance"]
            if isinstance(db_distances, list):
                distances.update(db_distances)

            for vert in line.coords:
                dist = line.project(shapely.Point(vert)) / total_length
                distances.add(dist)

            points = []
            for distance in sorted(distances):
                point = line.interpolate(distance, normalized=True)
                points.append(point)

            geom = shapely.LineString(points)
            return geom

        bridges["geometry"] = bridges.apply(make_bridge, axis=1)
        bridges = bridges.drop(columns=["distance"])

        bridges["cellsize"] = np.inf # Infinity so that it will not affect the triangulation (keeps the minimum cell size)

        return pd.concat([line_anchors, bridges], ignore_index=True) # type: ignore


    def _create_bridges_df(self, polygons_df: pd.DataFrame, vertices_df: pd.DataFrame, bridge_layer: QgsVectorLayer) -> pd.DataFrame:
        bridges = layer_to_gdf(
            bridge_layer,
            ["code", "freeflow_cd", "deck_cd", "sumergeflow_cd", "gaugenumber"],
        )
        bridges_values_dict = self.get_bridges_values_dict()

        # Create a DataFrame with the tiangles and its vertices position (optimized_df)
        polygons_df = polygons_df[polygons_df["category"] == "ground"].copy()

        c1 = vertices_df.loc[polygons_df["v1"], ['x', 'y', 'z']]
        c2 = vertices_df.loc[polygons_df["v2"], ['x', 'y', 'z']]
        c3 = vertices_df.loc[polygons_df["v3"], ['x', 'y', 'z']]

        c1.columns = ["x1", "y1", "z1"]
        c2.columns = ["x2", "y2", "z2"]
        c3.columns = ["x3", "y3", "z3"]

        c1.index = polygons_df.index
        c2.index = polygons_df.index
        c3.index = polygons_df.index

        optimized_df = pd.concat([polygons_df, c1, c2, c3], axis=1)

        # We create a DataFrame with the geometry of the triangles simplified to only the vertices (optimized_gdf)
        # This will be used to check intersections with the bridges
        coords = optimized_df[['x1','y1','x2','y2','x3','y3']].to_numpy()
        vertices_geom = shapely.multipoints(coords.reshape(-1, 3, 2))

        # We explode the MultiPoint geometries to create a GeoDataFrame with individual points
        # index_parts=True ensures that we know the order of the points in the original triangles
        # The index will have two levels: the triangle index and the point index (0, 1, 2)
        optimized_gdf = gpd.GeoDataFrame(
            optimized_df,
            geometry=vertices_geom
        ).explode(index_parts=True)

        # Now we can check for intersections with the bridges
        bridge_list = []  # Here we will store the bridge features
        for bridge in bridges.itertuples():
            bridge_geom: shapely.LineString = bridge.geometry

            bridge_geom_buf = bridge_geom.buffer(0.01)
            touching = optimized_gdf[
                optimized_gdf.intersects(bridge_geom_buf)
            ]

            # Segment the bridge geometry into straight segments so that only with the segments
            # we can check for touching edge only by knowing which vertices are touching
            segments = map(shapely.LineString, zip(bridge_geom.coords[:-1], bridge_geom.coords[1:]))
            for segment_geom in segments:

                mask = touching.intersects(segment_geom.buffer(0.01))
                segment_touching = touching[mask]

                for idx, group in segment_touching.groupby(level=0):
                    side = -1
                    if len(group) == 2:
                        verts = group.index.get_level_values(1).to_list()
                        # verts.sort()  # Sorting should not be necessary, as the order is already defined by the index
                        if verts == [0, 1]:
                            side = 1
                        elif verts == [1, 2]:
                            side = 2
                        elif verts == [0, 2]:
                            side = 3
                    else:
                        if len(group) > 2:
                            raise ValueError(f"Found more than 2 vertices in group {group.index}. This is unexpected.")

                        continue

                    assert side != -1, f"Side not found for group {group.index}"

                    # Get the relative distance along the bridge segment
                    # We will get the middle point of the edge to calculate the distance
                    v1 = group.iloc[0].geometry
                    v2 = group.iloc[1].geometry
                    mid_point = shapely.Point(
                        (v1.x + v2.x) / 2,
                        (v1.y + v2.y) / 2
                    )

                    # Get the absolute distance along the line to the point
                    relative_distance = bridge_geom.project(mid_point, normalized=True)

                    # Get bridge values based on code and distance
                    bridge_values = None
                    if bridge.code in bridges_values_dict:
                        values = bridges_values_dict[bridge.code]
                        # Extract the distances for bisect
                        distances = [v["distance"] for v in values]
                        index = bisect.bisect_right(distances, relative_distance)
                        bridge_values = values[index - 1] if index > 0 else None
                        bridge_next_value = values[index] if index < len(values) else None
                    else:
                        bridge_values = None
                        bridge_next_value = None

                    # Set values from bridge_values if found, otherwise use defaults
                    lowerdeckelev = (bridge_values["lowelev"]+bridge_next_value["lowelev"])/2 if bridge_values and bridge_next_value else None
                    bridgeopeningpercent = (bridge_values["openingval"]) if bridge_values else None
                    topelevn = (bridge_values["topelev"]+bridge_next_value["topelev"])/2 if bridge_values and bridge_next_value else None

                    freepressureflowcd = bridge.freeflow_cd
                    deckcd = bridge.deck_cd
                    sumergeflowcd = bridge.sumergeflow_cd
                    gaugenumber = bridge.gaugenumber


                    feature_list = [
                        idx,
                        side,
                        1,
                        -999,
                        lowerdeckelev,
                        bridgeopeningpercent,
                        freepressureflowcd,
                        topelevn,
                        100,
                        deckcd,
                        sumergeflowcd,
                        gaugenumber,
                        0,
                        0,
                        0,
                        0,
                        0
                    ]
                    bridge_list.append(feature_list)

        bridges_df = pd.DataFrame(bridge_list, columns=["element_id", "side", "num1", "num2", "lowerdeckelev", "bridgeopeningpercent", "freepressureflowcd", "topelevn", "num3", "deckcd", "sumergeflowcd", "gaugenumber", "num4", "num5", "num6", "num7", "num8"])

        return bridges_df

    def get_bridges_values_dict(self):
        bridge_values_dict = {}
        rows = self.dao.get_rows("SELECT * FROM bridge_value ORDER BY bridge_code, distance ASC")
        for value in rows:
            bridge = self.dao.get_row(f"SELECT length FROM bridge WHERE code = '{value['bridge_code']}'")
            if bridge is not None:
                length = bridge[0]
            else:
                continue

            if value["bridge_code"] not in bridge_values_dict.keys():
                bridge_values_dict[value["bridge_code"]] = []
            bridge_values_dict[value["bridge_code"]].append({
                "distance": round(value["distance"] / length, 3),
                "topelev": value["topelev"],
                "lowelev": value["lowelev"],
                "openingval": value["openingval"]
            })
        return bridge_values_dict
