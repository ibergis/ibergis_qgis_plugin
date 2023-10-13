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


def validate_cellsize(layer):
    # Create layer
    layer_name = f"{layer.name()}: Invalid cellsize"
    errors_layer = QgsVectorLayer("Polygon", layer_name, "memory")
    errors_layer.setCrs(layer.crs())
    provider = errors_layer.dataProvider()
    fid_field = QgsField("fid", QVariant.Int)
    cellsize_field = QgsField("cellsize", QVariant.Double)
    provider.addAttributes([fid_field, cellsize_field])
    errors_layer.updateFields()

    # Fill layer with cellsize errors
    errors_layer.startEditing()
    for feature in layer.getFeatures():
        cellsize = feature["cellsize"]
        if type(cellsize) in [int, float] and cellsize > 0:
            continue
        invalid_feature = QgsFeature(errors_layer.fields())
        invalid_feature.setAttributes([feature["fid"], feature["cellsize"]])
        invalid_feature.setGeometry(feature.geometry())
        errors_layer.addFeature(invalid_feature)
    errors_layer.commitChanges()

    return errors_layer


def validate_input_layers(layers_dict):
    error_layers = []

    # Validate ground layer
    ground_cellsize_layer = validate_cellsize(layers_dict["ground"])
    if ground_cellsize_layer.hasFeatures():
        error_layers.append(ground_cellsize_layer)

    # Validate roof layer
    roof_cellsize_layer = validate_cellsize(layers_dict["roof"])
    if roof_cellsize_layer.hasFeatures():
        error_layers.append(roof_cellsize_layer)

    return error_layers
