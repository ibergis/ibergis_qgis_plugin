"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import shutil
import sys
import json
from pathlib import Path

from functools import partial
from sip import isdeleted
from time import time
from datetime import timedelta

from qgis.PyQt.QtCore import QStringListModel, Qt, QTimer
from qgis.PyQt.QtWidgets import QWidget, QComboBox, QCompleter, QFileDialog, QGroupBox, QSpacerItem, QSizePolicy, \
    QGridLayout, QLabel, QTabWidget, QVBoxLayout, QGridLayout
from qgis.core import QgsApplication

import geopandas as gpd

from ...threads.epa_file_manager import GwEpaFileManager
from ...shared.options import GwOptions
from ...utils import tools_gw
from ...ui.ui_manager import GwExecuteModelUi
from .... import global_vars
from ....lib import tools_qgis, tools_qt, tools_db, tools_os
from ..dialog import GwAction


class GwExecuteModelButton(GwAction):
    """ Button 38: Execute model """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.project_type = global_vars.project_type
        self.epa_options_list = []
        self.export_path = None


    def clicked_event(self):

        self._open_execute_dlg()


    def _open_execute_dlg(self):
        self.execute_dlg = GwExecuteModelUi()
        tools_gw.load_settings(self.execute_dlg)

        # Populate combobox
        self._populate_mesh_cmb()

        # Signals
        self.execute_dlg.btn_options.clicked.connect(self._go2epa_options)
        self.execute_dlg.btn_folder_path.clicked.connect(partial(self._manage_btn_folder_path))
        self.execute_dlg.btn_accept.clicked.connect(partial(self._manage_btn_accept))

        tools_gw.open_dialog(self.execute_dlg, 'dlg_execute_model')


    def _populate_mesh_cmb(self):
        sql = "SELECT id, name as idval FROM cat_file"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(self.execute_dlg.cmb_mesh, rows, add_empty=True)


    def _go2epa_options(self):
        self.go2epa_options = GwOptions()
        self.go2epa_options.open_options_dlg()


    def _manage_btn_folder_path(self):
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.execute_dlg, 'txt_folder_path', str(path))


    def _manage_btn_accept(self):
        # Check if results exist on folder
        self.export_path = tools_qt.get_text(self.execute_dlg, 'txt_folder_path')
        if os.path.exists(f"{self.export_path}{os.sep}Iber2D.dat"):
            message = "Results files already exist in this path. Do you want to overwrite them?"
            answer = tools_qt.show_question(message, "overwrite file", force_action=True)
            if not answer:
                return False

        # TODO: ask for import
        do_import = True

        self.execute_model(folder_path=self.export_path, do_generate_inp=True, do_export=True, do_run=True,
                           do_import=do_import)


    def execute_model(self, folder_path: str = '', do_generate_inp: bool = True, do_export: bool = True, do_run: bool = True, do_import: bool = True):
        # Mesh files
        if do_export:
            mesh_id = tools_qt.get_combo_value(self.execute_dlg, 'cmb_mesh')
            self._copy_mesh_files(mesh_id, folder_path)
            self._copy_static_files(folder_path)
            self._create_hyetograph_file(folder_path)
            self._create_rain_file(folder_path)
            return

        # INP file
        if do_generate_inp:
            self._generate_inp(folder_path)


    def _copy_mesh_files(self, mesh_id, folder_path):

        sql = f"SELECT iber2d, roof, losses FROM cat_file WHERE id = '{mesh_id}'"
        row = tools_db.get_row(sql)
        if row:
            iber2d_content, roof_content, losses_content = row

            # Write content to files
            self._write_to_file(f'{folder_path}{os.sep}Iber2D.dat', iber2d_content)

            if roof_content:
                self._write_to_file(f'{folder_path}{os.sep}Iber_SWMM_roof.dat', roof_content)

            if not losses_content:
                losses_content = '0'
            else:
                # Losses method
                sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_method'"
                row = tools_db.get_row(sql, is_thread=True)
                losses_method = row[0] if row and row[0] is not None else 2
                # cn_multiplier
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_scs_cn_multiplier'"
                row = tools_db.get_row(sql, is_thread=True)
                cn_multiplier = row[0] if row else 0
                # ia_coeff
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_scs_ia_coefficient'"
                row = tools_db.get_row(sql, is_thread=True)
                ia_coeff = row[0] if row else 0
                # start_time
                sql = "SELECT value FROM config_user_params WHERE parameter = 'options_losses_starttime'"
                row = tools_db.get_row(sql, is_thread=True)
                start_time = row[0] if row else 0
                # Replace first line
                new_first_line = f"{losses_method} {cn_multiplier} {ia_coeff} {start_time}"
                losses_content_lines = losses_content.split('\n')
                losses_content_lines[0] = new_first_line
                losses_content = '\n'.join(losses_content_lines)

            self._write_to_file(f'{folder_path}{os.sep}Iber_Losses.dat', losses_content)


    def _write_to_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    def _copy_static_files(self, folder_path: str):
        folder = Path(global_vars.plugin_dir) / "resources" / "drain"
        file_names = ["Iber_Problemdata.dat", "Iber_SWMM.ini"]
        for file_name in file_names:
            shutil.copy(folder / file_name, folder_path)

    def _create_hyetograph_file(self, folder_path):
        file_name = Path(folder_path) / "Iber_Hyetograph.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = tools_db.get_row(sql)
        rain_class = int(row[0]) if row else 0

        if rain_class != 1:
            file_name.write_text("Hyetographs\n0\nEnd\n")
            return
        
        gdf = gpd.read_file(global_vars.gpkg_dao_data.db_filepath, layer="hyetograph")
        gdf['x'] = gdf.geometry.x
        gdf['y'] = gdf.geometry.y

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
                ts_rows = tools_db.get_rows(sql)
                if ts_rows:
                    file.write(f"{len(ts_rows)}\n")
                    for ts_row in ts_rows:
                        hours, minutes = map(int, ts_row["time"].split(":"))
                        seconds = hours * 3600 + minutes * 60
                        file.write(f"{seconds} {ts_row['value']}\n")

            file.write("End\n")

    def _create_rain_file(self, folder_path):
        file_name = Path(folder_path) / "Iber_Rain.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = tools_db.get_row(sql)
        rain_class = int(row[0]) if row else 0

        if rain_class != 2:
            file_name.write_text(f"{rain_class} 0\n")
            return

    def _generate_inp(self, folder_path):
        # INP file
        self.export_file_path = f"{folder_path}{os.sep}Iber_SWMM.inp"

        # Create timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(partial(self._calculate_elapsed_time, self.execute_dlg))
        self.timer.start(1000)

        # Set background task 'Go2Epa'
        description = f"Go2Epa"
        self.go2epa_task = GwEpaFileManager(description, self, timer=self.timer)
        QgsApplication.taskManager().addTask(self.go2epa_task)
        QgsApplication.taskManager().triggerTask(self.go2epa_task)


    def _calculate_elapsed_time(self, dialog):

        tf = time()  # Final time
        td = tf - self.t0  # Delta time
        self._update_time_elapsed(f"Exec. time: {timedelta(seconds=round(td))}", dialog)

    def _update_time_elapsed(self, text, dialog):

        if isdeleted(dialog):
            self.timer.stop()
            return

        lbl_timer = dialog.findChild(QLabel, 'lbl_timer')
        lbl_timer.setText(text)
