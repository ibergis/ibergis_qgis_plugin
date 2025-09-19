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
import threading
import traceback
import processing
import time
import platform
import pandas as pd

from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProcessingContext, QgsVectorLayer, QgsFeature, \
    QgsMeshLayer, QgsProject

from ..utils.feedback import Feedback
from ..utils import tools_dr, mesh_parser
from ... import global_vars
from ...lib import tools_log, tools_qt, tools_qgis
from ...lib.tools_gpkgdao import DrGpkgDao
from .task import DrTask
from .epa_file_manager import DrEpaFileManager
from ..admin.admin_btn import DrRptGpkgCreate
from ..processing.import_raster_results import ImportRasterResults
from ...resources.scripts.convert_asc_to_netcdf import convert_asc_to_netcdf
from typing import Optional, List
from dataclasses import dataclass
from ..utils.meshing_process import create_temp_mesh_layer
from swmm_api import read_rpt_file


@dataclass(frozen=True)
class RptTopicConfig:
    topic: str
    swmm_attr: str
    table_name: str
    field_map: dict[str, Optional[str]]
    parent_table: str


class DrExecuteModel(DrTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')

    # Progress percentages
    PROGRESS_INIT = 0
    PROGRESS_CONFIG = 2
    PROGRESS_MESH_FILES = 4
    PROGRESS_STATIC_FILES = 5
    PROGRESS_INLET = 6
    PROGRESS_HYETOGRAPHS = 7
    PROGRESS_RAIN = 8
    PROGRESS_CULVERTS = 9
    PROGRESS_INP = 10
    PROGRESS_IBER = 90
    EXPORT_RESULTS = 99
    PROGRESS_END = 100

    def __init__(self, description: str, params: dict, feedback, timer=None):
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
        self.dao: Optional[DrGpkgDao] = None
        self.init_params()
        self.generate_inp_infolog = None
        self.feedback = feedback
        self.process: Optional[ImportRasterResults] = None
        self.output = None
        self.import_results_infolog = None

    def init_params(self):
        self.dialog = self.params.get('dialog')
        self.folder_path = self.params.get('folder_path')
        self.do_generate_inp = self.params.get('do_generate_inp', True)
        self.do_export = self.params.get('do_export', True)
        self.do_run = self.params.get('do_run', True)
        self.do_import = self.params.get('do_import', True)
        self.do_write_inlets = self.params.get('do_write_inlets', True)
        self.pinlet_layer = self.params.get('pinlet_layer', tools_qgis.get_layer_by_tablename('pinlet'))
        self.do_generate_cogs = self.params.get('do_generate_cogs', False)

    def run(self):

        super().run()
        print(f"{self.description()} -> {threading.get_ident()}")
        self.dao = global_vars.gpkg_dao_data.clone()
        msg = "Task '{0}' execute function '{1}'"
        msg_params = ("Execute model", "_execute_model(self)",)
        tools_log.log_info(msg, msg_params=msg_params)
        self._delete_raster_results(show_question=False)
        status = self._execute_model()
        self._close_dao()

        return status

    def finished(self, result):

        super().finished(result)

        self.dialog.btn_cancel.setVisible(False)
        self.dialog.btn_accept.setVisible(False)
        self.dialog.btn_close.setVisible(True)

        # Create report geopackage
        if not self.isCanceled() and result:
            self._create_results_folder()
            self._delete_raster_results()
            relative_path = os.path.relpath(self.folder_path, QgsProject.instance().absolutePath())
            tools_qgis.set_project_variable('project_results_folder', relative_path)

        # self._close_file()
        if self.timer:
            self.timer.stop()
        if self.isCanceled():
            return

        # If Database exception, show dialog after task has finished
        if global_vars.session_vars['last_error']:
            tools_qt.show_exception_message(msg=global_vars.session_vars['last_error_msg'])

    def cancel(self):

        msg = "Task canceled - {0}"
        msg_params = (self.description(),)
        tools_qgis.show_info(msg, msg_params=msg_params)
        # self._close_file()
        super().cancel()

    def _create_results_folder(self):
        """Create results folder and generate results GPKG and NetCDF files"""

        msg = "Exporting results"
        title = "Export results"
        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)

        if not os.path.exists(f'{self.folder_path}{os.sep}IberGisResults'):
            os.mkdir(f'{self.folder_path}{os.sep}IberGisResults')

        # Create report geopackage
        self.rpt_result = DrRptGpkgCreate("results", f'{self.folder_path}{os.sep}IberGisResults')
        self.rpt_result.create_rpt_gpkg()
        msg = "GPKG file created"
        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
        self._fill_rpt_gpkg(title)

        # Create NetCDF file
        created_netcdf: bool = False
        raster_files: str = f'{self.folder_path}{os.sep}RasterResults'
        netcdf_file: str = f'{self.folder_path}{os.sep}IberGisResults'
        result_names: list[str] = ["Depth", "Velocity", "Rain_Depth"]
        #                            "Hazard_ACA", "Infiltration_Rate",  TODO: Verify necessary results from iber
        #                            "MAX_Hazard_ACA", "MAX_Severe_Hazard_RD9-2008", "Severe_Hazard_RD9-2008"
        #                            "Water_Elevation", "Water_Permanence"]
        try:
            convert_asc_to_netcdf(raster_files, netcdf_file, result_names, self.progress_changed, generate_cogs=self.do_generate_cogs)
        except Exception:
            msg = "Error creating NetCDF file"
            self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
        if os.path.exists(netcdf_file):
            msg = "NetCDF file created"
            self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
            msg = "Exported results"
            self.progress_changed.emit(tools_qt.tr(title), self.EXPORT_RESULTS, tools_qt.tr(msg), True)
            created_netcdf = True
        else:
            msg = "Error creating NetCDF file"
            self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)

        if self.isCanceled():
            return

        if created_netcdf and self.do_import:
            msg = "Do you want to import the results into the project?"
            title = 'Import results'
            result: Optional[bool] = tools_qt.show_question(msg, title, force_action=True)
            if result is not None and result:
                # Execute ImportRasterResults algorithm
                msg = "Importing results"
                self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
                self.feedback = Feedback()
                self.feedback.progress_changed.connect(self._import_results_progress_changed)
                self.process = ImportRasterResults()
                self.process.initAlgorithm(None)
                params: dict = {'FOLDER_RESULTS': f'{self.folder_path}', 'CUSTOM_NAME': f'{os.path.basename(str(self.folder_path))}'}
                context: QgsProcessingContext = QgsProcessingContext()
                self.output = self.process.processAlgorithm(params, context, self.feedback)
                if not bool(self.output):
                    msg = "Error importing results"
                    self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
                    return
                else:
                    self.output = self.process.postProcessAlgorithm(context, self.feedback)
                    if not bool(self.output):
                        msg = "Error importing results"
                        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
                        return
                msg = "Imported results"
                self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
        self.progress_changed.emit(None, self.PROGRESS_END, None, False)

    def _fill_rpt_gpkg(self, title: str):
        """Fill rpt gpkg"""
        dao_rpt = DrGpkgDao()
        dao_rpt.init_db(f'{self.folder_path}{os.sep}IberGisResults{os.sep}results.gpkg')
        dao_data = global_vars.gpkg_dao_data

        if os.path.exists(f'{self.folder_path}{os.sep}Iber_SWMM.rpt'):
            report_values = read_rpt_file(f'{self.folder_path}{os.sep}Iber_SWMM.rpt')
        else:
            msg = "Iber_SWMM.rpt file not found"
            self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
            return

        configs: list[RptTopicConfig] = [
            RptTopicConfig(
                topic='Node',
                swmm_attr='node_depth_summary',
                table_name='rpt_node',
                field_map={
                    'epa_type': 'Type',
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Arc',
                swmm_attr='link_flow_summary',
                table_name='rpt_arc',
                field_map={
                    'epa_type': 'Type',
                    'shape': None,
                    'geom1': None,
                    'geom2': None,
                    'geom3': None,
                    'geom4': None,
                    'arc_type': None
                },
                parent_table='arc'
            ),
            RptTopicConfig(
                topic='Node Depth',
                swmm_attr='node_depth_summary',
                table_name='rpt_nodedepth_sum',
                field_map={
                    'epa_type': 'Type',
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'aver_depth': 'Average_Depth_Meters',
                    'max_depth': 'Maximum_Depth_Meters',
                    'max_hgl': 'Maximum_HGL_Meters',
                    'time_days': 'Time of Max_Occurrence_days hr:min',
                    'time_hour': 'Time of Max_Occurrence_days hr:min',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Node Inflow',
                swmm_attr='node_inflow_summary',
                table_name='rpt_nodeinflow_sum',
                field_map={
                    'epa_type': 'Type',
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'max_latinf': 'Maximum_Lateral_Inflow_CMS',
                    'max_totinf': 'Maximum_Total_Inflow_CMS',
                    'time_days': 'Time of Max_Occurrence_days hr:min',
                    'time_hour': 'Time of Max_Occurrence_days hr:min',
                    'latinf_vol': 'Lateral_Inflow_Volume_10^6 ltr',
                    'totinf_vol': 'Total_Inflow_Volume_10^6 ltr',
                    'flow_balance_error': 'Flow_Balance_Error_Percent',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Node Surcharge',
                swmm_attr='node_surcharge_summary',
                table_name='rpt_nodesurcharge_sum',
                field_map={
                    'epa_type': 'Type',
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'hour_surch': 'Hours_Surcharged',
                    'max_height': 'Max. Height_Above Crown_Meters',
                    'min_depth': 'Min. Depth_Below Rim_Meters',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Node Flooding',
                swmm_attr='node_flooding_summary',
                table_name='rpt_nodeflooding_sum',
                field_map={
                    'epa_type': None,
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'hour_flood': 'Hours_Flooded',
                    'max_rate': 'Maximum_Rate_CMS',
                    'time_days': 'Time of Max_Occurrence_days hr:min',
                    'time_hour': 'Time of Max_Occurrence_days hr:min',
                    'tot_flood': 'Total_Flood_Volume_10^6 ltr',
                    'max_ponded': 'Maximum_Ponded_Depth_Meters',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Storage Volume',
                swmm_attr='storage_volume_summary',
                table_name='rpt_storagevol_sum',
                field_map={
                    'epa_type': None,
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'aver_vol': 'Average_Volume_1000 m3',
                    'avg_full': 'Avg_Pcnt_Full',
                    'evap_loss': 'Evap_Pcnt_Loss',
                    'exfil_loss': 'Exfil_Pcnt_Loss',
                    'max_vol': 'Maximum_Volume_1000 m3',
                    'max_full': 'Max_Pcnt_Full',
                    'time_days': 'Time of Max_Occurrence_days hr:min',
                    'time_hour': 'Time of Max_Occurrence_days hr:min',
                    'max_out': 'Maximum_Outflow_CMS',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Outfall Loading',
                swmm_attr='outfall_loading_summary',
                table_name='rpt_outfallflow_sum',
                field_map={
                    'epa_type': None,
                    'ymax': None,
                    'elev': None,
                    'y0': None,
                    'ysur': None,
                    'flow_freq': 'Flow_Freq_Pcnt',
                    'avg_flow': 'Avg_Flow_CMS',
                    'max_flow': 'Max_Flow_CMS',
                    'total_vol': 'Total_Volume_10^6 ltr',
                },
                parent_table='node'
            ),
            RptTopicConfig(
                topic='Link Flow',
                swmm_attr='link_flow_summary',
                table_name='rpt_arcflow_sum',
                field_map={
                    'epa_type': 'Type',
                    'shape': None,
                    'geom1': None,
                    'geom2': None,
                    'geom3': None,
                    'geom4': None,
                    'arc_type': None,
                    'max_flow': 'Maximum_|Flow|_CMS',
                    'time_days': 'Time of Max_Occurrence_days hr:min',
                    'time_hour': 'Time of Max_Occurrence_days hr:min',
                    'max_veloc': 'Maximum_|Veloc|_m/sec',
                    'mfull_flow': 'Max/_Full_Flow',
                    'mfull_dept': 'Max/_Full_Depth',
                },
                parent_table='arc'
            ),
            RptTopicConfig(
                topic='Flow Classification',
                swmm_attr='flow_classification_summary',
                table_name='rpt_flowclass_sum',
                field_map={
                    'epa_type': None,
                    'shape': None,
                    'geom1': None,
                    'geom2': None,
                    'geom3': None,
                    'geom4': None,
                    'length': 'Adjusted_/Actual_Length',
                    'dry': 'Dry',
                    'up_dry': 'Up_Dry',
                    'down_dry': 'Down_Dry',
                    'sub_crit': 'Sub_Crit',
                    'sub_crit_1': 'Sup_Crit',
                    'up_crit': 'Up_Crit',
                    'down_crit': 'Down_Crit',
                    'norm_ltd': 'Norm_Ltd',
                    'inlet_ctrl': 'Inlet_Ctrl',
                },
                parent_table='arc'
            ),
            RptTopicConfig(
                topic='Conduit Surcharge',
                swmm_attr='conduit_surcharge_summary',
                table_name='rpt_condsurcharge_sum',
                field_map={
                    'epa_type': None,
                    'shape': None,
                    'geom1': None,
                    'geom2': None,
                    'geom3': None,
                    'geom4': None,
                    'both_ends': 'HoursFull_Both_Ends',
                    'upstream': 'Hours Full_Upstream',
                    'dnstream': 'HoursFull_Dnstream',
                    'hour_nflow': 'Hours_Above Full_Normal Flow',
                    'hour_limit': 'Hours_Capacity_Limited',
                },
                parent_table='arc'
            ),
            RptTopicConfig(
                topic='Pumping',
                swmm_attr='pumping_summary',
                table_name='rpt_pumping_sum',
                field_map={
                    'epa_type': None,
                    'percent': 'Percent_Utilized',
                    'num_startup': 'Number of_Start-Ups',
                    'min_flow': 'Min_Flow_CMS',
                    'avg_flow': 'Avg_Flow_CMS',
                    'max_flow': 'Max_Flow_CMS',
                    'vol_ltr': 'Total_Volume_10^6 ltr',
                    'powus_kwh': 'Power_Usage_Kw-hr',
                    'timoff_min': '% Time Off_Pump Curve_Low',
                    'timoff_max': '% Time Off_Pump Curve_High',
                },
                parent_table='arc'
            ),
        ]

        msg = "Filling rpt gpkg"
        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)

        node_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=node', 'node', 'ogr')
        arc_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=arc', 'arc', 'ogr')

        node_dict: dict[str, QgsFeature] = {}
        arc_dict: dict[str, QgsFeature] = {}
        for feature in node_layer.getFeatures():
            node_dict[feature.attribute('code')] = feature
        for feature in arc_layer.getFeatures():
            arc_dict[feature.attribute('code')] = feature

        # Get SRID from the node layer
        srid = node_layer.crs().authid().split(':')[-1] if node_layer.crs().authid() else '25831'

        for cfg in configs:
            swmm_df = getattr(report_values, cfg.swmm_attr)
            table_name = cfg.table_name
            try:
                for index, data_row in swmm_df.iterrows():
                    start_sql = f"INSERT INTO {table_name} (code, "
                    end_sql = f") VALUES ('{index}', "
                    for field, swmm_field in cfg.field_map.items():
                        if swmm_field is None:
                            # Get value from inp table
                            sql = f"SELECT table_name FROM {cfg.parent_table} WHERE code = '{index}'"
                            row = dao_data.get_row(sql)
                            if row is None:
                                msg = f"Error getting table name for {cfg.topic}: \n {sql}"
                                self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
                                continue
                            sql = f"SELECT {field} FROM {cfg.parent_table} AS general INNER JOIN {row[0]} inp ON general.code = inp.code WHERE general.code = '{index}'"
                            row = dao_data.get_row(sql)
                            if row is None:
                                sql = f"SELECT {field} FROM {'rpt_node' if cfg.parent_table == 'node' else 'rpt_arc'} WHERE code = '{index}'"
                                row = dao_rpt.get_row(sql)
                                if row is None:
                                    continue
                            start_sql += f"{field}, "
                            end_sql += f"{row[0]}, " if isinstance(row[0], (int, float)) else f"'{row[0]}', "
                            continue
                        elif swmm_field not in data_row or pd.isna(data_row[swmm_field]) or str(data_row[swmm_field]) == 'nan':
                            continue
                        elif field == 'time_days':
                            start_sql += "time_days, "
                            end_sql += f"'{str(data_row[swmm_field]).split(' ')[0]}', "
                            continue
                        elif field == 'time_hour':
                            start_sql += "time_hour, "
                            end_sql += f"'{str(data_row[swmm_field]).split(' ')[-1]}', "
                            continue
                        start_sql += f"{field}, "
                        end_sql += f"{data_row[swmm_field]}, " if isinstance(data_row[swmm_field], (int, float)) else f"'{data_row[swmm_field]}', "
                    # Get geometry
                    geom = None
                    if cfg.parent_table == 'node':
                        if index in node_dict:
                            geom = node_dict[index].geometry().asWkt()
                    elif cfg.parent_table == 'arc':
                        if index in arc_dict:
                            geom = arc_dict[index].geometry().asWkt()
                    start_sql += "geom, "
                    end_sql += f"ST_GeomFromText('{geom}', {srid}), "

                    start_sql = start_sql[:-2]
                    end_sql = end_sql[:-2]
                    sql = f"{start_sql}{end_sql})"
                    result = dao_rpt.execute_sql(sql)
                    if not result:
                        msg = f"Error filling rpt gpkg for {cfg.topic}: \n {sql}"
                        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
            except Exception as e:
                msg = f"Error filling rpt gpkg for {cfg.topic}: \n {e}"
                self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)
        dao_rpt.close_db()

        msg = "Filled rpt gpkg"
        self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg), True)

    def _delete_raster_results(self, show_question: bool = True):
        """Delete raster results folder"""

        if show_question:
            result = tools_qt.show_question("Do you want to delete the ASC rasters? This will significantly reduce the size of the folder.")
        else:
            result = True
        raster_files: str = f'{self.folder_path}{os.sep}RasterResults'
        if os.path.exists(raster_files) and result:
            shutil.rmtree(raster_files)

    def _import_results_progress_changed(self, process, progress, text, new_line):
        self.progress_changed.emit(tools_qt.tr("Import results"), None, text, new_line)
        self.import_results_infolog = text

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
        title = "Export files"
        try:
            if self.isCanceled():
                return False
            # Mesh files
            if self.do_export:
                # Export config
                msg = "Exporting config files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INIT, tools_qt.tr(msg), False)
                self._create_config_files()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_CONFIG, tools_qt.tr(msg), True)

                if self.isCanceled():
                    return False

                # Export mesh
                msg = "Exporting mesh files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_CONFIG, tools_qt.tr(msg), False)
                mesh_id = tools_qt.get_combo_value(self.dialog, 'cmb_mesh')
                self._copy_mesh_files(mesh_id)
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_MESH_FILES, tools_qt.tr(msg), True)

                if self.isCanceled():
                    return False

                # Copy static files
                msg = "Copying static files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_MESH_FILES, tools_qt.tr(msg), False)
                self._copy_static_files()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_STATIC_FILES, tools_qt.tr(msg), True)

                if self.isCanceled():
                    return False

                # Create inlet file
                msg = "Creating inlet files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_STATIC_FILES, tools_qt.tr(msg), False)
                self._create_inlet_file(mesh_id, self.pinlet_layer)
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INLET, tools_qt.tr(msg), True)

                if self.isCanceled():
                    return False

                # Create hyetograph file
                msg = "Creating hyetograph files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INLET, tools_qt.tr(msg), False)
                status = self._create_hyetograph_file()
                if not status:
                    return False
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_HYETOGRAPHS, tools_qt.tr(msg), True)

                if self.isCanceled():
                    return False

                # Create rain file
                msg = "Creating rain files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_HYETOGRAPHS, tools_qt.tr(msg), False)
                self._create_rain_file()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_RAIN, tools_qt.tr(msg), True)

                # Create culvert file
                msg = "Creating culvert files..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_RAIN, tools_qt.tr(msg), False)
                self._create_culvert_file()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_CULVERTS, tools_qt.tr(msg), True)

            if self.isCanceled():
                return False

            # INP file
            title = "Generate INP"
            if self.do_generate_inp:
                msg = "Generating INP..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_CULVERTS, tools_qt.tr(msg), False)
                self._generate_inp()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INP, tools_qt.tr(msg), True)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INP, self.generate_inp_infolog, True)

            if self.isCanceled():
                return False

            title = "Run Iber"
            if self.do_run:
                msg = "Running Iber software..."
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_INP, tools_qt.tr(msg), False)
                self._run_iber()
                msg = "done!"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IBER, tools_qt.tr(msg), True)

            if self.isCanceled():
                return False

        except Exception as e:
            print(f"Exception in ExecuteModel thread: {e}")
            title = "ERROR"
            msg = "Exception in ExecuteModel thread: {0}\n {1}"
            msg_params = (e, traceback.format_exc())
            self.progress_changed.emit(tools_qt.tr(title), None, tools_qt.tr(msg, list_params=msg_params), True)
            return False

        return True

    def _create_config_files(self):
        # Iber_Results.dat
        file_name = Path(self.folder_path) / "Iber_Results.dat"
        mapper = [
            {"parameter": "result_depth", "tag": "Depth"},
            {"parameter": "result_vel", "tag": "Velocity"},
            {"parameter": "result_specific_discharge", "tag": "Specific_Discharge"},
            {"parameter": "result_water_elevation", "tag": "Water_Elevation"},
            {"parameter": "result_fronde_number", "tag": "Froude_Number"},
            {"parameter": "result_localtime_step", "tag": "Local_Time_Step"},
            {"parameter": "result_manning_coefficient", "tag": "Manning_Coefficient"},
            {"parameter": "result_critical_diameter", "tag": "Critical_Diameter"},
            {"parameter": "result_max_depth", "tag": "Maximum_Depth"},
            {"parameter": "result_max_vel", "tag": "Maximum_Velocity"},
            {"parameter": "result_max_spec_discharge", "tag": "Maximum_Spec_Discharge"},
            {"parameter": "result_max_water_elev", "tag": "Maximum_Water_Elev"},
            {"parameter": "result_max_localtime_step", "tag": "Maximum_Local_Time_Step"},
            {"parameter": "result_max_critical_diameter", "tag": "Maximum_Critical_Diameter"},
            {"parameter": "result_hazard_rd9_2008", "tag": "Hazard RD9/2008"},
            {"parameter": "result_hazard_aca2003", "tag": "Hazard ACA2003"},
            {"parameter": "result_hazard_pedestrians", "tag": "Pedestrians Hazard"},
            {"parameter": "result_hazard_vehicles", "tag": "Vehicles Hazard"},
            {"parameter": "result_depth_vector", "tag": "Depth_vector"},
            {"parameter": "result_bed_shear_stress", "tag": "Bed_Shear_Stress"},
            {"parameter": "result_max_bed_shear_stress", "tag": "Maximum_Bed_Shear_Stress"},
            {"parameter": "result_energy", "tag": "Energy"},
            {"parameter": "result_steamlines", "tag": "Streamlines"},
            {"parameter": "result_results_raster", "tag": "Results2Raster"},
            {"parameter": "result_results_raster_cell", "tag": "esults2Raster - Cell size"},
            {"parameter": "result_results_raster_maxs", "tag": "Results2Raster MAX"},
            {"parameter": "result_results_raster_frame", "tag": ""},
            {"parameter": "result_results_raster_xymax", "tag": ""},
            {"parameter": "result_results_raster_xymin", "tag": ""},
        ]
        sql = "SELECT parameter, value FROM config_param_user WHERE parameter like 'result_%'"
        rows = self.dao.get_rows(sql)
        if rows:
            parameters = {row['parameter']: row['value'] for row in rows}
            with open(file_name, 'w', newline='') as dat_file:
                for item in mapper:
                    value = parameters.get(item['parameter'], -9999)
                    if value in (None, "True", "False"):
                        value = "1" if value == "True" else "0"
                    parameter = item['tag']
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

        sql = f"SELECT iber2d, roof, losses, bridge FROM cat_file WHERE id = '{mesh_id}'"
        row = self.dao.get_row(sql)
        title = "Export files"
        self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(10, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
        if row:
            iber2d_content, roof_content, losses_content, bridges_content = row

            # Write content to files
            project_name, result_iber_format, iber2d_options = self._get_iber2d_options()
            iber2d_lines = iber2d_content.split('\n')
            if iber2d_lines[0] == "MATRIU":
                iber2d_content = f"{project_name}\n{iber2d_options}\n{iber2d_content}"
            else:
                iber2d_lines[1] = f"{iber2d_options}"
                iber2d_content = '\n'.join(iber2d_lines)
            # if iber2d_lines[0] == "MATRIU":
            #     iber2d_content = f"{project_name}\n{result_iber_format}\n{iber2d_options}\n{iber2d_content}"
            # else:
            #     iber2d_lines[1] = f"{result_iber_format}\n{iber2d_options}"
            #     iber2d_content = '\n'.join(iber2d_lines)

            self._write_to_file(f'{self.folder_path}{os.sep}Iber2D.dat', iber2d_content)
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(30, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            if roof_content:
                self._write_to_file(f'{self.folder_path}{os.sep}Iber_SWMM_roof.dat', roof_content)

            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(40, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            if not losses_content:
                losses_content = '0'
            elif losses_content != '0':
                # Losses method
                sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_method'"
                row = self.dao.get_row(sql)
                losses_method = row[0] if row and row[0] is not None else 2
                if losses_method == '0':
                    losses_content = '0'
                else:
                    self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(50, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # cn_multiplier
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_scs_cn_multiplier'"
                    row = self.dao.get_row(sql)
                    cn_multiplier = row[0] if row else 1
                    self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(55, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # ia_coeff
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_scs_ia_coefficient'"
                    row = self.dao.get_row(sql)
                    ia_coeff = row[0] if row else 0.2
                    self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(60, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # start_time
                    sql = "SELECT value FROM config_param_user WHERE parameter = 'options_losses_starttime'"
                    row = self.dao.get_row(sql)
                    start_time = row[0] if row else 0
                    self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(70, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)
                    # Replace first line
                    new_first_line = f"{losses_method} {cn_multiplier} {ia_coeff} {start_time}"
                    losses_content_lines = losses_content.split('\n')
                    losses_content_lines[0] = new_first_line
                    losses_content = '\n'.join(losses_content_lines)
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(80, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            self._write_to_file(f'{self.folder_path}{os.sep}Iber_Losses.dat', losses_content)
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(90, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

            if bridges_content:
                self._write_to_file(f'{self.folder_path}{os.sep}Iber_Internal_cond.dat', bridges_content)
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(100, self.PROGRESS_INIT, self.PROGRESS_MESH_FILES), '', False)

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
        title = "Export files"
        for i, file_name in enumerate(file_names):
            shutil.copy(folder / file_name, self.folder_path)
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(tools_dr.lerp_progress(i, 0, len(file_names)), self.PROGRESS_MESH_FILES, self.PROGRESS_STATIC_FILES), '', False)

    def _create_inlet_file(self, selected_mesh: Optional[QgsMeshLayer] = None, pinlet_layer: Optional[QgsVectorLayer] = None):
        file_name = Path(self.folder_path) / "Iber_SWMM_inlet_info.dat"
        ordered_keys = ['outlet_type', 'outlet_node', 'top_elev', 'width', 'length', 'depth', 'method', 'weir_cd', 'orifice_cd', 'a_param', 'b_param', 'efficiency']

        # Convert pinlets into inlets
        converted_inlets: Optional[List[QgsFeature]] = self._convert_pinlets_into_inlets(selected_mesh, pinlet_layer)

        if self.do_write_inlets:
            # Get existing inlets from current project
            inlet_layer = QgsVectorLayer(global_vars.gpkg_dao_data.db_filepath + "|layername=inlet", "inlet", "ogr")
            if not inlet_layer:
                return
            inlets = list(inlet_layer.getFeatures())

            # File headers
            headers = ['gully_id', 'outlet_type', 'node_id', 'xcoord', 'ycoord', 'zcoord', 'width', 'length',
                            'depth', 'method', 'weir_cd', 'orifice_cd', 'a_param', 'b_param', 'efficiency']
            # Write new inlets
            mode = 'w'
        else:
            # Append pinlets to existing file
            mode = 'a'

        with open(file_name, mode, newline='') as dat_file:
            transform_dict = {None: -9999, 'TO NETWORK': 'To_network', 'SINK': 'Sink', 'NULL': -9999}
            if self.do_write_inlets:
                # Write column headers
                header_str = f"{' '.join(headers)}\n"
                dat_file.write(header_str)
                for inlet in inlets:
                    values = []
                    for value in ordered_keys:
                        value_str = str(transform_dict.get(str(inlet[value]), inlet[value]))
                        values.append(value_str)
                    values.insert(0, str(inlet['code']))
                    values.insert(3, str(inlet.geometry().asPoint().x()))
                    values.insert(4, str(inlet.geometry().asPoint().y()))
                    values_str = f"{' '.join(values)}\n"
                    dat_file.write(values_str)
            if converted_inlets:
                # Write converted inlets
                for feature in converted_inlets:
                    values = []
                    for value in ordered_keys:
                        value_str = str(transform_dict.get(str(feature[value]), feature[value]))
                        values.append(value_str)
                    values.insert(0, str(feature['code']))
                    values.insert(3, str(feature.geometry().asPoint().x()))
                    values.insert(4, str(feature.geometry().asPoint().y()))
                    values_str = f"{' '.join(values)}\n"
                    dat_file.write(values_str)

    def _convert_pinlets_into_inlets(self, selected_mesh: Optional[int] = None, pinlet_layer: Optional[QgsVectorLayer] = None, minimum_size: Optional[float] = 2) -> Optional[List[QgsFeature]]:
        """Convert pinlets into inlets"""
        if selected_mesh is None:
            return None

        # Get pinlet layer
        if pinlet_layer is None:
            return None

        # Get mesh layer data
        sql = f"SELECT name, iber2d, roof, losses, bridge FROM cat_file WHERE id = {selected_mesh};"
        if not self.dao:
            return None
        row = self.dao.get_row(sql)

        if not row:
            return None

        # Create mesh layer
        mesh = mesh_parser.loads(row["iber2d"], row["roof"], row["losses"], row["bridge"])
        mesh_layer = create_temp_mesh_layer(mesh)

        if mesh_layer is None:
            return None

        # Split pinlet polygons by lines into a layer using QGIS processing algorithm: Split with lines
        splited_pinlets = processing.run(
            "native:splitwithlines", {
                'INPUT': pinlet_layer,
                'LINES': mesh_layer,
                'OUTPUT': 'memory:'
            }
        )
        splited_pinlets_layer: QgsVectorLayer = splited_pinlets['OUTPUT']
        if splited_pinlets_layer is None:
            return None
        splited_polygons = splited_pinlets_layer.getFeatures()

        # Group splited polygons by pinlet
        converted_inlets: List[QgsFeature] = []
        grouped_splited_polygons: dict[str, List[QgsFeature]] = {}
        for feature in splited_polygons:
            if feature['code'] in grouped_splited_polygons.keys():
                grouped_splited_polygons[f'{feature["code"]}'].append(feature)
            else:
                grouped_splited_polygons[f'{feature["code"]}'] = [feature]

        # Get valid polygons and get its centroids
        for pinlet_code in grouped_splited_polygons.keys():
            # Get pinlet and its area
            pinlet_layer_features = pinlet_layer.getFeatures()
            pinlet_perimeter: Optional[float] = None
            parent_pinlet: QgsFeature = None
            minimum_size_area: Optional[float] = None
            for pinlet_feature in pinlet_layer_features:
                if pinlet_feature['code'] == pinlet_code:
                    minimum_size_area = pinlet_feature.geometry().area() / 100 * minimum_size
                    pinlet_perimeter = pinlet_feature.geometry().length()
                    parent_pinlet = pinlet_feature
                    break
            if minimum_size_area is None or parent_pinlet is None or pinlet_perimeter is None:
                continue

            # Get total perimeter of the pinlet(sum of all splited polygon perimeters)
            total_perimeter: float = 0
            for feature in grouped_splited_polygons[pinlet_code]:
                # Check if the polygon is valid
                if feature.geometry().area() < minimum_size_area:
                    continue
                total_perimeter += feature.geometry().length()
            if total_perimeter is None or total_perimeter == 0:
                continue

            # Create inlets and calculate its length/width
            test_perimeter = 0
            last_id = 1
            for feature in grouped_splited_polygons[pinlet_code]:
                # Check if the polygon is valid
                if feature.geometry().area() < minimum_size_area:
                    continue

                # Create new inlet with the centroid of the polygon and copy its attributes from parent pinlet
                geom = feature.geometry()
                new_inlet = QgsFeature(feature.fields())
                new_inlet.setGeometry(geom.centroid())

                attrs = {}
                for field in feature.fields():
                    field_name = field.name()
                    attrs[field_name] = feature[field_name]
                new_inlet.setAttributes([attrs[field.name()] for field in feature.fields()])
                new_inlet['code'] = f'{parent_pinlet.id()}_{last_id}'
                last_id += 1

                # Calculate length/width
                length_width = 0
                length_width = (feature.geometry().length() * pinlet_perimeter / (total_perimeter)) / 4
                new_inlet['length'] = length_width
                new_inlet['width'] = length_width
                test_perimeter += (length_width * 4)

                # Add to list
                converted_inlets.append(new_inlet)

        if len(converted_inlets) == 0:
            return None

        return converted_inlets

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
            return True

        gdf = QgsVectorLayer(global_vars.gpkg_dao_data.db_filepath + "|layername=hyetograph", "hyetograph", "ogr")
        gdf_features = gdf.getFeatures()
        title = "Export files"
        self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(10, self.PROGRESS_STATIC_FILES, self.PROGRESS_HYETOGRAPHS), '', False)

        with open(file_name, "w") as file:
            file.write("Hyetographs\n")
            file.write(f"{gdf.featureCount()}\n")

            for i, ht_row in enumerate(gdf_features, start=1):
                file.write(f"{i}\n")
                file.write(f"{ht_row.geometry().asPoint().x()} {ht_row.geometry().asPoint().y()}\n")
                timeseries = timeseries_override if timeseries_override not in (None, '') else ht_row["timeseries"]
                if timeseries in (None, '', 'null', 'NULL'):
                    self.progress_changed.emit(None, None, f"\nERROR: Invalid timeseries for hyetograph {ht_row['code']}", True)
                    return False

                sql = f"""
                    SELECT time, value
                    FROM cat_timeseries_value
                    WHERE timeseries ='{timeseries}'
                """
                ts_rows = self.dao.get_rows(sql)
                if not ts_rows:
                    self.progress_changed.emit(None, None, f"\nERROR: Timeseries values not found for timeseries {timeseries}", True)
                    return False

                file.write(f"{len(ts_rows)}\n")
                for ts_row in ts_rows:
                    hours, minutes = map(int, ts_row["time"].split(":"))
                    seconds = hours * 3600 + minutes * 60
                    file.write(f"{seconds} {ts_row['value']}\n")

                self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(tools_dr.lerp_progress(i, 10, gdf.featureCount()), self.PROGRESS_STATIC_FILES, self.PROGRESS_HYETOGRAPHS), '', False)

            file.write("End\n")
        return True

    def _create_rain_file(self):
        file_name = Path(self.folder_path) / "Iber_Rain.dat"

        sql = "SELECT value FROM config_param_user WHERE parameter = 'options_rain_class'"
        row = self.dao.get_row(sql)
        rain_class = int(row[0]) if row and row[0] else 0
        title = "Export files"
        self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(50, self.PROGRESS_HYETOGRAPHS, self.PROGRESS_RAIN), '', False)

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

        times = [row["time"] for row in raster_rows]
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

    def _create_culvert_file(self):
        file_name = Path(self.folder_path) / "Iber_Culverts.dat"

        gdf = QgsVectorLayer(global_vars.gpkg_dao_data.db_filepath + "|layername=culvert", "culvert", "ogr")
        gdf_features = gdf.getFeatures()
        title = "Export files"
        self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(10, self.PROGRESS_RAIN, self.PROGRESS_CULVERTS), '', False)

        with open(file_name, "w") as file:
            file.write(f"{gdf.featureCount()}\n")

            for i, ht_row in enumerate(gdf_features, start=1):
                # 1 - fid
                file.write(f"{ht_row.id()} ")

                # 2 - iscalculate
                if ht_row["iscalculate"] is True:
                    file.write(f"{1} ")
                else:
                    file.write(f"{0} ")

                # 3, 4, 5, 6 - geometry
                file.write(f"{ht_row.geometry().asPolyline()[0].x()} {ht_row.geometry().asPolyline()[0].y()} ")
                file.write(f"{ht_row.geometry().asPolyline()[1].x()} {ht_row.geometry().asPolyline()[1].y()} ")
                # 7 - z_start
                if ht_row["z_start"] is None or str(ht_row["z_start"]) == "NULL":
                    file.write("0 ")
                else:
                    file.write(f"{ht_row['z_start']} ")
                # 8 - z_end
                if ht_row["z_end"] is None or str(ht_row["z_end"]) == "NULL":
                    file.write("0 ")
                else:
                    file.write(f"{ht_row['z_end']} ")

                # 9 - culvert type
                if ht_row["culvert_type"] == "CIRCULAR":
                    file.write("2 ")
                else:
                    file.write("1 ")

                # 10, 11, 12, 13 - geom2(width), geom1(height), manning, code
                file.write(f"{0 if str(ht_row['geom2']) == 'NULL' else ht_row['geom2']} " +
                           f"{0 if str(ht_row['geom1']) == 'NULL' else ht_row['geom1']} " +
                           f"{0 if str(ht_row['manning']) == 'NULL' else ht_row['manning']} " +
                           f"{0 if str(ht_row['collapse_moment']) == 'NULL' else ht_row['collapse_moment']} " +
                           f"{ht_row['code']}\n")

                self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(tools_dr.lerp_progress(i, 10, gdf.featureCount()), self.PROGRESS_RAIN, self.PROGRESS_CULVERTS), '', False)

    def _generate_inp(self):
        go2epa_params = {"dialog": self.dialog, "export_file_path": f"{self.folder_path}{os.sep}Iber_SWMM.inp", "is_subtask": True}
        self.generate_inp_task = DrEpaFileManager("Go2Epa", go2epa_params, self.feedback, None)
        self.generate_inp_task.debug_mode = False
        self.generate_inp_task.progress_changed.connect(self._generate_inp_progress_changed)
        self.feedback.progress_changed.connect(self._generate_inp_progress_changed)
        result = self.generate_inp_task._export_inp()
        return result

    def _generate_inp_progress_changed(self, process, progress, text, new_line):
        title = "Generate INP"
        if progress:
            self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(progress, self.PROGRESS_INP, self.PROGRESS_RAIN), text, new_line)
        else:
            self.progress_changed.emit(tools_qt.tr(title), progress, self.PROGRESS_INP, text, new_line)
            self.generate_inp_infolog = text

    def _run_iber(self):
        # iber_exe_path = f"{global_vars.plugin_dir}{os.sep}resources{os.sep}drain{os.sep}IberPlus.exe"  # TODO: Add checkbox to select between Iber and IberPlus
        if platform.system() == "Windows":
            iber_exe_path = f"{global_vars.plugin_dir}{os.sep}resources{os.sep}drain{os.sep}IberPlus.exe"
        else:
            iber_exe_path = f"{global_vars.plugin_dir}{os.sep}resources{os.sep}drain{os.sep}IberPlus"
        title = "Run Iber"

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

        init_progress = tools_dr.lerp_progress(10, self.PROGRESS_INP, self.PROGRESS_IBER)
        self.progress_changed.emit(tools_qt.tr(title), init_progress, '', False)

        # Add a small delay to ensure the files are copied
        time.sleep(1)

        process = subprocess.Popen([iber_exe_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   cwd=self.folder_path,
                                   bufsize=1,
                                   creationflags=subprocess.CREATE_NO_WINDOW)

        # Read output in real-time
        while not self.isCanceled():
            output = process.stdout.readline()  # TODO: Read the output from the file proceso.rep
            if output == '' and process.poll() is not None:
                break
            if output:
                try:
                    # 0.000        1.00000    13:58:47:68       0.000       0.000     0.00%        --
                    output_parts = [x for x in output.strip().split(' ') if x != '']
                    if len(output_parts) == 7 and float(output_parts[5].replace('%', '')) < 100:
                        output_percentage = output_parts[5].replace('%', '')
                        iber_percentage = tools_dr.lerp_progress(int(float(output_percentage)), init_progress, self.PROGRESS_IBER)
                        print(f"iber_percentage: {iber_percentage}")
                    else:
                        iber_percentage = None
                except Exception:
                    iber_percentage = None
                self.progress_changed.emit(tools_qt.tr(title), iber_percentage, f'{output.strip()}', True)

        if process.poll() is None:
            process.terminate()

        # Wait for the process to finish and get the return code
        return_code = process.wait()

        print(f"IberPlus execution finished. Return code: {return_code}")

        self.progress_changed.emit(tools_qt.tr(title), tools_dr.lerp_progress(100, self.PROGRESS_INP, self.PROGRESS_IBER), '', True)

    # endregion
