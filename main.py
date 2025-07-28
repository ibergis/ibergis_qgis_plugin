"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from functools import partial
from qgis.core import QgsApplication, QgsProject
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QToolBar, QToolButton, QApplication

from . import global_vars
from .lib import tools_qgis, tools_os, tools_log, tools_qt
try:
    required_packages = ['geopandas', 'gmsh', 'pandamesh', 'openpyxl', 'xlsxwriter', 'rasterio', 'xarray', 'rioxarray']
    imported_packages = []
    not_imported = []

    import geopandas  # noqa: F401
    imported_packages.append('geopandas')

    import platform
    if platform.system() == "Windows":
        from packages.gmsh import gmsh  # noqa: F401
    else:
        import gmsh  # noqa: F401
    imported_packages.append('gmsh')
    import pandamesh  # noqa: F401
    imported_packages.append('pandamesh')
    import openpyxl  # noqa: F401
    imported_packages.append('openpyxl')
    import xlsxwriter  # noqa: F401
    imported_packages.append('xlsxwriter')
    import rasterio  # noqa: F401
    imported_packages.append('rasterio')
    import xarray  # noqa: F401
    imported_packages.append('xarray')
    import rioxarray  # noqa: F401
    imported_packages.append('rioxarray')
except ImportError:
    not_imported = [pkg for pkg in required_packages if pkg not in imported_packages]
    msg = (
        "It appears that certain dependencies required for the DRAIN plugin were not detected. "
        "Please check if they are in the packages folder and restart QGIS. "
        "If the problem persists, please contact the plugin developers. "
        "The following packages could not be imported: {0}"
    )
    msg_params = (not_imported,)
    tools_qt.show_question(msg, msg_params=msg_params)


from .core.admin.admin_btn import DrAdminButton
from .core.load_project import DrLoadProject
from .core.utils import tools_dr
from .core.utils.signal_manager import DrSignalManager
from .core.ui.dialog import DrDialog
from .core.ui.main_window import DrMainWindow
from .core.processing.drain_provider import DrainProvider
from .core.processing.drain_mesh_provider import DrainMeshProvider

from typing import Optional


class Drain(QObject):

    def __init__(self, iface):
        """
        Constructor
            :param iface: An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time. (QgsInterface)
        """

        super(Drain, self).__init__()
        self.iface = iface
        self.load_project = None
        self.btn_add_layers = None
        self.action = None
        self.action_info = None
        self.provider: Optional[DrainProvider] = None
        self.provider_mesh: Optional[DrainMeshProvider] = None

    def initGui(self):
        """ Create the menu entries and toolbar icons inside the QGIS GUI """

        # Initialize plugin
        if self._init_plugin():
            # Force project read (to work with PluginReloader)
            self._project_read(False, False)
            self._initProcessing()
            self._initProcessingMesh()

    def unload(self, hide_gw_button=None):
        """
        Removes plugin menu items and icons from QGIS GUI
            :param hide_gw_button:
                                is True when you want to hide the admin button.
                                is False when you want to show the admin button.
                                is None when called from QGIS.
        """

        try:
            # Reset values for global_vars.project_vars
            global_vars.project_vars['info_type'] = None
            global_vars.project_vars['add_schema'] = None
            global_vars.project_vars['main_schema'] = None
            global_vars.project_vars['project_role'] = None
            global_vars.project_vars['project_type'] = None
        except Exception as e:
            msg = "Exception in unload when reset values for global_vars.project_vars: {0}"
            msg_params = (e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        msg = "Exception in unload when {0}: {1}"
        self._manage_dialogs(msg)

        self._manage_signals(hide_gw_button, msg)

        try:
            # Remove file handler when reloading
            if hide_gw_button:
                global_vars.logger.close_logger()
        except Exception as e:
            msg_params = ("global_vars.logger.close_logger()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        self._manage_buttons(hide_gw_button, msg)

        try:
            # Unload processing provider
            if hide_gw_button is None or False:
                QgsApplication.processingRegistry().removeProvider(self.provider)
                QgsApplication.processingRegistry().removeProvider(self.provider_mesh)
        except Exception as e:
            message = "Couldn't unload the processing providers: {0}"
            msg_params = (e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

        self.load_project = None

    def _manage_buttons(self, hide_gw_button, msg):
        try:
            # Remove 'Main Info button'
            self._unset_info_button()
        except Exception as e:
            msg_params = ("self._unset_info_button()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        try:
            # Remove ToC buttons
            self._unset_toc_buttons()
        except Exception as e:
            msg_params = ("self._unset_toc_buttons()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        try:
            # Remove 'Drain menu'
            tools_dr.unset_drain_menu()
        except Exception as e:
            msg_params = ("tools_dr.unset_drain_menu()",)
            tools_log.log_info(msg, parameter=str(e), msg_params=msg_params)

        try:
            # Check if project is current loaded and remove giswater action from PluginMenu and Toolbars
            if self.load_project:
                global_vars.project_type = None
                if self.load_project.buttons != {}:
                    for button in list(self.load_project.buttons.values()):
                        self.iface.removePluginMenu(self.plugin_name, button.action)
                        self.iface.removeToolBarIcon(button.action)
        except Exception as e:
            msg_params = ("self.iface.removePluginMenu(self.plugin_name, button.action)", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        try:
            # Check if project is current loaded and remove giswater toolbars from qgis
            if self.load_project:
                if self.load_project.plugin_toolbars:
                    for plugin_toolbar in list(self.load_project.plugin_toolbars.values()):
                        if plugin_toolbar.enabled:
                            plugin_toolbar.toolbar.setVisible(False)
                            del plugin_toolbar.toolbar
        except Exception as e:
            message = "Exception in unload when deleting {0}: {1}"
            msg_params = ("plugin_toolbar.toolbar", e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

        try:
            # Set 'Main Info button' if project is unload or project don't have layers
            layers = QgsProject.instance().mapLayers().values()
            if hide_gw_button is False and len(layers) == 0:
                self._set_info_button()
                tools_dr.create_drain_menu(False)
        except Exception as e:
            msg_params = ("self._set_info_button()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

    def _manage_signals(self, hide_gw_button, msg):
        if hide_gw_button is None:
            try:
                # Manage unset signals
                self._unset_signals()
            except Exception as e:
                msg_params = ("self._unset_signals()", e,)
                tools_qt.show_exception_message(msg, msg_params=msg_params)

        try:
            # Force action pan
            self.iface.actionPan().trigger()
        except Exception as e:
            msg_params = ("self.iface.actionPan().trigger()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        message = "Exception in unload when disconnecting {0} signal: {1}"
        try:
            # Disconnect QgsProject.instance().crsChanged signal
            tools_dr.disconnect_signal('load_project', 'project_read_crsChanged_set_epsg')
        except Exception as e:
            msg_params = ("QgsProject.instance().crsChanged", e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

        try:
            tools_dr.disconnect_signal('load_project', 'manage_attribute_table_focusChanged')
        except Exception as e:
            msg_params = ("focusChanged", e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

        try:
            tools_dr.disconnect_signal('load_project', 'currentLayerChanged')
        except Exception as e:
            msg_params = ("currentLayerChanged", e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

        try:
            tools_dr.disconnect_signal('layer_changed')
        except Exception as e:
            msg_params = ("layer_changed", e,)
            tools_qt.show_exception_message(message, msg_params=msg_params)

    def _manage_dialogs(self, msg):
        try:
            # Remove IberGIS dockers
            self._remove_dockers()
        except Exception as e:
            msg_params = ("self._remove_dockers()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

        try:
            # Close all open dialogs
            self._close_open_dialogs()
        except Exception as e:
            msg_params = ("self._close_open_dialogs()", e,)
            tools_qt.show_exception_message(msg, msg_params=msg_params)

    # region private functions
    def _initProcessing(self):
        """Init Processing provider"""
        self.provider = DrainProvider(global_vars.plugin_dir)
        QgsApplication.processingRegistry().addProvider(self.provider)

    def _initProcessingMesh(self):
        """Init Processing provider for mesh"""
        self.provider_mesh = DrainMeshProvider(global_vars.plugin_dir)
        QgsApplication.processingRegistry().addProvider(self.provider_mesh)

    def _init_plugin(self):
        """ Plugin main initialization function """

        # Initialize plugin global variables
        plugin_dir = os.path.dirname(__file__)
        global_vars.plugin_dir = plugin_dir
        global_vars.iface = self.iface
        self.plugin_name = tools_qgis.get_plugin_metadata('name', 'drain', plugin_dir)
        self.icon_folder = f"{plugin_dir}{os.sep}icons{os.sep}dialogs{os.sep}24x24{os.sep}"
        major_version = tools_qgis.get_major_version(plugin_dir=plugin_dir)
        user_folder_dir = f'{tools_os.get_datadir()}{os.sep}{self.plugin_name.capitalize()}{os.sep}{major_version}'
        global_vars.init_global(self.iface, self.iface.mapCanvas(), plugin_dir, self.plugin_name, user_folder_dir)

        # Create log file
        min_log_level = 20
        tools_log.set_logger(self.plugin_name, min_log_level)
        msg = "Initialize plugin"
        tools_log.log_info(msg)

        # Check if config file exists
        setting_file = os.path.join(plugin_dir, 'config', 'drain.config')
        if not os.path.exists(setting_file):
            msg = "Config file not found at: {0}"
            msg_params = (setting_file,)
            tools_qgis.show_warning(msg, msg_params=msg_params)
            return False

        # Set plugin and QGIS settings: stored in the registry (on Windows) or .ini file (on Unix)
        global_vars.init_plugin_settings(setting_file)
        global_vars.init_qgis_settings(self.plugin_name)

        # Check if user config folder exists
        self._manage_user_config_folder(f"{global_vars.user_folder_dir}{os.sep}core")

        # Initialize parsers of configuration files: init, session, giswater, user_params
        tools_dr.initialize_parsers()

        # Load all the variables from user_params.config to their respective user config files
        tools_dr.user_params_to_userconfig()

        # Set logger parameters min_log_level and log_limit_characters
        min_log_level = tools_dr.get_config_parser('log', 'log_level', 'user', 'init', False)
        log_limit_characters = tools_dr.get_config_parser('log', 'log_limit_characters', 'user', 'init', False)
        log_db_limit_characters = tools_dr.get_config_parser('log', 'log_db_limit_characters', 'user', 'init', False)
        global_vars.logger.set_logger_parameters(min_log_level, log_limit_characters, log_db_limit_characters)

        # Enable Python console and Log Messages panel if parameter 'enable_python_console' = True
        python_enable_console = tools_dr.get_config_parser('system', 'enable_python_console', 'project', 'drain')
        if python_enable_console == 'TRUE':
            tools_qgis.enable_python_console()

        # Create the DrSignalManager
        self._create_signal_manager()

        # Define signals
        self._set_signals()

        # Set main information button (always visible)
        self._set_info_button()

        return True

    def _create_signal_manager(self):
        """ Creates an instance of DrSignalManager and connects all the signals """

        global_vars.signal_manager = DrSignalManager()
        global_vars.signal_manager.show_message.connect(tools_qgis.show_message)

    def _manage_user_config_folder(self, user_folder_dir):
        """ Check if user config folder exists. If not create empty files init.config and session.config """

        try:
            config_folder = f"{user_folder_dir}{os.sep}config{os.sep}"
            if not os.path.exists(config_folder):
                message = "Creating user config folder: {0}"
                msg_params = (config_folder,)
                tools_log.log_info(message, msg_params=msg_params)
                os.makedirs(config_folder)

            # Check if config files exists. If not create them empty
            filepath = f"{config_folder}{os.sep}init.config"
            if not os.path.exists(filepath):
                open(filepath, 'a').close()
            filepath = f"{config_folder}{os.sep}session.config"
            if not os.path.exists(filepath):
                open(filepath, 'a').close()

        except Exception as e:
            message = "{0}: {1}"
            msg_params = ("manage_user_config_folder", e,)
            tools_log.log_warning(message, msg_params=msg_params)

    def _set_signals(self):
        """ Define iface event signals on Project Read / New Project / Save Project """

        try:
            tools_dr.connect_signal(self.iface.projectRead, self._project_read,
                                    'main', 'projectRead')
            tools_dr.connect_signal(self.iface.newProjectCreated, self._project_new,
                                    'main', 'newProjectCreated')
            tools_dr.connect_signal(self.iface.actionSaveProject().triggered, self._save_toolbars_position,
                                    'main', 'actionSaveProject_save_toolbars_position')
        except AttributeError:
            pass

    def _unset_signals(self):
        """ Disconnect iface event signals on Project Read / New Project / Save Project """

        try:
            tools_dr.disconnect_signal('main', 'projectRead')
        except TypeError:
            pass
        try:
            tools_dr.disconnect_signal('main', 'newProjectCreated')
        except TypeError:
            pass
        try:
            tools_dr.disconnect_signal('main', 'actionSaveProject_save_toolbars_position')
        except TypeError:
            pass

    def _set_info_button(self):
        """ Set Giswater information button (always visible)
            If project is loaded show information form relating to Plugin Giswater
            Else open admin form with which can manage database and qgis projects
        """

        # Create instance class and add button into QGIS toolbar
        main_toolbutton = QToolButton()
        self.action_info = self.iface.addToolBarWidget(main_toolbutton)

        # Set icon button if exists
        icon_path = self.icon_folder + '36.png'
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action = QAction(icon, "Show info", self.iface.mainWindow())
        else:
            self.action = QAction("Show info", self.iface.mainWindow())

        main_toolbutton.setDefaultAction(self.action)
        admin_button = DrAdminButton()
        self.action.triggered.connect(partial(admin_button.init_sql))

    def _unset_info_button(self):
        """ Unset Giswater information button (when plugin is disabled or reloaded) """

        # Disconnect signal from action if exists
        if self.action:
            self.action.triggered.disconnect()

        # Remove button from toolbar if exists
        if self.action_info:
            self.iface.removeToolBarIcon(self.action_info)

        # Set action and button as None
        self.action = None
        self.action_info = None

    def _unset_toc_buttons(self):
        """ Unset Add Child Layer and Toggle EPA World buttons (when plugin is disabled or reloaded) """

        toolbar = self.iface.mainWindow().findChild(QDockWidget, 'Layers').findChildren(QToolBar)[-1]
        for action in toolbar.actions():
            if action.objectName() not in ('DrAddChildLayerButton', 'DrEpaWorldButton'):
                continue
            toolbar.removeAction(action)  # Remove from toolbar
            action.deleteLater()  # Schedule for deletion

    def _project_new(self):
        """ Function executed when a user creates a new QGIS project """

        # Unload plugin when create new QGIS project
        self.unload(False)

    def _project_read(self, show_warning=True, hide_gw_button=True):
        """ Function executed when a user opens a QGIS project (*.qgs) """

        # Unload plugin before reading opened project
        self.unload(hide_gw_button)

        # Add file handler
        if hide_gw_button:
            global_vars.logger.add_file_handler()

        # Create class to manage code that performs project configuration
        self.load_project = DrLoadProject()
        self.load_project.project_read(show_warning)

    def _save_toolbars_position(self):

        # Get all QToolBar from qgis iface
        widget_list = self.iface.mainWindow().findChildren(QToolBar)
        own_toolbars = []

        # Get list with own QToolBars
        for w in widget_list:
            if w.property('gw_name'):
                own_toolbars.append(w)

        # Order list of toolbar in function of X position
        own_toolbars = sorted(own_toolbars, key=lambda k: k.x())
        if len(own_toolbars) == 0 or (len(own_toolbars) == 1 and own_toolbars[0].property('gw_name') == 'toc') or \
                global_vars.project_type is None:
            return

        # Set 'toolbars_order' parameter on 'toolbars_position' section on init.config user file (found in user path)
        sorted_toolbar_ids = [tb.property('gw_name') for tb in own_toolbars]
        sorted_toolbar_ids = ",".join(sorted_toolbar_ids)
        tools_dr.set_config_parser('toolbars_position', 'toolbars_order', str(sorted_toolbar_ids), "user", "init")

    def save_project(self):
        project = QgsProject.instance()
        project.write()

    def _remove_dockers(self):
        """ Remove Giswater dockers """

        # Get 'Search' docker form from qgis iface and remove it if exists
        docker_search = self.iface.mainWindow().findChild(QDockWidget, 'dlg_search')
        if docker_search:
            self.iface.removeDockWidget(docker_search)
            # TODO: manage this better, deleteLater() is not fast enough and deletes the docker after opening the search
            #  again on load_project.py --> if tools_os.set_boolean(open_search)
            docker_search.deleteLater()

        # Get 'Docker' docker form from qgis iface and remove it if exists
        docker_info = self.iface.mainWindow().findChild(QDockWidget, 'docker')
        if docker_info:
            self.iface.removeDockWidget(docker_info)

        # Remove 'current_selections' docker
        if global_vars.session_vars['current_selections']:
            self.iface.removeDockWidget(global_vars.session_vars['current_selections'])
            global_vars.session_vars['current_selections'].deleteLater()
            global_vars.session_vars['current_selections'] = None

        # Manage 'dialog_docker' from global_vars.session_vars and remove it if exists
        tools_dr.close_docker()

        # Get 'Layers' docker form and his actions from qgis iface and remove it if exists
        if self.btn_add_layers:
            dockwidget = self.iface.mainWindow().findChild(QDockWidget, 'Layers')
            toolbar = dockwidget.findChildren(QToolBar)[0]
            # TODO improve this, now remove last action
            toolbar.removeAction(toolbar.actions()[len(toolbar.actions()) - 1])
            self.btn_add_layers = None

    def _close_open_dialogs(self):
        """ Close Giswater open dialogs """

        # Get all widgets
        allwidgets = QApplication.allWidgets()

        # Only keep Giswater widgets that are currently open
        windows = [x for x in allwidgets if getattr(x, "isVisible", False)
                   and (issubclass(type(x), DrMainWindow) or issubclass(type(x), DrDialog))]

        # Close them
        for window in windows:
            try:
                tools_dr.close_dialog(window)
            except Exception as e:
                msg = "Exception in {0}: {1}"
                msg_params = ("_close_open_dialogs", e,)
                tools_log.log_info(msg, msg_params=msg_params)

    # endregion