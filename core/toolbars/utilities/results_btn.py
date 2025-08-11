"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import processing

from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsEditFormConfig, QgsProject
from qgis.PyQt.QtCore import Qt

from ....lib import tools_qgis
from .... import global_vars
from sip import isdeleted
from ....core.toolbars.dialog import DrAction
from ....core.toolbars.utilities.profile_btn import DrProfileButton
from ....core.toolbars.utilities.report_summary_btn import DrReportSummaryButton
from ....core.toolbars.utilities.results_folder_selector_btn import DrResultsFolderSelectorButton


class DrResultsButton(DrAction):
    """ Button 16: Results """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        if toolbar is not None:
            toolbar.removeAction(self.action)

        self.plugin_dir = global_vars.plugin_dir
        self.iface = global_vars.iface
        self.canvas = global_vars.canvas
        self.toolbar = toolbar
        self.profile_btn = None
        self.report_summary_btn = None
        self.results_folder_selector_btn = None

        self.menu = QMenu()
        self.menu.setObjectName('results_menu')
        self._fill_results_menu()

        self.menu.aboutToShow.connect(self._fill_results_menu)

        if toolbar is not None:
            self.action.setMenu(self.menu)
            toolbar.addAction(self.action)

    def clicked_event(self):
        # Get the widget for this action (the button)
        # convert_asc_to_netcdf('C:\\Users\\Usuario\\Documents\\_IBERGIS\\errors\\ERROR FROM RASTER TO NETCDF\\RasterResults',
        #                       'C:\\Users\\Usuario\\Documents\\_IBERGIS\\errors\\ERROR FROM RASTER TO NETCDF\\test1.nc',
        #                       None) TODO: Remove this when netcdf creation works properly
        button = self.toolbar.widgetForAction(self.action) if self.toolbar is not None else None
        if not self.menu.isVisible():
            if button is not None:
                # Show the menu below the button
                self.menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def show_profile(self):
        """ Show profile """

        # Return if theres the profile dialog open
        if (self.profile_btn is not None and self.profile_btn.dlg_draw_profile is not None and
                not isdeleted(self.profile_btn.dlg_draw_profile) and self.profile_btn.dlg_draw_profile.isVisible()):
            # Bring the existing dialog to the front
            self.profile_btn.dlg_draw_profile.setWindowState(
                self.profile_btn.dlg_draw_profile.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
            )
            self.profile_btn.dlg_draw_profile.raise_()
            self.profile_btn.dlg_draw_profile.show()
            self.profile_btn.dlg_draw_profile.activateWindow()
            return

        # Get the profile button class
        if self.profile_btn is None:
            self.profile_btn = DrProfileButton(None, None, None, None, None)
        self.profile_btn.clicked_event()

    def show_report_summary(self):
        """ Show report summary """

        # Return if theres the report summary dialog open
        if (self.report_summary_btn is not None and self.report_summary_btn.dlg_report_summary is not None and
                not isdeleted(self.report_summary_btn.dlg_report_summary) and self.report_summary_btn.dlg_report_summary.isVisible()):
            # Bring the existing dialog to the front
            self.report_summary_btn.dlg_report_summary.setWindowState(
                self.report_summary_btn.dlg_report_summary.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
            )
            self.report_summary_btn.dlg_report_summary.raise_()
            self.report_summary_btn.dlg_report_summary.show()
            self.report_summary_btn.dlg_report_summary.activateWindow()
            return

        # Get the report summary button class
        if self.report_summary_btn is None:
            self.report_summary_btn = DrReportSummaryButton(None, None, None, None, None)
        self.report_summary_btn.clicked_event()

    def show_time_series_graph(self):
        """ Show time series graph """

        print("show_time_series_graph")
        return
        # Return if theres one bridge dialog already open
        if self.dialog is not None and not isdeleted(self.dialog) and self.dialog.isVisible():
            # Bring the existing dialog to the front
            self.dialog.setWindowState(self.dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.dialog.raise_()
            self.dialog.show()
            self.dialog.activateWindow()
            tools_qgis.show_warning("There's a Bridge dialog already open.", dialog=self.dialog)
            return

        # Show info message
        msg = "Draw a linestring to define the bridge and then use right click to finish the drawing."
        tools_qgis.show_info(msg)

        # Get the bridge layer
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            tools_qgis.show_warning("Bridge layer not found.")
            return

        # Store previous form suppression setting
        config = bridge_layer.editFormConfig()
        self._conf_supp = config.suppress()
        config.setSuppress(QgsEditFormConfig.FeatureFormSuppress.SuppressOn)  # SuppressOn
        bridge_layer.setEditFormConfig(config)

        # Start editing and trigger add feature tool
        global_vars.iface.setActiveLayer(bridge_layer)
        bridge_layer.startEditing()
        global_vars.iface.actionAddFeature().trigger()

        # Connect to featureAdded signal
        bridge_layer.featureAdded.connect(self._on_bridge_feature_added)

    def set_results_folder(self):
        """ Set results folder """

        # Return if theres the results folder selector dialog open
        if (self.results_folder_selector_btn is not None and self.results_folder_selector_btn.dlg_results_folder_selector is not None and
                not isdeleted(self.results_folder_selector_btn.dlg_results_folder_selector) and self.results_folder_selector_btn.dlg_results_folder_selector.isVisible()):
            # Bring the existing dialog to the front
            self.results_folder_selector_btn.dlg_results_folder_selector.setWindowState(
                self.results_folder_selector_btn.dlg_results_folder_selector.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
            )
            self.results_folder_selector_btn.dlg_results_folder_selector.raise_()
            self.results_folder_selector_btn.dlg_results_folder_selector.show()
            self.results_folder_selector_btn.dlg_results_folder_selector.activateWindow()
            return

        # Get the results folder selector button class
        if self.results_folder_selector_btn is None:
            self.results_folder_selector_btn = DrResultsFolderSelectorButton(None, None, None, None, None)
        self.results_folder_selector_btn.clicked_event()

    def load_raster_results(self):
        """ Load raster results """

        results_folder = tools_qgis.get_project_variable('project_results_folder')
        if results_folder is None:
            tools_qgis.show_warning("No results folder selected")
            return
        results_folder = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{results_folder}")
        if not os.path.exists(results_folder) or not os.path.isdir(results_folder):
            tools_qgis.show_warning("Invalid results folder")
            return
        if not os.path.exists(os.path.join(results_folder, 'IberGisResults')):
            tools_qgis.show_warning("No IberGisResults folder found")
            return

        params = {
            'FOLDER_RESULTS': results_folder
        }
        processing.execAlgorithmDialog('IberGISProvider:ImportRasterResults', params)

    # region private functions
    def _fill_results_menu(self):
        """ Fill results menu """

        self.menu.clear()

        # Add results actions
        self.load_raster_results_action = QAction("Load raster results", self.menu)
        self.load_raster_results_action.triggered.connect(self.load_raster_results)
        self.load_raster_results_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '17.png')))

        self.profile_action = QAction("Profile", self.menu)
        self.profile_action.triggered.connect(self.show_profile)
        self.profile_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '15.png')))

        self.report_summary_action = QAction("Report Summary", self.menu)
        self.report_summary_action.triggered.connect(self.show_report_summary)
        self.report_summary_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '18.png')))
        # self.report_summary_action.setCheckable(True)

        self.time_series_graph_action = QAction("Time series graph", self.menu)
        self.time_series_graph_action.triggered.connect(self.show_time_series_graph)
        self.time_series_graph_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '19.png')))
        self.time_series_graph_action.setCheckable(True)

        self.set_results_folder_action = QAction("Set results folder", self.menu)
        self.set_results_folder_action.triggered.connect(self.set_results_folder)
        self.set_results_folder_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '20.png')))

        self.menu.addAction(self.load_raster_results_action)
        self.menu.addAction(self.profile_action)
        self.menu.addAction(self.report_summary_action)
        self.menu.addAction(self.time_series_graph_action)
        self.menu.addSeparator()
        self.menu.addAction(self.set_results_folder_action)

    # endregion