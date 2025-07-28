"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# flake8: noqa: E501
# -*- coding: utf-8 -*-
import sys

from qgis.PyQt.QtCore import QSettings


# region system variables (values are initialized on load project without changes during session)
iface = None                            # Instance of class QGisInterface. Provides the hook to manipulate QGIS application at runtime
canvas = None                           # Instance of class QgsMapCanvas. Contains "canvas", "mapTool", "xyCoordinates", "Cursor", "Extent"
plugin_dir = None                       # Plugin folder path
plugin_name = None                      # Plugin name
user_folder_dir = None                  # User folder path
list_configs = [                        # List of configuration files
    'init',
    'session',
    'dev',
    'drain',
    'user_params']
project_loaded = False                  # True when selected project has been loaded
load_project_menu = None               # Instance of class DrMenuLoad. Found in "/core/load_project_menu.py"
configs = {}                            # Dictionary of configuration files. Value is an array of 2 columns:
                                        # [0]-> Filepath. [1]-> Instance of class ConfigParser  # noqa: E116
configs['init'] = [None, None]          # User configuration file: init.config (located in user config folder)
configs['session'] = [None, None]       # Session configuration file: session.config (located in user config folder)
configs['dev'] = [None, None]           # Developer configuration file: dev.config (located in plugin config folder)
configs['drain'] = [None, None]         # Plugin configuration file: drain.config (located in plugin config folder)
configs['user_params'] = [None, None]   # Settings configuration file: user_params.config (plugin config folder)
schema_name = None                      # Schema name retrieved from QGIS project connection with PostgreSql
project_type = None                     # Project type get from table "sys_version"
data_epsg = None                        # SRID retrieved from QGIS project layer "v_edit_node"
project_epsg = None                     # EPSG of QGIS project
logger = None                           # Instance of class DrLogger. Found in "/lib/tools_log.py"
signal_manager = None                   # Instance of class DrSignalManager. Found in "/core/utils/signal_manager.py"
plugin_settings = None                  # Instance of class QSettings. QGIS settings related to plugin variables such as toolbars and checkable actions
current_user = None                     # Current user connected with PostgreSql
db_qsql_data = None                     # Instance of class QSqlDatabase (QSQLITE) used to manage QTableView widgets
db_qsql_config = None                   # Instance of class QSqlDatabase (QSQLITE) used to manage QTableView widgets
dao = None                              # Instance of class DrPgDao. Found in "/lib/tools_db.py"
dao_db_credentials = None               # Credentials used to establish the connection with PostgreSql. Saving {db, schema, table, service, host, port, user, password, sslmode}
gpkg_dao_data = None                    # Instance of class DrGpkgDao. Found in "/lib/tools_gpkg.py"
gpkg_dao_config = None                  # Instance of class DrGpkgDao. Found in "/lib/tools_gpkg.py"
project_vars = {}                       # Project variables from QgsProject related to Giswater
project_vars['info_type'] = None        # gwInfoType
project_vars['add_schema'] = None       # gwAddSchema
project_vars['main_schema'] = None      # gwMainSchema
project_vars['project_role'] = None     # gwProjectRole
project_vars['project_type'] = None     # gwProjectType
project_vars['project_gpkg_path'] = None     # gwProjectGpkgPath
# endregion


# region global user variables (values are initialized on load project without changes during session)
user_level = {                          # An instance used to know user level and user level configuration
    'level': None,                      # initial=1, normal=2, expert=3
    'showquestion': None,               # Used for show help (default config show for level 1 and 2)
    'showsnapmessage': None,            # Used to indicate to the user that they can snapping
    'showselectmessage': None,          # Used to indicate to the user that they can select
    'showadminadvanced': None,          # Manage advanced tab, fields manager tab and sample dev radio button from admin
}
date_format = None                      # Display format of the dates allowed in the forms: dd/MM/yyyy or dd-MM-yyyy or yyyy/MM/dd or yyyy-MM-dd
# endregion


# region Dynamic Variables (variables may change value during user's session)
session_vars = {}
session_vars['last_error'] = None          # An instance of the last database runtime error
session_vars['last_error_msg'] = None      # An instance of the last database runtime error message used in threads
session_vars['threads'] = []               # An instance of the different threads for the execution of the Giswater functionalities (type:list)
session_vars['dialog_docker'] = None       # An instance of DrDocker from "/core/ui/docker.py" which is used to mount a docker form
session_vars['info_docker'] = None         # An instance of current status of the info docker form configured by user. Can be True or False
session_vars['docker_type'] = None         # An instance of current status of the docker form configured by user. Can be configured "qgis_info_docker" and "qgis_form_docker"
session_vars['current_selections'] = None  # An instance of the current selections docker.
snappers = []                              # A list of all the snapper managers, used to disable them in 'Reset plugin' action
active_rubberbands = []                    # A list of all active rubber bands, used to disable them in 'Reset plugin' action
active_signals = {}                        # A dictionary containing all connected signals, first key is dlg_name/file_name, then there are all the signal names.
# endregion


# region Init Variables Functions

def init_global(p_iface, p_canvas, p_plugin_dir, p_plugin_name, p_user_folder_dir):
    """ Function to initialize the global variables needed to load plugin """

    global iface, canvas, plugin_dir, plugin_name, user_folder_dir
    iface = p_iface
    canvas = p_canvas
    plugin_dir = p_plugin_dir
    plugin_name = p_plugin_name
    user_folder_dir = p_user_folder_dir


def init_plugin_settings(setting_file):
    """ Function to set Giswater settings: stored in the registry (on Windows) or .ini file (on Unix) """

    global plugin_settings
    plugin_settings = QSettings(setting_file, QSettings.IniFormat)
    plugin_settings.setIniCodec(sys.getfilesystemencoding())


def init_qgis_settings(p_plugin_name):
    """ Function to set QGIS settings: stored in the registry (on Windows) or .ini file (on Unix) """

    global plugin_name
    plugin_name = p_plugin_name

# endregion