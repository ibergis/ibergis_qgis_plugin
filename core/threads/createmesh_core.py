from qgis.core import QgsVectorLayer, QgsField


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

def validate_layer(layer):
    if not layer.isValid():
        raise ValueError("Layer is not valid.")
    if not all(
        type(feature["cellsize"]) in [int, float] and feature["cellsize"] > 0
        for feature in layer.getFeatures()
    ):
        raise ValueError("Invalid values in column cellsize.")
