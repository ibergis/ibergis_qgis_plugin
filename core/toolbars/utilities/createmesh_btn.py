import datetime
from functools import partial
from time import time

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt.QtCore import QTimer

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
        self.dlg_mesh = GwCreateMeshUi()
        dlg = self.dlg_mesh

        self._check_for_previous_results()
        save_temp_meshes = False
        if self.temp_meshes:
            message = (
                "There are some temporary layers from previous runs of this tool that were not saved."
                ' Do you want to save them now? (Click "Cancel" to generate new meshes.)'
            )
            save_temp_meshes = tools_qt.show_question(message)

        tools_gw.load_settings(dlg)
        self._load_user_values()
        self._set_initial_signals()
        tools_gw.disable_tab_log(dlg)

        tools_gw.open_dialog(dlg, dlg_name="create_mesh")
        if save_temp_meshes:
            self._save_meshes()

    def _check_for_previous_results(self):
        self.temp_meshes = {}
        root = QgsProject.instance().layerTreeRoot()
        temp_group = tools_qgis.find_toc_group(root, "Mesh Temp Layers")
        if temp_group is None:
            return
        for layer in temp_group.findLayers():
            if layer.name() in ["Ground Mesh", "Roof Mesh"]:
                self.temp_meshes[layer.name()] = layer

    def _execute_process(self):
        dlg = self.dlg_mesh
        self.feedback = Feedback()
        if not self._validate_inputs():
            return
        self._save_user_values()
        self.thread = GwCreateMeshTask(
            "Import INP file",
            self.feedback,
        )

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(self.thread.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        self.thread.taskCompleted.connect(self._on_task_completed)
        self.thread.taskTerminated.connect(self._on_task_terminated)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(self.thread)

    def _load_user_values(self):
        self._user_values("load")

    def _on_task_completed(self):
        self._on_task_end("Task finished!")

    def _on_task_end(self, message):
        tools_gw.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": message}]}},
            reset_text=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.timer.stop()

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

    def _save_meshes(self):
        pass

    def _save_user_values(self):
        self._user_values("save")

    def _set_initial_signals(self):
        dlg = self.dlg_mesh
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(partial(tools_gw.close_dialog, dlg))

    def _set_progress_text(self, txt):
        tools_gw.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": txt}]}},
            reset_text=False,
            close=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _user_values(self, action):
        txt_widgets = []

        for widget in txt_widgets:
            if action == "load":
                value = tools_gw.get_config_parser(
                    "create_mesh",
                    widget,
                    "user",
                    "session",
                )
                tools_qt.set_widget_text(self.dlg_mesh, widget, value)
            elif action == "save":
                value = tools_qt.get_text(self.dlg_mesh, widget, False, False)
                value = value.replace("%", "%%")
                tools_gw.set_config_parser(
                    "create_mesh",
                    widget,
                    value,
                )

    def _validate_inputs(self):
        dlg = self.dlg_mesh
        return True
