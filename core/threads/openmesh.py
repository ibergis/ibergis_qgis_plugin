from pathlib import Path

from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant

from .task import GwTask
from ... import global_vars


class GwOpenMeshTask(GwTask):
    def __init__(self, description, file_path):
        super().__init__(description)
        self.file_path = file_path
        self.INITIAL_PROGRESS = 1
        self.POST_FILE_PROGRESS = 5
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()
        mesh = {"triangles": {}, "vertices": {}}

        self.setProgress(self.INITIAL_PROGRESS)

        with open(self.file_path) as file:
            section = ""
            for line in file:
                tokens = line.split()

                # skip empty lines
                if not len(tokens):
                    continue

                # section lines
                if tokens[0] in ["MATRIU", "VERTEXS", "CONDICIONS"]:
                    section = tokens[0]

                # ignore lines before first section
                if not section:
                    continue

                # MATRIU section
                if section == "MATRIU":
                    # skip lines that don't have 6 itens
                    # the count of polygons is also skipped
                    if len(tokens) != 6:
                        continue

                    v1, v2, v3, v4, roughness, fid = tokens
                    mesh["triangles"][fid] = {
                        "vertice_ids": [v1, v2, v3, v4],
                        "category": "ground",
                        "roughness": float(roughness),
                    }

                # VERTEXS section
                if section == "VERTEXS":
                    # skip lines that don't have 4 itens
                    # the count of polygons is also skipped
                    if len(tokens) != 4:
                        continue

                    x, y, z, fid = tokens
                    mesh["vertices"][fid] = {
                        "coordinates": (float(x), float(y)),
                        "elevation": float(z),
                    }

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

        total_tri = len(mesh["triangles"])
        counter_tri = 0
        for i, tri in mesh["triangles"].items():
            feature = QgsFeature()
            vertices = (mesh["vertices"][vert] for vert in tri["vertice_ids"])
            wkt = "TRIANGLE(("
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
            self.update_triangle_progress(counter_tri / total_tri)

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

    def update_triangle_progress(self, tri_progress: float):
        progress = (
            self.POST_LAYER_PROGRESS - self.POST_FILE_PROGRESS
        ) * tri_progress + self.POST_FILE_PROGRESS
        self.setProgress(progress)
