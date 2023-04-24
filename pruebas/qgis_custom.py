""" Execute QGIS from independent application """
from qgis.core import QgsProject, QgsApplication, QgsVectorLayer
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtGui import QColor

import os
import sys


if __name__ == '__main__':

    # Path to QGIS installation
    # QgsApplication.setPrefixPath('/usr', True)

    # Create a reference to the QgsApplication
    app = QgsApplication([], True)

    # Load providers
    app.initQgis()

    folder = os.getcwd()
    filename = "gis/Europa.shp"
    layer_path = os.path.join(folder, filename)
    if not os.path.exists(layer_path):
        print(f"File not found: {layer_path}")
        exit()

    # Set layer
    layer = QgsVectorLayer(layer_path, 'input', 'ogr')
    if not layer.isValid():
        print(f"Layer failed to load: {layer_path}")
        exit()

    # Set canvas
    canvas = QgsMapCanvas()
    canvas.setWindowTitle("PyQGIS Standalone Application Example")
    canvas.setCanvasColor(QColor("#222222"))
    canvas.show()

    # Add layer to the map
    QgsProject.instance().addMapLayer(layer)
    canvas.setExtent(layer.extent())
    canvas.setLayers([layer])

    # Execute custom application
    exitcode = app.exec_()

    # Remove the provider and layer registries from memory
    app.exitQgis()
    sys.exit(exitcode)
