"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, pyqtSignal

import os

from .task import DrTask
from ..utils import tools_dr
from ...lib import tools_qt, tools_log
from ... import global_vars


class DrGpkgCreateSchemaTask(DrTask):

    task_finished = pyqtSignal(list)

    def __init__(self, admin, description, params, timer=None):

        super().__init__(description)
        self.admin = admin
        self.params = params
        self.dict_folders_process = {}
        self.db_exception = (None, None, None)  # error, sql, filepath
        self.timer = timer
        self.config_dao = None

        # # Manage buttons & other dlg-related widgets
        # # Disable dlg_readsql_create_project buttons
        # self.admin.dlg_readsql_create_project.btn_cancel_task.show()
        # self.admin.dlg_readsql_create_project.btn_accept.hide()
        # self.admin.dlg_readsql_create_project.btn_close.setEnabled(False)
        # try:
        #     self.admin.dlg_readsql_create_project.key_escape.disconnect()
        # except TypeError:
        #     pass

        # # Disable red 'X' from dlg_readsql_create_project
        # self.admin.dlg_readsql_create_project.setWindowFlag(Qt.WindowCloseButtonHint, False)
        # self.admin.dlg_readsql_create_project.show()
        # # Disable dlg_readsql buttons
        # self.admin.dlg_readsql.btn_close.setEnabled(False)


    def run(self):

        super().run()
        self.finish_execution = {'import_data': False}
        self.dict_folders_process = {}
        self.admin.total_sql_files = 0
        self.admin.current_sql_file = 0
        self.config_dao = global_vars.gpkg_dao_config.clone()
        tools_log.log_info(f"Create schema: Executing function 'main_execution'")
        status = self.main_execution()
        if not status:
            tools_log.log_info("Function main_execution returned False")
            return False
        return True


    def finished(self, result):

        super().finished(result)
        # # Enable dlg_readsql_create_project buttons
        # self.admin.dlg_readsql_create_project.btn_cancel_task.hide()
        # self.admin.dlg_readsql_create_project.btn_accept.show()
        # self.admin.dlg_readsql_create_project.btn_close.setEnabled(True)
        # # Enable red 'X' from dlg_readsql_create_project
        # self.admin.dlg_readsql_create_project.setWindowFlag(Qt.WindowCloseButtonHint, True)
        # self.admin.dlg_readsql_create_project.show()
        # # Disable dlg_readsql buttons
        # self.admin.dlg_readsql.btn_close.setEnabled(True)

        if self.isCanceled():
            if self.timer:
                self.timer.stop()
            self.setProgress(100)
            # Handle db exception
            if self.db_exception != (None, None, None):
                error, sql, filepath = self.db_exception
                tools_qt.manage_exception_db(error, sql, filepath=filepath)
            return

        # Handle exception
        if self.exception is not None:
            msg = f"<b>Key: </b>{self.exception}<br>"
            msg += f"<b>key container: </b>'body/data/ <br>"
            msg += f"<b>Python file: </b>{__name__} <br>"
            msg += f"<b>Python function:</b> {self.__class__.__name__} <br>"
            tools_qt.show_exception_message("Key on returned json from ddbb is missed.", msg)

        if self.timer:
            self.timer.stop()

        self.admin.manage_process_result()
        self.setProgress(100)


    def main_execution(self) -> bool:
        """ Main common execution """

        tools_log.log_info(f"Creating GPKG {self.admin.gpkg_name}'")
        tools_log.log_info(f"Create schema: Executing function 'create_gpkg'")
        create_gpkg_status = self.admin.create_gpkg()
        if not create_gpkg_status:
            return False

        tools_log.log_info(f"Create schema: Executing function '_check_database_connection'")
        connection_status = self.admin._check_database_connection(self.admin.gpkg_full_path, self.admin.gpkg_name)
        if not connection_status:
            tools_log.log_info("Function '_check_database_connection' returned False")
            return False

        tools_log.log_info(f"Create schema: Executing function 'main_execution'")
        status = self.admin.create_schema_main_execution()
        if not status:
            tools_log.log_info("Function 'main_execution' returned False")
            return False

        tools_log.log_info(f"Create schema: Executing function 'custom_execution'")
        status_custom = self.admin.create_schema_custom_execution(self.config_dao)
        if not status_custom:
            tools_log.log_info("Function 'custom_execution' returned False")
            return False

        return True

    def custom_execution(self):
        """ Custom execution """

        example_data = self.params['example_data']
        tools_log.log_info("Execute 'custom_execution'")
        if self.admin.rdb_sample.isChecked() and example_data:
            tools_dr.set_config_parser('btn_admin', 'create_schema_type', 'rdb_sample', prefix=False)
            self.admin.load_sample_data()
        elif self.admin.rdb_data.isChecked():
            tools_dr.set_config_parser('btn_admin', 'create_schema_type', 'rdb_data', prefix=False)


    def calculate_number_of_files(self):
        """ Calculate total number of SQL to execute """

        total_sql_files = 0
        dict_process = {}
        list_process = ['load_base']

        for process_name in list_process:
            tools_log.log_info(f"Create schema: Executing function get_number_of_files_process('{process_name}')")
            dict_folders, total = self.get_number_of_files_process(process_name)
            total_sql_files += total
            tools_log.log_info(f"Number of SQL files '{process_name}': {total}")
            dict_process[process_name] = total
            self.dict_folders_process[process_name] = dict_folders

        return total_sql_files


    def get_number_of_files_process(self, process_name: str):
        """ Calculate number of files of all folders of selected @process_name """

        tools_log.log_info(f"Create schema: Executing function get_folders_process('{process_name}')")
        dict_folders = self.get_folders_process(process_name)
        if dict_folders is None:
            return dict_folders, 0

        number_of_files = 0
        for folder in dict_folders.keys():
            file_count = sum(len(files) for _, _, files in os.walk(folder))
            number_of_files += file_count
            dict_folders[folder] = file_count

        return dict_folders, number_of_files


    def get_folders_process(self, process_name):
        """ Get list of folders related with this @process_name """

        dict_folders = {}
        if process_name == 'load_base':
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_sys_gpkg)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_ddl)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_dml)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_rtree)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_trg)] = 0

        return dict_folders

