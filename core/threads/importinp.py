import traceback

from . import importinp_core as core
from .task import GwTask
from ..utils.generate_swmm_inp import inp2dict
from ... import global_vars


class GwImportInpTask(GwTask):
    def __init__(
        self, description, input_file, gpkg_path, sector_id, scenario_id, feedback
    ):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path
        self.sector_id = sector_id
        self.scenario_id = scenario_id
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
        dicts = inp2dict(self.input_file, self.feedback)
        if self.isCanceled():
            return False
        columns = {table: self._get_colums(table) for table in core.tables()}
        data = core.get_dataframes(
            dicts, self.sector_id, self.scenario_id, columns, global_vars.data_epsg
        )
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
            item["df"].to_file(gpkg_file, driver="GPKG", layer=item["table"], mode="a")
        return True
