from qgis.core import (
    QgsFeature,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsProcessing
)
from qgis.PyQt.QtCore import QCoreApplication
from shapely import GeometryType
from typing import Any

from ...lib import tools_qgis

class DrFixEdgeVertexAlgorithm(QgsProcessingAlgorithm):
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    POINT_LAYER = 'INPUT'
    ONLY_SELECTED = 'ONLY_SELECTED'

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'fix_edge_vertex'

    def displayName(self) -> str:
        return 'Fix Edge Vertex Errors'

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def createInstance(self) -> QgsProcessingAlgorithm:
        return type(self)()

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
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.POINT_LAYER,
            "Input Points Layer"
        ))
        self.addParameter(QgsProcessingParameterBoolean(
            self.ONLY_SELECTED,
            "Only selected points",
            True
        ))

    def processAlgorithm(self, parameters: dict[str, Any], context: 'QgsProcessingContext', feedback: QgsProcessingFeedback | None) -> dict[str, Any]:

        ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)
        points_layer = self.parameterAsVectorLayer(parameters, self.POINT_LAYER, context)
        only_selected = self.parameterAsBool(parameters, self.ONLY_SELECTED, context)

        if points_layer is None:
            raise ValueError("Input Points is None")

        project = QgsProject.instance()
        if project is None:
            raise ValueError("Project is None! Do you have a project open?")

        ground_layer.startEditing()
        roof_layer.startEditing()

        feature_iterator = points_layer.getFeatures()
        if only_selected:
            feature_iterator = points_layer.getSelectedFeatures()

        points_fid = []
        for point_feature in feature_iterator:
            point_feature: QgsFeature
            point = point_feature.geometry()

            assert point.type() == GeometryType.POINT, "Geometry type is not Point"

            if point_feature["layer"] == ground_layer.name():
                feature = ground_layer.getFeature(point_feature["polygon_fid"])
            elif point_feature["layer"] == roof_layer.name():
                feature = roof_layer.getFeature(point_feature["polygon_fid"])
            else:
                raise ValueError(f"Invalid layer: {point_feature['layer']}")

            polygon = feature.geometry()

            _, _, next_vert_index, _ = polygon.closestSegmentWithContext(point.asPoint())
            valid = polygon.insertVertex(point.constGet(), next_vert_index)
            if point_feature["layer"] == ground_layer.name():
                success = ground_layer.changeGeometry(feature.id(), polygon)
            elif point_feature["layer"] == roof_layer.name():
                success = roof_layer.changeGeometry(feature.id(), polygon)
            else:
                raise ValueError(f"Invalid layer: {point_feature['layer']}")

            if valid and success:
                points_fid.append(point_feature.id())

        if roof_layer.isEditable():
            if roof_layer.isModified():
                roof_layer.commitChanges()
            else:
                roof_layer.rollBack()

        if ground_layer.isEditable():
            if ground_layer.isModified():
                ground_layer.commitChanges()
            else:
                ground_layer.rollBack()

        # Remove fixed points from the input layer
        points_layer.startEditing()
        for point_fid in points_fid:
            points_layer.deleteFeature(point_fid)

        points_layer.commitChanges()
        points_layer.updateExtents()
        points_layer.triggerRepaint()

        return {}

    def shortHelpString(self):
        return self.tr("""Inserts missing vertices into ground and roof polygons at the locations of input points, ensuring topological correctness. 
                       Only valid point and polygon geometries are processed, and the operation is optimized for large datasets. 
                       If the process cannot fix the vertices, the tool will provide feedback to help diagnose the issue. 
                       Use this tool to quickly correct edge and vertex errors in mesh input layers for improved data quality and processing.""")

    def tr(self, string: str):
            return QCoreApplication.translate('Processing', string)