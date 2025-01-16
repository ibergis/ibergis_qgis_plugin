"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from pathlib import Path
import geopandas as gpd
import threading
import traceback

from qgis.PyQt.QtCore import pyqtSignal, QMetaMethod
from qgis.PyQt.QtWidgets import QTextEdit
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsField, QgsFields, QgsFeature, \
    QgsProject

from ..utils.generate_swmm_inp.generate_swmm_inp_file import GenerateSwmmInpFile
from ..utils import tools_dr
from ... import global_vars
from ...lib import tools_log, tools_qt, tools_db, tools_qgis, tools_os
from .task import DrTask
from .epa_file_manager import DrEpaFileManager


def lerp_progress(subtask_progress: int, global_min: int, global_max: int) -> int:
    global_progress = global_min + ((subtask_progress - 0) / (100 - 0)) * (global_max - global_min)

    return int(global_progress)


class DrExecuteModel(DrTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')

    # Progress percentages
    PROGRESS_INIT = 0
    PROGRESS_CONFIG = 5
    PROGRESS_MESH_FILES = 25
    PROGRESS_STATIC_FILES = 30
    PROGRESS_INLET = 35
    PROGRESS_HYETOGRAPHS = 40
    PROGRESS_RAIN = 50
    PROGRESS_INP = 70
    PROGRESS_IBER = 97
    PROGRESS_END = 100

    def __init__(self, description: str, params: dict, timer=None):
        """ Constructor for thread DrExecuteModel
            :param description: description of the task (str)
            :param params: possible params: {"dialog": QDialog, "folder_path": str, "do_generate_inp": bool, "do_export": bool, "do_run": bool, "do_import": bool}
            :param timer: QTimer
        """

        super().__init__(description)
        self.params = params
        self.json_result = None
        self.rpt_result = None
        self.fid = 140
        self.function_name = None
        self.timer = timer
        self.dao = None
        self.init_params()
        self.generate_inp_infolog = None


    def init_params(self):
        self.dialog = self.params.get('dialog')
        self.folder_path = self.params.get('folder_path')
        self.do_generate_inp = self.params.get('do_generate_inp', True)
        self.do_export = self.params.get('do_export', True)
        self.do_run = self.params.get('do_run', True)
        self.do_import = self.params.get('do_import', True)


    def run(self):

        super().run()
        print(f"{self.description()} -> {threading.get_ident()}")
        self.dao = global_vars.gpkg_dao_data.clone()
        tools_log.log_info(f"Task 'Execute model' execute function 'def _execute_model(self)'")
        status = self._execute_model()

        # self._close_dao()

        return status


    def finished(self, result):

        super().finished(result)

        self.dialog.btn_cancel.setVisible(False)
        self.dialog.btn_accept.setVisible(False)
        self.dialog.btn_close.setVisible(True)

        # self._close_file()
        if self.timer:
            self.timer.stop()
        if self.isCanceled():
            return

        # If Database exception, show dialog after task has finished
        if global_vars.session_vars['last_error']:
            tools_qt.show_exception_message(msg=global_vars.session_vars['last_error_msg'])


    def cancel(self):

        tools_qgis.show_info(f"Task canceled - {self.description()}")
        # self._close_file()
        super().cancel()


    def _close_dao(self, dao=None):

        if dao is None:
            dao = self.dao

        try:
            if dao:
                dao.close_db()
                del dao
        except Exception:
            pass


    # region private functions

    def _execute_model(self):
        try:
            if self.isCanceled():
                return False
            # Mesh files
            if self.do_export:
                # Export config
                self.progress_changed.emit("Export files", self.PROGRESS_INIT, "Exporting config files...", False)
                self._create_config_files()
                self.progress_changed.emit("Export files", self.PROGRESS_CONFIG, "done!", True)

                if self.isCanceled():
                    return False

                # Export mesh
                self.progress_changed.emit("Export files", self.PROGRESS_CONFIG, "Exporting mesh files...", False)
                mesh_id = tools_qt.get_combo_value(self.dialog, 'cmb_mesh')
                self._copy_mesh_files(mesh_id)
                self.progress_changed.emit("Export files", self.PROGRESS_MESH_FILES, "done!", True)

                if self.isCanceled():
                    return False

                # Copy static files
                self.progress_changed.emit("Export files", self.PROGRESS_MESH_FILES, "Copying static files...", False)
                self._copy_static_files()
                self.progress_changed.emit("Export files", self.PROGRESS_STATIC_FILES, "done!", True)

                if self.isCanceled():
                    return False

                # Create inlet file
                self.progress_changed.emit("Export files", self.PROGRESS_STATIC_FILES, "Creating inlet files...", False)
                self._create_inlet_file()
                self.progress_changed.emit("Export files", self.PROGRESS_INLET, "done!", True)

                if self.isCanceled():
                    return False

                # Create hyetograph file
                self.progress_changed.emit("Export files", self.PROGRESS_INLET, "Creating hyetograph files...", False)
                self._create_hyetograph_file()
                self.progress_changed.emit("Export files", self.PROGRESS_HYETOGRAPHS, "done!", True)

                if self.isCanceled():
                    return False

                # Create rain file
                self.progress_changed.emit("Export files", self.PROGRESS_HYETOGRAPHS, "Creating rain files...", False)
                self._create_rain_file()
                self.progress_changed.emit("Export files", self.PROGRESS_RAIN, "done!", True)

            if self.isCanceled():
                return False

            # INP file
            if self.do_generate_inp:
                self.progress_changed.emit("Generate INP", self.PROGRESS_RAIN, "Generating INP...", False)
                self._generate_inp()
                self.progress_changed.emit("Generate INP", self.PROGRESS_INP, "done!", True)
                self.progress_changed.emit("Generate INP", self.PROGRESS_INP, self.generate_inp_infolog, True)

            if self.isCanceled():
                return False

            if self.do_run:
                self.progress_changed.emit("Run Iber", self.PROGRESS_INP, "Running Iber software...", False)
                self._run_iber()
                self.progress_changed.emit("Run Iber", self.PROGRESS_IBER, "done!", True)

            if self.isCanceled():
                return False

            self.progress_changed.emit("", self.PROGRESS_END, "", True)
        except Exception as e:
            print(f"Exception in ExecuteModel thread: {e}")
            self.progress_changed.emit("ERROR", None, f"Exception in ExecuteModel thread: {e}\n {traceback.format_exc()}", True)
            return False

        return True

    def _create_config_files(self):
        # Iber_Results.dat
        file_name = Path(self.folder_path) / "Iber_Results.dat"
        mapper = {
            "result_depth": "Depth",
            "result_vel": "Velocity",
            "result_specific_discharge": "Specific_Discharge",
            "result_water_elevation": "Water_Elevation",
            "result_fronde_number": "Froude_Number",
            "result_localtime_step": "Local_Time_Step",
            "result_manning_coefficient": "Manning_Coefficient",
            "result_critical_diameter": "Critical_Diameter",
            "result_max_depth": "Maximum_Depth",
            "result_max_vel": "Maximum_Velocity",
            "result_max_spec_discharge": "Maximum_Spec_Discharge",
            "result_max_water_elev": "Maximum_Water_Elev",
            "result_max_localtime_step": "Maximum_Local_Time_Step",
            "result_max_critical_diameter": "Maximum_Critical_Diameter",
            "result_hazard_rd9_2008": "Hazard RD9/2008",
            "result_hazard_aca2003": "Hazard ACA2003",
            "result_depth_vector": "Depth_vector",
            "result_bed_shear_stress": "Bed_Shear_Stress",
            "result_max_bed_shear_stress": "Maximum_Bed_Shear_Stress",
            "result_energy": "Energy",
            "result_steamlines": "Streamlines",
            "result_results_raster": "Raster interpolation",
            "result_results_raster_cell": "Raster cell size",
        }
        sql = "SELECT parameter, value FROM config_param_user WHERE parameter like 'result_%'"
        rows = self.dao.get_rows(sql)
        if rows:
            with open(file_name, 'w', newline='') as dat_file:
                for row in rows:
                    value = row['value']
                    if value in (None, "True", "False"):
                        value = "1" if value == "True" else "0"
                    parameter = mapper.get(row['parameter'], row['parameter'])
                    line = f"{value}\t{parameter}\n"
                    dat_file.write(line)

        # Iber_SWMM.dat
        file_name = Path(self.folder_path) / "Iber_SWMM.dat"
        general_options_1 = "1"
        general_options_2 = "1"
        report_continuity = "1"
        report_flowstats = "1"
        report_controls = "1"
        report_input = "1"
        sql = "SELECT parameter, value FROM config_param_user " \
              "WHERE parameter IN ('plg_swmm_options', 'plg_swmm_outlet', " \
              "'inp_report_continuity', 'inp_report_flowstats', 'inp_report_controls', 'inp_report_input')"
        rows = self.dao.get_rows(sql)
        if rows:
            for row in rows:
                parameter = row['parameter']
                value = row['value']
                if parameter == 'plg_swmm_options':
                    general_options_1 = value
                elif parameter == 'plg_swmm_outlet':
                    general_options_2 = "1" if value == "True" else "0"
                elif parameter == 'inp_report_continuity':
                    report_continuity = "1" if value == "YES" else "0"
                elif parameter == 'inp_report_flowstats':
                    report_flowstats = "1" if value == "YES" else "0"
                elif parameter == 'inp_report_controls':
                    report_controls = "1" if value == "YES" else "0"
                elif parameter == 'inp_report_input':
                    report_input = "1" if value == "YES" else "0"

        with open(file_name, 'w', newline='') as dat_file:
            line = f"Iber-SWMM Version 1.0\n" \
                   f"1\n" \
                   f"General options:\n" \
                   f"{general_options_1}\n" \
                   f"{general_options_2}\n" \
                   f"Discharge results\n" \
                   f"{report_continuity} {report_flowstats} {report_controls} {report_input}\n"
            dat_file.write(line)

    def _copy_mesh_files(self, mesh_id):

        sql = f"SELECT iber2d, roof, losses FROM cat_file WHERE id = '{mesh_id}'"
        row = self.dao.get_row(sql)
        self.progress_changed.emit("Export files", lerp_progress(10, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
        if row:
            iber2d_content, roof_content, losses_content = row

            # Write content to files
            project_name, result_iber_format, iber2d_options = self._get_iber2d_options()
            iber2d_lines = iber2d_content.split('\n')
            if iber2d_lines[0] == "MATRIU":
                iber2d_content = f"{project_name}\n{result_iber_format}\n{iber2d_options}\n{iber2d_content}"
            else:
                iber2d_lines[1] = f"{result_iber_format}\n{iber2d_options}"
                iber2d_content = '\n'.join(iber2d_lines)

            self._write_to_file(f'{self.folder_path}{os.sep}Iber2D.dat', iber2d_content)
            self.progress_changed.emit("Export files", lerp_progress(30, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            if roof_content:
                self._write_to_file(f'{self.folder_path}{os.sep}Iber_SWMM_roof.dat', roof_content)
            self.progress_changed.emit("Export files", lerp_progress(40, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            if not losses_content:
                losses_content = '0'
            else:
                # Losses method
                sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_method'"
                row = self.dao.get_row(sql)
                losses_method = row[0] if row and row[0] is not None else 2
                if losses_method == '0':
                    losses_content = '0'
                else:
                    self.progress_changed.emit("Export files", lerp_progress(50, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # cn_multiplier
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_scs_cn_multiplier'"
                    row = self.dao.get_row(sql)
                    cn_multiplier = row[0] if row else 1
                    self.progress_changed.emit("Export files", lerp_progress(60, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # ia_coeff
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_scs_ia_coefficient'"
                    row = self.dao.get_row(sql)
                    ia_coeff = row[0] if row else 0.2
                    self.progress_changed.emit("Export files", lerp_progress(70, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # start_time
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_starttime'"
                    row = self.dao.get_row(sql)
                    start_time = row[0] if row else 0
                    self.progress_changed.emit("Export files", lerp_progress(80, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # Replace first line
                    new_first_line = f"{losses_method} {cn_multiplier} {ia_coeff} {start_time}"
                    losses_content_lines = losses_content.split('\n')
                    losses_content_lines[0] = new_first_line
                    losses_content = '\n'.join(losses_content_lines)
            self.progress_changed.emit("Export files", lerp_progress(90, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            self._write_to_file(f'{self.folder_path}{os.sep}Iber_Losses.dat', losses_content)
            self.progress_changed.emit("Export files", lerp_progress(100, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

    def _get_iber2d_options(self):

        sql = "SELECT parameter, value FROM config_param_user " \
              "WHERE parameter IN ('project_name','options_delta_time','options_tmax','options_rank_results'," \
              "'options_order','options_cfl','options_wetdry_edge','options_viscosity_coeff','options_t0'," \
              "'options_simulation_details','options_simulation_new','options_plan_id','options_simulation_plan'," \
              "'options_timeseries','result_iber_format');"
        rows = self.dao.get_rows(sql)
        if not rows:
            return 'OPTIONS_ERROR', "-9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999 -9999"

        options = {}
        for row in rows:
            parameter = row['parameter']
            value = row['value']
            if value is None:
                value = "0"
            if parameter == 'options_simulation_plan':
                value = "Enabled" if value == "True" else "Disabled"
            elif parameter == 'options_plan_id':
                value = "0"
            elif parameter == 'options_simulation_details':
                value = "1" if value == "True" else "0"
            options[parameter] = value

        project_name = options.get('project_name', 'test')
        result_iber_format = options.get('result_iber_format', '2')
        options_delta_time = options.get('options_delta_time', '0')
        options_tmax = options.get('options_tmax', '0')
        options_rank_results = options.get('options_rank_results', '0')
        options_order = options.get('options_order', '0')
        options_cfl = options.get('options_cfl', '0')
        options_wetdry_edge = options.get('options_wetdry_edge', '0')
        options_viscosity_coeff = options.get('options_viscosity_coeff', '0')
        options_t0 = options.get('options_t0', '0')
        options_simulation_details = options.get('options_simulation_details', '0')
        options_simulation_new = options.get('options_simulation_new', '0')
        options_plan_id = options.get('options_plan_id', '0')
        options_simulation_plan = options.get('options_simulation_plan', '0')
        options_timeseries = options.get('options_timeseries', '0')

        options_str = f"{options_delta_time} {options_tmax} {options_rank_results} {options_order} {options_cfl} {options_wetdry_edge} {options_viscosity_coeff} {options_t0} {options_simulation_details} {options_simulation_new} {options_plan_id} {options_simulation_plan} {options_timeseries}"
        return project_name, result_iber_format, options_str


    def _write_to_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    def _copy_static_files(self):
        folder = Path(global_vars.plugin_dir) / "resources" / "drain"
        file_names = ["Iber_Problemdata.dat", "Iber_SWMM.ini"]
        for i, file_name in enumerate(file_names):
            shutil.copy(folder / file_name, self.folder_path)
            self.progress_changed.emit("Export files", lerp_progress(lerp_progress(i, 0, len(file_names)), self.PROGRESS_MESH_FILES, self.PROGRESS_STATIC_FILES), '', False)

    def _create_inlet_file(self):
        file_name = Path(self.folder_path) / "Iber_SWMM_inlet_info.dat"

        sql = "SELECT gully_id, outlet_type, node_id, xcoord, ycoord, zcoord, width, length, depth, method, weir_cd, " \
              "orifice_cd, a_param, b_param, efficiency FROM vi_inlet"
        rows = self.dao.get_rows(sql)

        # Fetch column names
        column_names = ['gully_id', 'outlet_type', 'node_id', 'xcoord', 'ycoord', 'zcoord', 'width', 'length',
                        'depth', 'method', 'weir_cd', 'orifice_cd', 'a_param', 'b_param', 'efficiency']
        if rows:
            column_names = [key for key in rows[0].keys()]

        with open(file_name, 'w', newline='') as dat_file:
            # Write column headers
            header_str = f"{' '.join(column_names)}\n"
            dat_file.write(header_str)
            transform_dict = {None: -9999, 'TO NETWORK': 'To_network', 'SINK': 'Sink'}
            for row in rows:
                values = []
                for value in row:
                    value_str = str(transform_dict.get(value, value))
                    values.append(value_str)
                values_str = f"{' '.join(values)}\n"
                dat_file.write(values_str)

    def _create_hyetograph_file(self):
        file_name = Path(self.folder_path) / "Iber_Hyetograph.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = self.dao.get_row(sql)
        rain_class = int(row[0]) if row and row[0] else 0

        # options_setallhyetografs
        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_setallhyetografs'"
        row = self.dao.get_row(sql)
        timeseries_override = row[0] if row else None

        if rain_class != 1:
            file_name.write_text("Hyetographs\n0\nEnd\n")
            return

        gdf = gpd.read_file(global_vars.gpkg_dao_data.db_filepath, layer="hyetograph")
        gdf['x'] = gdf.geometry.x
        gdf['y'] = gdf.geometry.y
        self.progress_changed.emit("Export files", lerp_progress(10, self.PROGRESS_STATIC_FILES, self.PROGRESS_HYETOGRAPHS), '', False)

        with open(file_name, "w") as file:
            file.write("Hyetographs\n")
            file.write(f"{len(gdf)}\n")

            for i, ht_row in enumerate(gdf.itertuples(), start=1):
                file.write(f"{i}\n")
                file.write(f"{ht_row.x} {ht_row.y}\n")
                timeseries = timeseries_override if timeseries_override not in (None, '') else ht_row.timeseries

                sql = f"""
                    SELECT time, value
                    FROM cat_timeseries_value
                    WHERE timeseries ='{timeseries}'
                """
                ts_rows = self.dao.get_rows(sql)
                if ts_rows:
                    file.write(f"{len(ts_rows)}\n")
                    for ts_row in ts_rows:
                        hours, minutes = map(int, ts_row["time"].split(":"))
                        seconds = hours * 3600 + minutes * 60
                        file.write(f"{seconds} {ts_row['value']}\n")
                self.progress_changed.emit("Export files", lerp_progress(lerp_progress(i, 10, len(gdf)), self.PROGRESS_STATIC_FILES, self.PROGRESS_HYETOGRAPHS), '', False)

            file.write("End\n")

    def _create_rain_file(self):
        file_name = Path(self.folder_path) / "Iber_Rain.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = self.dao.get_row(sql)
        rain_class = int(row[0]) if row and row[0] else 0
        self.progress_changed.emit("Export files", lerp_progress(50, self.PROGRESS_HYETOGRAPHS, self.PROGRESS_RAIN), '', False)

        if rain_class != 2:
            file_name.write_text(f"{rain_class} 0\n")
            return

        # options_setrainfall_raster
        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_setrainfall_raster'"
        row = self.dao.get_row(sql)
        raster_id = row[0] if row else None
        if raster_id is None:
            file_name.write_text(f"{rain_class} 0\n")
            return

        # get information about raster
        sql = f"SELECT idval, raster_type FROM cat_raster WHERE id = '{raster_id}'"
        row = self.dao.get_row(sql)

        if not row:
            raise Exception(f"Raster data not found. Raster id: {raster_id}.")

        raster_idval = row["idval"]
        raster_type = row["raster_type"]

        if raster_type not in ("Intensity", "Volume"):
            raise Exception(f"Invalid raster type: {raster_type}.")

        raster_type_code = 0 if raster_type == "Intensity" else 1

        # get raster values
        sql = f"""
                SELECT time, fname
                FROM cat_raster_value
                WHERE raster ='{raster_idval}'
            """
        raster_rows = self.dao.get_rows(sql)

        if not raster_rows:
            raise Exception(f"Raster values not found. Raster idval: {raster_idval}.")

        def str2seconds(time: str) -> int:
            hours, minutes = map(int, time.split(":"))
            seconds = hours * 3600 + minutes * 60
            return seconds

        times = [str2seconds(row["time"]) for row in raster_rows]
        paths = [Path(row["fname"]) for row in raster_rows]

        project_folder = Path(self.dao.db_filepath).parent
        commom_path = paths[0].parent

        # check if all parents are the same
        if not all(path.parent == commom_path for path in paths):
            raise Exception(
                f"Not all rasters are in the same folder. Raster idval: {raster_idval}."
            )

        with open(file_name, "w") as file:
            file.write(f"{rain_class} {raster_type_code}\n")
            file.write(f"{project_folder / commom_path}\n")
            file.write(f"{len(times)}\n")
            for seconds, path in zip(times, paths):
                file.write(f'{seconds} "{path.name}"\n')

    def _generate_inp(self):
        go2epa_params = {"dialog": self.dialog, "export_file_path": f"{self.folder_path}{os.sep}Iber_SWMM.inp", "is_subtask": True}
        self.generate_inp_task = DrEpaFileManager("Go2Epa", go2epa_params, None)
        self.generate_inp_task.debug_mode = False
        self.generate_inp_task.progress_changed.connect(self._generate_inp_progress_changed)
        result = self.generate_inp_task._export_inp()
        return result

    def _generate_inp_progress_changed(self, progress, text):

        self.progress_changed.emit("Generate INP algorithm", lerp_progress(progress, self.PROGRESS_RAIN, self.PROGRESS_INP), text, True)
        self.generate_inp_infolog = text

    def _run_iber(self):
        iber_exe_path = f"{global_vars.plugin_dir}{os.sep}resources{os.sep}drain{os.sep}IberPlus.exe"

        if not os.path.exists(iber_exe_path):
            self.error_msg = f"File not found: {iber_exe_path}"
            return False

        # Temporarely copy files needed for iber to run
        source_folder = f"{global_vars.plugin_dir}{os.sep}resources{os.sep}drain{os.sep}temp_add_files"
        destination_folder = self.folder_path
        # Get a list of all files in the source folder
        files = os.listdir(source_folder)

        # Copy each file to the destination folder
        for file in files:
            source_path = os.path.join(source_folder, file)
            destination_path = os.path.join(destination_folder, file)
            shutil.copy2(source_path, destination_path)  # shutil.copy2 preserves metadata

        init_progress = lerp_progress(10, self.PROGRESS_INP, self.PROGRESS_IBER)
        self.progress_changed.emit("Run Iber", init_progress, '', False)

        process = subprocess.Popen([iber_exe_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   cwd=self.folder_path,
                                   bufsize=1,
                                   creationflags=subprocess.CREATE_NO_WINDOW)

        # Read output in real-time
        while not self.isCanceled():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                try:
                    # 0.000        1.00000    13:58:47:68       0.000       0.000     0.00%        --
                    output_parts = [x for x in output.strip().split(' ') if x != '']
                    output_percentage = output_parts[5].replace('%', '')
                    iber_percentage = lerp_progress(int(float(output_percentage)), init_progress, self.PROGRESS_IBER)
                except:
                    iber_percentage = None
                self.progress_changed.emit("Run Iber", iber_percentage, f'{output.strip()}', True)

        if process.poll() is None:
            process.terminate()

        # Wait for the process to finish and get the return code
        return_code = process.wait()

        print(f"IberPlus execution finished. Return code: {return_code}")

        self.progress_changed.emit("Run Iber", lerp_progress(100, self.PROGRESS_INP, self.PROGRESS_IBER), f'', True)


    # endregion
