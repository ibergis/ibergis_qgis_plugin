import traceback
from pathlib import Path
from itertools import chain, tee

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeedback,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsField,
    QgsPoint,
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsProcessingContext,
    QgsProcessing
)
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant

from . import createmesh_core as core
from .validatemesh import validate_input_layers, validate_inlets_in_triangles
from .task import DrTask
from ..utils import mesh_parser
from ..utils.meshing_process import triangulate_custom, create_temp_mesh_layer, layer_to_gdf
from ... import global_vars
from ...lib import tools_qgis, tools_qt

from typing import Union, Optional, Literal
import time
import numpy as np
import pandas as pd
import processing

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
        feedback: QgsFeedback,
        point_anchor_layer: Optional[QgsVectorLayer] = None,
        line_anchor_layer: Optional[QgsVectorLayer] = None,
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
        self.error_layers = None
        self.warning_layers = None

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self) -> bool:
        super().run()
        try:
            self.feedback.setProgressText("Starting process!")

            # Remove previous temp layers
            project = QgsProject.instance()
            layer_ids = (x.id() for x in project.mapLayersByName("Mesh Temp Layer"))
            project.removeMapLayers(layer_ids)
            group_name = "Mesh inputs errors & warnings"
            temp_group = tools_qgis.find_toc_group(project.layerTreeRoot(), group_name)
            if temp_group is not None:
                project.removeMapLayers(temp_group.findLayerIds())

            # Load input layers
            self.dao = global_vars.gpkg_dao_data.clone()
            db_path = self.dao.db_filepath.replace('\\', '/')
            path = f"{db_path}|layername="


            layers: dict[str, Union[QgsVectorLayer, QgsRasterLayer]] = {}

            # Load ground and roof layers from the QGIS project
            for layer in ["ground", "roof"]:
                layer_path = f"{path}{layer}"
                lyrs = []
                for lyr in QgsProject.instance().mapLayers().values():
                    if lyr.source() == layer_path:
                        print(f"Layer: {lyr.name()} - {lyr.source()}")
                        lyrs.append(lyr)

                if len(lyrs) == 0:
                    self.message = f"Layer '{layer}' not found in the QGIS project."
                    return False
                elif len(lyrs) > 1:
                    self.message = f"Layer '{layer}' found multiple times in the QGIS project."
                    return False
                else:
                    layers[layer] = lyrs[0]

            # Load other layers from the GPKG file
            layers_to_select = ["mesh_anchor_points", "inlet", "bridge"]
            for layer in layers_to_select:
                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False
                l = QgsVectorLayer(f"{path}{layer}", layer, "ogr")
                if not l.isValid():
                    self.message = f"Layer '{layer}' is not valid. Check if GPKG file has a '{layer}' layer."
                    return False
                layers[layer] = l

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

            # Create mesh
            self.feedback.setProgressText("Creating ground mesh...")
            self.feedback.setProgress(15)
            gt_feedback = QgsFeedback()
            gt_progress = lambda x: self.feedback.setProgress(x / 100 * (30 - 15) + 15)
            gt_feedback.progressChanged.connect(gt_progress)

            ground_triangulation_result = triangulate_custom(
                layers["ground"],
                ["custom_roughness", "landuse", "scs_cn"],
                point_anchor_layer=self.point_anchor_layer,
                line_anchor_layer=self.line_anchor_layer,
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
            if self.roughness_layer is None: # Fill with zeros
                ground_triangles_df["roughness"] = 0
            elif self.roughness_layer == "ground_layer": # From ground layer
                print("Getting roughness from ground layer... ", end="")
                start = time.time()
                def get_roughness(row):
                    if np.isnan(row["custom_roughness"]):
                        return landuses_df.loc[landuses_df['idval'] == row["landuse"], 'manning'].values[0]
                    else:
                        return row["custom_roughness"]

                # TODO: Try to not use apply
                # ground_triangles_df["roughness"] = ground_triangles_df["custom_roughness"].fillna()
                ground_triangles_df["roughness"] = ground_triangles_df.apply(get_roughness, axis=1)
                print(f"Done! {time.time() - start}s")
            else: # From raster layer
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

                if self.losses_layer == "ground_layer": # From ground layer
                    pass # already calculated
                else: # From raster layer
                    losses_from_raster = True

            # Vertices
            ground_vertices_df = pd.DataFrame(vertices, columns=["x", "y"])
            ground_vertices_df["category"] = "ground"

            # Get z-values from DEM
            if self.dem_layer is None:
                ground_vertices_df["z"] = 0
            else:
                ground_crs = layers["ground"].crs()
                dem_crs = self.dem_layer.crs()
                qct = QgsCoordinateTransform(ground_crs, dem_crs, QgsProject.instance())
                def get_z(x, y):
                    point = qct.transform(QgsPointXY(x, y))
                    val, res = self.dem_layer.dataProvider().sample(point, 1)
                    return val if res else 0

                ground_vertices_df["z"] = ground_vertices_df.apply(lambda row: get_z(row["x"], row["y"]), axis=1)

            # Get z-values from point anchors
            if self.point_anchor_layer is not None:
                point_anchor_df = layer_to_gdf(self.point_anchor_layer, ["z_value"])
                for _, anchor in point_anchor_df.iterrows():
                    x, y = anchor.geometry.x, anchor.geometry.y
                    mask = (ground_vertices_df["x"] == x) & (ground_vertices_df["y"] == y)
                    ground_vertices_df.loc[mask, "z"] = anchor["z_value"]

            print("Validating landuses... ", end="")
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
                roofs_df.index = roofs_df["fid"] # type: ignore

            bridges_df = self._create_bridges_df(triangles_df, vertices_df)
            print(f"Bridges: {bridges_df}")

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
            temp_layer = create_temp_mesh_layer(self.mesh)
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
                temp_layer = create_temp_mesh_layer(self.mesh)
                print(f"Done! {time.time() - start}s")

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
                INSERT INTO cat_file (name, iber2d, roof, losses)
                VALUES ('{self.mesh_name}', '{mesh_str}', '{roof_str}', '{losses_str}')
            """)

            self.feedback.setProgress(80)

            # Add temp layer to TOC
            tools_qt.add_layer_to_toc(temp_layer)

            # Check for triangles with more than one inlet
            inlet_warning = validate_inlets_in_triangles(temp_layer, layers["inlet"])
            if inlet_warning.hasFeatures():
                group_name = "Mesh inputs errors & warnings"
                tools_qt.add_layer_to_toc(inlet_warning, group_name, create_groups=True)
                project.layerTreeRoot().removeChildrenGroupWithoutLayers()
                iface.layerTreeView().model().sourceModel().modelReset.emit()

            # Refresh TOC
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            self.message = "Process finished!!!"
            self.feedback.setProgress(100)
            return True
        except Exception:
            self.exception = traceback.format_exc()
            self.message = (
                "Task failed. See the Log Messages Panel for more information."
            )
            return False

    def _create_bridges_df(self, polygons_df: pd.DataFrame, vertices_df: pd.DataFrame):
        context = QgsProcessingContext()
        # Create mesh edges layer
        mesh_edges_layer = self._create_mesh_edges_layer(polygons_df, vertices_df)  # FIXME: This takes too long
        # Create buffer for each bridge
        bridge_layer = tools_qgis.get_layer_by_tablename("bridge")
        buffer_layer = self._create_bridge_buffer(bridge_layer, context)
        # Join buffer with mesh edges
        valid_edges_layer = self._create_valid_edges_layer(buffer_layer, mesh_edges_layer, context)

        bridges_values_dict = self.get_bridges_values_dict()

        bridge_list = []
        for feature in valid_edges_layer.getFeatures():
            relative_distance = 0
            total_length = 0
            bridge_feature = None
            for bridge in bridge_layer.getFeatures():
                if bridge["code"] == feature["code"]:
                    total_length = bridge.geometry().length()
                    bridge_feature = bridge
                    break
            line_last_vertex = feature.geometry().asPolyline()[-1]
            # Get the absolute distance along the line to the point
            absolute_distance = bridge_feature.geometry().lineLocatePoint(QgsGeometry.fromPointXY(line_last_vertex))
            # Convert to relative distance (0 to 1)
            relative_distance = absolute_distance / total_length

            relative_distance = round(relative_distance, 2)
            element_id = feature['pol_id']
            side = feature['side']

            # Get bridge values based on code and distance
            bridge_values = None
            if feature["code"] in bridges_values_dict:
                # Get values with distance >= relative_distance
                matching_values = [v for v in bridges_values_dict[feature["code"]]
                                 if v["distance"] >= relative_distance]
                if matching_values:
                    # Take the first matching value (smallest distance >= relative_distance)
                    bridge_values = matching_values[0]

            # Set values from bridge_values if found, otherwise use defaults
            lowerdeckelev = bridge_values["lowelev"] if bridge_values else None
            bridgeopeningpercent = bridge_values["openingval"] if bridge_values else None
            topelevn = bridge_values["topelev"] if bridge_values else None

            freepressureflowcd = feature['freeflow_cd']
            deckcd = feature['deck_cd']
            sumergeflowcd = feature['sumergeflow_cd']
            gaugenumber = feature['gaugenumber']

            feature_list = [
                element_id,
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
            if value["bridge_code"] not in bridge_values_dict.keys():
                bridge_values_dict[value["bridge_code"]] = []
            bridge_values_dict[value["bridge_code"]].append({"distance": value["distance"], "topelev": value["topelev"]
                                                             , "lowelev": value["lowelev"], "openingval": value["openingval"]})
        return bridge_values_dict


    def _create_valid_edges_layer(self, buffer_layer: QgsVectorLayer, mesh_edges_layer: QgsVectorLayer, context: QgsProcessingContext):
        # Join buffer with mesh edges
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': mesh_edges_layer,
            'JOIN': buffer_layer,
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': 'memory:'
        }
        valid_edges_layer: QgsVectorLayer = processing.run('qgis:joinattributesbylocation', alg_params, context=context)['OUTPUT']
        return valid_edges_layer

    def _create_bridge_buffer(self, layer: QgsVectorLayer, context: QgsProcessingContext):
        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.1,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': layer,
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': 'memory:'
        }
        buffer_layer: QgsVectorLayer = processing.run('native:buffer', alg_params, context=context)['OUTPUT']
        return buffer_layer

    def _create_mesh_edges_layer(self, polygons_df: pd.DataFrame, vertices_df: pd.DataFrame):
        poly_df = polygons_df
        feature_edges = {}
        for pol in poly_df[poly_df["category"] == "ground"].itertuples():
            vert = [pol.v1, pol.v2, pol.v3, pol.v4]
            # Add last and first vertices as a edge if they are distinct
            last_edge = [(vert[-1], vert[0])] if vert[-1] != vert[0] else []
            edges = chain(self.pairwise(vert), last_edge)
            for side, verts in enumerate(edges, start=1):
                #edge = frozenset(verts)
                feature_edges[verts] = (pol.Index, side)

            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

        layer = QgsVectorLayer("LineString", "mesh_edges", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem(f"EPSG:{global_vars.data_epsg}"))
        provider = layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("pol_id", QVariant.String))
        fields.append(QgsField("side", QVariant.Int))
        provider.addAttributes(fields)
        layer.updateFields()

        features = []
        for edge, (pol_id, side) in feature_edges.items():
            coords = [vertices_df.loc[vert, ["x", "y"]].to_numpy() for vert in edge]
            feature = QgsFeature()
            feature.setGeometry(
                QgsGeometry.fromPolyline([QgsPoint(*coord) for coord in coords])
            )
            feature.setAttributes([pol_id, side])
            features.append(feature)
        provider.addFeatures(features)
        layer.updateExtents()

        return layer

    def pairwise(self, iterable):
        # pairwise('ABCDEFG') --> AB BC CD DE EF FG
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
