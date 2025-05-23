"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

import platform
from functools import partial
import os

from qgis.PyQt.QtCore import Qt, pyqtSignal, QVariant
from qgis.PyQt.QtWidgets import QCheckBox, QGridLayout, QLabel, QSizePolicy
from qgis.PyQt.QtGui import QColor
from qgis.core import Qgis, QgsWkbTypes, QgsSpatialIndex, QgsPointXY, QgsField, QgsProject, QgsVectorLayer, QgsFeature

from .task import DrTask
from ..utils import tools_dr
from ..ui.ui_manager import DrProjectCheckUi
from ... import global_vars
from ...lib import tools_qgis, tools_log, tools_qt, tools_os


class DrProjectCheckTask(DrTask):

    task_finished = pyqtSignal(list)
    progressUpdate = pyqtSignal(str)

    def __init__(self, description='', params=None, timer=None):

        super().__init__(description)
        self.params = params
        self.result = None
        self.dlg_audit_project = None
        self.timer = timer
        self.exception = None

        self.log_messages = []
        self.log_features_arc = []
        self.log_features_node = []
        self.log_features_polygon = []


    def run(self):

        super().run()

        layers = self.params['layers']
        init_project = self.params['init_project']
        self.dlg_audit_project = self.params['dialog']
        msg = "Task 'Check project' execute function '{0}'"
        msg_params = ("check_project_execution",)
        tools_log.log_info(msg, msg_params=msg_params)
        # Call functions
        status, self.result = self.check_project_execution(layers, init_project)
        if not status:
            msg = "Function {0} returned False. Reason"
            tools_log.log_info(msg, parameter=self.result, msg_params=msg_params)
            return False

        return True


    def finished(self, result):

        super().finished(result)

        self.dlg_audit_project.btn_accept.setEnabled(True)
        self.dlg_audit_project.progressBar.setVisible(False)
        if self.timer:
            self.timer.stop()
        if self.isCanceled():
            self.setProgress(100)
            return

        # Handle exception
        if self.exception is not None:
            msg = f"<b>{tools_qt.tr("Key")}: </b>{self.exception}<br>"
            msg += f"<b>{tools_qt.tr("Key container")}: </b>'body/data/ <br>"
            msg += f"<b>{tools_qt.tr("Python file")}: </b>{__name__} <br>"
            msg += f"<b>{tools_qt.tr("Python function")}:</b> {self.__class__.__name__} <br>"
            title = "Key on returned json from ddbb is missed."
            tools_qt.show_exception_message(title, msg)
            return

        # Show dialog with audit check project result
        self._show_check_project_result()

        self.setProgress(100)


    def check_project_execution(self, layers, init_project):
        """ Execute python functions to check the project """

        update_text = "CHECK PROJECT\n--------------------\n\n"
        self.progressUpdate.emit(update_text)
        # Check the network topology
        status, message = self._check_topology(layers)
        if not status:
            return False, f"Topology check failed: {message}"
        # Check roof volumes
        status, message = self._check_roof_volumes()
        if not status:
            return False, f"Roof volumes check failed: {message}"

        return True, message

    # region private functions


    def _get_project_feature_count(self, layers_to_check=None):
        # Initialize a variable to store the total feature count
        if layers_to_check is None:
            layers_to_check = []
        total_feature_count = 0
        layers = tools_qgis.get_project_layers()

        # Iterate through each layer
        for layer in layers:
            layer.dataProvider().reloadData()
            if layers_to_check and tools_qgis.get_tablename_from_layer(layer) not in layers_to_check:
                continue
            # Check if the layer is valid and has features
            if layer.isValid() and layer.featureCount() > 0:
                # Add the feature count of the layer to the total count
                total_feature_count += layer.featureCount()

        self.total_feature_count = total_feature_count


    def _check_topology(self, layers):
        """ Checks if there are node on top of eachother """

        try:
            geometry_dict = {
                QgsWkbTypes.LineGeometry: 'Arc',
                QgsWkbTypes.PointGeometry: 'Node',
                QgsWkbTypes.PolygonGeometry: 'Polygon'
            }
            update_text = 'Check topology process'
            self.progressUpdate.emit(update_text)
            node_layers_to_check = ['inp_storage', 'inp_outfall', 'inp_junction', 'inp_divider']
            node_layers = [tools_qgis.get_layer_by_tablename(lyr) for lyr in node_layers_to_check]
            node_layers = [lyr for lyr in node_layers if lyr is not None]
            node_buffer = 0.05

            arc_layers_to_check = ['inp_outlet', 'inp_weir', 'inp_orifice', 'inp_pump', 'inp_conduit']
            arc_layers = [tools_qgis.get_layer_by_tablename(lyr) for lyr in arc_layers_to_check]
            arc_layers = [lyr for lyr in arc_layers if lyr is not None]
            arc_buffer = 2

            polygon_layers_to_check = ['roof']
            polygon_layers = [tools_qgis.get_layer_by_tablename(lyr) for lyr in polygon_layers_to_check]
            polygon_layers = [lyr for lyr in polygon_layers if lyr is not None]

            layers_to_check = node_layers_to_check + arc_layers_to_check + polygon_layers_to_check
            # Get total number of features to provide accurate progress feedback
            self._get_project_feature_count(layers_to_check)

            progress_step = self.total_feature_count // 20  # 5% increments (20 steps)
            aux_progress_step = self.total_feature_count // 4  # 25% increments (4 steps)
            n = 0
            for layer in layers:
                layer_name = tools_qgis.get_tablename_from_layer(layer)
                if layer_name not in layers_to_check:
                    continue

                check_attr = []
                if layer.geometryType() == QgsWkbTypes.LineGeometry:
                    check_attr = ['node_1', 'node_2']
                    if layer_name in ('inp_weir', 'inp_conduit'):
                        check_attr.append('shape')
                elif layer.geometryType() == QgsWkbTypes.PointGeometry:
                    pass
                elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    if layer_name == 'roof':
                        check_attr = ['outlet_code']


                for feature in layer.getFeatures():
                    n += 1
                    progress_percent = (n / self.total_feature_count) * 100
                    # Give feedback
                    if n % progress_step == 0:
                        update_text = '.'
                        self.progressUpdate.emit(update_text)
                    if n % aux_progress_step == 0:
                        update_text = f"{int(progress_percent)}%"
                        self.progressUpdate.emit(update_text)
                    if n >= self.total_feature_count:
                        update_text = "100%"
                        self.progressUpdate.emit(update_text)
                    feature_geom = feature.geometry()

                    # Check NULL attributes
                    msg = None
                    descript = "NULL attributes: "
                    for attr in check_attr:
                        if feature[attr] in (None, 'NULL', 'null'):
                            if not msg:
                                msg = f"WARNING! {layer.name()} {feature['code']} doesn't have {attr}"
                            else:
                                msg += f", {attr}"

                            descript += f"{attr}, "
                    if msg:
                        self.log_messages.append(msg)
                        descript = descript[:-2]
                        getattr(self, f'log_features_{geometry_dict.get(feature_geom.type()).lower()}').append((feature, descript))

                    # Lines
                    if feature_geom.type() == QgsWkbTypes.LineGeometry:
                        pass

                    # Points
                    elif feature_geom.type() == QgsWkbTypes.PointGeometry:
                        for node_layer in node_layers:
                            spatial_index = QgsSpatialIndex(node_layer.getFeatures())
                            node = spatial_index.nearestNeighbor(feature_geom.asPoint(), 2, node_buffer)
                            if len(node) > 1:
                                msg = f"WARNING! Node {feature['code']} has another node too close."
                                self.log_messages.append(msg)
                                self.log_features_node.append(feature)
                                continue

                    # Polygons
                    elif feature_geom.type() == QgsWkbTypes.PolygonGeometry:
                        pass

                    # Other / No geometry
                    else:
                        pass
        except Exception as e:
            return False, e

        return True, "Success"


    def _check_roof_volumes(self):
        """  """

        try:
            layer_name = "roof"
            layer = tools_qgis.get_layer_by_tablename(layer_name)
            if layer is None:
                return False, f"Layer '{layer_name}' not found"

            for feature in layer.getFeatures():
                outlet_vol = feature["outlet_vol"] if feature["outlet_vol"] else 0
                street_vol = feature["street_vol"] if feature["street_vol"] else 0
                infiltr_vol = feature["infiltr_vol"] if feature["infiltr_vol"] else 0

                if outlet_vol + street_vol + infiltr_vol != 100:
                    msg = f"WARNING! Roof {feature['code']} has volumes that don't sum up to 100."
                    self.log_messages.append(msg)
                    descript = f"{outlet_vol=}, {street_vol=}, {infiltr_vol=}"
                    self.log_features_polygon.append((feature, descript))
        except Exception as e:
            return False, e

        return True, "Success"


    def _show_check_project_result(self):
        """ Show dialog with audit check project results """

        # Populate info_log
        txt_log = "\nRESULTS\n--------------------\n\n"

        if self.result != "Success":
            txt_log = f"{txt_log}Execution failed.\n{self.result}"
            tools_qt.set_widget_text(self.dlg_audit_project, 'txt_infolog', txt_log)
            tools_qt.hide_void_groupbox(self.dlg_audit_project)
            return
        for log_message in self.log_messages:
            txt_log = f"{txt_log}{log_message}\n"
        if not self.log_messages:
            txt_log = f"{txt_log}Everything OK!\n"

        cur_text = tools_qt.get_text(self.dlg_audit_project, 'txt_infolog')
        tools_qt.set_widget_text(self.dlg_audit_project, 'txt_infolog', f"{cur_text}\n\n{txt_log}")
        tools_qt.hide_void_groupbox(self.dlg_audit_project)

        # Add temporal layers if needed
        if any([self.log_features_node, self.log_features_arc, self.log_features_polygon]):
            self._add_temp_layers()


    def _add_temp_layers(self):
        """ Create temporal layers with the conflicting features """

        # Create a group & add layers to the group
        group_name = "DRAIN TEMPORAL"
        root = QgsProject.instance().layerTreeRoot()
        my_group = root.findGroup(group_name)
        if my_group is None:
            my_group = root.insertGroup(0, group_name)
        else:
            # If the group already exists, remove existing layers with names "node" and "arc"
            for child in my_group.children():
                if child.name() in ["node", "arc"]:
                    QgsProject.instance().removeMapLayer(child.layerId())

        if self.log_features_node:
            # Create in-memory layers
            node_fields = [QgsField("code", QVariant.String), QgsField("descript", QVariant.String)]
            node_layer = self.create_in_memory_layer("Point", "node", node_fields)
            # Add features to the layers
            self.add_features_to_layer(node_layer, self.log_features_node, 'code')
            # Add layer to ToC
            QgsProject.instance().addMapLayer(node_layer, False)
            my_group.insertLayer(0, node_layer)
            # Set layer symbology
            node_layer.renderer().symbol().setColor(QColor("red"))
            node_layer.renderer().symbol().setSize(3.5)
            node_layer.renderer().symbol().setOpacity(0.7)
            global_vars.iface.layerTreeView().refreshLayerSymbology(node_layer.id())

        if self.log_features_arc:
            # Create in-memory layers
            arc_fields = [QgsField("code", QVariant.String), QgsField("descript", QVariant.String)]
            arc_layer = self.create_in_memory_layer("LineString", "arc", arc_fields)
            # Add features to the layers
            self.add_features_to_layer(arc_layer, self.log_features_arc, 'code')
            # Add layer to ToC
            QgsProject.instance().addMapLayer(arc_layer, False)
            my_group.insertLayer(1, arc_layer)
            # Set the rendering style
            arc_layer.renderer().symbol().setColor(QColor("red"))
            arc_layer.renderer().symbol().setWidth(1.5)
            arc_layer.renderer().symbol().setOpacity(0.7)
            global_vars.iface.layerTreeView().refreshLayerSymbology(arc_layer.id())

        if self.log_features_polygon:
            # Create in-memory layers
            oolygon_fields = [QgsField("code", QVariant.String), QgsField("descript", QVariant.String)]
            polygon_layer = self.create_in_memory_layer("Polygon", "polygon", oolygon_fields)
            # Add features to the layers
            self.add_features_to_layer(polygon_layer, self.log_features_polygon, 'code')
            # Add layer to ToC
            QgsProject.instance().addMapLayer(polygon_layer, False)
            my_group.insertLayer(1, polygon_layer)
            # Set the rendering style
            polygon_layer.renderer().symbol().setColor(QColor("red"))
            polygon_layer.renderer().symbol().setOpacity(0.7)
            global_vars.iface.layerTreeView().refreshLayerSymbology(polygon_layer.id())

        # Refresh the map canvas
        global_vars.iface.mapCanvas().refresh()


    def create_in_memory_layer(self, geometry_type, layer_name, fields):
        srid = global_vars.project_epsg
        layer = QgsVectorLayer(f"{geometry_type}?crs=epsg:{srid}", layer_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        return layer


    def add_features_to_layer(self, layer, features, field_id):
        layer.startEditing()
        for feature, descript in features:
            feature_geom = feature.geometry()
            new_feature = QgsFeature(layer.fields())
            new_feature.setGeometry(feature_geom)
            new_feature.setAttribute(field_id, feature[field_id])
            new_feature.setAttribute('descript', descript)
            layer.addFeature(new_feature)
        layer.commitChanges()

    # endregion
