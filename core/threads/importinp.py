import traceback
import os
import pandas as pd

from datetime import datetime
from itertools import count

from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsCoordinateReferenceSystem, QgsProject, QgsFeature

from . import importinp_core as core
from .epa_file_manager import _tables_dict
from .task import DrTask
from ..utils.generate_swmm_inp.generate_swmm_import_inp_file import ImportInpFile
from ..utils import tools_dr
from ...lib import tools_qgis, tools_db
from ... import global_vars


class DrImportInpTask(DrTask):
    def __init__(self, description, input_file, gpkg_path, save_folder, feedback):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path
        self.save_folder = save_folder
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao = global_vars.gpkg_dao_data.clone()
            output = self._import_file()
            if not output:
                return False
            # Get non-visual data from xlsx and import it
            self._import_non_visual_data()
            # Disable triggers
            self._enable_triggers(False)
            # Get data from gpkg and import it to existing layers (changing the column names)
            self._import_gpkgs_to_project()
            # Enable triggers
            self._enable_triggers(True)
            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False

    def _import_file(self):

        self.process = ImportInpFile()
        self.process.initAlgorithm(None)
        params = self._manage_params()
        context = QgsProcessingContext()
        self.output = self.process.processAlgorithm(params, context, self.feedback)

        # processing.run("GenSwmmInp:ImportInpFile", {'INP_FILE':'P:\\31_GISWATER\\313_DEV\\epa_importinp\\maspi_proves\\ud_bcn_prim_saved.inp','GEODATA_DRIVER':1,'SAVE_FOLDER':'C:\\Users\\usuario\\Desktop\\QGIS Projects\\drain\\importinp','PREFIX':'','DATA_CRS':QgsCoordinateReferenceSystem('EPSG:25831')})
        return True

    def _manage_params(self) -> dict:
        params = {
            "INP_FILE": self.input_file,
            "GEODATA_DRIVER": 1, # 1: GPKG
            "SAVE_FOLDER": self.save_folder,
            "PREFIX": "",
            "DATA_CRS": QgsCoordinateReferenceSystem("EPSG:25831"),
        }
        return params

    def _enable_triggers(self, enable: bool) -> None:
        """ Enable or disable triggers in the database """

        create_sentences = [
            "PRAGMA foreign_keys = ON;",
            # Junctions
            "CREATE TRIGGER trg_del_inp_junction AFTER DELETE on inp_junction FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_junction'; END;",
            "CREATE TRIGGER trg_ins_code_inp_junction AFTER INSERT on inp_junction FOR EACH ROW BEGIN update inp_junction set code = 'J'||fid; END;",
            "CREATE TRIGGER trg_ins_inp_junction AFTER INSERT ON inp_junction FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_junction'); END;",
            "CREATE TRIGGER trg_upd_code_inp_junction AFTER UPDATE of code on inp_junction FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_junction'; END;",
            # Conduits
            "CREATE TRIGGER trg_del_inp_conduit AFTER DELETE on inp_conduit FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_conduit'; END;",
            "CREATE TRIGGER trg_ins_code_inp_conduit AFTER INSERT on inp_conduit FOR EACH ROW BEGIN update inp_conduit set code = 'C'||fid; END;",
            "CREATE TRIGGER trg_ins_inp_conduit AFTER INSERT ON inp_conduit FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_conduit'); END;",
            ("CREATE TRIGGER trg_ins_nodes_inp_conduit AFTER INSERT ON inp_conduit FOR EACH ROW "
            "BEGIN "
            "    UPDATE inp_conduit SET "
            "        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1), "
            "        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1) "
            "    WHERE fid = NEW.fid;-- AND (node_1 IS NULL OR node_2 IS NULL); "
            "END;"),
            "CREATE TRIGGER trg_upd_code_inp_conduit AFTER UPDATE of code on inp_conduit FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_conduit'; END;",
            ("CREATE TRIGGER trg_upd_nodes_inp_conduit AFTER UPDATE OF geom ON inp_conduit FOR EACH ROW "
            "BEGIN "
            "    UPDATE inp_conduit SET "
            "        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1), "
            "        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1) "
            "    WHERE geom = NEW.geom; -- AND (node_1 IS NULL OR node_2 IS NULL); "
            "END;"),
        ]
        delete_sentences = [
            "PRAGMA foreign_keys = OFF;",
            # Junctions
            "DROP TRIGGER trg_del_inp_junction",
            "DROP TRIGGER trg_ins_code_inp_junction",
            "DROP TRIGGER trg_ins_inp_junction",
            "DROP TRIGGER trg_upd_code_inp_junction",
            # Conduits
            "DROP TRIGGER trg_del_inp_conduit",
            "DROP TRIGGER trg_ins_code_inp_conduit",
            "DROP TRIGGER trg_ins_inp_conduit",
            "DROP TRIGGER trg_ins_nodes_inp_conduit",
            "DROP TRIGGER trg_upd_code_inp_conduit",
            "DROP TRIGGER trg_upd_nodes_inp_conduit",
        ]
        if enable:
            sentences = create_sentences
        else:
            sentences = delete_sentences

        for sentence in sentences:
            tools_db.execute_sql(sentence, dao=self.dao)

    def _import_non_visual_data(self):
        """ Import the non-visual data from the xlsx to the gpkg """

        from swmm_api import read_inp_file
        # Get the data from the inp file
        inp_file = self.input_file
        self.network = read_inp_file(inp_file)

        try:
            self._save_patterns()
            self._save_curves()
            self._save_timeseries()
            self._save_controls()
            # self._save_lids()
        except Exception as e:
            print(e)
            return

    def _import_gpkgs_to_project(self):
        """ Import the data from the gpkg to the project """

        gpkgs = ['SWMM_junctions', 'SWMM_outfalls', 'SWMM_storages', 'SWMM_pumps', 'SWMM_orifices', 'SWMM_weirs',
                 'SWMM_outlets', 'SWMM_conduits', 'SWMM_raingages', 'SWMM_subcatchments']
        layermap = {
            'SWMM_conduits': 'inp_conduit',
            'SWMM_junctions': 'inp_junction',
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
            gpkg_file = f"{self.save_folder}{os.sep}{gpkg}.gpkg"

            if not os.path.exists(gpkg_file):
                print(f"Skipping {gpkg_file}, does not exist.")
                continue

            imported_layers = tools_dr.load_gpkg(str(gpkg_file))

            for layer_name, source_layer in imported_layers.items():
                dr_layername = layermap.get(layer_name)
                if not dr_layername:
                    print(f"Skipping {dr_layername}, not found in layermap.")
                    continue

                target_layer = tools_qgis.get_layer_by_tablename(dr_layername)

                if not target_layer:
                    print(f"Skipping {dr_layername}, not found in project.")
                    continue

                target_layer = target_layer
                field_map = _tables_dict[dr_layername]["mapper"]
                print(f"Importing {dr_layername} into project...")
                self._insert_data(source_layer, target_layer, field_map, batch_size=50000)

                print(f"Imported {dr_layername} into project.")

    def _insert_data(self, source_layer, target_layer, field_map, batch_size=1000):
        """Copies features from the source layer to the target layer with mapped fields, committing in batches."""

        # Get the target field names in order
        target_field_names = [field.name() for field in target_layer.fields()]

        features_to_add = []

        for feature in source_layer.getFeatures():
            new_feature = QgsFeature(target_layer.fields())

            # Map attributes efficiently
            attributes = [None] * len(target_field_names)
            for src_field, tgt_field in field_map.items():
                if tgt_field in target_field_names:
                    attributes[target_field_names.index(tgt_field)] = feature[src_field]
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

        pattern_rows = tools_db.get_rows("SELECT idval FROM cat_pattern", dao=self.dao)
        patterns_db: list[str] = []
        if pattern_rows:
            patterns_db = [x[0] for x in pattern_rows]

        # self.results["patterns"] = 0
        for pattern_name, pattern in self.network[PATTERNS].items():
            if pattern_name in patterns_db:
                message = f'The pattern "{pattern_name}" already exists in database. Skipping...'
                print(message)
                continue

            pattern_type = pattern.cycle
            sql = f"INSERT INTO cat_pattern (idval, pattern_type) VALUES ('{pattern_name}', '{pattern_type}')"
            tools_db.execute_sql(sql, dao=self.dao)

            values = []
            for idx, f in enumerate(pattern.factors):
                values_str = f"('{pattern_name}', {idx+1}, {f})"
                values.append(values_str)

            values_str = ", ".join(values)
            sql = f"INSERT INTO cat_pattern_value (pattern, timestep, value) VALUES {values_str}"
            tools_db.execute_sql(sql, dao=self.dao)
            # self.results["patterns"] += 1

    def _save_curves(self) -> None:
        from swmm_api.input_file.section_labels import CURVES

        curve_rows = tools_db.get_rows("SELECT idval FROM cat_curve", dao=self.dao)
        curves_db: set[str] = set()
        if curve_rows:
            curves_db = {x[0] for x in curve_rows}

        # self.results["curves"] = 0
        for curve_name, curve in self.network[CURVES].items():
            if curve.kind is None:
                message = f'The "{curve_name}" curve does not have a specified curve type and was not imported.'
                print(message)
                continue

            if curve_name in curves_db:
                message = f'The curve "{curve_name}" already exists in database. Skipping...'
                print(message)
                continue

            curve_type: str = curve.kind

            sql = f"INSERT INTO cat_curve (idval, curve_type) VALUES ('{curve_name}', '{curve_type}')"
            tools_db.execute_sql(sql, dao=self.dao)

            values = []
            for x, y in curve.points:
                values_str = f"('{curve_name}', {x}, {y})"
                values.append(values_str)
            values_str = ", ".join(values)
            sql = f"INSERT INTO cat_curve_value (curve, xcoord, ycoord) VALUES {values_str}"
            tools_db.execute_sql(sql, dao=self.dao)
            # self.results["curves"] += 1

    def _save_timeseries(self) -> None:
        from swmm_api.input_file.section_labels import TIMESERIES
        from swmm_api.input_file.sections import TimeseriesFile, TimeseriesData

        ts_rows = tools_db.get_rows("SELECT idval FROM cat_timeseries", dao=self.dao)
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
        for ts_name, ts in self.network[TIMESERIES].items():
            if ts is None:
                message = f'The timeseries "{ts_name}" was not imported.'
                print(message)
                continue

            if ts_name in ts_db:
                message = f'The timeseries "{ts_name}" already exists in database. Skipping...'
                print(message)
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
            tools_db.execute_sql(sql, dao=self.dao)

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
                ts_data_f = format_ts(ts_data)

                values_str = ", ".join([f"'{ts_name}'"] + [f"'{x}'" for x in ts_data_f])
                values.append(f"({values_str})")
            values_str = ", ".join(values)
            sql += f"{values_str}"
            tools_db.execute_sql(sql, dao=self.dao)
            # self.results["timeseries"] += 1

    def _save_controls(self) -> None:
        from swmm_api.input_file.section_labels import CONTROLS

        controls_rows = tools_db.get_rows("SELECT descript FROM cat_controls", dao=self.dao)
        controls_db: set[str] = set()
        if controls_rows:
            controls_db = {x[0] for x in controls_rows}

        # self.results["controls"] = 0
        for control_name, control in self.network[CONTROLS].items():
            text = control.to_inp_line()
            if text in controls_db:
                msg = f"The control '{control_name}' is already on database. Skipping..."
                print(msg)
                continue
            sql = f"INSERT INTO cat_controls (descript) VALUES ('{text}')"
            tools_db.execute_sql(sql, dao=self.dao)
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
