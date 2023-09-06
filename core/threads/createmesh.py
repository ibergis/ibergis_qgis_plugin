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
            if not ground_layer.isValid():
                raise ValueError("Ground layer is not valid.")
            if not all(
                type(feature["cellsize"]) in [int, float] and feature["cellsize"] > 0
                for feature in ground_layer.getFeatures()
            ):
                raise ValueError("Invalid values in column cellsize.")
            poly_layer = triangulate_custom(ground_layer, feedback=self.feedback)
            QgsProject.instance().addMapLayer(poly_layer)
            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
