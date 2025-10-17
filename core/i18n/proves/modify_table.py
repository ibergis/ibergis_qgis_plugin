"""
This file is part of IberGIS
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import geopandas as gpd
import fiona

# Ruta al archivo GPKG
gpkg_path = "C:\\Users\\Usuario\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\drain_plugin\\core\\i18n\\drain_translations.gpkg"

try:
    layers = fiona.listlayers(gpkg_path)
    print("Capas disponibles en el GPKG:", layers)
except Exception as e:
    print("❌ Error al leer el GPKG:", e)

for layer in layers:
    # Leer el archivo GPKG y cargar la capa
    gdf_existing = gpd.read_file(gpkg_path, layer=layer)

    # Crear nuevos datos
    new_data = {
        'id': [1],
        'dialog_name': ['Dialog3'],
        'toolbar_name': ['Toolbar2'],
        'lb_en_us': ['Label 1']
    }

    # Crear un nuevo GeoDataFrame con el mismo CRS que el original
    gdf_new = gpd.GeoDataFrame(new_data)
    
    # Crear columna per mirar duplicats
    primary_keys = ['id', 'toolbar_name', 'dialog_name']
    gdf_existing['primary_key'] = gdf_existing[primary_keys].astype(str).agg('-'.join, axis=1)
    gdf_new['primary_key'] = gdf_new[primary_keys].astype(str).agg('-'.join, axis=1)

    # Filtrar las filas que no están en gdf_existing
    gdf_combined = gdf_existing[~gdf_existing['primary_key'].isin(gdf_new['primary_key'])]
    gdf_combined = gdf_combined._append(gdf_new, ignore_index=True)

    # Eliminar la columna 'primary_key' utilizada para la comparación
    gdf_combined = gdf_combined.drop(columns='primary_key')

    print(gdf_combined.head())

    # Guardar el GeoDataFrame combinado en el archivo GPKG
    gdf_combined = gpd.GeoDataFrame(gdf_combined)
    gdf_combined.to_file(gpkg_path, layer=layer, driver="GPKG")