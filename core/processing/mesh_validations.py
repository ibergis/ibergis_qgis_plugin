
from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterBoolean, QgsProject, QgsVectorLayer, QgsRasterLayer
from typing import Any

from ...lib import tools_qt
from ... import global_vars
from ..threads.validatemesh import validations_dict, validate_input_layers


class DrMeshValidationsAlgorithm(QgsProcessingAlgorithm):

    def __init__(self) -> None:
        super().__init__()
        self.validations = validations_dict()

        self.dao = global_vars.gpkg_dao_data.clone()
        path = f"{self.dao.db_filepath}|layername="
        layers_to_select = ["ground", "roof"]
        self.layers: dict[str, QgsVectorLayer | QgsRasterLayer] = {}
        for layer in layers_to_select:
            l = QgsVectorLayer(f"{path}{layer}", layer, "ogr")
            self.layers[layer] = l
        # self.layers["dem"] = self.dem_layer
        self.layers['dem'] = None

    def name(self) -> str:
        return 'mesh_validations'

    def displayName(self) -> str:
        return tools_qt.tr('Mesh Validations')

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrMeshValidationsAlgorithm()

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
        for id, data in self.validations.items():
            self.addParameter(QgsProcessingParameterBoolean(
                id,
                data['name'],
                defaultValue=True
            ))

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        """ Main function to run validations """

        # Get the validation parameters
        validations = []
        for validation in self.validations:
            if self.parameterAsBoolean(parameters, validation, context):
                validations.append(validation)



        # Validate the input layer
        validation_layers = validate_input_layers(self.layers, validations, feedback)
        if validation_layers is None:
            feedback.reportError("Validation layers not found")
            return {}

        error_layers, warning_layers = validation_layers

        if error_layers or warning_layers:
            group_name = "Mesh inputs errors & warnings"
            for layer in error_layers:
                QgsProject.instance().addMapLayer(layer)
                # tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
            for layer in warning_layers:
                QgsProject.instance().addMapLayer(layer)
                # tools_qt.add_layer_to_toc(layer, group_name, create_groups=True)
            # QgsProject.instance().layerTreeRoot().removeChildrenGroupWithoutLayers()
            # self.iface.layerTreeView().model().sourceModel().modelReset.emit()

        return {}
