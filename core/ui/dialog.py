"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QDialog, QSizePolicy
from qgis.PyQt.QtGui import QIcon

from qgis.gui import QgsMessageBar

from ... import global_vars


class GwDialog(QDialog):

    key_escape = QtCore.pyqtSignal()

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        # Create message bar
        try:
            self._messageBar = QgsMessageBar()
            self.messageBar().setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            for idx in range(self.layout().count(), 0, -1):
                item = self.layout().itemAt(idx - 1)
                row, column, rowSpan, columnSpan = self.layout().getItemPosition(idx - 1)
                if item is not None:
                    self.layout().removeItem(item)
                    if item.widget() is not None:
                        self.layout().addWidget(item.widget(), row + 1, column, rowSpan, columnSpan)
                    elif item.layout() is not None:
                        self.layout().addLayout(item.layout(), row + 1, column, rowSpan, columnSpan)
            self.layout().addWidget(self.messageBar(), 0, 0, 1, -1)
        except Exception:
            self._messageBar = global_vars.iface

        # Set window icon
        icon_folder = f"{global_vars.plugin_dir}{os.sep}icons"
        icon_path = f"{icon_folder}{os.sep}dialogs{os.sep}20x20{os.sep}drain.png"
        giswater_icon = QIcon(icon_path)
        self.setWindowIcon(giswater_icon)


    def keyPressEvent(self, event):

        try:
            if event.key() == QtCore.Qt.Key_Escape:
                self.key_escape.emit()
                return super().keyPressEvent(event)
        except RuntimeError:
            # Multiples signals are emited when we use key_scape in order to close dialog
            pass

    def messageBar(self):
        return self._messageBar
