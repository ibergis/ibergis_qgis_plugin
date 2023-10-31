import datetime
from functools import partial
from pathlib import Path
from time import time

from qgis.core import QgsApplication, QgsMapLayer, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QTimer

from ..dialog import GwAction
from ...threads.createmesh import GwCreateMeshTask
from ...ui.ui_manager import GwCreateMeshUi
from ...utils import Feedback, tools_gw
from .... import global_vars
from ....lib import tools_qt


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

        # Set widgets
        tools_gw.load_settings(dlg)
        tools_gw.disable_tab_log(dlg)
        tools_qt.double_validator(dlg.txt_slope)
        tools_qt.double_validator(dlg.txt_start)
        tools_qt.double_validator(dlg.txt_extent)
        dlg.btn_save.setVisible(False)

        # Fill raster layers combo
        project = QgsProject.instance()
        all_layers = project.mapLayers().values()
        raster_layers = (
            [layer.name(), layer]
            for layer in all_layers
            if layer.type() == QgsMapLayer.RasterLayer and layer.bandCount() == 1
        )
        rows = [["Fill elevation with zeroes", None], *raster_layers]
        tools_qt.fill_combo_values(dlg.cmb_dem_layer, rows, add_empty=True)

        # Set initial signals
        dlg.chk_transition.stateChanged.connect(dlg.txt_slope.setEnabled)
        dlg.chk_transition.stateChanged.connect(dlg.txt_start.setEnabled)
        dlg.chk_transition.stateChanged.connect(dlg.txt_extent.setEnabled)
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(partial(tools_gw.close_dialog, dlg))

        tools_gw.open_dialog(dlg, dlg_name="create_mesh")

    def _execute_process(self):
        dlg = self.dlg_mesh

        # Get and validate inputs
        enable_transition = dlg.chk_transition.isChecked()
        transition_slope = float(dlg.txt_slope.text())
        transition_start = float(dlg.txt_start.text())
        transition_extent = float(dlg.txt_extent.text())
        dem_layer = tools_qt.get_combo_value(dlg, dlg.cmb_dem_layer, index=1)
        if dem_layer == "":
            tools_qt.show_info_box("Please, select a DEM layer!")
            return
        fill_roughness = dlg.chk_roughness.isChecked()

        self.feedback = Feedback()
        self.thread_triangulation = GwCreateMeshTask(
            "Triangulation",
            enable_transition,
            transition_slope,
            transition_start,
            transition_extent,
            dem_layer,
            fill_roughness,
            feedback=self.feedback,
        )

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_save.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(self.thread_triangulation.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        self.thread_triangulation.taskCompleted.connect(self._on_task_completed)
        self.thread_triangulation.taskTerminated.connect(self._on_task_terminated)
        self.thread_triangulation.feedback.progressText.connect(self._set_progress_text)
        self.thread_triangulation.feedback.progress.connect(dlg.progress_bar.setValue)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(self.thread_triangulation)

    def _get_layer(self, dao, layer_name):
        path = f"{dao.db_filepath}|layername={layer_name}"
        return QgsVectorLayer(path, layer_name, "ogr")

    def _on_task_completed(self):
        self._on_task_end()
        dlg = self.dlg_mesh
        dlg.btn_save.clicked.connect(self._save_mesh)
        dlg.btn_save.setEnabled(True)
        dlg.btn_save.setVisible(True)
        dlg.meshes_saved = False

    def _on_task_end(self):
        thread = self.thread_triangulation
        message = "Task canceled." if thread.isCanceled() else thread.message
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
        self._on_task_end()

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
            file.write(f"\t{len(self.thread_triangulation.mesh['triangles'])}\n")
            for i, tri in self.thread_triangulation.mesh["triangles"].items():
                v1, v2, v3, v4 = tri["vertice_ids"]
                manning_number = 0.0180
                file.write(
                    f"\t\t{v1}\t\t{v2}\t\t{v3}\t\t{v4}\t\t{manning_number}\t\t{i}\n"
                )
            file.write("VERTEXS\n")
            file.write(f"\t{len(self.thread_triangulation.mesh['vertices'])}\n")
            for i, v in self.thread_triangulation.mesh["vertices"].items():
                x, y = v["coordinates"]
                z = v["elevation"]
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
