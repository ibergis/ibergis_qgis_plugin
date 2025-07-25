import datetime
import os
from functools import partial
from time import time

from qgis.core import Qgis, QgsApplication, QgsMapLayer, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QListWidgetItem, QComboBox, QTextEdit

from ..dialog import DrAction
from ...threads.createmesh import DrCreateMeshTask
from ...threads.validatemesh import validations_dict
from ...ui.ui_manager import DrCreateMeshUi
from ...utils import Feedback, tools_dr
from ...utils.meshing_process import create_anchor_layers
from .... import global_vars
from ....lib import tools_qt, tools_os, tools_qgis
from qgis.utils import iface


class DrCreateMeshButton(DrAction):
    """Button 36: CreateMesh"""

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.cur_process = None
        self.cur_text = None

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

        # Hide grb_cleanup
        dlg.grb_cleanup_data.setVisible(False)

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
            ["ground_layer", "Column scs_cn from ground layer"],
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
        # Dialog buttons
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
        only_selected_features = dlg.chk_only_selected.isChecked()
        clean_geometries = dlg.chk_clean_geometries.isChecked()
        clean_tolerance = float(dlg.txt_tolerance.text())
        enable_transition = dlg.chk_transition.isChecked()
        transition_slope = float(dlg.txt_slope.text())
        transition_start = float(dlg.txt_start.text())
        transition_extent = float(dlg.txt_extent.text())
        dem_layer = tools_qt.get_combo_value(dlg, dlg.cmb_dem_layer)
        if dem_layer == "":
            msg = "Please, select a DEM layer!"
            tools_qt.show_info_box(msg)
            return
        roughness_layer = tools_qt.get_combo_value(dlg, dlg.cmb_roughness_layer)
        if roughness_layer == "":
            msg = "Please, select a roughness layer!"
            tools_qt.show_info_box(msg)
            return
        losses_layer = tools_qt.get_combo_value(dlg, dlg.cmb_losses_layer)
        if losses_layer == "":
            msg = "Please, select a losses layer!"
            tools_qt.show_info_box(msg)
            return
        mesh_name = dlg.txt_name.text()

        if mesh_name == "":
            msg = "Please, fill the name of the mesh."
            tools_qt.show_info_box(msg)
            return

        if not mesh_name.isalnum() and "-" not in mesh_name:
            msg = "Only alphanumeric characters and hyphens are valid for the mesh name."
            tools_qt.show_info_box(msg)
            return

        # Check for existent meshes in file
        sql = "SELECT group_concat(name) as names FROM cat_file"
        retrieved_meshes = self.dao.get_row(sql)["names"]
        if retrieved_meshes is not None and mesh_name in retrieved_meshes.split(","):
            msg = "A mesh with the same name already exists. Do you want to overwrite it?"
            if not tools_qt.show_question(msg):
                return

        features = self.ground_layer.getFeatures()
        num_triangles = 0
        lowest_cellsize = float('inf')
        for feature in features:
            geom = feature.geometry()
            cellsize = feature["cellsize"]
            if cellsize < lowest_cellsize:
                lowest_cellsize = cellsize

            # sqrt(3)/4 * cellsize^2 = area of equilateral triangle
            triangle_area = 0.43301270189 * cellsize**2

            num_triangles += geom.area() / triangle_area

        print(f"Estimated number of triangles: {num_triangles}")
        # self.feedback.setProgressText(f"Estimated number of triangles: >{num_triangles}")

        # Warin the user if the number of triangles is too high with a dialog
        msg = ""
        if num_triangles > 10_000_000:
            msg = (
                # "Tens or hundreds of millions of records possible massive data generation, may impact performance."
                "The estimated number of triangles is extremely high (> 10M).\n"
                "This may take a long time to process.\n"
                "Check your memory, disk and cpu capabilties\n"
                "Do you want to continue?"
            )
            if not tools_qt.show_question(msg):
                return
        elif num_triangles > 1_000_000:
            msg = (
                "The estimated number of triangles is high (> 1M).\n"
                "This may take a long time to process.\n"
                "Make sure you have enough memory, disk and cpu capabilties\n"
                "Do you want to continue?"
            )
            if not tools_qt.show_question(msg):
                return

        # Create anchor layers combining mesh anchor points and bridge features
        mesh_anchor_points_lyr = self._get_layer(self.dao, "mesh_anchor_points")
        mesh_anchor_lines_lyr = self._get_layer(self.dao, "mesh_anchor_lines")
        bridge_lyr = self._get_layer(self.dao, "bridge")

        # Reset txt_infolog
        tools_qt.set_widget_text(dlg, 'txt_infolog', "")

        # Load input layers
        db_path = self.dao.db_filepath.replace('\\', '/')
        path = f"{db_path}|layername="

        # Load ground and roof layers from the QGIS project
        layers = {}
        for layer in ["ground", "roof"]:
            layer_path = f"{path}{layer}"
            layer_path = os.path.abspath(layer_path)
            lyrs = []
            for lyr in QgsProject.instance().mapLayers().values():
                if os.path.normpath(lyr.source()) == os.path.normpath(layer_path):
                    print(f"Layer: {lyr.name()} - {lyr.source()}")
                    lyrs.append(lyr)

            if len(lyrs) == 0:
                msg = f"Layer '{layer}' not found in the QGIS project."
                tools_qgis.show_warning(msg, dialog=dlg)
                return False
            elif len(lyrs) > 1:
                msg = f"Layer '{layer}' found multiple times in the QGIS project."
                tools_qgis.show_warning(msg, dialog=dlg)
                return False
            else:
                layers[layer] = lyrs[0]

        self.feedback = Feedback()
        self.thread_triangulation = DrCreateMeshTask(
            "Triangulation",
            execute_validations,
            clean_geometries,
            clean_tolerance,
            only_selected_features,
            enable_transition,
            transition_slope,
            transition_start,
            transition_extent,
            dem_layer,
            roughness_layer,
            losses_layer,
            mesh_name,
            point_anchor_layer=mesh_anchor_points_lyr,
            line_anchor_layer=mesh_anchor_lines_lyr,
            bridge_layer=bridge_lyr,
            feedback=self.feedback,
            ground_layer=layers["ground"],
            roof_layer=layers["roof"],
            inlet_layer=None,
            temporal_mesh=False,
            temp_layer_name="Mesh Temp Layer"
        )
        thread = self.thread_triangulation

        # Set signals
        dlg.btn_ok.setEnabled(False)
        dlg.btn_cancel.clicked.disconnect()
        dlg.btn_cancel.clicked.connect(thread.cancel)
        dlg.btn_cancel.clicked.connect(partial(dlg.btn_cancel.setText, "Canceling..."))
        thread.taskCompleted.connect(self._on_task_completed)
        thread.taskTerminated.connect(self._on_task_terminated)
        self.feedback.progress_changed.connect(self._progress_changed)
        self._progress_changed("Create Mesh", None, None, False)
        # thread.feedback.progressChanged.connect(dlg.progress_bar.setValue)

        # Show tab log
        tools_dr.set_tabs_enabled(self.dlg_mesh)
        self.dlg_mesh.mainTab.setCurrentIndex(1)

        # Timer
        self.t0 = time()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start(500)
        dlg.rejected.connect(self.timer.stop)

        QgsApplication.taskManager().addTask(thread)

    def _progress_changed(self, process, progress, text, new_line):
        # Progress bar
        if progress is not None:
            self.dlg_mesh.progress_bar.setValue(progress)

        # TextEdit log
        txt_infolog = self.dlg_mesh.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.dlg_mesh, txt_infolog, return_string_null=False)
        if process and process != self.cur_process:
            cur_text = f"{cur_text}\n" \
                       f"--------------------\n" \
                       f"{process}\n" \
                       f"--------------------\n\n"
            self.cur_process = process
            self.cur_text = None

        if self.cur_text:
            cur_text = self.cur_text

        end_line = '\n' if new_line else ''
        if text:
            txt_infolog.setText(f"{cur_text}{text}{end_line}")
        else:
            txt_infolog.setText(f"{cur_text}{end_line}")
        txt_infolog.show()
        # Scroll to the bottom
        scrollbar = txt_infolog.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

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

        # Add temp layer to TOC
        tools_qt.add_layer_to_toc(self.thread_triangulation.temp_layer, group="TEMPORAL")
        iface.setActiveLayer(self.thread_triangulation.temp_layer)
        iface.zoomToActiveLayer()

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
            group_name = "MESH INPUTS ERRORS & WARNINGS"
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
