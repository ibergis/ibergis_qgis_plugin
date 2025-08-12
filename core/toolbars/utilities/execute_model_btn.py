"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from functools import partial
from sip import isdeleted
from time import time
from datetime import timedelta

from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QTextEdit, QLabel
from qgis.core import QgsApplication

from ...threads.execute_model import DrExecuteModel
from ...shared.options import DrOptions
from ...utils import tools_dr, Feedback
from ...ui.ui_manager import DrExecuteModelUi
from .... import global_vars
from ....lib import tools_qt, tools_db, tools_os, tools_qgis
from ..dialog import DrAction


class DrExecuteModelButton(DrAction):
    """ Button 38: Execute model """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.project_type = global_vars.project_type
        self.epa_options_list = []
        self.export_path = None
        self.cur_process = None
        self.cur_text = None
        self.execute_model_task = None

    def clicked_event(self):

        self._open_execute_dlg()

    def _open_execute_dlg(self):
        self.execute_dlg = DrExecuteModelUi()
        tools_dr.load_settings(self.execute_dlg)

        # Populate combobox
        self._populate_mesh_cmb()

        # Fill widget values
        self._load_user_values()

        # Signals
        self.execute_dlg.btn_options.clicked.connect(self._go2epa_options)
        self.execute_dlg.btn_folder_path.clicked.connect(partial(self._manage_btn_folder_path))
        self.execute_dlg.btn_accept.clicked.connect(partial(self._manage_btn_accept))
        self.execute_dlg.btn_cancel.clicked.connect(partial(self._cancel_task))
        self.execute_dlg.btn_close.clicked.connect(partial(tools_dr.close_dialog, self.execute_dlg))

        self.execute_dlg.btn_cancel.setVisible(False)

        tools_dr.open_dialog(self.execute_dlg, 'execute_model')

    def _populate_mesh_cmb(self):
        sql = "SELECT id, name as idval FROM cat_file"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(self.execute_dlg.cmb_mesh, rows, add_empty=True)

    def _go2epa_options(self):
        self.go2epa_options = DrOptions(parent=self.execute_dlg)
        self.go2epa_options.open_options_dlg()

    def _manage_btn_folder_path(self):
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.execute_dlg, 'txt_folder_path', str(path))

    def _manage_btn_accept(self):
        # Check if results exist on folder
        self.export_path = tools_qt.get_text(self.execute_dlg, 'txt_folder_path')
        if not os.path.exists(self.export_path):
            try:
                os.mkdir(self.export_path)
            except Exception:
                msg = "The specified folder doesn't exist and it couldn't be created. Make sure the specified folder exists."
                tools_qt.show_info_box(msg)
                return False

        if os.path.exists(f"{self.export_path}{os.sep}Iber2D.dat"):
            msg = "Results files already exist in this path. Do you want to overwrite them?"
            title = "Overwrite file"
            answer = tools_qt.show_question(msg, title, force_action=True)
            if not answer:
                return False

        mesh_id = tools_qt.get_combo_value(self.execute_dlg, 'cmb_mesh')
        if mesh_id is None or mesh_id == '':
            msg = "No mesh selected. Please select a mesh."
            tools_qgis.show_warning(msg, dialog=self.execute_dlg)
            return False

        # TODO: ask for import
        do_import = True

        do_generate_inp = True
        sql = "SELECT value FROM config_param_user WHERE parameter = 'plg_swmm_options'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if row and row[0] == '0':
            do_generate_inp = False

        self._save_user_values()

        # Show tab log
        tools_dr.set_tabs_enabled(self.execute_dlg)
        self.execute_dlg.mainTab.setCurrentIndex(1)

        self.execute_dlg.btn_cancel.setVisible(True)
        self.execute_dlg.btn_close.setVisible(False)

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.execute_dlg))
        self.timer.start(1000)

        # Set background task 'Execute model'
        description = "Execute model"

        params = {"dialog": self.execute_dlg, "folder_path": self.export_path,
                  "do_generate_inp": do_generate_inp, "do_export": True, "do_run": True, "do_import": do_import}
        self.feedback = Feedback()
        self.execute_model_task = DrExecuteModel(description, params, self.feedback, timer=self.timer)
        self.execute_model_task.progress_changed.connect(self._progress_changed)
        self.feedback.progressChanged.connect(self._progress_changed)
        QgsApplication.taskManager().addTask(self.execute_model_task)
        QgsApplication.taskManager().triggerTask(self.execute_model_task)

    def _cancel_task(self):
        if self.execute_model_task:
            self.execute_model_task.cancel()

    def _progress_changed(self, process, progress, text, new_line):
        # Progress bar
        if progress is not None:
            self.execute_dlg.progress_bar.setValue(progress)

        # TextEdit log
        txt_infolog = self.execute_dlg.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.execute_dlg, txt_infolog, return_string_null=False)
        if process and process != self.cur_process:
            cur_text = f"{cur_text}\n" \
                       f"--------------------\n" \
                       f"{process}\n" \
                       f"--------------------\n\n"
            self.cur_process = process
            self.cur_text = None

        if self.cur_text:
            cur_text = self.cur_text

        end_line = '\n' if new_line else ''
        if text:
            txt_infolog.setText(f"{cur_text}{text}{end_line}")
        else:
            txt_infolog.setText(f"{cur_text}{end_line}")
        txt_infolog.show()
        # Scroll to the bottom
        scrollbar = txt_infolog.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _load_user_values(self):
        """ Load QGIS settings related with file_manager """

        # Mesh combo
        value = tools_dr.get_config_parser('btn_execute_model', 'cmb_mesh', "user", "session")
        if value:
            tools_qt.set_combo_value(self.execute_dlg.cmb_mesh, value, 0, False)

        # Export file path
        value = tools_dr.get_config_parser('btn_execute_model', 'txt_folder_path', "user", "session")
        if value:
            tools_qt.set_widget_text(self.execute_dlg, 'txt_folder_path', value)

    def _save_user_values(self):
        """ Save QGIS settings related with file_manager """

        # Mesh combo
        value = tools_qt.get_combo_value(self.execute_dlg, 'cmb_mesh')
        tools_dr.set_config_parser('btn_execute_model', 'cmb_mesh', value, "user", "session")

        # Export file path
        value = f"{tools_qt.get_text(self.execute_dlg, 'txt_folder_path', return_string_null=False)}"
        tools_dr.set_config_parser('btn_execute_model', 'txt_folder_path', f"{value}")

    def _calculate_elapsed_time(self, dialog):

        tf = time()  # Final time
        td = tf - self.t0  # Delta time
        self._update_time_elapsed(f"Exec. time: {timedelta(seconds=round(td))}", dialog)

    def _update_time_elapsed(self, text, dialog):

        if isdeleted(dialog):
            self.timer.stop()
            return

        lbl_timer = dialog.findChild(QLabel, 'lbl_timer')
        lbl_timer.setText(text)
