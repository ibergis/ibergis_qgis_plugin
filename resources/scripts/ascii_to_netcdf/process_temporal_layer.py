"""
Module to configure temporal properties for raster layers with time-based bands.
This is designed to be called from execute_model.py after importing NetCDF results.
"""
import datetime
import re
from qgis.core import (
    QgsRasterLayer,
    QgsTemporalController,
    QgsDateTimeRange,
    QgsRasterDataProvider,
    QgsRasterBandStats,
    QgsStyle,
    QgsSingleBandPseudoColorRenderer,
    QgsColorRampShader,
    QgsRasterLayerTemporalProperties,
    QgsInterval,
    Qgis
)
from qgis.PyQt.QtCore import QDateTime, Qt
from typing import Optional, Tuple


def configure_temporal_layer(
    layer: QgsRasterLayer,
    iface,
    start_date: str = '2025:1:1',
    start_time: str = '0:0:0',
    frames_per_second: int = 10
) -> Tuple[bool, str]:
    """
    Configure temporal properties for a raster layer with time-based bands.
    
    Args:
        layer: The QgsRasterLayer to configure
        iface: QGIS interface object
        start_date: Start date in format 'yyyy:m:d'
        start_time: Start time in format 'h:m:s'
        frames_per_second: Animation speed (typically 10 or 25)
    
    Returns:
        Tuple of (success: bool, message: str)
    """

    if not layer or not isinstance(layer, QgsRasterLayer):
        return False, "ERROR: Invalid raster layer provided."

    try:
        max_elapsed_seconds = 0.0

        # Loop through all bands in the raster to find the maximum time
        for i in range(1, layer.bandCount() + 1):
            band_desc = layer.bandName(i)
            match = re.search(r"time=(\d+\.?\d*)", band_desc)

            if match:
                time_val_float = float(match.group(1))
                if time_val_float > max_elapsed_seconds:
                    max_elapsed_seconds = time_val_float

        # Compute minimum band time interval
        band_times = []

        for i in range(1, layer.bandCount() + 1):
            band_desc = layer.bandName(i)
            match = re.search(r"time=(\d+\.?\d*)", band_desc)

            if match:
                t = float(match.group(1))
                band_times.append(t)

        if len(band_times) < 2:
            return False, "ERROR: Not enough bands to compute animation step."

        band_times.sort()
        delta_times = [t2 - t1 for t1, t2 in zip(band_times, band_times[1:])]
        min_delta = min(delta_times)

        # Calculate the end datetime
        try:
            start_year, start_month, start_day = map(int, start_date.split(':'))
            start_hour, start_min, start_sec = map(int, start_time.split(':'))
            start_datetime = datetime.datetime(start_year, start_month, start_day, start_hour, start_min, start_sec)

            duration = datetime.timedelta(seconds=max_elapsed_seconds)
            end_datetime = start_datetime + duration

            dt_dict = {
                1: start_datetime.year, 2: start_datetime.month, 3: start_datetime.day,
                4: start_datetime.hour, 5: start_datetime.minute, 6: start_datetime.second,
                7: end_datetime.year, 8: end_datetime.month, 9: end_datetime.day,
                10: end_datetime.hour, 11: end_datetime.minute, 12: end_datetime.second,
            }

            # Apply settings to QGIS temporal controller
            temporal_controller = iface.mapCanvas().temporalController()
            q_start_datetime = QDateTime(start_datetime)
            q_end_datetime = QDateTime(end_datetime)
            animation_range = QgsDateTimeRange(q_start_datetime, q_end_datetime)

            temporal_controller.setTemporalExtents(animation_range)
            temporal_controller.setFrameDuration(QgsInterval(min_delta))
            temporal_controller.setNavigationMode(Qgis.TemporalNavigationMode.Animated)

            # Set fixed temporal range for the layer
            _setup_temporal_callbacks(iface, layer, dt_dict)

            return True, f"Temporal animation configured successfully. Min interval: {min_delta}s"

        except ValueError:
            return False, "ERROR: The start_date or start_time format is incorrect. Please use 'yyyy:m:d' and 'h:m:s'."

    except Exception as e:
        return False, f"ERROR: Failed to configure temporal layer: {str(e)}"


def _setup_temporal_callbacks(iface, layer: QgsRasterLayer, dt_dict: dict) -> None:
    """
    Set up temporal callbacks and fixed temporal range for the layer.
    
    Args:
        iface: QGIS interface object
        layer: The raster layer to configure
        dt_dict: Dictionary with datetime components
    """
    # Create callback function for temporal range changes
    def temporal_range_changed(t_range: QgsDateTimeRange):
        if isinstance(layer, QgsRasterLayer):
            _set_band_based_on_range(layer, t_range)

    # Connect temporal controller
    temporal_controller: QgsTemporalController = iface.mapCanvas().temporalController()
    temporal_controller.updateTemporalRange.connect(temporal_range_changed)

    # Set fixed temporal range
    start_dt = datetime.datetime(dt_dict[1], dt_dict[2], dt_dict[3], dt_dict[4], dt_dict[5], dt_dict[6])
    end_dt = datetime.datetime(dt_dict[7], dt_dict[8], dt_dict[9], dt_dict[10], dt_dict[11], dt_dict[12])
    _set_fixed_temporal_range(layer, QgsDateTimeRange(start_dt, end_dt))


# These functions are based on https://github.com/GispoCoding/qgis_plugin_tools/blob/master/tools/raster_layers.py

def _set_raster_renderer_to_singleband(layer: QgsRasterLayer, band: int = 1) -> None:
    """
    Set raster renderer to a dynamic singleband pseudocolor using the 'Turbo' color ramp.
    The ramp is stretched to the min/max values of the given band.
    """
    provider: QgsRasterDataProvider = layer.dataProvider()
    stats: QgsRasterBandStats = provider.bandStatistics(band, QgsRasterBandStats.All, layer.extent(), 0)
    min_val = stats.minimumValue
    max_val = stats.maximumValue

    style = QgsStyle.defaultStyle()
    ramp = style.colorRamp("Turbo")
    if not ramp:
        ramp = style.colorRamp("Viridis")

    renderer = QgsSingleBandPseudoColorRenderer(provider, band)
    renderer.setClassificationMin(min_val)
    renderer.setClassificationMax(max_val)
    renderer.createShader(ramp, QgsColorRampShader.Interpolated)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def _set_band_based_on_range(layer: QgsRasterLayer, t_range: QgsDateTimeRange) -> int:
    """
    Set the appropriate band based on the temporal range.

    :param layer: raster layer
    :param t_range: temporal range
    :return: band number
    """
    band_num = 1
    tprops: QgsRasterLayerTemporalProperties = layer.temporalProperties()
    if tprops.isVisibleInTemporalRange(t_range) and t_range.begin().isValid() and t_range.end().isValid():
        if tprops.mode() == QgsRasterLayerTemporalProperties.ModeFixedTemporalRange:
            layer_t_range: QgsDateTimeRange = tprops.fixedTemporalRange()
            start: datetime.datetime = layer_t_range.begin().toPyDateTime()
            end: datetime.datetime = layer_t_range.end().toPyDateTime()
            delta = (end - start) / layer.bandCount()
            band_num = int((t_range.begin().toPyDateTime() - start) / delta) + 1
            _set_raster_renderer_to_singleband(layer, band_num)
    return band_num


def _set_fixed_temporal_range(layer: QgsRasterLayer, t_range: QgsDateTimeRange) -> None:
    """
    Set fixed temporal range for raster layer.
    
    :param layer: raster layer
    :param t_range: fixed temporal range
    """
    mode = QgsRasterLayerTemporalProperties.ModeFixedTemporalRange
    tprops: QgsRasterLayerTemporalProperties = layer.temporalProperties()
    tprops.setMode(mode)
    if t_range.begin().timeSpec() == 0 or t_range.end().timeSpec() == 0:
        begin = t_range.begin()
        end = t_range.end()
        begin.setTimeSpec(Qt.TimeSpec(1))
        end.setTimeSpec(Qt.TimeSpec(1))
        t_range = QgsDateTimeRange(begin, end)
    tprops.setFixedTemporalRange(t_range)
    tprops.setIsActive(True)