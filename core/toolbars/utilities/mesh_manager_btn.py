from functools import partial
from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QAbstractItemView, QTableView, QFileDialog
from qgis.PyQt.QtSql import QSqlTableModel
from qgis.utils import iface

from ..dialog import DrAction
from ...ui.ui_manager import DrMeshManagerUi, DrLineeditUi
from .createmesh_btn import DrCreateMeshButton
from ...threads.create_temp_layer import DrCreateTempMeshLayerTask
from ....lib import tools_qgis, tools_qt, tools_db
from ...utils import tools_dr, mesh_parser
from .... import global_vars
from ....lib.tools_gpkgdao import DrGpkgDao
from typing import Optional


class DrMeshManagerButton(DrAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.tablename = 'cat_file'
        self.tablename_value = 'boundary_conditions'
        self.dlg_manager = None
        self.dlg_bc = None
        self.dlg_ms = None
        self.last_mesh = None
        self.dao: Optional[DrGpkgDao] = None

    def clicked_event(self):
        self.manage_meshes()

    def manage_meshes(self):

        self.dlg_manager = DrMeshManagerUi()

        # Variables
        tbl_mesh_mng = self.dlg_manager.tbl_mesh_mng
        txt_filter = self.dlg_manager.txt_filter
        btn_create_mesh = self.dlg_manager.btn_create
        btn_view_mesh = self.dlg_manager.btn_view
        btn_import_mesh = self.dlg_manager.btn_import
        btn_delete_mesh = self.dlg_manager.btn_delete
        btn_cancel = self.dlg_manager.btn_cancel

        # Populate
        self._fill_manager_table(tbl_mesh_mng, 'v_ui_file') #, expr="file_name = 'Iber2D.dat'")

        self._set_active_mesh_label()

        btn_import_mesh.setToolTip("Import mesh from folder")

        # Signals
        txt_filter.textChanged.connect(partial(self._filter_table))
        btn_create_mesh.clicked.connect(partial(self._create_mesh))
        btn_view_mesh.clicked.connect(partial(self._view_mesh))
        btn_import_mesh.clicked.connect(partial(self._import_mesh))
        btn_delete_mesh.clicked.connect(partial(self._delete_mesh))
        tbl_mesh_mng.doubleClicked.connect(partial(self._view_mesh))
        btn_cancel.clicked.connect(partial(tools_dr.close_dialog, self.dlg_manager))

        tools_dr.open_dialog(self.dlg_manager, dlg_name="dlg_mesh_manager")

    def _set_active_mesh_label(self):

        # Populate active mesh label
        if tools_qgis.get_layer_by_layername("Mesh Temp Layer") and self.last_mesh:
            self.dlg_manager.lbl_active_mesh.setText(f"Active mesh: {self.last_mesh}")

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
                                      sectionResizeMode=2, stretchLastSection=False)
        widget.horizontalHeader().setSectionResizeMode(0, 1)

        # Sort the table by name
        model.sort(0, 0)

    def _reload_manager_table(self):
        try:
            self.dlg_manager.tbl_mesh_mng.model().select()
        except:
            pass

    def _filter_table(self, text):
        """ Filters manager table by id """

        widget_table = self.dlg_manager.tbl_mesh_mng
        id_field = 'name'

        if text is None:
            text = tools_qt.get_text(self.dlg_manager, self.dlg_manager.txt_filter, return_string_null=False)

        expr = f"CAST({id_field} AS TEXT) LIKE '%{text}%'"
        # Refresh model with selected filter
        widget_table.model().setFilter(expr)
        widget_table.model().select()

    def _create_mesh(self):
        self.create_mesh = DrCreateMeshButton('', None, None, None, None)
        self.create_mesh.clicked_event()
        self.create_mesh.dlg_mesh.finished.connect(self._reload_manager_table)

    def _view_mesh(self):
        # Variables
        table = self.dlg_manager.tbl_mesh_mng

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) != 1:
            msg = "Select only one mesh to display"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
            return

        # Get selected object IDs
        col = 'idval'
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        idx = selected_list[0]
        value = idx.sibling(idx.row(), col_idx).data()

        # Load data from GPKG
        sql = f"SELECT name, iber2d, roof, losses FROM cat_file WHERE name = '{value}'"
        row = tools_db.get_row(sql)

        if not row:
            return

        mesh = mesh_parser.loads(row["iber2d"], row["roof"], row["losses"])
        self.last_mesh = value

        self.thread = DrCreateTempMeshLayerTask("Create Temp Mesh Layer", mesh)
        self.thread.taskCompleted.connect(self._load_layer)
        QgsApplication.taskManager().addTask(self.thread)

    def _load_layer(self):
        """Add temp layer to TOC"""

        # Remove layer if already exists
        layer_name = self.thread.layer.name()
        tools_qgis.remove_layer_from_toc(layer_name, group_name="DRAIN TEMPORAL")

        # Add layer to TOC
        tools_qt.add_layer_to_toc(self.thread.layer, group="DRAIN TEMPORAL")
        iface.setActiveLayer(self.thread.layer)
        iface.zoomToActiveLayer()

        self._set_active_mesh_label()

    def _import_mesh(self):

        self.dao = global_vars.gpkg_dao_data.clone()
        project_folder = str(Path(self.dao.db_filepath).parent)
        folder_path = QFileDialog.getExistingDirectory(
            caption="Select folder",
            directory=project_folder,
        )

        if not folder_path:
            return

        MESH_FILE = "Iber2D.dat"
        mesh_path = Path(folder_path) / MESH_FILE
        ROOF_FILE = "Iber_SWMM_roof.dat"
        roof_path = Path(folder_path) / ROOF_FILE
        LOSSES_FILE = "Iber_Losses.dat"
        losses_path = Path(folder_path) / LOSSES_FILE

        if not mesh_path.exists():
            msg = "File {0} not found in this folder."
            msg_params = ("Iber2D.dat",)
            tools_qt.show_info_box(msg, msg_params=msg_params)
            return

        detected_files = [path.name for path in [mesh_path, roof_path, losses_path] if path.exists()]
        detected_files = ', '.join(detected_files)

        self.dlg_lineedit = DrLineeditUi()
        msg = "Choose a name for the mesh"
        tools_qt.set_widget_text(self.dlg_lineedit, 'lbl_title', msg)

        msg = "Detected files: {0}"
        msg_params = (detected_files,)
        tools_qt.set_widget_text(self.dlg_lineedit, 'lbl_subtitle', msg, msg_params=msg_params)

        self.dlg_lineedit.btn_accept.clicked.connect(partial(self._insert_mesh, mesh_path, roof_path, losses_path))
        self.dlg_lineedit.btn_cancel.clicked.connect(partial(tools_dr.close_dialog, self.dlg_lineedit))
        tools_dr.open_dialog(self.dlg_lineedit)

    def _insert_mesh(self, mesh_path, roof_path, losses_path):
        mesh_name = tools_qt.get_text(self.dlg_lineedit, 'txt_input')

        columns = "name, iber2d"
        values = f"'{mesh_name}'"
        with open(mesh_path) as f:
            content = f.read()
            values += f", '{content}'"

        if roof_path.exists():
            columns += ", roof"
            with open(roof_path) as f:
                content = f.read()
                values += f", '{content}'"

        columns += ", losses"
        if losses_path.exists():
            with open(losses_path) as f:
                content = f.read()
                values += f", '{content}'"
        else:
            values += ", '0'"

        sql = f"INSERT INTO cat_file ({columns}) VALUES ({values});"
        status = self.dao.execute_sql(sql)
        if status:
            msg = "Mesh successfully imported"
            tools_qgis.show_info(msg, dialog=self.dlg_manager)
        self.dao.close_db()

        self._reload_manager_table()
        tools_dr.close_dialog(self.dlg_lineedit)

    def _delete_mesh(self):
        # Variables
        table = self.dlg_manager.tbl_mesh_mng

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            msg = "Any record selected"
            tools_qgis.show_warning(msg, dialog=self.dlg_manager)
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

        msg = "Are you sure you want to delete these records?"
        title = "Delete records"
        answer = tools_qt.show_question(msg, title, id_list)
        if answer:
            for value in id_list:
                values.append(f"'{value}'")

            # Delete object from main table
            for value in values:
                id_field = 'name'
                sql = f"DELETE FROM {self.tablename} WHERE {id_field} = {value}"
                print(sql)
                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error deleting object."
                    tools_qgis.show_warning(msg, dialog=self.dlg_manager)
                    global_vars.gpkg_dao_data.rollback()
                    return

            # Commit & refresh table
            self.dao = global_vars.gpkg_dao_data
            if self.dao:
                self.dao.commit()
                sql = "vacuum;"
                self.dao.execute_sql(sql)
            self._reload_manager_table()
