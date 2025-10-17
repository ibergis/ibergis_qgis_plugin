"""
This file is part of IberGIS
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
from .fix_missing_vertex import DrFixMissingVertexAlgorithm
from .mesh_validations import DrMeshValidationsAlgorithm
from .remove_duplicate_vertices import DrRemoveDuplicateVertices
from .simplify_mesh_input_geometries import SimplifyMeshInputGeometries
from .create_temporal_mesh import CreateTemporalMesh
from .fix_intersections import FixIntersections
from .check_small_polygons import CheckSmallPolygons
from .fix_small_polygons import FixSmallPolygons
from .check_invalid_donuts import CheckInvalidDonuts
from .fix_geometry import FixGeometry
from .fix_orphan_grounds import FixOrphanGrounds
from .check_close_vertices import CheckCloseVertices


class DrainMeshProvider(QgsProcessingProvider):

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
        self.addAlgorithm(DrFixMissingVertexAlgorithm())
        self.addAlgorithm(DrMeshValidationsAlgorithm())
        self.addAlgorithm(DrRemoveDuplicateVertices())
        self.addAlgorithm(SimplifyMeshInputGeometries())
        self.addAlgorithm(CreateTemporalMesh())
        self.addAlgorithm(FixIntersections())
        self.addAlgorithm(CheckSmallPolygons())
        self.addAlgorithm(FixSmallPolygons())
        self.addAlgorithm(CheckInvalidDonuts())
        self.addAlgorithm(FixGeometry())
        self.addAlgorithm(FixOrphanGrounds())
        self.addAlgorithm(CheckCloseVertices())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'IberGISMeshProvider'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('IberGIS - Mesh')

    def icon(self):
        return QIcon(f"{self.plugin_dir}{os.sep}icons{os.sep}toolbars{os.sep}utilities{os.sep}59.png")

    def longName(self):
        return self.name()
