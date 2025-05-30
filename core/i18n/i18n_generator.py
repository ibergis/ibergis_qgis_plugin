"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import re
import subprocess
from functools import partial
import json
import ast
import shutil

import sqlite3

from ..ui.ui_manager import DrAdminTranslationUi
from ..utils import tools_dr
from ...lib import tools_qt, tools_qgis, tools_gpkgdao
from ... import global_vars

from PyQt5.QtWidgets import QApplication, QFileDialog

class DrI18NGenerator:

    def __init__(self):
        super().__init__()
        self.plugin_dir = global_vars.plugin_dir
        self.schema_name = global_vars.schema_name


    def init_dialog(self):
        """ Constructor """

        self.dlg_qm = DrAdminTranslationUi()
        tools_dr.load_settings(self.dlg_qm)

        self._load_user_values()

        self._check_connection()
        
        # Mysteriously without the partial the function check_connection is not called
        self.dlg_qm.btn_translate.clicked.connect(partial(self._check_translate_options))
        self.dlg_qm.btn_close.clicked.connect(partial(tools_dr.close_dialog, self.dlg_qm))
        self.dlg_qm.rejected.connect(self._save_user_values)
        self.dlg_qm.rejected.connect(self._close_db)
        self.dlg_qm.btn_search_file.clicked.connect(self.open_file_dialog)
        tools_dr.open_dialog(self.dlg_qm, dlg_name='admin_translation')

    def open_file_dialog(self):
        # You can change this to getOpenFileName or getExistingDirectory if needed
        self.path, _ = QFileDialog.getOpenFileName(None, "Select File")  # Set parent to None if unsure
        if self.path:
            self.dlg_qm.txt_path.setText(self.path)
        self._check_connection()

    def pass_schema_info(self, schema_info, schema_name):
        self.project_epsg = schema_info['project_epsg']
        self.project_version = schema_info['project_version']
        self.project_language = schema_info['project_language']
        self.schema_name = schema_name

    # region private functions


    def _check_connection(self):
        """ Check connection to database """

        self.dlg_qm.cmb_language.clear()
        self.dlg_qm.lbl_info.clear()
        self._close_db()
        self.path = f"{self.plugin_dir}{os.sep}core{os.sep}i18n{os.sep}drain_i18n.gpkg"
        status = self._init_db(self.path)

        if not status:
            self.dlg_qm.btn_translate.setEnabled(False)
            tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', self.last_error)
            return
        self._populate_cmb_language()


    def _populate_cmb_language(self):
        """ Populate combo with languages values """

        self.dlg_qm.btn_translate.setEnabled(True)
        host = tools_qt.get_text(self.dlg_qm, self.dlg_qm.txt_path)
        msg = 'Connected to {0}'
        msg_params = (host,)
        tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', msg, msg_params=msg_params)
        sql = "SELECt id, language FROM cat_language;"
        rows = self._get_rows(sql, self.cursor_i18n)
        tools_qt.fill_combo_values(self.dlg_qm.cmb_language, rows)
        language = tools_dr.get_config_parser('i18n_generator', 'qm_lang_language', "user", "init", False)

        tools_qt.set_combo_value(self.dlg_qm.cmb_language, language, 0)

    # region MAIN

    def _check_translate_options(self):
        """ Check the translation options selected by the user """

        self.dlg_qm.lbl_info.clear()
        msg = ''
        self.language = tools_qt.get_combo_value(self.dlg_qm, self.dlg_qm.cmb_language, 1)
        print(self.language)
        self.lower_lang = self.language.lower()

        py_msg = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_msg)
        if py_msg:
            status_py_msg = self._create_py_files()
            if status_py_msg is True:
                msg += tools_qt.tr("Python translation successful\n")
            elif status_py_msg is False:
                msg += tools_qt.tr("Python translation failed\n")
            elif status_py_msg is None:
                msg += tools_qt.tr("Python translation canceled\n")

        self._create_path_dic()
        for type_dbfile in self.path_dic:     
            if tools_qt.is_checked(self.dlg_qm, self.path_dic[type_dbfile]['checkbox']):
                status_all_db_msg, dbtable = self._create_all_db_files(self.path_dic[type_dbfile]["path"], type_dbfile)
                if status_all_db_msg is True:
                    msg += f"{type_dbfile} {tools_qt.tr('translation successful')}\n"
                elif status_all_db_msg is False:
                    msg += f"{type_dbfile} {tools_qt.tr('translation failed in table')}: {dbtable}\n"
                elif status_all_db_msg is None:
                    msg += f"{type_dbfile} {tools_qt.tr('translation canceled')}\n"     

        if msg != '':
            tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', msg)

    # endregion
    # region PY files

    def _create_py_files(self):
        """ Read the values of the database and generate the ts and qm files """

        # On the database, the dialog_name column must match the name of the ui file (no extension).
        # Also, open_dialog function must be called, passed as parameter dlg_name = 'ui_file_name_without_extension'

        key_label = f'lb_{self.lower_lang}'
        key_tooltip = f'tt_{self.lower_lang}'
        key_message = f'ms_{self.lower_lang}'

        # Get python messages values

        # Get python toolbars and buttons values
        if self.lower_lang == 'en_us':
            sql = f"SELECT source, ms_en_us FROM pymessage;"  # ADD new columns
            py_messages = self._get_rows(sql, self.cursor_i18n)
            sql = f"SELECT source, lb_en_us FROM pytoolbar;"
            py_toolbars = self._get_rows(sql, self.cursor_i18n)
            print(py_toolbars)
            # Get python dialog values
            sql = (f"SELECT dialog_name, source, lb_en_us, tt_en_us"
                f" FROM pydialog"
                f" ORDER BY dialog_name;")
            py_dialogs = self._get_rows(sql, self.cursor_i18n)
        else:
            sql = f"SELECT source, ms_en_us, {key_message}, auto_{key_message} FROM pymessage;"  # ADD new columns
            py_messages = self._get_rows(sql, self.cursor_i18n)
            sql = f"SELECT source, lb_en_us, {key_label}, auto_{key_label} FROM pytoolbar;"
            py_toolbars = self._get_rows(sql, self.cursor_i18n)
            # Get python dialog values
            sql = (f"SELECT dialog_name, source, lb_en_us, {key_label}, auto_{key_label}, tt_en_us,"
                f" {key_tooltip}, auto_{key_tooltip} FROM pydialog"
                f" ORDER BY dialog_name;")
            py_dialogs = self._get_rows(sql, self.cursor_i18n)

        ts_path = self.plugin_dir + os.sep + 'i18n' + os.sep + f'drain_{self.language}.ts'

        # Check if file exist
        if os.path.exists(ts_path):
            msg = "Are you sure you want to overwrite this file?"
            title = "Overwrite"
            answer = tools_qt.show_question(msg, title, parameter=f"\n\n{ts_path}")
            if not answer:
                return None
        ts_file = open(ts_path, "w")

        # Create header
        line = '<?xml version="1.0" encoding="utf-8"?>\n'
        line += '<!DOCTYPE TS>\n'
        line += f'<TS version="2.0" language="{self.language}">\n'
        ts_file.write(line)

        # Create children for toolbars and actions
        line = '\t<context>\n'
        line += '\t\t<name>drain</name>\n'
        line += '\t\t<!-- TOOLBARS AND ACTIONS -->\n'
        ts_file.write(line)
        for py_tlb in py_toolbars:
            py_tlb = dict(py_tlb)
            line = f"\t\t<message>\n"
            line += f"\t\t\t<source>{py_tlb['source']}</source>\n"
            if py_tlb[key_label] is None:  # Afegir aqui l'auto amb un if
                py_tlb[key_label] = py_tlb[f'auto_{key_label}']
                if py_tlb[f'auto_{key_label}'] is None:
                    py_tlb[key_label] = py_tlb['lb_en_us']
                    if py_tlb['lb_en_us'] is None:
                        py_tlb[key_label] = py_tlb['source']

            line += f"\t\t\t<translation>{py_tlb[key_label]}</translation>\n"
            line += f"\t\t</message>\n"
            line = line.replace("&", "")
            ts_file.write(line)

        line = '\t\t<!-- PYTHON MESSAGES -->\n'
        ts_file.write(line)

        # Create children for message
        for py_msg in py_messages:
            py_msg = dict(py_msg)
            line = f"\t\t<message>\n"
            line += f"\t\t\t<source>{py_msg['source']}</source>\n"
            if py_msg[key_message] is None:  # Afegir aqui l'auto amb un if
                py_msg[key_message] = py_msg[f'auto_{key_message}']
                if py_msg[f'auto_{key_message}'] is None:
                    py_msg[key_message] = py_msg['source']
            line += f"\t\t\t<translation>{py_msg[key_message]}</translation>\n"
            line += f"\t\t</message>\n"
            line = line.replace("&", "")
            ts_file.write(line)
        line = '\t</context>\n\n'

        line += '\t<!-- UI TRANSLATION -->\n'
        ts_file.write(line)

        # Create children for ui
        name = None
        for py_dlg in py_dialogs:
            py_dlg = dict(py_dlg)
            # Create child <context> (ui's name)
            if name and name != py_dlg['dialog_name']:
                line += '\t</context>\n'
                ts_file.write(line)

            if name != py_dlg['dialog_name']:
                name = py_dlg['dialog_name']
                line = '\t<context>\n'
                line += f'\t\t<name>{name}</name>\n'
                title = self._get_title(py_dialogs, name, key_label)
                if title:
                    line += f'\t\t<message>\n'
                    line += f'\t\t\t<source>title</source>\n'
                    line += f'\t\t\t<translation>{title}</translation>\n'
                    line += f'\t\t</message>\n'

            # Create child for labels
            line += f"\t\t<message>\n"
            line += f"\t\t\t<source>{py_dlg['source']}</source>\n"
            if py_dlg[key_label] is None:  # Afegir aqui l'auto amb un if
                if self.lower_lang != 'en_us':
                    py_dlg[key_label] = py_dlg[f'auto_{key_label}']
                if py_dlg[key_label] is None:
                    py_dlg[key_label] = py_dlg['lb_en_us']

            line += f"\t\t\t<translation>{py_dlg[key_label]}</translation>\n"
            line += f"\t\t</message>\n"

            # Create child for tooltip
            line += f"\t\t<message>\n"
            line += f"\t\t\t<source>tooltip_{py_dlg['source']}</source>\n"
            if py_dlg[key_tooltip] is None:  # Afegir aqui l'auto amb un if
                if self.lower_lang != 'en_us':
                    py_dlg[key_tooltip] = py_dlg[f'auto_{key_tooltip}']
                if not py_dlg[key_tooltip]:  # Afegir aqui l'auto amb un if
                    py_dlg[key_tooltip] = py_dlg['tt_en_us']
            line += f"\t\t\t<translation>{py_dlg[key_tooltip]}</translation>\n"
            line += f"\t\t</message>\n"

        # Close last context and TS
        line += '\t</context>\n'
        line += '</TS>\n\n'
        line = line.replace("&", "")
        ts_file.write(line)
        ts_file.close()
        del ts_file

        lrelease_path = f"{self.plugin_dir}{os.sep}resources{os.sep}i18n{os.sep}lrelease.exe"
        status = subprocess.call([lrelease_path, ts_path], shell=False)
        if status == 0:
            return True
        else:
            return False


    def _get_title(self, py_dialogs, name, key_label):
        """ Return title's according language """

        title = None
        for py in py_dialogs:
            if py['source'] == f'dlg_{name}':
                title = py[key_label]
                if not title:  # Afegir aqui l'auto amb un if
                    if self.lower_lang != 'en_us':
                        title = py[f'auto_{key_label}']
                    if not title:
                        title = py['lb_en_us']
                    return title
                return title
        return title
    
    # endregion
    # region Database files
    
    def _create_all_db_files(self, cfg_path, file_type):
        """ Read the values of the database and update the i18n files """
            
        file_name = f"{self.path_dic[file_type]["name"]}"

        # Check if file exist
        if os.path.exists(cfg_path + file_name):
            msg = "Are you sure you want to overwrite this file?"
            title = "Overwrite"
            answer = tools_qt.show_question(msg, title, parameter=f"\n\n{cfg_path}{file_name}")
            if not answer:
                return None, ""
        else:
            os.makedirs(cfg_path, exist_ok=True)

        # Get All table values
        self._write_header(cfg_path + file_name, file_type)
        dbtables = self.path_dic[file_type]["tables"]
        for dbtable in dbtables:
            dbtable_rows, dbtable_columns = self._get_table_values(dbtable)
            if not dbtable_rows:
                return False, dbtable
            else:
                if "json" in dbtable:
                    self._write_dbjson_values(dbtable_rows, cfg_path + file_name)
                else:
                    self._write_table_values(dbtable_rows, dbtable_columns, dbtable, cfg_path + file_name, file_type)            

        return True, ""
    
    # endregion
    # region Gen. any table files

    def _get_table_values(self, table):
        """ Get table values """

        # Update the part the of the program in process
        self.dlg_qm.lbl_info.clear()
        msg = "Updating {0}..."
        msg_params = (table,)
        tools_qt.set_widget_text(self.dlg_qm, 'lbl_info', msg, msg_params=msg_params)
        QApplication.processEvents()
        columns = []
        lang_colums = []

        if table == 'dbconfig_form_fields':
            columns = ["source_code", "context", "formname", "formtype", "source", "lb_en_us", "pl_en_us", "ds_en_us"]
            lang_colums = [f"lb_{self.lower_lang}", f"auto_lb_{self.lower_lang}", f"va_auto_lb_{self.lower_lang}", 
                           f"pl_{self.lower_lang}", f"auto_pl_{self.lower_lang}", f"va_auto_pl_{self.lower_lang}", 
                           f"ds_{self.lower_lang}", f"auto_ds_{self.lower_lang}", f"va_auto_ds_{self.lower_lang}"]

        if table == "dbtexts":
            columns = ["source_code", "source", "context", "al_en_us", "ds_en_us"]
            lang_colums = [f"al_{self.lower_lang}", f"auto_al_{self.lower_lang}", f"va_auto_al_{self.lower_lang}", 
                           f"ds_{self.lower_lang}", f"auto_ds_{self.lower_lang}", f"va_auto_ds_{self.lower_lang}"]

        if table == 'dbconfig_form_fields_json':
            columns = ["source_code", "context", "formname", "formtype", "source", "hint", "text", "lb_en_us"]
            lang_colums = [f"lb_{self.lower_lang}", f"auto_lb_{self.lower_lang}", f"va_auto_lb_{self.lower_lang}"]

        # Make the query
        sql=""
        if self.lower_lang == 'en_us':
            sql = (f"SELECT {", ".join(columns)} "
               f"FROM {table} "
               f"ORDER BY context;")
        else:
            sql = (f"SELECT {", ".join(columns)}, {", ".join(lang_colums)} "
               f"FROM {table} "
               f"ORDER BY context;")
        rows = self._get_rows(sql, self.cursor_i18n)

        # Return the corresponding information
        if not rows:
            return None, columns
        return rows, columns


    def _write_table_values(self, rows, columns, table, path, file_type):
        """
        Generate mass update SQL queries using VALUES and write them to file
            :param rows: List of values ([List][Dict])
            :param path: Full destination path (String)
            :return: (Boolean)
        """

        values_by_context = {}
        forenames = [col.split("_")[0] for col in columns if col.endswith("en_us")]

        for row_sqlite in rows:
            row = dict(row_sqlite) # Convert sqlite3.Row to dict
            texts = []
            for forename in forenames:
                value = row.get(f'{forename}_{self.lower_lang}')

                if not value and self.lower_lang != 'en_us':
                    value = row.get(f'auto_{forename}_{self.lower_lang}')

                if not value:
                    value = row.get(f'{forename}_en_us')

                if not value:
                    texts.append("NULL")
                else:
                    escaped_value = value.replace("'", "''")
                    texts.append(f"'{escaped_value}'")

            for i, text in enumerate(texts):
                texts[i] = self._replace_invalid_characters(texts[i])

            context = row['context']
            if context not in values_by_context:
                values_by_context[context] = []

            values_by_context[context].append((row, texts))

        with open(path, "a") as file:
            for context, data in values_by_context.items():
                if 'dbconfig_form_fields' in table:
                    for item_row, txt in data:
                        file.write(f"UPDATE {context} SET label = {txt[0]}, placeholder = {txt[1]}, descript = {txt[2]} WHERE formname = '{item_row['formname']}' AND formtype = '{item_row['formtype']}' AND columnname = '{item_row['source']}';\n")

                elif "dbtexts" in table:
                    if context == "sys_message":
                        for item_row, txt in data:
                            file.write(f"UPDATE {context} SET text = {txt[0]} WHERE id = '{item_row['source']}';\n")

                    elif context == "config_csv":
                        for item_row, txt in data:
                            file.write(f"UPDATE {context} SET alias = {txt[0]}, descript = {txt[1]} WHERE id = {item_row['source']};\n")

                    elif context == "edit_typevalue":
                        for item_row, txt in data:
                            file.write(f"UPDATE {context} SET idval = {txt[0]}, descript = {txt[1]} WHERE rowid = {item_row['source']};\n")

                    elif context == "gpkg_spatial_ref_sys":
                        for item_row, txt in data:
                            file.write(f"UPDATE {context} SET srs_name = {txt[0]}, definition = {txt[1]} WHERE srs_id = {item_row['source']};\n")
        del file


    # endregion
    # region Generate from Json

    def _write_dbjson_values(self, rows, path):
        closing = False
        values_by_context = {}

        updates = {}
        for row_sqlite in rows: # Iterate over sqlite3.Row objects
            row_dict = dict(row_sqlite) # Convert to dict for .get() and modification
            # Set key depending on context
            if row_dict["context"] == "config_form_fields":
                closing = True
                key = (row_dict["source"], row_dict["context"], row_dict["text"], row_dict["formname"], row_dict["formtype"])
            else:
                key = (row_dict["source"], row_dict["context"], row_dict["text"])
            updates.setdefault(key, []).append(row_dict) # Store the dict

        for key, related_rows_dicts in updates.items(): # related_rows_dicts are now lists of dicts
            # Unpack key
            source, context, original_text, *extra = key
            
            # Correct column based on context
            if context == "config_report":
                column = "filterparam"
            elif context == "config_toolbox":
                column = "inputparams"
            elif context == "config_form_fields":
                column = "widgetcontrols"
            else:
                print(f"Unknown context: {context}, skipping.")
                continue

            # Parse JSON safely
            if context != "config_form_fields":
                try:
                    json_data = ast.literal_eval(original_text)
                except (ValueError, SyntaxError):
                    print(f"Error parsing JSON from text: {original_text}")
                    continue
            else:
                modified = original_text.replace("'", "\"").replace("False", "false").replace("True", "true").replace("None", "null")
                try:
                    json_data = json.loads(modified)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    continue

            # Translate fields
            for row_dict in related_rows_dicts: # Iterate over dicts
                key_hint = row_dict["hint"].split('_')[0] # Use dict access
                default_text = row_dict.get("lb_en_us", "")
                translated = (
                    row_dict.get(f"lb_{self.lower_lang}") or
                    row_dict.get(f"auto_lb_{self.lower_lang}") or
                    default_text
                )

                if ", " in default_text:
                    default_list = default_text.split(", ")
                    translated_list = translated.split(", ")
                    for item in json_data:
                        if isinstance(item, dict) and key_hint in item and "comboNames" in item:
                            # Ensure item["comboNames"] is a list before using set operations or list comprehensions
                            if isinstance(item["comboNames"], list) and set(default_list).intersection(item["comboNames"]):
                                item["comboNames"] = [
                                    t if d in default_list else d
                                    for d, t in zip(default_list, translated_list)
                                ]
                else:
                    if isinstance(json_data, dict):
                        for key_name, value in json_data.items():
                            if key_name == key_hint and value == default_text:
                                json_data[key_name] = translated
                    elif isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict) and key_hint in item and item[key_hint] == default_text:
                                item[key_hint] = translated
                    else:
                        print("Unexpected json_data structure!")

            # Encode new JSON safely
            new_text = json.dumps(json_data, ensure_ascii=False).replace("'", "''")

            # Save the result grouped by context and column
            if context not in values_by_context:
                values_by_context[context] = []

            # related_rows_dicts[0] is the first dict for this group
            values_by_context[context].append((source, related_rows_dicts[0], new_text, column)) 

        # Now write to file
        with open(path, "a", encoding="utf-8") as file:
            for context, data in values_by_context.items():
                # Assume all entries in this context share same column
                column = data[0][3]

                if context == "config_form_fields":
                    values_str = ",\n    ".join([
                        f"('{item_row['source']}', '{item_row['formname']}', '{item_row['formtype']}', '{txt}')" # Use item_row as dict
                        for source_id, item_row, txt, col in data
                    ])
                    file.write(f"UPDATE {context} AS t\nSET {column} = v.text::json\nFROM (\n    VALUES\n    {values_str}\n) AS v(columnname, formname, formtype, text)\nWHERE t.columnname = v.columnname AND t.formname = v.formname AND t.formtype = v.formtype;\n\n")
                else:
                    values_str = ",\n    ".join([
                        f"({source_id}, '{txt}')" # Use source_id from the tuple
                        for source_id, item_row, txt, col in data
                    ])
                    file.write(f"UPDATE {context} AS t\nSET {column} = v.text::json\nFROM (\n    VALUES\n    {values_str}\n) AS v(id, text)\nWHERE t.id = v.id;\n\n")

            if closing:
                file.write("UPDATE config_param_system SET value = FALSE WHERE parameter = 'admin_config_control_trigger';\\n")  


    # endregion
 
    # region Extra functions

    def _write_header(self, path, file_type):
        """
        Write the file header
            :param path: Full destination path (String)
        """

        file = open(path, "w")
        header = (f'/*\n'
                  f'This file is part of drain project software\n'
                  f'The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License '
                  f'as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. '
                  f'This version of Giswater is provided by Giswater Association.\n'
                  f'*/\n\n\n')
        if file_type in ["i18n_ws", "i18n_ud"]:
            header += (f'SET search_path = SCHEMA_NAME, public, pg_catalog;\n'
                       f"UPDATE config_param_system SET value = FALSE WHERE parameter = 'admin_config_control_trigger';\n\n")
        elif file_type == "am":
            header += f'SET search_path = am, public;\n'
        elif file_type == "cm":
            header += f'SET search_path = SCHEMA_NAME, public, pg_catalog;\n'

        file.write(header)
        file.close()
        del file

    def _save_user_values(self):
        """ Save selected user values """

        host = tools_qt.get_text(self.dlg_qm, self.dlg_qm.txt_path, return_string_null=False)
        py_msg = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_msg)
        i18n_msg = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_i18n_files)

        tools_dr.set_config_parser('i18n_generator', 'txt_path', f"{host}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_generator', 'chk_py_msg', f"{py_msg}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_generator', 'chk_i18n_files', f"{i18n_msg}", "user", "session", prefix=False)


    def _load_user_values(self):
        """
        Load last selected user values
            :return: Dictionary with values
        """

        host = tools_dr.get_config_parser('i18n_generator', 'txt_path', "user", "session", False)
        py_msg = tools_dr.get_config_parser('i18n_generator', 'chk_py_msg', "user", "session", False)
        i18n_msg = tools_dr.get_config_parser('i18n_generator', 'chk_i18n_files', "user", "session", False)

        tools_qt.set_widget_text(self.dlg_qm, 'txt_path', host)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_py_msg, py_msg)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_i18n_files, i18n_msg)


    def _init_db(self, gpkg_path):
        """ Initializes database connection """

        try:
            self.conn_i18n = sqlite3.connect(gpkg_path)
            self.conn_i18n.row_factory = sqlite3.Row 
            self.cursor_i18n = self.conn_i18n.cursor()
            status = True
        except sqlite3.DatabaseError as e:
            self.last_error = e
            status = False

        return status


    def _close_db(self):
        """ Close database connection """

        try:
            status = True
            if self.cursor_i18n:
                self.cursor_i18n.close()
            if self.conn_i18n:
                self.conn_i18n.close()
            del self.cursor_i18n
            del self.conn_i18n
        except Exception as e:
            self.last_error = e
            status = False

        return status


    def _commit(self, cursor):
        """ Commit current database transaction """
        cursor.commit()


    def _rollback(self, cursor):
        """ Rollback current database transaction """
        cursor.rollback()


    def _get_rows(self, sql, cursor, commit=True):
        """ Get multiple rows from selected query """

        self.last_error = None
        rows = None
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if commit:
                self._commit(cursor)
        except Exception as e:
            self.last_error = e
            print(self.last_error)
            if commit:
                self._rollback(cursor)
        finally:
            return rows


    def _replace_invalid_characters(self, param):
        """
        This function replaces the characters that break JSON messages
         (", new line, etc.)
            :param param: The text to fix (String)
        """
        if "\\" in param:
            param = param.replace("\"", "''")
            param = param.replace("\r", "")
            param = param.replace("\n", " ")
        param = param.replace("'None'", "NULL")

        return param


    def _replace_invalid_quotation_marks(self, param):
        """
        This function replaces the characters that break JSON messages
         (')
            :param param: The text to fix (String)
        """
        param = re.sub(r"(?<!')'(?!')", "''", param)

        return param


    def _create_path_dic(self):
        self.path_dic = {
            "DB": {
                "path": f"{self.plugin_dir}{os.sep}dbmodel{os.sep}i18n{os.sep}{self.language}{os.sep}",
                "name": "dml.sql",
                "checkbox": self.dlg_qm.chk_i18n_files,
                "tables": ["dbconfig_form_fields", "dbtexts"]
            },
        }


    # endregion
