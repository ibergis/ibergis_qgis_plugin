import os
import re
import sys
import glob
import numpy as np
import rasterio
import xarray as xr
from typing import List, Tuple, Optional, Any
from osgeo import gdal
from qgis.core import QgsProject
try:
    from qgis.PyQt.QtCore import pyqtSignal
except ImportError:
    pyqtSignal = None

# TODO import proj.db from qgis or packages. if its not imported, the script will use the postgres one which is on a lower version


def convert_asc_to_netcdf(input_folder: str, output_folder: str, result_names: list[str], progress_changed: Optional[Any], generate_cogs: bool = False) -> None:
    if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
        if progress_changed:
            progress_changed.emit('Export results', None, "Error: The rasters folder does not exist.", True)
        print("Error: The rasters folder does not exist.")
        return

    # Regex patterns for each variable type
    regex_patterns = {}
    for name in result_names:
        regex_patterns[name] = re.compile(f"{name}" + r"_+([\d.]+)\.asc$")

    # --- Process each variable separately ---
    created_files = []

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
                progress_changed.emit('Export results', None, f"Warning: No files found for {var}", True)
            print(f"Warning: No files found for {var}")
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
                    crs = QgsProject.instance().crs().authid() if QgsProject.instance().crs() else "EPSG:25831"
                    height, width = array.shape

                data_array.append(array)

        # Temporal stack (t, y, x)
        stacked = np.stack(data_array, axis=0)

        # Spatial coordinates
        x_start = transform[2] - transform[0] / 2
        y_start = transform[5] - transform[4] / 2

        x_coords = np.array(x_start + np.arange(width) * transform[0], dtype=np.float64)
        y_coords = np.array(y_start + np.arange(height) * transform[4], dtype=np.float64)
        time_coords = np.array([t for t, _ in files], dtype=np.float64)

        da = xr.DataArray(
            stacked.astype(np.float32),  # Ensure data is float32
            dims=["time", "y", "x"],
            coords={
                "time": time_coords,
                "y": y_coords,
                "x": x_coords
            },
            name=var
        )

        # Assign CRS to each variable
        da.rio.write_crs(crs, inplace=True)
        da.rio.write_transform(transform, inplace=True)

        # --- Create Dataset for this variable and save ---
        ds = xr.Dataset({var: da})

        # Generate output filename for this variable
        output_file = os.path.join(output_folder, f"{var}.nc")

        try:
            ds.to_netcdf(output_file)
            created_files.append(output_file)
            if progress_changed:
                progress_changed.emit('Export results', None, f"NetCDF file created successfully: {output_file}", True)
            print(f"NetCDF file created successfully: {output_file}")
        except Exception as e:
            if progress_changed:
                progress_changed.emit('Export results', None, f"Error: Error saving NetCDF file for {var}: {e}", True)
            print(f"Error: Error saving NetCDF file for {var}: {e}")

        if generate_cogs:
            output_cog = os.path.join(output_folder, f"{var}.tif")
            try:
                gdal.Translate(output_cog, output_file, format='COG', noData='-9999')
                if progress_changed:
                    progress_changed.emit('Export results', None, f"COG file created successfully: {output_cog}", True)
                print(f"COG file created successfully: {output_cog}")
            except Exception as e:
                if progress_changed:
                    progress_changed.emit('Export results', None, f"Error: Error creating COG file for {var}: {e}", True)
                print(f"Error: Error creating COG file for {var}: {e}")

    if len(created_files) == 0:
        if progress_changed:
            progress_changed.emit('Export results', None, "Error: No NetCDF files were created.", True)
        print("Error: No NetCDF files were created.")
        return

    if progress_changed:
        progress_changed.emit('Export results', None, f"Successfully created {len(created_files)} NetCDF files", True)
    print(f"Successfully created {len(created_files)} NetCDF files: {', '.join(created_files)}")


if __name__ == "__main__":
    # Example usage
    input_folder = sys.argv[1]  # Results folder with the rasters
    output_folder = sys.argv[2]  # Output NetCDF folder
    result_names = sys.argv[3]  # Result names
    convert_asc_to_netcdf(input_folder, output_folder, result_names, None)