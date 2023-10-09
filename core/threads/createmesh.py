import traceback

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
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
    def __init__(self, description, ground_layer=None, roof_layer=None, feedback=None):
        super().__init__(description)
        self.ground_layer = ground_layer
        self.poly_ground_layer = None
        self.roof_layer = roof_layer
        self.poly_roof_layer = None
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.feedback.setProgressText("Starting process!")

            self.dao = global_vars.gpkg_dao_data.clone()

            self.mesh = {"triangles": {}, "vertices": {}}

            # Create mesh for ground
            self.feedback.setProgressText("Creating ground mesh...")
            ground_triangles, ground_vertices = triangulate_custom(
                self.ground_layer, feedback=self.feedback
            )
            for i, triangle in enumerate(ground_triangles, start=1):
                self.mesh["triangles"][i] = {
                    "vertices_ids": [triangle[v] + 1 for v in (0, 1, 2, 0)]
                }
                next_triangle_id = i + 1

            for i, vertice in enumerate(ground_vertices, start=1):
                self.mesh["vertices"][i] = {"coordinates": (vertice[0], vertice[1])}
                next_vertice_id = i + 1

            # Add roofs to mesh
            self.feedback.setProgressText("Creating roof mesh...")
            crs = self.roof_layer.crs()
            features = (
                core.feature_to_layer(feature, crs)
                for feature in self.roof_layer.getFeatures()
            )
            roof_meshes = (
                triangulate_custom(feature, feedback=self.feedback)
                for feature in features
            )
            for roof_triangles, roof_vertices in roof_meshes:
                for i, triangle in enumerate(roof_triangles, start=next_triangle_id):
                    self.mesh["triangles"][i] = {
                        "vertices_ids": [
                            triangle[v] + next_vertice_id for v in (0, 1, 2, 0)
                        ]
                    }
                    next_triangle_id = i + 1

                for i, vertice in enumerate(roof_vertices, start=next_vertice_id):
                    self.mesh["vertices"][i] = {"coordinates": (vertice[0], vertice[1])}
                    next_vertice_id = i + 1

            # Create temp layer
            self.feedback.setProgressText("Creating temp layer for visualization...")
            temp_layer = QgsVectorLayer("Polygon", "temp", "memory")
            temp_layer.setCrs(self.ground_layer.crs())
            provider = temp_layer.dataProvider()
            provider.addAttributes(
                [
                    QgsField("fid", QVariant.Int),
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
                        int(tri["vertices_ids"][0]),
                        int(tri["vertices_ids"][1]),
                        int(tri["vertices_ids"][2]),
                        int(tri["vertices_ids"][0]),
                    ]
                )
                provider.addFeature(feature)

            temp_layer.updateExtents()


            # Add temp layer to TOC
            root = QgsProject.instance().layerTreeRoot()
            group_name = "Mesh Temp Layers"
            temp_group = tools_qgis.find_toc_group(root, group_name)
            if temp_group is not None:
                for layer in temp_group.findLayers():
                    if layer.name() in ["Ground Mesh", "Roof Mesh"]:
                        tools_qgis.remove_layer_from_toc(
                            layer.name(), "Mesh Temp Layers"
                        )
            tools_qt.add_layer_to_toc(temp_layer, group_name, create_groups=True)

            # Refresh TOC
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
