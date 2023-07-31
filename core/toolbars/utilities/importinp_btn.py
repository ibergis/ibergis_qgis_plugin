import geopandas as gpd
from pathlib import Path
from . import importinp_core as core
from ..dialog import GwAction
from ...utils.generate_swmm_inp import inp2dict
from .... import global_vars


class GwImportINPButton(GwAction):
    """Button XX: ImportINP"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        inpfile = Path.home() / "Documents/drain/swmm.inp"
        gpkg_file = global_vars.gpkg_dao_data.db_filepath
        dicts = inp2dict(inpfile)
        columns = {table: self.get_colums(table) for table in core.tables()}
        data = core.get_dataframes(dicts, columns, global_vars.data_epsg)
        for item in data:
            item["df"].to_file(gpkg_file, driver="GPKG", layer=item["table"], mode="a")

        rows = global_vars.gpkg_dao_data.get_rows(
            "select * from inp_conduit where fid > 100 limit 5"
        )
        for row in rows:
            print(row)

    def get_colums(self, table):
        rows = global_vars.gpkg_dao_data.get_rows(
            f"select name from pragma_table_info('{table}')"
        )
        columns = {row[0] for row in rows if row[0] not in ("fid", "geom")}
        return columns
