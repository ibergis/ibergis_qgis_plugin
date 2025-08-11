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

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        # Call ParentDialog constructor
        super().__init__(icon_path, action_name, text, toolbar, action_group)

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
        if path and os.path.exists(path) and os.path.isdir(path):
            tools_dr.set_config_parser('btn_results_folder_selector', 'results_folder', path, "user", "session")
            # Save project path
            relative_path = os.path.relpath(path, QgsProject.instance().absolutePath())
            tools_qgis.set_project_variable('project_results_folder', relative_path)
            tools_qgis.show_info("Results folder saved successfully")
        else:
            tools_qgis.show_warning("Results folder is not valid", dialog=self.dlg_results_folder_selector)
            return

        tools_dr.close_dialog(self.dlg_results_folder_selector)

    # endregion
