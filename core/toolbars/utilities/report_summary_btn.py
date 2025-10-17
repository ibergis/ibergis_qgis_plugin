"""
This file is part of IberGIS
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from typing import Optional

from qgis.PyQt.QtWidgets import QTableWidgetItem

from ..dialog import DrAction
from ...ui.ui_manager import DrReportSummaryUi
from ...utils import tools_dr
from ....lib import tools_qt, tools_qgis, tools_os
from ....lib.tools_gpkgdao import DrGpkgDao
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QTableView


@dataclass(frozen=True)
class RptSummaryConfig:
    topic: str
    table_name: str
    field_labels: dict[str, Optional[str]]


class DrReportSummaryButton(DrAction):
    """ Button 18: Report Summary """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        # Call ParentDialog constructor
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.folder_path = None
        self.dao = DrGpkgDao()
        self.configs: list[RptSummaryConfig] = [
            RptSummaryConfig(
                topic='Node Depth',
                table_name='rpt_nodedepth_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'aver_depth': 'Average Depth Meters',
                    'max_depth': 'Maximum Depth Meters',
                    'max_hgl': 'Maximum HGL Meters',
                    'time_days': 'Day of Maximum Depth',
                    'time_hour': 'Hour of Maximum Depth',
                },
            ),
            RptSummaryConfig(
                topic='Node Inflow',
                table_name='rpt_nodeinflow_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'max_latinf': 'Maximum Lateral Inflow CMS',
                    'max_totinf': 'Maximum Total Inflow CMS',
                    'time_days': 'Day of Maximum Inflow',
                    'time_hour': 'Hour of Maximum Inflow',
                    'latinf_vol': 'Lateral Inflow Volume 10^6 ltr',
                    'totinf_vol': 'Total Inflow Volume 10^6 ltr',
                    'flow_balance_error': 'Flow Balance Error %',
                },
            ),
            RptSummaryConfig(
                topic='Node Surcharge',
                table_name='rpt_nodesurcharge_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'hour_surch': 'Hours Surcharged',
                    'max_height': 'Max Height Above Crown Meters',
                    'min_depth': 'Min Depth Below Rim Meters',
                },
            ),
            RptSummaryConfig(
                topic='Node Flooding',
                table_name='rpt_nodeflooding_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'hour_flood': 'Hours Flooded',
                    'max_rate': 'Maximum Rate CMS',
                    'time_days': 'Day of Maximum Flooding',
                    'time_hour': 'Hour of Maximum Flooding',
                    'tot_flood': 'Total Flood Volume 10^6 ltr',
                    'max_ponded': 'Maximum Ponded Depth Meters',
                },
            ),
            RptSummaryConfig(
                topic='Storage Volume',
                table_name='rpt_storagevol_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'aver_vol': 'Average Volume 1000 m3',
                    'avg_full': 'Average Percent Full',
                    'evap_loss': 'Evaporation Loss %',
                    'exfil_loss': 'Exfiltration Loss %',
                    'max_vol': 'Maximum Volume 1000 m3',
                    'max_full': 'Maximum Percent Full',
                    'time_days': 'Day of Maximum Volume',
                    'time_hour': 'Hour of Maximum Volume',
                    'max_out': 'Maximum Outflow CMS',
                },
            ),
            RptSummaryConfig(
                topic='Outfall Loading',
                table_name='rpt_outfallflow_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'flow_freq': 'Flow Frequency %',
                    'avg_flow': 'Average Flow CMS',
                    'max_flow': 'Maximum Flow CMS',
                    'total_vol': 'Total Volume 10^6 ltr',
                },
            ),
            RptSummaryConfig(
                topic='Link Flow',
                table_name='rpt_arcflow_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'max_flow': 'Maximum|Flow|CMS',
                    'time_days': 'Day of Maximum Flow',
                    'time_hour': 'Hour of Maximum Flow',
                    'max_veloc': 'Maximum|Velocity|m/sec',
                    'mfull_flow': 'Max / Full_Flow',
                    'mfull_dept': 'Max / Full_Depth',
                },
            ),
            RptSummaryConfig(
                topic='Flow Classification',
                table_name='rpt_flowclass_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'length': 'Adjusted/Actual Length',
                    'dry': 'Fully Dry',
                    'up_dry': 'Upstrm Dry',
                    'down_dry': 'Dnstrm Dry',
                    'sub_crit': 'Sub Critical',
                    'sub_crit_1': 'Super Critical',
                    'up_crit': 'Upstrm Critical',
                    'down_crit': 'Dnstrm Critical',
                    'norm_ltd': 'Normal Flow Limited',
                    'inlet_ctrl': 'Inlet Control',
                },
            ),
            RptSummaryConfig(
                topic='Conduit Surcharge',
                table_name='rpt_condsurcharge_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'both_ends': 'Hours Both Ends Full',
                    'upstream': 'Hours Upstream Full',
                    'dnstream': 'Hours Downstream Full',
                    'hour_nflow': 'Hours Above Normal Flow',
                    'hour_limit': 'Hours Capacity Limited',
                },
            ),
            RptSummaryConfig(
                topic='Pumping',
                table_name='rpt_pumping_sum',
                field_labels={
                    'code': 'Code',
                    'epa_type': 'Type',
                    'percent': 'Percent Utilized',
                    'num_startup': 'Number of Start-Ups',
                    'min_flow': 'Minimum Flow CMS',
                    'avg_flow': 'Average Flow CMS',
                    'max_flow': 'Maximum Flow CMS',
                    'vol_ltr': 'Total Volume 10^6 ltr',
                    'powus_kwh': 'Power Usage Kw-hr',
                    'timoff_min': '% Time Below Pump Curve',
                    'timoff_max': '% Time Above Pump Curve',
                },
            ),
        ]

    def clicked_event(self):

        self.action.setChecked(True)

        # Set dialog
        self.dlg_report_summary = DrReportSummaryUi()
        tools_dr.load_settings(self.dlg_report_summary)

        # Get results folder
        self.folder_path = tools_qgis.get_project_variable('project_results_folder')
        if self.folder_path is None:
            tools_qgis.show_warning("No results folder selected")
            return
        self.folder_path = os.path.abspath(f"{QgsProject.instance().absolutePath()}{os.sep}{self.folder_path}")
        if not os.path.exists(self.folder_path) or not os.path.isdir(self.folder_path):
            tools_qgis.show_warning("Invalid results folder")
            return
        if not os.path.exists(os.path.join(self.folder_path, 'IberGisResults', 'results.gpkg')) or \
                not os.path.exists(os.path.join(self.folder_path, 'Iber_SWMM.rpt')):
            tools_qgis.show_warning("No results.gpkg or Iber_SWMM.rpt file found")
            return

        # Init dao
        self.dao.init_db(os.path.join(self.folder_path, 'IberGisResults', 'results.gpkg'))

        # Populate widgets
        self._populate_widgets()

        # Set signals
        self.dlg_report_summary.cmb_topic.currentIndexChanged.connect(self._fill_tableview)
        self.dlg_report_summary.finished.connect(self._on_close_dialog)

        # Show form
        tools_dr.open_dialog(self.dlg_report_summary, dlg_name='report_summary')

    # region private functions

    def _on_close_dialog(self):
        """ Close dialog """

        self.dao.close_db()
        tools_dr.close_dialog(self.dlg_report_summary)

    def _populate_widgets(self):
        """ Populate widgets """

        # Populate combo
        cmb_topic = self.dlg_report_summary.cmb_topic
        for idx, cfg in enumerate(self.configs):
            cmb_topic.addItem(cfg.topic, str(idx))

        # Set tableview config
        tbl_summary = self.dlg_report_summary.tbl_summary
        tools_qt.set_tableview_config(tbl_summary, edit_triggers=QTableView.NoEditTriggers)

        # Fill tableview
        self._fill_tableview()

    def _fill_tableview(self, index=None):
        """ Fill tableview """

        topic_id = tools_qt.get_combo_value(self.dlg_report_summary, self.dlg_report_summary.cmb_topic)
        if topic_id is None:
            tools_qgis.show_warning("Invalid topic")
            return
        idx = int(topic_id)
        if idx < 0 or idx >= len(self.configs):
            tools_qgis.show_warning("Invalid topic")
            return
        cfg = self.configs[idx]

        # Get tableview
        tbl_summary = self.dlg_report_summary.tbl_summary
        tbl_summary.setRowCount(0)
        tbl_summary.setColumnCount(0)

        sql = f"SELECT * FROM {cfg.table_name}"
        rows = self.dao.get_rows(sql)
        if not rows:
            tools_qgis.show_warning("No data found")
            return

        # Get valid fields (only those that are not None in the config)
        valid_fields = []
        for field in rows[0].keys():
            if field in cfg.field_labels.keys() and cfg.field_labels[field] is not None:
                valid_fields.append(field)

        # Set table dimensions
        tbl_summary.setRowCount(len(rows))
        tbl_summary.setColumnCount(len(valid_fields))

        # Set headers
        for col_idx, field in enumerate(valid_fields):
            header_label = cfg.field_labels[field]
            tbl_summary.setHorizontalHeaderItem(col_idx, QTableWidgetItem(header_label))

        # Populate table data
        for row_idx, row_data in enumerate(rows):
            for col_idx, field in enumerate(valid_fields):
                value = row_data[field]
                if value is None:
                    value = ''
                tbl_summary.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def _select_results_path(self):
        """ Open folder dialog and set path to textbox """
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.dlg_draw_profile, 'txt_results_folder', str(path))

    # endregion
