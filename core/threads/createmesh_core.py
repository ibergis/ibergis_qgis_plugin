from qgis import processing
from qgis.core import QgsGeometry, QgsVectorLayer, QgsField


def create_mesh_dict(triangulations_list):
    mesh = {"triangles": {}, "vertices": {}}
    next_triangle_id = 1
    next_vertice_id = 1

    for triangles, vertices, metadata in triangulations_list:
        for i, triangle in enumerate(triangles, start=next_triangle_id):
            vertice_ids = [int(triangle[v] + next_vertice_id) for v in (0, 1, 2, 0)]
            mesh["triangles"][i] = {"vertice_ids": vertice_ids}
            mesh["triangles"][i].update(metadata)
            next_triangle_id = i + 1

        for i, vertice in enumerate(vertices, start=next_vertice_id):
            mesh["vertices"][i] = {"coordinates": (vertice)}
            mesh["vertices"][i].update(metadata)
            next_vertice_id = i + 1

    return mesh


def feature_to_layer(feature, crs):
    layer = QgsVectorLayer("MultiPolygon", "temp", "memory")
    layer.startEditing()
    layer.setCrs(crs)
    for field in feature.fields():
        layer.addAttribute(QgsField(field))
    layer.addFeature(feature)
    layer.commitChanges()
    layer.updateExtents()
    return layer


def triangulate_roof(roof_layer):
    params = {"INPUT": roof_layer, "OUTPUT": "TEMPORARY_OUTPUT"}
    res = processing.run("3d:tessellate", params)

    roof_meshes = []
    for feature in res["OUTPUT"].getFeatures():
        geom = feature.geometry()
        vertices = [(v.x(), v.y()) for v in geom.vertices()]
        triangles = [
            [vertices.index((v.x(), v.y())) for v in triangle.vertices()]
            for triangle in geom.asGeometryCollection()
        ]
        roof_metadata = {
            "category": "roof",
            "roof_id": feature["fid"],
            "elevation": feature["elev"],
            "roughness": feature["roughness"],
        }
        roof_meshes.append((triangles, vertices, roof_metadata))

    return roof_meshes
