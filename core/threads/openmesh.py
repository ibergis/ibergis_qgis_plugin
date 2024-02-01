from pathlib import Path

from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .task import DrTask
from ..utils import mesh_parser
from ... import global_vars
from ..utils.meshing_process import create_temp_mesh_layer


class DrOpenMeshTask(DrTask):
    def __init__(self, description, folder_path):
        super().__init__(description)
        self.folder_path = folder_path
        self.INITIAL_PROGRESS = 1
        self.POST_FILE_PROGRESS = 5
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()
        self.setProgress(self.INITIAL_PROGRESS)

        MESH_FILE = "Iber2D.dat"
        mesh_path = Path(self.folder_path) / MESH_FILE

        ROOF_FILE = "Iber_SWMM_roof.dat"
        roof_path = Path(self.folder_path) / ROOF_FILE

        with open(mesh_path) as mesh_file:
            if roof_path.exists():
                with open(roof_path) as roof_file:
                    mesh = mesh_parser.load_new(mesh_file, roof_file)
            else:
                mesh = mesh_parser.load_new(mesh_file)

        self.setProgress(self.POST_FILE_PROGRESS)
        temp_layer = create_temp_mesh_layer(mesh)
        self.setProgress(self.POST_LAYER_PROGRESS)

        self.layer = temp_layer
        return True

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

        total_tri = len(mesh["polygons"])
        counter_tri = 0
        for i, tri in mesh["polygons"].items():
            feature = QgsFeature()
            vertices = (mesh["vertices"][vert] for vert in tri["vertice_ids"])
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
