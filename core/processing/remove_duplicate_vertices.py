from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDistance,
    QgsProcessingParameterVectorLayer,
    QgsProcessing,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication
from typing import Any, Optional

from qgis import processing

from ...lib import tools_qt, tools_qgis
from ..utils import tools_dr
from ... import global_vars


class DrRemoveDuplicateVertices(QgsProcessingAlgorithm):
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    TOLERANCE = 'TOLERANCE'

    tolerance: float = 0.000001
    ground_layer: Optional[QgsVectorLayer] = None
    roof_layer: Optional[QgsVectorLayer] = None

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'remove_duplicate_vertices'

    def displayName(self) -> str:
        return tools_qt.tr('Remove Duplicate Vertices')

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrRemoveDuplicateVertices()

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
        self.addParameter(
            QgsProcessingParameterDistance(
                self.TOLERANCE,
                tools_qt.tr('Tolerance'),
                defaultValue=0.000001
            )
        )

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        self.tolerance = self.parameterAsDouble(parameters, 'TOLERANCE', context)
        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)

        feedback.setProgressText(self.tr('Removing duplicate vertices...'))

        return {}

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        if self.ground_layer is None or self.roof_layer is None:
            feedback.pushWarning(self.tr('Error getting source layers.'))
            return {}

        feedback.setProgress(1)

        for layer in [self.ground_layer, self.roof_layer]:
            feedback.setProgressText(f"Processing layer: {layer.name()}")
            db_path = global_vars.gpkg_dao_data.db_filepath.replace('\\', '/')

            # Set progress range
            min_progress: int = 0
            max_progress: int = 0
            if layer == self.ground_layer:
                min_progress = 20
                max_progress = 55
            elif layer == self.roof_layer:
                min_progress = 55
                max_progress = 90

            # Run processing algorithm to remove duplicate vertices
            output = processing.run(
                "native:removeduplicatevertices",
                {
                    'INPUT': layer,
                    'TOLERANCE': self.tolerance,
                    'USE_Z_VALUE': False,
                    'OUTPUT': 'TEMPORARY_OUTPUT',
                },
                context=context,
                feedback=None,
            )
            cleaned_layer = output['OUTPUT']

            # Check if the output layer is valid
            if cleaned_layer is None:
                feedback.pushWarning(self.tr('Error removing duplicate vertices.'))
                return {}

            feedback.setProgress(min_progress)

            if layer:
                # Get layer features into dict
                features_dict = {feature['code']: feature for feature in layer.getFeatures()}

                # Start editing
                layer.startEditing()

                # Process features in batches
                batch_size = 5000
                cleaned_features = list(cleaned_layer.getFeatures())
                total_features = len(cleaned_features)

                for i in range(0, total_features, batch_size):
                    if feedback.isCanceled():
                        break

                    batch = cleaned_features[i:i + batch_size]
                    changes = {}

                    for cleaned_feature in batch:
                        # Get the original feature by code
                        original_feature = features_dict[cleaned_feature['code']]
                        if original_feature.isValid():
                            # Update only the geometry
                            changes[original_feature.id()] = cleaned_feature.geometry()

                    # Apply the batch changes
                    if changes:
                        layer.dataProvider().changeGeometryValues(changes)

                    feedback.setProgress(tools_dr.lerp_progress(int(i / total_features * 100), min_progress + 5, max_progress))

                # Commit changes
                layer.commitChanges()
                layer.dataProvider().forceReload()

            feedback.setProgressText(f"Layer {layer.name()} cleaned and saved to {layer.source()}")

        return {}

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)
