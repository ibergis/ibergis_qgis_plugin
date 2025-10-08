"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from functools import partial
from typing import Optional, Literal

from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtCore import Qt, QDateTime
from qgis.core import QgsProject

from ..dialog import DrAction
from ...ui.ui_manager import DrTimeseriesGraphUi
from ...utils import tools_dr
from ....lib import tools_qgis
from ....core.utils.timeseries_plotter import TimeseriesPlotter, DataSeries as TSDataSeries


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


class DrTimeseriesGraphButton(DrAction):
    """ Button 19: Time Series Graph """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
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

        # Connect buttons
        self.ts_graph_selection_dlg.btn_accept.clicked.connect(partial(self._show_timeseries_plot, self.ts_graph_selection_dlg))
        self.ts_graph_selection_dlg.btn_cancel.clicked.connect(self.ts_graph_selection_dlg.close)

        # Initialize date fields with simulation dates if available
        self._initialize_date_fields(self.ts_graph_selection_dlg)

        tools_dr.open_dialog(self.ts_graph_selection_dlg, dlg_name='timeseries_graph')

    # region private functions

    def _add_data_series(self, dialog):
        """ Add empty data series and select it """

        # If list is empty, use current widget values
        if dialog.lst_data_series.count() == 0:
            object_type = dialog.cmb_type.currentText()
            object_name = dialog.txt_name.text()
            variable = dialog.cmb_variable.currentText()
            legend_label = dialog.txt_legend_label.text()
            axis = "Left" if dialog.rb_axis_left.isChecked() else "Right"
            data_series = DataSeries(object_type, object_name, variable, legend_label, axis)
        else:
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

    def _initialize_date_fields(self, dialog):
        """ Initialize date fields with simulation dates if available """

        results_folder = tools_qgis.get_project_variable('project_results_folder')
        if not results_folder:
            return

        results_folder = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{results_folder}")
        output_file = os.path.join(results_folder, 'Iber_SWMM.out')

        if not os.path.exists(output_file):
            return

        try:
            from swmm_api import read_out_file
            swmm_out = read_out_file(output_file)

            write_time_step = swmm_out.report_interval
            start_date = swmm_out.start_date
            end_date = start_date + swmm_out.n_periods * write_time_step
            # Set start and end dates from simulation
            start_dt = QDateTime(start_date)
            end_dt = QDateTime(end_date)

            dialog.dt_startdate.setDateTime(start_dt)
            dialog.dt_enddate.setDateTime(end_dt)

            swmm_out.close()
        except Exception as e:
            print(f"Could not initialize date fields: {e}")

    def _show_timeseries_plot(self, dialog):
        """ Show the timeseries plot based on user selections """

        # Get results folder
        results_folder = tools_qgis.get_project_variable('project_results_folder')
        if not results_folder:
            tools_qgis.show_warning("No results folder selected", dialog=dialog)
            return

        results_folder = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{results_folder}")
        output_file = os.path.join(results_folder, 'Iber_SWMM.out')

        if not os.path.exists(output_file):
            tools_qgis.show_warning("No Iber_SWMM.out file found in results folder", dialog=dialog)
            return

        # Get all data series from the list
        data_series_list = []
        for i in range(dialog.lst_data_series.count()):
            item = dialog.lst_data_series.item(i)
            data_series = item.data(Qt.UserRole)
            if data_series:
                # Validate data series
                if not data_series.object_type:
                    tools_qgis.show_warning(f"Data series at position {i + 1} is missing object type", dialog=dialog)
                    return
                if data_series.object_type != 'System' and not data_series.object_name:
                    tools_qgis.show_warning(f"Data series at position {i + 1} is missing object name", dialog=dialog)
                    return
                if not data_series.variable:
                    tools_qgis.show_warning(f"Data series at position {i + 1} is missing variable", dialog=dialog)
                    return

                # Convert to TSDataSeries (plotter's DataSeries class)
                ts_data_series = TSDataSeries(
                    object_type=data_series.object_type,
                    object_name=data_series.object_name,
                    variable=data_series.variable,
                    legend_label=data_series.legend_label,
                    axis=data_series.axis
                )
                data_series_list.append(ts_data_series)

        if not data_series_list:
            tools_qgis.show_warning("No data series to plot. Please add at least one data series.", dialog=dialog)
            return

        # Get time period settings
        start_date = dialog.dt_startdate.dateTime().toPyDateTime()
        end_date = dialog.dt_enddate.dateTime().toPyDateTime()
        use_elapsed_time = dialog.rb_elapsed_time.isChecked()

        # Create plotter and show plot
        try:
            plotter = TimeseriesPlotter(output_file)
            plotter.show_plot(
                data_series_list=data_series_list,
                start_date=start_date,
                end_date=end_date,
                use_elapsed_time=use_elapsed_time,
                title="SWMM Time Series"
            )
        except Exception as e:
            tools_qgis.show_warning(f"Error creating plot: {e}", dialog=dialog)
            print(f"Plot error details: {e}")

    # endregion

