"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from functools import partial
from sip import isdeleted
from time import time
from datetime import timedelta

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QLabel, QTextEdit

from ..dialog import GwAction
from ...threads.project_check import GwProjectCheckTask
from ...ui.ui_manager import GwProjectCheckUi

from ...utils import tools_gw
from ....lib import tools_qgis, tools_qt


class GwProjectCheckButton(GwAction):
    """ Button 59: Check project """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):

        self._open_check_project()


    # region private functions

    def _open_check_project(self):

        self._open_dialog()

        # Return layers in the same order as listed in TOC
        layers = tools_qgis.get_project_layers()

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.dlg_audit_project))
        self.timer.start(1000)

        params = {"layers": layers, "init_project": "false", "dialog": self.dlg_audit_project}
        self.project_check_task = GwProjectCheckTask('check_project', params, timer=self.timer)
        self.project_check_task.progressUpdate.connect(partial(self._progress_update, self.dlg_audit_project))
        QgsApplication.taskManager().addTask(self.project_check_task)
        QgsApplication.taskManager().triggerTask(self.project_check_task)


    def _progress_update(self, dialog, text):
        txt_infolog = dialog.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.dlg_audit_project, txt_infolog, return_string_null=False)
        text = f"{cur_text}{text}"
        txt_infolog.setText(text)
        txt_infolog.show()
        # tools_qt.set_widget_text(self.dlg_audit_project, txt_infolog, text)


    def _open_dialog(self):

        # Create dialog
        self.dlg_audit_project = GwProjectCheckUi()
        tools_gw.load_settings(self.dlg_audit_project)

        tools_qt.set_widget_enabled(self.dlg_audit_project, 'btn_accept', False)

        self.dlg_audit_project.btn_accept.clicked.connect(self.dlg_audit_project.reject)
        self.dlg_audit_project.rejected.connect(partial(tools_gw.save_settings, self.dlg_audit_project))

        # Open dialog
        tools_gw.open_dialog(self.dlg_audit_project, dlg_name='project_check')


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
