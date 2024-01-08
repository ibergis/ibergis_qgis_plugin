from qgis import processing
from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtCore import QVariant


def create_mesh_dict(triangulations_list):
    mesh = {"polygons": {}, "vertices": {}, "boundary_conditions": {}}
    next_polygon_id = 1
    next_vertice_id = 1

    for polygons, vertices, metadata in triangulations_list:
        for i, polygon in enumerate(polygons, start=next_polygon_id):
            vertice_ids = [int(polygon[v] + next_vertice_id) for v in (0, 1, 2, 0)]
            mesh["polygons"][i] = {"vertice_ids": vertice_ids}
            mesh["polygons"][i].update(metadata)
            next_polygon_id = i + 1

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


def get_ground_losses(mesh_dict, ground_layer, feedback):
    # Copy ground_layer features to a new in-memory vector layer
    copied_layer = QgsVectorLayer(
        f"Polygon?crs={ground_layer.crs().authid()}", "copied_ground_layer", "memory"
    )
    copied_layer_data_provider = copied_layer.dataProvider()
    attrs = ground_layer.fields().toList()
    copied_layer_data_provider.addAttributes(attrs)
    copied_layer.updateFields()
    for feature in ground_layer.getFeatures():
        copied_layer_data_provider.addFeature(feature)
    copied_layer.updateExtents()

    resolution = 1
    e = copied_layer.extent()
    params = {
        "BURN": 0,
        "DATA_TYPE": 5,
        "EXTENT": f"{e.xMinimum()},{e.xMaximum()},{e.yMinimum()},{e.yMaximum()} [EPSG:25831]",
        "EXTRA": "",
        "FIELD": "scs_cn",
        "HEIGHT": resolution,
        "INIT": None,
        "INPUT": copied_layer,
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

    losses_by_polygon = get_value_from_raster(
        raster_layer, mesh_dict, ground_layer.crs(), feedback
    )

    return losses_by_polygon


def get_ground_roughness(mesh_dict, ground_layer, landuses, feedback):
    # Calculate concrete values for each roughness polygon
    # (landuse or custom_roughness)
    url = "MultiPolygon?index=yes"
    temp_roughness = QgsVectorLayer(url, "roughness", "memory")
    temp_roughness.setCrs(ground_layer.crs())
    provider = temp_roughness.dataProvider()
    fields = [
        QgsField("fid", QVariant.Int),
        QgsField("roughness", QVariant.Double),
    ]
    provider.addAttributes(fields)
    temp_roughness.updateFields()
    for feature in ground_layer.getFeatures():
        new_feature = QgsFeature()
        new_feature.setGeometry(feature.geometry())
        if type(feature["custom_roughness"]) in [int, float]:
            roughness = feature["custom_roughness"]
        else:
            roughness = landuses[int(feature["landuse"])]
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

    roughness_by_polygon = get_value_from_raster(
        raster_layer, mesh_dict, ground_layer.crs(), feedback
    )

    return roughness_by_polygon


def get_value_from_raster(raster_layer, mesh_dict, crs, feedback):
    url = "Polygon?field=fid:integer&index=yes"
    ground_polygons = QgsVectorLayer(url, "gt", "memory")
    ground_polygons.setCrs(crs)
    for i, pol in mesh_dict["polygons"].items():
        if feedback.isCanceled():
            return
        if pol["category"] == "ground":
            feature = QgsFeature()
            polygon_points = [
                QgsPointXY(*mesh_dict["vertices"][vert]["coordinates"])
                for vert in pol["vertice_ids"]
            ]
            feature.setGeometry(QgsGeometry.fromPolygonXY([polygon_points]))
            feature.setAttributes([i])
            ground_polygons.dataProvider().addFeature(feature)
    ground_polygons.updateExtents()
    params = {
        "COLUMN_PREFIX": "_",
        "INPUT": ground_polygons,
        "INPUT_RASTER": raster_layer,
        "OUTPUT": "TEMPORARY_OUTPUT",
        "RASTER_BAND": 1,
        "STATISTICS": [9],  # majority
    }
    res = processing.run("native:zonalstatisticsfb", params, feedback=feedback)
    if feedback.isCanceled():
        return
    res_layer = res["OUTPUT"]
    value_by_polygon = {
        ft["fid"]: round(ft["_majority"], 8) for ft in res_layer.getFeatures()
    }
    return value_by_polygon


def triangulate_roof(roof_layer, feedback):
    params = {"INPUT": roof_layer, "OUTPUT": "TEMPORARY_OUTPUT"}
    res = processing.run("3d:tessellate", params)
    if feedback.isCanceled():
        return

    roof_meshes = []
    for feature in res["OUTPUT"].getFeatures():
        geom = feature.geometry()
        vertices = [(v.x(), v.y()) for v in geom.vertices()]
        polygons = [
            [vertices.index((v.x(), v.y())) for v in polygon.vertices()]
            for polygon in geom.asGeometryCollection()
        ]
        roof_metadata = {
            "category": "roof",
            "roof_id": feature["fid"],
            "elevation": feature["elev"],
            "roughness": feature["roughness"],
        }
        roof_meshes.append((polygons, vertices, roof_metadata))

    return roof_meshes
