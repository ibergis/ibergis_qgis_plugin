import os
import re
import sys
import glob
import numpy as np
import rasterio
import xarray as xr
from typing import List, Tuple, Optional
try:
    from qgis.PyQt.QtCore import pyqtSignal
except ImportError:
    pyqtSignal = None

#TODO import proj.db from qgis or packages. if its not imported, the script will use the postgres one which is on a lower version


def convert_asc_to_netcdf(input_folder: str, output_file: str, progress_changed: Optional[pyqtSignal]) -> None:
    if not os.path.exists(input_folder) and not os.path.isdir(input_folder):
        if progress_changed:
            progress_changed.emit('Export results', None, "Error: The rasters folder does not exist.", True)
        print("Error: The rasters folder does not exist.")
        return

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
        files: List[Tuple[float, str]] = []
        times: List[float] = []

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
            if progress_changed:
                progress_changed.emit('Export results', None, f"Error: No files found for {var}", True)
            print(f"Error: No files found for {var}")
            continue

        if progress_changed:
            progress_changed.emit('Export results', None, f"Loading {var} ({len(files)} files)...", True)
        print(f"Loading {var} ({len(files)} files)...")

        data_array = []

        for i, (time_value, filepath) in enumerate(files):
            with rasterio.open(filepath) as src:
                array = src.read(1)

                # Extract metadata from the first file
                if i == 0:
                    transform = src.transform
                    crs = "EPSG:25831"
                    height, width = array.shape

                data_array.append(array)

        # Temporal stack (t, y, x)
        stacked = np.stack(data_array, axis=0)

        # Spatial coordinates
        x_start = transform[2] - transform[0] / 2
        y_start = transform[5] - transform[4] / 2

        x_coords = x_start + np.arange(width) * transform[0]
        y_coords = y_start + np.arange(height) * transform[4]

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
        da.rio.write_transform(transform, inplace=True)

        datasets[var] = da

    if len(datasets) == 0:
        if progress_changed:
            progress_changed.emit('Export results', None, "Error: No data found in the dataset.", True)
        print("Error: No data found in the dataset.")
        return

    # --- Create final Dataset ---
    ds = xr.Dataset(datasets)

    # --- Save as NetCDF ---
    try:
        ds.to_netcdf(output_file)
    except Exception as e:
        if progress_changed:
            progress_changed.emit('Export results', None, f"Error: Error saving NetCDF file: {e}", True)
        print(f"Error: Error saving NetCDF file: {e}")
        return
    if progress_changed:
            progress_changed.emit('Export results', None, f"NetCDF file created successfully: {output_file}", True)
    print(f"NetCDF file created successfully: {output_file}")


if __name__ == "__main__":
    # Example usage
    input_folder = sys.argv[1] # Results folder with the rasters
    output_file = sys.argv[2] # Output NetCDF file
    convert_asc_to_netcdf(input_folder, output_file, None)