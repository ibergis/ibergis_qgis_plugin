import datetime
from functools import partial
from pathlib import Path
from time import time

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QTimer
from qgis.utils import iface

from ..dialog import GwAction
from ...threads.createmesh import GwCreateMeshTask
from ...ui.ui_manager import GwCreateMeshUi
from ...utils import Feedback, tools_gw
from .... import global_vars
from ....lib import tools_qgis, tools_qt


class GwCreateMeshButton(GwAction):
    """Button 36: CreateMesh"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dao = global_vars.gpkg_dao_data.clone()
        self.dlg_mesh = GwCreateMeshUi()
        dlg = self.dlg_mesh

        self.ground_layer = self._get_layer(self.dao, "ground")
        self.roof_layer = self._get_layer(self.dao, "roof")

        # Validate input layers
        errors = {}
        errors_ground_layer = []
        if not self.ground_layer.isValid():
            errors_ground_layer.append(
                "Ground layer is not valid. Check if GPKG file has a 'ground' layer."
            )
        else:
            if not all(
                type(feature["cellsize"]) in [int, float] and feature["cellsize"] > 0
                for feature in self.ground_layer.getFeatures()
            ):
                errors_ground_layer.append(
                    "There are invalid values in the column 'cellsize' of ground layer. "
                    "The values of 'cellsize' must be greater than zero."
                )
        if errors_ground_layer:
            errors["ground_layer"] = errors_ground_layer

        errors_roof_layer = []
        if not self.roof_layer.isValid():
            errors_roof_layer.append(
                "Roof layer is not valid. Check if GPKG file has a 'roof' layer."
            )
        else:
            if not all(
                type(feature["cellsize"]) in [int, float] and feature["cellsize"] > 0
                for feature in self.roof_layer.getFeatures()
            ):
                errors_roof_layer.append(
                    "There are invalid values in the column 'cellsize' of roof layer. "
                    "The values of 'cellsize' must be greater than zero."
                )
        if errors_roof_layer:
            errors["roof_layer"] = errors_roof_layer

        if errors:
            message = "**Please verify these problems in the input layers before proceeding:**\n\n"
            if "ground_layer" in errors:
                message += "- " + "\n- ".join(errors["ground_layer"]) + "\n"
            if "roof_layer" in errors:
                message += "- " + "\n- ".join(errors["roof_layer"]) + "\n"
            dlg.lbl_warnings.setText(message)
        else:
            dlg.lbl_warnings.hide()

        tools_gw.load_settings(dlg)
        tools_gw.disable_tab_log(dlg)

        # Set initial signals
        dlg = self.dlg_mesh
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(partial(tools_gw.close_dialog, dlg))

        tools_gw.open_dialog(dlg, dlg_name="create_mesh")

    def _execute_process(self):
        dlg = self.dlg_mesh
        self.feedback = Feedback()

        self.thread = GwCreateMeshTask(
            "Import INP file",
            ground_layer=self.ground_layer,
            roof_layer=self.roof_layer,
            feedback=self.feedback,
        )

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_save.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(self.thread.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        self.thread.taskCompleted.connect(self._on_task_completed)
        self.thread.taskTerminated.connect(self._on_task_terminated)
        self.thread.feedback.progressText.connect(self._set_progress_text)
        self.thread.feedback.progress.connect(dlg.progress_bar.setValue)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(self.thread)

    def _get_layer(self, dao, layer_name):
        path = f"{dao.db_filepath}|layername={layer_name}"
        return QgsVectorLayer(path, layer_name, "ogr")

    def _on_task_completed(self):
        self._on_task_end("Task finished!")
        dlg = self.dlg_mesh
        dlg.btn_save.clicked.connect(self._save_mesh)
        dlg.btn_save.setEnabled(True)
        dlg.meshes_saved = False

    def _on_task_end(self, message):
        tools_gw.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": message}]}},
            reset_text=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

        self.timer.stop()

        dlg = self.dlg_mesh
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(dlg.reject)

    def _on_task_terminated(self):
        message = "Task failed. See the Log Messages Panel for more information."
        if self.thread.isCanceled():
            message = "Task canceled."
        self._on_task_end(message)

    def _on_timer_timeout(self):
        # Update timer
        elapsed_time = time() - self.t0
        text = str(datetime.timedelta(seconds=round(elapsed_time)))
        self.dlg_mesh.lbl_timer.setText(text)

    def _save_mesh(self):
        self.dlg_mesh.btn_save.setEnabled(False)

        self.feedback.setProgressText("Saving mesh...")
        file_name = "mesh.dat"
        project_folder = Path(self.dao.db_filepath).parent
        file_path = project_folder / file_name

        with open(file_path, "w") as file:
            file.write("MATRIU\n")
            file.write(f"\t{len(self.thread.mesh['triangles'])}\n")
            for i, tri in self.thread.mesh["triangles"].items():
                v1, v2, v3, v4 = tri["vertices_ids"]
                manning_number = 0.0180
                file.write(f"\t\t{v1}\t\t{v2}\t\t{v3}\t\t{v4}\t\t{manning_number}\t\t{i}\n")
            file.write("VERTEXS\n")
            file.write(f"\t{len(self.thread.mesh['vertices'])}\n")
            for i, v in self.thread.mesh["vertices"].items():
                x, y = v["coordinates"]
                z = 0.000
                file.write(f"\t\t{x}\t\t{y}\t\t{z}\t\t{i}\n")

        # Remove temp layer
        project = QgsProject.instance()
        for layer in project.mapLayersByName("Mesh Temp Layer"):
            project.removeMapLayer(layer)

        self.dlg_mesh.meshes_saved = True
        self.feedback.setProgressText("Task finished!")

    def _set_progress_text(self, txt):
        tools_gw.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": txt}]}},
            reset_text=False,
            close=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())
