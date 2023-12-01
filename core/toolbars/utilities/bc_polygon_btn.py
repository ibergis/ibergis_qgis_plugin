from functools import partial
from pathlib import Path

from qgis.core import (
    QgsFeature,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProject,
)
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.utils import iface

from ..dialog import GwAction
from ...utils.get_boundary import GetBoundary
from .... import global_vars


class GwCreateBCFromPolygon(GwAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.layers = {"ground": None, "roof": None, "boundary_conditions": None}

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

        # TODO: Handle the case of Ground or Roof or BC layers not in TOC
        if not all(self.layers.values()):
            print(self.layers)

        # Get polygon id
        canvas = iface.mapCanvas()
        self.feature_identifier = QgsMapToolIdentifyFeature(canvas)
        self.feature_identifier.setLayer(self.layers["ground"])
        self.feature_identifier.featureIdentified.connect(self._get_feature_boundary)
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
        bc_layer.startEditing()
        bc_layer.addFeature(feat)
        iface.openFeatureForm(self.layers["boundary_conditions"], feat)
