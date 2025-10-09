"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import subprocess
import os
from functools import partial

from qgis.PyQt.QtCore import QDateTime
from qgis.PyQt.QtWidgets import QAction, QButtonGroup
from qgis.core import QgsVectorLayer, QgsProject
from qgis.gui import QgsMapToolEmitPoint

from ..dialog import DrAction
from ...ui.ui_manager import DrProfileUi
from ...utils import tools_dr
from ...utils.snap_manager import DrSnapManager
from ....lib import tools_qt, tools_qgis

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    msg = "Matplotlib Python package not found. Do you want to install Matplotlib?"
    if tools_qt.show_question(msg):
        subprocess.run(["python", "-m", "ensurepip"])
        install_matplotlib = subprocess.run(['python', '-m', 'pip', 'install', '-U', 'matplotlib'])
        if install_matplotlib.returncode:
            msg = "Matplotlib cannot be installed automatically. Please install Matplotlib manually."
            tools_qt.show_info_box(msg)
        else:
            msg = "Matplotlib installed successfully. Please restart QGIS."
            tools_qt.show_info_box(msg)


class DrNodeData:

    def __init__(self):

        self.start_point = None
        self.top_elev = None
        self.ymax = None
        self.z1 = None
        self.z2 = None
        self.cat_geom = None
        self.geom = None
        self.slope = None
        self.elev1 = None
        self.elev2 = None
        self.y1 = None
        self.y2 = None
        self.node_id = None
        self.elev = None
        self.code = None
        self.node_1 = None
        self.node_2 = None
        self.total_distance = None
        self.descript = None
        self.data_type = None
        self.surface_type = None
        self.none_values = None


class DrProfileButton(DrAction):
    """ Button 15: Profile """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        # Call ParentDialog constructor
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.snapper_manager = DrSnapManager(self.iface)
        self.vertex_marker = self.snapper_manager.vertex_marker
        self.list_of_selected_nodes = []
        self.nodes = []
        self.links = []
        self.rotation_vd_exist = False
        self.lastnode_datatype = 'REAL'
        self.none_values = []

    def clicked_event(self):

        self.action.setChecked(True)

        # Remove all selections on canvas
        self._remove_selection()

        # Set dialog
        self.dlg_draw_profile = DrProfileUi()
        tools_dr.load_settings(self.dlg_draw_profile)

        # Set allowed node layers for snapping (junction, divider, outfall, storage)
        self.layer_node = tools_qgis.get_layer_by_tablename('inp_junction', show_warning_=False)
        self.allowed_node_layers = []
        for _layer_name in ['inp_junction', 'inp_divider', 'inp_outfall', 'inp_storage']:
            _layer_obj = tools_qgis.get_layer_by_tablename(_layer_name, show_warning_=False)
            if _layer_obj:
                self.allowed_node_layers.append(_layer_obj)

        # Toolbar actions
        action = self.dlg_draw_profile.findChild(QAction, "actionProfile")
        tools_dr.add_icon(action, "131", sub_folder="24x24")
        action.triggered.connect(partial(self._activate_snapping_node))
        self.action_profile = action

        # Set radio button groups
        self.rbg_timestamp = QButtonGroup()
        self.rbg_timestamp.addButton(self.dlg_draw_profile.rb_instant)
        self.rbg_timestamp.addButton(self.dlg_draw_profile.rb_period)

        self.rbg_offsets = QButtonGroup()
        self.rbg_offsets.addButton(self.dlg_draw_profile.rb_depth)
        self.rbg_offsets.addButton(self.dlg_draw_profile.rb_elevation)

        # Set validators
        # self.dlg_draw_profile.txt_min_distance.setValidator(QDoubleValidator())

        # Triggers
        self.dlg_draw_profile.btn_draw_profile.clicked.connect(partial(self._get_profile))
        # self.dlg_draw_profile.btn_clear_profile.clicked.connect(self._clear_profile)
        self.dlg_draw_profile.rb_instant.clicked.connect(partial(self._manage_timestamp_widgets))
        self.dlg_draw_profile.rb_period.clicked.connect(partial(self._manage_timestamp_widgets))
        self.dlg_draw_profile.dlg_closed.connect(partial(tools_dr.save_settings, self.dlg_draw_profile))
        self.dlg_draw_profile.dlg_closed.connect(partial(self._remove_selection, actionpan=True))
        self.dlg_draw_profile.dlg_closed.connect(partial(self._disable_snapping))
        self.dlg_draw_profile.dlg_closed.connect(partial(self._reset_profile_variables))
        self.dlg_draw_profile.dlg_closed.connect(partial(tools_dr.disconnect_signal, 'profile'))

        # Set shortcut keys
        self.dlg_draw_profile.key_escape.connect(partial(tools_dr.close_dialog, self.dlg_draw_profile))

        # Set default values
        self.dlg_draw_profile.rb_instant.setChecked(True)
        self.dlg_draw_profile.rb_depth.setChecked(True)
        self._manage_timestamp_widgets()

        # Restore datetime values
        self._load_user_values()

        # Show form
        tools_dr.open_dialog(self.dlg_draw_profile, dlg_name='profile')

    # region private functions

    def _load_user_values(self):
        dtm_instant_val = tools_dr.get_config_parser('btn_profile', 'dtm_instant', "user", "session")
        dtm_start_val = tools_dr.get_config_parser('btn_profile', 'dtm_start', "user", "session")
        dtm_end_val = tools_dr.get_config_parser('btn_profile', 'dtm_end', "user", "session")
        if dtm_instant_val:
            dtm_instant_qdt = QDateTime.fromString(dtm_instant_val, 'yyyy-MM-dd HH:mm:ss')
            self.dlg_draw_profile.dtm_instant.setDateTime(dtm_instant_qdt)
        if dtm_start_val:
            dtm_start_qdt = QDateTime.fromString(dtm_start_val, 'yyyy-MM-dd HH:mm:ss')
            self.dlg_draw_profile.dtm_start.setDateTime(dtm_start_qdt)
        if dtm_end_val:
            dtm_end_qdt = QDateTime.fromString(dtm_end_val, 'yyyy-MM-dd HH:mm:ss')
            self.dlg_draw_profile.dtm_end.setDateTime(dtm_end_qdt)

    def _reset_profile_variables(self):

        self.initNode = None
        self.endNode = None
        self.first_node = True

    def _manage_timestamp_widgets(self):
        if self.dlg_draw_profile.rb_instant.isChecked():
            self.dlg_draw_profile.dtm_start.setEnabled(False)
            self.dlg_draw_profile.dtm_end.setEnabled(False)
            self.dlg_draw_profile.lbl_period_sep.setEnabled(False)
            self.dlg_draw_profile.dtm_instant.setEnabled(True)
        elif self.dlg_draw_profile.rb_period.isChecked():
            self.dlg_draw_profile.dtm_start.setEnabled(True)
            self.dlg_draw_profile.dtm_end.setEnabled(True)
            self.dlg_draw_profile.lbl_period_sep.setEnabled(True)
            self.dlg_draw_profile.dtm_instant.setEnabled(False)

    def _get_profile(self):

        # Clear main variables
        self.nodes.clear()
        self.links.clear()
        self.nodes = []
        self.links = []
        self.none_values = []

        # Save datetime values
        dtm_instant_val = self.dlg_draw_profile.dtm_instant.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        dtm_start_val = self.dlg_draw_profile.dtm_start.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        dtm_end_val = self.dlg_draw_profile.dtm_end.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        tools_dr.set_config_parser('btn_profile', 'dtm_instant', dtm_instant_val)
        tools_dr.set_config_parser('btn_profile', 'dtm_start', dtm_start_val)
        tools_dr.set_config_parser('btn_profile', 'dtm_end', dtm_end_val)

        # Execute draw profile
        self._draw_profile_v2()

        # # Maximize window (after drawing)
        # self.plot.show()
        # mng = self.plot.get_current_fig_manager()
        # mng.window.showMaximized()

        # if len(self.none_values) > 0:
        #     msg = "There are missing values in these nodes:"
        #     tools_qt.show_info_box(msg, inf_text=self.none_values)

    def _activate_snapping_node(self):

        if hasattr(self, "first_node"):
            self.snapper_manager.remove_marker()
        self.initNode = None if not hasattr(self, "initNode") else self.initNode
        self.endNode = None if not hasattr(self, "endNode") else self.endNode
        self.first_node = True if not hasattr(self, "first_node") else self.first_node

        if self.first_node is False:
            msg = "First node already selected with id: {0}. Select second one."
            msg_params = (self.initNode)
            tools_qgis.show_info(msg, msg_params=msg_params)

        # Set vertex marker propierties
        self.snapper_manager.set_vertex_marker(self.vertex_marker, icon_type=4)

        # Create the appropriate map tool and connect the gotPoint() signal.
        if hasattr(self, "emit_point") and self.emit_point is not None:
            tools_dr.disconnect_signal('profile', 'ep_canvasClicked_snapping_node')
        self.emit_point = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.emit_point)
        self.snapper = self.snapper_manager.get_snapper()
        self.iface.setActiveLayer(self.layer_node)

        tools_dr.connect_signal(self.canvas.xyCoordinates, self._mouse_move,
                                'profile', 'activate_snapping_node_xyCoordinates_mouse_move')
        tools_dr.connect_signal(self.emit_point.canvasClicked, partial(self._snapping_node),
                                'profile', 'ep_canvasClicked_snapping_node')
        # To activate action pan and not move the canvas accidentally we have to override the canvasReleaseEvent.
        # The "e" is the QgsMapMouseEvent given by the function
        self.emit_point.canvasReleaseEvent = lambda e: self._action_pan()

    def _mouse_move(self, point):

        event_point = self.snapper_manager.get_event_point(point=point)

        # Snapping
        result = self.snapper_manager.snap_to_project_config_layers(event_point)
        if result.isValid():
            layer = self.snapper_manager.get_snapped_layer(result)
            if hasattr(self, 'allowed_node_layers') and layer in self.allowed_node_layers:
                self.snapper_manager.add_marker(result, self.vertex_marker)
            else:
                self.vertex_marker.hide()
        else:
            self.vertex_marker.hide()

    def _snapping_node(self, point):   # @UnusedVariable

        # Get clicked point
        event_point = self.snapper_manager.get_event_point(point=point)

        # Snapping
        result = self.snapper_manager.snap_to_project_config_layers(event_point)

        if result.isValid():
            # Only allow features from the configured node layers
            snapped_layer = self.snapper_manager.get_snapped_layer(result)
            if hasattr(self, 'allowed_node_layers') and snapped_layer not in self.allowed_node_layers:
                tools_qgis.show_warning("Please select a node from inp_junction, inp_divider, inp_outfall or inp_storage")
                return
            # Get the feature
            snapped_feat = self.snapper_manager.get_snapped_feature(result)
            element_id = snapped_feat.attribute('code')
            self.element_id = str(element_id)

            if self.first_node:
                self.initNode = element_id
                self.first_node = False
                msg = "Node 1 selected"
                tools_qgis.show_info(msg, parameter=element_id)
                tools_qt.set_widget_text(self.dlg_draw_profile, 'txt_node_init', element_id)
            else:
                if self.element_id == self.initNode or self.element_id == self.endNode:
                    msg = "Node already selected"
                    param = element_id
                    tools_qgis.show_warning(msg, parameter=param)
                    tools_qgis.disconnect_snapping(False, self.emit_point, self.vertex_marker)
                    tools_dr.disconnect_signal('profile')
                    self.dlg_draw_profile.btn_draw_profile.setEnabled(False)
                    # Clear old list arcs
                    # self.dlg_draw_profile.tbl_list_arc.clear()

                    self._remove_selection()
                else:
                    self.endNode = element_id
                    msg = "Node 2 selected"
                    tools_qgis.show_info(msg, parameter=element_id)
                    tools_qt.set_widget_text(self.dlg_draw_profile, 'txt_node_end', element_id)
                    tools_qgis.disconnect_snapping(False, self.emit_point, self.vertex_marker)
                    tools_dr.disconnect_signal('profile')
                    self.dlg_draw_profile.btn_draw_profile.setEnabled(True)

                    # Clear old list arcs
                    # self.dlg_draw_profile.tbl_list_arc.clear()

                # Next profile will be done from scratch
                self.first_node = True

    def _action_pan(self):
        if self.first_node:
            # Set action pan
            self.iface.actionPan().trigger()

    def _draw_profile_v2(self):
        """ Draw profile """
        from swmm_api import __version__ as swmm_api_version
        from swmm_api import read_inp_file, read_out_file
        import pandas as pd
        from ...utils.profile_utils import ProfilePlotter

        # Get parameters
        results_folder = tools_qgis.get_project_variable('project_results_folder')
        if results_folder is None:
            tools_qgis.show_warning("No results folder selected")
            return
        results_folder = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{results_folder}")
        if not os.path.exists(results_folder) or not os.path.isdir(results_folder):
            tools_qgis.show_warning("Invalid results folder")
            return
        if not os.path.exists(os.path.join(results_folder, 'Iber_SWMM.inp')) or \
                not os.path.exists(os.path.join(results_folder, 'Iber_SWMM.out')):
            tools_qgis.show_warning("No Iber_SWMM.inp or Iber_SWMM.out file found")
            return
        timestamp: str = self.dlg_draw_profile.dtm_instant.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        custom_start: str = self.dlg_draw_profile.dtm_start.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        custom_end: str = self.dlg_draw_profile.dtm_end.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        offsets: int = 0 if self.dlg_draw_profile.rb_depth.isChecked() else 1  # 0 - Depth, 1 - Elevation
        plot_type: int = 0 if self.dlg_draw_profile.rb_instant.isChecked() else 1  # 0 - Static, 1 - Dynamic (time series)

        # Define the path of the files
        inputfile = f"{results_folder}{os.sep}Iber_SWMM.inp"
        outputfile = f"{results_folder}{os.sep}Iber_SWMM.out"

        # Load the simulation
        inp = read_inp_file(inputfile)
        out = read_out_file(outputfile)

        out.to_frame()

        # SWMM API and SWMM library versions. Informative.
        print(f'SWMM API version - {swmm_api_version}')
        swmm_version = out.swmm_version
        print(f'SWMM version - {swmm_version}')

        # Dataframe with all results
        # db_out = out2frame(outputfile)

        # Temporal parameters
        write_time_step = out.report_interval
        start_date = out.start_date
        end_date = start_date + out.n_periods * write_time_step

        print(f"Start date = {start_date}")
        print(f"End date   = {end_date}")

        # Result at a specific time 0 - Static
        print(f"Timestamp = {timestamp}")
        timestamp = pd.Timestamp(timestamp)
        print(f"Timestamp = {timestamp}")

        # Period of results, 1 - Dynamic (time series)
        custom_start = pd.Timestamp(custom_start)
        custom_end = pd.Timestamp(custom_end)
        print(f"Custom start = {custom_start}")
        print(f"Custom end   = {custom_end}")

        # Helper function to check if timestamp aligns with simulation timesteps
        def is_valid_timestep(check_time, start_time, timestep_interval):
            """Check if a timestamp aligns with simulation timesteps"""
            time_diff = check_time - start_time
            total_seconds = time_diff.total_seconds()
            timestep_seconds = timestep_interval.total_seconds()

            # Check if the time difference is a multiple of the timestep
            return abs(total_seconds % timestep_seconds) < 1e-6  # Small tolerance for floating point precision

        # Nodes
        start_node = self.initNode
        end_node = self.endNode
        print(f"Start node = {start_node}")
        print(f"End node   = {end_node}")

        # Visualization parameters
        c_inv = "black"
        c_ground_line = "black"
        ground_line_style = "dashed"
        c_crown = "black"
        c_ground = "lightgray"
        lw = 1
        c_water = "cyan"
        c_pipe = "grey"
        mh_width = 2  # TODO: make it scale with the plot size
        offset_ymax = 0.5

        # Create profile plotter
        profile_plotter = ProfilePlotter(
            inp, out, c_inv, c_ground_line, ground_line_style, c_crown, c_ground, c_water, c_pipe,
            lw, mh_width, offset_ymax, offsets
        )

        if plot_type == 0:
            # Check for timestamp
            if not (start_date <= timestamp <= end_date):
                msg_params = (start_date.strftime('%d-%m-%Y %H:%M:%S'), end_date.strftime('%d-%m-%Y %H:%M:%S'))
                tools_qgis.show_warning("The selected time must be within the simulation period. ({0} - {1})", msg_params=msg_params)
                return

            # Check if timestamp aligns with simulation timesteps
            if not is_valid_timestep(timestamp, start_date, write_time_step):
                timestep_minutes = int(write_time_step.total_seconds() / 60)
                tools_qgis.show_warning("The selected timestamp does not align with simulation timesteps. Timestep interval is {0} minutes.", msg_params=(timestep_minutes,))
                return

            fig, ax = profile_plotter.plot_longitudinal(start_node, end_node, timestamp, add_node_labels=False)
            fig.show()

        elif plot_type == 1:
            # Check for custom_start and custom_end
            if not (start_date <= custom_start <= end_date) or not (start_date <= custom_end <= end_date):
                msg_params = (start_date.strftime('%d-%m-%Y %H:%M:%S'), end_date.strftime('%d-%m-%Y %H:%M:%S'))
                tools_qgis.show_warning("The selected time range must be within the simulation period. ({0} - {1})", msg_params=msg_params)
                return
            elif custom_end <= custom_start:
                msg_params = (custom_start.strftime('%d-%m-%Y %H:%M:%S'), custom_end.strftime('%d-%m-%Y %H:%M:%S'))
                tools_qgis.show_warning("The end time must be bigger than the start time. ({0} >= {1})", msg_params=msg_params)
                return

            # Check if custom_start and custom_end align with simulation timesteps
            if not is_valid_timestep(custom_start, start_date, write_time_step):
                timestep_minutes = int(write_time_step.total_seconds() / 60)
                tools_qgis.show_warning("The start time does not align with simulation timesteps. Timestep interval is {0} minutes.", msg_params=(timestep_minutes,))
                return

            if not is_valid_timestep(custom_end, start_date, write_time_step):
                timestep_minutes = int(write_time_step.total_seconds() / 60)
                tools_qgis.show_warning("The end time does not align with simulation timesteps. Timestep interval is {0} minutes.", msg_params=(timestep_minutes,))
                return

            profile_plotter.show_with_slider(start_node, end_node, write_time_step, custom_start, custom_end)

    def _clear_profile(self):
        """ Manage button clear profile and leave form empty """

        # Clear list of nodes and arcs
        self.list_of_selected_nodes = []
        self.list_of_selected_arcs = []
        self.arcs = []
        self.nodes = []

        # Clear widgets
        # self.dlg_draw_profile.tbl_list_arc.clear()
        tools_qt.set_widget_text(self.dlg_draw_profile, 'txt_node_init', '')
        tools_qt.set_widget_text(self.dlg_draw_profile, 'txt_node_end', '')
        self.action_profile.setDisabled(False)
        self.dlg_draw_profile.btn_draw_profile.setEnabled(False)

        # Clear selection
        self._remove_selection()
        self._reset_profile_variables()

    def _delete_profile(self):
        """ Delete profile """

        selected_list = self.dlg_load.tbl_profiles.selectionModel().selectedRows()
        if len(selected_list) == 0:
            msg = "Any record selected"
            tools_qgis.show_warning(msg)
            return

        # Selected item from list
        profile_id = self.dlg_load.tbl_profiles.currentItem().text()

        extras = f'"profile_id":"{profile_id}", "action":"delete"'
        body = tools_dr.create_body(extras=extras)
        result = tools_dr.execute_procedure('gw_fct_setprofile', body)
        if result and 'message' in result:
            message = f"{result['message']}"
            tools_qgis.show_info(message)

        # Remove profile from list
        self.dlg_load.tbl_profiles.takeItem(self.dlg_load.tbl_profiles.row(self.dlg_load.tbl_profiles.currentItem()))

    def _remove_selection(self, actionpan=False):
        """ Remove selected features of all layers """

        for layer in self.canvas.layers():
            if type(layer) is QgsVectorLayer:
                layer.removeSelection()
        self.canvas.refresh()
        if actionpan:
            self.iface.actionPan().trigger()

    def _disable_snapping(self):
        """ Disable snapping """
        from qgis.core import QgsProject

        # Get the current snapping configuration
        snapping_config = QgsProject.instance().snappingConfig()

        # Disable snapping
        snapping_config.setEnabled(False)

        # Apply the configuration to the project
        QgsProject.instance().setSnappingConfig(snapping_config)

    # endregion
