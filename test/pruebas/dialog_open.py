# -*- coding: utf-8 -*-
import os
import sys
from qgis.PyQt import uic
from qgis.core import QgsApplication


def open_dialog(filepath, open_dialog=True):

    if not os.path.exists(filepath):
        print(f"File not found {filepath}")
        return None, None

    generated_class, base_class = uic.loadUiType(filepath)
    dialog = base_class()
    form = generated_class()
    form.setupUi(dialog)
    print(type(dialog))
    print(type(form))
    if open_dialog:
        dialog.show()

    return dialog, form


if __name__ == '__main__':

    # Create a reference to the QgsApplication
    app = QgsApplication([], True)

    # Load providers
    app.initQgis()

    folder_path = os.getcwd()
    if not os.path.exists(folder_path):
        print("File not found")
    filename = 'dialog_designer.ui'
    filepath = os.path.join(folder_path, filename)
    dialog, form = open_dialog(filepath)
    if dialog:
        dialog.setWindowTitle("TITLE")
        form.lbl_test.setText("Label TEST")
        form.txt_test.setText("LineEdit TEST")
        form.btn_test.move(190, 150)

    # Execute custom application
    exitcode = app.exec()

    # Remove the provider and layer registries from memory
    app.exitQgis()
    sys.exit(exitcode)
