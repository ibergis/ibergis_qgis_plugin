"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import Qgis, QgsEditFormConfig

from .task import DrTask
from ..utils import tools_dr, tools_fct
from ...lib import tools_log, tools_qgis, tools_qt, tools_os


class DrProjectLayersConfig(DrTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()

    def __init__(self, description, params):

        super().__init__(description)
        self.exception = None
        self.message = None
        self.available_layers = None
        self.body = None
        self.json_result = None
        self.vr_errors = None
        self.vr_missing = None


    def run(self):

        super().run()
        self.setProgress(0)
        self.vr_errors = set()
        self.vr_missing = set()
        self._get_layers_to_config()
        self._set_layer_config(self.available_layers)
        self.setProgress(100)

        return True


    def finished(self, result):

        super().finished(result)

        sql = "SELECT gw_fct_getinfofromid("
        if self.body:
            sql += f"{self.body}"
        sql += ");"
        tools_dr.manage_json_response(self.json_result, sql, None)

        # If user cancel task
        if self.isCanceled():
            return

        if result:
            if self.exception:
                if self.message:
                    msg = "{0}"
                    msg_params = (self.message,)
                    tools_log.log_warning(msg, msg_params=msg_params)
            return

        # If sql function return null
        if result is False:
            msg = "Task failed: {0}. This is probably a DB error, check postgres function '{1}'"
            msg_params = (self.description(), "gw_fct_getinfofromid",)
            tools_log.log_warning(msg, msg_params=msg_params)

        if self.exception:
            msg = "Task aborted: {0}"
            msg_params = (self.description(),)
            tools_log.log_info(msg, msg_params=msg_params)
            msg = "Exception: {0}"
            msg_params = (self.exception,)
            tools_log.log_warning(msg, msg_params=msg_params)


    # region private functions


    def _get_layers_to_config(self):
        """ Get available layers to be configured """

        self.available_layers = []

        all_layers_toc = tools_qgis.get_project_layers()
        for layer in all_layers_toc:
            table_name = tools_qgis.get_tablename_from_layer(layer)
            if table_name not in self.available_layers:
                self.available_layers.append(table_name)

        self._set_form_suppress(self.available_layers)


    def _set_form_suppress(self, layers_list):
        """ Set form suppress on "Hide form on add feature (global settings) """

        for layer_name in layers_list:
            layer = tools_qgis.get_layer_by_tablename(layer_name)
            if layer is None:
                continue
            if not hasattr(layer, 'editFormConfig'):
                continue
            config = layer.editFormConfig()
            if Qgis.QGIS_VERSION_INT >= 33200:
                config.setSuppress(QgsEditFormConfig.FeatureFormSuppress.Default)
            else:
                config.setSuppress(0)
            layer.setEditFormConfig(config)


    def _set_layer_config(self, layers):
        """ Set layer fields configured according to client configuration.
            At the moment manage:
                Column names as alias, combos as ValueMap, typeahead as textedit"""

        # Check only once if function 'getinfofromid' exists
        function_name = 'getinfofromid'
        exists = tools_os.check_python_function(tools_fct, function_name)
        if not exists:
            msg = "Function not found in {0}"
            msg_params = ("tools_fct",)
            tools_qgis.show_warning(msg, msg_params=msg_params, parameter=function_name)
            return None

        msg_failed = ""
        msg_key = ""
        total_layers = len(layers)
        layer_number = 0
        for layer_name in layers:

            if self.isCanceled():
                return False

            layer = tools_qgis.get_layer_by_tablename(layer_name)
            if not layer:
                continue

            layer_number = layer_number + 1
            self.setProgress((layer_number * 100) / total_layers)

            feature = f'"tableName":"{layer_name}", "isLayer":true'
            self.body = tools_dr.create_body(feature=feature)
            self.json_result = tools_dr.execute_procedure(function_name, self.body, is_thread=True, check_function=False)
            if not self.json_result:
                continue
            if 'status' not in self.json_result:
                continue
            if self.json_result['status'] == 'Failed':
                continue
            if 'body' not in self.json_result:
                msg = "Not '{0}'"
                msg_params = ("body",)
                tools_log.log_info(msg, msg_params=msg_params)
                continue
            if 'data' not in self.json_result['body']:
                msg = "Not '{0}'"
                msg_params = ("data",)
                tools_log.log_info(msg, msg_params=msg_params)
                continue

            print(f"{layer_name=}")
            tools_dr.config_layer_attributes(self.json_result, layer, layer_name, thread=self)

        if msg_failed != "":
            title = "Execute failed."
            tools_qt.show_exception_message(title, msg_failed)

        if msg_key != "":
            title = "Key on returned json from ddbb is missed."
            tools_qt.show_exception_message(title, msg_key)

    # endregion
