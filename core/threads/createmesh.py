import traceback

from qgis.core import QgsProject

from . import createmesh_core as core
from .task import GwTask
from ..utils.meshing_process import triangulate_custom
from ... import global_vars


class GwCreateMeshTask(GwTask):
    def __init__(self, description, feedback):
        super().__init__(description)
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao = global_vars.gpkg_dao_data.clone()

            ground_layer = core.get_layer(self.dao, "ground")
            core.validate_layer(ground_layer)
            poly_ground_layer = triangulate_custom(ground_layer, feedback=self.feedback)

            roof_layer = core.get_layer(self.dao, "roof")
            core.validate_layer(roof_layer)
            crs = roof_layer.crs()
            features = (
                core.feature_to_layer(feature, crs)
                for feature in roof_layer.getFeatures()
            )
            roof_meshes = (
                triangulate_custom(feature, feedback=self.feedback)
                for feature in features
            )
            poly_roof_layer = core.join_layers(roof_meshes)

            QgsProject.instance().addMapLayer(poly_ground_layer)
            QgsProject.instance().addMapLayer(poly_roof_layer)

            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
