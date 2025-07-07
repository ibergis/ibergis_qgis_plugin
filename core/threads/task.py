"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.core import QgsTask
from qgis.utils import iface

from ... import global_vars
from ...lib import tools_log


class DrTask(QgsTask, QObject):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()

    def __init__(self, description, duration=0):

        QObject.__init__(self)
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.duration = duration
        self.aux_conn = None

    def run(self) -> bool:

        global_vars.session_vars['threads'].append(self)
        # self.aux_conn = global_vars.dao.get_aux_conn()
        msg = "Started task {0}"
        msg_params = (self.description(),)
        tools_log.log_info(msg, msg_params=msg_params)
        iface.actionOpenProject().setEnabled(False)
        iface.actionNewProject().setEnabled(False)
        return True

    def finished(self, result):

        try:
            global_vars.session_vars['threads'].remove(self)
        except ValueError:
            pass
        # global_vars.dao.delete_aux_con(self.aux_conn)
        iface.actionOpenProject().setEnabled(True)
        iface.actionNewProject().setEnabled(True)
        if result:
            msg = "Task '{0}' completed"
            msg_params = (self.description(),)
            tools_log.log_info(msg, msg_params=msg_params)
        else:
            if self.exception is None:
                msg = "Task '{0}' not successful but without exception"
                msg_params = (self.description(),)
                tools_log.log_info(msg, msg_params=msg_params)
            else:
                msg = "Task '{0}' Exception: {1}"
                msg_params = (self.description(), self.exception,)
                tools_log.log_info(msg, msg_params=msg_params)

    def cancel(self):

        msg = "Task '{0}' was cancelled"
        msg_params = (self.description(),)
        tools_log.log_info(msg, msg_params=msg_params)
        super().cancel()