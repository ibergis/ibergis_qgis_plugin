"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from typing import List, Optional, Dict, Tuple
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
except ImportError:
    plt = None
    mdates = None
    Figure = None
    FigureCanvasQTAgg = None

try:
    from swmm_api import read_out_file
    from swmm_api.output_file.definitions import OBJECTS, VARIABLES
except ImportError:
    read_out_file = None
    OBJECTS = None
    VARIABLES = None


# Map UI variable names to swmm-api variable names
VARIABLE_MAPPING = {
    'Subcatchment': {
        'Precipitation': VARIABLES.SUBCATCHMENT.RAINFALL if VARIABLES else 'rainfall',
        'Snow Depth': VARIABLES.SUBCATCHMENT.SNOW_DEPTH if VARIABLES else 'snow_depth',
        'Evaporation': VARIABLES.SUBCATCHMENT.EVAPORATION if VARIABLES else 'evaporation',
        'Infiltration': VARIABLES.SUBCATCHMENT.INFILTRATION if VARIABLES else 'infiltration',
        'Runoff': VARIABLES.SUBCATCHMENT.RUNOFF if VARIABLES else 'runoff',
        'GW Flow': VARIABLES.SUBCATCHMENT.GW_OUTFLOW if VARIABLES else 'groundwater_outflow',
        'GW Elev.': VARIABLES.SUBCATCHMENT.GW_ELEVATION if VARIABLES else 'groundwater_elevation',
        'Soil Moisture': VARIABLES.SUBCATCHMENT.SOIL_MOISTURE if VARIABLES else 'soil_moisture',
    },
    'Node': {
        'Depth': VARIABLES.NODE.DEPTH if VARIABLES else 'depth',
        'Head': VARIABLES.NODE.HEAD if VARIABLES else 'head',
        'Volume': VARIABLES.NODE.VOLUME if VARIABLES else 'volume',
        'Lateral Inflow': VARIABLES.NODE.LATERAL_INFLOW if VARIABLES else 'lateral_inflow',
        'Total Inflow': VARIABLES.NODE.TOTAL_INFLOW if VARIABLES else 'total_inflow',
        'Flooding': VARIABLES.NODE.FLOODING if VARIABLES else 'flooding',
    },
    'Link': {
        'Flow': VARIABLES.LINK.FLOW if VARIABLES else 'flow',
        'Depth': VARIABLES.LINK.DEPTH if VARIABLES else 'depth',
        'Velocity': VARIABLES.LINK.VELOCITY if VARIABLES else 'velocity',
        'Volume': VARIABLES.LINK.VOLUME if VARIABLES else 'volume',
        'Capacity': VARIABLES.LINK.CAPACITY if VARIABLES else 'capacity',
    },
    'System': {
        'Temperature': VARIABLES.SYSTEM.AIR_TEMPERATURE if VARIABLES else 'air_temperature',
        'Precipitation': VARIABLES.SYSTEM.RAINFALL if VARIABLES else 'rainfall',
        'Snow Depth': VARIABLES.SYSTEM.SNOW_DEPTH if VARIABLES else 'snow_depth',
        'Infiltration': VARIABLES.SYSTEM.INFILTRATION if VARIABLES else 'infiltration',
        'Runoff': VARIABLES.SYSTEM.RUNOFF if VARIABLES else 'runoff',
        'DW Inflow': VARIABLES.SYSTEM.DW_INFLOW if VARIABLES else 'dry_weather_inflow',
        'GW Inflow': VARIABLES.SYSTEM.GW_INFLOW if VARIABLES else 'groundwater_inflow',
        'I&I Inflow': VARIABLES.SYSTEM.RDII_INFLOW if VARIABLES else 'RDII_inflow',
        'Direct Inflow': VARIABLES.SYSTEM.DIRECT_INFLOW if VARIABLES else 'direct_inflow',
        'Total Inflow': VARIABLES.SYSTEM.LATERAL_INFLOW if VARIABLES else 'lateral_inflow',
        'Flooding': VARIABLES.SYSTEM.FLOODING if VARIABLES else 'flooding',
        'Outflow': VARIABLES.SYSTEM.OUTFLOW if VARIABLES else 'outflow',
        'Storage': VARIABLES.SYSTEM.VOLUME if VARIABLES else 'volume',
        'Evaporation': VARIABLES.SYSTEM.EVAPORATION if VARIABLES else 'evaporation',
        'PET': VARIABLES.SYSTEM.PET if VARIABLES else 'PET',
    }
}

# Map UI object types to swmm-api object types
OBJECT_TYPE_MAPPING = {
    'Subcatchment': OBJECTS.SUBCATCHMENT if OBJECTS else 'subcatchment',
    'Node': OBJECTS.NODE if OBJECTS else 'node',
    'Link': OBJECTS.LINK if OBJECTS else 'link',
    'System': OBJECTS.SYSTEM if OBJECTS else 'system',
}


class DataSeries:
    """Class to hold data series information"""

    def __init__(self, object_type: Optional[str], object_name: Optional[str],
                 variable: Optional[str], legend_label: Optional[str], axis: str):
        self.object_type = object_type
        self.object_name = object_name
        self.variable = variable
        self.legend_label = legend_label
        self.axis = axis

    def get_swmm_object_type(self) -> Optional[str]:
        """Get the swmm-api object type"""
        if self.object_type:
            return OBJECT_TYPE_MAPPING.get(self.object_type)
        return None

    def get_swmm_variable(self) -> Optional[str]:
        """Get the swmm-api variable name"""
        if self.object_type and self.variable:
            return VARIABLE_MAPPING.get(self.object_type, {}).get(self.variable)
        return None

    def get_label(self) -> str:
        """Get the label for the legend"""
        if self.legend_label:
            return self.legend_label
        if self.object_type and self.object_name and self.variable:
            return f"{self.object_type} {self.object_name} - {self.variable}"
        return "Unknown"


class TimeseriesPlotter:
    """Class to handle extraction and plotting of timeseries data from SWMM output"""

    def __init__(self, output_file_path: str):
        """
        Initialize the timeseries plotter.

        Args:
            output_file_path: Path to the SWMM output file (.out)
        """
        if not read_out_file:
            raise ImportError("swmm-api package is not available")
        if not plt:
            raise ImportError("matplotlib package is not available")

        self.output_file_path = output_file_path
        self.swmm_output = None
        self.data_frame = None

    def load_output(self):
        """Load the SWMM output file"""
        if not os.path.exists(self.output_file_path):
            raise FileNotFoundError(f"Output file not found: {self.output_file_path}")

        try:
            self.swmm_output = read_out_file(self.output_file_path)
            self.data_frame = self.swmm_output.to_frame()
            print(self.data_frame)
        except Exception as e:
            raise RuntimeError(f"Failed to read output file: {e}")

    def extract_series_data(self, data_series: DataSeries,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Tuple[list, list]:
        """
        Extract timeseries data for a given DataSeries object.

        Args:
            data_series: DataSeries object with selection information
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Tuple of (time_values, data_values)
        """
        if self.data_frame is None:
            self.load_output()

        swmm_obj_type = data_series.get_swmm_object_type()
        swmm_variable = data_series.get_swmm_variable()

        if not swmm_obj_type or not swmm_variable:
            raise ValueError(f"Invalid object type or variable: {data_series.object_type}, {data_series.variable}")

        try:
            # For System type, object_name is empty
            if data_series.object_type == 'System':
                # System data has column structure: (object_type, '', variable)
                data = self.data_frame[(swmm_obj_type, '', swmm_variable)]
            else:
                # Other data has column structure: (object_type, object_name, variable)
                if not data_series.object_name:
                    raise ValueError(f"Object name is required for {data_series.object_type}")
                data = self.data_frame[(swmm_obj_type, data_series.object_name, swmm_variable)]

            # Filter by date range if provided
            if start_date:
                data = data[data.index >= start_date]
            if end_date:
                data = data[data.index <= end_date]

            time_values = data.index.to_list()
            data_values = data.values.tolist()

            return time_values, data_values

        except KeyError as e:
            raise KeyError(f"Could not find data for {data_series.object_type} '{data_series.object_name}' "
                          f"variable '{data_series.variable}': {e}")

    def create_plot(self, data_series_list: List[DataSeries],
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   use_elapsed_time: bool = True,
                   title: str = "Time Series Plot") -> Figure:
        """
        Create a matplotlib figure with the specified data series.

        Args:
            data_series_list: List of DataSeries objects to plot
            start_date: Optional start date filter
            end_date: Optional end date filter
            use_elapsed_time: If True, use elapsed time; if False, use date/time
            title: Plot title

        Returns:
            matplotlib Figure object
        """
        if not data_series_list:
            raise ValueError("No data series provided")

        # Create figure and axes
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = None

        # Separate series by axis
        left_series = [ds for ds in data_series_list if ds.axis == 'Left']
        right_series = [ds for ds in data_series_list if ds.axis == 'Right']

        # Create second y-axis if needed
        if right_series:
            ax2 = ax1.twinx()

        # Get simulation start time for elapsed time calculation
        sim_start_time = None
        if use_elapsed_time and self.swmm_output:
            sim_start_time = self.swmm_output.start_date

        # Plot left axis series
        for ds in left_series:
            try:
                time_values, data_values = self.extract_series_data(ds, start_date, end_date)

                if use_elapsed_time and sim_start_time:
                    # Convert to elapsed hours
                    time_values = [(t - sim_start_time).total_seconds() / 3600 for t in time_values]

                ax1.plot(time_values, data_values, label=ds.get_label(), linewidth=1.5)
            except Exception as e:
                print(f"Warning: Could not plot {ds.get_label()}: {e}")

        # Plot right axis series
        if ax2:
            for ds in right_series:
                try:
                    time_values, data_values = self.extract_series_data(ds, start_date, end_date)

                    if use_elapsed_time and sim_start_time:
                        # Convert to elapsed hours
                        time_values = [(t - sim_start_time).total_seconds() / 3600 for t in time_values]

                    ax2.plot(time_values, data_values, label=ds.get_label(), linewidth=1.5, linestyle='--')
                except Exception as e:
                    print(f"Warning: Could not plot {ds.get_label()}: {e}")

        # Configure axes
        ax1.set_xlabel('Elapsed Time (hours)' if use_elapsed_time else 'Date/Time')
        ax1.set_ylabel('Left Axis')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')

        if ax2:
            ax2.set_ylabel('Right Axis')
            ax2.legend(loc='upper right')

        # Format x-axis for date/time
        if not use_elapsed_time:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            fig.autofmt_xdate()

        ax1.set_title(title)
        fig.tight_layout()

        return fig

    def show_plot(self, data_series_list: List[DataSeries],
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  use_elapsed_time: bool = True,
                  title: str = "Time Series Plot"):
        """
        Create and show a matplotlib plot.

        Args:
            data_series_list: List of DataSeries objects to plot
            start_date: Optional start date filter
            end_date: Optional end date filter
            use_elapsed_time: If True, use elapsed time; if False, use date/time
            title: Plot title
        """
        fig = self.create_plot(data_series_list, start_date, end_date, use_elapsed_time, title)
        plt.show()

    def close(self):
        """Close the SWMM output file"""
        if self.swmm_output:
            try:
                self.swmm_output.close()
            except:
                pass

