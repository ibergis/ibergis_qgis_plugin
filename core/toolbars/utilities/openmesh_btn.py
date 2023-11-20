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
        folder_path = QFileDialog.getExistingDirectory(
            caption="Select folder",
            directory=project_folder,
        )

        if not folder_path:
            return

        MESH_FILE = "Iber2D.dat"
        mesh_path = Path(folder_path) / MESH_FILE

        if not mesh_path.exists():
            tools_qt.show_info_box("File Iber2D.dat not found in this folder.")
            return

        self.thread = GwOpenMeshTask("Open mesh file", folder_path)
        self.thread.taskCompleted.connect(self._load_layer)
        QgsApplication.taskManager().addTask(self.thread)

    def _load_layer(self):
        """Add temp layer to TOC"""
        tools_qt.add_layer_to_toc(self.thread.layer)
        iface.setActiveLayer(self.thread.layer)
        iface.zoomToActiveLayer()
