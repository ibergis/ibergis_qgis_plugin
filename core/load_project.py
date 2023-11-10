"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from functools import partial

from qgis.core import QgsProject, QgsSnappingUtils
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QToolBar, QActionGroup, QDockWidget, QApplication, QDialog

from .models.plugin_toolbar import GwPluginToolbar
from .toolbars import buttons
from .utils import tools_gw
from .. import global_vars
from ..lib import tools_qgis, tools_log, tools_qt, tools_os, tools_gpkgdao


class GwLoadProject(QObject):

    def __init__(self):
        """ Class to manage layers. Refactor code from main.py """

        super().__init__()
        self.iface = global_vars.iface
        self.plugin_toolbars = {}
        self.buttons_to_hide = []
        self.buttons = {}


    def project_read(self, show_warning=True):
        """ Function executed when a user opens a QGIS project (*.qgs) """

        global_vars.project_loaded = False
        if show_warning:
            tools_log.log_info("Project read started")

        self._get_user_variables()
        # Get variables from qgis project
        self._get_project_variables()

        # Check if loaded project is valid for Giswater
        if not self._check_project(show_warning):
            return

        # Set database connection to Geopackage file
        if not self._check_database_connection():
            return

        # TODO: Get SRID from table node
        global_vars.data_epsg = "25831"
        global_vars.project_type = "ud"

        # Removes all deprecated variables defined at drain.config
        #tools_gw.remove_deprecated_config_vars()

        project_role = global_vars.project_vars.get('project_role')
        global_vars.project_vars['project_role'] = None

        # Check if user has config files 'init' and 'session' and its parameters
        tools_gw.user_params_to_userconfig()

        # Check for developers options
        value = tools_gw.get_config_parser('log', 'log_sql', "user", "init", False)
        tools_qgis.user_parameters['log_sql'] = value
        value = tools_gw.get_config_parser('system', 'show_message_durations', "user", "init", False)
        tools_qgis.user_parameters['show_message_durations'] = value

        # Manage locale and corresponding 'i18n' file
        global_vars.plugin_name = tools_qgis.get_plugin_metadata('name', 'drain', global_vars.plugin_dir)
        tools_qt.manage_translation(global_vars.plugin_name)

        # Manage actions of the different plugin_toolbars
        self._manage_toolbars()

        # Manage "btn_updateall" from attribute table
        self._manage_attribute_table()

        # Check parameter 'force_tab_expl'
        force_tab_expl = tools_gw.get_config_parser('system', 'force_tab_expl', 'user', 'init', prefix=False)
        if tools_os.set_boolean(force_tab_expl, False):
            self._force_tab_exploitation()

        # Set global_vars.project_epsg
        global_vars.project_epsg = tools_qgis.get_epsg()
        tools_gw.connect_signal(QgsProject.instance().crsChanged, tools_gw.set_epsg,
                                'load_project', 'project_read_crsChanged_set_epsg')
        global_vars.project_loaded = True

        # Set indexing strategy for snapping so that it uses less memory if possible
        self.iface.mapCanvas().snappingUtils().setIndexingStrategy(QgsSnappingUtils.IndexHybrid)

        # Manage versions of Giswater and PostgreSQL
        plugin_version = tools_qgis.get_plugin_metadata('version', 0, global_vars.plugin_dir)
        # Only get the x.y.zzz, not x.y.zzz.n
        try:
            plugin_version_l = str(plugin_version).split('.')
            if len(plugin_version_l) >= 4:
                plugin_version = f'{plugin_version_l[0]}'
                for i in range(1, 3):
                    plugin_version = f"{plugin_version}.{plugin_version_l[i]}"
        except Exception:
            pass

        message = f"Project read finished. Plugin version: {plugin_version}"
        tools_log.log_info(message)

        # Reset dialogs position
        tools_gw.reset_position_dialog()


    # region private functions

    def _get_project_variables(self):
        """ Manage QGIS project variables """

        global_vars.project_vars = {}
        global_vars.project_vars['info_type'] = tools_qgis.get_project_variable('gwInfoType')
        global_vars.project_vars['add_schema'] = tools_qgis.get_project_variable('gwAddSchema')
        global_vars.project_vars['main_schema'] = tools_qgis.get_project_variable('gwMainSchema')
        global_vars.project_vars['project_role'] = tools_qgis.get_project_variable('gwProjectRole')
        global_vars.project_vars['project_type'] = tools_qgis.get_project_variable('gwProjectType')
        global_vars.project_vars['project_gpkg'] = tools_qgis.get_project_variable('project_gpkg_path')


    def _get_user_variables(self):
        """ Get config related with user variables """

        global_vars.user_level['level'] = tools_gw.get_config_parser('user_level', 'level', "user", "init", False)
        global_vars.user_level['showquestion'] = tools_gw.get_config_parser('user_level', 'showquestion', "user", "init", False)
        global_vars.user_level['showsnapmessage'] = tools_gw.get_config_parser('user_level', 'showsnapmessage', "user", "init", False)
        global_vars.user_level['showselectmessage'] = tools_gw.get_config_parser('user_level', 'showselectmessage', "user", "init", False)
        global_vars.user_level['showadminadvanced'] = tools_gw.get_config_parser('user_level', 'showadminadvanced', "user", "init", False)
        global_vars.date_format = tools_gw.get_config_parser('system', 'date_format', "user", "init", False)


    def _check_project(self, show_warning):
        """ TODO: Check if loaded project is valid for Drain """
        return True


    def _check_database_connection(self):
        """ Set database connection to Geopackage file """

        # Create object to manage GPKG database connection
        gpkg_dao_config = tools_gpkgdao.GwGpkgDao()
        global_vars.gpkg_dao_config = gpkg_dao_config
        # Define filepath of configuration GPKG
        filename = "config.gpkg"
        db_filepath = os.path.join(global_vars.plugin_dir, "samples", filename)
        tools_log.log_info(db_filepath)
        if not os.path.exists(db_filepath):
            tools_log.log_info(f"File not found: {db_filepath}")
            return False

        # Set DB connection
        tools_log.log_info(f"Set database connection")
        database_name = f"{global_vars.plugin_name}_config"
        status, global_vars.db_qsql_config = global_vars.gpkg_dao_config.init_qsql_db(db_filepath, database_name)
        if not status:
            last_error = global_vars.gpkg_dao_config.last_error
            tools_log.log_info(f"Error connecting to database (QSqlDatabase): {db_filepath}\n{last_error}")
            return False
        status = global_vars.gpkg_dao_config.init_db(db_filepath)
        if not status:
            last_error = global_vars.gpkg_dao_config.last_error
            tools_log.log_info(f"Error connecting to database (sqlite3): {db_filepath}\n{last_error}")
            return False

        # Create object to manage GPKG database connection
        gpkg_dao_data = tools_gpkgdao.GwGpkgDao()
        global_vars.gpkg_dao_data = gpkg_dao_data


        # Define filepath of data GPKG
        db_filepath =f"{global_vars.project_vars['project_gpkg']}"

        if db_filepath is None:
            filename = "sample.gpkg"
            db_filepath = os.path.join(global_vars.plugin_dir, "samples", filename)

        tools_log.log_info(db_filepath)
        if not os.path.exists(db_filepath):
            tools_log.log_info(f"File not found: {db_filepath}")
            return False

        # Set DB connection
        tools_log.log_info(f"Set database connection")
        database_name = f"{global_vars.plugin_name}_data"
        status, global_vars.db_qsql_data = global_vars.gpkg_dao_data.init_qsql_db(db_filepath, database_name)
        if not status:
            last_error = global_vars.gpkg_dao_data.last_error
            tools_log.log_info(f"Error connecting to database (QSqlDatabase): {db_filepath}\n{last_error}")
            return False
        status = global_vars.gpkg_dao_data.init_db(db_filepath)
        if not status:
            last_error = global_vars.gpkg_dao_data.last_error
            tools_log.log_info(f"Error connecting to database (sqlite3): {db_filepath}\n{last_error}")
            return False



        tools_log.log_info(f"Database connection successful")
        return True


    def _get_buttons_to_hide(self):
        """ Get all buttons to hide """

        buttons_to_hide = None
        try:
            row = tools_gw.get_config_parser('toolbars_hidebuttons', 'buttons_to_hide', "user", "init")
            if not row or row in (None, 'None'):
                return None

            buttons_to_hide = [int(x) for x in row.split(',')]

        except Exception as e:
            tools_log.log_warning(f"{type(e).__name__}: {e}")
        finally:
            return buttons_to_hide


    def _manage_toolbars(self):
        """ Manage actions of the custom plugin toolbars """

        # Dynamically get list of toolbars from config file
        toolbar_names = tools_gw.get_config_parser('toolbars', 'list_toolbars', "project", "drain")
        if toolbar_names in (None, 'None'):
            tools_log.log_info("Parameter 'toolbar_names' is None")
            return

        toolbars_order = tools_gw.get_config_parser('toolbars_position', 'toolbars_order', 'user', 'init')
        if toolbars_order in (None, 'None'):
            tools_log.log_info("Parameter 'toolbars_order' is None")
            return

        # Call each of the functions that configure the toolbars 'def toolbar_xxxxx(self, toolbar_id, x=0, y=0):'
        toolbars_order = toolbars_order.replace(' ', '').split(',')
        for tb in toolbars_order:
            self._create_toolbar(tb)

        # Manage action group of every toolbar
        icon_folder = f"{global_vars.plugin_dir}{os.sep}icons{os.sep}toolbars{os.sep}"
        parent = self.iface.mainWindow()
        for plugin_toolbar in list(self.plugin_toolbars.values()):
            ag = QActionGroup(parent)
            ag.setProperty('gw_name', 'gw_QActionGroup')
            for index_action in plugin_toolbar.list_actions:

                successful = False
                attempt = 0

                while not successful and attempt < 10:
                    button_def = tools_gw.get_config_parser('buttons_def', str(index_action), "project", "drain")
                    
                    if button_def not in (None, 'None'):
                        # Check if the class associated to the button definition exists
                        if hasattr(buttons, button_def):
                            text = tools_qt.tr(f'{button_def}')
                            icon_path = f"{icon_folder}{plugin_toolbar.toolbar_id}{os.sep}{index_action}.png"
                            button_class = getattr(buttons, button_def)
                            button = button_class(icon_path, button_def, text, plugin_toolbar.toolbar, ag)
                            self.buttons[index_action] = button
                        successful = True

                    attempt = attempt + 1

        # Disable buttons which are project type exclusive
        project_exclude = None
        successful = False
        attempt = 0
        while not successful and attempt < 10:
            project_exclude = tools_gw.get_config_parser('project_exclude', global_vars.project_type, "project", "drain")
            if project_exclude not in (None, "None"):
                successful = True
            attempt = attempt + 1

        if project_exclude not in (None, 'None'):
            project_exclude = project_exclude.replace(' ', '').split(',')
            for index in project_exclude:
                self._hide_button(index)

        # Hide buttons from buttons_to_hide
        buttons_to_hide = self._get_buttons_to_hide()
        if buttons_to_hide:
            for button_id in buttons_to_hide:
                self._hide_button(button_id)

        # Disable and hide all plugin_toolbars and actions
        self._enable_toolbars(False)

        # Enable toolbars: 'main'
        self._enable_toolbar("main")
        self._enable_toolbar("utilities")
        self._enable_toolbar("toc")
        self._hide_button("308")


    def _create_toolbar(self, toolbar_id):

        list_actions = tools_gw.get_config_parser('toolbars', str(toolbar_id), "project", "drain")
        if list_actions in (None, 'None'):
            return

        list_actions = list_actions.replace(' ', '').split(',')
        if type(list_actions) != list:
            list_actions = [list_actions]

        toolbar_name = tools_qt.tr(f'toolbar_{toolbar_id}_name')
        plugin_toolbar = GwPluginToolbar(toolbar_id, toolbar_name, True)

        # If the toolbar is ToC, add it to the Layers docker toolbar, if not, create a new toolbar
        if toolbar_id == "toc":
            plugin_toolbar.toolbar = self.iface.mainWindow().findChild(QDockWidget, 'Layers').findChildren(QToolBar)[0]
        else:
            plugin_toolbar.toolbar = self.iface.addToolBar(toolbar_name)

        plugin_toolbar.toolbar.setObjectName(toolbar_name)
        plugin_toolbar.toolbar.setProperty('gw_name', toolbar_id)
        plugin_toolbar.list_actions = list_actions
        self.plugin_toolbars[toolbar_id] = plugin_toolbar


    def _enable_toolbars(self, visible=True):
        """ Enable/disable all plugin toolbars from QGIS GUI """

        # Enable/Disable actions
        self._enable_all_buttons(visible)
        try:
            for plugin_toolbar in list(self.plugin_toolbars.values()):
                if plugin_toolbar.enabled:
                    plugin_toolbar.toolbar.setVisible(visible)
        except Exception as e:
            tools_log.log_warning(str(e))


    def _enable_all_buttons(self, enable=True):
        """ Utility to enable/disable all buttons """

        for index in self.buttons.keys():
            self._enable_button(index, enable)


    def _enable_button(self, button_id, enable=True):
        """ Enable/disable selected button """

        key = str(button_id).zfill(2)
        if key in self.buttons:
            self.buttons[key].action.setEnabled(enable)


    def _hide_button(self, button_id, hide=True):
        """ Enable/disable selected action """

        key = str(button_id).zfill(2)
        if key in self.buttons:
            self.buttons[key].action.setVisible(not hide)


    def _enable_toolbar(self, toolbar_id, enable=True):
        """ Enable/Disable toolbar. Normally because user has no permission """

        if toolbar_id in self.plugin_toolbars:
            plugin_toolbar = self.plugin_toolbars[toolbar_id]
            plugin_toolbar.toolbar.setVisible(enable)
            for index_action in plugin_toolbar.list_actions:
                self._enable_button(index_action, enable)


    def _force_tab_exploitation(self):
        """ Select tab 'tab_exploitation' in dialog 'dlg_selector_basic' """

        tools_gw.set_config_parser("dialogs_tab", f"dlg_selector_basic", f"tab_exploitation", "user", "session")


    def _manage_attribute_table(self):
        """ If configured, disable button "Update all" from attribute table """

        disable = tools_gw.get_config_parser('system', 'disable_updateall_attributetable', "user", "init", prefix=False)
        if tools_os.set_boolean(disable, False):
            tools_gw.connect_signal(QApplication.instance().focusChanged, self._manage_focus_changed,
                                    'load_project', 'manage_attribute_table_focusChanged')


    def _manage_focus_changed(self, old, new):
        """ Disable button "Update all" of QGIS attribute table dialog. Parameters are passed by the signal itself. """

        if new is None or not hasattr(new, 'window'):
            return

        table_dialog = new.window()
        # Check if focused widget's window is a QgsAttributeTableDialog
        if isinstance(table_dialog, QDialog) and table_dialog.objectName().startswith('QgsAttributeTableDialog'):
            try:
                # Look for the button "Update all"
                for widget in table_dialog.children():
                    if widget.objectName() == 'mUpdateExpressionBox':
                        widget_btn_updateall = None
                        for subwidget in widget.children():
                            if subwidget.objectName() == 'mRunFieldCalc':  # This is for the button itself
                                widget_btn_updateall = subwidget
                                tools_qt.set_widget_enabled(None, widget_btn_updateall, False)
                            if subwidget.objectName() == 'mUpdateExpressionText':  # This is the expression text field
                                try:
                                    subwidget.fieldChanged.disconnect()
                                except:
                                    pass
                                # When you type something in the expression text field, the button "Update all" is
                                # enabled. This will disable it again.
                                subwidget.fieldChanged.connect(partial(
                                    tools_qt.set_widget_enabled, None, widget_btn_updateall, False))
                        break
            except IndexError:
                pass

    # endregion
