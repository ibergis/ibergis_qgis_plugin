from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterDistance, QgsProject
from typing import Any

from qgis import processing

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt
from ... import global_vars


class DrRemoveDuplicateVertices(QgsProcessingAlgorithm):

    def __init__(self) -> None:
        super().__init__()
        self.dao: DrGpkgDao = global_vars.gpkg_dao_data.clone()

    def name(self) -> str:
        return 'remove_duplicate_vertices'

    def displayName(self) -> str:
        return tools_qt.tr('Remove duplicate vertices')

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrRemoveDuplicateVertices()

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
        self.addParameter(
            QgsProcessingParameterDistance(
                'TOLERANCE',
                tools_qt.tr('Tolerance'),
                defaultValue=0.000001
            )
        )

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        tolerance = self.parameterAsDouble(parameters, 'TOLERANCE', context)

        db_path = self.dao.db_filepath.replace('\\', '/')
        for layer_name in ['ground', 'roof']:
            feedback.pushInfo(f"Processing layer: {layer_name}")

            layer_path = f"{db_path}|layername={layer_name}"

            output = processing.run(
                "native:removeduplicatevertices",
                {
                    'INPUT': layer_path,
                    'TOLERANCE': tolerance,
                    'USE_Z_VALUE': False,
                    'OUTPUT': 'TEMPORARY_OUTPUT',
                },
                context=context,
                feedback=feedback,
            )
            cleaned_layer = output['OUTPUT']
            processing.run(
                "native:savefeatures",
                {
                    'INPUT': cleaned_layer,
                    'OUTPUT': db_path,
                    'LAYER_NAME': layer_name,
                    'ACTION_ON_EXISTING_FILE': 1,
                },
                context=context,
                feedback=feedback,
            )

            feedback.pushInfo(f"Layer {layer_name} cleaned and saved to {db_path}")

            # Update the layer in the project
            for lyr in QgsProject.instance().mapLayers().values():
                if lyr.source() == layer_path:
                    print(f"Layer: {lyr.name()} - {lyr.source()}")
                    lyr.dataProvider().forceReload()

        return {}
