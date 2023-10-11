import traceback

from qgis.core import (
    QgsCategorizedSymbolRenderer,
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
    def __init__(self, description, feedback=None):
        super().__init__(description)
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
            project.removeMapLayers(project.mapLayersByName("Mesh Temp Layer"))
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
                    message = f"Layer '{layer}' is not valid. Check if GPKG file has a '{layer}' layer."
                    self.feedback.setProgressText(message)
                    return False
                layers[layer] = l

            # Validate inputs
            error_layers = []

            # Validate ground layer
            # 1. Verify cellsize values
            ground_cellsize_layer = QgsVectorLayer(
                "Polygon", "ground: Invalid cellsize", "memory"
            )
            ground_cellsize_layer.setCrs(layers["ground"].crs())
            provider = ground_cellsize_layer.dataProvider()
            provider.addAttributes(
                [
                    QgsField("fid", QVariant.Int),
                    QgsField("cellsize", QVariant.Double),
                ]
            )
            ground_cellsize_layer.updateFields()
            ground_cellsize_layer.startEditing()
            for feature in layers["ground"].getFeatures():
                cellsize = feature["cellsize"]
                if type(cellsize) in [int, float] and cellsize > 0:
                    continue
                invalid_feature = QgsFeature(ground_cellsize_layer.fields())
                invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
                invalid_feature.setGeometry(feature.geometry())
                ground_cellsize_layer.addFeature(invalid_feature)
            ground_cellsize_layer.commitChanges()
            if ground_cellsize_layer.hasFeatures():
                error_layers.append(ground_cellsize_layer)

            # Add errors to TOC
            if error_layers:
                group_name = "Mesh inputs errors & warnings"
                for layer in error_layers:
                    tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
                iface.layerTreeView().model().sourceModel().modelReset.emit()
                return False
            project.layerTreeRoot().removeChildrenGroupWithoutLayers()
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            self.mesh = {"triangles": {}, "vertices": {}}

            # Create mesh for ground
            self.feedback.setProgressText("Creating ground mesh...")
            ground_triangles, ground_vertices = triangulate_custom(
                layers["ground"], feedback=self.feedback
            )
            for i, triangle in enumerate(ground_triangles, start=1):
                self.mesh["triangles"][i] = {
                    "category": "ground",
                    "vertices_ids": [int(triangle[v] + 1) for v in (0, 1, 2, 0)],
                }
                next_triangle_id = i + 1

            for i, vertice in enumerate(ground_vertices, start=1):
                self.mesh["vertices"][i] = {"coordinates": (vertice[0], vertice[1])}
                next_vertice_id = i + 1

            # Add roofs to mesh
            self.feedback.setProgressText("Creating roof mesh...")
            crs = layers["roof"].crs()
            features = (
                core.feature_to_layer(feature, crs)
                for feature in layers["roof"].getFeatures()
            )
            roof_meshes = (
                triangulate_custom(feature, feedback=self.feedback)
                for feature in features
            )
            for roof_triangles, roof_vertices in roof_meshes:
                for i, triangle in enumerate(roof_triangles, start=next_triangle_id):
                    self.mesh["triangles"][i] = {
                        "category": "roof",
                        "vertices_ids": [
                            int(triangle[v] + next_vertice_id) for v in (0, 1, 2, 0)
                        ],
                    }
                    next_triangle_id = i + 1

                for i, vertice in enumerate(roof_vertices, start=next_vertice_id):
                    self.mesh["vertices"][i] = {"coordinates": (vertice[0], vertice[1])}
                    next_vertice_id = i + 1

            # Create temp layer
            self.feedback.setProgressText("Creating temp layer for visualization...")
            temp_layer = QgsVectorLayer("Polygon", "Mesh Temp Layer", "memory")
            temp_layer.setCrs(layers["ground"].crs())
            provider = temp_layer.dataProvider()
            provider.addAttributes(
                [
                    QgsField("fid", QVariant.Int),
                    QgsField("category", QVariant.String),
                    QgsField("vertex_id1", QVariant.Int),
                    QgsField("vertex_id2", QVariant.Int),
                    QgsField("vertex_id3", QVariant.Int),
                    QgsField("vertex_id4", QVariant.Int),
                ]
            )
            temp_layer.updateFields()
            for i, tri in self.mesh["triangles"].items():
                if self.feedback.isCanceled():
                    return {}
                feature = QgsFeature()
                feature.setGeometry(
                    QgsGeometry.fromPolygonXY(
                        [
                            [
                                QgsPointXY(*self.mesh["vertices"][vert]["coordinates"])
                                for vert in tri["vertices_ids"]
                            ]
                        ]
                    )
                )
                feature.setAttributes(
                    [
                        i,
                        tri["category"],
                        int(tri["vertices_ids"][0]),
                        int(tri["vertices_ids"][1]),
                        int(tri["vertices_ids"][2]),
                        int(tri["vertices_ids"][0]),
                    ]
                )
                provider.addFeature(feature)

            temp_layer.updateExtents()

            # Set the style of the layer
            renderer = QgsCategorizedSymbolRenderer()
            ground_category = QgsRendererCategory(
                "ground", QgsFillSymbol.createSimple({"color": "#a6cee3"}), "Ground"
            )
            roof_category = QgsRendererCategory(
                "roof", QgsFillSymbol.createSimple({"color": "#fb9a99"}), "Roofs"
            )
            renderer = QgsCategorizedSymbolRenderer(
                "category", [ground_category, roof_category]
            )
            temp_layer.setRenderer(renderer)

            # Add temp layer to TOC
            tools_qt.add_layer_to_toc(temp_layer)

            # Refresh TOC
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
