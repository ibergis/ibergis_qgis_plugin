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

from qgis.PyQt.QtCore import pyqtSignal, QMetaMethod
from qgis.PyQt.QtWidgets import QTextEdit
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsField, QgsFields, QgsFeature, \
    QgsProject

from ..utils.generate_swmm_inp.generate_swmm_inp_file import GenerateSwmmInpFile
from ..utils import tools_gw
from ... import global_vars
from ...lib import tools_log, tools_qt, tools_db, tools_qgis, tools_os
from .task import GwTask
from .epa_file_manager import GwEpaFileManager


def lerp_progress(subtask_progress: int, global_min: int, global_max: int) -> int:
    global_progress = global_min + ((subtask_progress - 0) / (100 - 0)) * (global_max - global_min)

    return int(global_progress)


class GwExecuteModel(GwTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')

    # Progress percentages
    PROGRESS_INIT = 0
    PROGRESS_MESH_FILES = 15
    PROGRESS_STATIC_FILES = 20
    PROGRESS_HYETOGRAPHS = 35
    PROGRESS_RAIN = 45
    PROGRESS_INP = 70
    PROGRESS_IBER = 90
    PROGRESS_END = 100

    def __init__(self, description: str, params: dict, timer=None):
        """ Constructor for thread GwExecuteModel
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

        self.dialog.btn_cancel.setEnabled(False)
        self.dialog.btn_accept.setEnabled(True)

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
            # Mesh files
            if self.do_export:
                # Export mesh
                self.progress_changed.emit("Export files", self.PROGRESS_INIT, "Exporting mesh files...", False)
                mesh_id = tools_qt.get_combo_value(self.dialog, 'cmb_mesh')
                self._copy_mesh_files(mesh_id)
                self.progress_changed.emit("Export files", self.PROGRESS_MESH_FILES, "done!", True)

                # Copy static files
                self.progress_changed.emit("Export files", self.PROGRESS_MESH_FILES, "Copying static files...", False)
                self._copy_static_files()
                self.progress_changed.emit("Export files", self.PROGRESS_STATIC_FILES, "done!", True)

                # Create hyetograph file
                self.progress_changed.emit("Export files", self.PROGRESS_STATIC_FILES, "Creating hyetograph files...", False)
                self._create_hyetograph_file()
                self.progress_changed.emit("Export files", self.PROGRESS_HYETOGRAPHS, "done!", True)

                # Create rain file
                self.progress_changed.emit("Export files", self.PROGRESS_HYETOGRAPHS, "Creating rain files...", False)
                self._create_rain_file()
                self.progress_changed.emit("Export files", self.PROGRESS_RAIN, "done!", True)
                # return

            # INP file
            if self.do_generate_inp:
                self.progress_changed.emit("Generate INP", self.PROGRESS_RAIN, "Generating INP...", False)
                self._generate_inp()
                self.progress_changed.emit("Generate INP", self.PROGRESS_INP, "done!", True)
                self.progress_changed.emit("Generate INP", self.PROGRESS_INP, self.generate_inp_infolog, True)

            if self.do_run:
                self.progress_changed.emit("Run Iber", self.PROGRESS_INP, "Running Iber software...", False)
                self._run_iber()
                self.progress_changed.emit("Run Iber", self.PROGRESS_IBER, "done!", True)

            self.progress_changed.emit("", self.PROGRESS_END, "", True)
        except Exception as e:
            print(f"Exception in ExecuteModel thread: {e}")
            return False

        return True

    def _copy_mesh_files(self, mesh_id):

        sql = f"SELECT iber2d, roof, losses FROM cat_file WHERE id = '{mesh_id}'"
        row = self.dao.get_row(sql)
        self.progress_changed.emit("Export files", lerp_progress(10, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
        if row:
            iber2d_content, roof_content, losses_content = row

            # Write content to files
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
                self.progress_changed.emit("Export files", lerp_progress(50, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                # cn_multiplier
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_scs_cn_multiplier'"
                row = self.dao.get_row(sql)
                cn_multiplier = row[0] if row else 0
                self.progress_changed.emit("Export files", lerp_progress(60, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                # ia_coeff
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_scs_ia_coefficient'"
                row = self.dao.get_row(sql)
                ia_coeff = row[0] if row else 0
                self.progress_changed.emit("Export files", lerp_progress(70, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                # start_time
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_starttime'"
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

    def _write_to_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    def _copy_static_files(self):
        folder = Path(global_vars.plugin_dir) / "resources" / "drain"
        file_names = ["Iber_Problemdata.dat", "Iber_SWMM.ini"]
        for i, file_name in enumerate(file_names):
            shutil.copy(folder / file_name, self.folder_path)
            self.progress_changed.emit("Export files", lerp_progress(lerp_progress(i, 0, len(file_names)), self.PROGRESS_MESH_FILES, self.PROGRESS_STATIC_FILES), '', False)

    def _create_hyetograph_file(self):
        file_name = Path(self.folder_path) / "Iber_Hyetograph.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = self.dao.get_row(sql)
        rain_class = int(row[0]) if row and row[0] else 0

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

                sql = f"""
                    SELECT time, value 
                    FROM cat_timeseries_value 
                    WHERE timeseries ='{ht_row.timeseries}'
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

    def _generate_inp(self):
        go2epa_params = {"dialog": self.dialog, "export_file_path": f"{self.folder_path}{os.sep}Iber_SWMM.inp", "is_subtask": True}
        self.generate_inp_task = GwEpaFileManager("Go2Epa", go2epa_params, None)
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

        self.progress_changed.emit("Run Iber", lerp_progress(20, self.PROGRESS_INP, self.PROGRESS_IBER), '', False)

        result = subprocess.run([iber_exe_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                cwd=self.folder_path  # Execute from wanted folder
                                )
        print("IberPlus execution finished.")
        print("Exit code:", result.returncode)
        print("Standard Output:")
        print(result.stdout)
        print("Standard Error:")
        print(result.stderr)
        self.progress_changed.emit("Run Iber", lerp_progress(100, self.PROGRESS_INP, self.PROGRESS_IBER), f'{result.stdout}', True)

    # endregion