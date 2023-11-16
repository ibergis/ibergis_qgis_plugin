from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.utils import iface

from ..dialog import GwAction
from ...threads.openmesh import GwOpenMeshTask
from .... import global_vars
from ....lib import tools_qt


class GwOpenMeshButton(GwAction):
    """Button 33: OpenMesh"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dao = global_vars.gpkg_dao_data.clone()
        project_folder = str(Path(self.dao.db_filepath).parent)
        file_path = QFileDialog.getOpenFileName(
            caption="Open mesh file",
            directory=project_folder,
            filter="DAT file (*.dat)",
        )[0]

        if not file_path:
            return

        self.thread = GwOpenMeshTask("Open mesh file", file_path)
        self.thread.taskCompleted.connect(self._load_layer)
        QgsApplication.taskManager().addTask(self.thread)

    def _load_layer(self):
        """Add temp layer to TOC"""
        tools_qt.add_layer_to_toc(self.thread.layer)
        iface.setActiveLayer(self.thread.layer)
        iface.zoomToActiveLayer()
