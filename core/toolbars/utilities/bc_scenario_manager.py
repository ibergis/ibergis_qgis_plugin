from functools import partial

from qgis.PyQt.QtWidgets import QAbstractItemView, QTableView, QLineEdit, QComboBox
from qgis.PyQt.QtSql import QSqlTableModel

from ..dialog import GwAction
from ...ui.ui_manager import GwBCScenarioManagerUi, GwBCScenarioUi
from ....lib import tools_qgis, tools_qt, tools_db
from ...utils import tools_gw
from .... import global_vars


class GwBCScenarioManagerButton(GwAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.dlg_manager = None
        self.dlg_bc = None

    def clicked_event(self):
        self.manage_bc_scenario()

    def manage_bc_scenario(self):

        self.dlg_manager = GwBCScenarioManagerUi()

        # Variables
        tbl_bcs = self.dlg_manager.tbl_bcs
        btn_save_to_mesh = self.dlg_manager.btn_save_to_mesh
        btn_set_current_scenario = self.dlg_manager.btn_set_current_scenario
        btn_create_scenario = self.dlg_manager.btn_create_scenario
        btn_duplicate_scenario = self.dlg_manager.btn_duplicate_scenario
        btn_edit_scenario = self.dlg_manager.btn_edit_scenario
        btn_delete_scenario = self.dlg_manager.btn_delete_scenario

        # Populate
        self._fill_manager_table(tbl_bcs, 'cat_bscenario')

        # Signals
        btn_save_to_mesh.clicked.connect(partial(self._save_to_mesh))
        btn_set_current_scenario.clicked.connect(partial(self._set_current_scenario))
        btn_create_scenario.clicked.connect(partial(self._create_scenario))
        btn_duplicate_scenario.clicked.connect(partial(self._duplicate_scenario))
        btn_edit_scenario.clicked.connect(partial(self._edit_scenario))
        btn_delete_scenario.clicked.connect(partial(self._delete_scenario))
        tbl_bcs.doubleClicked.connect(partial(self._edit_scenario))

        tools_gw.open_dialog(self.dlg_manager, dlg_name="bc_scenario_manager")

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
            tools_qgis.show_warning(model.lastError().text(), dialog=self.dlg_manager)
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

    def _reload_manager_table(self):
        try:
            self.dlg_manager.tbl_bcs.model().select()
        except:
            pass

    # region Buttons

    def _save_to_mesh(self):
        pass

    def _set_current_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs
        tablename = 'cat_bscenario'
        tablename_value = 'boundary_conditions'

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            message = "Any record selected"
            tools_qgis.show_warning(message, dialog=self.dlg_manager)
            return

        # Get selected object IDs
        col = 'idval'
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        idval = selected_list[0].sibling(selected_list[0].row(), col_idx).data()

        # Set all scenarios as not active
        sql = f"""UPDATE {tablename} SET active = 0"""
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error setting the scenario as active"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
            return

        # Set current scenario as active
        sql = f"""UPDATE {tablename} SET active = 1 WHERE {col} = '{idval}'"""
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error setting the scenario as active"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
            return
        self._reload_manager_table()

    def _create_scenario(self):
        # Create dialog
        self.dlg_bc = GwBCScenarioUi()

        # Signals
        self.dlg_bc.btn_accept.clicked.connect(partial(self._accept_create_scenario))

        # Open dialog
        tools_gw.open_dialog(self.dlg_bc, dlg_name="bc_scenario")

    def _duplicate_scenario(self):
        pass

    def _edit_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs
        tablename = 'cat_bscenario'
        tablename_value = 'boundary_conditions'

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            message = "Any record selected"
            tools_qgis.show_warning(message, dialog=self.dlg_manager)
            return

        # Get selected object IDs
        col = 'idval'
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        idval = selected_list[0].sibling(selected_list[0].row(), col_idx).data()

        sql = f"""SELECT id, idval, name, descript FROM {tablename} WHERE {col} = '{idval}'"""
        print(sql)
        row = tools_db.get_row(sql)
        if not row:
            msg = f"There was an error getting the scenario information"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return

        # Get scenario values
        _id = row['id']
        idval = row['idval']
        name = row['name']
        descript = row['descript']

        # Create dialog
        self.dlg_bc = GwBCScenarioUi()

        # Populate widgets
        tools_qt.set_widget_text(self.dlg_bc, 'txt_id', _id)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_idval', idval)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_name', name)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_descript', descript)

        # Signals
        self.dlg_bc.btn_accept.clicked.connect(partial(self._accept_edit_scenario))

        # Open dialog
        tools_gw.open_dialog(self.dlg_bc, dlg_name="bc_scenario")

    def _delete_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs
        tablename = 'cat_bscenario'
        tablename_value = 'boundary_conditions'

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            message = "Any record selected"
            tools_qgis.show_warning(message, dialog=self.dlg_manager)
            return

        # Get selected object IDs
        col = 'idval'
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        id_list = []
        values = []
        for idx in selected_list:
            value = idx.sibling(idx.row(), col_idx).data()
            id_list.append(value)

        message = "Are you sure you want to delete these records?"
        answer = tools_qt.show_question(message, "Delete records", id_list)
        if answer:
            for value in id_list:
                values.append(f"'{value}'")

            # Delete values
            id_field = 'code'
            if id_field is not None:
                for value in values:
                    sql = f"DELETE FROM {tablename_value} WHERE {id_field} = {value}"
                    print(sql)
                    result = tools_db.execute_sql(sql, commit=False)
                    if not result:
                        msg = "There was an error deleting object values."
                        tools_qgis.show_warning(msg, dialog=self.dlg_manager)
                        global_vars.gpkg_dao_data.rollback()
                        return

            # Delete object from main table
            for value in values:
                id_field = 'idval'
                sql = f"DELETE FROM {tablename} WHERE {id_field} = {value}"
                print(sql)
                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error deleting object."
                    tools_qgis.show_warning(msg, dialog=self.dlg_manager)
                    global_vars.gpkg_dao_data.rollback()
                    return

            # Commit & refresh table
            global_vars.gpkg_dao_data.commit()
            self._reload_manager_table()

    # endregion

    # region Private functions

    def _accept_create_scenario(self):
        txt_idval = self.dlg_bc.txt_idval
        txt_name = self.dlg_bc.txt_name
        txt_descript = self.dlg_bc.txt_descript

        tablename = "cat_bscenario"

        idval = tools_qt.get_text(self.dlg_bc, txt_idval, add_quote=True)
        name = tools_qt.get_text(self.dlg_bc, txt_name, add_quote=True)
        descript = tools_qt.get_text(self.dlg_bc, txt_descript, add_quote=True)

        if not idval or idval == "null":
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")

        sql = f"""INSERT INTO {tablename} (idval, name, descript, active) VALUES ({idval}, {name}, {descript}, 0)"""
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error inserting the scenario"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return
        tools_gw.close_dialog(self.dlg_bc)
        self._reload_manager_table()

    def _accept_edit_scenario(self):
        txt_id = self.dlg_bc.txt_id
        txt_idval = self.dlg_bc.txt_idval
        txt_name = self.dlg_bc.txt_name
        txt_descript = self.dlg_bc.txt_descript

        tablename = "cat_bscenario"

        _id = tools_qt.get_text(self.dlg_bc, txt_id, add_quote=True)
        idval = tools_qt.get_text(self.dlg_bc, txt_idval, add_quote=True)
        name = tools_qt.get_text(self.dlg_bc, txt_name, add_quote=True)
        descript = tools_qt.get_text(self.dlg_bc, txt_descript, add_quote=True)

        if not idval or idval == "null":
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")

        sql = f"""UPDATE {tablename} SET idval = {idval}, name = {name}, descript = {descript} WHERE id = {_id}"""
        print(sql)
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error updating the scenario"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return
        tools_gw.close_dialog(self.dlg_bc)
        self._reload_manager_table()

    # endregion
