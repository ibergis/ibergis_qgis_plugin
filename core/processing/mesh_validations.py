from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsProcessing,
    QgsProject
)
from qgis.PyQt.QtCore import QCoreApplication
from typing import Any

from ...lib import tools_qt, tools_qgis
from ...core.utils import tools_dr
from ... import global_vars
from ..threads.validatemesh import validations_dict, validate_input_layers


class DrMeshValidationsAlgorithm(QgsProcessingAlgorithm):
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'

    def __init__(self) -> None:
        super().__init__()
        self.validations = validations_dict()

        self.dao = global_vars.gpkg_dao_data.clone()

    def name(self) -> str:
        return 'mesh_validations'

    def displayName(self) -> str:
        return tools_qt.tr('Mesh Validations')

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrMeshValidationsAlgorithm()

    def shortHelpString(self):
        return self.tr("""Checks ground and roof polygon layers for common data issues such as invalid geometries, missing values, and topological errors. 
                       The operation is optimized for large datasets, and results are provided as error or warning layers to help you quickly identify and resolve problems. 
                       Use this tool to validate your mesh input layers and improve data quality before further processing or analysis.""")

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
        ground_layer_param = tools_qgis.get_layer_by_tablename('ground')
        roof_layer_param = tools_qgis.get_layer_by_tablename('roof')

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GROUND_LAYER,
                self.tr('Ground layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=ground_layer_param
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.ROOF_LAYER,
                self.tr('Roof layer'),
                optional=False,
                types=[QgsProcessing.SourceType.VectorPolygon],
                defaultValue=roof_layer_param
            )
        )
        for id, data in self.validations.items():
            value = tools_dr.get_config_parser('processing', f'{self.name()}_{id}', 'user', 'session', get_none=True)
            self.addParameter(QgsProcessingParameterBoolean(
                id,
                data['name'],
                defaultValue=value if value is not None else True
            ))

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        """ Main function to run validations """

        ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        path = f"{self.dao.db_filepath}|layername="
        self.layers: dict[str, QgsVectorLayer | QgsRasterLayer] = {}
        if ground_layer is None:
            ground_layer = tools_qgis.get_layer_by_tablename('ground')
            if ground_layer is None:
                ground_layer = QgsVectorLayer(f"{path}{'ground'}", 'ground', "ogr")
        self.layers['ground'] = ground_layer
        if roof_layer is None:
            roof_layer = tools_qgis.get_layer_by_tablename('roof')
            if roof_layer is None:
                roof_layer = QgsVectorLayer(f"{path}{'roof'}", 'roof', "ogr")
        self.layers['roof'] = roof_layer
        self.layers['dem'] = None

        # Get the validation parameters
        validations = []
        for validation in self.validations:
            value = self.parameterAsBoolean(parameters, validation, context)
            tools_dr.set_config_parser('processing', f'{self.name()}_{validation}', value)
            if self.parameterAsBoolean(parameters, validation, context):
                validations.append(validation)

        # Validate the input layer
        validation_layers = validate_input_layers(self.layers, validations, feedback)
        if validation_layers is None:
            feedback.reportError("Validation layers not found")
            return {}

        error_layers, warning_layers = validation_layers

        if error_layers or warning_layers:
            group_name = "MESH INPUTS ERRORS & WARNINGS"
            root = QgsProject.instance().layerTreeRoot()

            for layer in error_layers:
                group = tools_qgis.find_toc_group(root, group_name)
                if group is None:
                    group = root.insertGroup(0, group_name)
                QgsProject.instance().addMapLayer(layer, False)
                group.insertLayer(0, layer)
            for layer in warning_layers:
                group = tools_qgis.find_toc_group(root, group_name)
                if group is None:
                    group = root.insertGroup(0, group_name)
                QgsProject.instance().addMapLayer(layer, False)
                group.insertLayer(0, layer)

        return {}

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)
