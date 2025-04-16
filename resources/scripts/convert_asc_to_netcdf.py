import os
import re
import glob
import numpy as np
import rasterio
import xarray as xr
import rioxarray

# --- Configuración ---
input_folder = f'..{os.sep}example{os.sep}fullproject{os.sep}RasterResults{os.sep}.'  # Carpeta con los .asc
output_file = f'.{os.sep}resultsNCDF{os.sep}modelo_resultados.nc'


# Regex por variable
regex_patterns = {
    "Depth": re.compile(r"Depth_+([\d.]+)\.asc$"),
    "Velocity": re.compile(r"Velocity_+([\d.]+)\.asc$"),
    "Velocity_x": re.compile(r"Velocity__x_([\d.]+)\.asc$"),
    "Velocity_y": re.compile(r"Velocity__y_([\d.]+)\.asc$")
}

# --- Cargar los datos por variable ---
datasets = {}

for var, patron in regex_patterns.items():
    archivos = []
    tiempos = []

    for filepath in glob.glob(os.path.join(input_folder, "*.asc")):
        filename = os.path.basename(filepath)
        match = patron.match(filename)
        if match:
            tiempo = float(match.group(1))
            archivos.append((tiempo, filepath))
            tiempos.append(tiempo)

    archivos.sort()
    tiempos.sort()

    if not archivos:
        print(f"[!] No se encontraron archivos para {var}")
        continue

    print(f"[+] Cargando {var} ({len(archivos)} archivos)...")

    data_array = []

    for i, (tiempo, filepath) in enumerate(archivos):
        with rasterio.open(filepath) as src:
            array = src.read(1)

            # Extraemos metadata del primero
            if i == 0:
                transform = src.transform
                crs = "EPSG:4326"  # ← aquí defines tu CRS manualmente
                height, width = array.shape

            data_array.append(array)

    # Stack temporal (t, y, x)
    stacked = np.stack(data_array, axis=0)

    # Coordenadas espaciales
    y_coords = np.arange(height) * transform[4] + transform[5]
    x_coords = np.arange(width) * transform[0] + transform[2]

    da = xr.DataArray(
        stacked,
        dims=["time", "y", "x"],
        coords={
            "time": [t for t, _ in archivos],
            "y": y_coords,
            "x": x_coords
        },
        name=var
    )

    # Asignar sistema de coordenadas a cada variable
    da.rio.write_crs(crs, inplace=True)

    datasets[var] = da

# --- Crear Dataset Final ---
ds = xr.Dataset(datasets)

# --- Guardar como NetCDF ---
ds.to_netcdf(output_file)
print(f"[✓] NetCDF guardado como {output_file}")