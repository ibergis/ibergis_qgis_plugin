"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import webbrowser
from functools import partial

try:
    from scipy.interpolate import CubicSpline
    import numpy as np
    import json
    scipy_imported = True
except ImportError:
    scipy_imported = False

from qgis.PyQt.QtWidgets import QAbstractItemView, QTableView, QTableWidget, QTableWidgetItem, QSizePolicy, QLineEdit, \
    QGridLayout, QComboBox, QApplication, QShortcut, QTextEdit, QHeaderView
from qgis.PyQt.QtGui import QKeySequence
from qgis.PyQt.QtSql import QSqlTableModel
from qgis.core import Qgis
from qgis.PyQt.QtCore import QTime, QDate, Qt
from ..ui.ui_manager import DrNonVisualManagerUi, DrNonVisualControlsUi, DrNonVisualCurveUi, DrNonVisualPatternUDUi, \
    DrNonVisualTimeseriesUi, DrNonVisualLidsUi, DrNonVisualRasterUi, DrNonVisualRasterImportUi
from ..utils.matplotlib_widget import MplCanvas
from ..utils import tools_dr
from ...lib import tools_qgis, tools_qt, tools_db, tools_os
from ... import global_vars
from typing import Optional


class DrNonVisual:

    def __init__(self):
        """ Class to control 'Add element' of toolbar 'edit' """

        self.plugin_dir = global_vars.plugin_dir
        self.iface = global_vars.iface
        self.canvas = global_vars.canvas
        self.dialog = None
        self.manager_dlg = None
        self.dict_views = {'cat_curve': 'curves',
                           'cat_pattern': 'patterns',
                           'cat_timeseries': 'timeseries',
                           'cat_controls': 'controls',
                           'cat_raster': 'rasters',
                           }
        self.dict_ids = {'cat_curve': 'idval', 'cat_curve_value': 'curve',
                         'cat_pattern': 'idval', 'cat_pattern_value': 'pattern',
                         'cat_controls': 'id',
                         'cat_timeseries': 'idval', 'cat_timeseries_value': 'timeseries',
                         'cat_raster': 'idval', 'cat_raster_value': 'raster',
                         }
        self.valid = (True, "")

    def get_nonvisual(self, object_name):
        """ Opens Non-Visual object dialog. Called from 'New Non-Visual object' button. """

        if object_name is None:
            return

        # Execute method get_{object_name}
        getattr(self, f'get_{object_name.lower()}')()

    # region manager
    def manage_nonvisual(self):
        """ Opens Non-Visual objects manager. Called from 'Non-Visual object manager' button. """

        # Get dialog
        self.manager_dlg = DrNonVisualManagerUi()
        tools_dr.load_settings(self.manager_dlg)

        # Show import button if current tab is rasters
        tab_name = self.manager_dlg.main_tab.tabText(self.manager_dlg.main_tab.currentIndex())
        if tab_name == 'Rasters':
            self.manager_dlg.btn_import.setVisible(True)
        else:
            self.manager_dlg.btn_import.setVisible(False)

        # Make and populate tabs
        self._manage_tabs_manager()

        # Connect dialog signals
        self.manager_dlg.txt_filter.textChanged.connect(partial(self._filter_table, self.manager_dlg))
        self.manager_dlg.main_tab.currentChanged.connect(partial(self._filter_table, self.manager_dlg, None))
        self.manager_dlg.btn_duplicate.clicked.connect(partial(self._duplicate_object, self.manager_dlg))
        self.manager_dlg.btn_create.clicked.connect(partial(self._create_object, self.manager_dlg))
        self.manager_dlg.btn_delete.clicked.connect(partial(self._delete_object, self.manager_dlg))
        self.manager_dlg.btn_cancel.clicked.connect(self.manager_dlg.reject)
        self.manager_dlg.btn_import.clicked.connect(partial(self._import_rasters, self.manager_dlg))
        self.manager_dlg.finished.connect(partial(tools_dr.close_dialog, self.manager_dlg))

        # Open dialog
        tools_dr.open_dialog(self.manager_dlg, dlg_name='nonvisual_manager')

    def _manage_tabs_manager(self):
        """ Creates and populates manager tabs """

        dict_views_project = self.dict_views
        for key in dict_views_project.keys():
            qtableview = QTableView()
            qtableview.setObjectName(f"tbl_{dict_views_project[key]}")
            tab_idx = self.manager_dlg.main_tab.addTab(qtableview, f"{dict_views_project[key].capitalize()}")
            self.manager_dlg.main_tab.widget(tab_idx).setObjectName(key)
            self.manager_dlg.main_tab.widget(tab_idx).setProperty('function', f"get_{dict_views_project[key]}")
            function_name = f"get_{dict_views_project[key]}"

            self._fill_manager_table(qtableview, key)

            qtableview.doubleClicked.connect(partial(self._get_nonvisual_object, qtableview, function_name))

    def _get_nonvisual_object(self, tbl_view, function_name):
        """ Opens Non-Visual object dialog. Called from manager tables. """

        object_id = tbl_view.selectionModel().selectedRows()[0].data()
        if hasattr(self, function_name):
            getattr(self, function_name)(object_id)

    def _fill_manager_table(self, widget, table_name, set_edit_triggers=QTableView.EditTrigger.NoEditTriggers, expr=None):
        """ Fills manager table """

        # Set model
        model = QSqlTableModel(db=global_vars.db_qsql_data)
        model.setTable(table_name)
        model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        model.setSort(0, Qt.SortOrder.AscendingOrder)
        model.select()

        # Check for errors
        if model.lastError().isValid():
            tools_qgis.show_warning(model.lastError().text(), dialog=self.manager_dlg)
        # Attach model to table view
        if expr:
            widget.setModel(model)
            widget.model().setFilter(expr)
        else:
            widget.setModel(model)
        widget.setSortingEnabled(True)

        # Set widget & model properties
        tools_qt.set_tableview_config(widget, selection=QAbstractItemView.SelectionBehavior.SelectRows, edit_triggers=set_edit_triggers,
                                      sectionResizeMode=QHeaderView.ResizeMode.Fixed, stretchLastSection=True)
        # tools_dr.set_tablemodel_config(self.manager_dlg, widget, table_name)

        # Sort the table by feature id
        model.sort(1, Qt.SortOrder.AscendingOrder)

    def _filter_table(self, dialog, text):
        """ Filters manager table by id """

        widget_table = dialog.main_tab.currentWidget()
        tablename = widget_table.objectName()
        id_field = self.dict_ids.get(tablename, 'idval')
        tab_name = dialog.main_tab.tabText(dialog.main_tab.currentIndex())

        # Show import button if current tab is rasters
        if tab_name == 'Rasters':
            dialog.btn_import.setVisible(True)
        else:
            dialog.btn_import.setVisible(False)

        if text is None:
            text = tools_qt.get_text(dialog, dialog.txt_filter, return_string_null=False)

        expr = f"CAST({id_field} AS TEXT) LIKE '%{text}%'"
        # Refresh model with selected filter
        widget_table.model().setFilter(expr)
        widget_table.model().select()

    def _create_object(self, dialog):
        """ Creates a new non-visual object from the manager """

        table = dialog.main_tab.currentWidget()
        function_name = table.property('function')
        getattr(self, function_name)()

    def _duplicate_object(self, dialog):
        """ Duplicates the selected object """

        # Variables
        table = dialog.main_tab.currentWidget()
        function_name = table.property('function')

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            msg = "Any record selected"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Get selected workspace id
        index = table.selectionModel().currentIndex()
        value = index.sibling(index.row(), 0).data()

        try:
            value = int(value)
        except ValueError:
            pass

        # Open dialog with values but no id
        getattr(self, function_name)(value, duplicate=True)

    def _delete_object(self, dialog):
        """ Deletes selected object and its values """

        # Variables
        table = dialog.main_tab.currentWidget()
        tablename = table.objectName()
        tablename_value = f"{tablename}_value"

        # Get selected row
        selected_list = table.selectionModel().selectedRows()
        if len(selected_list) == 0:
            msg = "Any record selected"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Get selected object IDs
        col = self.dict_ids.get(tablename)
        col_idx = tools_qt.get_col_index_by_col_name(table, col)
        if not col_idx:
            col_idx = 0
        id_list = []
        values = []
        for idx in selected_list:
            value = idx.sibling(idx.row(), col_idx).data()
            id_list.append(value)

        msg = "Are you sure you want to delete these records?"
        answer = tools_qt.show_question(msg, "Delete records", id_list)
        if answer:
            # Add quotes to id if not inp_controls/inp_rules
            if tablename not in ('inp_controls', 'inp_rules'):
                for value in id_list:
                    values.append(f"'{value}'")

            # Delete values
            id_field = self.dict_ids.get(tablename_value)
            if id_field is not None:
                for value in values:
                    sql = f"DELETE FROM {tablename_value} WHERE {id_field} = {value}"
                    print(sql)
                    result = tools_db.execute_sql(sql, commit=False)
                    if not result:
                        msg = "There was an error deleting object values."
                        tools_qgis.show_warning(msg, dialog=dialog)
                        global_vars.gpkg_dao_data.rollback()
                        return

            # Delete object from main table
            for value in values:
                id_field = self.dict_ids.get(tablename)
                sql = f"DELETE FROM {tablename} WHERE {id_field} = {value}"
                print(sql)
                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error deleting object."
                    tools_qgis.show_warning(msg, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return

            # Commit & refresh table
            global_vars.gpkg_dao_data.commit()
            self._reload_manager_table()

    # endregion

    # region curves
    def get_curves(self, curve=None, duplicate=False):
        """ Opens dialog for curve """

        # Get dialog
        self.dialog = DrNonVisualCurveUi()
        tools_dr.load_settings(self.dialog)

        # Create plot widget
        plot_widget = self._create_plot_widget(self.dialog)

        # Define variables
        tbl_curve_value = self.dialog.tbl_curve_value
        cmb_curve_type = self.dialog.cmb_curve_type

        paste_shortcut = QShortcut(QKeySequence.Paste, tbl_curve_value)
        paste_shortcut.activated.connect(partial(self._paste_curve_values, tbl_curve_value))

        # Create & fill cmb_curve_type
        curve_type_headers, curve_type_list = self._create_curve_type_lists()
        if curve_type_list:
            tools_qt.fill_combo_values(cmb_curve_type, curve_type_list)

        # Populate data if editing curve
        tools_qt.set_widget_text(self.dialog, self.dialog.txt_curve, curve)
        tools_qt.set_widget_enabled(self.dialog, self.dialog.txt_curve, False)
        if curve:
            self._populate_curve_widgets(curve, duplicate=duplicate)
        else:
            self._load_curve_widgets(self.dialog)

        # Treat as new object if curve is None or if we're duplicating
        is_new = (curve is None) or duplicate

        # Connect dialog signals
        cmb_curve_type.currentIndexChanged.connect(partial(self._manage_curve_type, self.dialog, curve_type_headers, tbl_curve_value))
        tbl_curve_value.cellChanged.connect(partial(self._onCellChanged, tbl_curve_value))
        tbl_curve_value.cellChanged.connect(partial(self._manage_curve_value, self.dialog, tbl_curve_value))
        tbl_curve_value.cellChanged.connect(partial(self._manage_curve_plot, self.dialog, tbl_curve_value, plot_widget))
        self.dialog.btn_accept.clicked.connect(partial(self._accept_curves, self.dialog, is_new))
        self._connect_dialog_signals()

        # Set initial curve_value table headers
        self._manage_curve_type(self.dialog, curve_type_headers, tbl_curve_value, 0)
        self._manage_curve_plot(self.dialog, tbl_curve_value, plot_widget, None, None)
        # Set scale-to-fit
        tools_qt.set_tableview_config(tbl_curve_value, sectionResizeMode=QHeaderView.ResizeMode.Stretch, edit_triggers=QTableView.EditTrigger.DoubleClicked)

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='nonvisual_curve')

    def _paste_curve_values(self, tbl_curve_value):
        selected = tbl_curve_value.selectedRanges()
        if not selected:
            return

        text = QApplication.clipboard().text()
        rows = text.split("\n")

        for r, row in enumerate(rows):
            columns = row.split("\t")
            for c, value in enumerate(columns):
                item = QTableWidgetItem(value)
                row_pos = selected[0].topRow() + r
                col_pos = selected[0].leftColumn() + c
                tbl_curve_value.setItem(row_pos, col_pos, item)

    def _create_curve_type_lists(self):
        """ Creates a list & dict to manage curve_values table headers """

        curve_type_list = []
        curve_type_headers = {}
        sql = "SELECT id, idval, addparam FROM edit_typevalue WHERE typevalue = 'inp_curve_type'"
        rows = tools_db.get_rows(sql)

        if rows:
            curve_type_list = [[row[0], row[1]] for row in rows]
            curve_type_headers = {row[0]: json.loads(row[2]).get('header') for row in rows}

        return curve_type_headers, curve_type_list

    def _populate_curve_widgets(self, curve, duplicate=False):
        """ Fills in all the values for curve dialog """

        # Variables
        txt_name = self.dialog.txt_curve_name
        txt_descript = self.dialog.txt_descript
        cmb_curve_type = self.dialog.cmb_curve_type
        tbl_curve_value = self.dialog.tbl_curve_value

        sql = f"SELECT id, idval, curve_type, descript FROM cat_curve WHERE id = '{curve}'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if not row:
            return
        curve_name = row[1]
        curve_type = row[2]
        descript = row[3]

        # Populate text & combobox widgets
        if not duplicate:
            tools_qt.set_widget_text(self.dialog, txt_name, curve_name)
            tools_qt.set_widget_enabled(self.dialog, txt_name, False)

        tools_qt.set_combo_value(cmb_curve_type, curve_type, 0, add_new=False)
        tools_qt.set_widget_text(self.dialog, txt_descript, descript)

        # Populate table curve_values
        sql = f"SELECT xcoord, ycoord FROM cat_curve_value WHERE curve = '{curve_name}'"
        rows = tools_db.get_rows(sql)
        if not rows:
            return
        for n, row in enumerate(rows):
            tbl_curve_value.setItem(n, 0, QTableWidgetItem(f"{row[0]}"))
            tbl_curve_value.setItem(n, 1, QTableWidgetItem(f"{row[1]}"))
            tbl_curve_value.insertRow(tbl_curve_value.rowCount())

    def _load_curve_widgets(self, dialog):
        """ Load values from session.config """

        # Variables
        cmb_curve_type = dialog.cmb_curve_type

        # Get values
        curve_type = tools_dr.get_config_parser('nonvisual_curves', 'cmb_curve_type', "user", "session")

        # Populate widgets
        tools_qt.set_widget_text(dialog, cmb_curve_type, curve_type)

    def _save_curve_widgets(self, dialog):
        """ Save values from session.config """

        # Variables
        cmb_curve_type = dialog.cmb_curve_type

        # Get values
        curve_type = tools_qt.get_combo_value(dialog, cmb_curve_type)

        # Populate widgets
        tools_dr.set_config_parser('nonvisual_curves', 'cmb_curve_type', curve_type)

    def _manage_curve_type(self, dialog, curve_type_headers, table, index):
        """ Manage curve values table headers """

        curve_type = tools_qt.get_combo_value(dialog, 'cmb_curve_type')
        if curve_type and curve_type_headers:
            headers = curve_type_headers.get(curve_type)
            table.setHorizontalHeaderLabels(headers)

    def _manage_curve_value(self, dialog, table, row, column):
        """ Validate data in curve values table """

        # Get curve_type
        curve_type = tools_qt.get_text(dialog, 'cmb_curve_type')
        # Control data depending on curve type
        valid = True
        self.valid = (True, "")
        if column == 0:
            # If not first row, check if previous row has a smaller value than current row
            if row - 1 >= 0:
                cur_cell = table.item(row, column)
                prev_cell = table.item(row - 1, column)
                if None not in (cur_cell, prev_cell):
                    if cur_cell.data(0) not in (None, '') and prev_cell.data(0) not in (None, ''):
                        cur_value = float(cur_cell.data(0))
                        prev_value = float(prev_cell.data(0))
                        if (cur_value < prev_value) and (curve_type != 'SHAPE' and global_vars.project_type != 'ud'):
                            valid = False
                            self.valid = (False, "Invalid curve. First column values must be ascending.")

        # If first check is valid, check all rows for column for final validation
        if valid:

            # Create list with column values
            x_values = []
            y_values = []
            for n in range(0, table.rowCount()):
                x_item = table.item(n, 0)
                if x_item is not None:
                    if x_item.data(0) not in (None, ''):
                        x_values.append(float(x_item.data(0)))
                    else:
                        x_values.append(None)
                else:
                    x_values.append(None)

                y_item = table.item(n, 1)
                if y_item is not None:
                    if y_item.data(0) not in (None, ''):
                        y_values.append(float(y_item.data(0)))
                    else:
                        y_values.append(None)
                else:
                    y_values.append(None)

            # Iterate through values
            # Check that x_values are ascending
            for i, n in enumerate(x_values):
                if i == 0 or n is None:
                    continue
                if (n > x_values[i - 1]) or (curve_type == 'SHAPE' and global_vars.project_type == 'ud'):
                    continue
                valid = False
                self.valid = (False, "Invalid curve. First column values must be ascending.")
                break
            # If PUMP, check that y_values are descending

            if curve_type == 'PUMP':
                for i, n in enumerate(y_values):
                    if i == 0 or n is None:
                        continue
                    if n < y_values[i - 1]:
                        continue
                    valid = False
                    self.valid = (False, "Invalid curve. Second column values must be descending.")
                    break

            if valid:
                # Check that all values are in pairs
                x_len = len([x for x in x_values if x is not None])  # Length of the x_values list without Nones
                y_len = len([y for y in y_values if y is not None])  # Length of the y_values list without Nones
                valid = x_len == y_len
                self.valid = (valid, "Invalid curve. Values must go in pairs.")

    def _manage_curve_plot(self, dialog, table, plot_widget, file_name=None, geom1=None, geom2=None):
        """ Note: row & column parameters are passed by the signal """

        # Clear plot
        plot_widget.axes.cla()

        # Read row values
        values = self._read_tbl_values(table)

        temp_list = []  # String list with all table values
        for v in values:
            temp_list.append(v)

        # Clean nulls of the end of the list
        clean_list = []
        for i, item in enumerate(temp_list):
            last_idx = -1
            for j, value in enumerate(item):
                if value != 'null':
                    last_idx = j
            clean_list.append(item[:last_idx + 1])

        # Convert list items to float
        float_list = []
        for lst in clean_list:
            temp_lst = []
            if len(lst) < 2:
                continue
            for item in lst:
                try:
                    value = float(item)
                except ValueError:
                    value = 0
                temp_lst.append(value)
            float_list.append(temp_lst)

        # Create x & y coordinate points to draw line
        # float_list = [[x1, y1], [x2, y2], [x3, y3]]
        x_list = [x[0] for x in float_list]  # x_list = [x1, x2, x3]
        y_list = [x[1] for x in float_list]  # y_list = [y1, y2, y3]

        # Create curve if only one value with curve_type 'PUMP'
        curve_type = tools_qt.get_combo_value(dialog, dialog.cmb_curve_type)
        if scipy_imported and len(x_list) == 1 and curve_type == 'PUMP':
            # Draw curve with points (0, 1.33y), (x, y), (2x, 0)
            x = x_list[0]
            y = y_list[0]
            x_array = np.array([0, x, 2 * x])
            y_array = np.array([1.33 * y, y, 0])

            # Define x_array as 100 equally spaced values between the min and max of original x_array
            xnew = np.linspace(x_array.min(), x_array.max(), 100)

            # Define spline
            spl = CubicSpline(x_array, y_array)
            y_smooth = spl(xnew)

            x_list = xnew
            y_list = y_smooth

        # Manage inverted plot and mirror plot for SHAPE type
        if curve_type == 'SHAPE':

            if [] in (x_list, y_list):
                if file_name:
                    fig_title = f"{file_name}"
                    plot_widget.axes.text(0, 1.02, f"{fig_title}", fontsize=12)
                return

            if geom1:
                for i in range(len(x_list)):
                    x_list[i] *= float(geom1)
                for i in range(len(y_list)):
                    y_list[i] *= float(geom1)

            # Calcule el área
            area = np.trapz(y_list, x_list) * 2

            # Create inverted plot
            plot_widget.axes.plot(y_list, x_list, color="blue")

            # Get inverted points from y_lits
            y_list_inverted = [-y for y in y_list]

            # Create mirror plot
            plot_widget.axes.plot(y_list_inverted, x_list, color="blue")

            # Manage close figure
            aux_x_list = [x_list[0], x_list[0]]
            aux_y_list = [y_list_inverted[0], y_list[0]]
            plot_widget.axes.plot(aux_y_list, aux_x_list, color="blue")

            # Manage separation figure
            aux_x_list = [x_list[0], x_list[-1]]
            aux_y_list = [y_list[-1], y_list[-1]]
            plot_widget.axes.plot(aux_y_list, aux_x_list, color="grey", alpha=0.5, linestyle="dashed")

            if file_name:
                fig_title = f"{file_name}"
                if area and geom1 and geom2:
                    fig_title = f"{file_name} (S: {round(area * 100, 2)} dm2 - {round(geom1, 2)} x {round(geom2, 2)})"
                plot_widget.axes.text(min(y_list_inverted) * 1.1, max(x_list) * 1.07, f"{fig_title}", fontsize=8)
        else:
            plot_widget.axes.plot(x_list, y_list, color='indianred')

        # Draw plot
        plot_widget.draw()

    def _accept_curves(self, dialog, is_new):
        """ Manage accept button (insert & update) """

        # Variables
        txt_id = dialog.txt_curve
        txt_name = dialog.txt_curve_name
        txt_descript = dialog.txt_descript
        cmb_curve_type = dialog.cmb_curve_type
        tbl_curve_value = dialog.tbl_curve_value

        # Get widget values
        curve = tools_qt.get_text(dialog, txt_id, add_quote=True)
        curve_name = tools_qt.get_text(dialog, txt_name, add_quote=True)
        curve_type = tools_qt.get_combo_value(dialog, cmb_curve_type)
        descript = tools_qt.get_text(dialog, txt_descript, add_quote=True)

        valid, msg = self.valid
        if not valid:
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Check that there are no empty fields
        if not curve_name or curve_name == 'null':
            tools_qt.set_stylesheet(txt_name)
            return
        tools_qt.set_stylesheet(txt_name, style="")

        if is_new:
            curve_name = curve_name.strip("'")

            # Insert cat_curve
            sql = f"""INSERT INTO cat_curve (idval, curve_type, descript) """ \
                  f"""VALUES ('{curve_name}', '{curve_type}', {descript})"""
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting curve."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            # Get inserted curve id
            sql = "SELECT last_insert_rowid();"
            curve = tools_db.get_row(sql, commit=False)[0]

            # Insert cat_curve_value
            result = self._insert_curve_values(dialog, tbl_curve_value, curve_name)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()
        elif curve is not None:
            # Update curve fields
            table_name = 'cat_curve'

            # curve_type = curve_type.strip("'")
            curve = curve.strip("'")
            curve_name = curve_name.strip("'")
            descript = descript.strip("'")
            if curve_type == -1:
                curve_type = 'null'
            fields = f"""{{"idval": "{curve_name}", "curve_type": "{curve_type}", "descript": "{descript}"}}"""

            result = self._setfields(curve, table_name, fields)
            if not result:
                return

            # Delete existing curve values
            sql = f"DELETE FROM cat_curve_value WHERE curve = '{curve_name}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old curve values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Insert new curve values
            result = self._insert_curve_values(dialog, tbl_curve_value, curve_name)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_curve_widgets(dialog)
        tools_dr.close_dialog(dialog)

    def _insert_curve_values(self, dialog, tbl_curve_value, curve_name):
        """ Insert table values into cat_curve_values """

        values = self._read_tbl_values(tbl_curve_value)

        is_empty = True
        for row in values:
            if row == (['null'] * tbl_curve_value.columnCount()):
                continue
            is_empty = False

        if is_empty:
            msg = "You need at least one row of values."
            tools_qgis.show_warning(msg, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        for row in values:
            if row == (['null'] * tbl_curve_value.columnCount()):
                continue

            sql = f"INSERT INTO cat_curve_value (curve, xcoord, ycoord) " \
                  f"VALUES ('{curve_name}', "
            for x in row:
                sql += f"{x}, "
            sql = sql.rstrip(', ') + ")"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting curve value."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return False
        return True
    # endregion

    # region patterns
    def get_patterns(self, pattern=None, duplicate=False):
        """ Opens dialog for patterns """

        # Get dialog
        self.dialog = DrNonVisualPatternUDUi()
        tools_dr.load_settings(self.dialog)

        # Manage widgets depending on the project_type
        #    calls -> def _manage_ud_patterns_dlg(self):
        getattr(self, f'_manage_{global_vars.project_type}_patterns_dlg')(pattern, duplicate=duplicate)

        # Connect dialog signals
        self._connect_dialog_signals()

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name=f'nonvisual_pattern_{global_vars.project_type}')

    def _manage_ud_patterns_dlg(self, pattern, duplicate=False):
        # Variables
        cmb_pattern_type = self.dialog.cmb_pattern_type

        # Set scale-to-fit for tableview
        self._scale_to_fit_pattern_tableviews(self.dialog)

        # Create plot widget
        plot_widget = self._create_plot_widget(self.dialog)

        for table in [self.dialog.tbl_monthly, self.dialog.tbl_daily, self.dialog.tbl_hourly, self.dialog.tbl_weekend]:
            paste_shortcut = QShortcut(QKeySequence.Paste, table)
            paste_shortcut.activated.connect(partial(self._paste_patterns_values, table))

        sql = "SELECT id, idval FROM edit_typevalue WHERE typevalue = 'inp_typevalue_pattern'"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(cmb_pattern_type, rows)

        tools_qt.set_widget_text(self.dialog, self.dialog.txt_pattern, pattern)
        tools_qt.set_widget_enabled(self.dialog, self.dialog.txt_pattern, False)
        if pattern:
            self._populate_ud_patterns_widgets(pattern, duplicate=duplicate)
        else:
            self._load_ud_pattern_widgets(self.dialog)

        # Signals
        cmb_pattern_type.currentIndexChanged.connect(partial(self._manage_patterns_tableviews, self.dialog, cmb_pattern_type, plot_widget))

        self._manage_patterns_tableviews(self.dialog, cmb_pattern_type, plot_widget)

        # Connect OK button to insert all inp_pattern and inp_pattern_value data to database
        is_new = (pattern is None) or duplicate
        self.dialog.btn_accept.clicked.connect(partial(self._accept_pattern_ud, self.dialog, is_new))

    def _paste_patterns_values(self, tbl_pattern_value):
        selected = tbl_pattern_value.selectedRanges()
        if not selected:
            return

        text = QApplication.clipboard().text()
        rows = text.split("\n")
        columns = rows[0].split("\t")
        for c, value in enumerate(columns):
            item = QTableWidgetItem(value)
            row_pos = selected[0].topRow()
            col_pos = selected[0].leftColumn() + c
            tbl_pattern_value.setItem(row_pos, col_pos, item)

    def _scale_to_fit_pattern_tableviews(self, dialog):
        tables = [dialog.tbl_monthly, dialog.tbl_daily, dialog.tbl_hourly, dialog.tbl_weekend]
        for table in tables:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setMinimumSectionSize(50)

    def _populate_ud_patterns_widgets(self, pattern, duplicate=False):
        """ Fills in all the values for ud pattern dialog """

        # Variables
        txt_name = self.dialog.txt_name
        cmb_pattern_type = self.dialog.cmb_pattern_type
        txt_descript = self.dialog.txt_descript

        sql = f"SELECT id, idval, pattern_type, descript FROM cat_pattern WHERE id = '{pattern}'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if not row:
            return

        pattern_name = row[1]
        pattern_type = row[2]
        descript = row[3]

        # Populate text & combobox widgets
        if not duplicate:
            tools_qt.set_widget_enabled(self.dialog, txt_name, False)
            tools_qt.set_widget_text(self.dialog, txt_name, pattern_name)
        tools_qt.set_combo_value(cmb_pattern_type, pattern_type, 0, add_new=False)
        tools_qt.set_widget_text(self.dialog, txt_descript, descript)

        # Populate table pattern_values
        sql = f"SELECT id, pattern, timestep, value FROM cat_pattern_value WHERE pattern = '{pattern_name}'"
        rows = tools_db.get_rows(sql)
        if not rows:
            return
        values = {}
        for row in rows:
            values[row[2]] = row[3]
        table = self.dialog.findChild(QTableWidget, f"tbl_{pattern_type.lower()}")
        for i in range(0, table.columnCount()):
            value = f"{values.get(i + 1)}"
            if value == 'None':
                value = ''
            table.setItem(0, i, QTableWidgetItem(value))

    def _load_ud_pattern_widgets(self, dialog):
        """ Load values from session.config """

        # Variables
        cmb_pattern_type = dialog.cmb_pattern_type

        # Get values
        pattern_type = tools_dr.get_config_parser('nonvisual_patterns', 'cmb_pattern_type', "user", "session")

        # Populate widgets
        tools_qt.set_combo_value(cmb_pattern_type, str(pattern_type), 0)

    def _save_ud_pattern_widgets(self, dialog):
        """ Save values from session.config """

        # Variables
        cmb_pattern_type = dialog.cmb_pattern_type

        # Get values
        pattern_type = tools_qt.get_combo_value(dialog, cmb_pattern_type)

        # Populate widgets
        tools_dr.set_config_parser('nonvisual_patterns', 'cmb_pattern_type', pattern_type)

    def _manage_patterns_tableviews(self, dialog, cmb_pattern_type, plot_widget):

        # Variables
        tbl_monthly = dialog.tbl_monthly
        tbl_daily = dialog.tbl_daily
        tbl_hourly = dialog.tbl_hourly
        tbl_weekend = dialog.tbl_weekend

        # Hide all tables
        tbl_monthly.setVisible(False)
        tbl_daily.setVisible(False)
        tbl_hourly.setVisible(False)
        tbl_weekend.setVisible(False)

        # Only show the pattern_type one
        pattern_type = tools_qt.get_combo_value(dialog, cmb_pattern_type)
        cur_table = dialog.findChild(QTableWidget, f"tbl_{pattern_type.lower()}")
        cur_table.setVisible(True)
        try:
            cur_table.cellChanged.disconnect()
        except TypeError:
            pass
        cur_table.cellChanged.connect(partial(self._manage_ud_patterns_plot, cur_table, plot_widget))
        self._manage_ud_patterns_plot(cur_table, plot_widget, None, None)

    def _accept_pattern_ud(self, dialog, is_new):
        """ Manage accept button (insert & update) """

        # Variables
        txt_id = dialog.txt_pattern
        txt_name = dialog.txt_name
        txt_descript = dialog.txt_descript
        cmb_pattern_type = dialog.cmb_pattern_type

        # Get widget values
        pattern = tools_qt.get_text(dialog, txt_id, add_quote=True)
        pattern_name = tools_qt.get_text(dialog, txt_name, add_quote=True)
        pattern_type = tools_qt.get_combo_value(dialog, cmb_pattern_type)
        descript = tools_qt.get_text(dialog, txt_descript, add_quote=True)

        # Check that there are no empty fields
        if not pattern_name or pattern_name == 'null':
            tools_qt.set_stylesheet(txt_name)
            return
        tools_qt.set_stylesheet(txt_name, style="")

        if is_new:
            # Insert inp_pattern
            sql = f"INSERT INTO cat_pattern (idval, pattern_type, descript)" \
                  f"VALUES({pattern_name}, '{pattern_type}', {descript})"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting pattern."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Insert inp_pattern_value
            result = self._insert_ud_pattern_values(dialog, pattern_type, pattern_name)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()
        elif pattern is not None:
            # Update inp_pattern
            table_name = 'cat_pattern'

            pattern = pattern.strip("'")
            descript = descript.strip("'")
            fields = f"""{{"pattern_type": "{pattern_type}", "descript": "{descript}"}}"""

            result = self._setfields(pattern, table_name, fields)
            if not result:
                return

            # Update inp_pattern_value
            sql = f"DELETE FROM cat_pattern_value WHERE pattern = '{pattern}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old pattern values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            result = self._insert_ud_pattern_values(dialog, pattern_type, pattern_name)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_ud_pattern_widgets(dialog)
        tools_dr.close_dialog(dialog)

    def _insert_ud_pattern_values(self, dialog, pattern_type, pattern_name):
        """ Insert table values into v_edit_inp_pattern_values """

        table = dialog.findChild(QTableWidget, f"tbl_{pattern_type.lower()}")

        values = self._read_tbl_values(table)

        is_empty = True
        for row in values:
            if row == (['null'] * table.columnCount()):
                continue
            is_empty = False

        if is_empty:
            msg = "You need at least one row of values."
            tools_qgis.show_warning(msg, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        for row in values:
            if row == (['null'] * table.columnCount()):
                continue

            for n, x in enumerate(row):
                sql = "INSERT INTO cat_pattern_value (pattern, timestep, value) "
                sql += f"VALUES ({pattern_name}, {n + 1}, {x});"
                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error inserting pattern value."
                    tools_qgis.show_warning(msg, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False

        return True

    def _manage_ud_patterns_plot(self, table, plot_widget, row, column):
        """ Note: row & column parameters are passed by the signal """

        # Clear plot
        plot_widget.axes.cla()

        # Read row values
        values = self._read_tbl_values(table)
        temp_list = []  # String list with all table values
        for v in values:
            temp_list.append(v)

        # Clean nulls of the end of the list
        clean_list = []
        for i, item in enumerate(temp_list):
            last_idx = -1
            for j, value in enumerate(item):
                if value != 'null':
                    last_idx = j
            clean_list.append(item[:last_idx + 1])

        # Convert list items to float
        float_list = []
        for lst in clean_list:
            temp_lst = []
            for item in lst:
                try:
                    value = float(item)
                except ValueError:
                    value = 0
                temp_lst.append(value)
            float_list.append(temp_lst)

        # Create lists for pandas DataFrame
        x_offset = 0
        for lst in float_list:
            if not lst:
                continue
            # Create lists with x zeros as offset to append new rows to the graph
            df_list = [0] * x_offset
            df_list.extend(lst)

            plot_widget.axes.bar(range(0, len(df_list)), df_list, width=1, align='edge', color='lightcoral', edgecolor='indianred')
            plot_widget.axes.set_xticks(range(0, len(df_list)))
            x_offset += len(lst)

        # Draw plot
        plot_widget.draw()

    # endregion

    # region controls
    def get_controls(self, control_id=None, duplicate=False):
        """ Opens dialog for controls """

        # Get dialog
        self.dialog = DrNonVisualControlsUi()
        tools_dr.load_settings(self.dialog)

        if control_id is not None:
            self._populate_controls_widgets(control_id)
        else:
            self._load_controls_widgets(self.dialog)

        # Connect dialog signals
        is_new = (control_id is None) or duplicate
        self.dialog.btn_accept.clicked.connect(partial(self._accept_controls, self.dialog, is_new, control_id))
        self._connect_dialog_signals()

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='nonvisual_controls')

    def _populate_controls_widgets(self, control_id):
        """ Fills in all the values for control dialog """

        # Variables
        txt_text = self.dialog.txt_text

        sql = f"SELECT id, descript FROM cat_controls WHERE id = '{control_id}'"
        row = tools_db.get_row(sql)
        if not row:
            return

        # Populate text & combobox widgets
        tools_qt.set_widget_text(self.dialog, txt_text, row[1])

    def _load_controls_widgets(self, dialog):
        """ Load values from session.config """

        pass
        # # Variables
        # chk_active = dialog.chk_active
        #
        # # Get values
        # active = tools_dr.get_config_parser('nonvisual_controls', 'chk_active', "user", "session")
        #
        # # Populate widgets
        # tools_qt.set_checked(dialog, chk_active, active)

    def _save_controls_widgets(self, dialog):
        """ Save values from session.config """

        pass
        # # Variables
        # chk_active = dialog.chk_active
        #
        # # Get values
        # active = tools_qt.is_checked(dialog, chk_active)
        #
        # # Populate widgets
        # tools_dr.set_config_parser('nonvisual_controls', 'chk_active', active)

    def _accept_controls(self, dialog, is_new, control_id):
        """ Manage accept button (insert & update) """

        # Variables
        txt_text = dialog.txt_text

        # Get widget values
        text = tools_qt.get_text(dialog, txt_text, add_quote=True)

        # Check that there are no empty fields
        if not text or text == 'null':
            tools_qt.set_stylesheet(txt_text)
            return
        tools_qt.set_stylesheet(txt_text, style="")

        if is_new:
            # Insert cat_controls
            sql = f"INSERT INTO cat_controls (descript)" \
                  f"VALUES({text})"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting control."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()
        elif control_id is not None:
            table_name = 'cat_controls'

            text = text.strip("'")
            text = text.replace("\n", "\\n")
            fields = f"""{{"descript": "{text}"}}"""

            result = self._setfields(control_id, table_name, fields)
            if not result:
                return
            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_controls_widgets(dialog)
        tools_dr.close_dialog(dialog)

    # endregion

    # region timeseries
    def get_timeseries(self, timser_id=None, duplicate=False):
        """ Opens dialog for timeseries """

        # Get dialog
        self.dialog = DrNonVisualTimeseriesUi()
        tools_dr.load_settings(self.dialog)

        # Variables
        cmb_timeser_type = self.dialog.cmb_timeser_type
        cmb_times_type = self.dialog.cmb_times_type
        tbl_timeseries_value = self.dialog.tbl_timeseries_value

        paste_shortcut = QShortcut(QKeySequence.Paste, tbl_timeseries_value)
        paste_shortcut.activated.connect(partial(self._paste_timeseries_values, tbl_timeseries_value))

        # Populate combobox
        timeser_type_headers = self._populate_timeser_combos(cmb_times_type, cmb_timeser_type)

        tools_qt.set_widget_text(self.dialog, self.dialog.txt_id, timser_id)
        tools_qt.set_widget_enabled(self.dialog, self.dialog.txt_id, False)
        if timser_id is not None:
            self._populate_timeser_widgets(timser_id, duplicate=duplicate)
        else:
            self._load_timeseries_widgets(self.dialog)

        # Set scale-to-fit
        tools_qt.set_tableview_config(tbl_timeseries_value, sectionResizeMode=QHeaderView.ResizeMode.Stretch, edit_triggers=QTableView.EditTrigger.DoubleClicked)

        is_new = (timser_id is None) or duplicate

        # Connect dialog signals
        cmb_timeser_type.currentTextChanged.connect(partial(self._manage_timeser_type, self.dialog, tbl_timeseries_value, cmb_times_type, timeser_type_headers))
        cmb_times_type.currentTextChanged.connect(partial(self._manage_times_type, tbl_timeseries_value))
        tbl_timeseries_value.cellChanged.connect(partial(self._onCellChanged, tbl_timeseries_value))
        self.dialog.btn_accept.clicked.connect(partial(self._accept_timeseries, self.dialog, is_new))
        self._connect_dialog_signals()

        self._manage_times_type(tbl_timeseries_value, tools_qt.get_combo_value(self.dialog, cmb_times_type))

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='nonvisual_timeseries')

    def _paste_timeseries_values(self, tbl_timeseries_value):
        selected = tbl_timeseries_value.selectedRanges()
        if not selected:
            return

        text = QApplication.clipboard().text()
        rows = text.split("\n")

        times_type = tools_qt.get_combo_value(self.dialog, self.dialog.cmb_times_type)
        for r, row in enumerate(rows):
            columns = row.split("\t")
            for c, value in enumerate(columns):
                item = QTableWidgetItem(value)
                row_pos = selected[0].topRow() + r
                col_pos = selected[0].leftColumn() + c
                if times_type == 'RELATIVE':
                    col_pos += 1
                tbl_timeseries_value.setItem(row_pos, col_pos, item)

    def _populate_timeser_combos(self, cmb_times_type, cmb_timeser_type):
        """ Populates timeseries dialog combos """

        timeser_type_headers = {}
        sql = "SELECT id, idval, addparam FROM edit_typevalue WHERE typevalue = 'inp_timeseries_type'"
        rows = tools_db.get_rows(sql)
        if rows:
            timeser_type_list = [[row[0], row[1]] for row in rows]
            timeser_type_headers = {row[0]: json.loads(row[2]).get('header') for row in rows if row[2]}
            tools_qt.fill_combo_values(cmb_timeser_type, timeser_type_list, index_to_show=1)

        sql = "SELECT id, idval FROM edit_typevalue WHERE typevalue = 'inp_timeseries_timestype'"
        rows = tools_db.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(cmb_times_type, rows, index_to_show=1)

        return timeser_type_headers

    def _populate_timeser_widgets(self, timser_id, duplicate=False):
        """ Fills in all the values for timeseries dialog """

        # Variables
        txt_idval = self.dialog.txt_idval
        txt_descript = self.dialog.txt_descript
        txt_fname = self.dialog.txt_fname
        tbl_timeseries_value = self.dialog.tbl_timeseries_value

        sql = f"SELECT id, idval, timser_type, times_type, descript, fname FROM cat_timeseries WHERE id = '{timser_id}'"
        row = tools_db.get_row(sql)
        if not row:
            return

        idval = row[1]
        timeser_type = row[2]
        times_type = row[3]
        descript = row[4]
        fname = row[5]

        # Populate text & combobox widgets
        if not duplicate:
            tools_qt.set_widget_text(self.dialog, txt_idval, idval)
            tools_qt.set_widget_enabled(self.dialog, txt_idval, False)
        tools_qt.set_combo_value(self.dialog.cmb_timeser_type, timeser_type, 0, add_new=False)
        tools_qt.set_combo_value(self.dialog.cmb_times_type, times_type, 0, add_new=False)
        tools_qt.set_widget_text(self.dialog, txt_descript, descript)
        tools_qt.set_widget_text(self.dialog, txt_fname, fname)

        # Populate table timeseries_values
        sql = f"SELECT id, date, time, value FROM cat_timeseries_value WHERE timeseries = '{idval}'"
        rows = tools_db.get_rows(sql)
        if not rows:
            return

        row0, row1, row2 = None, None, None
        if times_type == 'FILE':
            return
        elif times_type == 'RELATIVE':
            row0, row1, row2 = None, 'time', 'value'
        elif times_type == 'ABSOLUTE':
            row0, row1, row2 = 'date', 'time', 'value'

        headers_rel_dict = {'date': 1, 'time': 2, 'value': 3}

        for n, row in enumerate(rows):
            if row0:
                value = f"{row[headers_rel_dict.get(row0)]}"
                if value in (None, 'None', 'null'):
                    value = ''
                tbl_timeseries_value.setItem(n, 0, QTableWidgetItem(value))
            value = f"{row[headers_rel_dict.get(row1)]}"
            if value in (None, 'None', 'null'):
                value = ''
            tbl_timeseries_value.setItem(n, 1, QTableWidgetItem(value))
            value = f"{row[headers_rel_dict.get(row2)]}"
            if value in (None, 'None', 'null'):
                value = ''
            tbl_timeseries_value.setItem(n, 2, QTableWidgetItem(f"{value}"))
            tbl_timeseries_value.insertRow(tbl_timeseries_value.rowCount())

    def _manage_timeser_type(self, dialog, tbl_timeseries_value, cmb_times_type, timeser_type_headers, text):
        """ Manage timeseries times_type depending on timeseries_type """

        timeser_type = tools_qt.get_text(dialog, 'cmb_timeser_type', return_string_null=False)
        if timeser_type and timeser_type_headers:
            if timeser_type in timeser_type_headers:
                headers = timeser_type_headers.get(timeser_type)
            else:
                headers = ['Date\n(M/D/Y)', 'Time\n(H:M)', 'Value']
            tbl_timeseries_value.setHorizontalHeaderLabels(headers)

        if text in ('BC ELEVATION', 'BC FLOW'):
            tools_qt.set_combo_value(cmb_times_type, 'RELATIVE', 0, False)
            tools_qt.set_widget_enabled(dialog, cmb_times_type, False)
            return
        tools_qt.set_widget_enabled(dialog, cmb_times_type, True)

    def _manage_times_type(self, tbl_timeseries_value, text):
        """ Manage timeseries table columns depending on times_type """

        if text == 'RELATIVE':
            tbl_timeseries_value.setColumnHidden(0, True)
            return
        tbl_timeseries_value.setColumnHidden(0, False)

    def _load_timeseries_widgets(self, dialog):
        """ Load values from session.config """

        # Variables
        cmb_timeser_type = dialog.cmb_timeser_type
        cmb_times_type = dialog.cmb_times_type

        # Get values
        timeser_type = tools_dr.get_config_parser('nonvisual_timeseries', 'cmb_timeser_type', "user", "session")
        times_type = tools_dr.get_config_parser('nonvisual_timeseries', 'cmb_times_type', "user", "session")

        # Populate widgets
        tools_qt.set_combo_value(cmb_timeser_type, str(timeser_type), 0)
        tools_qt.set_combo_value(cmb_times_type, str(times_type), 0)

    def _save_timeseries_widgets(self, dialog):
        """ Save values from session.config """

        # Variables
        cmb_timeser_type = dialog.cmb_timeser_type
        cmb_times_type = dialog.cmb_times_type

        # Get values
        timeser_type = tools_qt.get_combo_value(dialog, cmb_timeser_type)
        times_type = tools_qt.get_combo_value(dialog, cmb_times_type)

        # Populate widgets
        tools_dr.set_config_parser('nonvisual_timeseries', 'cmb_timeser_type', timeser_type)
        tools_dr.set_config_parser('nonvisual_timeseries', 'cmb_times_type', times_type)

    def _accept_timeseries(self, dialog, is_new):
        """ Manage accept button (insert & update) """

        # Variables
        txt_id = dialog.txt_id
        txt_idval = dialog.txt_idval
        cmb_timeser_type = dialog.cmb_timeser_type
        cmb_times_type = dialog.cmb_times_type
        txt_descript = dialog.txt_descript
        txt_fname = dialog.txt_fname
        tbl_timeseries_value = dialog.tbl_timeseries_value

        # Get widget values
        timeseries = tools_qt.get_text(dialog, txt_id, add_quote=True)
        idval = tools_qt.get_text(dialog, txt_idval, add_quote=True)
        timser_type = tools_qt.get_combo_value(dialog, cmb_timeser_type)
        times_type = tools_qt.get_combo_value(dialog, cmb_times_type)
        descript = tools_qt.get_text(dialog, txt_descript, add_quote=True)
        fname = tools_qt.get_text(dialog, txt_fname, add_quote=True)

        # Check that there are no empty fields
        if not idval or idval == 'null':
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")
        idval = idval.strip("'")

        if is_new:
            # Insert inp_timeseries
            sql = f"INSERT INTO cat_timeseries (idval, timser_type, times_type, descript, fname)" \
                  f"VALUES('{idval}', '{timser_type}', '{times_type}', {descript}, {fname})"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting timeseries."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Insert inp_timeseries_value
            result = self._insert_timeseries_value(dialog, tbl_timeseries_value, times_type, idval)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()
        elif timeseries is not None:
            # Update inp_timeseries
            table_name = 'cat_timeseries'

            timeseries = timeseries.strip("'")
            timser_type = timser_type.strip("'")
            times_type = times_type.strip("'")
            descript = descript.strip("'")
            fname = fname.strip("'")
            fields = f"""{{"idval": "{idval}", "timser_type": "{timser_type}", "times_type": "{times_type}", "descript": "{descript}", "fname": "{fname}"}}"""
            result = self._setfields(timeseries, table_name, fields)
            if not result:
                return

            # Update inp_timeseries_value
            sql = f"DELETE FROM cat_timeseries_value WHERE timeseries = '{idval}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old timeseries values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            result = self._insert_timeseries_value(dialog, tbl_timeseries_value, times_type, idval)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_timeseries_widgets(dialog)
        tools_dr.close_dialog(dialog)

    def _insert_timeseries_value(self, dialog, tbl_timeseries_value, times_type, timeseries):
        """ Insert table values into cat_timeseries_value """

        date_formats_list = ['MM/dd/yyyy', 'M/dd/yyyy', 'MM/d/yyyy', 'M/d/yyyy',
                             'MM.dd.yyyy', 'M.dd.yyyy', 'MM.d.yyyy', 'M.d.yyyy',
                             'MM-dd-yyyy', 'M-dd-yyyy', 'MM-d-yyyy', 'M-d-yyyy']
        invalid_times = list()
        invalid_dates = list()
        output_date_format = 'MM/dd/yyyy'

        values = list()
        for y in range(0, tbl_timeseries_value.rowCount()):
            values.append(list())
            for x in range(0, tbl_timeseries_value.columnCount()):
                value = "null"
                item = tbl_timeseries_value.item(y, x)
                if item is not None and item.data(0) not in (None, ''):
                    value = item.data(0)
                    if x == 1 and isinstance(value, str):
                        time_values = item.data(0).split(':')
                        if len(time_values) == 2:
                            # Check if both values are integers
                            try:
                                hours = int(time_values[0])
                                minutes = int(time_values[1])
                                # Validate minutes range (00-59)
                                if 0 <= minutes <= 59:
                                    # Add 0 if minutes or hours are a single digit
                                    if hours < 10:
                                        hours = f"0{hours}"
                                    if minutes < 10:
                                        minutes = f"0{minutes}"
                                    value = f"{hours}:{minutes}"
                                else:
                                    invalid_times.append(item.data(0))
                            except ValueError:
                                invalid_times.append(item.data(0))
                        else:
                            invalid_times.append(item.data(0))
                    elif x == 0 and isinstance(value, str):
                        # Convert to MM/dd/yyyy date format
                        for i in range(0, len(date_formats_list)):
                            value = QDate.fromString(item.data(0), date_formats_list[i])  # Try to convert
                            if not value.isNull():
                                value = value.toString(output_date_format)  # Convert QDate to string
                                break
                        if not isinstance(value, str) and value.isNull():
                            invalid_dates.append(item.data(0))
                    else:
                        try:  # Try to convert to float, otherwise put quotes
                            value = float(value)
                        except ValueError:
                            value = f"'{value}'"
                values[y].append(value)

        if len(invalid_times) > 0:
            msg = "Invalid time format: {0}"
            msg_params = (', '.join(invalid_times),)
            tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        if len(invalid_dates) > 0:
            msg = "Invalid date format: {0}"
            msg_params = (', '.join(invalid_dates),)
            tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        # Check if table is empty
        is_empty = True
        for row in values:
            if row == (['null'] * tbl_timeseries_value.columnCount()):
                continue
            is_empty = False

        if is_empty:
            msg = "You need at least one row of values."
            tools_qgis.show_warning(msg, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        if times_type == 'ABSOLUTE':
            for row in values:
                if row == (['null'] * tbl_timeseries_value.columnCount()):
                    continue
                if 'null' in (row[0], row[1], row[2]):
                    msg = "You have to fill in '{0}', '{1}' and '{2}' fields!"
                    msg_params = ("date", "time", "value",)
                    tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False

                sql = "INSERT INTO cat_timeseries_value (timeseries, date, time, value) "
                sql += f"VALUES ('{timeseries}', '{row[0]}', '{row[1]}', {row[2]})"

                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error inserting pattern value."
                    tools_qgis.show_warning(msg, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False
        elif times_type == 'RELATIVE':

            for row in values:
                if row == (['null'] * tbl_timeseries_value.columnCount()):
                    continue
                if 'null' in (row[1], row[2]):
                    msg = "You have to fill in '{0}' and '{1}' fields!"
                    msg_params = ("time", "value",)
                    tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False

                sql = "INSERT INTO cat_timeseries_value (timeseries, time, value) "
                sql += f"VALUES ('{timeseries}', '{row[1]}', {row[2]})"

                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error inserting pattern value."
                    tools_qgis.show_warning(msg, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False

        return True

    # endregion

    # region lids
    def get_lids(self, lidco_id=None, duplicate=None):
        """ Opens dialog for lids """

        # Get dialog
        self.dialog = DrNonVisualLidsUi()

        # Set dialog not resizable
        self.dialog.setFixedSize(self.dialog.size())

        tools_dr.load_settings(self.dialog)

        is_new = (lidco_id is None) or duplicate

        # Manage decimal validation for QLineEdit
        widget_list = self.dialog.findChildren(QLineEdit)
        for widget in widget_list:
            if widget.objectName() != "txt_name":
                tools_qt.double_validator(widget, 0, 9999999, 3)

        # Populate LID Type combo
        sql = "SELECT id, idval FROM inp_typevalue WHERE typevalue = 'inp_value_lidtype' ORDER BY idval"
        rows = global_vars.gpkg_dao_data.get_rows(sql)

        if rows:
            tools_qt.fill_combo_values(self.dialog.cmb_lidtype, rows, 1)

        # Populate Control Curve combo
        sql = "SELECT id FROM cat_curve; "
        rows = global_vars.gpkg_dao_data.get_rows(sql)
        if rows:
            tools_qt.fill_combo_values(self.dialog.txt_7_cmb_control_curve, rows)

        # Signals
        self.dialog.cmb_lidtype.currentIndexChanged.connect(partial(self._manage_lids_tabs, self.dialog))
        self.dialog.btn_ok.clicked.connect(partial(self._accept_lids, self.dialog, is_new, lidco_id))
        self.dialog.btn_cancel.clicked.connect(self.dialog.reject)
        self.dialog.finished.connect(partial(tools_dr.close_dialog, self.dialog))
        self.dialog.btn_help.clicked.connect(partial(self._open_help))

        self._manage_lids_tabs(self.dialog)

        if lidco_id:
            self._populate_lids_widgets(self.dialog, lidco_id, duplicate)
        else:
            self._load_lids_widgets(self.dialog)

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='nonvisual_lids')

    def _open_help(self):
        webbrowser.open('https://giswater.gitbook.io/giswater-manual/7.-export-import-of-the-hydraulic-model')

    def _populate_lids_widgets(self, dialog, lidco_id, duplicate=False):
        """ Fills in all the values for lid dialog """

        # Get lidco_type
        cmb_lidtype = dialog.cmb_lidtype

        sql = f"SELECT lidco_type FROM inp_lid WHERE lidco_id='{lidco_id}'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if not row:
            return
        lidco_type = row[0]

        if not duplicate:
            tools_qt.set_widget_text(self.dialog, self.dialog.txt_name, lidco_id)
            tools_qt.set_widget_enabled(self.dialog, self.dialog.txt_name, False)
        tools_qt.set_combo_value(cmb_lidtype, str(lidco_type), 0)

        # Populate tab values
        sql = f"SELECT value_2, value_3, value_4, value_5, value_6, value_7,value_8 " \
              f"FROM inp_lid_value WHERE lidco_id='{lidco_id}'"
        rows = global_vars.gpkg_dao_data.get_rows(sql)

        if rows:
            idx = 0
            for i in range(self.dialog.tab_lidlayers.count()):
                if self.dialog.tab_lidlayers.isTabVisible(i):
                    try:
                        row = rows[idx]
                    except IndexError:  # The tab exists in dialog but not in db (drain might be optional)
                        continue

                    # List with all QLineEdit children
                    child_list = self.dialog.tab_lidlayers.widget(i).children()
                    visible_widgets = [widget for widget in child_list if isinstance(widget, QLineEdit)]
                    visible_widgets = self._order_list(visible_widgets)

                    for x, value in enumerate(row):
                        if value in ('null', None):
                            continue
                        try:
                            widget = visible_widgets[x]
                        except IndexError:  # The widget exists in dialog but not in db (db error, extra values)
                            continue
                        tools_qt.set_widget_text(self.dialog, widget, f"{value}")
                    idx += 1

    def _load_lids_widgets(self, dialog):
        """ Load values from session.config """

        # Variable
        cmb_lidtype = dialog.cmb_lidtype

        # Get values
        lidtype = tools_dr.get_config_parser('nonvisual_lids', 'cmb_lidtype', "user", "session")

        # Populate widgets
        tools_qt.set_combo_value(cmb_lidtype, str(lidtype), 0)

        for i in range(dialog.tab_lidlayers.count()):
            if Qgis.QGIS_VERSION_INT >= 32000:
                if not dialog.tab_lidlayers.isTabVisible(i):
                    continue
            else:
                if not dialog.tab_lidlayers.isTabEnabled(i):
                    continue

                # List with all QLineEdit children
                child_list = dialog.tab_lidlayers.widget(i).children()
                visible_widgets = [widget for widget in child_list if
                                   isinstance(widget, QLineEdit) or isinstance(widget, QComboBox)]
                visible_widgets = self._order_list(visible_widgets)

                for y, widget in enumerate(visible_widgets):
                    value = tools_dr.get_config_parser('nonvisual_lids', f"{widget.objectName()}", "user", "session")

                    if isinstance(widget, QLineEdit):
                        tools_qt.set_widget_text(dialog, widget, str(value))
                    else:
                        tools_qt.set_combo_value(widget, str(value), 0)

    def _save_lids_widgets(self, dialog):
        """ Save values from session.config """

        # Variables
        txt_name = dialog.txt_name
        cmb_lidtype = dialog.cmb_lidtype

        # Get values
        name = tools_qt.get_text(dialog, txt_name)
        lidtype = tools_qt.get_combo_value(dialog, cmb_lidtype)

        for i in range(dialog.tab_lidlayers.count()):
            if dialog.tab_lidlayers.isTabVisible(i):
                # List with all QLineEdit children
                child_list = dialog.tab_lidlayers.widget(i).children()
                visible_widgets = [widget for widget in child_list if isinstance(widget, QLineEdit) or isinstance(widget, QComboBox)]
                visible_widgets = self._order_list(visible_widgets)

                for y, widget in enumerate(visible_widgets):
                    if isinstance(widget, QLineEdit):
                        value = tools_qt.get_text(dialog, widget)
                    else:
                        value = tools_qt.get_combo_value(dialog, widget)
                    tools_dr.set_config_parser('nonvisual_lids', f"{widget.objectName()}", value)

        # Populate widgets
        tools_dr.set_config_parser('nonvisual_lids', 'cmb_lidtype', lidtype)
        tools_dr.set_config_parser('nonvisual_lids', 'txt_name', name)

    def _manage_lids_tabs(self, dialog):

        cmb_lidtype = dialog.cmb_lidtype
        tab_lidlayers = dialog.tab_lidlayers
        lidco_id = str(cmb_lidtype.currentText())

        # Tabs to show
        sql = f"SELECT addparam, id FROM inp_typevalue WHERE typevalue = 'inp_value_lidtype' and idval =  '{lidco_id}'"
        row = global_vars.gpkg_dao_data.get_row(sql)

        lidtabs = []
        if row:
            json_result = row[0]
            lid_id = row[1]
            lidtabs = json_result[f"{lid_id}"]

        # Show tabs
        for i in range(tab_lidlayers.count()):
            tab_name = tab_lidlayers.widget(i).objectName().upper()

            # Set the first non-hidden tab selected
            if tab_name == lidtabs[0]:
                tab_lidlayers.setCurrentIndex(i)

            if tab_name not in lidtabs:
                if Qgis.QGIS_VERSION_INT >= 32000:
                    tab_lidlayers.setTabVisible(i, False)
                else:
                    tab_lidlayers.setTabEnabled(i, False)

            else:
                if Qgis.QGIS_VERSION_INT >= 32000:
                    tab_lidlayers.setTabVisible(i, True)
                else:
                    tab_lidlayers.setTabEnabled(i, True)

                if tab_name == 'DRAIN':
                    if lid_id == 'RD':
                        tab_lidlayers.setTabText(i, "Roof Drainage")
                    else:
                        tab_lidlayers.setTabText(i, "Drain")
                self._manage_lids_hide_widgets(self.dialog, lid_id)

        # Set image
        self._manage_lids_images(lidco_id)

    def _manage_lids_hide_widgets(self, dialog, lid_id):
        """ Hides widgets that are not necessary in specific tabs """

        # List of widgets
        widgets_hide = {'BC': {'lbl_surface_side_slope', 'txt_5_surface_side_slope', 'lbl_drain_delay', 'txt_4_drain_delay'},
                        'RG': {'lbl_surface_side_slope', 'txt_5_surface_side_slope'},
                        'GR': {'lbl_surface_slope', 'txt_4_surface_slope'},
                        'IT': {'lbl_surface_side_slope', 'txt_5_surface_side_slope', 'lbl_drain_delay', 'txt_4_drain_delay'},
                        'PP': {'lbl_surface_side_slope', 'txt_5_surface_side_slope', 'lbl_drain_delay', 'txt_4_drain_delay'},
                        'RB': {'lbl_seepage_rate', 'txt_3_seepage_rate', 'lbl_clogging_factor_storage', 'txt_4_clogging_factor_storage'},
                        'RD': {'lbl_vegetation_volume', 'txt_2_vegetation_volume', 'lbl_surface_side_slope', 'txt_5_surface_side_slope',
                               'lbl_flow_exponent', 'lbl_offset', 'lbl_drain_delay', 'lbl_open_level',
                               'lbl_closed_level', 'lbl_control_curve', 'lbl_flow_description', 'txt_2_flow_exponent',
                               'txt_3_offset', 'txt_4_drain_delay', 'txt_5_open_level', 'txt_6_closed_level', 'txt_7_cmb_control_curve', },
                        'VS': {''}}

        # Hide widgets in list
        for i in range(dialog.tab_lidlayers.count()):
            if Qgis.QGIS_VERSION_INT >= 32000:
                if not dialog.tab_lidlayers.isTabVisible(i):
                    continue
            else:
                if not dialog.tab_lidlayers.isTabEnabled(i):
                    continue

            # List of children
            list = dialog.tab_lidlayers.widget(i).children()
            for y in list:
                if not isinstance(y, QGridLayout):
                    y.show()
                    for j in widgets_hide[lid_id]:
                        if j == y.objectName():
                            y.hide()

    def _manage_lids_images(self, lidco_id):
        """ Manage images depending on lidco_id selected"""

        sql = f"SELECT id FROM inp_typevalue WHERE typevalue = 'inp_value_lidtype' and idval = '{lidco_id}'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if not row:
            return

        img = f"ud_lid_{row[0]}"
        tools_qt.add_image(self.dialog, 'lbl_section_image',
                           f"{self.plugin_dir}{os.sep}resources{os.sep}png{os.sep}{img}")

    def _accept_lids(self, dialog, is_new, lidco_id):
        """ Manage accept button (insert & update) """

        # Variables
        cmb_lidtype = dialog.cmb_lidtype
        txt_lidco_id = dialog.txt_name

        # Get widget values
        lidco_type = tools_qt.get_combo_value(dialog, cmb_lidtype)
        lidco_id = tools_qt.get_text(dialog, txt_lidco_id, add_quote=True)

        # Insert in table 'inp_lid'
        if is_new:
            if not lidco_id or lidco_id == 'null':
                tools_qt.set_stylesheet(txt_lidco_id)
                return
            tools_qt.set_stylesheet(txt_lidco_id, style="")

            # Insert in inp_lid
            if lidco_id != '':
                sql = f"INSERT INTO inp_lid(lidco_id, lidco_type) VALUES({lidco_id}, '{lidco_type}')"
                result = tools_db.execute_sql(sql, commit=False)

                if not result:
                    msg = "There was an error inserting lid."
                    tools_qgis.show_warning(msg, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False

            # Inserts in table inp_lid_value
            result = self._insert_lids_values(dialog, lidco_id.strip("'"), lidco_type)
            if not result:
                sql = f"DELETE FROM inp_lid WHERE lidco_id ={lidco_id}"
                tools_db.execute_sql(sql, commit=False)
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        elif lidco_id is not None:
            # Update inp_lid fields
            table_name = 'inp_lid'

            fields = f"""{{"lidco_type": "{lidco_type}"}}"""

            result = self._setfields(lidco_id.strip("'"), table_name, fields)
            if not result:
                return

            # Delete existing inp_lid_value values
            sql = f"DELETE FROM inp_lid_value WHERE lidco_id = {lidco_id}"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old lid values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return

            # Inserts in table inp_lid_value
            result = self._insert_lids_values(dialog, lidco_id.strip("'"), lidco_type)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_lids_widgets(dialog)
        tools_dr.close_dialog(dialog)

    def _insert_lids_values(self, dialog, lidco_id, lidco_type):

        control_values = {
            'BC': {'txt_1_thickness', 'txt_1_thickness_storage'},
            'RG': {'txt_1_thickness', 'txt_1_thickness_storage'},
            'GR': {'txt_1_thickness', 'drainmat_2'},
            'IT': {'txt_1_thickness_storage'},
            'PP': {'txt_1_thickness_pavement', 'txt_1_thickness_storage'},
            'RB': {''},
            'RD': {''},
            'VS': {'txt_1_berm_height'}
        }

        for i in range(dialog.tab_lidlayers.count()):
            if dialog.tab_lidlayers.isTabVisible(i):
                tab_name = dialog.tab_lidlayers.widget(i).objectName().upper()
                # List with all QLineEdit children
                child_list = dialog.tab_lidlayers.widget(i).children()
                widgets_list = [widget for widget in child_list if type(widget) in (QLineEdit, QComboBox)]
                # Get QLineEdits and QComboBox that are visible
                visible_widgets = [widget for widget in widgets_list if not widget.isHidden()]
                visible_widgets = self._order_list(visible_widgets)

                sql = "INSERT INTO inp_lid_value (lidco_id, lidlayer,"
                for y, widget in enumerate(visible_widgets):
                    sql += f"value_{y + 2}, "
                sql = sql.rstrip(', ') + ")"
                sql += f"VALUES ('{lidco_id}', '{tab_name}', "
                for widget in visible_widgets:
                    value = tools_qt.get_text(dialog, widget.objectName(), add_quote=True)
                    if value == "null":
                        value = "'0'"
                    # Control values that cannot be 0
                    if widget.objectName() in control_values[lidco_type] and value == "'0'":
                        dialog.tab_lidlayers.setCurrentWidget(dialog.tab_lidlayers.widget(i))
                        msg = "Marked values must be greater than 0"
                        title = "LIDS"
                        tools_qt.show_info_box(msg, title)
                        tools_qt.set_stylesheet(widget)

                        return False
                    tools_qt.set_stylesheet(widget, style="")

                    sql += f"{value}, "
                sql = sql.rstrip(', ') + ")"
                result = tools_db.execute_sql(sql, commit=False)
                if not result:
                    msg = "There was an error inserting {0}."
                    msg_params = ("lid",)
                    tools_qgis.show_warning(msg, msg_params=msg_params, dialog=dialog)
                    global_vars.gpkg_dao_data.rollback()
                    return False
        return True

    # endregion

    # region rasters
    def get_rasters(self, raster_id=None, duplicate=False):
        """ Opens dialog for raster """

        # Get dialog
        self.dialog = DrNonVisualRasterUi()
        tools_dr.load_settings(self.dialog)

        # Define variables
        tbl_raster_value = self.dialog.tbl_raster_value
        cmb_raster_type = self.dialog.cmb_raster_type

        # Activate paste shortcut
        paste_shortcut = QShortcut(QKeySequence.Paste, tbl_raster_value)
        paste_shortcut.activated.connect(partial(self._paste_raster_values, tbl_raster_value))

        # Populate combobox
        self._populate_raster_combo(cmb_raster_type)

        # Populate data if editing raster
        tools_qt.set_widget_text(self.dialog, self.dialog.txt_raster_id, raster_id)
        tools_qt.set_widget_enabled(self.dialog, self.dialog.txt_raster_id, False)
        if raster_id is not None:
            self._populate_raster_widgets(raster_id, duplicate=duplicate)
        else:
            self._load_raster_widgets(self.dialog)

        # Set scale-to-fit
        tools_qt.set_tableview_config(tbl_raster_value, sectionResizeMode=QHeaderView.ResizeMode.Stretch, edit_triggers=QTableView.EditTrigger.DoubleClicked)

        is_new = (raster_id is None) or duplicate

        # Connect dialog signals
        tbl_raster_value.cellChanged.connect(partial(self._onCellChanged, tbl_raster_value))
        self.dialog.btn_accept.clicked.connect(partial(self._accept_raster, self.dialog, is_new))
        self._connect_dialog_signals()

        # Open dialog
        tools_dr.open_dialog(self.dialog, dlg_name='nonvisual_raster')

    def _paste_raster_values(self, tbl_raster_value):
        """ Paste values from clipboard to table """

        selected = tbl_raster_value.selectedRanges()
        if not selected:
            return

        text = QApplication.clipboard().text()
        rows = text.split("\n")

        for r, row in enumerate(rows):
            columns = row.split("\t")
            for c, value in enumerate(columns):
                item = QTableWidgetItem(value)
                row_pos = selected[0].topRow() + r
                col_pos = selected[0].leftColumn() + c
                tbl_raster_value.setItem(row_pos, col_pos, item)

    def _populate_raster_combo(self, cmb_raster_type):
        """ Populates raster dialog combos """

        raster_type_headers = {}
        sql = "SELECT id, idval, addparam FROM edit_typevalue WHERE typevalue = 'inp_rain_format'"
        rows = tools_db.get_rows(sql)
        if rows:
            raster_type_list = [[row[0], row[1]] for row in rows]
            raster_type_headers = {row[0]: json.loads(row[2]).get('header') for row in rows if row[2]}
            tools_qt.fill_combo_values(cmb_raster_type, raster_type_list)

        return raster_type_headers

    def _populate_raster_widgets(self, raster_id, duplicate=False):
        """ Fills in all the values for raster dialog """

        # Variables
        txt_name = self.dialog.txt_raster_name
        cmb_raster_type = self.dialog.cmb_raster_type
        tbl_raster_value = self.dialog.tbl_raster_value

        sql = f"SELECT * FROM cat_raster WHERE id = '{raster_id}'"
        row = global_vars.gpkg_dao_data.get_row(sql)
        if not row:
            return
        raster_name = row[1]
        raster_type = row[2]

        # Populate text & combobox widgets
        if not duplicate:
            tools_qt.set_widget_text(self.dialog, txt_name, raster_name)
            tools_qt.set_widget_enabled(self.dialog, txt_name, False)

        tools_qt.set_combo_value(cmb_raster_type, raster_type, 0, add_new=False)

        # Populate table raster_values
        sql = f"SELECT time, fname FROM cat_raster_value WHERE raster = '{raster_name}'"
        rows = tools_db.get_rows(sql)
        if not rows:
            return
        print(f"ROWS -> {rows}")
        for n, row in enumerate(rows):
            tbl_raster_value.setItem(n, 0, QTableWidgetItem(f"{QTime(0, 0, 0).addSecs(row[0]).toString('HH:mm:ss')}"))
            tbl_raster_value.setItem(n, 1, QTableWidgetItem(f"{row[1]}"))
            tbl_raster_value.insertRow(tbl_raster_value.rowCount())

    def _load_raster_widgets(self, dialog):
        """ Load values from session.config """

        # Variables
        cmb_raster_type = dialog.cmb_raster_type

        # Get values
        raster_type = tools_dr.get_config_parser('nonvisual_rasters', 'cmb_raster_type', "user", "session")

        # Populate widgets
        tools_qt.set_widget_text(dialog, cmb_raster_type, raster_type)

    def _save_raster_widgets(self, dialog):
        """ Save values from session.config """

        # Variables
        cmb_raster_type = dialog.cmb_raster_type

        # Get values
        raster_type = tools_qt.get_combo_value(dialog, cmb_raster_type)

        # Populate widgets
        tools_dr.set_config_parser('nonvisual_rasters', 'cmb_raster_type', raster_type)

    def _accept_raster(self, dialog, is_new):
        """ Manage accept button (insert & update) """

        # Variables
        txt_id = dialog.txt_raster_id
        txt_idval = dialog.txt_raster_name
        cmb_raster_type = dialog.cmb_raster_type
        tbl_raster_value = dialog.tbl_raster_value

        # Get widget values
        raster_id = tools_qt.get_text(dialog, txt_id, add_quote=True)
        idval = tools_qt.get_text(dialog, txt_idval, add_quote=True)
        raster_type = tools_qt.get_combo_value(dialog, cmb_raster_type)

        # Check that there are no empty fields
        if not idval or idval == 'null':
            tools_qt.set_stylesheet(txt_idval)
            return
        tools_qt.set_stylesheet(txt_idval, style="")
        idval = idval.strip("'")

        if is_new:
            # Insert inp_raster
            sql = f"INSERT INTO cat_raster (idval, raster_type)" \
                  f"VALUES('{idval}', '{raster_type}')"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting timeseries."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            # Get inserted raster id
            sql = "SELECT last_insert_rowid();"
            raster_id = tools_db.get_row(sql, commit=False)[0]

            # Insert inp_raster_value
            result = self._insert_raster_values(dialog, tbl_raster_value, idval)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()
        elif raster_id is not None:
            # Update inp_timeseries
            table_name = 'cat_raster'

            raster_id = raster_id.strip("'")
            raster_type = raster_type.strip("'")
            fields = f"""{{"raster_type": "{raster_type}"}}"""

            result = self._setfields(raster_id, table_name, fields)
            if not result:
                return

            # Update inp_raster_value
            sql = f"DELETE FROM cat_raster_value WHERE raster = '{idval}'"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error deleting old timeseries values."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return
            result = self._insert_raster_values(dialog, tbl_raster_value, idval)
            if not result:
                return

            # Commit
            global_vars.gpkg_dao_data.commit()
            # Reload manager table
            self._reload_manager_table()

        self._save_raster_widgets(dialog)
        tools_dr.close_dialog(dialog)

    def _insert_raster_values(self, dialog, tbl_raster_value, raster_id):
        """ Insert table values into cat_raster_values """

        values = self._read_tbl_values(tbl_raster_value)

        is_empty = True
        for row in values:
            if row == (['null'] * tbl_raster_value.columnCount()):
                continue
            is_empty = False

        if is_empty:
            msg = "You need at least one row of values."
            tools_qgis.show_warning(msg, dialog=dialog)
            global_vars.gpkg_dao_data.rollback()
            return False

        for row in values:
            if row == (['null'] * tbl_raster_value.columnCount()):
                continue
            time_value: int = self._str2seconds(row[0])
            sql = "INSERT INTO cat_raster_value (raster, time, fname) "
            sql += f"VALUES ('{raster_id}', {time_value}, '{row[1]}')"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting raster value."
                tools_qgis.show_warning(msg, dialog=dialog)
                global_vars.gpkg_dao_data.rollback()
                return False
        return True

    def _str2seconds(self, time: str) -> int:
        hours, minutes, seconds = map(int, time.split(":"))
        seconds = hours * 3600 + minutes * 60 + seconds
        return seconds

    # endregion

    # region private functions
    def _setfields(self, id, table_name, fields):

        feature = f'"id":"{id}", '
        feature += f'"tableName":"{table_name}" '
        extras = f'"fields":{fields}'
        body = tools_dr.create_body(feature=feature, extras=extras)
        print(f"body :>> {body}")
        json_result = tools_dr.execute_procedure('setfields', body, commit=False)
        print(f"json_result :>> {json_result}")
        if (not json_result) or (json_result.get('status') in (None, 'Failed')):
            global_vars.gpkg_dao_data.rollback()
            return False

        return True

    def _reload_manager_table(self):

        try:
            self.manager_dlg.main_tab.currentWidget().model().select()
        except Exception:
            pass

    def _connect_dialog_signals(self):

        self.dialog.btn_cancel.clicked.connect(self.dialog.reject)
        self.dialog.rejected.connect(partial(tools_dr.close_dialog, self.dialog))

    def _onCellChanged(self, table, row, column):
        """ Note: row & column parameters are passed by the signal """

        # Add a new row if the edited row is the last one
        if row >= (table.rowCount() - 1):
            headers = ['Multiplier' for n in range(0, table.rowCount() + 1)]
            table.insertRow(table.rowCount())
            table.setVerticalHeaderLabels(headers)
        # Remove "last" row (empty one) if the real last row is empty
        elif row == (table.rowCount() - 2):
            for n in range(0, table.columnCount()):
                item = table.item(row, n)
                if item is not None:
                    if item.data(0) not in (None, ''):
                        return
            table.setRowCount(table.rowCount() - 1)

    def _read_tbl_values(self, table, clear_nulls=False):

        values = list()
        for y in range(0, table.rowCount()):
            values.append(list())
            for x in range(0, table.columnCount()):
                value = "null"
                item = table.item(y, x)
                if item is not None and item.data(0) not in (None, ''):
                    value = item.data(0)
                if clear_nulls and value == "null":
                    continue
                values[y].append(value)
        return values

    def _create_plot_widget(self, dialog):

        plot_widget = MplCanvas(dialog, width=5, height=4, dpi=100)
        plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        plot_widget.setMinimumSize(100, 100)
        dialog.lyt_plot.addWidget(plot_widget, 0, 0)

        return plot_widget

    def _order_list(self, lst):
        """Order widget list by objectName"""

        for x in range(len(lst)):
            for j in range(0, (len(lst) - x - 1)):
                if lst[j].objectName() > lst[(j + 1)].objectName():
                    lst[j], lst[(j + 1)] = lst[(j + 1)], lst[j]
        return lst

    def _import_rasters(self, dialog):
        # Configure and open import dialog
        self.raster_import_dlg = DrNonVisualRasterImportUi()

        # Build combos
        time_systems = [['hours', 'hours'], ['minutes', 'minutes'], ['seconds', 'seconds']]
        tools_qt.fill_combo_values(self.raster_import_dlg.cmb_time_system, time_systems)
        self._previous_time_system = tools_qt.get_combo_value(self.raster_import_dlg, self.raster_import_dlg.cmb_time_system)

        self._populate_raster_combo(self.raster_import_dlg.cmb_raster_type)

        # Set listeners
        self.raster_import_dlg.btn_cancel.clicked.connect(self.raster_import_dlg.reject)
        self.raster_import_dlg.rejected.connect(partial(tools_dr.close_dialog, self.raster_import_dlg))
        self.raster_import_dlg.btn_ok.clicked.connect(partial(self._import_rasters_accept, self.raster_import_dlg))
        self.raster_import_dlg.btn_push_raster_input_folder.clicked.connect(self._open_raster_input_folder)
        self.raster_import_dlg.cmb_time_system.currentIndexChanged.connect(self._on_time_system_changed)

        # Open dialog
        tools_dr.open_dialog(self.raster_import_dlg, dlg_name='nonvisual_raster_import')

    def _import_rasters_accept(self, dialog: DrNonVisualRasterImportUi):
        """ Check raster files and save them to database """

        plugin_dir: str = os.path.dirname(global_vars.gpkg_dao_data.db_filepath)
        folder_path: Optional[str] = tools_qt.get_text(self.raster_import_dlg, 'txt_folder_path', return_string_null=False)
        timestep_value: float = self.raster_import_dlg.sb_time_value.value()
        time_system = tools_qt.get_combo_value(self.raster_import_dlg, self.raster_import_dlg.cmb_time_system)
        raster_type = tools_qt.get_combo_value(self.raster_import_dlg, self.raster_import_dlg.cmb_raster_type)
        raster_name: Optional[str] = tools_qt.get_text(self.raster_import_dlg, 'txt_raster_name', return_string_null=False)

        if raster_name is None or raster_name == '':
            msg = "Please enter a raster name"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Check folder
        folder_path = tools_qt.get_text(dialog, 'txt_folder_path')
        if not folder_path:
            msg = "Please select a folder"
            tools_qgis.show_warning(msg, dialog=dialog)
            return
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            msg = "Invalid folder path"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Check if folder is inside plugin directory
        try:
            plugin_path = os.path.abspath(plugin_dir)
            folder_path = os.path.abspath(folder_path)
            if not folder_path.startswith(plugin_path):
                msg = "Selected folder must be inside the same directory as the geopackage file"
                tools_qgis.show_warning(msg, dialog=dialog)
                return
        except Exception:
            msg = "Error validating folder path"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        result = tools_qt.show_question("The raster files will be ordered by filename on alphabetical order.\n\n Do you want to continue?", "Import rasters", force_action=True)
        if not result:
            return

        # Get raster files
        files = os.listdir(folder_path)
        files.sort()
        filtered_files = []
        for file in files:
            if file.endswith('.asc') or file.endswith('.txt'):
                filtered_files.append(file)
        if len(filtered_files) == 0:
            msg = "No raster files found in the selected folder"
            tools_qgis.show_warning(msg, dialog=dialog)
            return

        # Show tab log
        tools_dr.set_tabs_enabled(self.raster_import_dlg)
        self.raster_import_dlg.mainTab.setCurrentIndex(1)

        self.raster_import_dlg.btn_ok.setEnabled(False)

        self._set_progress_text("Importing rasters...", 0, True)

        # Insert inp_raster
        sql = f"INSERT INTO cat_raster (idval, raster_type)" \
                f"VALUES('{raster_name}', '{raster_type}')"
        result = tools_db.execute_sql(sql, commit=False)
        if not result:
            msg = "There was an error inserting raster."
            tools_qgis.show_warning(msg, dialog=dialog)
            self._set_progress_text("Error inserting raster: " + msg, 100, True)
            global_vars.gpkg_dao_data.rollback()
            return

        # Initialize time as QTime starting from 00:00
        current_seconds = 0

        # Convert timestep_value to minutes based on time_system
        seconds_to_add = 0
        if time_system == 'hours':
            seconds_to_add = int(timestep_value * 3600)
        elif time_system == 'minutes':
            seconds_to_add = int(timestep_value * 60)
        elif time_system == 'seconds':
            seconds_to_add = int(timestep_value)

        for index, raster in enumerate(filtered_files):
            # Calculate relative path from plugin directory
            raster_full_path = os.path.join(folder_path, raster)
            relative_path = os.path.relpath(raster_full_path, plugin_dir)

            # Insert inp_raster_value with relative path and formatted time
            sql = "INSERT INTO cat_raster_value (raster, time, fname) "
            sql += f"VALUES ('{raster_name}', '{current_seconds}', '{relative_path}')"
            result = tools_db.execute_sql(sql, commit=False)
            if not result:
                msg = "There was an error inserting raster value."
                tools_qgis.show_warning(msg, dialog=dialog)
                self._set_progress_text("Error inserting raster value: " + msg, 100, True)
                global_vars.gpkg_dao_data.rollback()
                return False

            # Increment time by timestep
            current_seconds += seconds_to_add

            time_str = QTime(0, 0, 0).addSecs(current_seconds).toString('HH:mm:ss')

            self._set_progress_text(f"Imported raster {raster} with time {time_str}", tools_dr.lerp_progress(int(index / len(filtered_files) * 100), 0, 90), True)

        global_vars.gpkg_dao_data.commit()
        self._set_progress_text("Rasters imported successfully", 100, True)
        self.raster_import_dlg.btn_cancel.setText("Close")
        # Reload manager table
        self._reload_manager_table()

    def _set_progress_text(self, text: str, progress: int, new_line: bool = False):
        """ Set text to textbox """

        # Progress bar
        if progress is not None:
            self.raster_import_dlg.progress_bar.setValue(progress)

        # TextEdit log
        txt_infolog = self.raster_import_dlg.findChild(QTextEdit, 'txt_infolog')
        cur_text = tools_qt.get_text(self.raster_import_dlg, txt_infolog, return_string_null=False)

        end_line = '\n' if new_line else ''
        if text:
            txt_infolog.setText(f"{cur_text}{text}{end_line}")
        else:
            txt_infolog.setText(f"{cur_text}{end_line}")
        txt_infolog.show()
        # Scroll to the bottom
        scrollbar = txt_infolog.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _open_raster_input_folder(self):
        """ Open folder dialog and set path to textbox """
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.raster_import_dlg, 'txt_folder_path', str(path))

    def _on_time_system_changed(self):
        """ Update Spinbox value based on selected time system """

        # Get current time system
        time_system = tools_qt.get_combo_value(self.raster_import_dlg, self.raster_import_dlg.cmb_time_system)

        # Get current value from appropriate spinbox based on previous time system
        current_value: float = 0
        if hasattr(self, '_previous_time_system'):
            current_value = self.raster_import_dlg.sb_time_value.value()

        # Convert value based on time system change
        converted_value: float = current_value
        if hasattr(self, '_previous_time_system'):
            # Convert from previous to new time system
            if self._previous_time_system == 'hours':
                if time_system == 'minutes':
                    converted_value = current_value * 60
                elif time_system == 'seconds':
                    converted_value = current_value * 3600
            elif self._previous_time_system == 'minutes':
                if time_system == 'hours':
                    converted_value = current_value / 60
                elif time_system == 'seconds':
                    converted_value = current_value * 60
            elif self._previous_time_system == 'seconds':
                if time_system == 'hours':
                    converted_value = current_value / 3600
                elif time_system == 'minutes':
                    converted_value = current_value / 60

        # Update appropriate spinbox with converted value
        self.raster_import_dlg.sb_time_value.setValue(converted_value)

        # Store current time system for next change
        self._previous_time_system = time_system

    # endregion
