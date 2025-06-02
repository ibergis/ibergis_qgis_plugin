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

from qgis.core import QgsProcessingContext
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QLabel, QTextEdit

from ..dialog import DrAction
from ...processing.check_project import DrCheckProjectAlgorithm
from ...ui.ui_manager import DrProjectCheckUi

from ...utils import tools_dr, Feedback
from ....lib import tools_qt


class DrProjectCheckButton(DrAction):
    """ Button 59: Check project """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.cur_process = None
        self.cur_text = None

    def clicked_event(self):

        self._open_check_project()

    # region private functions

    def _open_check_project(self):

        self._open_dialog()

        # Return layers in the same order as listed in TOC
        # layers = tools_qgis.get_project_layers()

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.dlg_audit_project))
        self.timer.start(1000)

        # Execute CheckProjectAlgorithm
        self._progress_update(None, 0, "\nCheck Project Algorithm\n", True)
        self.feedback = Feedback()
        self.feedback.progress_changed.connect(self._progress_update)
        self.process = DrCheckProjectAlgorithm()
        self.process.initAlgorithm(None)
        context: QgsProcessingContext = QgsProcessingContext()
        self.output = self.process.processAlgorithm({}, context, self.feedback)
        if self.output:
            return
        self._progress_update(None, 60, None, False)
        # Load temporal layers
        self.output = self.process.postProcessAlgorithm(context, self.feedback)
        if self.output:
            return
        self._progress_update(None, 100, None, True)
        self._progress_update(None, None, "Check Project Algorithm.....Executed", True)
        self.dlg_audit_project.btn_accept.setEnabled(True)

        self.timer.stop()

    def _progress_update(self, process, progress, text, new_line):
        # Progress bar
        if progress is not None:
            self.dlg_audit_project.progressBar.setValue(progress)

        # TextEdit log
        txt_infolog = self.dlg_audit_project.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.dlg_audit_project, txt_infolog, return_string_null=False)
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

    # def _progress_update(self, process, progress, text, new_line):
    #     txt_infolog = dialog.findChild(QTextEdit, 'txt_infolog')
    #     cur_text = tools_qt.get_text(self.dlg_audit_project, txt_infolog, return_string_null=False)
    #     text = f"{cur_text}{text}"
    #     txt_infolog.setText(text)
    #     txt_infolog.show()
        # tools_qt.set_widget_text(self.dlg_audit_project, txt_infolog, text)

    def _open_dialog(self):

        # Create dialog
        self.dlg_audit_project = DrProjectCheckUi()
        tools_dr.load_settings(self.dlg_audit_project)

        tools_qt.set_widget_enabled(self.dlg_audit_project, 'btn_accept', False)

        self.dlg_audit_project.btn_accept.clicked.connect(self.dlg_audit_project.reject)
        self.dlg_audit_project.rejected.connect(partial(tools_dr.save_settings, self.dlg_audit_project))

        # Open dialog
        tools_dr.open_dialog(self.dlg_audit_project, dlg_name='project_check')

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
