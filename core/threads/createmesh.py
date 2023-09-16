import traceback

from qgis.core import QgsProject
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
        self.roof_layer = roof_layer
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.feedback.setProgressText("Starting process!")

            self.dao = global_vars.gpkg_dao_data.clone()

            layers = []

            if self.ground_layer is not None:
                self.feedback.setProgressText("Creating ground mesh...")
                poly_ground_layer = triangulate_custom(
                    self.ground_layer, feedback=self.feedback
                )
                poly_ground_layer.setName("Ground Mesh")
                layers.append(poly_ground_layer)

            if self.roof_layer is not None:
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
                poly_roof_layer = core.join_layers(roof_meshes)
                poly_roof_layer.setName("Roof Mesh")
                layers.append(poly_roof_layer)

            root = QgsProject.instance().layerTreeRoot()
            group_name = "Mesh Temp Layers"
            temp_group = tools_qgis.find_toc_group(root, group_name)
            if temp_group is not None:
                for layer in temp_group.findLayers():
                    if layer.name() in ["Ground Mesh", "Roof Mesh"]:
                        tools_qgis.remove_layer_from_toc(
                            layer.name(), "Mesh Temp Layers"
                        )
            for layer in layers:
                tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)

            # Refresh TOC
            iface.layerTreeView().model().sourceModel().modelReset.emit()

            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
