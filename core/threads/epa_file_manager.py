"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import subprocess
import tempfile
import sqlite3
import pandas as pd

from qgis.PyQt.QtCore import pyqtSignal, QMetaMethod
from qgis.PyQt.QtWidgets import QTextEdit
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsField, QgsFields, QgsFeature, \
    QgsProject

from ..utils.generate_swmm_inp.generate_swmm_inp_file import GenerateSwmmInpFile
from ..utils import tools_dr
from ... import global_vars
from ...lib import tools_log, tools_qt, tools_db, tools_qgis, tools_os
from .task import DrTask
from .importinp_core import _tables

_tables_dict = {}
_tables_dict_swapped = {}
for table_info in _tables:
    table_name = table_info["table_name"]

    if table_name not in _tables_dict:
        _tables_dict[table_name] = table_info
    else:
        _tables_dict[table_name]['mapper'].update(table_info['mapper'])

for table_name, table_info in _tables_dict.items():
    # Swap keys and values in the "mapper" dictionary
    swapped_mapper = {v: k for k, v in table_info["mapper"].items()}

    # Update the entry in _tables_dict
    _tables_dict_swapped[table_name] = {
        "table_name": table_info["table_name"],
        "section": table_info["section"],
        "mapper": swapped_mapper,
    }


class DrEpaFileManager(DrTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()
    progress_changed = pyqtSignal(int, str)

    def __init__(self, description, params, timer=None):

        super().__init__(description)
        self.params = params
        self.json_result = None
        self.rpt_result = None
        self.fid = 140
        self.function_name = None
        self.timer = timer
        self.initialize_variables()
        self.set_variables_from_params()

        # If enabled it will: add the output layers to your project, save the .xlsx files and the generated .inp file
        self.debug_mode = False
        self.debug_folder_path = ''  # This is the folder where the .xlsx and .inp files will be saved


    def initialize_variables(self):

        self.exception = None
        self.error_msg = None
        self.message = None
        self.common_msg = ""
        self.function_failed = False
        self.complet_result = None
        self.replaced_velocities = False
        self.output = None
        self.dao = global_vars.gpkg_dao_data.clone()


    def set_variables_from_params(self):
        """ Set variables from object Go2Epa """

        self.dlg_go2epa = self.params.get("dialog")
        self.export_file_path = self.params.get("export_file_path")
        self.is_subtask = self.params.get("is_subtask", False)


    def run(self):

        super().run()

        self.initialize_variables()
        tools_log.log_info(f"Task 'Generate INP file' execute function 'def _export_inp(self)'")
        status = self._export_inp()

        self._close_dao()

        return status


    def finished(self, result):

        super().finished(result)

        if not self.is_subtask:
            self.dlg_go2epa.btn_cancel.setEnabled(False)
            self.dlg_go2epa.btn_accept.setEnabled(True)

        # self._close_file()
        if self.timer:
            self.timer.stop()
        if self.isCanceled():
            return

        print("OUTPUT:")
        print(self.output)

        if not self.is_subtask:
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

    def _export_inp(self):

        if self.isCanceled():
            return False

        tools_log.log_info(f"Export INP file")

        self.process = GenerateSwmmInpFile()
        self.process.initAlgorithm(None)
        params = self._manage_params()
        context = QgsProcessingContext()
        self.feedback = QgsProcessingFeedback()
        self.feedback.progressChanged.connect(self._progress_changed)
        self.output = self.process.processAlgorithm(params, context, self.feedback)

        if self.output is not None:
            # Add transects
            self._write_transects()
            if self.export_file_path:
                try:
                    shutil.copy(self.QGIS_OUT_INP_FILE, f"{self.export_file_path}")
                except Exception as e:
                    print(e)
            if self.debug_mode:
                try:
                    shutil.copy(self.QGIS_OUT_INP_FILE, f"{self.debug_folder_path}{os.sep}debug.inp")
                except Exception as e:
                    print(e)

        return True

    def _progress_changed(self, progress):

        text = f"{self.feedback.textLog()}"
        self.progress_changed.emit(progress, text)


    def _manage_params(self):

        temp_file = tempfile.NamedTemporaryFile(suffix='.inp', delete=False)
        self.QGIS_OUT_INP_FILE = temp_file.name
        FILE_CONDUITS = self._copy_layer_renamed_fields('vi_conduits', rename=False)
        FILE_JUNCTIONS = self._copy_layer_renamed_fields('vi_junctions', rename=False)
        FILE_DIVIDERS = self._copy_layer_renamed_fields('vi_dividers', rename=False)
        FILE_ORIFICES = self._copy_layer_renamed_fields('vi_orifices', rename=False)
        FILE_OUTFALLS = self._copy_layer_renamed_fields('vi_outfalls', rename=False)
        FILE_OUTLETS = self._copy_layer_renamed_fields('vi_outlets', rename=False)
        FILE_STORAGES = self._copy_layer_renamed_fields('vi_storage', rename=False)
        FILE_PUMPS = self._copy_layer_renamed_fields('vi_pumps', rename=False)
        FILE_WEIRS = self._copy_layer_renamed_fields('vi_weirs', rename=False)
        FILE_CURVES = self._create_curves_file()
        FILE_PATTERNS = self._create_patterns_file()
        FILE_OPTIONS = self._create_options_file()
        # TODO: FILE_REPORT
        # TODO: FILE_CONTROLS
        FILE_TIMESERIES = self._create_timeseries_file()
        FILE_INFLOWS = self._create_inflows_file()
        FILE_TRANSECTS = None  # TODO: ARCHIVO EXCEL 'vi_transects'
        FILE_STREETS = None
        params = {
            'QGIS_OUT_INP_FILE': self.QGIS_OUT_INP_FILE,
            'FILE_CONDUITS': FILE_CONDUITS,
            'FILE_JUNCTIONS': FILE_JUNCTIONS,
            'FILE_DIVIDERS': FILE_DIVIDERS,
            'FILE_ORIFICES': FILE_ORIFICES,
            'FILE_OUTFALLS': FILE_OUTFALLS,
            'FILE_OUTLETS': FILE_OUTLETS,
            'FILE_STORAGES': FILE_STORAGES,
            'FILE_PUMPS': FILE_PUMPS,
            'FILE_WEIRS': FILE_WEIRS,
            'FILE_CURVES': FILE_CURVES,
            'FILE_PATTERNS': FILE_PATTERNS,
            'FILE_OPTIONS': FILE_OPTIONS,
            'FILE_TIMESERIES': FILE_TIMESERIES,
            'FILE_INFLOWS': FILE_INFLOWS,
            'FILE_TRANSECTS': FILE_TRANSECTS
        }

        if self.debug_mode:
            try:
                shutil.copy(FILE_CURVES, f"{self.debug_folder_path}{os.sep}debug_curves.xlsx")
                shutil.copy(FILE_PATTERNS, f"{self.debug_folder_path}{os.sep}debug_patterns.xlsx")
                shutil.copy(FILE_OPTIONS, f"{self.debug_folder_path}{os.sep}debug_options.xlsx")
                shutil.copy(FILE_TIMESERIES, f"{self.debug_folder_path}{os.sep}debug_timeseries.xlsx")
                shutil.copy(FILE_INFLOWS, f"{self.debug_folder_path}{os.sep}debug_inflows.xlsx")
            except Exception as e:
                print(e)

        return params

    def _copy_layer_renamed_fields(self, input_layer: str, rename=True):
        # Input layer
        output_layer_name = f'{input_layer}_output'
        input_layer_name = input_layer
        input_path = f"{QgsProject.instance().absolutePath()}{os.sep}{global_vars.project_vars['project_gpkg']}"
        input_layer_uri = f"{input_path}|layername={input_layer_name}"
        input_layer = QgsVectorLayer(input_layer_uri, input_layer_name, 'ogr')

        if not rename:
            if self.debug_mode:
                QgsProject.instance().addMapLayer(input_layer)
            return input_layer

        # Output layer
        geometry_type = input_layer.geometryType()
        geometry_type_map = {0: "Point", 1: "LineString", 2: "Polygon", 4: "NoGeometry"}
        geometry_type = geometry_type_map.get(geometry_type, "Unknown")
        srid = input_layer.crs().authid()
        if geometry_type in ("NoGeometry", "Unknown"):
            srid = global_vars.project_epsg
        output_layer = QgsVectorLayer(f'{geometry_type}?crs={srid}', f'{output_layer_name}', 'memory')

        # Copy fields with modified names
        fields = QgsFields()
        for field in input_layer.fields():
            new_field_name = _tables_dict_swapped[input_layer_name]['mapper'].get(field.name())
            if new_field_name in (None, ''):
                # TODO: review if some column is missing from mapper
                continue
            new_field = QgsField(new_field_name, field.type())
            fields.append(new_field)

        output_layer.dataProvider().addAttributes(fields)
        output_layer.updateFields()

        # Copy features
        features = []
        for feature in input_layer.getFeatures():
            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())
            new_feature.setFields(output_layer.fields())
            for field in output_layer.fields():
                new_attribute = field.name()
                old_attribute = _tables_dict[input_layer_name]['mapper'].get(new_attribute)
                new_feature.setAttribute(new_attribute, feature.attribute(old_attribute))

            features.append(new_feature)

        output_layer.dataProvider().addFeatures(features)

        if self.debug_mode:
            # Add the output layer to the project
            QgsProject.instance().addMapLayer(output_layer)

        return output_layer


    def _create_curves_file(self):
        # Use pandas to read the SQL table into a DataFrame
        query = """SELECT
                    cc.curve_type,
                    cc.idval AS curve_name,
                    ccv.xcoord,
                    ccv.ycoord,
                    cc.descript
                FROM
                    cat_curve cc
                JOIN
                    cat_curve_value ccv ON cc.idval = ccv.curve;"""
        conn = self.dao.conn
        df = pd.read_sql_query(query, conn)

        # Group the data by the 'curve_type' column
        grouped_data = df.groupby(['curve_type'])

        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file_path = temp_file.name
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            headers = ["Name", "Depth", "Area", "Annotation"]  # TODO: maybe use respective x-value/y-value columns depending on curve_type
            # Iterate over each group and save it to a separate sheet
            for curve_type, data in grouped_data:
                # Concatenate all curves of the same curve_type, with curve_name separated by semicolon
                grouped_by_curve_name = data.groupby('curve_name')
                # Track the current row position
                current_row = 1
                sheet_name = f"{curve_type[0].capitalize()}"

                for curve_name, curve_data in grouped_by_curve_name:
                    # Remove the 'curve_type' columns from the individual sheets
                    curve_data.drop(['curve_type'], axis=1, inplace=True)
                    # Save the curve data to a sheet named with the curve_type
                    curve_data.to_excel(writer, sheet_name=sheet_name, startrow=current_row, index=False, header=False)

                    # Insert a semicolon between different curve_names
                    writer.sheets[sheet_name].write(current_row + curve_data.shape[0], 0, ';')

                    # Update the current row position
                    current_row += curve_data.shape[0] + 1

                # Write headers
                for i, header in enumerate(headers):
                    writer.sheets[sheet_name].write(0, i, header)

        return file_path


    def _create_patterns_file(self):
        # Use pandas to read the SQL table into a DataFrame
        query = """SELECT
                    cp.pattern_type,
                    cp.idval AS pattern_name,
                    cpv.timestep,
                    cpv.value
                FROM
                    cat_pattern cp
                JOIN
                    cat_pattern_value cpv ON cp.idval = cpv.pattern;"""
        conn = self.dao.conn
        df = pd.read_sql_query(query, conn)

        # Group the data by the 'pattern_type' column
        grouped_data = df.groupby(['pattern_type'])

        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file_path = temp_file.name
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            tstamp_cols = {"HOURLY": "Time", "DAILY": "Day", "MONTHLY": "Month", "WEEKEND": "Time"}
            # Iterate over each group and save it to a separate sheet
            for pattern_type, data in grouped_data:
                # Concatenate all patterns of the same pattern_type, with pattern_name separated by semicolon
                grouped_by_pattern_name = data.groupby('pattern_name')
                # Track the current row position
                current_row = 1

                sheet_name = f"{pattern_type[0].capitalize()}"

                headers = ["Name", tstamp_cols.get(pattern_type[0], "DAILY"), "Factor"]

                for pattern_name, pattern_data in grouped_by_pattern_name:
                    # Remove the 'pattern_type' columns from the individual sheets
                    pattern_data.drop(['pattern_type'], axis=1, inplace=True)
                    # Save the pattern data to a sheet named with the pattern_type
                    pattern_data.to_excel(writer, sheet_name=sheet_name, startrow=current_row, index=False, header=False)

                    # Insert a semicolon between different pattern_names
                    writer.sheets[sheet_name].write(current_row + pattern_data.shape[0], 0, ';')

                    # Update the current row position
                    current_row += pattern_data.shape[0] + 1

                # Write headers
                for i, header in enumerate(headers):
                    writer.sheets[sheet_name].write(0, i, header)

        return file_path


    def _create_options_file(self):
        query = """SELECT
                    Option,
                    Value
                FROM
                    vi_options;"""
        conn = self.dao.conn
        df = pd.read_sql_query(query, conn)

        # Apply the desired transformation to the 'Option' column
        df['Option'] = df['Option'].str.replace('inp_options_', '').str.upper()

        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file_path = temp_file.name
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            sheet_name = "OPTIONS"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        return file_path


    def _create_timeseries_file(self):
        # Use pandas to read the SQL table into a DataFrame
        query = """SELECT
                    ct.idval AS timeseries_name,
                    ctv.date,
                    ctv.time,
                    ctv.value,
                    ct.fname,
                    ct.descript
                FROM
                    cat_timeseries ct
                LEFT JOIN
                    cat_timeseries_value ctv ON ct.idval = ctv.timeseries
                WHERE
                    timser_type NOT IN ('BC ELEVATION', 'BC FLOW');"""
        conn = self.dao.conn
        df = pd.read_sql_query(query, conn)

        # Group the data by the 'timeseries_name' column
        grouped_data = df.groupby(['timeseries_name'])

        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file_path = temp_file.name
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            sheet_name = "Timeseries"
            # Track the current row position
            current_row = 1
            headers = ["Name", "Date", "Time", "Value", "File_Name", "Annotation"]

            # Iterate over each timeseries and put a ';' in-between them
            for timeseries_name, data in grouped_data:

                # Save the pattern data to a sheet named with the pattern_type
                data.to_excel(writer, sheet_name=sheet_name, startrow=current_row, index=False, header=False)

                # Insert a semicolon between different pattern_names
                writer.sheets[sheet_name].write(current_row + data.shape[0], 0, ';')

                # Update the current row position
                current_row += data.shape[0] + 1

            # Write headers
            for i, header in enumerate(headers):
                writer.sheets[sheet_name].write(0, i, header)

        return file_path


    def _create_inflows_file(self):

        # Direct inflows
        query = """SELECT
                    Name, Constituent, Baseline, Baseline_Pattern, Time_Series, Scale_Factor, Type, Units_Factor
                FROM
                    vi_inflows;"""
        conn = self.dao.conn
        df_direct = pd.read_sql_query(query, conn)

        # Dry Weather inflows (dwf)
        query = """SELECT
                        Name, Constituent, Average_Value, Time_Pattern1, Time_Pattern2, Time_Pattern3, Time_Pattern4
                    FROM
                        vi_dwf;"""
        conn = self.dao.conn
        df_dwf = pd.read_sql_query(query, conn)

        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        file_path = temp_file.name
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            # Write Direct inflows to its sheet
            df_direct.to_excel(writer, sheet_name="Direct", index=False)
            # Write Dry Weather inflows to its sheet
            df_dwf.to_excel(writer, sheet_name="Dry_Weather", index=False)

        return file_path


    def _write_transects(self):

        sql = """SELECT data_group, value FROM vi_transects;"""
        rows = self.dao.get_rows(sql)
        if not rows:
            return False

        with open(self.QGIS_OUT_INP_FILE, 'a') as file:
            file.write("[TRANSECTS]\n")
            for row in rows:
                # Manage nulls
                row = tuple('' if val is None else val for val in row)
                # Write lines
                file.write('  '.join(row) + "\n")

    # endregion
