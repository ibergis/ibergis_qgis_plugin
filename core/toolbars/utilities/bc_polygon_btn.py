from functools import partial
from pathlib import Path

from qgis.core import (
    QgsFeature,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProject,
)
from qgis.gui import QgsMapToolIdentifyFeature, QgsRubberBand
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

from ..dialog import DrAction
from ...ui.ui_manager import DrBCFormUi
from ...utils import tools_dr
from ...utils.get_boundary import GetBoundary
from .... import global_vars
from ....lib import tools_db, tools_qgis, tools_qt


class DrCreateBCFromPolygon(DrAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.layers = {"ground": None, "roof": None, "boundary_conditions": None}
        self.action.setCheckable(True)
        self.dropdown_tree = {
            "2D Inlet": {
                "Total Discharge": {
                    "Critical/Subcritical": "INLET TOTAL DISCHARGE (SUB)CRITICAL"
                },
                "Water Elevation": "INLET WATER ELEVATION",
            },
            "2D Outlet": {
                "Supercritical/Critical": "OUTLET (SUPER)CRITICAL",
                "Subcritical": {
                    "Weir": {
                        "Height": "OUTLET SUBCRITICAL WEIR HEIGHT",
                        "Elevation": "OUTLET SUBCRITICAL WEIR ELEVATION",
                    },
                    "Given level": "OUTLET SUBCRITICAL GIVEN LEVEL",
                },
            },
        }
        self.bt_config = {
            "INLET TOTAL DISCHARGE (SUB)CRITICAL": {
                "timeseries": True,
                "timser_type": "BC FLOW",
                "other1": False,
                "lbl_other1": "other1",
                "other2": False,
                "lbl_other2": "other2",
            },
            "INLET WATER ELEVATION": {
                "timeseries": True,
                "timser_type": "BC ELEVATION",
                "other1": False,
                "lbl_other1": "other1",
                "other2": False,
                "lbl_other2": "other2",
            },
            "OUTLET (SUPER)CRITICAL": {
                "timeseries": False,
                "other1": False,
                "lbl_other1": "other1",
                "other2": False,
                "lbl_other2": "other2",
            },
            "OUTLET SUBCRITICAL WEIR HEIGHT": {
                "timeseries": False,
                "other1": True,
                "lbl_other1": "Weir Coefficient",
                "other2": True,
                "lbl_other2": "Height",
            },
            "OUTLET SUBCRITICAL WEIR ELEVATION": {
                "timeseries": False,
                "other1": True,
                "lbl_other1": "Weir Coefficient",
                "other2": True,
                "lbl_other2": "Elevation",
            },
            "OUTLET SUBCRITICAL GIVEN LEVEL": {
                "timeseries": True,
                "timser_type": "BC ELEVATION",
                "other1": False,
                "lbl_other1": "other1",
                "other2": False,
                "lbl_other2": "other2",
            },
        }

    def clicked_event(self):
        # Get ground, roof and boundary_condition layers
        dbpath = Path(global_vars.gpkg_dao_data.db_filepath).as_posix().lower()
        for layer in QgsProject.instance().mapLayers().values():
            layer_source = layer.dataProvider().dataSourceUri().lower()
            if layer_source.startswith(dbpath):
                for layer_name in self.layers:
                    if f"layername={layer_name}" in layer_source.split("|"):
                        self.layers[layer_name] = layer
                        break

        if not all(self.layers.values()):
            message = (
                "To make 'Create Boundary Condition from Polygon' function properly, "
                "you must have the ground, roof, and boundary conditions layers included in your project."
            )
            tools_qt.show_info_box(message)
            self.action.setChecked(False)
            return

        # Get polygon id
        canvas = iface.mapCanvas()
        self.feature_identifier = QgsMapToolIdentifyFeature(canvas)
        self.feature_identifier.setLayer(self.layers["ground"])
        self.feature_identifier.featureIdentified.connect(self._get_feature_boundary)
        self.lastMapTool = canvas.mapTool()
        canvas.mapToolSet.connect(self._uncheck)
        canvas.setMapTool(self.feature_identifier)

    def _get_feature_boundary(self, feature):
        # Get geometry of the boundary
        get_boundary = GetBoundary()
        get_boundary.initAlgorithm()
        params = {
            "polygon_id": feature["fid"],
            "ground_layer": self.layers["ground"],
            "roof_layer": self.layers["roof"],
            "OUTPUT": "TEMPORARY_OUTPUT",
        }
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        results = get_boundary.processAlgorithm(params, context, feedback)
        result_layer = context.getMapLayer(results["OUTPUT"])
        # Ignore empty results
        if result_layer.featureCount() == 0:
            return
        geometry = next(result_layer.getFeatures()).geometry()

        # Create new feature in boundary_conditions layer and open form
        bc_layer = self.layers["boundary_conditions"]
        feat = QgsFeature(bc_layer.fields())
        feat.setGeometry(geometry)
        feat["fid"] = "Autogenerate"
        self.rubber_band = QgsRubberBand(iface.mapCanvas())
        self.rubber_band.setWidth(3)
        self.rubber_band.setColor(QColor(255, 0, 0, 255))
        self.rubber_band.setToGeometry(geometry)

        # Configure and open form
        self.dlg = DrBCFormUi()

        sql = f"""SELECT id, idval FROM cat_bscenario WHERE active = 1"""
        row = tools_db.get_row(sql)
        if not row:
            msg = "No current bcscenario found"
            tools_qgis.show_warning(msg)
            bc_layer.rollBack()
            return
        self.cur_scenario = row["idval"]
        scenario_name = row["idval"]

        self.dlg.txt_fid.setText(feat["fid"])
        self.dlg.txt_bscenario_id.setText(str(scenario_name))
        tools_qt.double_validator(self.dlg.txt_other1)
        tools_qt.double_validator(self.dlg.txt_other2)

        # Handle boundary type combos
        self.dlg.cmb_bt1.currentTextChanged.connect(partial(self._manage_cmb_bt, 1))
        self.dlg.cmb_bt2.currentTextChanged.connect(partial(self._manage_cmb_bt, 2))
        self.dlg.cmb_bt3.currentTextChanged.connect(partial(self._manage_cmb_bt, 3))
        self.dlg.cmb_bt4.currentTextChanged.connect(partial(self._manage_cmb_bt, 4))
        self.dlg.cmb_bt2.setVisible(False)
        self.dlg.cmb_bt3.setVisible(False)
        self.dlg.cmb_bt4.setVisible(False)

        self.dlg.rejected.connect(bc_layer.rollBack)
        self.dlg.rejected.connect(self.rubber_band.reset)
        self.dlg.buttonBox.accepted.connect(
            partial(self._validate_and_save, bc_layer, feat)
        )

        iface.mapCanvas().setMapTool(self.lastMapTool)
        tools_dr.open_dialog(self.dlg, dlg_name="new_boundary_condition")
        tools_qt.fill_combo_box_list(
            self.dlg, self.dlg.cmb_bt1, self.dropdown_tree, allow_nulls=False
        )

    def _manage_cmb_bt(self, level, selected):
        combos = [
            self.dlg.cmb_bt1,
            self.dlg.cmb_bt2,
            self.dlg.cmb_bt3,
            self.dlg.cmb_bt4,
        ]
        if selected:
            selected_path = [cmb.currentText() for cmb in combos[0:level]]
            next_level = self.dropdown_tree
            for option in selected_path:
                next_level = next_level[option]
            if type(next_level) == dict:
                self.boundary_type = None
                tools_qt.fill_combo_box_list(
                    self.dlg, combos[level], next_level, allow_nulls=False
                )
                combos[level].setVisible(True)
            else:
                self.boundary_type = next_level
                config = self.bt_config[next_level]
                self.dlg.lbl_timeseries.setVisible(config["timeseries"])
                self.dlg.cmb_timeseries.setVisible(config["timeseries"])
                if config["timeseries"]:
                    rows = tools_db.get_rows(
                        f"""
                        SELECT id, idval FROM cat_timeseries 
                        WHERE timser_type = '{config['timser_type']}'
                        """
                    )
                    tools_qt.fill_combo_values(self.dlg.cmb_timeseries, rows)
                self.dlg.lbl_other1.setText(config["lbl_other1"])
                self.dlg.lbl_other1.setVisible(config["other1"])
                self.dlg.txt_other1.setVisible(config["other1"])
                self.dlg.lbl_other2.setText(config["lbl_other2"])
                self.dlg.lbl_other2.setVisible(config["other2"])
                self.dlg.txt_other2.setVisible(config["other2"])
                for combo in combos[level:]:
                    combo.clear()
                    combo.setVisible(False)
        else:
            for combo in combos[level:]:
                combo.clear()
                combo.setVisible(False)

    def _uncheck(self, old_tool):
        canvas = iface.mapCanvas()
        if canvas.mapTool() != self.feature_identifier:
            self.action.setChecked(False)
            canvas.mapToolSet.disconnect(self._uncheck)

    def _validate_and_save(self, layer, feature):
        layer.changeAttributeValue
        feature.setAttribute("code", self.dlg.txt_code.text())
        feature.setAttribute("descript", self.dlg.txt_descript.text())
        feature.setAttribute("bscenario", self.cur_scenario)
        feature.setAttribute("boundary_type", self.boundary_type)

        config = self.bt_config[self.boundary_type]
        if config["timeseries"]:
            timeseries = tools_qt.get_combo_value(
                self.dlg, self.dlg.cmb_timeseries
            )
            feature.setAttribute("timeseries", timeseries)
        if config["other1"]:
            other1_str = self.dlg.txt_other1.text()
            if not other1_str:
                tools_qt.show_info_box(
                    f"Please fill the field: '{config['lbl_other1']}'"
                )
                return
            feature.setAttribute("other1", float(other1_str))
        if config["other2"]:
            other2_str = self.dlg.txt_other2.text()
            if not other2_str:
                tools_qt.show_info_box(
                    f"Please fill the field: '{config['lbl_other2']}'"
                )
                return
            feature.setAttribute("other2", float(other2_str))

        self.dlg.accept()
        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        self.rubber_band.reset()
