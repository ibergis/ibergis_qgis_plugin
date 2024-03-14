import traceback

from . import importinp_core as core
from .task import DrTask
from ..utils.generate_swmm_inp import inp2dict
from ... import global_vars


class DrImportInpTask(DrTask):
    def __init__(self, description, input_file, gpkg_path, feedback):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao = global_vars.gpkg_dao_data.clone()
            return self._import_file()
        except Exception:
            self.exception = traceback.format_exc()
            return False

    def _get_colums(self, table):
        rows = self.dao.get_rows(f"select name from pragma_table_info('{table}')")
        columns = {row[0] for row in rows if row[0] not in ("fid", "geom")}
        return columns

    def _import_file(self):
        gpkg_file = self.dao.db_filepath
        inp_dict = inp2dict(self.input_file, self.feedback)
        if self.isCanceled():
            return False
        data = core.get_dataframes(inp_dict, global_vars.data_epsg)

        if self.isCanceled():
            return False

        for i, item in enumerate(data):
            self.feedback.setProgress(i / len(data) * 100)
            table_name = item["table"]
            df = item["df"]
            if len(df) == 0:
                self.feedback.setProgressText(f"Skipping empty table {table_name}")
                continue
            if self.isCanceled():
                return False
            self.feedback.setProgressText(f"Saving table {table_name}")

            if table_name in ["OPTIONS", "REPORT"]:
                for row in df.itertuples():
                    self.dao.execute_sql(
                        f"""
                        UPDATE config_param_user
                        SET value = '{row.value}'
                        WHERE parameter = '{row.parameter}'
                        """
                    )
                continue

            if table_name == "CONTROLS":
                self.dao.execute_sql(
                    f"INSERT INTO cat_controls (descript) VALUES ('{df}')"
                )
                continue

            columns = self._get_colums(table_name)

            invalid_columns = set(df.columns).difference(columns, {"geometry"})
            if invalid_columns:
                raise ValueError(f"Invalid columns for {table_name}: {invalid_columns}")

            missing_columns = columns.difference(df.columns)
            for column in missing_columns:
                df[column] = None

            if "geometry" in df.columns:
                df.to_file(gpkg_file, driver="GPKG", layer=table_name, mode="a")
            else:
                connection = self.dao.conn
                df.to_sql(table_name, connection, if_exists="append", index=False)

        return True
