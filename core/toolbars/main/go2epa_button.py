"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from functools import partial
from time import time
from datetime import timedelta

from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QLabel, QTextEdit
from qgis.core import QgsApplication

from ...threads.epa_file_manager import DrEpaFileManager
from ...shared.options import DrOptions
from ...utils import tools_dr, Feedback
from ...ui.ui_manager import DrGo2EpaUI
from .... import global_vars
from ....lib import tools_qgis, tools_qt, tools_os
from ..dialog import DrAction


class DrGo2IberButton(DrAction):
    """ Button 23: Go2epa """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.project_type = global_vars.project_type
        self.epa_options_list = []
        self.cur_process = None
        self.cur_text = None

    def clicked_event(self):

        self._open_go2epa()

    # region private functions

    def _open_go2epa(self):
        """ Button 23: Open form to set INP, RPT and project """

        # Show form in docker?
        # tools_dr.init_docker('qgis_form_docker')

        # Create dialog
        self.dlg_go2epa = DrGo2EpaUI()
        tools_dr.load_settings(self.dlg_go2epa)
        self._load_user_values()
        # self.dlg_go2epa.chk_export_subcatch.setVisible(False)

        # Set signals
        self._set_signals()
        self.dlg_go2epa.btn_cancel.setEnabled(False)

        # Disable tab log
        tools_dr.disable_tab_log(self.dlg_go2epa)

        # Set shortcut keys
        self.dlg_go2epa.key_escape.connect(partial(tools_dr.close_docker))

        if global_vars.session_vars['dialog_docker']:
            tools_qt.manage_translation('go2epa', self.dlg_go2epa)
            tools_dr.docker_dialog(self.dlg_go2epa)
            self.dlg_go2epa.btn_close.clicked.disconnect()
            self.dlg_go2epa.btn_close.clicked.connect(partial(tools_dr.close_docker, option_name='position'))
        else:
            tools_dr.open_dialog(self.dlg_go2epa, dlg_name='go2epa')

    def _set_signals(self):

        self.dlg_go2epa.btn_cancel.clicked.connect(self._cancel_task)
        self.dlg_go2epa.btn_file_path.clicked.connect(partial(self._manage_btn_file_path))
        self.dlg_go2epa.btn_accept.clicked.connect(self._go2epa_accept)
        self.dlg_go2epa.btn_close.clicked.connect(partial(tools_dr.close_dialog, self.dlg_go2epa))
        self.dlg_go2epa.rejected.connect(partial(tools_dr.close_dialog, self.dlg_go2epa))
        self.dlg_go2epa.btn_options.clicked.connect(self._go2epa_options)
        self.dlg_go2epa.mainTab.currentChanged.connect(partial(self._manage_btn_accept))

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

    def _progress_changed(self, process, progress, text, new_line):
        # TextEdit log
        txt_infolog = self.dlg_go2epa.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.dlg_go2epa, txt_infolog, return_string_null=False)
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

    def _check_fields(self):

        result_name = tools_qt.get_text(self.dlg_go2epa, self.dlg_go2epa.txt_file_path, False, False)

        # Control result name
        if result_name == '':
            self.dlg_go2epa.txt_file_path.setStyleSheet("border: 1px solid red")
            msg = "This parameter is mandatory. Please, set a value"
            tools_qt.show_details(msg, title="Rpt fail", inf_text=None)
            return False

        self.dlg_go2epa.txt_file_path.setStyleSheet(None)

        return True

    def _load_user_values(self):
        """ Load QGIS settings related with file_manager """

        # Export file path
        value = tools_dr.get_config_parser('btn_go2epa', 'go2epa_file_path', "user", "session")
        self.dlg_go2epa.txt_file_path.setText(value)

        # value = tools_dr.get_config_parser('btn_go2epa', 'go2epa_chk_UD', "user", "session")
        # tools_qt.set_checked(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch, value)

    def _save_user_values(self):
        """ Save QGIS settings related with file_manager """

        # Export file path
        txt_file_path = f"{tools_qt.get_text(self.dlg_go2epa, 'txt_file_path', return_string_null=False)}"
        tools_dr.set_config_parser('btn_go2epa', 'go2epa_file_path', f"{txt_file_path}")
        # chk_export_subcatch = f"{tools_qt.is_checked(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch)}"
        # tools_dr.set_config_parser('btn_go2epa', 'go2epa_chk_UD', f"{chk_export_subcatch}")

    def _manage_form_settings(self, action):

        return

        # if action == 'save':
        #     # Get widgets form values
        #     self.txt_result_name = tools_qt.get_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name)
        #     # self.chk_export_subcatch = self.dlg_go2epa.chk_export_subcatch.isChecked()
        # elif action == 'restore':
        #     # Set widgets form values
        #     if self.txt_result_name is not 'null': tools_qt.set_widget_text(self.dlg_go2epa, self.dlg_go2epa.txt_result_name, self.txt_result_name)
        #     # if self.chk_export_subcatch is not 'null': tools_qt.set_widget_text(self.dlg_go2epa, self.dlg_go2epa.chk_export_subcatch, self.chk_export_subcatch)

    def _go2epa_accept(self):
        """ Save INP, RPT and result name"""

        # Manage if task is already running
        if hasattr(self, 'go2epa_task') and self.go2epa_task is not None:
            try:
                if self.go2epa_task.isActive():
                    msg = "Go2Epa task is already active!"
                    tools_qgis.show_warning(msg)
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
        self.export_file_path = tools_qt.get_text(self.dlg_go2epa, 'txt_file_path')
        if os.path.exists(self.export_file_path):
            try:
                msg = "The specified file already exists. Do you want to overwrite it?"
                response = tools_qt.show_question(msg, True)
                if not response:
                    return
                os.remove(self.export_file_path)
            except Exception:
                if os.path.isdir(self.export_file_path):
                    msg = "The specified path is a directory. Please, set a valid file name"
                    tools_qt.show_info_box(msg)
                return

        tools_dr.set_tabs_enabled(self.dlg_go2epa)
        self.dlg_go2epa.mainTab.setCurrentIndex(1)
        self.dlg_go2epa.btn_accept.setEnabled(False)
        self.dlg_go2epa.btn_cancel.setEnabled(True)

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.dlg_go2epa))
        self.timer.start(1000)

        # Set background task 'Go2Epa'
        description = f"{tools_qt.tr('Go2Epa')}"
        params = {"dialog": self.dlg_go2epa, "export_file_path": self.export_file_path}
        self.feedback = Feedback()
        self.go2epa_task = DrEpaFileManager(description, params, self.feedback, timer=self.timer)
        self._progress_changed("Export INP", 0, None, False)
        self.go2epa_task.progress_changed.connect(self._progress_changed)
        self.feedback.progress_changed.connect(self._progress_changed)
        QgsApplication.taskManager().addTask(self.go2epa_task)
        QgsApplication.taskManager().triggerTask(self.go2epa_task)

    def _cancel_task(self):

        if hasattr(self, 'go2epa_task'):
            self.go2epa_task.cancel()

    def _go2epa_options(self):
        self.go2epa_options = DrOptions(tabs_to_show=["tab_inp_swmm"])
        self.go2epa_options.open_options_dlg()

    def _calculate_elapsed_time(self, dialog):

        tf = time()  # Final time
        td = tf - self.t0  # Delta time
        self._update_time_elapsed(f"Exec. time: {timedelta(seconds=round(td))}", dialog)

    def _update_time_elapsed(self, text, dialog):

        try:
            lbl_time = dialog.findChild(QLabel, 'lbl_time')
            lbl_time.setText(text)
        except RuntimeError:
            self.timer.stop()
            return

    # endregion