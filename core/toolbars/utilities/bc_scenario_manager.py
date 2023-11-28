from qgis.PyQt.QtWidgets import QAbstractItemView, QTableView, QLineEdit, QComboBox
from qgis.PyQt.QtSql import QSqlTableModel

from ..dialog import GwAction
from ...ui.ui_manager import GwBCScenarioManagerUi
from ....lib import tools_qgis, tools_qt
from ...utils import tools_gw
from .... import global_vars


class GwBCScenarioManagerButton(GwAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.dlg = None

    def clicked_event(self):
        self.manage_bc_scenario()

    def manage_bc_scenario(self):

        self.dlg = GwBCScenarioManagerUi()

        # Variables
        tbl_bcs = self.dlg.tbl_bcs

        # Populate
        self._fill_manager_table(tbl_bcs, 'cat_bscenario')

        # Signals

        tools_gw.open_dialog(self.dlg, dlg_name="bc_scenario_manager")

    def _fill_manager_table(self, widget, table_name, set_edit_triggers=QTableView.NoEditTriggers, expr=None):
        """ Fills manager table """

        # Set model
        model = QSqlTableModel(db=global_vars.db_qsql_data)
        model.setTable(table_name)
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        model.setSort(0, 0)
        model.select()

        # Check for errors
        if model.lastError().isValid():
            tools_qgis.show_warning(model.lastError().text(), dialog=self.dlg)
        # Attach model to table view
        if expr:
            widget.setModel(model)
            widget.model().setFilter(expr)
        else:
            widget.setModel(model)
        widget.setSortingEnabled(True)

        # Set widget & model properties
        tools_qt.set_tableview_config(widget, selection=QAbstractItemView.SelectRows, edit_triggers=set_edit_triggers,
                                      sectionResizeMode=2, stretchLastSection=True)

        # Sort the table by feature id
        model.sort(1, 0)
