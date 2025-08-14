"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
import json
import time
import datetime
import getpass
# -*- coding: utf-8 -*-
import os
from functools import partial
from osgeo import gdal

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QRadioButton, QLineEdit, QComboBox, QFileDialog, QTableView, QAbstractItemView
from qgis.core import QgsProject, QgsApplication
from qgis.utils import reloadPlugin

from .gis_file_create import DrGisFileCreate
from ..ui.ui_manager import DrAdminUi
from ..i18n.i18n_generator import DrI18NGenerator
from ..i18n.schema_i18n_update import DrSchemaI18NUpdate
from ..i18n.i18n_manager import DrSchemaI18NManager
from ..utils import tools_dr
from ..threads.project_gpkg_schema_create import DrGpkgCreateSchemaTask
from ... import global_vars
from ...lib import tools_qt, tools_qgis, tools_log, tools_gpkgdao, tools_db


class DrGpkgBase:
    """Base class for geopackage operations"""

    def __init__(self):
        self.error_count = 0
        self.plugin_dir = global_vars.plugin_dir
        self.sql_dir = os.path.normpath(os.path.join(self.plugin_dir, 'dbmodel'))
        self.gpkg_dao_data = None

    def _check_database_connection(self, db_filepath, database_name):
        """Set database connection to Geopackage file"""

        # Create object to manage GPKG database connection
        gpkg_dao_data = tools_gpkgdao.DrGpkgDao()
        self.gpkg_dao_data = gpkg_dao_data

        # Check if file path exists
        if not os.path.exists(db_filepath):
            msg = "File not found: {0}"
            msg_params = (db_filepath,)
            tools_log.log_info(msg, msg_params=msg_params)
            return False

        # Set DB connection
        msg = "Set database connection"
        tools_log.log_info(msg)
        status = self.gpkg_dao_data.init_db(db_filepath)
        if not status:
            last_error = self.gpkg_dao_data.last_error
            msg = "Error connecting to database ({0}): {1}\n{2}"
            msg_params = ("sqlite3", db_filepath, last_error,)
            tools_log.log_info(msg, msg_params=msg_params)
            return False

        status, self.db_qsql_data = self.gpkg_dao_data.init_qsql_db(db_filepath, database_name)
        if not status:
            last_error = self.gpkg_dao_data.last_error
            msg = "Error connecting to database ({0}): {1}\n{2}"
            msg_params = ("QSqlDatabase", db_filepath, last_error,)
            tools_log.log_info(msg, msg_params=msg_params)
            return False

        msg = "Database connection successful"
        tools_log.log_info(msg)
        return True

    def _read_execute_file(self, filepath, project_epsg=None):
        """Read and execute a SQL file"""

        status = False
        f = None
        try:
            f = open(filepath, 'r', encoding="utf8")
            if f:
                sql_content = f.read()
                if project_epsg:
                    sql_content = sql_content.replace("<SRID_VALUE>", project_epsg)
                status = self.gpkg_dao_data.execute_script_sql(sql_content)
                if status is False:
                    self.error_count += 1
                    msg = "Error executing file: {0}\nDatabase error: {1}"
                    print(msg)
                    msg_params = (os.path.basename(filepath), self.gpkg_dao_data.last_error,)
                    tools_log.log_warning(msg, msg_params=msg_params)
                    tools_qt.show_info_box(msg)
                    return False

        except Exception as e:
            self.error_count += 1
            msg = "Error executing file: {0}\n{1}"
            msg_params = (os.path.basename(filepath), str(e),)
            tools_log.log_warning(msg, msg_params=msg_params)
            tools_qt.show_info_box(msg, msg_params=msg_params)
            status = False

        finally:
            if f:
                f.close()
            return status

    def _execute_trg_creation(self):
        """Create triggers for tables"""

        # Geom tables
        sql = "SELECT table_name, index_col FROM tables_geom;"
        rows = self.gpkg_dao_data.get_rows(sql)
        list_tbl_geom = [(row[0], row[1]) for row in rows] if rows else []

        for tablename, index_col in list_tbl_geom:
            if index_col:
                sql = f"""CREATE INDEX idx_{index_col}_{tablename} ON {tablename} ({index_col});"""
                self.gpkg_dao_data.execute_sql(sql, commit=False)

            aux_str = "AFTER"
            if 'v_' in tablename or 'vi_' in tablename:
                aux_str = "INSTEAD OF"
            sql = f"""CREATE VIRTUAL TABLE rtree_{tablename}_geom USING rtree(id, minx, maxx, miny, maxy);"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER trigger_delete_feature_count_{tablename} {aux_str} DELETE ON {tablename} BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower("{tablename}"); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER trigger_insert_feature_count_{tablename} {aux_str} INSERT ON {tablename} BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower("{tablename}"); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_delete {aux_str} DELETE ON {tablename} WHEN (old.geom NOT NULL) BEGIN DELETE FROM rtree_{tablename}_geom WHERE id= OLD.fid; END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_insert {aux_str} INSERT ON {tablename} WHEN (new.geom NOT NULL AND NOT ST_IsEmpty(NEW.geom)) BEGIN INSERT OR REPLACE INTO rtree_{tablename}_geom VALUES (NEW.fid, ST_MinX(NEW.geom), ST_MaxX(NEW.geom), ST_MinY(NEW.geom), ST_MaxY(NEW."geom") ); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_update1 {aux_str} UPDATE OF geom ON {tablename} WHEN OLD.fid = NEW.fid AND (NEW.geom NOTNULL AND NOT ST_IsEmpty(NEW.geom) ) BEGIN INSERT OR REPLACE INTO rtree_{tablename}_geom VALUES (NEW.fid, ST_MinX(NEW.geom), ST_MaxX(NEW.geom), ST_MinY(NEW.geom), ST_MaxY(NEW.geom)); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_update2 {aux_str} UPDATE OF geom ON {tablename} WHEN OLD.fid = NEW.fid AND (NEW.geom ISNULL OR ST_IsEmpty(NEW.geom) ) BEGIN DELETE FROM rtree_{tablename}_geom WHERE id= OLD.fid; END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_update3 {aux_str} UPDATE ON {tablename} WHEN OLD.fid != NEW.fid AND (NEW.geom NOTNULL AND NOT ST_IsEmpty(NEW.geom) ) BEGIN DELETE FROM rtree_{tablename}_geom WHERE id= OLD.fid; INSERT OR REPLACE INTO rtree_{tablename}_geom VALUES (NEW.fid, ST_MinX(NEW.geom), ST_MaxX(NEW.geom), ST_MinY(NEW.geom), ST_MaxY(NEW.geom)); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER rtree_{tablename}_geom_update4 {aux_str} UPDATE ON {tablename} WHEN OLD.fid != NEW.fid AND (NEW.geom ISNULL OR ST_IsEmpty(NEW.geom) ) BEGIN DELETE FROM rtree_{tablename}_geom WHERE id IN (OLD.fid, NEW.fid); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)

            self.gpkg_dao_data.commit()

        # No-geom tables
        sql = "SELECT table_name, index_col FROM tables_nogeom;"
        rows = self.gpkg_dao_data.get_rows(sql)

        list_tbl_nogeom = [(row[0], row[1]) for row in rows] if rows else []

        for tablename, index_col in list_tbl_nogeom:
            if index_col:
                sql = f"""CREATE INDEX idx_{index_col}_{tablename} ON {tablename} ({index_col});"""
                self.gpkg_dao_data.execute_sql(sql, commit=False)

            aux_str = "AFTER"
            if 'v_' in tablename or 'vi_' in tablename:
                aux_str = "INSTEAD OF"
            sql = f"""CREATE TRIGGER "trigger_delete_feature_count_{tablename}" {aux_str} DELETE ON "{tablename}" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower("{tablename}"); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            sql = f"""CREATE TRIGGER "trigger_insert_feature_count_{tablename}" {aux_str} INSERT ON "{tablename}" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower("{tablename}"); END;"""
            self.gpkg_dao_data.execute_sql(sql, commit=False)
            self.gpkg_dao_data.commit()


class DrAdminButton(DrGpkgBase):
    """Class to control action 'Admin'"""

    def __init__(self):
        super().__init__()
        self.project_params = {}
        self.project_descript = None
        self.gpkg_full_path = None
        self.dict_folders_process = {}
        self.plugin_version, self.message = tools_qgis.get_plugin_version()
        self.project_epsg = None
        self.gpkg_name = None
        self.project_path = None
        self.dlg_readsql = None
        self.total_sql_files = 0    # Total number of SQL files to process
        self.current_sql_file = 0   # Current number of SQL file
        self.gpkg_dao_config = None
        self.last_srid = None

    def init_sql(self):
        """ Button 100: Execute SQL. Info show info """

        # Connect to sqlite database
        self.gpkg_dao_config = tools_gpkgdao.DrGpkgDao()

        # Add transaltor lobby translator
        tools_qt._add_translator()

        # Create the dialog and signals
        self._init_show_database()

    def create_project_data_schema(self):
        """"""

        gpkg_name = tools_qt.get_text(self.dlg_readsql, 'gpkg_name', return_string_null=False)
        project_descript = tools_qt.get_text(self.dlg_readsql, 'txt_description', return_string_null=False)
        project_path = tools_qt.get_text(self.dlg_readsql, 'data_path', return_string_null=False)
        project_srid = tools_qt.get_text(self.dlg_readsql, 'srid_id')
        project_locale = tools_qt.get_combo_value(self.dlg_readsql, self.cmb_locale, 0)

        if not gpkg_name or not project_path or not project_descript:
            msg = "Please fill all empty fields."
            tools_qt.show_info_box(msg)
            return

        # Set class variables
        self.gpkg_name = gpkg_name
        self.project_descript = project_descript
        self.project_path = project_path
        self.project_epsg = project_srid
        self.locale = project_locale

        self.gpkg_full_path = project_path + "/" + gpkg_name + ".gpkg"
        if os.path.exists(self.gpkg_full_path):
            msg = "Geopackage already exists. Do you want to overwrite it?"
            response = tools_qt.show_question(msg)
            if not response:
                return False
            if global_vars.gpkg_dao_data:
                global_vars.gpkg_dao_data.close_db()
            os.remove(self.gpkg_full_path)

        log_suffix = '%Y%m%d %H:%M:%S'
        self.project_params = {"project_name": self.gpkg_name, "project_descript": self.project_descript,
                               "project_user": getpass.getuser(), "project_tstamp": str(time.strftime(log_suffix)),
                               "project_version": self.plugin_version}

        # Save in settings
        tools_dr.set_config_parser('btn_admin', 'gpkg_name', f'{self.gpkg_name}', prefix=False)
        tools_dr.set_config_parser('btn_admin', 'project_description', f'{self.project_descript}', prefix=False)
        tools_dr.set_config_parser('btn_admin', 'project_path', f'{self.project_path}', prefix=False)
        tools_dr.set_config_parser('btn_admin', 'project_srid', f'{self.project_epsg}', prefix=False)
        tools_dr.set_config_parser('btn_admin', 'project_locale', f'{self.locale}', prefix=False)

        # Check if srid value is valid
        if self.last_srids is None:
            msg = "This SRID value does not exist on Database. Please select a diferent one."
            title = "Info"
            tools_qt.show_info_box(msg, title)
            return

        # Timer
        self.t0 = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)

        params = {}
        self.create_gpkg_thread = DrGpkgCreateSchemaTask(self, "Create GPKG", params, timer=self.timer)
        QgsApplication.taskManager().addTask(self.create_gpkg_thread)
        QgsApplication.taskManager().triggerTask(self.create_gpkg_thread)

    def change_tab(self):

        self.dlg_readsql.tab_main.setCurrentIndex(1)
        gpkg_name = tools_dr.get_config_parser('btn_admin', 'gpkg_name', "user", "session",
                                               False, force_reload=True)
        gpkg_path = tools_dr.get_config_parser('btn_admin', 'project_path', "user", "session",
                                               False, force_reload=True)
        self.dlg_readsql.txt_gis_file.setText(gpkg_name)
        self.dlg_readsql.txt_gis_gpkg.setText(f"{gpkg_path}/{gpkg_name}.gpkg")
        self.dlg_readsql.txt_gis_folder.setText(gpkg_path)

    def manage_process_result(self, is_utils=False, dlg=None):
        """"""

        status = (self.error_count == 0)
        self._manage_result_message(status, parameter="Create project")
        if not status:
            # Reset count error variable to 0
            self.error_count = 0
            msg = global_vars.session_vars['last_error_msg']
            tools_qt.show_exception_message(msg=msg)
            msg = "A rollback on schema will be done."
            tools_qgis.show_info(msg)
            if dlg:
                tools_dr.close_dialog(dlg)
            return
        global_vars.gpkg_dao_data.close_db()
        global_vars.gpkg_dao_data = global_vars.gpkg_dao_data.clone()
        self.change_tab()

    def init_dialog_create_project(self):
        """ Initialize dialog (only once) """

        # Find Widgets in form
        self.rdb_sample = self.dlg_readsql.findChild(QRadioButton, 'rdb_sample')
        self.rdb_data = self.dlg_readsql.findChild(QRadioButton, 'rdb_data')
        self.txt_gpkg_name = self.dlg_readsql.findChild(QLineEdit, 'gpkg_name')
        self.txt_description = self.dlg_readsql.findChild(QLineEdit, 'txt_description')
        self.txt_data_path = self.dlg_readsql.findChild(QLineEdit, 'data_path')
        self.cmb_locale = self.dlg_readsql.findChild(QComboBox, 'cmb_locale')
        self.txt_srid = self.dlg_readsql.findChild(QLineEdit, 'srid_id')

        # Load user values
        self.txt_gpkg_name.setText(tools_dr.get_config_parser('btn_admin', 'gpkg_name', "user", "session",
                                                              False, force_reload=True))
        self.txt_description.setText(tools_dr.get_config_parser('btn_admin', 'project_description', "user", "session",
                                                                False, force_reload=True))
        self.txt_data_path.setText(tools_dr.get_config_parser('btn_admin', 'project_path', "user", "session",
                                                              False, force_reload=True))
        self.txt_srid.setText(tools_dr.get_config_parser('btn_admin', 'project_srid', "user", "session",
                                                         False, force_reload=True))

        # Manage SRID
        self._manage_srid()

        # Populate combo with all locales
        filename = "config.gpkg"
        db_filepath = f"{global_vars.plugin_dir}{os.sep}config{os.sep}{filename}"
        tools_log.log_info(db_filepath)
        if os.path.exists(db_filepath):
            status = self.gpkg_dao_config.init_db(db_filepath)
            if status:
                list_locale = self._select_active_locales()
                tools_qt.fill_combo_values(self.cmb_locale, list_locale, 1)
                locale = tools_dr.get_config_parser('btn_admin', 'project_locale', 'user', 'session', False,
                                                    force_reload=True)
                tools_qt.set_combo_value(self.cmb_locale, locale, 0)
            else:
                msg = self.gpkg_dao_config.last_error
                tools_log.log_warning(msg)
        else:
            msg = "Database not found: {0}"
            msg_params = (db_filepath,)
            tools_log.log_warning(msg, msg_params=msg_params)

        # Disable locale combo if sample is selected
        if self.rdb_sample.isChecked():
            self.txt_srid.setEnabled(False)
        else:
            self.txt_srid.setEnabled(True)

        # Set shortcut keys
        self.dlg_readsql.key_escape.connect(
            partial(tools_dr.close_dialog, self.dlg_readsql, False))

        # Populate tbl_srid
        self._filter_srid_changed()

        # Set signals
        self._set_signals_create_project()

    def load_base(self, dict_folders):
        """"""

        for folder in dict_folders.keys():
            if "i18n" not in folder:
                if str(folder).endswith("trg"):
                    self._execute_trg_creation()
                status = self._execute_files(folder)
                if not status:
                    return False
        return True

    def load_sample_data(self):

        folder_example = os.path.join(self.sql_dir, "example")
        status = self._execute_files(folder_example)
        return status

    def _init_show_database(self):
        """ Initialization code of the form (to be executed only once) """

        # Get SQL folder and check if exists
        self.sql_dir = os.path.normpath(os.path.join(global_vars.plugin_dir, 'dbmodel'))
        if not os.path.exists(self.sql_dir):
            msg = "SQL folder not found: {0}"
            msg_params = (self.sql_dir,)
            tools_qgis.show_message(msg, msg_params=msg_params)
            return

        self.project_version = '0'

        # Get locale of QGIS application
        self.locale = tools_qgis.get_locale()

        # Declare all file variables
        self.file_pattern_ddl = "ddl"
        self.file_pattern_dml = "dml"
        self.file_pattern_sys_gpkg = "sys_gpkg"
        self.file_pattern_trg = "trg"

        # Declare all folders
        self.folder_software = self.sql_dir

        # Create dialog object
        self.dlg_readsql = DrAdminUi()
        tools_dr.load_settings(self.dlg_readsql)

        # Set transations tabs only visible for advanced users
        if global_vars.user_level['level'] not in global_vars.user_level['showadminadvanced']:
            tools_qt.remove_tab(self.dlg_readsql.tab_main, "tab_i18n")

        # Get widgets form
        self.cmb_connection = self.dlg_readsql.findChild(QComboBox, 'cmb_connection')

        # Set Listeners
        self.dlg_readsql.dlg_closed.connect(partial(self._close_dialog_admin, self.dlg_readsql))

        # Set shortcut keys
        self.dlg_readsql.key_escape.connect(partial(tools_dr.close_dialog, self.dlg_readsql))

        self.message_update = ''
        self.error_count = 0

        # Set title
        window_title = f'Drain ({self.plugin_version})'
        self.dlg_readsql.setWindowTitle(window_title)

        tools_dr.open_dialog(self.dlg_readsql, 'admin_ui')

        self.init_dialog_create_project()

        self._open_form_create_gis_project()

    def _gis_create_project(self):
        """"""

        # Get gis folder, gis file, project type and schema
        gis_folder = tools_qt.get_text(self.dlg_readsql, 'txt_gis_folder')
        if gis_folder is None or gis_folder == 'null':
            msg = "GIS folder not set"
            tools_qgis.show_warning(msg)
            return

        gpkg_file = tools_qt.get_text(self.dlg_readsql, "txt_gis_gpkg")
        if gpkg_file is None or gpkg_file == 'null':
            msg = "GKPG file path name not set"
            tools_qgis.show_warning(msg)
            return

        tools_dr.set_config_parser('btn_admin', 'qgis_file_path', gis_folder, prefix=False)
        tools_dr.set_config_parser('btn_admin', 'gpkg_file_path', gpkg_file, prefix=False)

        gis_file = tools_qt.get_text(self.dlg_readsql, 'txt_gis_file')
        if gis_file is None or gis_file == 'null':
            msg = "GIS file name not set"
            tools_qgis.show_warning(msg)
            return

        # Generate QGIS project
        self._generate_qgis_project(gis_folder, gis_file, gpkg_file, self.project_epsg)

    def _generate_qgis_project(self, gis_folder, gis_file, gpkg_file, srid):
        """ Generate QGIS project """

        gis = DrGisFileCreate(self.plugin_dir)
        result, qgs_path = gis.gis_project_database(gis_folder, gis_file, gpkg_file, srid)
        self._close_dialog_admin(self.dlg_readsql)
        if result:
            self._open_project(qgs_path)

    def _open_project(self, qgs_path):
        """ Open a QGis project """

        project = QgsProject.instance()
        project.read(qgs_path)

        # Reload plugin
        file_name = os.path.basename(self.plugin_dir)
        reloadPlugin(f"{file_name}")

    def _open_form_create_gis_project(self):
        """"""

        # Set default values
        qgis_file_path = tools_dr.get_config_parser('btn_admin', 'qgis_file_path', "user", "session", prefix=False,
                                                    force_reload=True)
        if qgis_file_path is None:
            qgis_file_path = os.path.expanduser("~")
        tools_qt.set_widget_text(self.dlg_readsql, 'txt_gis_folder', qgis_file_path)
        gpkg_file_path = tools_dr.get_config_parser('btn_admin', 'gpkg_file_path', "user", "session", prefix=False,
                                                    force_reload=True)
        tools_qt.set_widget_text(self.dlg_readsql, 'txt_gis_gpkg', gpkg_file_path)

        # Set listeners
        self.dlg_readsql.btn_gis_folder.clicked.connect(
            partial(tools_qt.get_folder_path, self.dlg_readsql, "txt_gis_folder"))
        self.dlg_readsql.btn_gis_gpkg.clicked.connect(partial(self._select_file_gpkg))
        self.dlg_readsql.btn_qgis_accept.clicked.connect(partial(self._gis_create_project))
        self.dlg_readsql.btn_qgis_close.clicked.connect(partial(self._close_dialog_admin, self.dlg_readsql))
        self.dlg_readsql.dlg_closed.connect(partial(self._close_dialog_admin, self.dlg_readsql))

        # Set shortcut keys
        self.dlg_readsql.key_escape.connect(partial(tools_dr.close_dialog, self.dlg_readsql))

    def _close_dialog_admin(self, dlg):
        """ Close dialog """
        tools_dr.close_dialog(dlg, delete_dlg=False)

    def _update_locale(self):
        """"""
        # TODO: Class variable foder_locale is unused
        cmb_locale = tools_qt.get_combo_value(self.dlg_readsql, self.cmb_locale, 0)
        self.folder_locale = os.path.join(self.sql_dir, 'i18n', cmb_locale)

        if self.rdb_sample.isChecked():
            tools_qt.set_widget_text(self.dlg_readsql, self.filter_srid, '25831')
            self.txt_srid.setEnabled(False)
        else:
            if self.last_srid is not None:
                tools_qt.set_widget_text(self.dlg_readsql, self.filter_srid, self.last_srid)
            self.txt_srid.setEnabled(True)

    def _manage_srid(self):
        """ Manage SRID configuration """

        self.filter_srid = self.dlg_readsql.findChild(QLineEdit, 'srid_id')
        tools_qt.set_widget_text(self.dlg_readsql, self.filter_srid, '25831')
        self.txt_srid.setEnabled(False)
        self.tbl_srid = self.dlg_readsql.findChild(QTableView, 'tbl_srid')
        self.tbl_srid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_srid.clicked.connect(partial(self._set_selected_srid))

    def _set_selected_srid(self, index):

        model = self.tbl_srid.model()
        row = index.row()
        srid = model.data(model.index(row, 0), Qt.DisplayRole)
        tools_qt.set_widget_text(self.dlg_readsql, self.filter_srid, srid)

    def _filter_srid_changed(self):
        """"""
        filter_value = tools_qt.get_text(self.dlg_readsql, self.filter_srid)
        if filter_value == 'null':
            filter_value = ''
        sql = ("SELECT srid  as " + '"SRID"' + ",description as " + '"Description"' +
               "FROM srs WHERE CAST(srid AS TEXT) LIKE '" + str(filter_value))
        sql += "%' order by srs_id DESC"

        self.last_srids = self.gpkg_dao_config.get_rows(sql)
        self.model_srid = QStandardItemModel(self.tbl_srid)
        self.model_srid.setHorizontalHeaderLabels(['SRID', 'Description'])

        # Populate the model with the data from the SQL query
        for row in self.last_srids:
            srid_item = QStandardItem(str(row[0]))
            description_item = QStandardItem(row[1])
            self.model_srid.appendRow([srid_item, description_item])

        # Set the model for the QTableView
        self.tbl_srid.setModel(self.model_srid)
        self.tbl_srid.setColumnWidth(0, 100)
        self.tbl_srid.setColumnWidth(1, 300)
        self.tbl_srid.horizontalHeader().setStretchLastSection(True)

        if self.rdb_data.isChecked():
            self.last_srid = filter_value

    def _set_signals_create_project(self):
        """"""

        self.dlg_readsql.btn_gpkg_accept.clicked.connect(partial(self.create_project_data_schema))
        self.dlg_readsql.btn_gpkg_close.clicked.connect(
            partial(self._close_dialog_admin, self.dlg_readsql))
        self.cmb_locale.currentIndexChanged.connect(partial(self._update_locale))
        self.dlg_readsql.btn_push_path.clicked.connect(partial(self._select_path))
        self.filter_srid.textChanged.connect(partial(self._filter_srid_changed))

        # i18n
        self.dlg_readsql.btn_i18n.clicked.connect(partial(self._i18n_manager))
        self.dlg_readsql.btn_update_translation.clicked.connect(partial(self._update_translations))
        self.dlg_readsql.btn_translation.clicked.connect(partial(self._manage_translations))
        self.dlg_readsql.rdb_sample.clicked.connect(partial(self._update_locale))
        self.dlg_readsql.rdb_data.clicked.connect(partial(self._update_locale))

    def _manage_translations(self):
        """ Initialize the translation functionalities """

        qm_gen = DrI18NGenerator()
        qm_gen.init_dialog()

    def _update_translations(self):
        """ Initialize the translation functionalities """

        qm_i18n_up = DrSchemaI18NUpdate()
        qm_i18n_up.init_dialog()

    def _i18n_manager(self):
        """ Initialize the i18n functionalities """

        qm_i18n_manager = DrSchemaI18NManager()
        qm_i18n_manager.init_dialog()

    def _select_path(self):
        """ Select file path"""

        path = tools_qt.get_text(self.dlg_readsql, 'data_path')
        if path is None or path == '':
            path = self.plugin_dir

        if not os.path.exists(path):
            path = os.path.dirname(__file__)

        message = tools_qt.tr("Select GPKG path")
        file_path = QFileDialog.getExistingDirectory(None, message, path)
        if file_path is None or file_path == '':
            return
        self.dlg_readsql.data_path.setText(file_path)

    def _select_file_gpkg(self):
        """ Select GPKG file """

        file_gpkg = tools_qt.get_text(self.dlg_readsql, 'txt_gis_gpkg')
        # Set default value if necessary
        if file_gpkg is None or file_gpkg == '':
            file_gpkg = self.plugin_dir

        # Get directory of that file
        folder_path = os.path.dirname(file_gpkg)
        if not os.path.exists(folder_path):
            folder_path = os.path.dirname(__file__)
        os.chdir(folder_path)
        message = tools_qt.tr("Select GPKG file")
        file_gpkg, filter_ = QFileDialog.getOpenFileName(None, message, "", '*.gpkg')
        self.dlg_readsql.txt_gis_gpkg.setText(file_gpkg)

    def _execute_files(self, filedir):
        """"""

        if not os.path.exists(filedir):
            msg = "Folder not found: {0}"
            msg_params = (filedir,)
            tools_log.log_info(msg, msg_params=msg_params)
            return True

        msg = "Processing folder: {0}"
        msg_params = (filedir,)
        tools_log.log_info(msg, msg_params=msg_params)
        filelist = sorted(os.listdir(filedir))
        status = True

        if self.project_epsg:
            self.project_epsg = str(self.project_epsg).replace('"', '')
        else:
            msg = "There is no project selected or it is not valid. Please check the first tab..."
            tools_log.log_warning(msg)
        for file in filelist:
            if ".sql" in file:
                if "trg_delete" in file:
                    continue
                tools_log.log_info(os.path.join(filedir, file))
                self.current_sql_file += 1
                status = self._read_execute_file(os.path.join(filedir, file), self.project_epsg)
                if not status:
                    return False

        return status

    def create_schema_main_execution(self):
        """ Main common execution """

        msg = "Create schema: Executing function {0}"
        msg_params = ("calculate_number_of_files",)
        tools_log.log_info(msg, msg_params=msg_params)

        self.total_sql_files = self.calculate_number_of_files()

        msg = "Number of SQL files '{0}': {1}"
        msg_params = ("TOTAL", self.total_sql_files,)
        tools_log.log_info(msg, msg_params=msg_params)

        status = self.load_base(self.dict_folders_process['load_base'])
        return status

    def create_schema_custom_execution(self, config_dao=None):
        """ Custom execution """

        if self.rdb_sample.isChecked():
            msg = "Execute '{0}' (example data)"
            msg_params = ("load_sample_data",)
            tools_log.log_info(msg, msg_params=msg_params)
            tools_dr.set_config_parser('btn_admin', 'create_schema_type', 'rdb_sample', prefix=False)
            load_sample = self.load_sample_data()
            print(load_sample)
            if not load_sample:
                return
            print(self.populate_config_params())
            return self.populate_config_params()
        elif self.rdb_data.isChecked():
            msg = "Execute '{0}' (empty data)"
            msg_params = ("load_sample_data",)
            tools_log.log_info(msg, msg_params=msg_params)
            tools_dr.set_config_parser('btn_admin', 'create_schema_type', 'rdb_data', prefix=False)
            print(self.populate_config_params())
            return self.populate_config_params()

    def populate_config_params(self):
        """Populate table config_param_user"""

        sql_select = "SELECT columnname, vdefault, widgetcontrols FROM config_form_fields WHERE formtype = 'form_options'"
        rows = tools_db.get_rows(sql_select)
        print(f"rows-{rows}")

        if not rows:
            return False

        for row in rows:
            data = (row[0], row[1])
            sql_insert = "INSERT INTO config_param_user (parameter, value) VALUES (?,?)"
            try:
                tools_db.execute_sql_placeholder(sql_insert, data)

                # Add include widget for outlayer and raster symbology
                if row[2] is not None:
                    widgetcontrols = json.loads(row[2])
                    if "include_widget" in widgetcontrols and widgetcontrols.get('include_widget'):
                        tools_db.execute_sql_placeholder(sql_insert, (row[0] + '_include', '1'))
                    elif "include_widget" in widgetcontrols and not widgetcontrols.get('include_widget'):
                        tools_db.execute_sql_placeholder(sql_insert, (row[0] + '_include', '0'))
            except Exception:
                msg = "Error executing SQL: {0}\nDatabase error: {1}"
                msg_params = (sql_insert, global_vars.gpkg_dao_data.last_error,)
                tools_log.log_warning(msg, msg_params=msg_params)
                tools_qt.show_info_box(msg)
                return False

        self.populate_project_params()

        return True

    def populate_project_params(self):
        """Populate project params in config_param_user"""

        for key, value in self.project_params.items():
            sql = f"UPDATE config_param_user SET value = '{value}' WHERE parameter='{key}'"
            try:
                global_vars.gpkg_dao_data.execute_sql(sql)
            except Exception:
                msg = "Error executing SQL: {0}\nDatabase error: {1}"
                msg_params = (sql, global_vars.gpkg_dao_data.last_error,)
                tools_log.log_warning(msg, msg_params=msg_params)
                tools_qt.show_info_box(msg)
                return False

    def create_gpkg(self):
        """ Create Geopackage """

        gpkg_name = self.gpkg_name
        path = self.project_path

        self.gpkg_full_path = path + "/" + gpkg_name + ".gpkg"
        if os.path.exists(self.gpkg_full_path):
            msg = "Geopackage already exists."
            tools_log.log_warning(msg, parameter=self.gpkg_full_path)
            return False

        driver = gdal.GetDriverByName('GPKG')
        dataset = driver.Create(self.gpkg_full_path, 0, 0, 0, gdal.GDT_Unknown)
        del dataset
        return True

    def calculate_number_of_files(self):
        """ Calculate total number of SQL to execute """

        total_sql_files = 0
        dict_process = {}
        list_process = ['load_base']

        for process_name in list_process:
            msg = "Create schema: Executing function {0}"
            msg_params = (f"get_number_of_files_process('{process_name}')",)
            tools_log.log_info(msg, msg_params=msg_params)
            dict_folders, total = self.get_number_of_files_process(process_name)
            total_sql_files += total
            msg = "Number of SQL files '{0}': {1}"
            msg_params = (process_name, total,)
            tools_log.log_info(msg, msg_params=msg_params)
            dict_process[process_name] = total
            self.dict_folders_process[process_name] = dict_folders

        return total_sql_files

    def get_number_of_files_process(self, process_name: str):
        """ Calculate number of files of all folders of selected @process_name """

        msg = "Create schema: Executing function {0}"
        msg_params = (f"get_folders_process('{process_name}')",)
        tools_log.log_info(msg, msg_params=msg_params)
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
            dict_folders[os.path.join(self.folder_software, self.file_pattern_sys_gpkg)] = 0
            dict_folders[os.path.join(self.folder_software, self.file_pattern_ddl)] = 0
            dict_folders[os.path.join(self.folder_software, self.file_pattern_dml)] = 0
            dict_folders[os.path.join(self.folder_software, self.file_pattern_trg)] = 0

        return dict_folders

    def _manage_result_message(self, status, msg_ok=None, msg_error=None, parameter=None):
        """ Manage message depending result @status """

        if status:
            if msg_ok is None:
                msg_ok = "Process finished successfully"
            tools_qgis.show_info(msg_ok, parameter=parameter, dialog=self.dlg_readsql)
        else:
            if msg_error is None:
                msg_error = "Process finished with some errors"
            tools_qgis.show_warning(msg_error, parameter=parameter, dialog=self.dlg_readsql)

    def _select_active_locales(self):

        sql = "SELECT locale as id, name as idval FROM locales WHERE active = 1"
        rows = self.gpkg_dao_config.get_rows(sql)
        return rows

    def _on_timer_timeout(self):
        # Update timer
        elapsed_time = time.time() - self.t0
        text = str(datetime.timedelta(seconds=round(elapsed_time)))
        self.dlg_readsql.lbl_time.setText(text)


class DrRptGpkgCreate(DrGpkgBase):
    """Class to handle report geopackage creation"""

    def __init__(self, gpkg_name, project_path):
        super().__init__()
        self.gpkg_name = gpkg_name
        self.project_path = project_path
        self.gpkg_full_path = None

    def create_rpt_gpkg(self):
        """Create and initialize the report geopackage"""

        # Create the geopackage file
        self.gpkg_full_path = os.path.join(self.project_path, f"{self.gpkg_name}.gpkg")
        if os.path.exists(self.gpkg_full_path):
            msg = "Report geopackage already exists."
            tools_log.log_warning(msg, parameter=self.gpkg_full_path)
            return False

        driver = gdal.GetDriverByName('GPKG')
        dataset = driver.Create(self.gpkg_full_path, 0, 0, 0, gdal.GDT_Unknown)
        del dataset

        # Initialize database connection
        if not self._check_database_connection(self.gpkg_full_path, self.gpkg_name):
            return False

        # Execute SQL files
        status = self._execute_sql_files()
        if not status:
            return False

        # Create triggers
        self._execute_trg_creation()

        return True

    def _execute_sql_files(self):
        """Execute SQL files from rpt_gpkg directory"""

        rpt_gpkg_dir = os.path.join(self.sql_dir, "rpt_gpkg")
        if not os.path.exists(rpt_gpkg_dir):
            msg = "Report GPKG directory not found: {0}"
            msg_params = (rpt_gpkg_dir,)
            tools_log.log_info(msg, msg_params=msg_params)
            return False

        # Execute files in order: ddl.sql first, then dml.sql
        sql_files = ['ddl.sql', 'dml.sql']
        for sql_file in sql_files:
            file_path = os.path.join(rpt_gpkg_dir, sql_file)
            if not os.path.exists(file_path):
                msg = "SQL file not found: {0}"
                msg_params = (file_path,)
                tools_log.log_info(msg, msg_params=msg_params)
                continue

            status = self._read_execute_file(file_path, global_vars.data_epsg)
            if not status:
                return False

        return True
