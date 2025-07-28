from qgis.core import (
    QgsFeature,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsProcessing,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication
from shapely import GeometryType
from typing import Any, Optional

from ...lib import tools_qgis

class DrFixMissingVertexAlgorithm(QgsProcessingAlgorithm):
    GROUND_LAYER = 'GROUND_LAYER'
    ROOF_LAYER = 'ROOF_LAYER'
    POINT_LAYER = 'INPUT'
    ONLY_SELECTED = 'ONLY_SELECTED'

    ground_layer: Optional[QgsVectorLayer] = None
    roof_layer: Optional[QgsVectorLayer] = None
    points_layer: Optional[QgsVectorLayer] = None
    only_selected: bool = False

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'fix_missing_vertex'

    def displayName(self) -> str:
        return 'Fix Missing Vertex Errors'

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

    def processAlgorithm(self, parameters: dict[str, Any], context: 'QgsProcessingContext', feedback: QgsProcessingFeedback) -> dict[str, Any]:
        """ Initialize parameters """

        self.ground_layer = self.parameterAsVectorLayer(parameters, self.GROUND_LAYER, context)
        self.roof_layer = self.parameterAsVectorLayer(parameters, self.ROOF_LAYER, context)
        self.points_layer = self.parameterAsVectorLayer(parameters, self.POINT_LAYER, context)
        self.only_selected = self.parameterAsBool(parameters, self.ONLY_SELECTED, context)

        feedback.setProgressText(self.tr('Fixing edge vertices...'))

        if self.points_layer is None:
            feedback.pushWarning(self.tr("Input Points is None"))
            return {}

        project = QgsProject.instance()
        if project is None:
            feedback.pushWarning(self.tr("Project is None! Do you have a project open?"))
            return {}

        return {}

    def postProcessAlgorithm(self, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        """ Fix vertex edge errors """

        if self.ground_layer is None or self.roof_layer is None or self.points_layer is None:
            feedback.pushWarning(self.tr("Layers are not set"))
            return {}

        self.ground_layer.startEditing()
        self.roof_layer.startEditing()

        feature_iterator = self.points_layer.getFeatures()
        if self.only_selected:
            feature_iterator = self.points_layer.getSelectedFeatures()

        ground_features: dict[str, QgsFeature] = {}
        for feature in self.ground_layer.getFeatures():
            ground_features[feature['code']] = feature.id()
        roof_features: dict[str, QgsFeature] = {}
        for feature in self.roof_layer.getFeatures():
            roof_features[feature['code']] = feature.id()

        points_fid = []
        for point_feature in feature_iterator:
            point_feature: QgsFeature
            point = point_feature.geometry()

            assert point.type() == GeometryType.POINT, "Geometry type is not Point"

            feature = None
            if point_feature["layer"] == self.ground_layer.name():
                if point_feature["polygon_code"] in ground_features:
                    feature = self.ground_layer.getFeature(ground_features[point_feature["polygon_code"]])
                else:
                    feedback.pushWarning(self.tr(f"Polygon code {point_feature['polygon_code']} not found in ground layer"))
            elif point_feature["layer"] == self.roof_layer.name():
                if point_feature["polygon_code"] in roof_features:
                    feature = self.roof_layer.getFeature(roof_features[point_feature["polygon_code"]])
                else:
                    feedback.pushWarning(self.tr(f"Polygon code {point_feature['polygon_code']} not found in roof layer"))
            else:
                feedback.pushWarning(self.tr(f"Invalid layer: {point_feature['layer']}"))
                continue

            if feature is None:
                continue

            polygon = feature.geometry()
            if polygon is None:
                feedback.pushWarning(self.tr(f"Invalid geometry for polygon {point_feature['polygon_code']}"))
                continue

            try:
                # Get the exact point coordinates
                point_coords = point.asPoint()

                # Find the closest segment and get the insertion index
                _, _, next_vert_index, _ = polygon.closestSegmentWithContext(point_coords)

                # Insert the vertex at the exact point location
                valid = polygon.insertVertex(x=point_coords.x(), y=point_coords.y(), beforeVertex=next_vert_index)

                if not valid:
                    feedback.pushWarning(self.tr(f"Failed to insert vertex at coordinates ({point_coords.x()}, {point_coords.y()})"))
                    continue

                if point_feature["layer"] == self.ground_layer.name():
                    success = self.ground_layer.changeGeometry(feature.id(), polygon)
                else:
                    success = self.roof_layer.changeGeometry(feature.id(), polygon)

                if not success:
                    feedback.pushWarning(self.tr(f"Failed to update geometry for polygon {point_feature['polygon_code']}"))
                    continue

                if valid and success:
                    points_fid.append(point_feature.id())
                    feedback.setProgressText(self.tr(f"Successfully inserted vertex at ({point_coords.x()}, {point_coords.y()})"))
            except Exception as e:
                feedback.pushWarning(self.tr(f"Error processing point {point_feature.id()}: {str(e)}"))
                continue

        # Commit changes
        if self.roof_layer.isModified():
            self.roof_layer.commitChanges()
        else:
            self.roof_layer.rollBack()

        if self.ground_layer.isModified():
            self.ground_layer.commitChanges()
        else:
            self.ground_layer.rollBack()

        self.ground_layer.updateExtents()
        self.ground_layer.triggerRepaint()
        self.roof_layer.updateExtents()
        self.roof_layer.triggerRepaint()

        # Remove fixed points from the input layer
        self.points_layer.startEditing()
        self.points_layer.deleteFeatures(points_fid)

        self.points_layer.commitChanges()
        self.points_layer.updateExtents()
        self.points_layer.triggerRepaint()

        feedback.setProgressText(self.tr('Fixed edge vertices...'))

        return {}

    def shortHelpString(self):
        return self.tr("""Inserts missing vertices into ground and roof polygons at the locations of input points, ensuring topological correctness. 
                       Only valid point and polygon geometries are processed, and the operation is optimized for large datasets. 
                       If the process cannot fix the vertices, the tool will provide feedback to help diagnose the issue. 
                       Use this tool to quickly correct edge and vertex errors in mesh input layers for improved data quality and processing.""")

    def tr(self, string: str):
            return QCoreApplication.translate('Processing', string)