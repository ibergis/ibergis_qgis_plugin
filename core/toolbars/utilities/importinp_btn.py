from functools import partial
from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QFileDialog

from ..dialog import GwAction
from ...threads.importinp import GwImportInpTask
from ...ui.ui_manager import GwImportInpUi
from ...utils import tools_gw
from .... import global_vars
from ....lib import tools_qt


class GwImportINPButton(GwAction):
    """Button 42: ImportINP"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dlg_import = GwImportInpUi()
        dlg = self.dlg_import

        tools_gw.load_settings(dlg)
        self._load_user_values()
        self._set_initial_signals()
        tools_gw.disable_tab_log(dlg)
        tools_gw.open_dialog(dlg, dlg_name="import")

    def _execute_process(self):
        if not self._validate_inputs():
            return
        self._save_user_values()
        db_filepath = global_vars.gpkg_dao_data.db_filepath
        self.thread = GwImportInpTask("Import INP file", self.input_file, db_filepath)
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

    def _save_user_values(self):
        self._user_values("save")

    def _set_initial_signals(self):
        dlg = self.dlg_import
        dlg.btn_push_inp_input_file.clicked.connect(
            partial(self._get_file_dialog, dlg.data_inp_input_file)
        )
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(partial(tools_gw.close_dialog, dlg))

    def _user_values(self, action):
        txt_widgets = ["data_inp_input_file"]

        for widget in txt_widgets:
            if action == "load":
                value = tools_gw.get_config_parser(
                    "add_demand_check",
                    widget,
                    "user",
                    "session",
                )
                tools_qt.set_widget_text(self.dlg_import, widget, value)
            elif action == "save":
                value = tools_qt.get_text(self.dlg_import, widget, False, False)
                value = value.replace("%", "%%")
                tools_gw.set_config_parser(
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
