import traceback
from pathlib import Path

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeedback,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingFeedback,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface

from . import createmesh_core as core
from .validatemesh import validate_input_layers, validate_inlets_in_triangles
from .task import GwTask
from ..utils import mesh_parser
from ..utils.meshing_process import triangulate_custom
from ... import global_vars
from ...lib import tools_qgis, tools_qt


class GwCreateMeshTask(GwTask):
    def __init__(
        self,
        description,
        execute_validations,
        enable_transition,
        transition_slope,
        transition_start,
        transition_extent,
        dem_layer,
        roughness_layer,
        losses_layer,
        mesh_name,
        feedback=None,
    ):
        super().__init__(description)
        self.execute_validations = execute_validations
        self.enable_transition = enable_transition
        self.transition_slope = transition_slope
        self.transition_start = transition_start
        self.transition_extent = transition_extent
        self.dem_layer = dem_layer
        self.roughness_layer = roughness_layer
        self.losses_layer = losses_layer
        self.mesh_name = mesh_name
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
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
            path = f"{self.dao.db_filepath}|layername="
            layers = {
                "ground": None,
                "roof": None,
                "mesh_anchor_points": None,
                "inlet": None,
            }
            for layer in layers:
                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False
                l = QgsVectorLayer(f"{path}{layer}", layer, "ogr")
                if not l.isValid():
                    self.message = f"Layer '{layer}' is not valid. Check if GPKG file has a '{layer}' layer."
                    return False
                layers[layer] = l

            layers["dem"] = self.dem_layer

            # Validate landuses roughness values
            if self.roughness_layer is not None:
                sql = "SELECT id, manning FROM cat_landuses"
                rows = self.dao.get_rows(sql)
                landuses = {} if rows is None else dict(rows)

                if self.roughness_layer == "ground_layer":
                    sql = "SELECT DISTINCT landuse FROM ground WHERE landuse IS NOT NULL AND custom_roughness IS NULL"
                    rows = self.dao.get_rows(sql)
                    used_landuses = (
                        [] if rows is None else [int(row[0]) for row in rows]
                    )
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
                    if l not in landuses or landuses[l] is None
                ]

                if missing_roughness:
                    self.message = "The following landuses are used, but don't have a value for roughness: "
                    self.message += f"{', '.join(missing_roughness)}. "
                    self.message += (
                        "Please, verify the 'cat_landuses' table and try again."
                    )
                    return False

            self.feedback.setProgress(5)

            # Validate inputs
            if self.execute_validations:
                self.feedback.setProgressText("Validating inputs...")
                validation_layers = validate_input_layers(
                    layers, self.execute_validations, self.feedback
                )
                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False

                error_layers, warning_layers = validation_layers

                # Add errors to TOC
                if error_layers or warning_layers:
                    group_name = "Mesh inputs errors & warnings"
                    for layer in error_layers:
                        tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
                    for layer in warning_layers:
                        tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
                    project.layerTreeRoot().removeChildrenGroupWithoutLayers()
                    iface.layerTreeView().model().sourceModel().modelReset.emit()

                    if error_layers:
                        self.message = "There are errors in input data. Please, check the error layers."
                        self.feedback.setProgress(100)
                        return False
                project.layerTreeRoot().removeChildrenGroupWithoutLayers()
                iface.layerTreeView().model().sourceModel().modelReset.emit()

            # Create mesh
            triangulations = []

            self.feedback.setProgressText("Creating ground mesh...")
            self.feedback.setProgress(15)
            gt_feedback = QgsFeedback()
            gt_progress = lambda x: self.feedback.setProgress(x / 100 * (30 - 15) + 15)
            gt_feedback.progressChanged.connect(gt_progress)
            ground_triang = triangulate_custom(
                layers["ground"],
                point_anchor_layer=layers["mesh_anchor_points"],
                enable_transition=self.enable_transition,
                transition_slope=self.transition_slope,
                transition_start=self.transition_start,
                transition_extent=self.transition_extent,
                feedback=gt_feedback,
            )
            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False
            triangulations.append((*ground_triang, {"category": "ground"}))

            self.feedback.setProgressText("Creating roof mesh...")
            self.feedback.setProgress(30)
            triangulations += core.triangulate_roof(layers["roof"], self.feedback)
            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

            self.mesh = core.create_mesh_dict(triangulations)

            # Get roofs
            self.feedback.setProgressText("Getting roof data...")
            sql = """
                SELECT 
                    code, fid, slope, width, roughness, isconnected,
                    outlet_code, outlet_vol, street_vol, infiltr_vol
                FROM roof
            """
            rows = self.dao.get_rows(sql)
            self.mesh["roofs"] = {}
            if rows is not None:
                for row in rows:
                    (
                        code,
                        fid,
                        slope,
                        width,
                        roughness,
                        isconnected,
                        outlet_code,
                        outlet_vol,
                        street_vol,
                        infiltr_vol,
                    ) = row
                    roof_name = code or fid
                    self.mesh["roofs"][fid] = {
                        "name": roof_name,
                        "slope": slope,
                        "width": width,
                        "roughness": roughness,
                        "isconnected": isconnected,
                        "outlet_code": outlet_code,
                        "outlet_vol": outlet_vol,
                        "street_vol": street_vol,
                        "infiltr_vol": infiltr_vol,
                    }

            # Get ground elevation
            self.feedback.setProgressText("Getting vertice elevations...")
            # TODO: Fill roof elevations
            self.feedback.setProgress(40)
            if self.dem_layer is None:
                for vertice in self.mesh["vertices"].values():
                    if vertice["category"] == "ground":
                        vertice["elevation"] = 0
            else:
                ground_crs = layers["ground"].crs()
                dem_crs = self.dem_layer.crs()
                qct = QgsCoordinateTransform(ground_crs, dem_crs, QgsProject.instance())
                for vertice in self.mesh["vertices"].values():
                    if self.feedback.isCanceled():
                        self.message = "Task canceled."
                        return False
                    if vertice["category"] == "ground":
                        point = qct.transform(QgsPointXY(*vertice["coordinates"]))
                        val, res = self.dem_layer.dataProvider().sample(point, 1)
                        vertice["elevation"] = val if res else 0

            # Get ground roughness
            if self.roughness_layer is None:
                for polygon_id, polygon in self.mesh["polygons"].items():
                    if polygon["category"] == "ground":
                        polygon["roughness"] = 0
            else:
                self.feedback.setProgressText("Getting ground roughness...")
                self.feedback.setProgress(50)
                ggr_feedback = QgsProcessingFeedback()
                ggr_progress = lambda x: self.feedback.setProgress(
                    x / 100 * (80 - 50) + 50
                )
                ggr_feedback.progressChanged.connect(ggr_progress)
                ggr_feedback.canceled.connect(self.feedback.cancel)
                if self.roughness_layer == "ground_layer":
                    roughness_dict = core.get_ground_roughness(
                        self.mesh, layers["ground"], landuses, ggr_feedback
                    )
                    if self.feedback.isCanceled():
                        self.message = "Task canceled."
                        return False
                    for polygon_id, roughness in roughness_dict.items():
                        polygon = self.mesh["polygons"][polygon_id]
                        polygon["roughness"] = roughness
                else:
                    polygon_landuses = core.get_value_from_raster(
                        self.roughness_layer,
                        self.mesh,
                        layers["ground"].crs(),
                        ggr_feedback,
                    )
                    if self.feedback.isCanceled():
                        self.message = "Task canceled."
                        return False
                    for polygon_id, landuse in polygon_landuses.items():
                        polygon = self.mesh["polygons"][polygon_id]
                        polygon["roughness"] = landuses[landuse]

            # Get ground losses
            if self.losses_layer is None:
                for polygon_id, polygon in self.mesh["polygons"].items():
                    # FIXME: put losses OFF
                    if polygon["category"] == "ground":
                        polygon["scs_cn"] = 0
            else:
                self.feedback.setProgressText("Getting ground losses...")
                self.feedback.setProgress(50)
                ggl_feedback = QgsProcessingFeedback()
                ggl_progress = lambda x: self.feedback.setProgress(
                    x / 100 * (80 - 50) + 50
                )
                ggl_feedback.progressChanged.connect(ggl_progress)
                ggl_feedback.canceled.connect(self.feedback.cancel)

                if self.losses_layer == "ground_layer":
                    losses_dict = core.get_ground_losses(
                        self.mesh, layers["ground"], ggl_feedback
                    )
                else:
                    losses_dict = core.get_value_from_raster(
                        self.losses_layer,
                        self.mesh,
                        layers["ground"].crs(),
                        ggl_feedback,
                    )

                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False
                for polygon_id, losses in losses_dict.items():
                    polygon = self.mesh["polygons"][polygon_id]
                    polygon["scs_cn"] = losses
                # FIXME: configure self.mesh["losses"]

            # Delete old mesh
            self.feedback.setProgressText("Saving mesh to GPKG file...")
            sql = f"""
                DELETE FROM cat_file
                WHERE name = '{self.mesh_name}'
            """
            self.dao.execute_sql(sql)

            # Save mesh
            mesh_str, roof_str, losses_str = mesh_parser.dumps(self.mesh)
            sql = f"""
                INSERT INTO cat_file (name, iber2d, roof, losses)
                VALUES ('{self.mesh_name}', '{mesh_str}', '{roof_str}', '{losses_str}')
            """
            self.dao.execute_sql(sql)

            # Create temp layer
            self.feedback.setProgressText(
                "Mesh saved to GPKG file!!!\nCreating temp layer for visualization..."
            )
            self.feedback.setProgress(80)
            temp_layer = QgsVectorLayer("Polygon", "Mesh Temp Layer", "memory")
            temp_layer.setCrs(layers["ground"].crs())
            provider = temp_layer.dataProvider()
            fields = [
                QgsField("fid", QVariant.Int),
                QgsField("category", QVariant.String),
                QgsField("vertex_id1", QVariant.Int),
                QgsField("vertex_id2", QVariant.Int),
                QgsField("vertex_id3", QVariant.Int),
                QgsField("vertex_id4", QVariant.Int),
                QgsField("roughness", QVariant.Double),
            ]
            provider.addAttributes(fields)
            temp_layer.updateFields()
            for i, tri in self.mesh["polygons"].items():
                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False
                feature = QgsFeature()
                vertices = (self.mesh["vertices"][vert] for vert in tri["vertice_ids"])
                wkt = "TRIANGLE(("
                wkt += ",".join(
                    f"{v['coordinates'][0]} {v['coordinates'][1]} {v['elevation']}"
                    for v in vertices
                )
                wkt += "))"
                feature.setGeometry(QgsGeometry.fromWkt(wkt))
                feature.setAttributes(
                    [i, tri["category"], *tri["vertice_ids"], tri["roughness"]]
                )
                provider.addFeature(feature)

            temp_layer.updateExtents()

            # Set the style of the layer
            style_path = "resources/templates/mesh_temp_layer.qml"
            style_path = Path(global_vars.plugin_dir) / style_path
            style_path = str(style_path)
            temp_layer.loadNamedStyle(style_path)
            temp_layer.triggerRepaint()

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
