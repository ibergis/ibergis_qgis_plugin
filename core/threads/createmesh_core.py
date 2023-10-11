from qgis.core import QgsFeature, QgsVectorLayer, QgsField
from qgis.PyQt.QtCore import QVariant


def create_mesh_dict(triangulations_list):
    mesh = {"triangles": {}, "vertices": {}}
    next_triangle_id = 1
    next_vertice_id = 1

    # The first element is ground
    category = "ground"

    for triangles, vertices in triangulations_list:
        for i, triangle in enumerate(triangles, start=next_triangle_id):
            vertice_ids = [int(triangle[v] + next_vertice_id) for v in (0, 1, 2, 0)]
            mesh["triangles"][i] = {"category": category, "vertice_ids": vertice_ids}
            next_triangle_id = i + 1

        for i, vertice in enumerate(vertices, start=next_vertice_id):
            mesh["vertices"][i] = {"coordinates": (vertice)}
            next_vertice_id = i + 1

        # All the other elements are roof
        category = "roof"

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


def get_layer(dao, layer_name):
    path = f"{dao.db_filepath}|layername={layer_name}"
    return QgsVectorLayer(path, layer_name, "ogr")


def join_layers(iterable):
    joined_layer = next(iterable).clone()
    for layer in iterable:
        joined_layer.startEditing()
        joined_layer.addFeatures(layer.getFeatures())
        joined_layer.commitChanges()
    joined_layer.updateExtents()
    return joined_layer


def validate_input_layers(layers_dict):
    error_layers = []

    # Validate ground layer
    # 1. Verify cellsize values
    ground_cellsize_layer = QgsVectorLayer(
        "Polygon", "ground: Invalid cellsize", "memory"
    )
    ground_cellsize_layer.setCrs(layers_dict["ground"].crs())
    provider = ground_cellsize_layer.dataProvider()
    provider.addAttributes(
        [
            QgsField("fid", QVariant.Int),
            QgsField("cellsize", QVariant.Double),
        ]
    )
    ground_cellsize_layer.updateFields()
    ground_cellsize_layer.startEditing()
    for feature in layers_dict["ground"].getFeatures():
        cellsize = feature["cellsize"]
        if type(cellsize) in [int, float] and cellsize > 0:
            continue
        invalid_feature = QgsFeature(ground_cellsize_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
        invalid_feature.setGeometry(feature.geometry())
        ground_cellsize_layer.addFeature(invalid_feature)
    ground_cellsize_layer.commitChanges()
    if ground_cellsize_layer.hasFeatures():
        error_layers.append(ground_cellsize_layer)

    return error_layers
