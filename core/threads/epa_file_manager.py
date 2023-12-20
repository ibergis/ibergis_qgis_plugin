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
import subprocess
import sqlite3
import pandas as pd

from qgis.PyQt.QtCore import pyqtSignal, QMetaMethod
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsField, QgsFields, QgsFeature, QgsProject

from ..utils.generate_swmm_inp.generate_swmm_inp_file import GenerateSwmmInpFile
from ..utils import tools_gw
from ... import global_vars
from ...lib import tools_log, tools_qt, tools_db, tools_qgis, tools_os
from .task import GwTask
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


class GwEpaFileManager(GwTask):
    """ This shows how to subclass QgsTask """

    fake_progress = pyqtSignal()

    def __init__(self, description, go2epa, timer=None):

        super().__init__(description)
        self.go2epa = go2epa
        self.json_result = None
        self.rpt_result = None
        self.fid = 140
        self.function_name = None
        self.timer = timer
        self.initialize_variables()
        self.set_variables_from_go2epa()


    def initialize_variables(self):

        self.exception = None
        self.error_msg = None
        self.message = None
        self.common_msg = ""
        self.function_failed = False
        self.complet_result = None
        self.replaced_velocities = False
        self.output = None
        self.folder_path = None


    def set_variables_from_go2epa(self):
        """ Set variables from object Go2Epa """

        self.dlg_go2epa = self.go2epa.dlg_go2epa
        self.result_name = self.go2epa.result_name


    def run(self):

        super().run()

        self.initialize_variables()
        tools_log.log_info(f"Task 'Go2Epa' execute function 'def _get_steps'")
        # steps = self._get_steps()
        status = True
        tools_log.log_info(f"Task 'Go2Epa' execute function 'def _exec_function_pg2epa'")
        status = self._new_export_inp()

            # status = self._exec_function_pg2epa(steps)
            # if not status:
            #     self.function_name = 'gw_fct_pg2epa_main'
            #     return False

        # if self.go2epa_export_inp:
        #     tools_log.log_info(f"Task 'Go2Epa' execute function 'def _export_inp'")
        #     status = self._export_inp()
        #
        # if status and self.go2epa_execute_epa:
        #     tools_log.log_info(f"Task 'Go2Epa' execute function 'def _execute_epa'")
        #     status = self._execute_epa()
        #
        # if status and self.go2epa_import_result:
        #     tools_log.log_info(f"Task 'Go2Epa' execute function 'def _import_rpt'")
        #     self.function_name = 'gw_fct_rpt2pg_main'
        #     status = self._import_rpt()

        return status


    def finished(self, result):

        super().finished(result)

        self.dlg_go2epa.btn_cancel.setEnabled(False)
        self.dlg_go2epa.btn_accept.setEnabled(True)

        # self._close_file()
        if self.timer:
            self.timer.stop()
        if self.isCanceled():
            return

        print("OUTPUT:")
        print(self.output)

        # If Database exception, show dialog after task has finished
        if global_vars.session_vars['last_error']:
            tools_qt.show_exception_message(msg=global_vars.session_vars['last_error_msg'])


    def cancel(self):

        tools_qgis.show_info(f"Task canceled - {self.description()}")
        # self._close_file()
        super().cancel()


    def _close_file(self, file=None):

        if file is None:
            file = self.file_rpt

        try:
            if file:
                file.close()
                del file
        except Exception:
            pass


    # region private functions

    def _new_export_inp(self):

        if self.isCanceled():
            return False

        tools_log.log_info(f"Export INP file")

        self.process = GenerateSwmmInpFile()
        self.process.initAlgorithm(None)
        params = self._manage_params()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        self.output = self.process.processAlgorithm(params, context, feedback)
        print("process finished")
        print(feedback.textLog())
        return True


    def _manage_params(self):

        self.folder_path = 'C:/Users/usuario/Desktop/QGIS Projects/drain/export_inp/'
        FILE_RAINGAGES = self._copy_layer_renamed_fields('inp_raingage')
        FILE_CONDUITS = self._copy_layer_renamed_fields('inp_conduit')
        FILE_JUNCTIONS = self._copy_layer_renamed_fields('inp_junction')
        FILE_DIVIDERS = self._copy_layer_renamed_fields('inp_divider')
        FILE_ORIFICES = self._copy_layer_renamed_fields('inp_orifice')
        FILE_OUTFALLS = self._copy_layer_renamed_fields('inp_outfall')
        FILE_OUTLETS = self._copy_layer_renamed_fields('inp_outlet')
        FILE_STORAGES = self._copy_layer_renamed_fields('inp_storage')
        FILE_PUMPS = self._copy_layer_renamed_fields('inp_pump')
        FILE_SUBCATCHMENTS = self._copy_layer_renamed_fields('inp_subcatchment')
        FILE_WEIRS = self._copy_layer_renamed_fields('inp_weir')
        FILE_CURVES = self._create_curves_file()
        FILE_PATTERNS = self._create_patterns_file()
        FILE_OPTIONS = self._create_options_file()
        # TODO: FILE_REPORT
        FILE_TIMESERIES = self._create_timeseries_file()
        FILE_INFLOWS = self._create_inflows_file()
        FILE_QUALITY = None
        FILE_TRANSECTS = None  # TODO: ARCHIVO EXCEL 'vi_transects'
        FILE_STREETS = None
        params = {
            'QGIS_OUT_INP_FILE': f'{self.folder_path}{self.result_name}.inp',
            'FILE_RAINGAGES': FILE_RAINGAGES,
            'FILE_CONDUITS': FILE_CONDUITS,
            'FILE_JUNCTIONS': FILE_JUNCTIONS,
            'FILE_DIVIDERS': FILE_DIVIDERS,
            'FILE_ORIFICES': FILE_ORIFICES,
            'FILE_OUTFALLS': FILE_OUTFALLS,
            'FILE_OUTLETS': FILE_OUTLETS,
            'FILE_STORAGES': FILE_STORAGES,
            'FILE_PUMPS': FILE_PUMPS,
            'FILE_SUBCATCHMENTS': FILE_SUBCATCHMENTS,
            'FILE_WEIRS': FILE_WEIRS,
            'FILE_CURVES': FILE_CURVES,
            'FILE_PATTERNS': FILE_PATTERNS,
            'FILE_OPTIONS': FILE_OPTIONS,
            'FILE_TIMESERIES': FILE_TIMESERIES,
            'FILE_INFLOWS': FILE_INFLOWS,
            'FILE_QUALITY': FILE_QUALITY,
            'FILE_TRANSECTS': FILE_TRANSECTS,
            'FILE_STREETS': FILE_STREETS
        }

        return params

    def _copy_layer_renamed_fields(self, input_layer: str):
        # Input layer
        output_layer_name = f'{input_layer}_output'
        input_layer_name = input_layer
        input_path = global_vars.project_vars['project_gpkg']
        input_layer_uri = f"{input_path}|layername={input_layer_name}"
        input_layer = QgsVectorLayer(input_layer_uri, input_layer_name, 'ogr')

        # Output layer
        geometry_type = input_layer.geometryType()
        geometry_type_map = {0: "Point", 1: "LineString", 2: "Polygon", 4: "NoGeometry"}
        print(f"{geometry_type=}")
        geometry_type = geometry_type_map.get(geometry_type, "Unknown")
        print(f"mapped {geometry_type=}")
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
                    cat_curve_value ccv ON cc.id = ccv.idval;"""
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Group the data by the 'curve_type' column
        grouped_data = df.groupby(['curve_type'])

        file_path = f'{self.folder_path}{os.sep}curves_file.xlsx'
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
                    cat_pattern_value cpv ON cp.id = cpv.idval;"""
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Group the data by the 'pattern_type' column
        grouped_data = df.groupby(['pattern_type'])

        file_path = f'{self.folder_path}{os.sep}patterns_file.xlsx'
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            tstamp_cols = {"HOURLY": "Hour", "DAILY": "Day", "MONTHLY": "Month", "WEEKEND": "Hour"}
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
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Apply the desired transformation to the 'Option' column
        df['Option'] = df['Option'].str.replace('inp_options_', '').str.upper()

        file_path = f'{self.folder_path}{os.sep}options_file.xlsx'
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
                    cat_timeseries_value ctv ON ct.id = ctv.idval;"""
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Group the data by the 'timeseries_name' column
        grouped_data = df.groupby(['timeseries_name'])

        file_path = f'{self.folder_path}{os.sep}timeseries_file.xlsx'
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
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df_direct = pd.read_sql_query(query, conn)
        conn.close()

        # Dry Weather inflows (dwf)
        query = """SELECT
                        Name, Constituent, Average_Value, Time_Pattern1, Time_Pattern2, Time_Pattern3, Time_Pattern4
                    FROM
                        vi_dwf;"""
        conn = sqlite3.connect(f"{global_vars.project_vars['project_gpkg']}")
        df_dwf = pd.read_sql_query(query, conn)
        conn.close()

        file_path = f'{self.folder_path}{os.sep}inflows_file.xlsx'
        # Create a new Excel writer
        with pd.ExcelWriter(file_path) as writer:
            # Write Direct inflows to its sheet
            df_direct.to_excel(writer, sheet_name="Direct", index=False)
            # Write Dry Weather inflows to its sheet
            df_dwf.to_excel(writer, sheet_name="Dry_Weather", index=False)

        return file_path

    # endregion