import traceback
import os
import math

from datetime import datetime
from itertools import count

from qgis.core import QgsProcessingContext, QgsFeature
from qgis.PyQt.QtCore import pyqtSignal

from .epa_file_manager import _tables_dict
from .task import DrTask
from ..utils.generate_swmm_inp.generate_swmm_import_inp_file import ImportInpFile
from ..utils import tools_dr
from ...lib import tools_qgis, tools_log, tools_qt
from ...lib.tools_gpkgdao import DrGpkgDao
from ... import global_vars
from typing import Optional


class DrImportInpTask(DrTask):
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')

    # Progress percentages
    PROGRESS_INIT = 0
    PROGRESS_IMPORT_FILE = 70
    PROGRESS_IMPORT_NON_VISUAL = 80
    PROGRESS_IMPORT_GPKGS = 90
    PROGRESS_END = 100

    def __init__(self, description, input_file, gpkg_path, save_folder, feedback):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path
        self.save_folder = save_folder
        self.feedback = feedback
        self.dividers_to_update: dict[str, str] = {}

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao: Optional[DrGpkgDao] = global_vars.gpkg_dao_data.clone()
            output = self._import_file()
            if not output:
                return False
            # Get non-visual data from xlsx and import it
            self._import_non_visual_data()
            if self.isCanceled():
                return
            # Disable triggers
            self._enable_triggers(False)
            if self.isCanceled():
                return
            return True
        except Exception:
            self.exception = traceback.format_exc()
            title = "Error"
            self.progress_changed.emit(tools_qt.tr(title), None, self.exception, True)
            return False

    def finished(self, result):

        super().finished(result)

        if self.dao is not None:
            self.dao.close_db()

        if self.isCanceled() or not result:
            return

        self.dao: Optional[DrGpkgDao] = global_vars.gpkg_dao_data

        # Get data from gpkg and import it to existing layers (changing the column names)
        self._import_gpkgs_to_project()

        if self.isCanceled():
            return
        # Execute the after import fct
        self._execute_after_import_fct()
        if self.isCanceled():
            return
        # Enable triggers
        self._enable_triggers(True)

    def _import_file(self):

        self.process = ImportInpFile()
        self.process.initAlgorithm(None)
        params = self._manage_params()
        context = QgsProcessingContext()
        self.output = self.process.processAlgorithm(params, context, self.feedback)

        # processing.run("GenSwmmInp:ImportInpFile", {'INP_FILE':'P:\\31_GISWATER\\313_DEV\\epa_importinp\\maspi_proves\\ud_bcn_prim_saved.inp','GEODATA_DRIVER':1,'SAVE_FOLDER':'C:\\Users\\usuario\\Desktop\\QGIS Projects\\drain\\importinp','PREFIX':'','DATA_CRS':QgsCoordinateReferenceSystem('EPSG:25831')})
        return True

    def _execute_after_import_fct(self):
        """ Execute the after import fct """

        fct_path = os.path.join(global_vars.plugin_dir, 'dbmodel', 'fct', 'fct_after_import_inp.sql')
        with open(fct_path, 'r', encoding="utf8") as f:
            sql = f.read()
        status = self.dao.execute_script_sql(str(sql))
        if not status:
            msg = "Error {0} not executed"
            msg_params = (fct_path,)
            tools_log.log_error(msg, msg_params=msg_params)
            title = "Execute after import fct"
            msg = "Error {0} not executed"
            msg_params = (fct_path,)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)

    def _manage_params(self) -> dict:
        params = {
            "INP_FILE": self.input_file,
            "GEODATA_DRIVER": 1,  # 1: GPKG
            "SAVE_FOLDER": self.save_folder,
            "PREFIX": "",
            "DATA_CRS": f"EPSG:{global_vars.project_epsg}",
        }
        return params

    def _enable_triggers(self, enable: bool) -> None:
        """ Enable or disable triggers in the database """
        if self.isCanceled():
            return
        trg_path = os.path.join(global_vars.plugin_dir, 'dbmodel', 'trg')
        if enable:
            f_to_read = os.path.join(trg_path, 'trg_create.sql')
            with open(f_to_read, 'r', encoding="utf8") as f:
                sql = f.read()
        else:
            f_to_read = os.path.join(trg_path, 'trg_delete.sql')
            with open(f_to_read, 'r', encoding="utf8") as f:
                sql = f.read()
        status = self.dao.execute_script_sql(str(sql))
        if not status:
            print(f"Error {f_to_read} not executed")
            print(self.dao.last_error)
            if enable:
                title = "Enable triggers"
                msg = "Error {0} not executed: {1}"
                msg_params = (f_to_read, self.dao.last_error)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)
            else:
                title = "Disable triggers"
                msg = "Error {0} not executed: {1}"
                msg_params = (f_to_read, self.dao.last_error)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_NON_VISUAL, tools_qt.tr(msg, list_params=msg_params), True)
        else:
            if enable:
                title = "Enable triggers"
                msg = "Triggers created"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_END, tools_qt.tr(msg), True)
            else:
                title = "Disable triggers"
                msg = "Triggers disabled"
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_NON_VISUAL, tools_qt.tr(msg), True)

    def _import_non_visual_data(self):
        """ Import the non-visual data from the xlsx to the gpkg """

        from swmm_api import read_inp_file
        # Get the data from the inp file
        inp_file = self.input_file
        self.network = read_inp_file(inp_file)

        try:
            self.PROGRESS_IMPORT_FILE += 3
            self._save_patterns()
            self.PROGRESS_IMPORT_FILE += 3
            self._save_curves()
            self.PROGRESS_IMPORT_FILE += 3
            self._save_timeseries()
            self.PROGRESS_IMPORT_FILE += 3
            self._save_controls()
            # self._save_lids()
        except Exception as e:
            print(e)
            return

    def _import_gpkgs_to_project(self):
        """ Import the data from the gpkg to the project """

        gpkgs = ['SWMM_junctions', 'SWMM_outfalls', 'SWMM_storages', 'SWMM_dividers', 'SWMM_pumps', 'SWMM_orifices', 'SWMM_weirs',
                 'SWMM_outlets', 'SWMM_conduits', 'SWMM_raingages', 'SWMM_subcatchments']
        layermap = {
            'SWMM_conduits': 'inp_conduit',
            'SWMM_junctions': 'inp_junction',
            'SWMM_dividers': 'inp_divider',
            'SWMM_orifices': 'inp_orifice',
            'SWMM_outfalls': 'inp_outfall',
            'SWMM_outlets': 'inp_outlet',
            'SWMM_pumps': 'inp_pump',
            'SWMM_raingages': 'inp_raingage',
            'SWMM_storages': 'inp_storage',
            'SWMM_subcatchments': 'inp_subcatchment',
            'SWMM_weirs': 'inp_weir'
        }
        for gpkg in gpkgs:
            if self.isCanceled():
                return
            self.PROGRESS_IMPORT_GPKGS = int(math.ceil((len(gpkgs) / 10)) * (gpkgs.index(gpkg) + 1) + self.PROGRESS_IMPORT_NON_VISUAL)
            gpkg_file = f"{self.save_folder}{os.sep}{gpkg}.gpkg"
            title = "Import gpkgs to project"
            msg = "Processing file...{0}"
            msg_params = (gpkg_file,)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)

            if not os.path.exists(gpkg_file):
                print(f"Skipping {gpkg_file}, does not exist.")
                msg = "Skipping {0}, does not exist."
                msg_params = (gpkg_file,)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            imported_layers = tools_dr.load_gpkg(str(gpkg_file))

            for layer_name, source_layer in imported_layers.items():
                if self.isCanceled():
                    return
                dr_layername = layermap.get(layer_name)
                if not dr_layername:
                    print(f"Skipping {dr_layername}, not found in layermap.")
                    msg = "Skipping {0}, not found in layermap."
                    msg_params = (dr_layername,)
                    self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)
                    continue

                target_layer = tools_qgis.get_layer_by_tablename(dr_layername)

                if not target_layer:
                    print(f"Skipping {dr_layername}, not found in project.")
                    msg = "Skipping {0}, not found in project."
                    msg_params = (dr_layername,)
                    self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)
                    continue

                target_layer = target_layer
                field_map = _tables_dict[dr_layername]["mapper"]
                print(f"Importing {dr_layername} into project...")
                msg = "Importing {0} into project..."
                msg_params = (dr_layername,)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)
                self._insert_data(source_layer, target_layer, field_map, batch_size=50000)

                print(f"Imported {dr_layername} into project.")
                msg = "Imported {0} into project."
                msg_params = (dr_layername,)
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)

                # Insert junctions, dividers, outfalls, storages into node table
                if dr_layername in ['inp_junction', 'inp_divider', 'inp_outfall', 'inp_storage']:
                    # For some reason the node table is not detected
                    sql = "SELECT * FROM node"
                    self.dao.execute_sql(sql)
                    if self.dao.last_error:
                        print(self.dao.last_error)
                    sql = f"INSERT INTO node (table_fid, code, geom, table_name) SELECT fid, code, geom, '{dr_layername}' FROM {dr_layername}"
                    self.dao.execute_sql(sql)
                elif dr_layername in ['inp_conduit', 'inp_pump', 'inp_orifice', 'inp_weir', 'inp_outlet']:
                    # For some reason the arc table is not detected
                    sql = "SELECT * FROM arc"
                    self.dao.execute_sql(sql)
                    sql = f"INSERT INTO arc (table_fid, code, geom, table_name) SELECT fid, code, geom, '{dr_layername}' FROM {dr_layername}"
                    self.dao.execute_sql(sql)
                if self.dao.last_error:
                    print(self.dao.last_error)
                    title = "Import gpkgs to project"
                    msg = "Error inserting nodes or arcs: {0}"
                    msg_params = (self.dao.last_error,)
                    self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_GPKGS, tools_qt.tr(msg, list_params=msg_params), True)

        # Update dividers arc
        for divider in self.dividers_to_update.keys():
            sql = f"UPDATE inp_divider SET divert_arc = '{self.dividers_to_update[divider]}' WHERE code = '{divider}';"
            self.dao.execute_sql(sql)

    def _insert_data(self, source_layer, target_layer, field_map, batch_size=1000):
        """Copies features from the source layer to the target layer with mapped fields, committing in batches."""

        # Get the target field names in order
        target_field_names = [field.name() for field in target_layer.fields()]

        features_to_add = []

        for feature in source_layer.getFeatures():
            if self.isCanceled():
                return
            new_feature = QgsFeature(target_layer.fields())

            # Map attributes efficiently
            attributes = [None] * len(target_field_names)
            for src_field, tgt_field in field_map.items():
                if tgt_field in target_field_names:
                    if not (source_layer.name() == "SWMM_dividers" and tgt_field == "divert_arc"):
                        attributes[target_field_names.index(tgt_field)] = feature[src_field]
                    else:
                        self.dividers_to_update[feature['Name']] = feature[src_field]
            new_feature.setAttributes(attributes)
            new_feature.setGeometry(feature.geometry())  # Preserve geometry
            features_to_add.append(new_feature)

            # Commit in batches
            if len(features_to_add) >= batch_size:
                target_layer.startEditing()
                target_layer.addFeatures(features_to_add)
                target_layer.commitChanges()
                features_to_add.clear()

        # Commit any remaining features
        if features_to_add:
            target_layer.startEditing()
            target_layer.addFeatures(features_to_add)
            target_layer.commitChanges()

    def _save_patterns(self):
        from swmm_api.input_file.section_labels import PATTERNS

        pattern_rows = self.dao.get_rows("SELECT idval FROM cat_pattern")
        patterns_db: list[str] = []
        if pattern_rows:
            patterns_db = [x[0] for x in pattern_rows]

        # self.results["patterns"] = 0
        title = "Save patterns"
        for pattern_name, pattern in self.network[PATTERNS].items():
            if self.isCanceled():
                return
            if pattern_name in patterns_db:
                msg = "The pattern {0} already exists in database. Skipping..."
                msg_params = (pattern_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            pattern_type = pattern.cycle
            sql = f"INSERT INTO cat_pattern (idval, pattern_type) VALUES ('{pattern_name}', '{pattern_type}')"
            self.dao.execute_sql(sql)
            msg = "Inserted pattern {0}, type {1} into cat_pattern"
            msg_params = (pattern_name, pattern_type)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)

            values = []
            for idx, f in enumerate(pattern.factors):
                if self.isCanceled():
                    return
                values_str = f"('{pattern_name}', {idx + 1}, {f})"
                values.append(values_str)

            values_str = ", ".join(values)
            sql = f"INSERT INTO cat_pattern_value (pattern, timestep, value) VALUES {values_str}"
            self.dao.execute_sql(sql)
            # self.progress_changed.emit("Save patterns", self.PROGRESS_IMPORT_FILE, f'Inserted pattern values({values_str}) into cat_pattern_value', True)
            # self.results["patterns"] += 1

    def _save_curves(self) -> None:
        from swmm_api.input_file.section_labels import CURVES

        curve_rows = self.dao.get_rows("SELECT idval FROM cat_curve")
        curves_db: set[str] = set()
        if curve_rows:
            curves_db = {x[0] for x in curve_rows}

        # self.results["curves"] = 0
        title = "Save curves"
        for curve_name, curve in self.network[CURVES].items():
            if self.isCanceled():
                return
            if curve.kind is None:
                msg = "The {0} curve does not have a specified curve type and was not imported."
                msg_params = (curve_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            if curve_name in curves_db:
                msg = "The curve {0} already exists in database. Skipping..."
                msg_params = (curve_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            curve_type: str = curve.kind

            sql = f"INSERT INTO cat_curve (idval, curve_type) VALUES ('{curve_name}', '{curve_type}')"
            self.dao.execute_sql(sql)
            msg = "Inserted curve {0}, type {1} into cat_curve"
            msg_params = (curve_name, curve_type)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)

            values = []
            for x, y in curve.points:
                if self.isCanceled():
                    return
                values_str = f"('{curve_name}', {x}, {y})"
                values.append(values_str)
            values_str = ", ".join(values)
            sql = f"INSERT INTO cat_curve_value (curve, xcoord, ycoord) VALUES {values_str}"
            self.dao.execute_sql(sql)
            # self.progress_changed.emit("Save curves", self.PROGRESS_IMPORT_FILE, f'Inserted curve values({values_str}) into cat_curve_value', True)
            # self.results["curves"] += 1

    def _save_timeseries(self) -> None:
        from swmm_api.input_file.section_labels import TIMESERIES
        from swmm_api.input_file.sections import TimeseriesFile, TimeseriesData

        ts_rows = self.dao.get_rows("SELECT idval FROM cat_timeseries")
        ts_db: set[str] = set()
        if ts_rows:
            ts_db = {x[0] for x in ts_rows}

        def format_ts(ts_data: tuple) -> tuple:
            ts_data_f = tuple()
            if not ts_data:
                return ts_data_f

            def format_time(time, value) -> tuple:
                if isinstance(time, float):
                    total_minutes = int(time * 60)
                    hh = total_minutes // 60
                    mm = total_minutes % 60
                    return (f"{hh:02}:{mm:02}", value)
                if isinstance(time, datetime):
                    date_str = time.strftime("%m/%d/%Y")
                    time_str = time.strftime("%H:%M")
                    return (f"{date_str}", f"{time_str}", value)
                return tuple()

            ts_data_f = format_time(ts_data[0], ts_data[1])
            return ts_data_f

        # self.results["timeseries"] = 0
        title = "Save timeseries"
        for ts_name, ts in self.network[TIMESERIES].items():
            if self.isCanceled():
                return
            if ts is None:
                msg = "The timeseries {0} was not imported."
                msg_params = (ts_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            if ts_name in ts_db:
                msg = "The timeseries {0} already exists in database. Skipping..."
                msg_params = (ts_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)
                continue

            fname = None
            times_type = None
            if type(ts) is TimeseriesFile:
                fname = ts.filename
                times_type = "FILE"
            elif type(ts) is TimeseriesData:
                times_type = "ABSOLUTE" if isinstance(ts.data[0][0], datetime) else "RELATIVE"

            fields_str = "idval, timser_type, times_type"
            if fname:
                fields_str += ", fname"
            values_str = f"'{ts_name}', 'OTHER', '{times_type}'"
            if fname:
                values_str += f", '{fname}'"
            sql = f"INSERT INTO cat_timeseries ({fields_str}) VALUES ({values_str})"
            self.dao.execute_sql(sql)
            msg = "Inserted timeseries({0}) into cat_timeseries"
            msg_params = (values_str,)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_FILE, tools_qt.tr(msg, list_params=msg_params), True)

            match times_type:
                case "RELATIVE":
                    fields = "timeseries, time, value"
                case "ABSOLUTE":
                    fields = "timeseries, date, time, value"
                case _:
                    continue

            sql = f"INSERT INTO cat_timeseries_value ({fields}) VALUES "
            values = []
            for ts_data in ts.data:
                if self.isCanceled():
                    return
                ts_data_f = format_ts(ts_data)

                values_str = ", ".join([f"'{ts_name}'"] + [f"'{x}'" for x in ts_data_f])
                values.append(f"({values_str})")
            values_str = ", ".join(values)
            sql += f"{values_str}"
            self.dao.execute_sql(sql)
            # self.progress_changed.emit("Save timeseries", self.PROGRESS_IMPORT_FILE, f'Inserted timeseries values({values_str}) into cat_timeseries_value', True)
            # self.results["timeseries"] += 1

    def _save_controls(self) -> None:
        from swmm_api.input_file.section_labels import CONTROLS

        controls_rows = self.dao.get_rows("SELECT descript FROM cat_controls")
        controls_db: set[str] = set()
        if controls_rows:
            controls_db = {x[0] for x in controls_rows}

        # self.results["controls"] = 0
        title = "Save controls"
        for control_name, control in self.network[CONTROLS].items():
            if self.isCanceled():
                return
            text = control.to_inp_line()
            if text in controls_db:
                msg = "The control {0} is already on database. Skipping..."
                msg_params = (control_name,)
                print(tools_qt.tr(msg, list_params=msg_params))
                self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_NON_VISUAL, tools_qt.tr(msg, list_params=msg_params), True)
                continue
            sql = f"INSERT INTO cat_controls (descript) VALUES ('{text}')"
            self.dao.execute_sql(sql)
            msg = "Inserted control({0}) into cat_controls"
            msg_params = (text,)
            self.progress_changed.emit(tools_qt.tr(title), self.PROGRESS_IMPORT_NON_VISUAL, tools_qt.tr(msg, list_params=msg_params), True)
            # self.results["controls"] += 1

    def _save_lids(self) -> None:
        from swmm_api.input_file.section_labels import LID_CONTROLS

        lid_rows = get_rows("SELECT lidco_id FROM inp_lid", commit=self.force_commit)
        lids_db: set[str] = set()
        if lid_rows:
            lids_db = {x[0] for x in lid_rows}

        self.results["lids"] = 0
        for lid_name, lid in self.network[LID_CONTROLS].items():
            if lid_name in lids_db:
                # Manage if lid already exists
                for i in count(2):
                    new_name = f"{lid_name}_{i}"
                    if new_name in lids_db:
                        continue
                    message = f'The curve "{lid_name}" has been renamed to "{new_name}" to avoid a collision with an existing curve.'
                    self.mappings["curves"][lid_name] = new_name
                    lid_name = new_name
                    break

            lid_type: str = lid.lid_kind
            sql = "INSERT INTO inp_lid (lidco_id, lidco_type) VALUES (%s, %s)"
            params = (lid_name, lid_type)
            execute_sql(sql, params, commit=self.force_commit)

            # Insert lid_values
            sql = """
                INSERT INTO inp_lid_value (lidco_id, lidlayer, value_2, value_3, value_4, value_5, value_6, value_7, value_8)
                VALUES %s
            """
            template = "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = []
            for k, v in lid.layer_dict.items():
                match k:
                    case 'SURFACE':
                        lid_values = (lid_name, k, v.StorHt, v.VegFrac, v.Rough, v.Slope, v.Xslope, None, None)
                    case 'SOIL':
                        lid_values = (lid_name, k, v.Thick, v.Por, v.FC, v.WP, v.Ksat, v.Kcoeff, v.Suct)
                    case 'PAVEMENT':
                        lid_values = (lid_name, k, v.Thick, v.Vratio, v.FracImp, v.Perm, v.Vclog, v.regeneration_interval, v.regeneration_fraction)
                    case 'STORAGE':
                        lid_values = (lid_name, k, v.Height, v.Vratio, v.Seepage, v.Vclog, v.Covrd, None, None)
                    case 'DRAIN':
                        lid_values = (lid_name, k, v.Coeff, v.Expon, v.Offset, v.Delay, v.open_level, v.close_level, v.Qcurve)
                    case 'DRAINMAT':
                        lid_values = (lid_name, k, v.Thick, v.Vratio, v.Rough, None, None, None, None)
                    case _:
                        continue
                params.append(lid_values)
            toolsdb_execute_values(sql, params, template, commit=self.force_commit)
            self.results["lids"] += 1
