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


    def clicked_event(self):

        self._open_execute_dlg()


    def _open_execute_dlg(self):
        self.execute_dlg = GwExecuteModelUi()
        tools_gw.load_settings(self.execute_dlg)

        tools_gw.open_dialog(self.execute_dlg, 'dlg_execute_model')
