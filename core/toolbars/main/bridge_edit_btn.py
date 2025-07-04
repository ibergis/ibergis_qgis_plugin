"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from functools import partial

from qgis.gui import QgsMapToolIdentifyFeature
from qgis.utils import iface

from ..dialog import DrAction
from ...shared.bridge import DrBridge
from ....lib import tools_qgis, tools_qt


class DrBridgeEditButton(DrAction):
    """ Button ---: Bridge edit """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.action.setCheckable(True)
        self.bridge = DrBridge()

    def clicked_event(self):
        # Get bridge layer
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            msg = "Bridge layer not found. Please make sure the bridge layer is loaded in your project."
            tools_qt.show_info_box(msg)
            self.action.setChecked(False)
            return

        # Set up map tool for bridge selection
        canvas = iface.mapCanvas()
        self.feature_identifier = QgsMapToolIdentifyFeature(canvas)
        self.feature_identifier.setLayer(bridge_layer)
        self.feature_identifier.featureIdentified.connect(self._on_bridge_selected)
        self.lastMapTool = canvas.mapTool()
        canvas.mapToolSet.connect(self._uncheck)
        canvas.setMapTool(self.feature_identifier)

    def _on_bridge_selected(self, feature):
        """Callback when a bridge feature is selected on the map."""
        # Reset map tool
        iface.mapCanvas().setMapTool(self.lastMapTool)
        self.action.setChecked(False)

        # Open bridge dialog with selected feature
        self.bridge.manage_bridge(feature)

    def _uncheck(self, old_tool):
        """Uncheck the button when map tool changes."""
        canvas = iface.mapCanvas()
        if canvas.mapTool() != self.feature_identifier:
            self.action.setChecked(False)
            canvas.mapToolSet.disconnect(self._uncheck)
