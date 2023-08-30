import traceback

from qgis.core import QgsProject, QgsVectorLayer

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
            table_name = "ground"
            path = f"{self.dao.db_filepath}|layername={table_name}"
            source_layer = QgsVectorLayer(path, table_name, "ogr")
            if not source_layer.isValid():
                raise ValueError("Ground layer is not valid.")
            poly_layer = triangulate_custom(source_layer, feedback=self.feedback)
            QgsProject.instance().addMapLayer(poly_layer)
            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
