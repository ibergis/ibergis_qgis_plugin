from qgis.core import QgsVectorLayer


def get_layer(dao, layer_name):
    path = f"{dao.db_filepath}|layername={layer_name}"
    return QgsVectorLayer(path, layer_name, "ogr")


def validate_layer(layer):
    if not layer.isValid():
        raise ValueError("Layer is not valid.")
    if not all(
        type(feature["cellsize"]) in [int, float] and feature["cellsize"] > 0
        for feature in layer.getFeatures()
    ):
        raise ValueError("Invalid values in column cellsize.")
