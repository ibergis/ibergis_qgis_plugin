from qgis.core import QgsFeature, QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterBoolean, QgsProcessingParameterVectorLayer, QgsProject, QgsVectorLayer
from shapely import GeometryType
from typing import Any

from lib.tools_gpkgdao import DrGpkgDao
from .... import global_vars

class DrFixEdgeVertexAlgorithm(QgsProcessingAlgorithm):
    GROUND_LAYER = 'GROUND_LAYER'
    POINT_LAYER = 'INPUT'
    ONLY_SELECTED = 'ONLY_SELECTED'

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'fix_edge_vertex'

    def displayName(self) -> str:
        return 'Fix Edge Vertex Errors'

    def createInstance(self) -> QgsProcessingAlgorithm:
        return type(self)()

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
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

        points_layer = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        only_selected = self.parameterAsBool(parameters, 'ONLY_SELECTED', context)

        if points_layer is None:
            raise ValueError("Input Points is None")

        project = QgsProject.instance()
        if project is None:
            raise ValueError("Project is None! Do you have a project open?")

        self.dao: DrGpkgDao = global_vars.gpkg_dao_data
        ground_layer = QgsVectorLayer(
            f"{self.dao.db_filepath}|layername=ground",
            "ground",
            "ogr"
        )

        ground_layer.startEditing()

        feature_iterator = points_layer.getFeatures()
        if only_selected:
            feature_iterator = points_layer.getSelectedFeatures()

        points_fid = []
        for point_feature in feature_iterator:
            point_feature: QgsFeature
            point = point_feature.geometry()

            assert point.type() == GeometryType.POINT, "Geometry type is not Point"

            feature = ground_layer.getFeature(point_feature["polygon_fid"])
            polygon = feature.geometry()

            _, _, next_vert_index, _ = polygon.closestSegmentWithContext(point.asPoint())
            valid = polygon.insertVertex(point.constGet(), next_vert_index)
            success = ground_layer.changeGeometry(feature.id(), polygon)

            if valid and success:
                points_fid.append(point_feature.id())

        # TODO: idk if the updateExtents and triggerRepaint are needed
        ground_layer.commitChanges()
        ground_layer.updateExtents()
        ground_layer.triggerRepaint()

        # Remove fixed points from the input layer
        points_layer.startEditing()
        for point_fid in points_fid:
            points_layer.deleteFeature(point_fid)

        points_layer.commitChanges()
        points_layer.updateExtents()
        points_layer.triggerRepaint()

        return {}


