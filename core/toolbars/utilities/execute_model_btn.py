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
from ....lib import tools_qgis, tools_qt, tools_db
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
        self.execute_dlg.btn_ok.clicked.connect(partial(self._execute_model))

        tools_gw.open_dialog(self.execute_dlg, 'dlg_execute_model')


    def _populate_mesh_cmb(self):
        sql = "SELECT id, name as idval FROM cat_file"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(self.execute_dlg.cmb_mesh, rows, add_empty=True)


    def _go2epa_options(self):
        self.go2epa_options = GwOptions()
        self.go2epa_options.open_options_dlg()


    def _execute_model(self):
        msg = "This tool hasn't been implemented yet."
        tools_qt.show_info_box(msg)
        return

        inp_file_path = f"{self.export_path}{os.sep}Iber_SWMM.inp"
        if os.path.exists(inp_file_path):
            message = "An Iber_SWMM.inp file already exists in this path. Do you want to overwrite file?"
            answer = tools_qt.show_question(message, "overwrite file", force_action=True)
            if not answer:
                return False
