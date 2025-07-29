"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from functools import partial
import os

from qgis.PyQt.QtWidgets import QTableView, QSizePolicy, QLineEdit, \
    QApplication, QShortcut, QMenu, QAction
from qgis.PyQt.QtGui import QKeySequence, QIcon, QDoubleValidator
from qgis.core import QgsFeature, QgsEditFormConfig, QgsProject, QgsMapLayer, QgsCoordinateTransform, QgsPointXY
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
from qgis.gui import QgsMapToolIdentifyFeature

from ...ui.ui_manager import DrBridgeUi
from ...utils.matplotlib_widget import MplCanvas
from ...utils import tools_dr
from ....lib import tools_qgis, tools_qt, tools_db
from .... import global_vars
from typing import Optional
from ....core.toolbars.dialog import DrAction
from ....core.utils.item_delegates import NumericDelegate, NumericTableWidgetItem


class PlotParameters:
    """ Class to store plot parameters """
    # MAIN
    X_LABEL = 'Distance (m)'
    Y_LABEL = 'Elevation (m)'
    TITLE = 'Bridge Profile'
    GRID_ENABLED = True
    GRID_ALPHA = 0.3
    LEGEND_LOC = 3
    LEGEND_LABELSPACING = 0.1
    LEGEND_FONTSIZE = 8
    # Error
    ERROR_TEXT_COLOR = 'black'
    ERROR_BACKGROUND_COLOR = '#a11d00'
    # Info
    INFO_TEXT_COLOR = 'black'

    # Bridge
    TOPELEV_MARKER_COLOR = "x"
    LOWELEV_MARKER_COLOR = "x"
    TOPELEV_LINE_COLOR = '#001246'
    LOWELEV_LINE_COLOR = '#003dec'
    ELEVATION_FILL_COLOR = 'gray'
    # DEM
    DEM_LINE_COLOR = 'green'
    GROUND_FILL_COLOR = '#a16900'


class DrBridgeButton(DrAction):

    TOPELEV_DEFAULT = 10
    LOWELEV_DEFAULT = 8
    DECK_DEFAULT = 1.7
    FREEFLOW_DEFAULT = 0.6
    SUMERGEFLOW_DEFAULT = 0.8
    GAUGENUMBER_DEFAULT = 1

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        """ Class to control 'Add element' of toolbar 'edit' """

        if toolbar is not None:
            toolbar.removeAction(self.action)

        self.plugin_dir = global_vars.plugin_dir
        self.iface = global_vars.iface
        self.canvas = global_vars.canvas
        self.dialog = None
        self.manager_dlg = None
        self.plot_widget = None
        self.current_bridge = None
        self.toolbar = toolbar

        self.menu = QMenu()
        self.menu.setObjectName('bridge_menu')
        self._fill_bridge_menu()

        self.menu.aboutToShow.connect(self._fill_bridge_menu)

        if toolbar is not None:
            self.action.setMenu(self.menu)
            toolbar.addAction(self.action)

    def clicked_event(self):
        # Get the widget for this action (the button)
        button = self.toolbar.widgetForAction(self.action) if self.toolbar is not None else None
        if not self.menu.isVisible():
            if button is not None:
                # Show the menu below the button
                self.menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def manage_bridge(self, bridge: Optional[QgsFeature] = None, is_new: bool = False):
        """ Opens Bridge dialog. Called from 'Bridge add' button and 'Bridge edit' button. """

        # Store the bridge feature for DEM sampling
        self.current_bridge = bridge

        # Get dialog
        self.dialog = DrBridgeUi()
        tools_dr.load_settings(self.dialog)

        # Add button icons
        tools_dr.add_icon(self.dialog.btn_add, '111', '24x24')
        tools_dr.add_icon(self.dialog.btn_del, '112', '24x24')

        # Configure placeholders
        line_texts = {
            'txt_deck': str(self.DECK_DEFAULT),
            'txt_freeflow': str(self.FREEFLOW_DEFAULT),
            'txt_sumergeflow': str(self.SUMERGEFLOW_DEFAULT),
            'txt_gaugenumber': str(self.GAUGENUMBER_DEFAULT)
        }
        for line_name, line_text in line_texts.items():
            self.dialog.findChild(QLineEdit, line_name).setPlaceholderText(line_text)

        # Add profile widget first (needed for plotting)
        self.add_profile_widget(self.dialog)

        # Fill bridge fields
        if bridge is not None and not is_new:
            self._fill_fields(bridge)

        if bridge is not None and is_new:
            self.dialog.txt_length.setText(str(round(bridge.geometry().length(), 3)))

        # Set scale-to-fit and fill table
        tools_qt.set_tableview_config(self.dialog.tbl_bridge_value, sectionResizeMode=1, edit_triggers=QTableView.DoubleClicked)
        # Fill table
        self._fill_table(self.dialog.tbl_bridge_value, bridge, is_new)

        # Fill dem files combobox
        all_layers = QgsProject.instance().mapLayers().values()
        raster_layers = [layer for layer in all_layers if layer.type() == QgsMapLayer.RasterLayer]
        self.dialog.cmb_dem.clear()
        self.dialog.cmb_dem.addItems([layer.name() for layer in raster_layers])

        # Connect dialog signals
        self.dialog.btn_cancel.clicked.connect(self.dialog.reject)
        self.dialog.btn_accept.clicked.connect(partial(self.accept_bridge, self.dialog, bridge, is_new))
        self.dialog.btn_add.clicked.connect(partial(self._manage_table, self.dialog, bridge, True))
        self.dialog.btn_del.clicked.connect(partial(self._manage_table, self.dialog, bridge, False))
        self.dialog.finished.connect(partial(self.close_dialog, self.dialog))
        self.dialog.tbl_bridge_value.itemChanged.connect(partial(self._onItemChanged, self.dialog.tbl_bridge_value))
        self.dialog.chk_dem.stateChanged.connect(partial(self._update_bridge_profile_plot, self.dialog.tbl_bridge_value))
        self.dialog.cmb_dem.currentIndexChanged.connect(partial(self._update_bridge_profile_plot, self.dialog.tbl_bridge_value))

        # Connect paste shortcut
        paste_shortcut = QShortcut(QKeySequence.Paste, self.dialog.tbl_bridge_value)
        paste_shortcut.activated.connect(partial(self._paste_bridge_values, self.dialog.tbl_bridge_value))

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='bridge')

        # Update profile plot after filling table
        self._update_bridge_profile_plot(self.dialog.tbl_bridge_value)

    def add_profile_widget(self, dialog):
        """ Add profile widget """
        plot_widget = MplCanvas(dialog, width=8, height=3, dpi=100)
        plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_widget.setMinimumSize(200, 150)
        plot_widget.setMaximumHeight(300)
        dialog.lyt_plot.addWidget(plot_widget, 0, 0)
        self.plot_widget = plot_widget

    def close_dialog(self, dialog):
        """ Close dialog """

        # Stop editing bridge layer
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            tools_qgis.show_warning("Bridge layer not found.")
            return

        if bridge_layer.isEditable():
            bridge_layer.rollBack()

        global_vars.gpkg_dao_data.rollback()

        tools_dr.close_dialog(dialog)

    def edit_bridge(self):
        """ Edit bridge """

        # Return if theres one bridge dialog already open
        if self.dialog is not None:
            try:
                if self.dialog.isVisible():
                    # Bring the existing dialog to the front
                    self.dialog.setWindowState(self.dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                    self.dialog.raise_()
                    self.dialog.show()
                    self.dialog.activateWindow()
                    tools_qgis.show_warning("There's a Bridge dialog already open.", dialog=self.dialog)
                    return
            except RuntimeError:
                pass

        # Show info message
        msg = "Select a bridge to edit."
        tools_qgis.show_info(msg)

        # Get bridge layer
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            msg = "Bridge layer not found. Please make sure the bridge layer is loaded in your project."
            tools_qt.show_info_box(msg)
            self.bridge_edit_action.setChecked(False)
            return

        # Set up map tool for bridge selection
        canvas = iface.mapCanvas()
        self.feature_identifier = QgsMapToolIdentifyFeature(canvas)
        self.feature_identifier.setLayer(bridge_layer)
        self.feature_identifier.featureIdentified.connect(self._on_bridge_selected)
        self.lastMapTool = canvas.mapTool()
        canvas.mapToolSet.connect(self._uncheck)
        canvas.setMapTool(self.feature_identifier)

    def accept_bridge(self, dialog, bridge: Optional[QgsFeature] = None, is_new: bool = False):
        """ Manage accept button (insert & update) """

        if bridge is None:
            msg = "Bridge not found"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Variables
        txt_code = dialog.txt_code
        txt_deck = dialog.txt_deck
        txt_freeflow = dialog.txt_freeflow
        txt_sumergeflow = dialog.txt_sumergeflow
        txt_gaugenumber = dialog.txt_gaugenumber
        txt_length = dialog.txt_length
        txt_descript = dialog.txt_descript

        # Get widget values
        code = tools_qt.get_text(dialog, txt_code, add_quote=False)
        deck = tools_qt.get_text(dialog, txt_deck, add_quote=False)
        freeflow = tools_qt.get_text(dialog, txt_freeflow, add_quote=False)
        sumergeflow = tools_qt.get_text(dialog, txt_sumergeflow, add_quote=False)
        gaugenumber = tools_qt.get_text(dialog, txt_gaugenumber, add_quote=False)
        length = tools_qt.get_text(dialog, txt_length, add_quote=False)
        descript = tools_qt.get_text(dialog, txt_descript, add_quote=False)

        values = {
            'deck': deck,
            'freeflow': freeflow,
            'sumergeflow': sumergeflow,
            'gaugenumber': gaugenumber,
            'length': length,
            'descript': descript,
            'geom': f"ST_GeomFromText('{bridge.geometry().asWkt()}')"
        }

        for key, value in values.items():
            if key not in ('geom', 'descript'):
                try:
                    values[key] = float(value)
                except ValueError:
                    if value != 'null':
                        msg = "Invalid value '{0}'."
                        msg_params = (value,)
                        tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
                        return
                    else:
                        values[key] = 'null'

        # Map dictionary keys to database column names
        column_mapping = {
            'deck': 'deck_cd',
            'freeflow': 'freeflow_cd',
            'sumergeflow': 'sumergeflow_cd',
            'gaugenumber': 'gaugenumber',
            'length': 'length',
            'descript': 'descript',
            'geom': 'geom'
        }

        # Map default values
        default_values = {
            'deck': self.DECK_DEFAULT,
            'freeflow': self.FREEFLOW_DEFAULT,
            'sumergeflow': self.SUMERGEFLOW_DEFAULT,
            'gaugenumber': self.GAUGENUMBER_DEFAULT
        }

        # Insert or update
        if is_new:
            # Insert - only include non-null values
            columns = []
            column_values = []

            for key, value in values.items():
                if value != 'null':
                    columns.append(column_mapping[key])
                    # Handle string values that need quotes
                    if key == 'geom':
                        column_values.append(value)
                    elif isinstance(value, str) and not value.replace('.', '').replace('-', '').isdigit():
                        column_values.append(f"'{value}'")
                    else:
                        column_values.append(str(value))

            if not columns:
                msg = "At least one field must have a value."
                tools_qgis.show_warning(msg, dialog=dialog)
                return

            # Get bridge layer and roll back the new qgis feature to avoid duplicated features
            bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
            if bridge_layer is None:
                tools_qgis.show_warning("Bridge layer not found.")
                return

            if bridge_layer.isEditable():
                bridge_layer.rollBack()

            deck = default_values['deck']
            freeflow = default_values['freeflow']
            sumergeflow = default_values['sumergeflow']
            gaugenumber = default_values['gaugenumber']

            # Insert bridge
            columns_str = ', '.join(columns)
            values_str = ', '.join(column_values)
            sql = f"INSERT INTO bridge ({columns_str}) VALUES ({values_str})"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting bridge."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Get the generated id
            sql = "SELECT last_insert_rowid();"
            row = tools_db.get_row(sql, commit=False)
            if not row:
                msg = "There was an error getting the generated bridge id."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            id = row[0]

            # Get the generated code (should be updated by trigger)
            sql = f"SELECT code, length FROM bridge WHERE fid = {id}"
            row = tools_db.get_row(sql, commit=False)
            if not row:
                msg = "There was an error getting the generated bridge code."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            code = row[0]
            length = row[1]

            # Insert bridge_value
            result = self._insert_bridge_value(dialog, dialog.tbl_bridge_value, code, float(length))
            if not result:
                global_vars.gpkg_dao_data.rollback()
                return
        else:
            # Update - only include non-null values
            set_clauses = []
            for key, value in values.items():
                # Handle string values that need quotes
                if key == 'geom':
                    set_clauses.append(f"{column_mapping[key]} = {value}")
                elif value == 'null' and key != 'descript':
                    set_clauses.append(f"{column_mapping[key]} = {default_values[key]}")
                elif isinstance(value, str) and not value.replace('.', '').replace('-', '').isdigit() and value != 'null':
                    set_clauses.append(f"{column_mapping[key]} = '{value}'")
                else:
                    set_clauses.append(f"{column_mapping[key]} = {value}")

            set_clause_str = ', '.join(set_clauses)
            sql = f"UPDATE bridge SET {set_clause_str} WHERE code = '{code}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error updating bridge."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Update bridge_value
            sql = f"DELETE FROM bridge_value WHERE bridge_code = '{code}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old bridge values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            result = self._insert_bridge_value(dialog, dialog.tbl_bridge_value, code, float(length))
            if not result:
                global_vars.gpkg_dao_data.rollback()
                return

        # Commit
        global_vars.gpkg_dao_data.commit()

        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            tools_qgis.show_warning("Bridge layer not found.")
            return
        bridge_layer.dataProvider().reloadData()
        bridge_layer.triggerRepaint()

        # Reload manager table
        tools_dr.close_dialog(dialog)

    def add_bridge(self):
        """ Add bridge interactively by drawing a linestring and then opening the bridge dialog. """

        # Return if theres one bridge dialog already open
        if self.dialog is not None:
            try:
                if self.dialog.isVisible():
                    # Bring the existing dialog to the front
                    self.dialog.setWindowState(self.dialog.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                    self.dialog.raise_()
                    self.dialog.show()
                    self.dialog.activateWindow()
                    tools_qgis.show_warning("There's a Bridge dialog already open.", dialog=self.dialog)
                    return
            except RuntimeError:
                pass

        # Show info message
        msg = "Draw a linestring to define the bridge and then use right click to finish the drawing."
        tools_qgis.show_info(msg)

        # Get the bridge layer
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            tools_qgis.show_warning("Bridge layer not found.")
            return

        # Store previous form suppression setting
        config = bridge_layer.editFormConfig()
        self._conf_supp = config.suppress()
        config.setSuppress(QgsEditFormConfig.FeatureFormSuppress.SuppressOn)  # SuppressOn
        bridge_layer.setEditFormConfig(config)

        # Start editing and trigger add feature tool
        global_vars.iface.setActiveLayer(bridge_layer)
        bridge_layer.startEditing()
        global_vars.iface.actionAddFeature().trigger()

        # Connect to featureAdded signal
        bridge_layer.featureAdded.connect(self._on_bridge_feature_added)

    # region private functions

    def _show_empty_plot(self, text: str = '', is_error: bool = False):
        """ Show empty plot with instructions for new bridges """

        if self.plot_widget is None:
            return

        # Clear previous plot
        self.plot_widget.axes.clear()

        # Show instructions
        if is_error:
            self.plot_widget.axes.text(0.5, 0.5, text,
                            ha='center', va='center', transform=self.plot_widget.axes.transAxes,
                            fontsize=12, color=PlotParameters.ERROR_TEXT_COLOR, zorder=5, fontweight='bold', bbox=dict(facecolor=PlotParameters.ERROR_BACKGROUND_COLOR, alpha=0.9))
        else:
            self.plot_widget.axes.text(0.5, 0.5, text,
                            ha='center', va='center', transform=self.plot_widget.axes.transAxes,
                            fontsize=12, color=PlotParameters.INFO_TEXT_COLOR)

        # Set basic plot properties
        self.plot_widget.axes.set_xlabel(PlotParameters.X_LABEL)
        self.plot_widget.axes.set_ylabel(PlotParameters.Y_LABEL)
        self.plot_widget.axes.set_title(PlotParameters.TITLE)
        self.plot_widget.axes.grid(PlotParameters.GRID_ENABLED, alpha=PlotParameters.GRID_ALPHA)

        # Set reasonable default limits
        self.plot_widget.axes.set_xlim(0, 100)
        self.plot_widget.axes.set_ylim(0, 10)

        # Refresh the plot
        self.plot_widget.draw()

    def _interpolate_dem_at_distance(self, distance, dem_distances, dem_values):
        """ Interpolate DEM value at a specific distance """

        if not dem_distances or not dem_values or len(dem_distances) != len(dem_values):
            return 0

        # If distance is exactly at a sampled point
        if distance in dem_distances:
            idx = dem_distances.index(distance)
            return dem_values[idx]

        # Find the two closest points for interpolation
        if distance < dem_distances[0]:
            return dem_values[0]
        if distance > dem_distances[-1]:
            return dem_values[-1]

        # Find the two points that bracket the distance
        for i in range(len(dem_distances) - 1):
            if dem_distances[i] <= distance <= dem_distances[i + 1]:
                # Linear interpolation
                d1, d2 = dem_distances[i], dem_distances[i + 1]
                v1, v2 = dem_values[i], dem_values[i + 1]
                if d2 - d1 > 0:
                    ratio = (distance - d1) / (d2 - d1)
                    return v1 + ratio * (v2 - v1)
                else:
                    return v1

        return 0

    def _get_dem_profile_along_bridge(self):
        """ Get DEM profile along the bridge geometry at regular intervals """

        try:
            # Get the selected DEM layer name
            dem_layer_name = self.dialog.cmb_dem.currentText()

            # Find the DEM layer
            project = QgsProject.instance()
            dem_layer = None
            if dem_layer_name:
                for layer in project.mapLayers().values():
                    if layer.name() == dem_layer_name and layer.type() == QgsMapLayer.RasterLayer:
                        dem_layer = layer
                        break

            if dem_layer is None:
                return [], []

            # Use the stored bridge feature
            if self.current_bridge is None:
                return [], []

            # Get bridge geometry
            bridge_geom = self.current_bridge.geometry()
            if bridge_geom is None:
                return [], []

            # Get bridge length
            bridge_length = bridge_geom.length()
            if bridge_length <= 0:
                return [], []

            # Set up coordinate transformation if needed
            bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
            if bridge_layer is None:
                return [], []

            bridge_crs = bridge_layer.crs()
            dem_crs = dem_layer.crs()
            transform = None
            if bridge_crs != dem_crs:
                transform = QgsCoordinateTransform(bridge_crs, dem_crs, QgsProject.instance())

            # Sample DEM at regular intervals every distance_increment
            dem_distances = []
            dem_values = []

            distance: float = 0
            distance_increment: float = 0.5
            while distance <= bridge_length:
                # Get point along the bridge at this distance
                point_along_line = bridge_geom.interpolate(distance)
                if point_along_line is None:
                    break

                # Transform coordinates if needed
                if transform:
                    point_along_line.transform(transform)

                # Sample the DEM at this point
                point_xy = QgsPointXY(point_along_line.asPoint())
                val, res = dem_layer.dataProvider().sample(point_xy, 1)

                # Use the DEM value if successful, otherwise use 0
                if res:
                    dem_value = val
                else:
                    return [], []

                dem_distances.append(distance)
                dem_values.append(dem_value)

                if distance < bridge_length and (distance + distance_increment) > bridge_length:
                    distance = bridge_length
                else:
                    distance += distance_increment

            return dem_distances, dem_values

        except Exception as e:
            tools_qgis.show_warning(f"Error sampling DEM: {str(e)}")
            return [], []

    def _update_bridge_profile_plot(self, table):
        """ Update bridge profile plot with current table data """

        if self.plot_widget is None:
            return

        # Enable/disable dem combo box
        if self.dialog.chk_dem.isChecked():
            self.dialog.cmb_dem.setEnabled(True)
        else:
            self.dialog.cmb_dem.setEnabled(False)

        # Clear previous plot
        self.plot_widget.axes.clear()

        # Extract data from table
        valid_values = True
        incoherent_top_low_elevs = True
        distances = []
        topelevs = []
        lowelevs = []
        openingvals = []

        for row in range(table.rowCount()):
            # Skip empty rows
            if (table.item(row, 0) is None or table.item(row, 0).data(0) in (None, '')) and \
                (table.item(row, 1) is None or table.item(row, 1).data(0) in (None, '')) and \
                (table.item(row, 2) is None or table.item(row, 2).data(0) in (None, '')) and \
                (table.item(row, 3) is None or table.item(row, 3).data(0) in (None, '')):
                continue

            # Get distance (column 0)
            distance_item = table.item(row, 0)
            if distance_item is not None and distance_item.data(0) not in (None, ''):
                try:
                    distance = float(distance_item.data(0))
                except ValueError:
                    valid_values = False
                    break
            else:
                valid_values = False
                break

            # Get topelev (column 1)
            topelev_item = table.item(row, 1)
            topelev = 0.0
            if topelev_item is not None and topelev_item.data(0) not in (None, ''):
                try:
                    topelev = float(topelev_item.data(0))
                except ValueError:
                    valid_values = False
                    break
            else:
                valid_values = False
                break

            # Get lowelev (column 2)
            lowelev_item = table.item(row, 2)
            lowelev = 0.0
            if lowelev_item is not None and lowelev_item.data(0) not in (None, ''):
                try:
                    lowelev = float(lowelev_item.data(0))
                except ValueError:
                    valid_values = False
                    break
            else:
                valid_values = False
                break

            # Get openingval (column 3)
            openingval_item = table.item(row, 3)
            openingval = 100.0  # Default value
            if openingval_item is not None and openingval_item.data(0) not in (None, ''):
                try:
                    openingval = float(openingval_item.data(0))
                except ValueError:
                    valid_values = False
                    break
            else:
                valid_values = False
                break

            if topelev < lowelev:
                incoherent_top_low_elevs = False

            distances.append(distance)
            topelevs.append(topelev)
            lowelevs.append(lowelev)
            openingvals.append(openingval)

        if not valid_values:
            self._show_empty_plot('Invalid values in the table', is_error=True)
            return

        if not incoherent_top_low_elevs:
            text = 'There are incoherent top and low elevations'
            self.plot_widget.axes.text(0.5, 0.5, text,
                            ha='center', va='center', transform=self.plot_widget.axes.transAxes,
                            fontsize=12, color=PlotParameters.ERROR_TEXT_COLOR, zorder=5, fontweight='bold', bbox=dict(facecolor=PlotParameters.ERROR_BACKGROUND_COLOR, alpha=0.9))

        # Only plot if we have valid data
        if len(distances) < 2:
            self.plot_widget.axes.text(0.5, 0.5, 'Add at least 2 points\nto see the profile',
                                     ha='center', va='center', color=PlotParameters.INFO_TEXT_COLOR, transform=self.plot_widget.axes.transAxes)
            self.plot_widget.draw()
            return

        # Sort data by distance
        sorted_data = sorted(zip(distances, topelevs, lowelevs, openingvals))
        distances, topelevs, lowelevs, openingvals = zip(*sorted_data)

        # Get DEM data if checkbox is checked
        dem_error = False
        dem_distances = []
        dem_values = []
        if self.dialog.chk_dem.isChecked() and self.dialog.cmb_dem.currentText():
            dem_distances, dem_values = self._get_dem_profile_along_bridge()
            if len(dem_distances) < 2 or len(dem_values) < 2:
                dem_error = True
                dem_distances = []
                dem_values = []

        if dem_error and self.dialog.chk_dem.isChecked():
            self._show_empty_plot('Invalid DEM data', is_error=True)

        # Process data to add bridge columns when openingval is 0
        processed_distances = []
        processed_topelevs = []
        processed_lowelevs = []
        processed_openingvals = []

        # Check if any elevations are invalid
        has_invalid_elevations = False
        for dist, top, low, opening in sorted_data:
            dem_elev = self._interpolate_dem_at_distance(dist, dem_distances, dem_values)
            if dem_elev > top or dem_elev > low:
                has_invalid_elevations = True
                break

        # Process all points with consistent elevation source
        for i, (dist, top, low, opening) in enumerate(sorted_data):
            # Add the original point
            processed_distances.append(dist)
            processed_topelevs.append(top)
            processed_lowelevs.append(low)
            processed_openingvals.append(opening)

            # If openingval is 0, add bridge column points
            if opening == 0:
                # Use 0 for all bridge columns if any elevations are invalid, otherwise use DEM
                if has_invalid_elevations:
                    column_elev = 0
                else:
                    column_elev = self._interpolate_dem_at_distance(dist, dem_distances, dem_values)

                # Add point with lowelev = column_elev at same distance
                processed_distances.append(dist)
                processed_topelevs.append(top)
                processed_lowelevs.append(column_elev)
                processed_openingvals.append(0)

                # Add point with lowelev = column_elev at next distance (if not last point)
                if i < len(sorted_data) - 1:
                    next_dist: float = sorted_data[i + 1][0]
                    next_top: float = sorted_data[i + 1][1]
                    if has_invalid_elevations:
                        next_column_elev = 0
                    else:
                        next_column_elev = self._interpolate_dem_at_distance(next_dist, dem_distances, dem_values)

                    processed_distances.append(next_dist)
                    processed_topelevs.append(next_top)
                    processed_lowelevs.append(next_column_elev)
                    processed_openingvals.append(0)

        # Plot DEM line first (background)
        if not dem_error and self.dialog.chk_dem.isChecked():
            label = 'DEM Ground'
            self.plot_widget.axes.plot(dem_distances, dem_values, color=PlotParameters.DEM_LINE_COLOR, linewidth=2, label=label, alpha=0.7, zorder=1)
            self.plot_widget.axes.fill_between(dem_distances, dem_values, 0, alpha=0.6, color=PlotParameters.GROUND_FILL_COLOR, zorder=2)

        # Plot the bridge lines on top
        self.plot_widget.axes.plot(processed_distances, processed_topelevs, color=PlotParameters.TOPELEV_LINE_COLOR, linewidth=1.5, label='Top Elevation', marker=PlotParameters.TOPELEV_MARKER_COLOR, markersize=3, zorder=3)
        self.plot_widget.axes.plot(processed_distances, processed_lowelevs, color=PlotParameters.LOWELEV_LINE_COLOR, linewidth=1.5, label='Low Elevation', marker=PlotParameters.LOWELEV_MARKER_COLOR, markersize=3, zorder=3)

        # Fill area between top and low elevation and between ground and 0
        self.plot_widget.axes.fill_between(processed_distances, processed_lowelevs, processed_topelevs, alpha=0.5, color=PlotParameters.ELEVATION_FILL_COLOR, zorder=2)

        # Customize plot
        self.plot_widget.axes.set_xlabel(PlotParameters.X_LABEL)
        self.plot_widget.axes.set_ylabel(PlotParameters.Y_LABEL)
        self.plot_widget.axes.set_title(PlotParameters.TITLE)
        self.plot_widget.axes.legend(loc=PlotParameters.LEGEND_LOC, labelspacing=PlotParameters.LEGEND_LABELSPACING, fontsize=PlotParameters.LEGEND_FONTSIZE)
        self.plot_widget.axes.grid(PlotParameters.GRID_ENABLED, alpha=PlotParameters.GRID_ALPHA)

        # Reduce padding around the plot
        self.plot_widget.figure.tight_layout(pad=1)  # Reduce padding around the entire figure

        # Set reasonable axis limits with rectangular aspect
        if processed_distances:
            all_elevs = list(topelevs) + list(lowelevs)
            if dem_values:
                all_elevs.extend(dem_values)
            all_distances = list(distances)

            if self.dialog.chk_dem.isChecked():
                # Calculate data ranges
                x_min, x_max = min(all_distances), max(all_distances)
                y_min, y_max = min(all_elevs), max(all_elevs)
                x_range = x_max - x_min
                y_range = y_max - y_min

                # Add a small margin (5% of range, or 1 if range is 0)
                x_margin = x_range * 0.05 if x_range > 0 else 1
                y_margin = y_range * 0.05 if y_range > 0 else 1

                self.plot_widget.axes.set_xlim(x_min - x_margin, x_max + x_margin)
                self.plot_widget.axes.set_ylim(y_min - y_margin, y_max + y_margin)
                self.plot_widget.axes.set_aspect('equal', adjustable='datalim')
            else:
                x_range = max(processed_distances) - min(processed_distances)
                y_range = max(all_elevs) - min(all_elevs) if all_elevs else 10

                # Add margins
                x_margin = x_range * 0.02 if x_range > 0 else 1
                y_margin = y_range * 0.1 if y_range > 0 else 1

                # Calculate centers for both axes
                x_center = (min(processed_distances) + max(processed_distances)) / 2
                y_center = (min(all_elevs) + max(all_elevs)) / 2 if all_elevs else 5

                # Set ranges centered on the data with margins
                self.plot_widget.axes.set_xlim(x_center - x_range / 2 - x_margin, x_center + x_range / 2 + x_margin)
                self.plot_widget.axes.set_ylim(((y_center - y_range / 2 - y_margin) - 10), (y_center + y_range / 2 + y_margin) + 1)
                self.plot_widget.axes.set_aspect('auto')

        # Refresh the plot
        self.plot_widget.draw()

    def _fill_table(self, widget, bridge, is_new: bool = False):
        """ Fill bridge table """

        # Set delegate for table
        widget.setItemDelegateForColumn(0, NumericDelegate(parent=widget, min_value=-100000, max_value=100000, step=0.1, decimals=3))
        widget.setItemDelegateForColumn(1, NumericDelegate(parent=widget, min_value=-100000, max_value=100000, step=1, decimals=3))
        widget.setItemDelegateForColumn(2, NumericDelegate(parent=widget, min_value=-100000, max_value=100000, step=1, decimals=3))
        widget.setItemDelegateForColumn(3, NumericDelegate(parent=widget, min_value=0, max_value=100, step=1, decimals=2))

        for row in range(widget.rowCount()):
            widget.removeRow(row)

        # Insert default rows
        if is_new:
            widget.insertRow(0)
            widget.setItem(0, 0, NumericTableWidgetItem('0.0'))
            widget.setItem(0, 1, NumericTableWidgetItem(str(self.TOPELEV_DEFAULT)))
            widget.setItem(0, 2, NumericTableWidgetItem(str(self.LOWELEV_DEFAULT)))
            widget.setItem(0, 3, NumericTableWidgetItem('100'))
            widget.insertRow(1)
            widget.setItem(1, 0, NumericTableWidgetItem(str(round(bridge.geometry().length(), 3))))
            widget.setItem(1, 1, NumericTableWidgetItem(str(self.TOPELEV_DEFAULT)))
            widget.setItem(1, 2, NumericTableWidgetItem(str(self.LOWELEV_DEFAULT)))
            widget.setItem(1, 3, NumericTableWidgetItem('100'))
            return

        # Populate table timeseries_values
        sql = f"SELECT id, distance, topelev, lowelev, openingval FROM bridge_value WHERE bridge_code = '{bridge['code']}'"
        rows = tools_db.get_rows(sql)
        if not rows:
            return

        row0, row1, row2, row3 = 'distance', 'topelev', 'lowelev', 'openingval'

        headers_rel_dict = {'distance': 1, 'topelev': 2, 'lowelev': 3, 'openingval': 4}
        default_line_texts = {
            'topelev': '0.0',
            'lowelev': '0.0',
            'openingval': '100'
        }

        # Insert rows
        for n, row in enumerate(rows):
            widget.insertRow(widget.rowCount())
            value = f"{row[headers_rel_dict.get(row0)]}"
            if value in (None, 'None', 'null'):
                value = ''
            widget.setItem(n, 0, NumericTableWidgetItem(value))
            value = f"{row[headers_rel_dict.get(row1)]}"
            if value in (None, 'None', 'null'):
                value = default_line_texts['topelev']
            widget.setItem(n, 1, NumericTableWidgetItem(value))
            value = f"{row[headers_rel_dict.get(row2)]}"
            if value in (None, 'None', 'null'):
                value = default_line_texts['lowelev']
            widget.setItem(n, 2, NumericTableWidgetItem(value))
            value = f"{row[headers_rel_dict.get(row3)]}"
            if value in (None, 'None', 'null'):
                value = default_line_texts['openingval']
            widget.setItem(n, 3, NumericTableWidgetItem(value))

    def _paste_bridge_values(self, tbl_bridge_value):
        """ Paste bridge values from clipboard """

        selected = tbl_bridge_value.selectedRanges()
        if not selected:
            return

        text = QApplication.clipboard().text()
        rows = text.split("\n")

        for r, row in enumerate(rows):
            columns = row.split("\t")
            for c, value in enumerate(columns):
                item = NumericTableWidgetItem(value)
                row_pos = selected[0].topRow() + r
                col_pos = selected[0].leftColumn() + c
                tbl_bridge_value.setItem(row_pos, col_pos, item)

        # Update plot after pasting data
        self._update_bridge_profile_plot(tbl_bridge_value)

    def _fill_bridge_menu(self):
        """ Fill bridge menu """

        self.menu.clear()

        # Add bridge add action
        self.bridge_add_action = QAction("Add Bridge", self.menu)
        self.bridge_add_action.triggered.connect(self.add_bridge)
        self.bridge_add_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'main', '219.png')))
        self.bridge_edit_action = QAction("Edit Bridge", self.menu)
        self.bridge_edit_action.triggered.connect(self.edit_bridge)
        self.bridge_edit_action.setIcon(QIcon(os.path.join(self.plugin_dir, 'icons', 'toolbars', 'main', '220.png')))
        self.bridge_edit_action.setCheckable(True)

        self.menu.addAction(self.bridge_add_action)
        self.menu.addAction(self.bridge_edit_action)

    def _on_bridge_feature_added(self, feature_id: int):
        """Callback when a new bridge feature is added interactively."""
        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            return
        try:
            bridge_layer.featureAdded.disconnect(self._on_bridge_feature_added)
        except Exception:
            pass
        feature = tools_qt.get_feature_by_id(bridge_layer, feature_id)
        if feature is None:
            return
        # Restore previous form suppression
        config = bridge_layer.editFormConfig()
        config.setSuppress(self._conf_supp)
        bridge_layer.setEditFormConfig(config)
        # Open the bridge dialog with the new feature
        self.manage_bridge(feature, True)

    def _onItemChanged(self, table, item):
        # Update profile plot
        self._update_bridge_profile_plot(table)

    def _fill_fields(self, bridge):
        """ Fill bridge fields """

        if self.dialog is None:
            return

        bridge_fields = {
            'txt_code': bridge['code'],
            'txt_deck': bridge['deck_cd'],
            'txt_freeflow': bridge['freeflow_cd'],
            'txt_sumergeflow': bridge['sumergeflow_cd'],
            'txt_gaugenumber': bridge['gaugenumber'],
            'txt_length': bridge['length'],
            'txt_descript': bridge['descript']
        }

        for field_name, field_value in bridge_fields.items():
            if field_value in (None, 'None', 'null', 'NULL'):
                field_value = ''
            self.dialog.findChild(QLineEdit, field_name).setText(str(field_value))
            if field_name not in ('txt_code', 'txt_descript'):
                self.dialog.findChild(QLineEdit, field_name).setValidator(QDoubleValidator())

    def _insert_bridge_value(self, dialog, tbl_bridge_value, code, length):
        """ Insert bridge value """

        # Get table values
        values = list()
        distances = list()
        for y in range(0, tbl_bridge_value.rowCount()):
            values.append(list())
            for x in range(0, tbl_bridge_value.columnCount()):
                value = ""
                item = tbl_bridge_value.item(y, x)
                if item is not None and item.data(0) not in (None, ''):
                    try:
                        value = float(item.data(0))
                        if x == 0:
                            distances.append(value)
                    except ValueError:
                        value = f"'{item.data(0)}'"
                values[y].append(value)

        # Check if table is empty
        is_empty = True
        if len(values) == 0:
            is_empty = True
        else:
            for row in values:
                if row == (['null'] * tbl_bridge_value.columnCount()):
                    continue
                is_empty = False

        if is_empty or len(distances) < 2:
            msg = "You need at least start(0) and end({0}) points."
            msg_params = (str(length),)
            tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
            return False

        # Check if distances are valid
        if len(distances) != len(set(distances)):
            msg = "Distances must be unique."
            tools_qgis.show_warning(msg, dialog=dialog)
            return False
        for distance in distances:
            if distance < 0 or distance > length:
                msg = "Distances must be between 0 and the bridge length."
                tools_qgis.show_warning(msg, dialog=dialog)
                return False
        if 0 not in distances or length not in distances:
            msg = "Distances must include 0 and {0}."
            msg_params = (str(length),)
            tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
            return False

        for row in values:
            if row == (['null'] * tbl_bridge_value.columnCount()):
                continue

            for index, value in enumerate(row):
                if value == "":
                    msg = 'You have empty values.'
                    tools_qgis.show_warning(msg, dialog=dialog)
                    return False
                try:
                    row[index] = float(value)
                except ValueError:
                    msg = "Invalid value '{0}'."
                    msg_params = (value,)
                    tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
                    return False

            sql = "INSERT INTO bridge_value (bridge_code, distance"
            sql += ", topelev" if row[1] != 'null' else ""
            sql += ", lowelev" if row[2] != 'null' else ""
            sql += ", openingval" if row[3] != 'null' else ""
            sql += ") "
            sql += f"VALUES ('{code}'"
            sql += f", {row[0]}" if row[0] != 'null' else ""
            sql += f", {row[1]}" if row[1] != 'null' else ""
            sql += f", {row[2]}" if row[2] != 'null' else ""
            sql += f", {row[3]}" if row[3] != 'null' else ""
            sql += ")"

            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting pattern value."
                tools_qgis.show_warning(msg, dialog=dialog)
                return False

        return True

    def _on_bridge_selected(self, feature):
        """Callback when a bridge feature is selected on the map."""
        # Reset map tool
        iface.mapCanvas().setMapTool(self.lastMapTool)
        self.bridge_edit_action.setChecked(False)

        # Open bridge dialog with selected feature
        self.manage_bridge(feature)

    def _uncheck(self, old_tool):
        """Uncheck the button when map tool changes."""
        canvas = iface.mapCanvas()
        if canvas.mapTool() != self.feature_identifier:
            self.bridge_edit_action.setChecked(False)
            canvas.mapToolSet.disconnect(self._uncheck)

    def _manage_table(self, dialog, bridge: QgsFeature, is_add: bool):
        """ Manage table """

        selection_model = dialog.tbl_bridge_value.selectionModel()
        selected_rows = selection_model.selectedRows()
        if is_add:
            # Add a new row
            if dialog.tbl_bridge_value.rowCount() == 0:
                # Add a new default row
                dialog.tbl_bridge_value.insertRow(0)
                dialog.tbl_bridge_value.setItem(0, 0, NumericTableWidgetItem('0.0'))
                dialog.tbl_bridge_value.setItem(0, 1, NumericTableWidgetItem(str(self.TOPELEV_DEFAULT)))
                dialog.tbl_bridge_value.setItem(0, 2, NumericTableWidgetItem(str(self.LOWELEV_DEFAULT)))
                dialog.tbl_bridge_value.setItem(0, 3, NumericTableWidgetItem('100'))
                dialog.tbl_bridge_value.insertRow(1)
                dialog.tbl_bridge_value.setItem(1, 0, NumericTableWidgetItem(str(round(bridge.geometry().length(), 3))))
                dialog.tbl_bridge_value.setItem(1, 1, NumericTableWidgetItem(str(self.TOPELEV_DEFAULT)))
                dialog.tbl_bridge_value.setItem(1, 2, NumericTableWidgetItem(str(self.LOWELEV_DEFAULT)))
                dialog.tbl_bridge_value.setItem(1, 3, NumericTableWidgetItem('100'))
            elif len(selected_rows) == 1:
                # Add a new row after the selected row with the same values
                dialog.tbl_bridge_value.insertRow(selected_rows[0].row() + 1)
                item0 = dialog.tbl_bridge_value.item(selected_rows[0].row(), 0) if dialog.tbl_bridge_value.item(selected_rows[0].row(), 0) not in (None, '') else '0.0'
                item1 = dialog.tbl_bridge_value.item(selected_rows[0].row(), 1) if dialog.tbl_bridge_value.item(selected_rows[0].row(), 1) not in (None, '') else '0.0'
                item2 = dialog.tbl_bridge_value.item(selected_rows[0].row(), 2) if dialog.tbl_bridge_value.item(selected_rows[0].row(), 2) not in (None, '') else '0.0'
                item3 = dialog.tbl_bridge_value.item(selected_rows[0].row(), 3) if dialog.tbl_bridge_value.item(selected_rows[0].row(), 3) not in (None, '') else '100'
                dialog.tbl_bridge_value.setItem(selected_rows[0].row() + 1, 0, NumericTableWidgetItem(item0))
                dialog.tbl_bridge_value.setItem(selected_rows[0].row() + 1, 1, NumericTableWidgetItem(item1))
                dialog.tbl_bridge_value.setItem(selected_rows[0].row() + 1, 2, NumericTableWidgetItem(item2))
                dialog.tbl_bridge_value.setItem(selected_rows[0].row() + 1, 3, NumericTableWidgetItem(item3))
            elif len(selected_rows) == 0:
                msg = "You have to select a row."
                tools_qgis.show_warning(msg, dialog=dialog)
                return
            else:
                msg = "You can only add one row at a time."
                tools_qgis.show_warning(msg, dialog=dialog)
                return
        else:
            # Delete selected rows
            if len(selected_rows) <= 0:
                msg = "You have to select at least one row."
                tools_qgis.show_warning(msg, dialog=dialog)
                return

            items = list()
            rows = list()
            for row in selected_rows:
                items.append(row.data(0))
                rows.append(int(row.row()))

            msg = "Are you sure you want to delete this rows{0}?"
            msg_params = (str(items),)
            response = tools_qt.show_question(msg, msg_params=msg_params, force_action=True)
            if response:
                for row in sorted(rows, reverse=True):
                    dialog.tbl_bridge_value.removeRow(row)

        self._update_bridge_profile_plot(dialog.tbl_bridge_value)

    # endregion