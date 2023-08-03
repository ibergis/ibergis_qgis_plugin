from . import importinp_core as core
from .task import GwTask
from ..utils.generate_swmm_inp import inp2dict
from ... import global_vars
from ...lib.tools_gpkgdao import GwGpkgDao


class GwImportInpTask(GwTask):
    def __init__(self, description, input_file, gpkg_path):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path

    def run(self):
        super().run()
        try:
            self.dao = GwGpkgDao()
            self.dao.init_db(self.gpkg_path)
            self._import_file()
        except Exception as e:
            self.exception = e
            return False
        return True

    def _get_colums(self, table):
        rows = self.dao.get_rows(f"select name from pragma_table_info('{table}')")
        columns = {row[0] for row in rows if row[0] not in ("fid", "geom")}
        return columns

    def _import_file(self):
        gpkg_file = self.dao.db_filepath
        dicts = inp2dict(self.input_file)
        columns = {table: self._get_colums(table) for table in core.tables()}
        data = core.get_dataframes(dicts, columns, global_vars.data_epsg)
        for item in data:
            if len(item["df"]) == 0:
                print(f"Skipping empty table {item['table']}")
                continue
            print(f"Saving table {item['table']}")
            item["df"].to_file(gpkg_file, driver="GPKG", layer=item["table"], mode="a")
