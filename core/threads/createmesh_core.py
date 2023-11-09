from qgis import processing
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant


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


def get_ground_roughness(mesh_dict, roughness_layer, landuses, feedback):
    # Calculate concrete values for each roughness polygon
    # (landuse or custom_roughness)
    url = "MultiPolygon?index=yes"
    temp_roughness = QgsVectorLayer(url, "roughness", "memory")
    temp_roughness.setCrs(roughness_layer.crs())
    provider = temp_roughness.dataProvider()
    fields = [
        QgsField("fid", QVariant.Int),
        QgsField("roughness", QVariant.Double),
    ]
    provider.addAttributes(fields)
    temp_roughness.updateFields()
    for feature in roughness_layer.getFeatures():
        new_feature = QgsFeature()
        new_feature.setGeometry(feature.geometry())
        if type(feature["custom_roughness"]) in [int, float]:
            roughness = feature["custom_roughness"]
        else:
            roughness = landuses[feature["landuse"]]
        new_feature.setAttributes([feature["fid"], roughness])
        provider.addFeature(new_feature)
    temp_roughness.updateExtents()

    # Rasterize temp_roughness layer
    resolution = 1
    e = temp_roughness.extent()
    params = {
        "BURN": 0,
        "DATA_TYPE": 5,
        "EXTENT": f"{e.xMinimum()},{e.xMaximum()},{e.yMinimum()},{e.yMaximum()}",
        "EXTRA": "",
        "FIELD": "roughness",
        "HEIGHT": resolution,
        "INIT": None,
        "INPUT": temp_roughness,
        "INVERT": False,
        "NODATA": 0,
        "OPTIONS": "",
        "OUTPUT": "TEMPORARY_OUTPUT",
        "UNITS": 1,
        "USE_Z": False,
        "WIDTH": resolution,
    }
    res = processing.run("gdal:rasterize", params)
    if feedback.isCanceled():
        return
    raster_layer = res["OUTPUT"]

    # Get roughness for each ground triangle
    url = "Polygon?field=fid:integer&index=yes"
    ground_triangles = QgsVectorLayer(url, "gt", "memory")
    ground_triangles.setCrs(roughness_layer.crs())
    for i, tri in mesh_dict["triangles"].items():
        if feedback.isCanceled():
            return
        if tri["category"] == "ground":
            feature = QgsFeature()
            polygon_points = [
                QgsPointXY(*mesh_dict["vertices"][vert]["coordinates"])
                for vert in tri["vertice_ids"]
            ]
            feature.setGeometry(QgsGeometry.fromPolygonXY([polygon_points]))
            feature.setAttributes([i])
            ground_triangles.dataProvider().addFeature(feature)
    ground_triangles.updateExtents()
    params = {
        "COLUMN_PREFIX": "_",
        "INPUT": ground_triangles,
        "INPUT_RASTER": raster_layer,
        "OUTPUT": "TEMPORARY_OUTPUT",
        "RASTER_BAND": 1,
        "STATISTICS": [9],
    }
    res = processing.run("native:zonalstatisticsfb", params)
    if feedback.isCanceled():
        return
    res_layer = res["OUTPUT"]
    roughness_by_triangle = {
        ft["fid"]: round(ft["_majority"], 8) for ft in res_layer.getFeatures()
    }
    return roughness_by_triangle


def triangulate_roof(roof_layer, feedback):
    params = {"INPUT": roof_layer, "OUTPUT": "TEMPORARY_OUTPUT"}
    res = processing.run("3d:tessellate", params)
    if feedback.isCanceled():
        return

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
