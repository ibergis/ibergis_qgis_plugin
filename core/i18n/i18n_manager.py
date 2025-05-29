"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import re
import os
import sqlite3
from psycopg2.extras import execute_values
from functools import partial
from datetime import datetime, date
from itertools import product


from ..ui.ui_manager import DrSchemaI18NManagerUi
from ..utils import tools_dr
from ...lib import tools_qt, tools_qgis, tools_db, tools_log, tools_os, tools_gpkgdao
from ... import global_vars
from qgis.PyQt.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication, QFileDialog


class DrSchemaI18NManager:

    def __init__(self):
        self.plugin_dir = global_vars.plugin_dir
        self.schema_name = global_vars.schema_name
        self.project_type_selected = None

    def init_dialog(self):
        """ Constructor """

        self.dlg_qm = DrSchemaI18NManagerUi()  # Initialize the UI
        tools_dr.load_settings(self.dlg_qm)
        self._load_user_values()  # keep values
        self._set_connection()
        self.dev_commit = tools_dr.get_config_parser('system', 'force_commit', "user", "init", prefix=True)
        self._set_signals()  # Set all the signals to wait for response

        tools_dr.open_dialog(self.dlg_qm, dlg_name='admin_i18n_manager')


    def _set_signals(self):
        # Mysteriously without the partial the function check_connection is not called
        self.dlg_qm.btn_search.clicked.connect(self._update_i18n_database)
        self.dlg_qm.btn_close.clicked.connect(partial(tools_dr.close_dialog, self.dlg_qm))
        self.dlg_qm.btn_close.clicked.connect(partial(self._close_db_i18n))
        self.dlg_qm.btn_close.clicked.connect(partial(self._close_db_org))
        self.dlg_qm.btn_close.clicked.connect(partial(self._save_user_values))
        self.dlg_qm.rejected.connect(self._save_user_values)
        self.dlg_qm.rejected.connect(self._close_db_org)
        self.dlg_qm.rejected.connect(self._close_db_i18n)

    def _load_user_values(self):
        """
        Load last selected user values
            :return: Dictionary with values
        """
        py_msg = tools_dr.get_config_parser('i18n_manager', 'qm_py_msg', "user", "session", False)
        py_dialogs = tools_dr.get_config_parser('i18n_manager', 'qm_py_dialogs', "user", "session", False)
        db_msg = tools_dr.get_config_parser('i18n_manager', 'qm_db_msg', "user", "session", False)
        su_tbl = tools_dr.get_config_parser('i18n_manager', 'qm_su_tbl', "user", "session", False)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_for_su_tables, su_tbl)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_py_messages, py_msg)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_py_dialogs, py_dialogs)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_db_dialogs, db_msg)

    def _set_connection(self):
        """ Set connection to database """

        self.dlg_qm.lbl_info.clear()
        self._close_db_org()
        # Connection with origin db
        path_i18n =  f"{self.plugin_dir}{os.sep}core{os.sep}i18n{os.sep}drain_i18n.gpkg"
        path_sample =  f"{self.plugin_dir}{os.sep}core{os.sep}i18n{os.sep}drain_sample.gpkg"
        status_i18n = self._init_db_i18n(path_i18n)
        status_org = self._init_db_org(path_sample)

        # Send messages
        if not status_i18n:
            self.dlg_qm.btn_search.setEnabled(False)
            self.dlg_qm.lbl_info.clear()
            msg = "Error connecting to i18n database"
            tools_qt.show_info_box(msg)
            QApplication.processEvents()
            return
        else:
            self.dlg_qm.btn_search.setEnabled(True)
            self.dlg_qm.lbl_info.clear()
            msg = "Successful connection to the translations geopackage"
            tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', "Conexión correcta con el geopackage de traducciones")
            QApplication.processEvents()

        if not status_org:
            self.dlg_qm.btn_search.setEnabled(False)
            self.dlg_qm.lbl_info.clear()
            msg = "Error connecting to origin geopackage"
            tools_qt.show_info_box(msg)
            QApplication.processEvents()
            return

    def _init_db_i18n(self, gpkg_path):
        """Initializes database connection"""

        try:
            self.conn_i18n = sqlite3.connect(gpkg_path)
            self.conn_i18n.row_factory = sqlite3.Row 
            self.cursor_i18n = self.conn_i18n.cursor()
            return True
        except sqlite3.DatabaseError as e:
            self.last_error = e
            return False

    def _init_db_org(self, gpkg_path):
        """Initializes database connection"""

        try:
            self.conn_org = sqlite3.connect(gpkg_path)
            self.conn_org.row_factory = sqlite3.Row 
            self.cursor_org = self.conn_i18n.cursor()
            return True
        except sqlite3.DatabaseError as e:
            self.last_error = e
            return False

    def _close_db_org(self):
        """ Close database connection """

        try:
            if self.cursor_org:
                self.cursor_org.close()
            if self.conn_org:
                self.conn_org.close()
            del self.cursor_org
            del self.conn_org
        except Exception as e:
            self.last_error = e

    def _close_db_i18n(self):
        """ Close database connection """
        try:
            if self.cursor_i18n:
                self.cursor_i18n.close()
            if self.conn_i18n:
                self.conn_i18n.close()
            del self.cursor_i18n
            del self.conn_i18n
        except Exception as e:
            self.last_error = e

    def _save_user_values(self):
        """ Save selected user values """
        py_msg = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_messages)
        py_dialogs = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_dialogs)
        db_msg = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_db_dialogs)
        su_tbl = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_for_su_tables)
        tools_dr.set_config_parser('i18n_manager', 'qm_py_msg', f"{py_msg}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_manager', 'qm_py_dialogs', f"{py_dialogs}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_manager', 'qm_db_msg', f"{db_msg}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_manager', 'qm_su_tbl', f"{su_tbl}", "user", "session", prefix=False)

    def pass_schema_info(self, schema_info):
        self.project_type = schema_info['project_type']
        self.project_epsg = schema_info['project_epsg']
        self.project_version = schema_info['project_version']

    # endregion
    def _update_i18n_database(self):
        self.project_types = []

        self.py_messages = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_messages)
        self.py_dialogs = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_dialogs)
        
        if self.project_types:
            self._update_db_tables()

        if self.py_messages:
            self._update_py_messages()
        
        if self.py_dialogs:
            self._update_py_dialogs()


    # region Missing DB Dialogs
    def _update_db_tables(self):
        self.check_for_su_tables = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_for_su_tables)
        major_version = tools_qgis.get_major_version(plugin_dir=self.plugin_dir).replace(".", "")
        text_error = ''
        no_repeat_table = []

        for self.project_type in self.project_types:
            tables_i18n, sutables_i18n = self.tables_dic(self.project_type)
            self.schema_org = self.project_type
            print(self.project_type)
            if self.project_type != "am":
                self.schema_org = f"{self.project_type}{major_version}_trans"

            schema_exists = self._detect_schema(self.schema_org)
            if not schema_exists:
                msg = "The schema ({0}) does not exists"
                msg_params = (self.schema_org,)
                tools_qt.show_info_box(msg, msg_params=msg_params)
                return
            if self.check_for_su_tables:
                tables_i18n.extend(sutables_i18n)

            text_error += f'\n{self.project_type}:\n'
            self.dlg_qm.lbl_info.clear()
            for table_i18n in tables_i18n:
                if table_i18n not in no_repeat_table:
                    table_exists = self.detect_table_func(table_i18n)
                    correct_lang = self._verify_lang()
                    self._change_table_lyt(table_i18n.split(".")[1])
                    if not table_exists:
                        msg = "The table ({0}) does not exists"
                        msg_params = (self.schema_org,)
                        tools_qt.show_info_box(msg, msg_params=msg_params)
                        no_repeat_table.append(table_i18n)
                    elif correct_lang:
                        text_error += self._update_tables(table_i18n)

                        #check for all primary keys reapeted, but project_types
                        text_error += self._update_project_type(table_i18n)
                        self._vacuum_commit(table_i18n, self.conn_i18n, self.cursor_i18n)
                    else:
                        msg = "Incorrect languages, make sure to have the giswater project in english"
                        tools_qt.show_info_box(msg)
                        break                   

                

        self.dlg_qm.lbl_info.clear()
        tools_qt.show_info_box(text_error)


    def _update_tables(self, table_i18n):
        tables_org = self._find_table_org(table_i18n)
        
        query = ""
        for table_org in tables_org:
            if "json" in table_i18n:
                query += self._json_update(table_i18n, table_org)
            elif "dbconfig_form_fields_feat" in table_i18n:
                query += self._dbconfig_form_fields_feat_update(table_i18n)
            else:
                query += self._update_any_table(table_i18n, table_org)

        if query == '':
            return f'{table_i18n.split(".")[1]}: 1- No update needed. '
        else:
            try:
                self.cursor_i18n.execute(query)
                self.conn_i18n.commit()
                return f'{table_i18n.split(".")[1]}: 1- Succesfully updated table. '
            except Exception as e:
                self.conn_i18n.rollback()
                return f"An error occured while translating {table_i18n}: {e}\n"
    

    def _update_any_table(self, table_i18n, table_org):
        columns_i18n, columns_org, names = self._get_rows_to_compare(table_i18n, table_org)

        columns = ", ".join(columns_i18n)
        query = f"SELECT {columns} FROM {table_i18n};"
        rows_i18n = self._get_rows(query, self.cursor_i18n)
        print(query)

        columns = ", ".join(columns_org)
        query = f"SELECT {columns} FROM {self.schema_org}.{table_org};"
        rows_org = self._get_rows(query, self.cursor_org)
        print(query)

        query = ""
        if rows_i18n:
            for row_i18n in rows_i18n:
                for column_i18n in columns_i18n:
                    if "CAST(" in column_i18n:
                        column_i18n = column_i18n[5:].split(" ")[0]
                    if row_i18n[column_i18n] is None:
                        row_i18n[column_i18n] = ''

        for row_org in rows_org:
            for column_org in columns_org:
                if row_org[column_org] is None:
                    row_org[column_org] = ''

            row_org_com = row_org
            no_project_type = ["dbconfig_form_fields", "dbconfig_csv", "dbconfig_form_tabs", "dbconfig_report", "dbconfig_toolbox", 
                               "edit_typevalue", "plan_typevalue", "om_typevalue", "dbtable", "su_feature", "su_basic_tables"]
            if table_i18n in no_project_type:
               row_org_com.append(self.project_type) 

            # Check if the row from org doesn't exist in i18n, and construct the query
            if rows_i18n is None or row_org_com not in rows_i18n:
                # Safely handle NULL values and avoid SQL injection
                texts = []
                for name in names:
                    value = f"'{row_org[name].replace("'", "''")}'" if row_org[name] not in [None, ''] else 'NULL'
                    texts.append(value)

                if 'dbconfig_form_fields' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (context, source_code, project_type, source, formname, formtype, lb_en_us, tt_en_us) 
                                    VALUES ('{table_org}', 'giswater', '{self.project_type}', '{row_org['columnname']}', '{row_org['formname']}', '{row_org['formtype']}',
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (context, source_code, project_type, source, formname, formtype) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, tt_en_us = {texts[1]};\n"""
                    
                elif 'dbparam_user' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (context, source_code, source, formname, project_type, lb_en_us, tt_en_us) 
                                    VALUES ('{table_org}', 'giswater', '{row_org['id']}', '{row_org['formname']}', '{row_org['project_type']}',
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (context, source_code, project_type, source, formname) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, tt_en_us = {texts[1]};\n"""
                    
                elif 'dbconfig_param_system' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (context, source_code, project_type, source, lb_en_us, tt_en_us) 
                                    VALUES ('{table_org}', 'giswater', '{row_org['project_type']}', '{row_org['parameter']}',
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (context, source_code, project_type, source) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, tt_en_us = {texts[1]};\n"""
                    
                elif 'dbconfig_typevalue' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (context, source_code, project_type, source, formname, formtype, tt_en_us) 
                                    VALUES ('{table_org}', 'giswater', '{self.project_type}', '{row_org['id']}', '{row_org['typevalue']}', 
                                    'form_feature', {texts[0]}) 
                                    ON CONFLICT (context, source_code, project_type, source, formname, formtype) 
                                    DO UPDATE SET tt_en_us = {texts[0]};\n"""
                
                elif 'dbmessage' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (context, source_code, project_type, log_level, source, ms_en_us, ht_en_us) 
                                    VALUES ('{table_org}', 'giswater', '{row_org['project_type']}', '{row_org['log_level']}','{row_org['id']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, log_level, source)  
                                    DO UPDATE SET ms_en_us = {texts[0]}, ht_en_us = {texts[1]};\n"""
                    
                elif 'dbfprocess' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, ex_en_us, in_en_us, na_en_us) 
                                    VALUES ('giswater', '{table_org}', '{row_org['project_type']}', '{row_org['fid']}', 
                                    {texts[0]}, {texts[1]}, {texts[2]}) 
                                    ON CONFLICT (source_code, project_type, context, source) 
                                    DO UPDATE SET ex_en_us = {texts[0]}, in_en_us = {texts[1]}, na_en_us = {texts[2]};\n"""

                elif 'dbconfig_csv' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, al_en_us, ds_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['fid']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, source) 
                                    DO UPDATE SET al_en_us = {texts[0]}, ds_en_us = {texts[1]};\n"""
                    
                elif 'dbconfig_form_tabs' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, formname, source, lb_en_us, tt_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['formname']}', '{row_org['tabname']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, formname, source) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, tt_en_us = {texts[1]};\n"""
                    
                   
                elif 'dbconfig_report' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, al_en_us, ds_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['id']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, source) 
                                    DO UPDATE SET al_en_us = {texts[0]}, ds_en_us = {texts[1]};\n"""
                    
                elif 'dbconfig_toolbox' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, al_en_us, ob_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['id']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, source) 
                                    DO UPDATE SET al_en_us = {texts[0]}, ob_en_us = {texts[1]};\n"""
                    
                elif 'dbfunction' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, ds_en_us) 
                                    VALUES ('giswater', '{table_org}', '{row_org['project_type']}', '{row_org['id']}', 
                                    {texts[0]}) 
                                    ON CONFLICT (source_code, project_type, context, source) 
                                    DO UPDATE SET ds_en_us = {texts[0]};\n"""

                elif 'dbtypevalue' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, typevalue, source, vl_en_us, ds_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['typevalue']}', '{row_org['id']}', 
                                    {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, project_type, context, typevalue, source) 
                                    DO UPDATE SET vl_en_us = {texts[0]}, ds_en_us = {texts[1]};\n"""
                    
                elif 'dbconfig_form_tableview' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, location_type, columnname, source, al_en_us) 
                                    VALUES ('giswater', '{table_org}', '{row_org['project_type']}', '{row_org['location_type']}', '{row_org['columnname']}', '{row_org['objectname']}', 
                                    {texts[0]}) 
                                    ON CONFLICT (source_code, context, project_type, location_type, columnname, source) 
                                    DO UPDATE SET al_en_us = {texts[0]};\n"""

                elif 'dbtable' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, ds_en_us, al_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org['id']}', {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, context, project_type, source) 
                                    DO UPDATE SET ds_en_us = {texts[0]}, al_en_us = {texts[1]};\n"""    
                
                elif 'su_basic_tables' in table_i18n:
                    source = row_org["id"]
                    if table_org == "value_state_type" or self.project_type == "am":
                        texts.append('null')
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, source, na_en_us, ob_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{source}', {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, context, project_type, source) 
                                    DO UPDATE SET na_en_us = {texts[0]}, ob_en_us = {texts[1]};\n"""
                    
                elif 'su_feature' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, feature_class, feature_type, lb_en_us, ds_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org["feature_class"]}', '{row_org["feature_type"]}', {texts[0]}, {texts[1]}) 
                                    ON CONFLICT (source_code, context, project_type, feature_class, feature_type, lb_en_us) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, ds_en_us = {texts[1]};\n"""  
                    
                elif 'dbconfig_engine' in table_i18n:
                    query_row = f"""INSERT INTO {table_i18n} (source_code, context, project_type, parameter, method, lb_en_us, ds_en_us, pl_en_us) 
                                    VALUES ('giswater', '{table_org}', '{self.project_type}', '{row_org["parameter"]}', '{row_org["method"]}', {texts[0]}, {texts[1]}, {texts[2]}) 
                                    ON CONFLICT (source_code, context, project_type, parameter, method) 
                                    DO UPDATE SET lb_en_us = {texts[0]}, ds_en_us = {texts[1]}, pl_en_us = {texts[2]};\n""" 
                    

                query += query_row
        return query              

    def _get_rows_to_compare(self, table_i18n, table_org):
        if 'dbconfig_form_fields' in table_i18n:
            columns_i18n = ["formname", "formtype", "source", "lb_en_us", "tt_en_us", "project_type"]
            columns_org = ["formname", "formtype", "columnname", "label", "tooltip"]
            names = ["label", "tooltip"]

        elif 'dbparam_user' in table_i18n:
            columns_i18n = ["project_type", "source", "formname", "lb_en_us", "tt_en_us"]
            columns_org = ["project_type", "id", "formname", "label", "descript"]
            names = ["label", "descript"]

        elif 'dbconfig_param_system' in table_i18n:
            columns_i18n = ["project_type", "source", "lb_en_us", "tt_en_us"]
            columns_org = ["project_type", "parameter", "label", "descript"]
            names = ["label", "descript"]

        elif 'dbconfig_typevalue' in table_i18n:
            columns_i18n = ["formname", "source", "tt_en_us"]
            columns_org = ["typevalue", "id", "idval"]
            names = ["idval"]

        elif 'dbmessage' in table_i18n:
            columns_i18n = ["project_type", "CAST(source AS INTEGER) AS source", "CAST(log_level AS INTEGER) AS log_level", "ms_en_us", "ht_en_us"]
            columns_org = ["project_type", "id", "log_level", "error_message", "hint_message"]
            names = ["error_message", "hint_message"]

        elif 'dbfprocess' in table_i18n:
            columns_i18n = ["project_type", "CAST(source AS INTEGER) AS source", "ex_en_us", "in_en_us", "na_en_us"]
            columns_org = ["project_type", "fid", "except_msg", "info_msg", "fprocess_name"]
            names = ["except_msg", "info_msg", "fprocess_name"]

        elif 'dbconfig_csv' in table_i18n:
            columns_i18n = ["project_type", "source", "al_en_us", "ds_en_us"]
            columns_org = ["fid", "alias", "descript"]
            names = ["alias", "descript"]

        elif 'dbconfig_form_tabs' in table_i18n:
            columns_i18n = ["project_type", "formname", "source", "lb_en_us", "tt_en_us"]
            columns_org = ["formname", "tabname", "label", "tooltip"]
            names = ["label", "tooltip"]

        elif 'dbconfig_report' in table_i18n:
            columns_i18n = ["project_type", "source", "al_en_us", "ds_en_us"]
            columns_org = ["id", "alias", "descript"]
            names = ["alias", "descript"]

        elif 'dbconfig_toolbox' in table_i18n:
            columns_i18n = ["project_type", "source", "al_en_us", "ob_en_us"]
            columns_org = ["id", "alias", "observ"]
            names = ["alias", "observ"]

        elif 'dbfunction' in table_i18n:
            columns_i18n = ["project_type", "source", "ds_en_us"]
            columns_org = ["project_type", "id", "descript"]
            names = ["descript"]

        elif 'dbtypevalue' in table_i18n:
            columns_i18n = ["project_type", "typevalue", "source", "vl_en_us"]
            columns_org = ["typevalue", "id", "idval", "descript"]
            names = ["idval", "descript"]

        elif 'dbconfig_form_tableview' in table_i18n:
            columns_i18n = ["project_type", "location_type", "source", "al_en_us"]
            columns_org = ["project_type", "location_type", "objectname", "columnname", "alias"]
            names = ["columnname"]

        elif 'dbtable' in table_i18n:
            columns_i18n = ["project_type", "source", "ds_en_us", "al_en_us"]
            columns_org = ["id", "descript", "alias"]
            names = ["descript", "alias"]

        elif 'su_basic_tables' in table_i18n:
            columns_i18n = ["project_type", "source", "na_en_us", "ob_en_us"]
            columns_org = ["id", "name"]
            names = ["name"]
            if table_org == "value_state" and self.project_type in ["ud", "ws"]:
                columns_org = ["id", "name", "observ"]
                names = ["name", "observ"]
            elif table_org == "doc_type":
                columns_org = ["id", "comment"]
                names = ["id", "comment"]
            elif self.project_type == "am":
                columns_org = ["id", "idval"]
                names = ["idval"]

        elif 'su_feature' in table_i18n:
            columns_i18n = ["project_type", "feature_class", "feature_type", "lb_en_us", "ds_en_us"]
            columns_org = ["feature_class", "feature_type", "id", "descript"]
            names = ["id", "descript"]

        elif 'dbconfig_engine' in table_i18n:
            columns_i18n = ["project_type", "parameter", "method", "lb_en_us", "ds_en_us", "pl_en_us"]
            columns_org = ["parameter", "method", "label", "descript", "placeholder"]
            names = ["label", "descript", "placeholder"]

        return columns_i18n, columns_org, names
    
    # endregion
    # region Json
    
    def _json_update(self, table_i18n, table_org):
        column = ""
        if table_org == 'config_report':
            column = "filterparam"
        elif table_org == 'config_toolbox':
            column = 'inputparams'
        elif table_org == 'config_form_fields':
            column = 'widgetcontrols'
        query = f"SELECT * FROM {self.schema_org}.{table_org}"
        rows = self._get_rows(query, self.cursor_org)
        query = ""
        for row in rows:
            
            safe_row_column = str(row[column]).replace("'", "''")
            if row[column] not in [None, "", "None"]:
                datas = self.extract_and_update_strings(row[column])    

                for i, data in enumerate(datas):
                    
                    for key, text in data.items():
                        # Handle string or list of strings
                        if isinstance(text, list):
                            text = ", ".join(text)  # or use another delimiter
                        elif not isinstance(text, str):
                            continue  # Skip if it's not a string or list

                        safe_text = text.replace("'", "''")
                        if "config_form_fields" in table_i18n:
                            print(row)
                            print(f"data: {data}")
                            query_row = f""" INSERT INTO {table_i18n} (source_code, project_type, context, formname, formtype, source, hint, text, lb_en_us)
                            VALUES ('giswater', '{self.project_type}', '{table_org}', '{row['formname']}', '{row['formtype']}', '{row['columnname']}', '{key}_{i}', '{safe_row_column}', '{safe_text}')
                            ON CONFLICT (source_code, project_type, context, formname, formtype, source, hint, text)
                            DO UPDATE SET lb_en_us = '{safe_text}'; """ 
                            
                            # Execute or collect query_row
                            query += query_row
                        else:
                            query_row = f""" INSERT INTO {table_i18n} (source_code, project_type, context, hint, text, source, lb_en_us)
                            VALUES ('giswater', '{self.project_type}', '{table_org}', '{key}_{i}', '{safe_row_column}', '{row['id']}', '{safe_text}')
                            ON CONFLICT (source_code, project_type, context, hint, text, source)
                            DO UPDATE SET lb_en_us = '{safe_text}'; """ 

                            # Execute or collect query_row
                            query += query_row
        return query
    

    # endregion
    # region Config_form_fields_feat
    
    def _dbconfig_form_fields_feat_update(self, table_i18n):
        schema = table_i18n.split('.')[0]
        table_org = f"{schema}.dbconfig_form_fields"
        query = f"""
            INSERT INTO {table_i18n}
            select distinct on (feature_type, project_type, source) *
            FROM (
                SELECT 'ARC' AS feature_type, * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_arc%' OR formname = 'v_edit_arc')
                
                UNION
                
                SELECT 'NODE', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_node%' OR formname = 'v_edit_node')
                
                UNION
                
                SELECT 'CONNEC', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_connec%' OR formname = 'v_edit_connec')
                
                UNION
                
                SELECT 'GULLY', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_gully%' OR formname = 'v_edit_gully')
                
                UNION
                
                SELECT 'ELEMENT', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_element%' OR formname = 'v_edit_element')
                
                UNION
                
                SELECT 'LINK', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_link%' OR formname = 'v_edit_link')
                
                UNION
                
                SELECT 'FLWREG', * 
                FROM {table_org} 
                WHERE formtype = 'form_feature' AND (formname LIKE 've_flwreg%' OR formname = 'v_edit_flwreg')
            ) AS unioned
            ON CONFLICT (feature_type, source_code, project_type, context, formname, formtype, source)
            DO NOTHING;

            delete from {table_org}  where formtype = 'form_feature' and (formname like 've_arc%' or formname in ('v_edit_arc'));

            delete from {table_org} where formtype = 'form_feature' and (formname like 've_node%' or formname in ('v_edit_node'));

            delete from {table_org} where formtype = 'form_feature' and (formname like 've_connec%' or formname in ('v_edit_connec'));

            delete from {table_org} where formtype = 'form_feature' and (formname like 've_gully%' or formname in ('v_edit_gully'));

            delete from {table_org} where formtype = 'form_feature' and (formname like 've_element%' or formname in ('v_edit_element'));

            delete from {table_org} where formtype = 'form_feature'and (formname like 've_link%' or formname in ('v_edit_link'));

            delete from {table_org} where formtype = 'form_feature'  and (formname like 've_flwreg%' or formname in ('v_edit_flwreg'));
        """
        return query
            
    #endregion
    # region Rewrite Project_type
    def _update_project_type(self, table):
        """Function to rewrite the repeated rows with different project_type to only one with project_type = 'utils'"""

        # Step 1: Determine column names
        try:
            self._detect_column_names(table)
        except Exception as e:
            return f"Error deleting rows: {e}"

        # Step 2: Get the duplicated rows
        query = self._get_duplicates_rows(table)
        try:
            self.cursor_i18n.execute(query)
            initial_rows = self.cursor_i18n.fetchall()
        except Exception as e:
            return f"Error deleting rows: {e}"

        # Step 3: Create the rows with the correct project_type
        final_rows = []
        primary_rows = []
        final_rows_no_utils = []
        for row in initial_rows:
            primary_row = [row[primary_key] for primary_key in self.primary_keys if primary_key != 'project_type']
            if row['project_type'] in ['ws', 'ud', 'utils']:
                if primary_row not in primary_rows:
                    final_rows.append(row)
                    primary_rows.append(primary_row)
            elif row['project_type'] not in [None, 'None', '']:
                final_rows_no_utils.append(row)

        # Step 4: Delete the initial rows that are duplicates (those that will be replaced by final_rows)
        delete_query = self._delete_duplicates_rows(table)
        try:
            self.cursor_i18n.execute(delete_query)
            self.conn_i18n.commit()  # Commit the deletion
        except Exception as e:
            self.conn_i18n.rollback()  # Rollback in case of error
            return f"Error deleting rows: {e}"

        # Step 5: Insert the unique final rows back into the table
        final_rows_tot = final_rows + final_rows_no_utils if final_rows_no_utils else final_rows
        insert_query = self._add_duplicates_rows(table, final_rows_tot, final_rows)
        if insert_query == "":
            return "No rows to unify"
        try:
            self.cursor_i18n.execute(insert_query)
        except Exception as e:
            self.conn_i18n.rollback()  # Rollback in case of error
            return f"Error inserting rows: {e}"

        self.conn_i18n.commit()  # Commit the insertions
        return f"2- Rows updated successfully.\n"

    def _get_duplicates_rows(self, table):
        """Create query to determine the duplicated rows"""

        query = f"""WITH duplicates AS (
                SELECT """
        query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        query += f""", COUNT(*) AS duplicate_count
                FROM {table}
                GROUP BY """
        query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        query += f"""\nHAVING COUNT(*) > 1
            )
            SELECT t.*, d.duplicate_count
            FROM {table} t
            JOIN duplicates d
            ON 
        """
        query += "AND ".join([f"""t.{primary_key} = d.{primary_key} """ for primary_key in self.primary_keys if primary_key != 'project_type'])
        query += """ORDER BY duplicate_count DESC, (project_type = 'utils') DESC, project_type;"""
        return query

    def _delete_duplicates_rows(self, table):
        """Create query to delete the duplicated rows"""

        delete_query = """
            WITH duplicates AS (
                SELECT """
        delete_query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        delete_query += f""", COUNT(*) AS duplicate_count
                FROM {table}
                GROUP BY """
        delete_query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        delete_query += f"""\nHAVING COUNT(*) > 1
            )
            DELETE FROM {table} WHERE ("""
        delete_query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        delete_query += """) IN (SELECT """
        delete_query += ", ".join([primary_key for primary_key in self.primary_keys if primary_key != 'project_type'])
        delete_query += """  FROM duplicates);"""
        return delete_query

    def _add_duplicates_rows(self, table, final_rows_tot, final_rows):
        """Create query to add the correct rows to the table"""

        insert_query = ""
        for k, row in enumerate(final_rows_tot):
            row_keys = list(row.keys())[:-1]
            if k < len(final_rows):
                row_keys.remove('project_type')
            insert_query += f"INSERT INTO {table} ("

            # Handle columns (keys)
            insert_query += ", ".join([row_key for row_key in row_keys])
            insert_query += ", project_type) VALUES ("

            values = []
            for row_key in row_keys:
                value = row[row_key]
                if isinstance(value, str):
                    value = f"""'{value.replace("'", "''")}'"""  # Escape single quotes in strings
                elif isinstance(value, (datetime, date)):  # Handle timestamps properly
                    value = f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
                elif value in [None, 'None', '']:
                    value = "Null"
                else:
                    value = str(value)  # Convert other types directly
                values.append(value)
            # Add processed values to query
            insert_query += ", ".join(values)
            insert_query += ", 'utils');\n" if k < len(final_rows) else ");\n"
        return insert_query

    # endregion

    #region Python
    def _update_py_dialogs(self):
        # Make the user know what is being done
        self.project_type = "python"
        self._change_table_lyt("pydialog")

        # Find the files to search for messages
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        files = self._find_files(path, ".ui")
        
        # Determine the key and find the messages
        messages = []
        primary_keys_final = []
        keys = ["<string>", "<widget", 'name=']
        for file in files:
            coincidencias = self._search_lines(file, keys[0])
            if coincidencias:
                for num_line, content in coincidencias:
                    dialog_name, toolbar_name, source = self._search_dialog_info(file, keys[1], keys[2], num_line)
                    pattern = rf'>(.*?)<'
                    match = re.search(pattern, content)
                    if match:
                        messages.append((match.group(1), dialog_name, toolbar_name, source))
                        primary_keys_final.append((source, dialog_name, toolbar_name))

        # Add btn_help to messages
        messages.append(("Help", "common", "common", "btn_help"))
        primary_keys_final.append(("btn_help", "common", "common"))

        # Determine existing primary keys from the database
        primary_keys_org = []
        try:
            self.cursor_i18n.execute("SELECT source, dialog_name, toolbar_name FROM pydialog")
            rows = self.cursor_i18n.fetchall()
            for row in rows:
                primary_keys_org.append((row["source"], row["dialog_name"], row["toolbar_name"]))
        except sqlite3.Error as e:
            print(f"Error fetching existing primary keys: {e}")

        # Delete removed widgets
        primary_keys_org_set = set(primary_keys_org)
        primary_keys_final_set = set(primary_keys_final)
        deleted_keys = primary_keys_org_set - primary_keys_final_set

        if deleted_keys:
            for source, dialog_name, toolbar_name in deleted_keys:
                # Get proper messages
                dialog_name = dialog_name.replace("'", "''")
                toolbar_name = toolbar_name.replace("'", "''")
                source = source.replace("'", "''")
                # Query
                query = "DELETE FROM pydialog WHERE source = ? AND dialog_name = ? AND toolbar_name = ?"
                try:
                    self.cursor_i18n.execute(query, (source, dialog_name, toolbar_name))
                except sqlite3.Error as e:
                    print(f"Error deleting row: {e} - Query: {query} - Data: {(source, dialog_name, toolbar_name)}")

        # Update the table
        text_error = ""
        query = ""
        for message, dialog_name, toolbar_name, source in messages:

            # Get proper messages
            message = message.replace("'", "''")
            dialog_name = dialog_name.replace("'", "''")
            toolbar_name = toolbar_name.replace("'", "''")
            source = source.replace("'", "''")

            # Small change to confirm correct values
            if source.startswith('dlg_'):
                actual_source = f"dlg_{dialog_name}"
            else:
                actual_source = source

            # Write query
            query = (
                f"""INSERT INTO pydialog (source, dialog_name, toolbar_name, lb_en_us) VALUES ("""
                f"""'{actual_source}', '{dialog_name}', '{toolbar_name}', '{message}') """
                f"""ON CONFLICT(source_code, source, dialog_name, toolbar_name) DO UPDATE SET """
                f"""lb_en_us = '{message}';\n"""
            )

            # Run query
            try:
                self.cursor_i18n.execute(query)
            except Exception as e:
                text_error += f"Error updating: {message}.\n"
                print(query)
                print(e)
        
        if len(text_error) > 1:
            tools_qt.show_info_box(text_error)
        else:
            msg = "All dialogs updated correctly"
            tools_qt.show_info_box(msg)

        self.conn_i18n.commit()
    
    def _update_py_messages(self):
        self.project_type = "python"
        self._change_table_lyt("pymessage")
        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        print(path)
        files = self._find_files(path, ".py")
        
        messages = []
        fields = ['message', 'msg', 'title']
        patterns = ['=', ' =', '= ', ' = ']
        quotes = ['"', "'", '(']

        # Generate all combinations
        keys = [f"{field}{pattern}{quote}" for field, pattern, quote in product(fields, patterns, quotes)]

        for file in files:
            for key in keys:
                coincidencias = self._search_lines(file, key)
                if coincidencias:
                    for num_line, content in coincidencias:
                        if "(" in key:
                            key = 'msg = "'
                        match = re.search(rf'{re.escape(key)}(.*?){key[-1]}', content)
                        if match:
                            messages.append(match.group(1))

        # Determine existing primary keys from the database
        primary_keys_org = []
        try:
            self.cursor_i18n.execute("SELECT source FROM pymessage")
            rows = self.cursor_i18n.fetchall()
            for row in rows:
                primary_keys_org.append(row["source"])
        except sqlite3.Error as e:
            print(f"Error fetching existing primary keys: {e}")

        # Delete removed widgets
        primary_keys_org_set = set(primary_keys_org)
        primary_keys_final_set = set(messages)
        deleted_messages = primary_keys_org_set - primary_keys_final_set

        if deleted_messages:
            for source in deleted_messages:
                source = source.replace("'", "''")
                query = f"DELETE FROM pymessage WHERE source = '{source}'"
                try:
                    self.cursor_i18n.execute(query)
                except sqlite3.Error as e:
                    print(f"Error deleting row: {e} - Query: {query}")

        # Insert new messages
        msg = ""
        msg_params = None
        new_messages = primary_keys_final_set - primary_keys_org_set
        if new_messages:
            for message in new_messages:
                message = message.replace("'", "''")
                query = f"""INSERT OR IGNORE INTO pymessage (source, ms_en_us) VALUES ('{message}', '{message}') """

                try:
                    self.cursor_i18n.execute(query)
                except Exception as e:
                    msg = "Error updating: {0}.\n"
                    msg_params = (message,)
                    tools_qt.show_exception_message(msg, msg_params=msg_params)

        if len(msg) > 1:
            tools_qt.show_info_box(msg)
        else:
            msg = "All messages updated correctly"
            tools_qt.show_info_box(msg)

        self.conn_i18n.commit()

    # endregion
    # region Python functions

    def _find_files(self, path, file_type):
        py_files = []

        for folder, subfolder, files in os.walk(path):
            if 'packages' in folder.split(os.sep):
                continue
            for file in files:
                if file.endswith(file_type):
                    file_path = os.path.join(folder, file)
                    py_files.append(file_path)

        return py_files

    def _search_lines(self, file, key):
        found_lines = []
        try:
            with open(file, "r", encoding="utf-8") as f:
                in_multiline = False
                full_text = ""

                for num_line, raw_line in enumerate(f):
                    line = raw_line.strip()
                    
                    if in_multiline:
                        full_text += line
                        if line.endswith(")"):
                            found_lines = self._msg_multines_end(found_lines, full_text, num_line)
                            in_multiline = False
                        continue

                    if line.startswith(key):
                        if "(" not in key:
                            found_lines.append((num_line, line))
                        else:
                            if line.endswith(")"):
                                found_lines = self._msg_multines_end(found_lines, full_text, num_line)
                            else:
                                # Begin multi-line
                                in_multiline = True
                                full_text = line

        except FileNotFoundError:
            print(f"Error: File not found: {file}")
        except Exception as e:
            print(f"Error reading file {file}: {e}")
        return found_lines
    

    def _msg_multines_end(self, found_lines, full_text, num_line):
        matches = re.findall(r"(['\"])(.*?)\1", full_text)
        if matches:
            final_text = 'msg = "' + ''.join(m[1] for m in matches) + '"'
            found_lines.append((num_line, final_text))
        else:
            print(f"Error: Could not extract message from line: {full_text}")
            found_lines.append((num_line, full_text.strip()))
        return found_lines
    
    
    def _search_dialog_info(self, file, key_row, key_text, num_line):
        with open(file, "r", encoding="utf-8") as f:
            # Extract folder and file name (assuming the file path is used)
            toolbar_name = os.path.basename(os.path.dirname(file))
            dialog_name = os.path.basename(file)
            dialog_name = dialog_name.split(".")[0]

            # Read all lines into a list
            lines = f.readlines()
            
            # Search for the key in the file, starting from the given line
            while num_line >= 0 and key_row not in lines[num_line]:
                num_line -= 1  
            
            if num_line < 0:
                return None  

            # Now extract the value between quotes using regex
            pattern = rf'{re.escape(key_text)}"(.*?)"'
            match = re.search(pattern, lines[num_line])

            if match:
                source = match.group(1)
            else:
                source = ""
            
            return dialog_name, toolbar_name, source


    def _extra_messages_to_find():
        # writen to be detected by the automatical finder of pymessages
        message = "File"

    #endregion
    # region Global funcitons
    
    def _detect_schema(self, schema_name):
        query = "SELECT schema_name FROM information_schema.schemata;"
        self.cursor_org.execute(query)
        schemas = self.cursor_org.fetchall()
        
        existing_schema = False
        for schema in schemas:
            # schema is a tuple like ('information_schema',) so you need to access the first element
            if schema[0] == schema_name:
                existing_schema = True
                break  # Exit the loop early once we find the schema
        
        return existing_schema


    def detect_table_func(self, table):
        self.cursor_i18n.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{table.split('.')[0]}' AND table_name = '{table.split('.')[1]}';")
        result = self.cursor_i18n.fetchone()
        existing_table = result[0] > 0  # Check if count is greater than 0
        return existing_table

    def _find_table_org(self, table_i18n):
        # Create the query using table_i18n
        query = f'SELECT * FROM {table_i18n}'
        rows = self._get_rows(query, self.cursor_i18n)

        table_name = table_i18n.split(".")[1]
        tables_org = []
        # Process the table name based on its prefix
        if "dbtypevalue" in table_i18n:
            tables_org = ["edit_typevalue","plan_typevalue","om_typevalue"]
        elif "dbjson" in table_i18n:
            tables_org = ["config_report", "config_toolbox"]
        elif "dbconfig_form_fields_json" in table_i18n:
            tables_org = ["config_form_fields"]
        elif "dbconfig_engine" in table_i18n:
            tables_org = ["config_engine", "config_engine_def"]
        elif table_name.startswith("dbconfig"):
            tables_org = [table_name[2:]] # Get everything after the first two characters
        elif table_name.startswith("su_"):
            if self.project_type == "am":
                tables_org = ["value_result_type", "value_status"]
            if self.project_type in ["ws", "ud"]:
                if table_name == "su_feature":
                    tables_org = ["cat_feature"]
                else:
                    tables_org = ["value_state", "value_state_type"]
        else:
            tables_org = [f"sys_{table_name[2:]}"]  # Prepend "sys_" and get everything after the first two characters
        
        # If rows exist, retrieve 'context' from the first row
        seen_contexts = set(tables_org)
        for row in rows:
            context = row.get('context')
            row_project_type = row.get("project_type")
            if context not in seen_contexts and row_project_type == self.project_type:
                tables_org.append(context)
                seen_contexts.add(context) # Use .get() to avoid KeyError if 'context' doesn't exist
        if tables_org is None:
            return None  # Or some fallback behavior
        
        return tables_org

    
    def _get_rows(self, sql, cursor):
        """ Get multiple rows from selected query """
        rows = None
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            return rows

    def _vacuum_commit(self, table, conn, cursor):
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(0)
        cursor.execute(f"VACUUM FULL {table};")
        cursor.execute(f"ANALYZE {table};")
        conn.set_isolation_level(old_isolation_level)

    def _change_table_lyt(self, table):
        # Update the part the of the program in process
        self.dlg_qm.lbl_info.clear()
        msg = "From {0}, updating {1}..."
        msg_params = (self.project_type, table)
        tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', msg, msg_params=msg_params)
        QApplication.processEvents()

    def _detect_column_names(self, table):
        query = f"""
            SELECT a.attname AS column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass
            AND i.indisprimary;
            """

        self.cursor_i18n.execute(query)
        results = self.cursor_i18n.fetchall()
        self.primary_keys = [row['column_name'] for row in results]

    def extract_and_update_strings(self, data):
        """Recursively extract and return list of dictionaries with translatable keys."""
        translatable_keys = ['label', 'tooltip', 'placeholder', 'text', 'comboNames']
        results = []

        def recurse(item):
            if isinstance(item, dict):
                entry = {}
                for key, value in item.items():
                    if key in translatable_keys:
                        if key == 'comboNames' and isinstance(value, list):
                            entry[key] = value
                        elif isinstance(value, str):
                            entry[key] = value
                    # Recurse into children
                    recurse(value)
                if entry:
                    results.append(entry)
            elif isinstance(item, list):
                for sub in item:
                    recurse(sub)

        recurse(data)
        return results
    

    def _verify_lang(self):
        if self.project_type in ["ws", "ud"]:
            query = f"SELECT language from {self.schema_org}.sys_version"
            self.cursor_org.execute(query)
            language_org = self.cursor_org.fetchone()[0]
            if language_org != 'en_US':
                return False
        return True
    
    def tables_dic(self, schema_type):
        dbtables_dic = {
            "ws": {
                "dbtables": [ "dbparam_user", "dbconfig_param_system", "dbconfig_form_fields", "dbconfig_typevalue", 
                    "dbfprocess", "dbmessage", "dbconfig_csv", "dbconfig_form_tabs", "dbconfig_report", 
                    "dbconfig_toolbox", "dbfunction", "dbtypevalue", "dbconfig_form_fields_feat", 
                    "dbconfig_form_tableview", "dbtable", "dbjson", "dbconfig_form_fields_json"
                 ],
                 "sutables": ["su_basic_tables", "su_feature"]
            },
            "ud": {
                "dbtables": [ "dbparam_user", "dbconfig_param_system", "dbconfig_form_fields", "dbconfig_typevalue", 
                    "dbfprocess", "dbmessage", "dbconfig_csv", "dbconfig_form_tabs", "dbconfig_report", 
                    "dbconfig_toolbox", "dbfunction", "dbtypevalue", "dbconfig_form_fields_feat", 
                    "dbconfig_form_tableview", "dbtable", "dbjson", "dbconfig_form_fields_json"
                 ],
                 "sutables": ["su_basic_tables", "su_feature"]
            },
            "am": {
                "dbtables": ["dbconfig_engine", "dbconfig_form_tableview", "su_basic_tables"],
                "sutables": []
            },
            "cm": {
                "dbtables": [], #["dbtable", "dbconfig_form_fields", "dbconfig_form_tabs", "dbconfig_param_system", "sys_typevalue", "dbconfig_form_fields_json"]
                "sutables": []
            },
        }
        return dbtables_dic[schema_type]['dbtables'], dbtables_dic[schema_type]['sutables']

    # endregion

    # region Py messages
    def _extra_messages(self):
        message = "layoutorder not found. "
        message = "widgettype is wrongly configured. Needs to be in {0}"
        message = "widgetname not found. "
        message = "Key"
        message = "Key container"
        message = "Python file"
        message = "Python function"
        message = "File name"
        message = "Function name"
        message = "Line number"
        message = "Detail"
        message = "Context"
        message = "SQL"
        message = "Message error"
        message = "Process finished successfully"
        message = "Info"
        message = "Process finished with some errors"
        message = "Widgettype not found."
        message = "Widgetname not found."
        message = "Widgettype is wrongly configured. Needs to be in "
        message = "Layoutorder not found."
        message = "Python function"
        message = "has been deprecated. Use"
        message = "instead."
        message = "translation successful"
        message = "translation failed in table"
        message = "translation canceled"
        message = "Python translation successful"
        message = "Python translation failed"
        message = "Python translation canceled"
        message = "Database translation successful to"
        message = "Database translation failed."
        message = "Database translation canceled."
        message = "There have been errors translating:"
    # endregion