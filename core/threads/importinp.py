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
        columns = {table: self._get_colums(table) for table in core.tables()}
        data = core.get_dataframes(inp_dict, global_vars.data_epsg)

        if self.isCanceled():
            return False

        for i, item in enumerate(data):
            self.feedback.setProgress(i / len(data) * 100)
            if len(item["df"]) == 0:
                self.feedback.setProgressText(f"Skipping empty table {item['table']}")
                continue
            if self.isCanceled():
                return False
            self.feedback.setProgressText(f"Saving table {item['table']}")

            if item["table"] == "cat_curve":
                curves = item["df"][["idval", "curve_type"]].drop_duplicates()
                curve_values = item["df"][["idval", "xcoord", "ycoord"]].rename(
                    columns={"idval": "curve"}
                )
                connection = self.dao.conn
                curves.to_sql("cat_curve", connection, if_exists="append", index=False)
                curve_values.to_sql(
                    "cat_curve_value", connection, if_exists="append", index=False
                )
            else:
                invalid_columns = set(item["df"].columns).difference(
                    columns[item["table"]], {"geometry"}
                )
                if invalid_columns:
                    raise ValueError(
                        f"Invalid columns for {item['table']}: {invalid_columns}"
                    )
                missing_columns = columns[item["table"]].difference(item["df"].columns)
                for column in missing_columns:
                    item["df"][column] = None
                item["df"].to_file(
                    gpkg_file, driver="GPKG", layer=item["table"], mode="a"
                )

        # for i, item in enumerate(data.values()):

        #     self.feedback.setProgress(i / len(data) * 100)

        #     ##TODO: Check this
        #     if item["df"] is None:
        #         continue

        #     if len(item["df"]) == 0:
        #         self.feedback.setProgressText(f"Skipping empty table {item['table']}")
        #         continue
        #     if self.isCanceled():
        #         return False
        #     self.feedback.setProgressText(f"Saving table {item['table']}")

        #     ##TODO:: Verify conflicts with "mode"=a to append values
        #     item["df"].to_file(gpkg_file, driver="GPKG", layer=item["table"], mode="a")
        #     # item["df"].to_file(gpkg_file, driver="GPKG", layer=item["table"])

        return True
