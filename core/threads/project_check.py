"""
This file is part of IberGIS
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-


from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProcessingContext


from ..processing.check_project import DrCheckProjectAlgorithm
from ..utils import Feedback
from .task import DrTask
from ...lib import tools_qt
from functools import partial


class DrProjectCheckTask(DrTask):

    task_finished = pyqtSignal(list)
    progressUpdate = pyqtSignal(str, int, str, bool)

    def __init__(self, description='', params=None, timer=None):

        super().__init__(description)
        self.params = params
        self.result = None
        self.dlg_audit_project = None
        self.timer = timer
        self.exception = None
        self.show_only_errors: bool = self.params['chb_info'] if self.params else False
        self.feedback = None
        self.process = None
        self.context = None
        self.output = None
        self.txt_infolog = self.params['txt_infolog'] if self.params else None

        self.log_messages = []
        self.log_features_arc = []
        self.log_features_node = []
        self.log_features_polygon = []

    def run(self):

        super().run()

        # Execute CheckProjectAlgorithm
        self.progressUpdate.emit(None, 0, "\nCheck Project Algorithm\n", True)
        self.feedback = Feedback()
        self.feedback.progress_changed.connect(partial(self.progressUpdate.emit))
        self.process = DrCheckProjectAlgorithm()
        self.process.initAlgorithm(None)
        self.context = QgsProcessingContext()
        self.output = self.process.processAlgorithm({'BOOL_SHOW_INFO': self.show_only_errors, 'TXT_INFOLOG': self.txt_infolog}, self.context, self.feedback)
        if self.output:
            return

        return True

    def finished(self, result):

        super().finished(result)

        if self.isCanceled():
            self.setProgress(100)
            return

        # Load temporal layers
        if self.process is not None:
            # Execute postProcessAlgorithm and capture feedback messages
            self.output = self.process.postProcessAlgorithm(self.context, self.feedback)

            # Emit error messages
            msg = "Errors"
            self.progressUpdate.emit(None, None, f"\n{tools_qt.tr(msg)}\n----------", True)
            for msg in self.process.error_messages:
                self.progressUpdate.emit(None, None, msg, True)

            # Emit warning messages
            msg = "Warnings"
            self.progressUpdate.emit(None, None, f"\n{tools_qt.tr(msg)}\n--------------", True)
            for msg in self.process.warning_messages:
                self.progressUpdate.emit(None, None, msg, True)

            # Emit info messages if enabled
            if not self.show_only_errors:
                msg = "Info"
                self.progressUpdate.emit(None, None, f"\n{tools_qt.tr(msg)}\n------", True)
                for msg in self.process.info_messages:
                    self.progressUpdate.emit(None, None, msg, True)

        if self.output:
            return

        self.progressUpdate.emit(None, 100, None, True)
        msg = "Check Project Algorithm.....Finished"
        self.progressUpdate.emit(None, None, tools_qt.tr(msg), True)

        if self.timer:
            self.timer.stop()

        # Scroll to top
        self.txt_infolog.verticalScrollBar().setValue(0)

        self.setProgress(100)
