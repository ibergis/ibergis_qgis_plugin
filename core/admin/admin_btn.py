"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QFileDialog, QTableView, QAbstractItemView
from osgeo import gdal
from sip import isdeleted
from time import time
from datetime import timedelta

from qgis.PyQt.QtCore import QDate
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QRadioButton, QLineEdit, QComboBox, QLabel
from qgis.core import QgsProject
from qgis.utils import reloadPlugin

from .gis_file_create import GwGisFileCreate
from ..ui.ui_manager import GwAdminUi, GwAdminDbProjectUi, GwAdminGisProjectUi
from ..utils import tools_gw
from ... import global_vars
from ...lib import tools_qt, tools_qgis, tools_log, tools_db, tools_os, tools_gpkgdao
from ..ui.docker import GwDocker


class GwAdminButton:

    def __init__(self):
        """ Class to control toolbar 'om_ws' """

        # Initialize instance attributes
        self.gpkg_full_path = None
        self.dict_folders_process =  {}
        self.iface = global_vars.iface
        self.settings = global_vars.giswater_settings
        self.plugin_dir = global_vars.plugin_dir
        self.schema_name = global_vars.schema_name
        self.plugin_version, self.message = tools_qgis.get_plugin_version()
        self.canvas = global_vars.canvas
        self.project_type = None
        self.project_epsg = None
        self.gpkg_name = None
        self.project_path = None
        self.dlg_readsql = None
        self.dlg_info = None
        self.dlg_readsql_create_project = None
        self.project_type_selected = None
        self.schema_type = None
        self.form_enabled = True
        self.total_sql_files = 0    # Total number of SQL files to process
        self.current_sql_file = 0   # Current number of SQL file
        self.progress_value = 0     # (current_sql_file / total_sql_files) * 100
        self.progress_ratio = 0.8   # Ratio to apply to 'progress_value'
        self.gpkg_dao = None
        self.gpkg = None


    def init_sql(self, set_database_connection=False, username=None, show_dialog=True):
        """ Button 100: Execute SQL. Info show info """

        # Connect to sqlite database
        self.gpkg_dao = tools_gpkgdao.GwGpkgDao()



        # Set label status connection
        self.icon_folder = f"{self.plugin_dir}{os.sep}icons{os.sep}dialogs{os.sep}20x20{os.sep}"
        self.status_ok = QPixmap(f"{self.icon_folder}status_ok.png")
        self.status_ko = QPixmap(f"{self.icon_folder}status_ko.png")
        self.status_no_update = QPixmap(f"{self.icon_folder}status_not_updated.png")

        # Create the dialog and signals
        self._init_show_database()
        self._info_show_database(username=username, show_dialog=show_dialog)



    def create_project_data_schema(self):
        """"""
        gpkg_name = tools_qt.get_text(self.dlg_readsql_create_project, 'gpkg_name', return_string_null=False)
        project_path = tools_qt.get_text(self.dlg_readsql_create_project, 'data_path', return_string_null=False)
        project_srid = tools_qt.get_text(self.dlg_readsql_create_project, 'srid_id')
        project_locale = tools_qt.get_combo_value(self.dlg_readsql_create_project, self.cmb_locale, 0)


        if not gpkg_name or not project_path:
            tools_qt.show_info_box("Please fill all empty fields.")
            return

        # Set class variables
        self.gpkg_name = gpkg_name
        self.project_path = project_path
        self.schema_type = 'dev'
        self.project_epsg = project_srid
        self.locale = project_locale

        # Save in settings
        locale = tools_qt.get_combo_value(self.dlg_readsql_create_project, self.cmb_locale, 0)
        tools_gw.set_config_parser('btn_admin', 'project_locale', f'{locale}', prefix=False)

        msg = "This process will take time (few minutes). Are you sure to continue?"
        title = "Create example"
        answer = tools_qt.show_question(msg, title)
        if not answer:
            return

        #Check if srid value is valid
        if self.last_srids is None:
            msg = "This SRID value does not exist on Database. Please select a diferent one."
            tools_qt.show_info_box(msg, "Info")
            return

        tools_log.log_info(f"Creating GPKG {self.gpkg_name}'")

        tools_log.log_info(f"'Create schema' execute function 'def create_gpkg'")
        self.create_gpkg()
        tools_log.log_info(f"'Create schema' execute function 'def _check_database_connection'")
        connection_status = self._check_database_connection(self.gpkg_full_path)
        if not connection_status:
            tools_log.log_info("Function _check_database_connection returned False")
            return
        tools_log.log_info(f"'Create schema' execute function 'def main_execution'")
        status = self.create_schema_main_execution()

        if not status:
            tools_log.log_info("Function main_execution returned False")
            return

        tools_log.log_info(f"'Create schema' execute function 'def custom_execution'")
        status_custom = self.create_schema_custom_execution()

        if not status_custom:
            tools_log.log_info("Function custom_execution returned False")
            return
        else:
            tools_qt.show_info_box("Geopackage created successfully.")


    def manage_process_result(self, is_test=False, is_utils=False, dlg=None):
        """"""

        status = (self.error_count == 0)
        self._manage_result_message(status, parameter="Create project")
        if status:
            if is_utils is False:
                self._close_dialog_admin(self.dlg_readsql_create_project)
            # Reset count error variable to 0
            self.error_count = 0
            tools_qt.show_exception_message(msg=global_vars.session_vars['last_error_msg'])
            tools_qgis.show_info("A rollback on schema will be done.")
            if dlg:
                tools_gw.close_dialog(dlg)


    def execute_last_process(self, new_project=False, schema_name=None, schema_type='', locale=False, srid=None):
        """ Execute last process function """

        if new_project is True:
            extras = '"isNewProject":"' + str('TRUE') + '", '
        else:
            extras = '"isNewProject":"' + str('FALSE') + '", '
        extras += '"gwVersion":"' + str(self.plugin_version) + '", '
        extras += '"projectType":"' + str(schema_type).upper() + '", '
        if srid is None:
            srid = self.project_epsg
        extras += '"epsg":' + str(srid).replace('"', '')
        if new_project is True:
            if str(self.descript) != 'null':
                extras += ', ' + '"descript":"' + str(self.descript) + '"'
            extras += ', ' + '"name":"' + str(schema_name) + '"'
            extras += ', ' + '"author":"' + str(self.username) + '"'
            current_date = QDate.currentDate().toString('dd-MM-yyyy')
            extras += ', ' + '"date":"' + str(current_date) + '"'

        self.schema_name = schema_name

        # Get current locale
        if not locale:
            locale = tools_qt.get_combo_value(self.dlg_readsql_create_project, self.cmb_locale, 0)

        client = '"client":{"device":4, "lang":"' + str(locale) + '"}, '
        data = '"data":{' + extras + '}'
        body = "$${" + client + data + "}$$"
        result = tools_gw.execute_procedure('gw_fct_admin_schema_lastprocess', body, self.schema_name, commit=False)
        if result is None or ('status' in result and result['status'] == 'Failed'):
            self.error_count = self.error_count + 1

        return result

    def init_dialog_create_project(self, project_type=None):
        """ Initialize dialog (only once) """

        self.dlg_readsql_create_project = GwAdminDbProjectUi()
        tools_gw.load_settings(self.dlg_readsql_create_project)

        # Find Widgets in form
        self.rdb_sample = self.dlg_readsql_create_project.findChild(QRadioButton, 'rdb_sample')
        self.rdb_data = self.dlg_readsql_create_project.findChild(QRadioButton, 'rdb_data')


        # TODO: do and call listener for buton + table -> temp_csv
        # Manage SRID
        self._manage_srid()

        # Get combo locale
        self.cmb_locale = self.dlg_readsql_create_project.findChild(QComboBox, 'cmb_locale')

        # Populate combo with all locales
        filename = "config.gpkg"
        db_filepath = f"{global_vars.plugin_dir}{os.sep}samples{os.sep}{filename}"
        tools_log.log_info(db_filepath)
        if os.path.exists(db_filepath):
            status = self.gpkg_dao.init_db(db_filepath)
            if status:
                list_locale = self._select_active_locales()
                tools_qt.fill_combo_values(self.cmb_locale, list_locale, 1)
                locale = tools_gw.get_config_parser('btn_admin', 'project_locale', 'user', 'session', False,
                                                    force_reload=True)
                tools_qt.set_combo_value(self.cmb_locale, locale, 0)
            else:
                msg = self.gpkg_dao.last_error
                tools_log.log_warning(msg)
        else:
            tools_log.log_warning(f"Database not found: {db_filepath}")

        # Set shortcut keys
        self.dlg_readsql_create_project.key_escape.connect(
            partial(tools_gw.close_dialog, self.dlg_readsql_create_project, False))

        # Populate tbl_srid
        self._filter_srid_changed()

        # Set signals
        self._set_signals_create_project()


    # region 'Create Project'

    def load_base(self, dict_folders):
        """"""

        for folder in dict_folders.keys():
            status = self._execute_files(folder, set_progress_bar=True)
            if not status and self.dev_commit is False:
                return False

        return True


    def load_locale(self):

        if self._process_folder(self.folder_locale) is False:
            folder_locale = os.path.join(self.sql_dir, 'i18n', 'en_US')
            if self._process_folder(folder_locale) is False:
                return False
            else:
                status = self._execute_files(folder_locale, True, set_progress_bar=True)
                if status is False and self.dev_commit is False:
                    return False
        else:
            status = self._execute_files(self.folder_locale, True, set_progress_bar=True)
            if status is False and self.dev_commit is False:
                return False

        return True


    def load_sample_data(self, project_type="dev"):

        #global_vars.dao.commit()
        folder_example = os.path.join(self.sql_dir, "example")
        status = self._execute_files(folder_example, set_progress_bar=True)
        if not status and self.dev_commit is False:
            return False

        return True

    # endregion


    # region private functions

    def _init_show_database(self):
        """ Initialization code of the form (to be executed only once) """

        # Get SQL folder and check if exists
        self.sql_dir = os.path.normpath(os.path.join(global_vars.plugin_dir, 'dbmodel'))
        if not os.path.exists(self.sql_dir):
            tools_qgis.show_message(f"SQL folder not found: {self.sql_dir}")
            return

        self.project_version = '0'

        # Get locale of QGIS application
        self.locale = tools_qgis.get_locale()

        # Declare all file variables
        self.file_pattern_ddl = "ddl"
        self.file_pattern_dml = "dml"
        self.file_pattern_rtree = "rtree"
        self.file_pattern_sys_gpkg = "sys_gpkg"
        self.file_pattern_trg = "trg"

        # Declare all folders
        if self.schema_name is not None and self.project_type is not None:
            self.folder_software = os.path.join(self.sql_dir, self.project_type)
        else:
            # self.folder_software = ""
            self.folder_software = os.path.join(self.sql_dir, "dev")

        # Check if user have commit permissions
        self.dev_commit = tools_gw.get_config_parser('system', 'dev_commit', "project", "dev", False, force_reload=True)
        self.dev_commit = tools_os.set_boolean(self.dev_commit)

        # Create dialog object
        self.dlg_readsql = GwAdminUi()
        tools_gw.load_settings(self.dlg_readsql)

        # Get widgets form
        self.cmb_connection = self.dlg_readsql.findChild(QComboBox, 'cmb_connection')

        # Set Listeners
        self._set_signals()

        # Set shortcut keys
        self.dlg_readsql.key_escape.connect(partial(tools_gw.close_dialog, self.dlg_readsql))

    def _set_signals(self):
        """ Set signals. Function has to be executed only once (during form initialization) """

        self.dlg_readsql.btn_close.clicked.connect(partial(self._close_dialog_admin, self.dlg_readsql))
        self.dlg_readsql.btn_schema_create.clicked.connect(partial(self._open_create_project))
        #self.cmb_connection.currentIndexChanged.connect(partial(self._event_change_connection))
        #self.cmb_connection.currentIndexChanged.connect(partial(self._set_info_project))
        self.dlg_readsql.btn_gis_create.clicked.connect(partial(self._open_form_create_gis_project))
        self.dlg_readsql.dlg_closed.connect(partial(self._save_custom_sql_path, self.dlg_readsql))
        self.dlg_readsql.dlg_closed.connect(partial(self._close_dialog_admin, self.dlg_readsql))


    def _info_show_database(self, connection_status=True, username=None, show_dialog=False):
        """"""

        self.message_update = ''
        self.error_count = 0
        self.schema = None

        # Get database connection user and role
        self.username = username


        # Set title
        window_title = f'Drain ({self.plugin_version})'
        self.dlg_readsql.setWindowTitle(window_title)

        self.form_enabled = True
        message = ''

        if connection_status is False:
            self.form_enabled = False
            message = 'There is an error in the configuration of the pgservice file, ' \
                      'please check it or consult your administrator'
            ignore_widgets =  ['cmb_connection', 'btn_gis_create', 'cmb_project_type', 'project_schema_name']
            tools_qt.enable_dialog(self.dlg_readsql, False, ignore_widgets)
            self.dlg_readsql.lbl_status.setPixmap(self.status_ko)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_status_text', message)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_schema_name', '')
            self.dlg_readsql.btn_gis_create.setEnabled(False)
            self._manage_docker()
            return

        elif connection_status is False:
            self.form_enabled = False
            msg = "Connection Failed. Please, check connection parameters"
            tools_qgis.show_message(msg, 1)
            tools_qt.enable_dialog(self.dlg_readsql, False, 'cmb_connection')
            self.dlg_readsql.lbl_status.setPixmap(self.status_ko)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_status_text', msg)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_schema_name', '')
            self._manage_docker()
            return

        if not tools_db.check_role(self.username, is_admin=True) and not show_dialog:
            tools_log.log_warning(f"User not found: {self.username}")
            return

        if self.form_enabled is False:
            ignore_widgets =  ['cmb_connection', 'btn_gis_create', 'cmb_project_type', 'project_schema_name']
            tools_qt.enable_dialog(self.dlg_readsql, False, ignore_widgets)
            self.dlg_readsql.lbl_status.setPixmap(self.status_ko)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_status_text', message)
            tools_qt.set_widget_text(self.dlg_readsql, 'lbl_schema_name', '')

        if show_dialog:
            self._manage_docker()


    def _gis_create_project(self):
        """"""

        # Get gis folder, gis file, project type and schema
        gis_folder = tools_qt.get_text(self.dlg_create_gis_project, 'txt_gis_folder')
        if gis_folder is None or gis_folder == 'null':
            tools_qgis.show_warning("GIS folder not set")
            return

        qgis_file_type = self.dlg_create_gis_project.cmb_roletype.currentIndex()
        tools_gw.set_config_parser('btn_admin', 'qgis_file_type', qgis_file_type, prefix=False)
        tools_gw.set_config_parser('btn_admin', 'qgis_file_path', gis_folder, prefix=False)
        qgis_file_export = self.dlg_create_gis_project.chk_export_passwd.isChecked()
        tools_gw.set_config_parser('btn_admin', 'qgis_file_export', qgis_file_export, prefix=False)

        gis_file = tools_qt.get_text(self.dlg_create_gis_project, 'txt_gis_file')
        if gis_file is None or gis_file == 'null':
            tools_qgis.show_warning("GIS file name not set")
            return

        project_type = tools_qt.get_text(self.dlg_readsql, 'cmb_project_type')
        schema_name = tools_qt.get_text(self.dlg_readsql, 'project_schema_name')

        # Get roletype and export password
        roletype = tools_qt.get_text(self.dlg_create_gis_project, 'cmb_roletype')
        export_passwd = tools_qt.is_checked(self.dlg_create_gis_project, 'chk_export_passwd')

        if export_passwd:
            msg = "Credentials will be stored in GIS project file"
            tools_qt.show_info_box(msg, "Warning")

        # Generate QGIS project
        self._generate_qgis_project(gis_folder, gis_file, project_type, schema_name, export_passwd, roletype)


    def _generate_qgis_project(self, gis_folder, gis_file, project_type, schema_name, export_passwd, roletype):
        """ Generate QGIS project """

        gis = GwGisFileCreate(self.plugin_dir)
        result, qgs_path = gis.gis_project_database(gis_folder, gis_file, project_type, schema_name, export_passwd,
                                                    roletype)

        self._close_dialog_admin(self.dlg_create_gis_project)
        self._close_dialog_admin(self.dlg_readsql)
        if result:
            self._open_project(qgs_path)


    def _open_project(self, qgs_path):
        """ Open a QGis project """

        project = QgsProject.instance()
        project.read(qgs_path)

        # Load Giswater plugin
        file_name = os.path.basename(self.plugin_dir)
        reloadPlugin(f"{file_name}")


    def _open_form_create_gis_project(self):
        """"""

        # Check if exist schema
        # schema_name = tools_qt.get_text(self.dlg_readsql, 'project_schema_name')
        # if schema_name is None:
        #     msg = "In order to create a qgis project you have to create a schema first ."
        #     tools_qt.show_info_box(msg)
        #     return

        # Create GIS project dialog
        self.dlg_create_gis_project = GwAdminGisProjectUi()
        tools_gw.load_settings(self.dlg_create_gis_project)

        # Set default values
        qgis_file_type = tools_gw.get_config_parser('btn_admin', 'qgis_file_type', "user", "session", prefix=False,
                                                    force_reload=True)
        if qgis_file_type is not None:
            try:
                qgis_file_type = int(qgis_file_type)
                self.dlg_create_gis_project.cmb_roletype.setCurrentIndex(qgis_file_type)
            except Exception:
                pass
        # schema_name = tools_qt.get_text(self.dlg_readsql, self.dlg_readsql.project_schema_name)
        # tools_qt.set_widget_text(self.dlg_create_gis_project, 'txt_gis_file', schema_name)
        qgis_file_path = tools_gw.get_config_parser('btn_admin', 'qgis_file_path', "user", "session", prefix=False,
                                                    force_reload=True)
        if qgis_file_path is None:
            qgis_file_path = os.path.expanduser("~")
        tools_qt.set_widget_text(self.dlg_create_gis_project, 'txt_gis_folder', qgis_file_path)
        qgis_file_export = tools_gw.get_config_parser('btn_admin', 'qgis_file_export', "user", "session", prefix=False,
                                                      force_reload=True)
        qgis_file_export = tools_os.set_boolean(qgis_file_export, False)
        self.dlg_create_gis_project.chk_export_passwd.setChecked(qgis_file_export)


        # Set listeners
        self.dlg_create_gis_project.btn_gis_folder.clicked.connect(
            partial(tools_qt.get_folder_path, self.dlg_create_gis_project, "txt_gis_folder"))
        self.dlg_create_gis_project.btn_accept.clicked.connect(partial(self._gis_create_project))
        self.dlg_create_gis_project.btn_close.clicked.connect(partial(self._close_dialog_admin, self.dlg_create_gis_project))
        self.dlg_create_gis_project.dlg_closed.connect(partial(self._close_dialog_admin, self.dlg_create_gis_project))

        # Set shortcut keys
        self.dlg_create_gis_project.key_escape.connect(partial(tools_gw.close_dialog, self.dlg_create_gis_project))

        # Open MainWindow
        tools_gw.open_dialog(self.dlg_create_gis_project, dlg_name='admin_gisproject')


    def _btn_constrains_changed(self, button, call_function=False):
        """"""

        lbl_constrains_info = self.dlg_readsql.findChild(QLabel, 'lbl_constrains_info')

        if button.text() == 'OFF':
            button.setText("ON")
            lbl_constrains_info.setText('(Constrains enabled)  ')
            if call_function:
                # Enable constrains
                sql = 'SELECT gw_fct_admin_manage_ct($${"client":{"lang":"ES"}, "data":{"action":"ADD"}}$$)'
                tools_db.execute_sql(sql)

        elif button.text() == 'ON':
            button.setText("OFF")
            lbl_constrains_info.setText('(Constrains dissabled)')
            if call_function:
                # Disable constrains
                sql = 'SELECT gw_fct_admin_manage_ct($${"client":{"lang":"ES"}, "data":{"action":"DROP"}}$$)'
                tools_db.execute_sql(sql)


    def _load_sql(self, path_folder, no_ct=False, utils_schema_name=None, set_progress_bar=False):
        """"""

        for (path, ficheros, archivos) in os.walk(path_folder):
            status = self._execute_files(path, no_ct=no_ct, utils_schema_name=utils_schema_name,
                                         set_progress_bar=set_progress_bar)
            if not status:
                return False

        return True


    """ Functions execute process """

    def _bk_schema_name(self, list_schemas, project_name, i):
        """ Check for available bk schema name """

        if f"{project_name}{i}" not in list_schemas:
            return f"{project_name}{i}"
        else:
            return self._bk_schema_name(list_schemas, project_name, i + 1)


    def _close_dialog_admin(self, dlg):
        """ Close dialog """
        tools_gw.close_dialog(dlg, delete_dlg=False)
        self.schema = None


    def _update_locale(self):
        """"""
        # TODO: Check this!
        cmb_locale = tools_qt.get_combo_value(self.dlg_readsql, self.cmb_locale, 0)
        self.folder_locale = os.path.join(self.sql_dir, 'i18n', cmb_locale)



    def _populate_data_schema_name(self, widget):
        """"""

        # Get filter
        filter_ = tools_qt.get_text(self.dlg_readsql, widget)
        if filter_ in (None, 'null') and self.schema_type:
            filter_ = self.schema_type
        if filter_ is None:
            return
        # Populate Project data schema Name
        sql = "SELECT schema_name FROM information_schema.schemata"
        rows = tools_db.get_rows(sql)
        if rows is None:
            return

        result_list = []
        for row in rows:
            sql = (f"SELECT EXISTS (SELECT * FROM information_schema.tables "
                   f"WHERE table_schema = '{row[0]}' "
                   f"AND table_name = 'sys_version')")
            exists = tools_db.get_row(sql)
            if exists and str(exists[0]) == 'True':
                sql = f"SELECT project_type FROM {row[0]}.sys_version"
                result = tools_db.get_row(sql)
                if result is not None and result[0] == filter_.upper():
                    elem = [row[0], row[0]]
                    result_list.append(elem)
        if not result_list:
            self.dlg_readsql.project_schema_name.clear()
            return

        tools_qt.fill_combo_values(self.dlg_readsql.project_schema_name, result_list, 1)

    def _manage_srid(self):
        """ Manage SRID configuration """

        self.filter_srid = self.dlg_readsql_create_project.findChild(QLineEdit, 'srid_id')
        tools_qt.set_widget_text(self.dlg_readsql_create_project, self.filter_srid, '25831')
        self.tbl_srid = self.dlg_readsql_create_project.findChild(QTableView, 'tbl_srid')
        self.tbl_srid.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.model_srid = QSqlQueryModel()
        # self.tbl_srid.setModel(self.model_srid)
        self.tbl_srid.clicked.connect(partial(self._set_selected_srid))

    def _set_selected_srid(self, index):
        model = self.tbl_srid.model()
        row = index.row()
        srid = model.data(model.index(row, 0), Qt.DisplayRole)
        tools_qt.set_widget_text(self.dlg_readsql_create_project, self.filter_srid, srid)

        # selected_list = self.tbl_srid.selectionModel().selectedRows()
        # selected_row = selected_list[0].row()
        # srid = self.tbl_srid.model().record(selected_row).value("SRID")
        # tools_qt.set_widget_text(self.dlg_readsql_create_project, self.filter_srid, srid)


    def _filter_srid_changed(self):
        """"""

        filter_value = tools_qt.get_text(self.dlg_readsql_create_project, self.filter_srid)
        if filter_value == 'null':
            filter_value = ''
        sql = ("SELECT srid  as " + '"SRID"' + ",description as " + '"Description"' +
                "FROM srs WHERE CAST(srid AS TEXT) LIKE '" + str(filter_value))

        sql += "%' order by srs_id DESC"

        self.last_srids = self.gpkg_dao.get_rows(sql);


        print("ROWS: ", self.last_srids)

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

    def _set_info_project(self):
        """"""

        if self.form_enabled is False:
            return

        # set variables from table version
        schema_name = tools_qt.get_text(self.dlg_readsql, self.dlg_readsql.project_schema_name)

        self.postgresql_version = tools_db.get_pg_version()
        self.postgis_version = tools_db.get_postgis_version()

        if schema_name == 'null':
            tools_qt.enable_tab_by_tab_name(self.dlg_readsql.tab_main, "others", False)

            msg = (f'Database version: {self.postgresql_version}\n'
                   f'PostGis version: {self.postgis_version}\n \n')
            self.software_version_info.setText(msg)

        else:
            dict_info = tools_gw.get_project_info(schema_name)
            self.project_type = dict_info['project_type']
            self.project_epsg = dict_info['project_epsg']
            self.project_version = dict_info['project_version']
            self.project_language = dict_info['project_language']

            msg = (f'Database version: {self.postgresql_version}\n'
                   f'PostGis version: {self.postgis_version}\n \n'
                   f'Schema name: {schema_name}\n'
                   f'Version: {self.project_version}\n'
                   f'EPSG: {self.project_epsg}\n'
                   f'Language: {self.project_language}\n')

            self.software_version_info.setText(msg)

            # Set label schema name
            self.lbl_schema_name.setText(str(schema_name))

        # Update windowTitle
        window_title = f'Giswater ({self.plugin_version})'
        self.dlg_readsql.setWindowTitle(window_title)

        if schema_name == 'null' and self.form_enabled:
            tools_qt.set_widget_text(self.dlg_readsql, self.dlg_readsql.lbl_status_text, '')
            tools_qt.set_widget_text(self.dlg_readsql, self.dlg_readsql.lbl_schema_name, '')
        elif str(self.plugin_version) > str(self.project_version) and self.form_enabled:
            self.dlg_readsql.lbl_status.setPixmap(self.status_no_update)
            tools_qt.set_widget_text(self.dlg_readsql, self.dlg_readsql.lbl_status_text,
                                     '(Schema version is lower than plugin version, please update schema)')
            self.dlg_readsql.btn_info.setEnabled(True)
        elif str(self.plugin_version) < str(self.project_version) and self.form_enabled:
            self.dlg_readsql.lbl_status.setPixmap(self.status_no_update)
            tools_qt.set_widget_text(self.dlg_readsql, self.dlg_readsql.lbl_status_text,
                                     '(Schema version is higher than plugin version, please update plugin)')
            self.dlg_readsql.btn_info.setEnabled(False)
        elif self.form_enabled:
            self.dlg_readsql.lbl_status.setPixmap(self.status_ok)
            tools_qt.set_widget_text(self.dlg_readsql, self.dlg_readsql.lbl_status_text, '')
            self.dlg_readsql.btn_info.setEnabled(False)


    def _process_folder(self, folderpath, filepattern=''):
        """"""

        try:
            os.listdir(os.path.join(folderpath, filepattern))
            return True
        except Exception:
            return False


    def _set_signals_create_project(self):
        """"""

        self.dlg_readsql_create_project.btn_accept.clicked.connect(partial(self.create_project_data_schema))
        self.dlg_readsql_create_project.btn_close.clicked.connect(
            partial(self._close_dialog_admin, self.dlg_readsql_create_project))
        self.cmb_locale.currentIndexChanged.connect(partial(self._update_locale))
        self.dlg_readsql_create_project.btn_push_path.clicked.connect(partial(self._select_path))
        self.filter_srid.textChanged.connect(partial(self._filter_srid_changed))



    def _open_create_project(self):
        """"""

        # Create dialog and signals
        if self.dlg_readsql_create_project is None:
            self.init_dialog_create_project()

        # Open dialog
        self.dlg_readsql_create_project.setWindowTitle(f"Create new Geopackage")
        tools_gw.open_dialog(self.dlg_readsql_create_project, dlg_name='admin_dbproject')

    def _select_path(self):
        """ Select file path"""

        path = tools_qt.get_text(self.dlg_readsql_create_project, 'data_file')
        if path is None or path == '':
            path = self.plugin_dir

        if not os.path.exists(path):
            folder_path = os.path.dirname(__file__)

        message = tools_qt.tr("Select GPKG path")
        file_path = QFileDialog.getExistingDirectory(None, message)
        self.dlg_readsql_create_project.data_path.setText(file_path)

    def _execute_files(self, filedir, i18n=False, no_ct=False, set_progress_bar=False):
        """"""

        if not os.path.exists(filedir):
            tools_log.log_info(f"Folder not found: {filedir}")
            return True

        tools_log.log_info(f"Processing folder: {filedir}")
        filelist = sorted(os.listdir(filedir))

        status = True

        if self.project_epsg:
            self.project_epsg = str(self.project_epsg).replace('"', '')
        else:
            msg = "There is no project selected or it is not valid. Please check the first tab..."
            tools_log.log_warning(msg)
        for file in filelist:
            if ".sql" in file:
                if (no_ct is True and "tablect.sql" not in file) or no_ct is False:
                    tools_log.log_info(os.path.join(filedir, file))
                    self.current_sql_file += 1
                    status = self._read_execute_file(filedir, file, self.project_epsg)
                    print("PROJECT EPSG 2: ",self.project_epsg)
                    if not status and self.dev_commit is False:
                        return False

        return status


    def _read_execute_file(self, filedir, file, project_epsg):
        """"""
        status = False
        f = None
        try:
            filepath = os.path.join(filedir, file)
            f = open(filepath, 'r', encoding="utf8")
            if f:
                f_to_read = str(f.read().replace("SRID_VALUE", self.project_epsg))
                status = self.gpkg_dao.execute_script_sql(str(f_to_read))
                tools_log.log_info(f"LAST ERROR: ,{self.gpkg_dao.last_error}")
                if status is False:
                    self.error_count = self.error_count + 1
                    tools_log.log_info(f"_read_execute_file error {filepath}")
                    tools_log.log_info(f"Message: {global_vars.session_vars['last_error']}")
                    if self.dev_commit is False:
                        global_vars.dao.rollback()
                    return False

        except Exception as e:
            self.error_count = self.error_count + 1
            tools_log.log_info(f"_read_execute_file exception: {file}")
            tools_log.log_info(str(e))
            if self.dev_commit is False:
                global_vars.dao.rollback()
            status = False

        finally:
            if f:
                f.close()
            return status

    def create_schema_main_execution(self):
        """ Main common execution """

        self.progress_ratio = 0.8
        tools_log.log_info(f"Task 'Create schema' execute function 'def calculate_number_of_files'")
        self.total_sql_files = self.calculate_number_of_files()
        tools_log.log_info(f"Number of SQL files 'TOTAL': {self.total_sql_files}")

        status = self.load_base(self.dict_folders_process['load_base'])
        if not status and self.dev_commit is False:
            return False

        status = True

        if not status and self.dev_commit is False:
            return False

        return True


    def create_schema_custom_execution(self):
        """ Custom execution """

        # example_data = self.params['example_data']

        tools_log.log_info("Execute 'custom_execution'")
        self.current_sql_file = 85
        self.total_sql_files = 100
        self.progress_ratio = 1.0

        if self.rdb_sample.isChecked():
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_sample', prefix=False)
            return self.load_sample_data()
        elif self.rdb_data.isChecked():
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_data', prefix=False)
            return True


    def _check_database_connection(self, db_filepath):
        """ Set database connection to Geopackage file """

        if not os.path.exists(db_filepath):
            tools_log.log_info(f"File path NOT found: {db_filepath}")
            return False

        # Set DB connection
        tools_log.log_info(f"Set database connection")
        status = self.gpkg_dao.init_db(db_filepath)
        if not status:
            last_error = self.gpkg_dao.last_error
            tools_log.log_info(f"Error connecting to database (sqlite3): {db_filepath}\n{last_error}")
            return False
        status, global_vars.db_qsql = self.gpkg_dao.init_qsql_db(db_filepath, global_vars.plugin_name)
        if not status:
            last_error = self.gpkg_dao.last_error
            tools_log.log_info(f"Error connecting to database (QSqlDatabase): {db_filepath}\n{last_error}")
            return False

        tools_log.log_info(f"Database connection successful")
        print("Database connection successful")
        return True

    def create_gpkg(self):
        """ Create Geopackage """
        gpkg_name = self.gpkg_name
        path = self.project_path
        # project_locale = self.params['project_locale']
        # project_srid = self.params['project_srid']

        self.gpkg_full_path = path + "/" + gpkg_name + ".gpkg"

        driver = gdal.GetDriverByName('GPKG')
        dataset = driver.Create(self.gpkg_full_path, 0, 0, 0, gdal.GDT_Unknown)
        del dataset

    def calculate_number_of_files(self):
        """ Calculate total number of SQL to execute """

        total_sql_files = 0
        dict_process = {}
        list_process = ['load_base']

        for process_name in list_process:
            tools_log.log_info(
                f"Task 'Create schema' execute function 'def get_number_of_files_process' with parameters: '{process_name}'")
            dict_folders, total = self.get_number_of_files_process(process_name)
            total_sql_files += total
            tools_log.log_info(f"Number of SQL files '{process_name}': {total}")
            dict_process[process_name] = total
            self.dict_folders_process[process_name] = dict_folders

        return total_sql_files

    def get_number_of_files_process(self, process_name: str):
        """ Calculate number of files of all folders of selected @process_name """

        tools_log.log_info(
            f"Task 'Create schema' execute function 'def get_folders_process' with parameters: '{process_name}'")
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
            dict_folders[os.path.join(self.folder_software, self.file_pattern_rtree)] = 0
            dict_folders[os.path.join(self.folder_software, self.file_pattern_trg)] = 0

        return dict_folders

    def _manage_result_message(self, status, msg_ok=None, msg_error=None, parameter=None):
        """ Manage message depending result @status """

        if status:
            if msg_ok is None:
                msg_ok = "Process finished successfully"
            tools_qgis.show_info(msg_ok, parameter=parameter)
        else:
            if msg_error is None:
                msg_error = "Process finished with some errors"
            tools_qgis.show_warning(msg_error, parameter=parameter)



    def _select_active_locales(self):

        sql = f"SELECT locale as id, name as idval FROM locales WHERE active = 1"
        rows = self.gpkg_dao.get_rows(sql)
        return rows


    def _save_custom_sql_path(self, dialog):

        folder_path = tools_qt.get_text(dialog, "custom_path_folder")
        if folder_path == "null":
            folder_path = None
        tools_gw.set_config_parser("btn_admin", "custom_sql_path", f"{folder_path}", "user", "session")


    def _manage_docker(self):
        """ Puts the dialog in a docker, depending on the user configuration """

        try:
            tools_gw.close_docker('admin_position')
            global_vars.session_vars['docker_type'] = 'qgis_form_docker'
            global_vars.session_vars['dialog_docker'] = GwDocker()
            global_vars.session_vars['dialog_docker'].dlg_closed.connect(partial(tools_gw.close_docker, 'admin_position'))
            tools_gw.manage_docker_options('admin_position')
            tools_gw.docker_dialog(self.dlg_readsql)
            self.dlg_readsql.dlg_closed.connect(partial(tools_gw.close_docker, 'admin_position'))
            tools_gw.open_dialog(self.dlg_readsql, dlg_name='admin_ui')
        except Exception as e:
            tools_log.log_info(str(e))
            tools_gw.open_dialog(self.dlg_readsql, dlg_name='admin_ui')


    def _load_base_utils(self):

        folder = os.path.join(self.sql_dir, 'corporate', 'utils', 'utils')
        status = self._execute_files(folder, utils_schema_name='utils')
        if not status and self.dev_commit is False:
            return False
        folder = os.path.join(self.sql_dir, 'corporate', 'utils', 'utils', 'fct')
        status = self._execute_files(folder, utils_schema_name='utils')
        if not status and self.dev_commit is False:
            return False
        folder = os.path.join(self.sql_dir, 'corporate', 'utils', 'ws')
        status = self._execute_files(folder, utils_schema_name=self.ws_project_name)
        if not status and self.dev_commit is False:
            return False
        folder = os.path.join(self.sql_dir, 'corporate', 'utils', 'ud')
        status = self._execute_files(folder, utils_schema_name=self.ud_project_name)
        if not status and self.dev_commit is False:
            return False

        return True


    def _update_utils_schema(self, schema_version=None, schema_name=None):

        folder_utils_updates = os.path.join(self.sql_dir, 'corporate', 'utils', 'updates')

        if not os.path.exists(folder_utils_updates):
            tools_qgis.show_message("The update folder was not found in sql folder")
            self.error_count = self.error_count + 1
            return False

        folders = sorted(os.listdir(folder_utils_updates))
        for folder in folders:
            sub_folders = sorted(os.listdir(os.path.join(folder_utils_updates, folder)))

            for sub_folder in sub_folders:
                aux = str(self.ws_project_result[0]).replace('.', '')
                if (schema_version is None and sub_folder <= aux) or schema_version is not None and (schema_version < sub_folder < aux):
                    folder_update = os.path.join(folder_utils_updates, folder, sub_folder, 'utils')
                    if self._process_folder(folder_update):
                        status = self._load_sql(folder_update, utils_schema_name='utils')
                        if status is False:
                            return False
                    if self.project_type_selected == 'ws':
                        folder_update = os.path.join(folder_utils_updates, folder, sub_folder, 'ws')
                        if self._process_folder(folder_update):
                            if schema_name is None:
                                schema_name = self.ws_project_name
                            status = self._load_sql(folder_update, utils_schema_name=schema_name)
                            if status is False:
                                return False
                    if self.project_type_selected == 'ud':
                        folder_update = os.path.join(folder_utils_updates, folder, sub_folder, 'ud')
                        if self._process_folder(folder_update):
                            if schema_name is None:
                                schema_name = self.ud_project_name
                            status = self._load_sql(folder_update, utils_schema_name=schema_name)
                            if status is False:
                                return False
                    folder_update = os.path.join(folder_utils_updates, folder, sub_folder, 'i18n', self.locale)
                    if self._process_folder(folder_update) is True:
                        status = self._execute_files(folder_update, True)
                        if status is False:
                            return False

        return True


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
