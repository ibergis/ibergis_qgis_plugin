from sqlite3 import Row
from typing import Literal
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsVectorLayer

from ...lib.tools_gpkgdao import DrGpkgDao

LayerType = Literal["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon"]

class Query:
    def __init__(self, query: str, layer_type: LayerType, description: str, short_name: str, show_layer: bool = True) -> None:
        self.query = query
        self.layer_type = layer_type
        self.short_name = short_name
        self.description = description
        self.show_layer = show_layer

    def execute(self, dao: DrGpkgDao) -> QgsVectorLayer | int:
        if self.show_layer:
            query = f"SELECT AsWKT(geom) as geom FROM ({self.query})"
            rows: list[Row] | None = dao.get_rows(query)
            if not rows:
                return 0

            layer = QgsVectorLayer(self.layer_type, self.short_name, "memory")
            layer.setCrs(QgsProject.instance().crs())
            features = []
            provider = layer.dataProvider()
            for row in rows:
                row: Row
                geom = QgsGeometry.fromWkt(row['geom'])
                feature = QgsFeature()
                feature.setGeometry(geom)
                features.append(feature)

            provider.addFeatures(features)
            layer.updateExtents()

            return layer
        else:
            query = f"SELECT count(*) as count FROM ({self.query})"
            rows: Row | None = dao.get_row(query)
            if not rows:
                return 0
            return rows['count']


def get_queries() -> list[Query]:
    return [
        Query(
            "SELECT * FROM arc LIMIT 5",
            "LineString",
            "Arc test description",
            "Arc test",
            show_layer=False,
        ),
        Query(
            "SELECT * FROM node LIMIT 5",
            "Point",
            "Node test description",
            "Node test",
            show_layer=True,
        )
    ]
