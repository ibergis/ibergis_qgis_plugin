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
from functools import partial
from itertools import product


from ..ui.ui_manager import DrSchemaI18NManagerUi
from ..utils import tools_dr
from ...lib import tools_qt
from ... import global_vars
from PyQt5.QtWidgets import QApplication


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
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_py_messages, py_msg)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_py_dialogs, py_dialogs)
        tools_qt.set_checked(self.dlg_qm, self.dlg_qm.chk_db_dialogs, db_msg)

    def _set_connection(self):
        """ Set connection to database """

        self.dlg_qm.lbl_info.clear()
        self._close_db_org()
        # Connection with origin db
        path_i18n = f"{self.plugin_dir}{os.sep}core{os.sep}i18n{os.sep}ibergis_i18n.gpkg"
        path_sample = f"{self.plugin_dir}{os.sep}core{os.sep}i18n{os.sep}ibergis_sample.gpkg"
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
            self.cursor_org = self.conn_org.cursor()
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
        tools_dr.set_config_parser('i18n_manager', 'qm_py_msg', f"{py_msg}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_manager', 'qm_py_dialogs', f"{py_dialogs}", "user", "session", prefix=False)
        tools_dr.set_config_parser('i18n_manager', 'qm_db_msg', f"{db_msg}", "user", "session", prefix=False)
        
    def pass_schema_info(self, schema_info):
        self.project_type = schema_info['project_type']
        self.project_epsg = schema_info['project_epsg']
        self.project_version = schema_info['project_version']

    # endregion
    def _update_i18n_database(self):
        self.py_messages = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_messages)
        self.py_dialogs = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_py_dialogs)
        self.db_tables = tools_qt.is_checked(self.dlg_qm, self.dlg_qm.chk_db_dialogs)
        
        if self.db_tables:
            self._update_db_tables()

        if self.py_messages:
            self._update_py_messages()
        
        if self.py_dialogs:
            self._update_py_dialogs()

    # region Missing DB Dialogs
    def _update_db_tables(self):
        no_repeat_table = []
        self.project_type = "DB"

        self.tables_dic()
        tables_i18n = self.dbtables_dic[self.project_type]['dbtables']

        text_error = f"\n{self.project_type}\n"
        self.dlg_qm.lbl_info.clear()
        for table_i18n in tables_i18n:
            if table_i18n not in no_repeat_table:
                table_exists = self.detect_table_func(table_i18n)
                correct_lang = self._verify_lang()
                self._change_table_lyt(table_i18n)
                if not table_exists:
                    msg = "The table ({0}) does not exists"
                    msg_params = (table_i18n,)
                    tools_qt.show_info_box(msg, msg_params=msg_params)
                    no_repeat_table.append(table_i18n)
                elif correct_lang:
                    text_error += self._update_tables(table_i18n)
                else:
                    msg = "Incorrect languages, make sure to have the giswater project in english"
                    tools_qt.show_info_box(msg)
                    break 

        self._vacuum_commit(self.conn_i18n, self.cursor_i18n)      
        self.dlg_qm.lbl_info.clear()
        tools_qt.show_info_box(text_error)

    def _update_tables(self, table_i18n):
        tables_org = self.dbtables_dic[self.project_type]['tables_org'][table_i18n]
        
        text_error = ""
        for table_org in tables_org:
            if "json" in table_i18n:
                text_error += self._json_update(table_i18n, table_org)
            else:
                text_error += self._update_any_table(table_i18n, table_org)
        return text_error

    def _update_any_table(self, table_i18n, table_org):
        columns_i18n, columns_org, names = self._get_rows_to_compare(table_i18n, table_org)

        columns_select_i18n = ", ".join(columns_i18n)
        query_i18n = f"SELECT {columns_select_i18n} FROM {table_i18n};"
        rows_i18n_sqlite = self._get_rows(query_i18n, self.cursor_i18n)
        
        processed_rows_i18n = []
        if rows_i18n_sqlite:
            for row_sqlite in rows_i18n_sqlite:
                row_dict = dict(row_sqlite)
                for column_name in columns_i18n:
                    # Handle potential CAST in column name for dictionary key access
                    actual_column_name = column_name
                    if "CAST(" in column_name:
                        actual_column_name = column_name[5:].split(" ")[0]
                    if row_dict[actual_column_name] is None:
                        row_dict[actual_column_name] = ''
                processed_rows_i18n.append(row_dict)
        
        columns_select_org = ", ".join(columns_org)
        query_org = f"SELECT {columns_select_org} FROM {table_org};"
        rows_org_sqlite = self._get_rows(query_org, self.cursor_org)
        
        text_error = ""
        if rows_org_sqlite:
            for row_org_sqlite_item in rows_org_sqlite:
                row_org_dict = dict(row_org_sqlite_item)
                for column_org_name in columns_org:
                    if row_org_dict[column_org_name] is None:
                        row_org_dict[column_org_name] = ''

                row_org_com_for_check = {col_i18n: row_org_dict.get(col_i18n) for col_i18n in columns_i18n if col_i18n in row_org_dict}

                if processed_rows_i18n is None or row_org_com_for_check not in processed_rows_i18n: 
                    texts = []
                    for name in names:
                        value = f"'{row_org_dict[name].replace("'", "''")}'" if row_org_dict[name] not in [None, ''] else 'NULL'
                        texts.append(value)

                    if 'dbconfig_form_fields' in table_i18n:
                        query = f"""INSERT INTO {table_i18n} (context, source_code, source, formname, formtype, lb_en_us, tt_en_us, pl_en_us, ds_en_us) 
                                        VALUES ('{table_org}', 'ibergis', '{row_org_dict['columnname']}', '{row_org_dict['formname']}', '{row_org_dict['formtype']}',
                                        {texts[0]}, {texts[1]}, {texts[2]}, {texts[3]}) 
                                        ON CONFLICT (context, source_code, source, formname, formtype) 
                                        DO UPDATE SET lb_en_us = {texts[0]}, tt_en_us = {texts[1]}, pl_en_us = {texts[2]}, ds_en_us = {texts[3]};\n"""
                    
                    elif 'dbtexts' in table_i18n:
                        source = ""
                        if table_org == "config_csv":
                            source = row_org_dict['id']
                        elif table_org == "edit_typevalue":
                            source = row_org_dict['rowid']
                        elif table_org == "sys_message":
                            source = row_org_dict['id']
                            texts.append("NULL")
                        elif table_org == "gpkg_spatial_ref_sys":
                            source = row_org_dict['srs_id']
                        query = f"""INSERT INTO {table_i18n} (source_code, context, source, al_en_us, ds_en_us) 
                                        VALUES ('ibergis', '{table_org}', '{source}', {texts[0]}, {texts[1]}) 
                                        ON CONFLICT (source_code, context, source) 
                                        DO UPDATE SET al_en_us = {texts[0]}, ds_en_us = {texts[1]};\n"""
                        
                    try:
                        self.cursor_i18n.execute(query)
                        self.conn_i18n.commit()
                    except Exception as e:
                        self.conn_i18n.rollback()
                        text_error += f"An error occured while translating {table_i18n}: {e}\n"
        if text_error == '':
            return f'{table_i18n}: 1- Succesfully updated table. '
        else:
            return f"{text_error}\n"
        
    def _get_rows_to_compare(self, table_i18n, table_org):
        if 'dbconfig_form_fields' in table_i18n:
            columns_i18n = ["formname", "formtype", "source", "lb_en_us", "tt_en_us", "pl_en_us", "ds_en_us"]
            columns_org = ["formname", "formtype", "columnname", "label", "tooltip", "placeholder", "descript"]
            names = ["label", "tooltip", "placeholder", "descript"]

        elif 'dbtexts' in table_i18n:
            columns_i18n = ["source", "al_en_us", "ds_en_us"]
            if table_org == "config_csv":
                columns_org = ["id", "alias", "descript"]
                names = ["alias", "descript"]
            elif table_org == "edit_typevalue":
                columns_org = ["rowid", "idval", "descript"]
                names = ["idval", "descript"]
            elif table_org == "sys_message":
                columns_org = ["id", "text"]
                names = ["text"]
            elif table_org == "gpkg_spatial_ref_sys":
                columns_org = ["srs_id", "srs_name", "definition"]
                names = ["srs_name", "definition"]
        return columns_i18n, columns_org, names
    
    # endregion
    # region Json
    
    def _json_update(self, table_i18n, table_org):
        self._change_table_lyt(table_i18n)
        column = "widgetcontrols"
        query = f"SELECT * FROM {table_org}"
        print(query)
        rows = self._get_rows(query, self.cursor_org)
        query = ""
        print(rows)
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
                        print(row)
                        print(f"data: {data}")
                        query_row = f""" INSERT INTO {table_i18n} (source_code, context, formname, formtype, source, hint, text, lb_en_us)
                        VALUES ('giswater', '{table_org}', '{row['formname']}', '{row['formtype']}', '{row['columnname']}', '{key}_{i}', '{safe_row_column}', '{safe_text}')
                        ON CONFLICT (source_code, context, formname, formtype, source, hint, text)
                        DO UPDATE SET lb_en_us = '{safe_text}'; """ 
                        
                        # Execute or collect query_row
                        query += query_row
        return query
    
    # endregion
    # region Python
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
                    pattern = r'>(.*?)<'
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
                except Exception:
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

    # endregion
    # region Global funcitons

    def detect_table_func(self, table):
        self.cursor_i18n.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        table_exists = self.cursor_i18n.fetchone() is not None
        if table_exists:
            return True
        else:
            return False

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

    def _vacuum_commit(self, conn, cursor):
        cursor.execute("VACUUM")
        conn.commit()

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
        return True
        query = "SELECT language from sys_version"
        self.cursor_org.execute(query)
        language_org = self.cursor_org.fetchone()[0]
        if language_org != 'en_US':
            return False
        return True
    
    def tables_dic(self):
        self.dbtables_dic = {
            "DB": {
                "dbtables": [ "dbtexts", "dbconfig_form_fields", "dbconfig_form_fields_json"],
                "tables_org": {
                    "dbtexts": ["config_csv", "edit_typevalue", "sys_message", "gpkg_spatial_ref_sys"],
                    "dbconfig_form_fields": ["config_form_fields"],
                    "dbconfig_form_fields_json": ["config_form_fields"]
                }
            },
        }

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
        message = "{0} has been deprecated. Use {1} instead."
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
        message = "SWMM OPTIONS"
        message = "SWMM RESULTS"
        message = "IBER OPTIONS"
        message = "IBER RESULTS"
        message = "IBER PLUGINS"
    # endregion