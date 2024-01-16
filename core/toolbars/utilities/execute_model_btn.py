"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import sys
import json

from functools import partial
from sip import isdeleted
from time import time
from datetime import timedelta

from qgis.PyQt.QtCore import QStringListModel, Qt, QTimer
from qgis.PyQt.QtWidgets import QWidget, QComboBox, QCompleter, QFileDialog, QGroupBox, QSpacerItem, QSizePolicy, \
    QGridLayout, QLabel, QTabWidget, QVBoxLayout, QGridLayout
from qgis.core import QgsApplication

from ...threads.epa_file_manager import GwEpaFileManager
from ...shared.options import GwOptions
from ...utils import tools_gw
from ...ui.ui_manager import GwExecuteModelUi
from .... import global_vars
from ....lib import tools_qgis, tools_qt, tools_db, tools_os
from ..dialog import GwAction


class GwExecuteModelButton(GwAction):
    """ Button 38: Execute model """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.project_type = global_vars.project_type
        self.epa_options_list = []
        self.export_path = None


    def clicked_event(self):

        self._open_execute_dlg()


    def _open_execute_dlg(self):
        self.execute_dlg = GwExecuteModelUi()
        tools_gw.load_settings(self.execute_dlg)

        # Populate combobox
        self._populate_mesh_cmb()

        # Signals
        self.execute_dlg.btn_options.clicked.connect(self._go2epa_options)
        self.execute_dlg.btn_folder_path.clicked.connect(partial(self._manage_btn_folder_path))
        self.execute_dlg.btn_accept.clicked.connect(partial(self._execute_model))

        tools_gw.open_dialog(self.execute_dlg, 'dlg_execute_model')


    def _populate_mesh_cmb(self):
        sql = "SELECT id, name as idval FROM cat_file"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(self.execute_dlg.cmb_mesh, rows, add_empty=True)


    def _go2epa_options(self):
        self.go2epa_options = GwOptions()
        self.go2epa_options.open_options_dlg()


    def _manage_btn_folder_path(self):
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.execute_dlg, 'txt_folder_path', str(path))


    def _execute_model(self):
        # Check if results exist on folder
        self.export_path = tools_qt.get_text(self.execute_dlg, 'txt_folder_path')
        if os.path.exists(f"{self.export_path}{os.sep}Iber2D.dat"):
            message = "Results files already exist in this path. Do you want to overwrite them?"
            answer = tools_qt.show_question(message, "overwrite file", force_action=True)
            if not answer:
                return False

        # Mesh files
        self._copy_mesh_files()

        # INP file
        self._generate_inp()


    def _copy_mesh_files(self):

        mesh_id = tools_qt.get_combo_value(self.execute_dlg, 'cmb_mesh')
        sql = f"SELECT iber2d, roof, losses FROM cat_file WHERE id = '{mesh_id}'"
        row = tools_db.get_row(sql)
        if row:
            iber2d_content, roof_content, losses_content = row

            # Write content to files
            self._write_to_file(f'{self.export_path}{os.sep}Iber2D.dat', iber2d_content)

            if roof_content:
                self._write_to_file(f'{self.export_path}{os.sep}Iber_SWMM_roof.dat', roof_content)

            if losses_content:
                self._write_to_file(f'{self.export_path}{os.sep}Iber_Losses.dat', losses_content)


    def _write_to_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)


    def _generate_inp(self):
        # INP file
        self.export_file_path = f"{self.export_path}{os.sep}Iber_SWMM.inp"

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.execute_dlg))
        self.timer.start(1000)

        # Set background task 'Go2Epa'
        description = f"Go2Epa"
        self.go2epa_task = GwEpaFileManager(description, self, timer=self.timer)
        QgsApplication.taskManager().addTask(self.go2epa_task)
        QgsApplication.taskManager().triggerTask(self.go2epa_task)


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
