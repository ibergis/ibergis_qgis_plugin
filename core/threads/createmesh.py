import traceback

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsRendererCategory,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface

from . import createmesh_core as core
from .task import GwTask
from ..utils.meshing_process import triangulate_custom
from ... import global_vars
from ...lib import tools_qgis, tools_qt


class GwCreateMeshTask(GwTask):
    def __init__(
        self,
        description,
        enable_transition,
        transition_slope,
        transition_start,
        transition_extent,
        dem_layer,
        feedback=None,
    ):
        super().__init__(description)
        self.enable_transition = enable_transition
        self.transition_slope = transition_slope
        self.transition_start = transition_start
        self.transition_extent = transition_extent
        self.dem_layer = dem_layer
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
            layers = {"ground": None, "roof": None}
            for layer in layers:
                l = QgsVectorLayer(f"{path}{layer}", layer, "ogr")
                if not l.isValid():
                    self.message = f"Layer '{layer}' is not valid. Check if GPKG file has a '{layer}' layer."
                    return False
                layers[layer] = l

            # Validate inputs
            error_layers = core.validate_input_layers(layers)

            # Add errors to TOC
            if error_layers:
                group_name = "Mesh inputs errors & warnings"
                for layer in error_layers:
                    tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
                iface.layerTreeView().model().sourceModel().modelReset.emit()
                self.message = (
                    "There are errors in input data. Please, check the error layers."
                )
                return False
            project.layerTreeRoot().removeChildrenGroupWithoutLayers()
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            # Create mesh
            triangulations = []

            self.feedback.setProgressText("Creating ground mesh...")
            ground_triang = triangulate_custom(
                layers["ground"],
                enable_transition=self.enable_transition,
                transition_slope=self.transition_slope,
                transition_start=self.transition_start,
                transition_extent=self.transition_extent,
                feedback=self.feedback,
            )
            triangulations.append(ground_triang)

            self.feedback.setProgressText("Creating roof mesh...")
            crs = layers["roof"].crs()
            for feature in layers["roof"].getFeatures():
                layer = core.feature_to_layer(feature, crs)
                roof_triang = triangulate_custom(
                    layer, enable_transition=False, feedback=self.feedback
                )
                triangulations.append(roof_triang)

            self.mesh = core.create_mesh_dict(triangulations)

            # Get elevation
            # FIXME use following line after fixing GPKG CRS issue
            # ground_crs = layers["ground"].crs()
            self.feedback.setProgressText("Getting vertice elevations...")
            ground_crs = QgsProject.instance().crs()
            dem_crs = self.dem_layer.crs()
            qct = QgsCoordinateTransform(ground_crs, dem_crs, QgsProject.instance())
            for vertice in self.mesh["vertices"].values():
                if self.dem_layer is None:
                    vertice["elevation"] = 0
                else:
                    point = qct.transform(QgsPointXY(*vertice["coordinates"]))
                    val, res = self.dem_layer.dataProvider().sample(point, 1)
                    vertice["elevation"] = val if res else 0

            # Create temp layer
            self.feedback.setProgressText("Creating temp layer for visualization...")
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
            ]
            provider.addAttributes(fields)
            temp_layer.updateFields()
            for i, tri in self.mesh["triangles"].items():
                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False
                feature = QgsFeature()
                polygon_points = [
                    QgsPointXY(*self.mesh["vertices"][vert]["coordinates"])
                    for vert in tri["vertice_ids"]
                ]
                feature.setGeometry(QgsGeometry.fromPolygonXY([polygon_points]))
                feature.setAttributes([i, tri["category"], *tri["vertice_ids"]])
                provider.addFeature(feature)

            temp_layer.updateExtents()

            # Set the style of the layer
            renderer = QgsCategorizedSymbolRenderer()
            categories = [
                QgsRendererCategory(
                    "ground", QgsFillSymbol.createSimple({"color": "#a6cee3"}), "Ground"
                ),
                QgsRendererCategory(
                    "roof", QgsFillSymbol.createSimple({"color": "#fb9a99"}), "Roof"
                ),
            ]
            renderer = QgsCategorizedSymbolRenderer("category", categories)
            temp_layer.setRenderer(renderer)

            # Add temp layer to TOC
            tools_qt.add_layer_to_toc(temp_layer)

            # Refresh TOC
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            self.message = "Triangulation finished! Check the temporary layer and click the button bellow to proceed to the next step."
            return True
        except Exception:
            self.exception = traceback.format_exc()
            self.message = (
                "Task failed. See the Log Messages Panel for more information."
            )
            return False
