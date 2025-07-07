"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QStyledItemDelegate, QLineEdit, QDoubleSpinBox
from qgis.PyQt.QtCore import Qt


class NumericDelegate(QStyledItemDelegate):
    """ Delegate for numeric fields (double - SpinBox) """

    def __init__(self, parent=None, min_value: float=0, max_value: float=100000, step: float=1, decimals: int=3):
        super(NumericDelegate, self).__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(3)  # Number of decimal places
        editor.setMinimum(self.min_value)  # Set your minimum value
        editor.setMaximum(self.max_value)   # Set your maximum value
        editor.setSingleStep(self.step)     # Step size
        editor.setAlignment(Qt.AlignCenter)
        editor.setKeyboardTracking(False)
        editor.setToolTip("Enter a floating value")
        return editor
