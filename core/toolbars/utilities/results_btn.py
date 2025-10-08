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
from qgis.core import QgsEditFormConfig, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import Qt
from typing import Optional

from ....lib import tools_qgis
from ...utils import tools_dr
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
        button = self.toolbar.widgetForAction(self.action) if self.toolbar is not None else None
        if not self.menu.isVisible():
            if button is not None:
                # Show the menu below the button
                self.menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def show_profile(self):
        """ Show profile """

        # Return if theres one profile dialog already open
        if tools_dr.check_if_already_open('dlg_draw_profile', self.profile_btn):
            return

        # Get the profile button class
        if self.profile_btn is None:
            self.profile_btn = DrProfileButton(None, None, None, None, None)
        self.profile_btn.clicked_event()

    def show_report_summary(self):
        """ Show report summary """

        # Return if theres one report summary dialog already open
        if tools_dr.check_if_already_open('dlg_report_summary', self.report_summary_btn):
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

        # Return if theres one results folder selector dialog already open
        if tools_dr.check_if_already_open('dlg_results_folder_selector', self.results_folder_selector_btn):
            return

        # Get the results folder selector button class
        if self.results_folder_selector_btn is None:
            self.results_folder_selector_btn = DrResultsFolderSelectorButton(None, None, None, None, None, self)
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

    def load_vector_results(self):
        """ Load vector results """

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
        if not os.path.exists(os.path.join(results_folder, 'IberGisResults', 'results.gpkg')):
            tools_qgis.show_warning("No results gpkg file found")
            return
        style_folder = os.path.join(global_vars.plugin_dir, 'resources', 'templates', 'rpt')
        if not os.path.exists(style_folder) or not os.path.isdir(style_folder):
            tools_qgis.show_warning("No style folder found")
            return

        rpt_layers = {
            'rpt_storagevol_sum': 'Storage Volume',
            'rpt_outfallflow_sum': 'Outfall Flow',
            'rpt_pumping_sum': 'Pumping Summary',
            'rpt_condsurcharge_sum': 'Conduit Surcharge',
            'rpt_flowclass_sum': 'Flow Classification',
            'rpt_arcflow_sum': 'Arc Flow',
            'rpt_nodedepth_sum': 'Node Depth',
            'rpt_nodeinflow_sum': 'Node Inflow',
            'rpt_nodesurcharge_sum': 'Node Surcharge',
            'rpt_nodeflooding_sum': 'Node Flooding'
        }
        group_name = "RESULTS - " + os.path.basename(results_folder)
        group = QgsProject.instance().layerTreeRoot().insertGroup(0, group_name)
        for tablename, layer_name in rpt_layers.items():
            qml_file = os.path.join(style_folder, f'{tablename}.qml')
            if not os.path.exists(qml_file) or not os.path.isfile(qml_file):
                tools_qgis.show_warning(f"No qml file found for {tablename}")
                continue
            qgs_layer = QgsVectorLayer(f'{results_folder}{os.sep}IberGisResults{os.sep}results.gpkg|layername={tablename}', layer_name, 'ogr')
            if not qgs_layer.isValid():
                tools_qgis.show_warning(f"No valid layer found for {tablename}")
                continue
            qgs_layer.loadNamedStyle(qml_file)
            qgs_layer.triggerRepaint()
            qgs_layer.setDataSource(f'{results_folder}{os.sep}IberGisResults{os.sep}results.gpkg|layername={tablename}', layer_name, 'ogr')
            QgsProject.instance().addMapLayer(qgs_layer, False)
            group.addLayer(qgs_layer)

    # region private functions
    def _fill_results_menu(self):
        """ Fill results menu """

        self.menu.clear()

        rel_path = tools_qgis.get_project_variable('project_results_folder')
        abs_path = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{rel_path}")
        if abs_path is None or not os.path.exists(abs_path) or not os.path.isdir(abs_path):
            tools_qgis.set_project_variable('project_results_folder', None)
            abs_path = None
        if abs_path is not None:
            folder_name = f" - {os.path.basename(abs_path)}"
        else:
            folder_name = ""

        # Add results actions
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

        self.load_raster_results_action = QAction("Load raster results", self.menu)
        self.load_raster_results_action.triggered.connect(self.load_raster_results)
        self.load_raster_results_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '17.png')))

        self.load_vector_results_action = QAction("Load vector results", self.menu)
        self.load_vector_results_action.triggered.connect(self.load_vector_results)
        self.load_vector_results_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '21.png')))

        self.set_results_folder_action = QAction(f"Set results folder{folder_name}", self.menu)
        self.set_results_folder_action.triggered.connect(self.set_results_folder)
        self.set_results_folder_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '20.png')))

        # Validate results folder and disable actions if not valid
        validation_results = self.validate_results_folder(abs_path)
        self.profile_action.setDisabled(not validation_results[0])
        self.report_summary_action.setDisabled(not validation_results[1])
        self.time_series_graph_action.setDisabled(not validation_results[2])
        self.load_raster_results_action.setDisabled(not validation_results[3])
        self.load_vector_results_action.setDisabled(not validation_results[4])

        self.time_series_graph_action.setDisabled(True)  # TODO: Remove this when time series graph is implemented

        self.menu.addAction(self.profile_action)
        self.menu.addAction(self.report_summary_action)
        self.menu.addAction(self.time_series_graph_action)
        self.menu.addSeparator()
        self.menu.addAction(self.load_raster_results_action)
        self.menu.addAction(self.load_vector_results_action)
        self.menu.addSeparator()
        self.menu.addAction(self.set_results_folder_action)

    def validate_results_folder(self, folder: Optional[str]) -> list[bool]:
        """ Validate results folder
                Args:
                    folder (str): The folder to validate
                Returns:
                    list: A list of boolean values indicating if the folder is valid for each type of results(profile, report_summary, time_series_graph, load_raster_results, load_vector_results, set_results_folder)
        """
        validations = [False] * 6

        if folder is None:
            return validations

        # Validate folder
        if not os.path.exists(folder) or not os.path.isdir(folder):
            return validations
        validations[5] = True

        # Validate profile
        if os.path.exists(os.path.join(folder, 'Iber_SWMM.inp')) and \
            os.path.exists(os.path.join(folder, 'Iber_SWMM.out')):
            validations[0] = True

        # Validate report summary
        if os.path.exists(os.path.join(folder, 'Iber_SWMM.rpt')):
            validations[1] = True

        # Validate time series graph
        if os.path.exists(os.path.join(folder, 'Iber_SWMM.out')):
            validations[2] = True

        if not os.path.exists(os.path.join(folder, 'IberGisResults')):
            return validations

        # Validate load raster results
        has_netcdf_file = False
        for file in os.listdir(os.path.join(folder, 'IberGisResults')):
            if file.endswith('.nc'):
                has_netcdf_file = True
                break
        validations[3] = has_netcdf_file

        # Validate load vector results
        if os.path.exists(os.path.join(folder, 'IberGisResults', 'results.gpkg')):
            validations[4] = True

        return validations

    # endregion