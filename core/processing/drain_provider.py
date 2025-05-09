"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
from .import_ground_geometries import ImportGroundGeometries
from .import_roof_geometries import ImportRoofGeometries
from .fix_vertex_edge import DrFixEdgeVertexAlgorithm
from .import_execute_results import ImportExecuteResults
from .check_project import DrCheckProjectAlgorithm
from .set_outlet_for_inlets import SetOutletForInlets

class DrainProvider(QgsProcessingProvider):

    def __init__(self, plugin_dir):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)
        self.plugin_dir = plugin_dir

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.addAlgorithm(ImportGroundGeometries())
        self.addAlgorithm(ImportRoofGeometries())
        self.addAlgorithm(DrFixEdgeVertexAlgorithm())
        self.addAlgorithm(ImportExecuteResults())
        self.addAlgorithm(DrCheckProjectAlgorithm())
        self.addAlgorithm(SetOutletForInlets())


    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'DrainProvider'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Drain')

    def icon(self):
        return QIcon(f"{self.plugin_dir}{os.sep}icons{os.sep}toolbars{os.sep}utilities{os.sep}59.png")

    def longName(self):
        return self.name()