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
from ...shared.options import PcOptions
from ...utils import tools_gw
from ...ui.ui_manager import GwGo2EpaUI, GwGo2EpaOptionsUi
from .... import global_vars
from ....lib import tools_qgis, tools_qt, tools_db, tools_os
from ..dialog import GwAction


class GwGo2IberButton(GwAction):
    """ Button 23: Go2epa """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.project_type = global_vars.project_type
        self.epa_options_list = []


    def clicked_event(self):

        self._open_go2epa()


    def check_result_id(self):
        """ Check if selected @result_id already exists """

        self.dlg_go2epa.txt_result_name.setStyleSheet(None)


    # region private functions

    def _open_go2epa(self):
        """ Button 23: Open form to set INP, RPT and project """

        # Show form in docker?
        # tools_gw.init_docker('qgis_form_docker')

        # Create dialog
        self.dlg_go2epa = GwGo2EpaUI()
        tools_gw.load_settings(self.dlg_go2epa)
        self._load_user_values()
        # self.dlg_go2epa.chk_export_subcatch.setVisible(False)

        # Set signals
        self._set_signals()
        self.dlg_go2epa.btn_cancel.setEnabled(False)

        # Enable/disable 'Export INP file' widgets
        self._manage_chk_export_file(tools_qt.is_checked(self.dlg_go2epa, 'chk_export_file'))

        # Disable tab log
        tools_gw.disable_tab_log(self.dlg_go2epa)

        # Set shortcut keys
        self.dlg_go2epa.key_escape.connect(partial(tools_gw.close_docker))

        self.check_result_id()
        if global_vars.session_vars['dialog_docker']:
            tools_qt.manage_translation('go2epa', self.dlg_go2epa)
            tools_gw.docker_dialog(self.dlg_go2epa)
            self.dlg_go2epa.btn_close.clicked.disconnect()
            self.dlg_go2epa.btn_close.clicked.connect(partial(tools_gw.close_docker, option_name='position'))
        else:
            tools_gw.open_dialog(self.dlg_go2epa, dlg_name='go2epa')


    def _set_signals(self):

        self.dlg_go2epa.btn_cancel.clicked.connect(self._cancel_task)
        self.dlg_go2epa.txt_result_name.textChanged.connect(partial(self.check_result_id))
        self.dlg_go2epa.chk_export_file.stateChanged.connect(partial(self._manage_chk_export_file))
        self.dlg_go2epa.btn_file_path.clicked.connect(partial(self._manage_btn_file_path))
        self.dlg_go2epa.btn_accept.clicked.connect(self._go2epa_accept)
        self.dlg_go2epa.btn_close.clicked.connect(partial(tools_gw.close_dialog, self.dlg_go2epa))
        self.dlg_go2epa.rejected.connect(partial(tools_gw.close_dialog, self.dlg_go2epa))
        self.dlg_go2epa.btn_options.clicked.connect(self._go2epa_options)
        self.dlg_go2epa.mainTab.currentChanged.connect(partial(self._manage_btn_accept))


    def _manage_chk_export_file(self, checked):

        tools_qt.set_widget_enabled(self.dlg_go2epa, 'txt_file_path', bool(checked))
        tools_qt.set_widget_enabled(self.dlg_go2epa, 'btn_file_path', bool(checked))


    def _manage_btn_file_path(self):

        path = tools_os.open_save_file_path(extension="*.inp")
        if path:
            tools_qt.set_widget_text(self.dlg_go2epa, 'txt_file_path', str(path))


    def _manage_btn_accept(self, index):
        """
        Disable btn_accept when on tab info log and/or if go2epa_task is active
            :param index: tab index (passed by signal)
        """

        if index == 1:
            self.dlg_go2epa.btn_accept.setEnabled(False)
        else:
            # Disable if task is active, enabled otherwise
            if hasattr(self, 'go2epa_task') and self.go2epa_task is not None:
                try:
                    if self.go2epa_task.isActive():
                        self.dlg_go2epa.btn_accept.setEnabled(False)
                        return
                except RuntimeError:
                    pass
            self.dlg_go2epa.btn_accept.setEnabled(True)


    def _check_fields(self):

        result_name = tools_qt.get_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name, False, False)

        # Control result name
        if result_name == '':
            self.dlg_go2epa.txt_result_name.setStyleSheet("border: 1px solid red")
            msg = "This parameter is mandatory. Please, set a value"
            tools_qt.show_details(msg, title="Rpt fail", inf_text=None)
            return False

        self.dlg_go2epa.txt_result_name.setStyleSheet(None)

        # TODO: check in cat_file
        # sql = (f"SELECT result_id FROM rpt_cat_result "
        #        f"WHERE result_id = '{result_name}' LIMIT 1")
        # row = tools_db.get_row(sql)
        # if row:
        #     msg = "Result name already exists, do you want overwrite?"
        #     answer = tools_qt.show_question(msg, title="Alert")
        #     if not answer:
        #         return False

        return True


    def _load_user_values(self):
        """ Load QGIS settings related with file_manager """

        # Result name
        self.dlg_go2epa.txt_result_name.setMaxLength(16)
        self.result_name = tools_gw.get_config_parser('btn_go2epa', 'go2epa_RESULT_NAME', "user", "session")
        self.dlg_go2epa.txt_result_name.setText(self.result_name)
        # Check export file
        value = tools_gw.get_config_parser('btn_go2epa', 'go2epa_chk_export_file', "user", "session")
        tools_qt.set_checked(self.dlg_go2epa, 'chk_export_file', value)
        # Export file path
        value = tools_gw.get_config_parser('btn_go2epa', 'go2epa_file_path', "user", "session")
        self.dlg_go2epa.txt_file_path.setText(value)

        # value = tools_gw.get_config_parser('btn_go2epa', 'go2epa_chk_UD', "user", "session")
        # tools_qt.set_checked(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch, value)


    def _save_user_values(self):
        """ Save QGIS settings related with file_manager """

        # Result name
        txt_result_name = f"{tools_qt.get_text(self.dlg_go2epa, 'txt_result_name', return_string_null=False)}"
        tools_gw.set_config_parser('btn_go2epa', 'go2epa_RESULT_NAME', f"{txt_result_name}")
        # Check export file
        chk_export_file = tools_qt.is_checked(self.dlg_go2epa, 'chk_export_file')
        tools_gw.set_config_parser('btn_go2epa', 'go2epa_chk_export_file', f"{chk_export_file}")
        # Export file path
        txt_file_path = f"{tools_qt.get_text(self.dlg_go2epa, 'txt_file_path', return_string_null=False)}"
        tools_gw.set_config_parser('btn_go2epa', 'go2epa_file_path', f"{txt_file_path}")
        # chk_export_subcatch = f"{tools_qt.is_checked(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch)}"
        # tools_gw.set_config_parser('btn_go2epa', 'go2epa_chk_UD', f"{chk_export_subcatch}")


    def _manage_form_settings(self, action):

        if action == 'save':
            # Get widgets form values
            self.txt_result_name = tools_qt.get_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name)
            # self.chk_export_subcatch = self.dlg_go2epa.chk_export_subcatch.isChecked()
        elif action == 'restore':
            # Set widgets form values
            if self.txt_result_name is not 'null': tools_qt.set_widget_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name, self.txt_result_name)
            # if self.chk_export_subcatch is not 'null': tools_qt.set_widget_text(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch, self.chk_export_subcatch)


    def _go2epa_accept(self):
        """ Save INP, RPT and result name"""

        # Manage if task is already running
        if hasattr(self, 'go2epa_task') and self.go2epa_task is not None:
            try:
                if self.go2epa_task.isActive():
                    message = "Go2Epa task is already active!"
                    tools_qgis.show_warning(message)
                    return
            except RuntimeError:
                pass

        # Save user values
        self._save_user_values()

        self.dlg_go2epa.txt_infolog.clear()
        status = self._check_fields()
        if status is False:
            return

        # Get widgets values
        self.result_name = tools_qt.get_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name, False, False)
        # self.export_subcatch = tools_qt.is_checked(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch)
        self.export_file = tools_qt.is_checked(self.dlg_go2epa, 'chk_export_file')
        self.export_file_path = tools_qt.get_text(self.dlg_go2epa, 'txt_file_path')

        self.dlg_go2epa.btn_accept.setEnabled(False)
        self.dlg_go2epa.btn_cancel.setEnabled(True)

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.dlg_go2epa))
        self.timer.start(1000)

        # Set background task 'Go2Epa'
        description = f"Go2Epa"
        self.go2epa_task = GwEpaFileManager(description, self, timer=self.timer)
        QgsApplication.taskManager().addTask(self.go2epa_task)
        QgsApplication.taskManager().triggerTask(self.go2epa_task)


    def _cancel_task(self):

        if hasattr(self, 'go2epa_task'):
            self.go2epa_task.cancel()


    def _go2epa_options(self):
        self.go2epa_options = PcOptions()
        self.go2epa_options.open_options_dlg()


    def _calculate_elapsed_time(self, dialog):

        tf = time()  # Final time
        td = tf - self.t0  # Delta time
        self._update_time_elapsed(f"Exec. time: {timedelta(seconds=round(td))}", dialog)

    def _update_time_elapsed(self, text, dialog):

        if isdeleted(dialog):
            self.timer.stop()
            return

        lbl_time = dialog.findChild(QLabel, 'lbl_time')
        lbl_time.setText(text)

    # endregion