"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import processing
from functools import partial
from typing import Optional, Literal

from qgis.PyQt.QtWidgets import QMenu, QAction, QListWidgetItem
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import Qt

from ....lib import tools_qgis
from ...utils import tools_dr
from .... import global_vars
from ....core.toolbars.dialog import DrAction
from ....core.ui.ui_manager import DrTimeseriesGraphUi
from ....core.toolbars.utilities.profile_btn import DrProfileButton
from ....core.toolbars.utilities.report_summary_btn import DrReportSummaryButton
from ....core.toolbars.utilities.results_folder_selector_btn import DrResultsFolderSelectorButton


TS_GRAPH_TYPES = ['Subcatchment', 'Node', 'Link', 'System']
TS_GRAPH_VARIABLES = {
    'Subcatchment': [
        'Precipitation', 'Snow Depth', 'Evaporation', 'Infiltration', 'Runoff', 'GW Flow', 'GW Elev.', 'Soil Moisture'
    ],
    'Node': [
        'Depth', 'Head', 'Volume', 'Lateral Inflow', 'Total Inflow', 'Flooding'
    ],
    'Link': [
        'Flow', 'Depth', 'Velocity', 'Volume', 'Capacity'
    ],
    'System': [
        'Temperature', 'Precipitation', 'Snow Depth', 'Infiltration', 'Runoff', 'DW Inflow', 'GW Inflow',
        'I&I Inflow', 'Direct Inflow', 'Total Inflow', 'Flooding', 'Outflow', 'Storage', 'Evaporation', 'PET'
    ]
}


class DataSeries:
    """ Class to hold data series information """

    def __init__(self, object_type: Optional[Literal['Subcatchment', 'Node', 'Link', 'System']],
                 object_name: Optional[str], variable: Optional[str], legend_label: Optional[str],
                 axis: Literal['Left', 'Right']):
        self.object_type = object_type
        self.object_name = object_name
        self.variable = variable
        self.legend_label = legend_label
        self.axis = axis

    def __str__(self):
        # Handle empty values for better display
        object_type = self.object_type or ""
        object_name = self.object_name or ""
        variable = self.variable or ""
        legend_label = self.legend_label or ""

        if not object_type and not object_name and not variable:
            return "New series"

        if legend_label:
            return f"{legend_label}"

        return f"{object_type} {object_name} {variable}"


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
        self.ts_graph_selection_dlg = DrTimeseriesGraphUi()

        # Fill combos
        self._fill_cmb_type(self.ts_graph_selection_dlg)
        self._fill_cmb_variable(self.ts_graph_selection_dlg)

        # Connect signals
        self.ts_graph_selection_dlg.cmb_type.currentTextChanged.connect(partial(self._fill_cmb_variable, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.btn_add.clicked.connect(partial(self._add_data_series, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.btn_delete.clicked.connect(partial(self._delete_data_series, self.ts_graph_selection_dlg))

        # Connect list selection change
        self.ts_graph_selection_dlg.lst_data_series.currentItemChanged.connect(partial(self._on_list_selection_changed, self.ts_graph_selection_dlg))

        # Connect widget changes to update DataSeries
        self.ts_graph_selection_dlg.cmb_type.currentTextChanged.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.txt_name.textChanged.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.cmb_variable.currentTextChanged.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.txt_legend_label.textChanged.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.rb_axis_left.toggled.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.rb_axis_right.toggled.connect(partial(self._on_widget_changed, self.ts_graph_selection_dlg))

        tools_dr.open_dialog(self.ts_graph_selection_dlg, dlg_name='timeseries_graph')

    def _add_data_series(self, dialog):
        """ Add empty data series and select it """

        # Create empty DataSeries instance with default values
        data_series = DataSeries(None, None, None, None, "Left")

        # Create QListWidgetItem with string representation and add to list
        list_item = QListWidgetItem(str(data_series))
        list_item.setData(Qt.UserRole, data_series)  # Store the DataSeries object
        dialog.lst_data_series.addItem(list_item)

        # Select the newly added item
        dialog.lst_data_series.setCurrentItem(list_item)

    def _on_list_selection_changed(self, dialog):
        """ Handle list selection change to update widgets """

        current_item = dialog.lst_data_series.currentItem()
        if current_item is None:
            return

        # Get the DataSeries object from the selected item
        data_series = current_item.data(Qt.UserRole)
        if data_series is None:
            return

        # Block signals to prevent recursive updates
        dialog.cmb_type.blockSignals(True)
        dialog.txt_name.blockSignals(True)
        dialog.cmb_variable.blockSignals(True)
        dialog.txt_legend_label.blockSignals(True)
        dialog.rb_axis_left.blockSignals(True)
        dialog.rb_axis_right.blockSignals(True)

        # Update widgets with DataSeries data
        if data_series.object_type:
            dialog.cmb_type.setCurrentText(data_series.object_type)
        dialog.txt_name.setText(data_series.object_name)
        if data_series.variable:
            dialog.cmb_variable.setCurrentText(data_series.variable)
        dialog.txt_legend_label.setText(data_series.legend_label)

        # Set axis radio buttons
        if data_series.axis == "Left":
            dialog.rb_axis_left.setChecked(True)
        else:
            dialog.rb_axis_right.setChecked(True)

        # Unblock signals
        dialog.cmb_type.blockSignals(False)
        dialog.txt_name.blockSignals(False)
        dialog.cmb_variable.blockSignals(False)
        dialog.txt_legend_label.blockSignals(False)
        dialog.rb_axis_left.blockSignals(False)
        dialog.rb_axis_right.blockSignals(False)

        # Update variable combo after unblocking signals if type is set
        if data_series.object_type:
            self._fill_cmb_variable(dialog)
            # Set the variable again after filling the combo
            if data_series.variable:
                dialog.cmb_variable.setCurrentText(data_series.variable)

    def _on_widget_changed(self, dialog):
        """ Handle widget changes to update selected DataSeries """

        current_item = dialog.lst_data_series.currentItem()
        if current_item is None:
            return

        # Get the DataSeries object from the selected item
        data_series = current_item.data(Qt.UserRole)
        if data_series is None:
            return

        # Update DataSeries with widget values
        data_series.object_type = dialog.cmb_type.currentText()
        data_series.object_name = dialog.txt_name.text()
        data_series.variable = dialog.cmb_variable.currentText()
        data_series.legend_label = dialog.txt_legend_label.text()
        data_series.axis = "Left" if dialog.rb_axis_left.isChecked() else "Right"

        # Update the list item text with new string representation
        current_item.setText(str(data_series))

    def _delete_data_series(self, dialog):
        """ Delete selected data series """

        current_item = dialog.lst_data_series.currentItem()
        if current_item is None:
            return

        # Get the current row and remove the item
        current_row = dialog.lst_data_series.currentRow()
        dialog.lst_data_series.takeItem(current_row)

    def _fill_cmb_type(self, dialog):
        # Type
        cmb_type = dialog.cmb_type
        cmb_type.clear()
        cmb_type.addItems(TS_GRAPH_TYPES)

    def _fill_cmb_variable(self, dialog):
        # Variables
        cmb_variable = dialog.cmb_variable
        cmb_variable.blockSignals(True)
        cmb_variable.clear()
        cmb_variable.addItems(TS_GRAPH_VARIABLES[dialog.cmb_type.currentText()])
        cmb_variable.blockSignals(False)

    def set_results_folder(self):
        """ Set results folder """

        # Return if theres one results folder selector dialog already open
        if tools_dr.check_if_already_open('dlg_results_folder_selector', self.results_folder_selector_btn):
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

        rel_path = tools_qgis.get_project_variable('project_results_folder')
        abs_path = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{rel_path}")
        if abs_path is None or not os.path.exists(abs_path) or not os.path.isdir(abs_path):
            tools_qgis.set_project_variable('project_results_folder', None)
            abs_path = None
        if abs_path is not None:
            folder_name = f" - {os.path.basename(abs_path)}"
        else:
            folder_name = ""
        self.set_results_folder_action = QAction(f"Set results folder{folder_name}", self.menu)
        self.set_results_folder_action.triggered.connect(self.set_results_folder)
        self.set_results_folder_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'utilities', '20.png')))

        if abs_path is None or not os.path.exists(abs_path) or not os.path.isdir(abs_path):
            self.load_raster_results_action.setDisabled(True)
            self.profile_action.setDisabled(True)
            self.report_summary_action.setDisabled(True)
            self.time_series_graph_action.setDisabled(True)
            self.load_vector_results_action.setDisabled(True)
        self.time_series_graph_action.setDisabled(True)  # TODO: Remove this when time series graph is implemented

        self.menu.addAction(self.profile_action)
        self.menu.addAction(self.report_summary_action)
        self.menu.addAction(self.time_series_graph_action)
        self.menu.addSeparator()
        self.menu.addAction(self.load_raster_results_action)
        self.menu.addAction(self.load_vector_results_action)
        self.menu.addSeparator()
        self.menu.addAction(self.set_results_folder_action)

    # endregion