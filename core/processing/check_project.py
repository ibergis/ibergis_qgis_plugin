from sqlite3 import Row

from numpy.__config__ import show
from qgis.core import QgsFeature, QgsProcessingAlgorithm, QgsProcessingContext, QgsGeometry, QgsProcessingFeedback, QgsProcessingParameterBoolean, QgsProcessingParameterVectorLayer, QgsProject, QgsVectorLayer
from shapely import Polygon
from typing import Any

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt
from ... import global_vars

class Query:
    def __init__(self, query: str, description: str, short_name: str, show_layer: bool = True) -> None:
        self.query = query
        self.short_name = short_name
        self.description = description
        self.show_layer = show_layer

    def execute(self, dao: DrGpkgDao) -> QgsVectorLayer | int:
        if self.show_layer:
            query = f"SELECT AsWKT(geom) as geom FROM ({self.query})"
            rows: list[Row] | None = dao.get_rows(query)
            if not rows:
                return 0

            layer = QgsVectorLayer("Polygon", self.short_name, "memory")
            layer.setCrs(QgsProject.instance().crs())
            provider = layer.dataProvider()
            for row in rows:
                geom = row['geom']
                geom = QgsGeometry.fromWkt(geom)
                feature = QgsFeature()
                feature.setGeometry(geom)
                provider.addFeature(feature)
            layer.updateExtents()

            return layer
        else:
            query = f"SELECT count(*) as count FROM ({self.query})"
            rows: Row | None = dao.get_row(query)
            if not rows:
                return 0
            return rows['count']


class DrCheckProjectAlgorithm(QgsProcessingAlgorithm):

    QUERIES: list[Query] = [
        Query(
            "SELECT * FROM ground LIMIT 5",
            "Ground Geometries",
            "Ground Geometries",
            show_layer=False,
        ),
    ]

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'check_project'

    def displayName(self) -> str:
        return tools_qt.tr('Check Project')

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrCheckProjectAlgorithm()

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
        for query in self.QUERIES:
            self.addParameter(
                QgsProcessingParameterBoolean(
                    query.short_name,
                    tools_qt.tr(query.description),
                    defaultValue=True,
                )
            )

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback | None) -> dict[str, Any]:
        self.dao: DrGpkgDao = global_vars.gpkg_dao_data

        for query in self.QUERIES:
            if feedback and feedback.isCanceled():
                break

            if not self.parameterAsBoolean(parameters, query.short_name, context):
                continue

            layer = query.execute(self.dao)
            if isinstance(layer, QgsVectorLayer):
                QgsProject.instance().addMapLayer(layer)
            elif isinstance(layer, int):
                if feedback:
                    feedback.setProgressText(f"{query.short_name}: {layer} geometries")

        return {}
