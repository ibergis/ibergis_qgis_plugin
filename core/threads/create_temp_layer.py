from pathlib import Path

from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .task import DrTask
from ... import global_vars


class DrCreateTempMeshLayerTask(DrTask):
    # TODO: includes losses_str
    def __init__(self, description, mesh):
        super().__init__(description)
        self.mesh = mesh
        self.POST_FILE_PROGRESS = 5
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()

        self.setProgress(self.POST_FILE_PROGRESS)

        temp_layer = QgsVectorLayer("Polygon", "Mesh Temp Layer", "memory")
        temp_layer.setCrs(QgsProject.instance().crs())
        provider = temp_layer.dataProvider()
        fields = [
            QgsField("fid", QVariant.Int),
            QgsField("category", QVariant.String),
            QgsField("vertex_id1", QVariant.Int),
            QgsField("vertex_id2", QVariant.Int),
            QgsField("vertex_id3", QVariant.Int),
            QgsField("vertex_id4", QVariant.Int),
            QgsField("roughness", QVariant.Double),
        ]
        provider.addAttributes(fields)
        temp_layer.updateFields()

        if self.isCanceled():
            return False

        total_tri = len(self.mesh["polygons"])
        counter_tri = 0
        for i, tri in self.mesh["polygons"].items():
            feature = QgsFeature()
            vertices = (self.mesh["vertices"][vert] for vert in tri["vertice_ids"])
            wkt = "POLYGON(("
            wkt += ",".join(
                f"{v['coordinates'][0]} {v['coordinates'][1]} {v['elevation']}"
                for v in vertices
            )
            wkt += "))"
            feature.setGeometry(QgsGeometry.fromWkt(wkt))
            feature.setAttributes(
                [i, tri["category"], *tri["vertice_ids"], tri["roughness"]]
            )
            provider.addFeature(feature)
            counter_tri += 1
            self.update_polygon_progress(counter_tri / total_tri)

            if self.isCanceled():
                return False

        temp_layer.updateExtents()

        self.setProgress(self.POST_LAYER_PROGRESS)

        # Set the style of the layer
        style_path = "resources/templates/mesh_temp_layer.qml"
        style_path = Path(global_vars.plugin_dir) / style_path
        style_path = str(style_path)
        temp_layer.loadNamedStyle(style_path)
        temp_layer.triggerRepaint()

        self.layer = temp_layer
        return True

    def update_polygon_progress(self, tri_progress: float):
        progress = (
            self.POST_LAYER_PROGRESS - self.POST_FILE_PROGRESS
        ) * tri_progress + self.POST_FILE_PROGRESS
        self.setProgress(progress)
