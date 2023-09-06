from qgis.core import QgsVectorLayer

def get_layer(dao, layer_name):
  path = f"{dao.db_filepath}|layername={layer_name}"
  return QgsVectorLayer(path, layer_name, "ogr")