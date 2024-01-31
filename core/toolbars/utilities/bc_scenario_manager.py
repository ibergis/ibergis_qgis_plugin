import datetime
from functools import partial
from time import time

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QAbstractItemView, QTableView
from qgis.PyQt.QtSql import QSqlTableModel

from ..dialog import DrAction
from ...ui.ui_manager import DrBCScenarioManagerUi, DrBCScenarioUi, DrMeshSelectorUi
from ....lib import tools_qgis, tools_qt, tools_db
from ...threads.savetomesh import DrSaveToMeshTask
from ...utils import Feedback, tools_gw, mesh_parser
from .... import global_vars


def set_bc_filter():

    sql = f"""SELECT idval FROM cat_bscenario WHERE active = 1"""
    row = tools_db.get_row(sql)
    if not row:
        msg = "No current bcscenario found"
        tools_qgis.show_warning(msg)
        return
    cur_scenario = row['idval']

    layer_name = 'boundary_conditions'
    bc_layer = tools_qgis.get_layer_by_tablename(layer_name)
    if bc_layer is None:
        msg = f"Layer {layer_name} not found."
        tools_qgis.show_warning(msg)
        return
    bc_layer.setSubsetString(f"bscenario = '{cur_scenario}'")


class DrBCScenarioManagerButton(DrAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.tablename = 'cat_bscenario'
        self.tablename_value = 'boundary_conditions'
        self.dlg_manager = None
        self.dlg_bc = None
        self.dlg_ms = None

    def clicked_event(self):
        self.manage_bc_scenario()

    def manage_bc_scenario(self):

        self.dlg_manager = DrBCScenarioManagerUi()

        # Variables
        tbl_bcs = self.dlg_manager.tbl_bcs
        txt_filter = self.dlg_manager.txt_filter
        btn_save_to_mesh = self.dlg_manager.btn_save_to_mesh
        btn_set_current_scenario = self.dlg_manager.btn_set_current_scenario
        btn_create_scenario = self.dlg_manager.btn_create_scenario
        btn_duplicate_scenario = self.dlg_manager.btn_duplicate_scenario
        btn_edit_scenario = self.dlg_manager.btn_edit_scenario
        btn_delete_scenario = self.dlg_manager.btn_delete_scenario
        btn_cancel = self.dlg_manager.btn_cancel

        # Populate
        self._fill_manager_table(tbl_bcs, 'cat_bscenario')
        self._set_lbl_current_scenario()

        # Signals
        txt_filter.textChanged.connect(partial(self._filter_table))
        btn_save_to_mesh.clicked.connect(partial(self._save_to_mesh))
        btn_set_current_scenario.clicked.connect(partial(self._set_current_scenario))
        btn_create_scenario.clicked.connect(partial(self._create_scenario))
        btn_duplicate_scenario.clicked.connect(partial(self._duplicate_scenario))
        btn_edit_scenario.clicked.connect(partial(self._edit_scenario))
        btn_delete_scenario.clicked.connect(partial(self._delete_scenario))
        tbl_bcs.doubleClicked.connect(partial(self._edit_scenario))
        btn_cancel.clicked.connect(partial(tools_gw.close_dialog, self.dlg_manager))

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

        # Hide id and active columns
        widget.setColumnHidden(0, True)
        widget.setColumnHidden(4, True)

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

    def _filter_table(self, text):
        """ Filters manager table by id """

        widget_table = self.dlg_manager.tbl_bcs
        id_field = 'idval'

        if text is None:
            text = tools_qt.get_text(self.dlg_manager, self.dlg_manager.txt_filter, return_string_null=False)

        expr = f"CAST({id_field} AS TEXT) LIKE '%{text}%'"
        # Refresh model with selected filter
        widget_table.model().setFilter(expr)
        widget_table.model().select()

    # region Buttons

    def _save_to_mesh(self):
        # Variables
        table = self.dlg_manager.tbl_bcs
        dao = global_vars.gpkg_dao_data.clone()

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) != 1:
            message = "Select only one scenario to save to mesh"
            tools_qgis.show_warning(message, dialog=self.dlg_manager)
            return
        
        # Get selected object IDs
        col = 'idval'
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        idval = selected_list[0].sibling(selected_list[0].row(), col_idx).data()
        
        # TODO: Check for empty scenarios

        sql = "SELECT name FROM cat_file"
        rows = dao.get_rows(sql)
        if not rows:
            message = (
                "No meshes found in GPKG file. Create a mesh with "
                "Create Mesh button before saving the boundary conditions to it."
            )
            tools_qgis.show_warning(message, dialog=self.dlg_manager)
            return

        self.dlg_ms = DrMeshSelectorUi()
        dlg = self.dlg_ms
        tools_gw.load_settings(dlg)
        tools_gw.disable_tab_log(dlg)
        dlg.btn_cancel.clicked.connect(partial(tools_gw.close_dialog, dlg))
        dlg.btn_ok.clicked.connect(partial(self._accept_save_to_mesh, idval))
        set_ok_enabled = lambda x: dlg.btn_ok.setEnabled(bool(x))
        dlg.cmb_mesh.currentTextChanged.connect(set_ok_enabled)

        mesh_names = [row[0] for row in rows]
        tools_qt.fill_combo_box_list(None, dlg.cmb_mesh, mesh_names)
        
        tools_gw.open_dialog(dlg)

    def _set_current_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs

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
        sql = f"""UPDATE {self.tablename} SET active = 0"""
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error setting the scenario as active"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
            return

        # Set current scenario as active
        sql = f"""UPDATE {self.tablename} SET active = 1 WHERE {col} = '{idval}'"""
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error setting the scenario as active"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
            return
        self._set_lbl_current_scenario(idval)
        self._reload_manager_table()
        set_bc_filter()

    def _create_scenario(self):
        # Create dialog
        self.dlg_bc = DrBCScenarioUi()

        tools_qt.set_widget_visible(self.dlg_bc, 'lbl_id', False)
        tools_qt.set_widget_visible(self.dlg_bc, 'txt_id', False)

        # Signals
        self.dlg_bc.btn_accept.clicked.connect(partial(self._accept_create_scenario))

        # Open dialog
        tools_gw.open_dialog(self.dlg_bc, dlg_name="bc_scenario")

    def _duplicate_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs

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

        sql = f"""SELECT idval FROM {self.tablename} WHERE {col} = '{idval}'"""
        row = tools_db.get_row(sql)
        if not row:
            msg = f"There was an error getting the scenario information"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return

        # Get scenario values
        idval = row['idval']

        # Create dialog
        self.dlg_bc = DrBCScenarioUi()

        # Populate widgets
        tools_qt.set_widget_text(self.dlg_bc, 'txt_idval', f"{idval}_copy")

        # Signals
        self.dlg_bc.btn_accept.clicked.connect(partial(self._accept_duplicate_scenario, idval))

        # Open dialog
        tools_gw.open_dialog(self.dlg_bc, dlg_name="bc_scenario")

    def _edit_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs

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

        sql = f"""SELECT id, idval, name, descript FROM {self.tablename} WHERE {col} = '{idval}'"""
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
        self.dlg_bc = DrBCScenarioUi()

        # Populate widgets
        tools_qt.set_widget_text(self.dlg_bc, 'txt_id', _id)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_idval', idval)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_name', name)
        tools_qt.set_widget_text(self.dlg_bc, 'txt_descript', descript)

        tools_qt.set_widget_visible(self.dlg_bc, 'lbl_id', False)
        tools_qt.set_widget_visible(self.dlg_bc, 'txt_id', False)

        # Signals
        self.dlg_bc.btn_accept.clicked.connect(partial(self._accept_edit_scenario))

        # Open dialog
        tools_gw.open_dialog(self.dlg_bc, dlg_name="bc_scenario")

    def _delete_scenario(self):
        # Variables
        table = self.dlg_manager.tbl_bcs

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
                    sql = f"DELETE FROM {self.tablename_value} WHERE {id_field} = {value}"
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
                sql = f"DELETE FROM {self.tablename} WHERE {id_field} = {value}"
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

    def _set_lbl_current_scenario(self, idval=None):
        # Get current scenario if not provided
        if idval is None:
            sql = f"""SELECT idval FROM {self.tablename} WHERE active = 1"""
            row = tools_db.get_row(sql)
            if not row:
                msg = "No current scenario found."
                tools_qgis.show_warning(msg, dialog=self.dlg_manager)
                return
            idval = row['idval']

        # Set lbl_current_scenario text
        lbl_current_scenario = self.dlg_manager.lbl_current_scenario
        tools_qt.set_widget_text(self.dlg_manager, lbl_current_scenario, idval)

    def _accept_create_scenario(self):
        txt_idval = self.dlg_bc.txt_idval
        txt_name = self.dlg_bc.txt_name
        txt_descript = self.dlg_bc.txt_descript

        idval = tools_qt.get_text(self.dlg_bc, txt_idval, add_quote=True)
        name = tools_qt.get_text(self.dlg_bc, txt_name, add_quote=True)
        descript = tools_qt.get_text(self.dlg_bc, txt_descript, add_quote=True)

        if not idval or idval == "null":
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")

        sql = f"""INSERT INTO {self.tablename} (idval, name, descript, active) VALUES ({idval}, {name}, {descript}, 0)"""
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

        _id = tools_qt.get_text(self.dlg_bc, txt_id, add_quote=True)
        idval = tools_qt.get_text(self.dlg_bc, txt_idval, add_quote=True)
        name = tools_qt.get_text(self.dlg_bc, txt_name, add_quote=True)
        descript = tools_qt.get_text(self.dlg_bc, txt_descript, add_quote=True)

        if not idval or idval == "null":
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")

        sql = f"""UPDATE {self.tablename} SET idval = {idval}, name = {name}, descript = {descript} WHERE id = {_id}"""
        print(sql)
        status = tools_db.execute_sql(sql)
        if status is False:
            msg = f"There was an error updating the scenario"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return
        tools_gw.close_dialog(self.dlg_bc)
        self._reload_manager_table()

    def _accept_duplicate_scenario(self, code_from):
        txt_idval = self.dlg_bc.txt_idval
        txt_name = self.dlg_bc.txt_name
        txt_descript = self.dlg_bc.txt_descript

        idval = tools_qt.get_text(self.dlg_bc, txt_idval, add_quote=True)
        name = tools_qt.get_text(self.dlg_bc, txt_name, add_quote=True)
        descript = tools_qt.get_text(self.dlg_bc, txt_descript, add_quote=True)

        if not idval or idval == "null":
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")

        sql = f"""INSERT INTO {self.tablename} (idval, name, descript, active) VALUES ({idval}, {name}, {descript}, 0)"""
        status = tools_db.execute_sql(sql, commit=False)
        if status is False:
            msg = f"There was an error inserting the scenario"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            return

        sql = f"""INSERT INTO {self.tablename_value} (code, descript, tin_id, edge_id, boundary_type, geom) 
            SELECT {idval}, descript, tin_id, edge_id, boundary_type, geom FROM {self.tablename_value} WHERE code = '{code_from}' """
        status = tools_db.execute_sql(sql, commit=False)
        if status is False:
            msg = f"There was an error inserting the scenario geometries"
            tools_qgis.show_warning(msg, dialog=self.dlg_bc)
            global_vars.gpkg_dao_data.rollback()
            return

        global_vars.gpkg_dao_data.commit()
        tools_gw.close_dialog(self.dlg_bc)
        self._reload_manager_table()

    def _accept_save_to_mesh(self, bcscenario):
        mesh_name = self.dlg_ms.cmb_mesh.currentText()
        dao = global_vars.gpkg_dao_data

        sql = f"SELECT iber2d, roof, losses FROM cat_file WHERE name = '{mesh_name}'"
        row = dao.get_row(sql)
        mesh_str = row["iber2d"]
        roof_str = None if row["roof"] is None else row["roof"]
        losses_str = None if row["losses"] is None else row["losses"]

        # Parse mesh and check for preexistent boundary conditions
        mesh = mesh_parser.loads(mesh_str, roof_str, losses_str)

        if mesh["boundary_conditions"]:
            message = "This process will override the boundary conditions of this mesh. Are you sure?"
            answer = tools_qt.show_question(message, "Override boundary conditions")
            if not answer:
                return

        self.feedback = Feedback()
        self.thread_savetomesh = DrSaveToMeshTask(
            "Save to mesh",
            bcscenario,
            mesh_name,
            mesh,
            feedback=self.feedback,
        )
        thread = self.thread_savetomesh

        # Set signals
        self.dlg_ms.btn_ok.setEnabled(False)
        self.dlg_ms.btn_cancel.clicked.disconnect()
        self.dlg_ms.btn_cancel.clicked.connect(thread.cancel)
        self.dlg_ms.btn_cancel.clicked.connect(partial(self.dlg_ms.btn_cancel.setText, "Canceling..."))
        thread.taskCompleted.connect(self._on_s2m_completed)
        thread.taskTerminated.connect(self._on_s2m_terminated)
        thread.feedback.progressText.connect(self._set_progress_text)
        thread.feedback.progressChanged.connect(self.dlg_ms.progress_bar.setValue)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        self.dlg_ms.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(thread)

    def _on_s2m_completed(self):
        self._on_s2m_end()
        dlg = self.dlg_ms
        dlg.meshes_saved = False

    def _on_s2m_end(self):
        thread = self.thread_savetomesh
        message = "Task canceled." if thread.isCanceled() else thread.message
        tools_gw.fill_tab_log(
            self.dlg_ms,
            {"info": {"values": [{"message": message}]}},
            reset_text=False,
        )
        sb = self.dlg_ms.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

        self.timer.stop()

        dlg = self.dlg_ms
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(dlg.reject)

    def _on_s2m_terminated(self):
        self._on_s2m_end()

    def _on_timer_timeout(self):
        # Update timer
        elapsed_time = time() - self.t0
        text = str(datetime.timedelta(seconds=round(elapsed_time)))
        self.dlg_ms.lbl_timer.setText(text)

    def _set_progress_text(self, txt):
        tools_gw.fill_tab_log(
            self.dlg_ms,
            {"info": {"values": [{"message": txt}]}},
            reset_text=False,
            close=False,
        )
        sb = self.dlg_ms.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    # endregion
