import datetime
from functools import partial
from pathlib import Path
from time import time

from qgis.core import QgsApplication, QgsMapLayer, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QListWidgetItem, QComboBox

from ..dialog import DrAction
from ...threads.createmesh import DrCreateMeshTask
from ...threads.validatemesh import validations_dict
from ...ui.ui_manager import DrCreateMeshUi
from ...utils import Feedback, tools_dr, mesh_parser
from .... import global_vars
from ....lib import tools_qt, tools_os


class DrCreateMeshButton(DrAction):
    """Button 36: CreateMesh"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dao = global_vars.gpkg_dao_data.clone()
        self.dlg_mesh = DrCreateMeshUi()
        dlg = self.dlg_mesh
        self.validations = validations_dict()

        self.ground_layer = self._get_layer(self.dao, "ground")
        self.roof_layer = self._get_layer(self.dao, "roof")

        # Set widgets
        tools_dr.load_settings(dlg)
        tools_dr.disable_tab_log(dlg)
        tools_qt.double_validator(dlg.txt_tolerance)
        tools_qt.double_validator(dlg.txt_slope)
        tools_qt.double_validator(dlg.txt_start)
        tools_qt.double_validator(dlg.txt_extent)

        # Fill raster layers combos
        project = QgsProject.instance()
        all_layers = project.mapLayers().values()
        raster_layers = [
            [layer, layer.name()]
            for layer in all_layers
            if layer.type() == QgsMapLayer.RasterLayer and layer.bandCount() == 1
        ]
        # DEM
        rows = [[None, "Fill elevation with zeroes"], *raster_layers]
        tools_qt.fill_combo_values(dlg.cmb_dem_layer, rows, add_empty=False)
        # Roughness
        rows = [
            [None, "Fill roughness with zeroes"],
            ["ground_layer", "Ground"],
            *raster_layers,
        ]
        tools_qt.fill_combo_values(dlg.cmb_roughness_layer, rows, add_empty=False)
        # Roughness
        rows = [
            [None, "Fill losses with zeroes"],
            ["ground_layer", "Ground"],
            *raster_layers,
        ]
        tools_qt.fill_combo_values(dlg.cmb_losses_layer, rows, add_empty=False)

        # Load user's last values
        self._load_widget_values()

        # Set initial signals
        dlg.chk_validation.clicked.connect(dlg.btn_config.setEnabled)
        dlg.btn_config.clicked.connect(partial(dlg.stackedWidget.setCurrentIndex, 1))
        dlg.btn_back.clicked.connect(partial(dlg.stackedWidget.setCurrentIndex, 0))
        dlg.btn_select_all.clicked.connect(self._listval_select_all)
        dlg.btn_clear_selection.clicked.connect(self._listval_clear_selection)
        dlg.btn_toggle_selection.clicked.connect(self._listval_toggle_selection)
        dlg.btn_valid_ok.clicked.connect(partial(dlg.stackedWidget.setCurrentIndex, 0))
        dlg.chk_clean_geometries.stateChanged.connect(dlg.txt_tolerance.setEnabled)
        dlg.chk_transition.stateChanged.connect(dlg.txt_slope.setEnabled)
        dlg.chk_transition.stateChanged.connect(dlg.txt_start.setEnabled)
        dlg.chk_transition.stateChanged.connect(dlg.txt_extent.setEnabled)
        dlg.btn_ok.clicked.connect(self._execute_process)
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.rejected.connect(self._save_widget_values)
        dlg.rejected.connect(partial(tools_dr.close_dialog, dlg))

        # Create List Items
        flags = Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        for validation in self.validations.values():
            validation["list_item"] = QListWidgetItem(validation["name"])
            validation["list_item"].setFlags(flags)
            validation["list_item"].setCheckState(Qt.Checked)

        # Add items to list, in categories
        categories = {
            "ground": "Ground Layer Checks:",
            "roof": "Roof Layer Checks:",
            None: "Other Checks:",
        }
        for category, label in categories.items():
            item = QListWidgetItem(label)
            item.setFlags(Qt.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            dlg.list_validations.addItem(item)
            for validation in self.validations.values():
                if validation["layer"] == category:
                    dlg.list_validations.addItem(validation["list_item"])

        tools_dr.open_dialog(dlg, dlg_name="create_mesh")

    def _execute_process(self):
        dlg = self.dlg_mesh

        # Get and validate inputs
        execute_validations = []
        if dlg.chk_validation.isChecked():
            execute_validations = [
                validation_id
                for validation_id, validation in self.validations.items()
                if validation["list_item"].checkState() == Qt.Checked
            ]
        clean_geometries = dlg.chk_clean_geometries.isChecked()
        clean_tolerance = float(dlg.txt_tolerance.text())
        enable_transition = dlg.chk_transition.isChecked()
        transition_slope = float(dlg.txt_slope.text())
        transition_start = float(dlg.txt_start.text())
        transition_extent = float(dlg.txt_extent.text())
        dem_layer = tools_qt.get_combo_value(dlg, dlg.cmb_dem_layer)
        if dem_layer == "":
            tools_qt.show_info_box("Please, select a DEM layer!")
            return
        roughness_layer = tools_qt.get_combo_value(dlg, dlg.cmb_roughness_layer)
        if roughness_layer == "":
            tools_qt.show_info_box("Please, select a roughness layer!")
            return
        losses_layer = tools_qt.get_combo_value(dlg, dlg.cmb_losses_layer)
        if losses_layer == "":
            tools_qt.show_info_box("Please, select a losses layer!")
            return
        mesh_name = dlg.txt_name.text()

        if mesh_name == "":
            tools_qt.show_info_box("Please, fill the name of the mesh.")
            return

        if not mesh_name.isalnum() and "-" not in mesh_name:
            tools_qt.show_info_box(
                "Only alphanumeric characters and hyphens are valid for the mesh name."
            )
            return

        # Check for existent meshes in file
        sql = "SELECT group_concat(name) as names FROM cat_file"
        retrieved_meshes = self.dao.get_row(sql)["names"]
        if retrieved_meshes is not None and mesh_name in retrieved_meshes.split(","):
            message = (
                "A mesh with the same name already exists. Do you want to overwrite it?"
            )
            if not tools_qt.show_question(message):
                return

        # Reset txt_infolog
        tools_qt.set_widget_text(dlg, 'txt_infolog', "")

        self.feedback = Feedback()
        self.thread_triangulation = DrCreateMeshTask(
            "Triangulation",
            execute_validations,
            clean_geometries,
            clean_tolerance,
            enable_transition,
            transition_slope,
            transition_start,
            transition_extent,
            dem_layer,
            roughness_layer,
            losses_layer,
            mesh_name,
            feedback=self.feedback,
        )
        thread = self.thread_triangulation

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(thread.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        thread.taskCompleted.connect(self._on_task_completed)
        thread.taskTerminated.connect(self._on_task_terminated)
        thread.feedback.progressText.connect(self._set_progress_text)
        # thread.feedback.progressChanged.connect(dlg.progress_bar.setValue)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(thread)

    def _load_widget_values(self):
        dlg = self.dlg_mesh
        # chk_validation
        chk_validation = tools_dr.get_config_parser('dlg_create_mesh', 'chk_validation', "user", "session")
        if chk_validation not in (None, 'null'):
            tools_qt.set_checked(dlg, 'chk_validation', chk_validation)
            dlg.btn_config.setEnabled(tools_os.set_boolean(chk_validation))

        # chk_transition
        chk_transition = tools_dr.get_config_parser('dlg_create_mesh', 'chk_transition', "user", "session")
        if chk_transition not in (None, 'null'):
            tools_qt.set_checked(dlg, 'chk_transition', chk_transition)
        # txt_slope
        txt_slope = tools_dr.get_config_parser('dlg_create_mesh', 'txt_slope', "user", "session")
        if txt_slope not in (None, 'null'):
            tools_qt.set_widget_text(dlg, 'txt_slope', txt_slope)
        # txt_start
        txt_start = tools_dr.get_config_parser('dlg_create_mesh', 'txt_start', "user", "session")
        if txt_start not in (None, 'null'):
            tools_qt.set_widget_text(dlg, 'txt_start', txt_start)
        # txt_extent
        txt_extent = tools_dr.get_config_parser('dlg_create_mesh', 'txt_extent', "user", "session")
        if txt_extent not in (None, 'null'):
            tools_qt.set_widget_text(dlg, 'txt_extent', txt_extent)

        # cmb_dem_layer
        cmb_dem_layer = tools_dr.get_config_parser('dlg_create_mesh', 'cmb_dem_layer', "user", "session")
        if cmb_dem_layer not in (None, 'null'):
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_dem_layer'), cmb_dem_layer, 1, add_new=False)
        else:
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_dem_layer'), "Fill elevation with zeroes", 1, add_new=False)
        # cmb_roughness_layer
        cmb_roughness_layer = tools_dr.get_config_parser('dlg_create_mesh', 'cmb_roughness_layer', "user", "session")
        if cmb_roughness_layer not in (None, 'null'):
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_roughness_layer'), cmb_roughness_layer, 1, add_new=False)
        else:
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_roughness_layer'), "Ground", 1, add_new=False)
        # cmb_losses_layer
        cmb_losses_layer = tools_dr.get_config_parser('dlg_create_mesh', 'cmb_losses_layer', "user", "session")
        if cmb_losses_layer not in (None, 'null'):
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_losses_layer'), cmb_losses_layer, 1, add_new=False)
        else:
            tools_qt.set_combo_value(dlg.findChild(QComboBox, 'cmb_losses_layer'), "Ground", 1, add_new=False)

        # txt_name
        txt_name = tools_dr.get_config_parser('dlg_create_mesh', 'txt_name', "user", "session")
        if txt_name not in (None, 'null'):
            tools_qt.set_widget_text(dlg, 'txt_name', txt_name)

    def _save_widget_values(self):
        dlg = self.dlg_mesh
        # chk_validation
        chk_validation = tools_qt.is_checked(dlg, 'chk_validation')
        tools_dr.set_config_parser('dlg_create_mesh', 'chk_validation', chk_validation, "user", "session")

        # chk_transition
        chk_transition = tools_qt.is_checked(dlg, 'chk_transition')
        tools_dr.set_config_parser('dlg_create_mesh', 'chk_transition', chk_transition, "user", "session")
        # txt_slope
        txt_slope = tools_qt.get_text(dlg, 'txt_slope')
        tools_dr.set_config_parser('dlg_create_mesh', 'txt_slope', txt_slope, "user", "session")
        # txt_start
        txt_start = tools_qt.get_text(dlg, 'txt_start')
        tools_dr.set_config_parser('dlg_create_mesh', 'txt_start', txt_start, "user", "session")
        # txt_extent
        txt_extent = tools_qt.get_text(dlg, 'txt_extent')
        tools_dr.set_config_parser('dlg_create_mesh', 'txt_extent', txt_extent, "user", "session")

        # cmb_dem_layer
        cmb_dem_layer = tools_qt.get_combo_value(dlg, 'cmb_dem_layer', 1)
        tools_dr.set_config_parser('dlg_create_mesh', 'cmb_dem_layer', cmb_dem_layer, "user", "session")
        # cmb_roughness_layer
        cmb_roughness_layer = tools_qt.get_combo_value(dlg, 'cmb_roughness_layer', 1)
        tools_dr.set_config_parser('dlg_create_mesh', 'cmb_roughness_layer', cmb_roughness_layer, "user", "session")
        # cmb_losses_layer
        cmb_losses_layer = tools_qt.get_combo_value(dlg, 'cmb_losses_layer', 1)
        tools_dr.set_config_parser('dlg_create_mesh', 'cmb_losses_layer', cmb_losses_layer, "user", "session")

        # txt_name
        txt_name = tools_qt.get_text(dlg, 'txt_name')
        tools_dr.set_config_parser('dlg_create_mesh', 'txt_name', txt_name, "user", "session")

    def _get_layer(self, dao, layer_name):
        path = f"{dao.db_filepath}|layername={layer_name}"
        return QgsVectorLayer(path, layer_name, "ogr")

    def _on_task_completed(self):
        self._on_task_end()
        dlg = self.dlg_mesh
        dlg.meshes_saved = False

    def _on_task_end(self):
        thread = self.thread_triangulation
        message = "Task canceled." if thread.isCanceled() else thread.message
        tools_dr.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": message}]}},
            reset_text=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

        self.timer.stop()

        # Add errors to TOC
        if thread.error_layers or thread.warning_layers:
            group_name = "Mesh inputs errors & warnings"
            for layer in thread.error_layers:
                tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
            for layer in thread.warning_layers:
                tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
            QgsProject.instance().layerTreeRoot().removeChildrenGroupWithoutLayers()
            self.iface.layerTreeView().model().sourceModel().modelReset.emit()

        dlg = self.dlg_mesh
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(dlg.reject)
        dlg.mainTab.setTabEnabled(0, True)
        dlg.btn_ok.setEnabled(True)

    def _on_task_terminated(self):
        self._on_task_end()

    def _on_timer_timeout(self):
        # Update timer
        elapsed_time = time() - self.t0
        text = str(datetime.timedelta(seconds=round(elapsed_time)))
        self.dlg_mesh.lbl_timer.setText(text)

    def _set_progress_text(self, txt):
        tools_dr.fill_tab_log(
            self.dlg_mesh,
            {"info": {"values": [{"message": txt}]}},
            reset_text=False,
            close=False,
        )
        sb = self.dlg_mesh.txt_infolog.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _listval_clear_selection(self):
        for validation in self.validations.values():
            validation["list_item"].setCheckState(Qt.Unchecked)

    def _listval_select_all(self):
        for validation in self.validations.values():
            validation["list_item"].setCheckState(Qt.Checked)

    def _listval_toggle_selection(self):
        for validation in self.validations.values():
            if validation["list_item"].checkState() == Qt.Unchecked:
                validation["list_item"].setCheckState(Qt.Checked)
            else:
                validation["list_item"].setCheckState(Qt.Unchecked)
