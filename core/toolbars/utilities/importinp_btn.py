import datetime
from functools import partial
from pathlib import Path
from time import time

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QFileDialog

from ..dialog import DrAction
from ...threads.importinp import DrImportInpTask
from ...ui.ui_manager import DrImportInpUi
from ...utils import Feedback, tools_dr
from .... import global_vars
from ....lib import tools_qt


class DrImportINPButton(DrAction):
    """Button 42: ImportINP"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dlg_import = DrImportInpUi()
        dlg = self.dlg_import

        tools_dr.load_settings(dlg)
        self._load_user_values()
        self._set_initial_signals()
        tools_dr.disable_tab_log(dlg)
        tools_dr.open_dialog(dlg, dlg_name="import")

    def _execute_process(self):
        dlg = self.dlg_import
        self.feedback = Feedback()
        if not self._validate_inputs():
            return
        self._save_user_values()
        self.thread = DrImportInpTask(
            "Import INP file",
            self.input_file,
            global_vars.gpkg_dao_data.db_filepath,
            self.feedback,
        )

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(self.thread.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        self.thread.feedback.progressText.connect(self._set_progress_text)
        self.thread.feedback.progressChanged.connect(dlg.progress_bar.setValue)
        self.thread.taskCompleted.connect(self._on_task_completed)
        self.thread.taskTerminated.connect(self._on_task_terminated)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(self.thread)

    def _get_file_dialog(self, widget):
        # Check if selected file exists. Set default value if necessary
        file_path = tools_qt.get_text(self.dlg_import, widget)
        if file_path in (None, "null") or not Path(file_path).exists():
            file_path = str(Path.home())

        # Open dialog to select file
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        msg = "Select file"
        file_path = file_dialog.getOpenFileName(
            parent=None, caption=tools_qt.tr(msg), directory=file_path
        )[0]
        if file_path:
            tools_qt.set_widget_text(self.dlg_import, widget, str(file_path))

    def _load_user_values(self):
        self._user_values("load")

    def _on_task_completed(self):
        self._on_task_end("Task finished!")

    def _on_task_end(self, message):
        tools_dr.fill_tab_log(
            self.dlg_import,
            {"info": {"values": [{"message": message}]}},
            reset_text=False,
        )
        sb = self.dlg_import.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.feedback.setProgress(100)
        self.feedback = None
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
        self.dlg_import.lbl_timer.setText(text)

    def _save_user_values(self):
        self._user_values("save")

    def _set_initial_signals(self):
        dlg = self.dlg_import
        dlg.btn_push_inp_input_file.clicked.connect(
            partial(self._get_file_dialog, dlg.data_inp_input_file)
        )
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(partial(tools_dr.close_dialog, dlg))

    def _set_progress_text(self, txt):
        tools_dr.fill_tab_log(
            self.dlg_import,
            {"info": {"values": [{"message": txt}]}},
            reset_text=False,
            close=False,
        )
        sb = self.dlg_import.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _user_values(self, action):
        txt_widgets = ["data_inp_input_file"]

        for widget in txt_widgets:
            if action == "load":
                value = tools_dr.get_config_parser(
                    "add_demand_check",
                    widget,
                    "user",
                    "session",
                )
                tools_qt.set_widget_text(self.dlg_import, widget, value)
            elif action == "save":
                value = tools_qt.get_text(self.dlg_import, widget, False, False)
                value = value.replace("%", "%%")
                tools_dr.set_config_parser(
                    "add_demand_check",
                    widget,
                    value,
                )

    def _validate_inputs(self):
        dlg = self.dlg_import

        input_file = dlg.data_inp_input_file.toPlainText()
        if not input_file or not Path(input_file).exists():
            tools_qt.show_info_box("You should select an input INP file!")
            return False

        self.input_file = input_file
        return True
