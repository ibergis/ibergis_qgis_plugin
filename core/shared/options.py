"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import json
from functools import partial
from typing import List, Dict, Any

from qgis.PyQt.QtWidgets import QWidget, QComboBox, QGroupBox, QSpacerItem, QSizePolicy, \
    QGridLayout, QTabWidget
from qgis.PyQt.QtCore import QDateTime
from ..ui.ui_manager import DrGo2EpaOptionsUi
from ..utils import tools_dr
from ...lib import tools_qgis, tools_qt
from ... import global_vars


class DrOptions:

    def __init__(self, tabs_to_show=None, parent=None):
        self.epa_options_list = None
        self.dlg_go2epa_options = None
        self.tabs_to_show = tabs_to_show
        if self.tabs_to_show is None:
            self.tabs_to_show = ["tab_inp_swmm", "tab_rpt_swmm", "tab_main", "tab_rpt_iber", "tab_plugins"]
        self.tab_aliases = {"tab_inp_swmm": tools_qt.tr("SWMM OPTIONS"), "tab_rpt_swmm": tools_qt.tr("SWMM RESULTS"),
                            "tab_main": tools_qt.tr("IBER OPTIONS"), "tab_rpt_iber": tools_qt.tr("IBER RESULTS"),
                            "tab_plugins": tools_qt.tr("IBER PLUGINS")
                            }
        self.parent = parent

    def open_options_dlg(self):
        self._go2epa_options()

    def _go2epa_options(self):
        """ Button 23: Open form to set INP, RPT and project """

        # Clear list
        self.epa_options_list = []

        # Create dialog
        self.dlg_go2epa_options = DrGo2EpaOptionsUi(parent=self.parent)
        tools_dr.load_settings(self.dlg_go2epa_options)

        # Call getconfig
        form = '"formName":"epaoptions"'
        body = tools_dr.create_body(form=form)
        json_result = tools_dr.execute_procedure('getconfig', body)
        if not json_result or json_result['status'] == 'Failed':
            return False

        # Get sys_param values
        v_sql = "SELECT distinct tabname " \
                "FROM config_form_fields " \
                "WHERE formname = 'dlg_options' AND tabname IS NOT NULL"
        tab_list = global_vars.gpkg_dao_data.get_rows(v_sql)
        tab_list = sorted(tab_list, key=lambda tab: self.tabs_to_show.index(tab[0]) if tab[0] in self.tabs_to_show else float('inf'))

        v_sql = "select distinct (layoutname), tabname " \
                "FROM config_form_fields " \
                "WHERE formname = 'dlg_options' AND layoutname IS NOT NULL"
        lyt_list = global_vars.gpkg_dao_data.get_rows(v_sql)

        v_sql = "SELECT id, idval " \
                "FROM edit_typevalue " \
                "WHERE typevalue = 'dlg_options_layout'"
        titles_list = global_vars.gpkg_dao_data.get_rows(v_sql)
        titles_dict = {row[0]: row[1] for row in titles_list}

        main_tab = self.dlg_go2epa_options.findChild(QTabWidget, 'main_tab')

        # Mount form tabs
        for tab in tab_list:
            tab_name = tab[0]
            if tab_name not in self.tabs_to_show:
                continue

            tab_widget = QWidget(main_tab)
            tab_widget.setObjectName(f"{tab_name}")
            main_tab.addTab(tab_widget, f"{self.tab_aliases.get(tab_name, tab_name)}")

            # Mount layout tabs
            layout = QGridLayout()

            for i, lyt in enumerate(lyt_list):
                if lyt[1] == tab_name:

                    groupBox = QGroupBox()
                    lyt_title = titles_dict.get(lyt[0])
                    if lyt_title:
                        groupBox.setTitle(f"{lyt_title}")
                    gridlayout = QGridLayout()
                    gridlayout.setObjectName(f"{lyt[0]}")

                    try:
                        lyt_name_split = lyt[0].split('_')
                        lyt_row = lyt_name_split[-2]
                        lyt_col = lyt_name_split[-1]
                        row = int(lyt_row) - 1
                        col = int(lyt_col) - 1
                    except Exception:
                        msg = "Layout '{0}' has an invalid name. It has to end with {1} indicating where in the dialog it should go."
                        msg_params = (lyt[0], "row_column",)
                        tools_qgis.show_warning(msg, msg_params=msg_params)
                        continue

                    layout.addWidget(groupBox, row, col)

                    groupBox.setLayout(gridlayout)

            # Add Vertical Spacer widget
            vertical_spacer1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            layout.addItem(vertical_spacer1)

            tab_widget.setLayout(layout)

        # Build dialog widgets
        tools_dr.build_dialog_options(
            self.dlg_go2epa_options, json_result['body']['form']['formTabs'], 0, self.epa_options_list)

        # Remove empty groups
        for group in self.dlg_go2epa_options.findChildren(QGroupBox):
            child_widgets = group.findChildren(QWidget)
            if not child_widgets:
                parent_layout = group.parentWidget().layout()
                parent_layout.removeWidget(group)
                group.deleteLater()

        # Event on change from combo parent
        self._get_event_combo_parent(json_result)
        self.dlg_go2epa_options.btn_accept.clicked.connect(partial(self._update_values, self.epa_options_list))
        self.dlg_go2epa_options.btn_cancel.clicked.connect(partial(tools_dr.close_dialog, self.dlg_go2epa_options))
        self.dlg_go2epa_options.rejected.connect(partial(tools_dr.close_dialog, self.dlg_go2epa_options))

        tools_dr.open_dialog(self.dlg_go2epa_options, dlg_name='go2epa_options')

    def _update_values(self, _json):

        _json = self._parse_values_json(_json)
        my_json = json.dumps(_json)
        form = '"formName":"epaoptions"'
        extras = f'"fields":{my_json}'
        body = tools_dr.create_body(form=form, extras=extras)
        json_result = tools_dr.execute_procedure('setconfig', body)
        if not json_result or json_result['status'] == 'Failed':
            return False

        tools_dr.manage_current_selections_docker(json_result)

        msg = "Values has been updated"
        tools_qgis.show_info(msg)
        # Close dialog
        tools_dr.close_dialog(self.dlg_go2epa_options)

    def _get_event_combo_parent(self, complet_result):

        for field in complet_result['body']['form']['formTabs'][0]["fields"]:
            if field['isparent']:
                widget = self.dlg_go2epa_options.findChild(QComboBox, field['widgetname'])
                if widget:
                    widget.currentIndexChanged.connect(partial(self._fill_child, self.dlg_go2epa_options, widget))

    def _fill_child(self, dialog, widget):

        combo_parent = widget.objectName()
        combo_id = tools_qt.get_combo_value(dialog, widget)
        # TODO cambiar por gw_fct_getchilds then unified with tools_dr.get_child if posible
        json_result = tools_dr.execute_procedure('gw_fct_getcombochilds', f"'epaoptions', '', '', '{combo_parent}', '{combo_id}', ''")
        if not json_result or json_result['status'] == 'Failed':
            return False

        for combo_child in json_result['fields']:
            if combo_child is not None:
                tools_dr.manage_combo_child(dialog, widget, combo_child)

    def _parse_values_json(self, _json: List[Dict[str, Any]]):

        format_str = "yyyy-MM-dd"

        for item in _json:
            if isinstance(item["value"], QDateTime):
                item["value"] = item["value"].toString(format_str)

        return _json
