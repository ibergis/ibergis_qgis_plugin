import os
import re
import glob
import numpy as np
import rasterio
import xarray as xr
import rioxarray

# --- Configuration ---
input_folder = f'..{os.sep}example{os.sep}fullproject{os.sep}RasterResults{os.sep}.'  # Folder with .asc files
output_file = f'.{os.sep}resultsNCDF{os.sep}result.nc'

# Regex patterns for each variable type
regex_patterns = {
    "Depth": re.compile(r"Depth_+([\d.]+)\.asc$"),
    "Velocity": re.compile(r"Velocity_+([\d.]+)\.asc$"),
    "Velocity_x": re.compile(r"Velocity__x_([\d.]+)\.asc$"),
    "Velocity_y": re.compile(r"Velocity__y_([\d.]+)\.asc$")
}

# --- Load variable data ---
datasets = {}

for var, pattern in regex_patterns.items():
    files = []
    times = []

    for filepath in glob.glob(os.path.join(input_folder, "*.asc")):
        filename = os.path.basename(filepath)
        match = pattern.match(filename)
        if match:
            time_value = float(match.group(1))
            files.append((time_value, filepath))
            times.append(time_value)

    files.sort()
    times.sort()

    if not files:
        print(f"[!] No files found for {var}")
        continue

    print(f"[+] Loading {var} ({len(files)} files)...")

    data_array = []

    for i, (time_value, filepath) in enumerate(files):
        with rasterio.open(filepath) as src:
            array = src.read(1)

            # Extract metadata from the first file
            if i == 0:
                transform = src.transform
                crs = "EPSG:25831"  # ← set your CRS manually here
                height, width = array.shape

            data_array.append(array)

    # Temporal stack (t, y, x)
    stacked = np.stack(data_array, axis=0)

    # Spatial coordinates
    y_coords = np.arange(height) * transform[4] + transform[5]
    x_coords = np.arange(width) * transform[0] + transform[2]

    da = xr.DataArray(
        stacked,
        dims=["time", "y", "x"],
        coords={
            "time": [t for t, _ in files],
            "y": y_coords,
            "x": x_coords
        },
        name=var
    )

    # Assign CRS to each variable
    da.rio.write_crs(crs, inplace=True)

    datasets[var] = da

# --- Create final Dataset ---
ds = xr.Dataset(datasets)

# --- Save as NetCDF ---
ds.to_netcdf(output_file)
print(f"[✓] NetCDF saved as {output_file}")