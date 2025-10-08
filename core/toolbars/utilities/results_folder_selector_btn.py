"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
from functools import partial

from qgis.core import QgsProject

from ..dialog import DrAction
from ...ui.ui_manager import DrResultsFolderSelectorUi
from ...utils import tools_dr
from ....lib import tools_qt, tools_qgis, tools_os


class DrResultsFolderSelectorButton(DrAction):
    """ Button 20: Results Folder Selector """

    def __init__(self, icon_path, action_name, text, toolbar, action_group, results_btn):

        # Call ParentDialog constructor
        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.results_btn = results_btn

    def clicked_event(self):

        self.action.setChecked(True)

        # Set dialog
        self.dlg_results_folder_selector = DrResultsFolderSelectorUi()
        tools_dr.load_settings(self.dlg_results_folder_selector)

        # Set last parameters
        current_path = tools_qgis.get_project_variable('project_results_folder')
        if not current_path or not os.path.exists(current_path):
            tools_qt.set_widget_text(self.dlg_results_folder_selector, self.dlg_results_folder_selector.txt_folder_path,
                                    tools_dr.get_config_parser('btn_results_folder_selector', 'results_folder', "user", "session"))
        else:
            tools_qt.set_widget_text(self.dlg_results_folder_selector, self.dlg_results_folder_selector.txt_folder_path,
                                    current_path)

        self.dlg_results_folder_selector.btn_folder_path.clicked.connect(self._select_results_path)
        self.dlg_results_folder_selector.btn_accept.clicked.connect(self._save_results_folder)
        self.dlg_results_folder_selector.btn_cancel.clicked.connect(partial(tools_dr.close_dialog, self.dlg_results_folder_selector))
        self.dlg_results_folder_selector.rejected.connect(partial(tools_dr.close_dialog, self.dlg_results_folder_selector))

        # Show form
        tools_dr.open_dialog(self.dlg_results_folder_selector, dlg_name='results_folder_selector')

    # region private functions

    def _select_results_path(self):
        """ Open folder dialog and set path to textbox """
        path = tools_os.open_folder_path()
        if path:
            tools_qt.set_widget_text(self.dlg_results_folder_selector, 'txt_folder_path', str(path))

    def _save_results_folder(self):
        """ Save results folder """
        path = tools_qt.get_text(self.dlg_results_folder_selector, 'txt_folder_path')

        # Validate results folder
        validation_results = self.results_btn.validate_results_folder(path)
        if not validation_results[5]:
            msg = "Results folder is not valid"
            tools_qgis.show_warning(msg, dialog=self.dlg_results_folder_selector)
            return

        # Check if there are any results in the results folder
        result_data = any(validation_results[0:5])
        if not result_data:
            msg = "No results found in the folder"
            tools_qgis.show_warning(msg, dialog=self.dlg_results_folder_selector)
            return

        # Check if all results are valid
        if not all(validation_results[0:5]):
            msg = "The folder is missing data; some result buttons will be disabled"
            tools_qgis.show_info(msg)

        tools_dr.set_config_parser('btn_results_folder_selector', 'results_folder', path, "user", "session")
        # Save project path
        relative_path = os.path.relpath(path, QgsProject.instance().absolutePath())
        tools_qgis.set_project_variable('project_results_folder', relative_path)
        msg = "Results folder saved successfully"
        tools_qgis.show_info(msg)

        tools_dr.close_dialog(self.dlg_results_folder_selector)

    # endregion
