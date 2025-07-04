"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic, QtCore

from .dialog import DrDialog
from .main_window import DrMainWindow

# region private functions


def _get_ui_class(ui_file_name, subfolder='shared'):
    """ Get UI Python class from @ui_file_name """

    # Folder that contains UI files
    if subfolder in ('main', 'utilities'):
        ui_folder_path = os.path.dirname(__file__) + os.sep + 'toolbars' + os.sep + subfolder
    else:
        ui_folder_path = os.path.dirname(__file__) + os.sep + subfolder

    ui_file_path = os.path.abspath(os.path.join(ui_folder_path, ui_file_name))
    return uic.loadUiType(ui_file_path)[0]

# endregion


# region main
FORM_CLASS = _get_ui_class('go2epa.ui', 'main')


class DrGo2EpaUI(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('go2epa_options.ui', 'main')


class DrGo2EpaOptionsUi(DrDialog, FORM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_curve.ui', 'main')


class DrNonVisualCurveUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_controls.ui', 'main')


class DrNonVisualControlsUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_manager.ui', 'main')


class DrNonVisualManagerUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_print.ui', 'main')


class DrNonVisualPrint(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_pattern_ud.ui', 'main')


class DrNonVisualPatternUDUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_timeseries.ui', 'main')


class DrNonVisualTimeseriesUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_lids.ui', 'main')


class DrNonVisualLidsUi(DrDialog, FROM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_raster.ui', 'main')


class DrNonVisualRasterUi(DrDialog, FROM_CLASS):
    pass


FORM_CLASS = _get_ui_class('csv.ui', 'utilities')


class DrCsvUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('toolbox_reports.ui', 'utilities')


class DrToolboxReportsUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('import_inp.ui', 'utilities')


class DrImportInpUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('execute_model.ui', 'utilities')


class DrExecuteModelUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('mesh_selector.ui', 'utilities')


class DrMeshSelectorUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('create_mesh.ui', 'utilities')


class DrCreateMeshUi(DrDialog, FORM_CLASS):
    pass


FROM_CLASS = _get_ui_class('nonvisual_import_raster.ui', 'main')


class DrNonVisualRasterImportUi(DrDialog, FROM_CLASS):
    pass

FROM_CLASS = _get_ui_class('bridge.ui', 'main')


class DrBridgeUi(DrDialog, FROM_CLASS):
    pass

# endregion


# region ADMIN
FORM_CLASS = _get_ui_class('admin_ui.ui', 'admin')


class DrAdminUi(DrMainWindow, FORM_CLASS):
    dlg_closed = QtCore.pyqtSignal()


FORM_CLASS = _get_ui_class('admin_translation.ui', 'admin')


class DrAdminTranslationUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('admin_update_translation.ui', 'admin')


class DrSchemaI18NUpdateUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('admin_i18n_manager.ui', 'admin')


class DrSchemaI18NManagerUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('toolbox.ui', 'utilities')


class DrToolboxUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('toolbox_tool.ui', 'utilities')


class DrToolboxManagerUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('bc_scenario_manager.ui', 'utilities')


class DrBCScenarioManagerUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('bc_scenario.ui', 'utilities')


class DrBCScenarioUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('bc_form.ui', 'utilities')


class DrBCFormUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('mesh_manager.ui', 'utilities')


class DrMeshManagerUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('project_check.ui', 'utilities')


class DrProjectCheckUi(DrDialog, FORM_CLASS):
    pass


UINAME = "profile"
FORM_CLASS = _get_ui_class(f'{UINAME}.ui', 'utilities')


class DrProfileUi(DrMainWindow, FORM_CLASS):
    pass


UINAME = "profile_list"
FORM_CLASS = _get_ui_class(f'{UINAME}.ui', 'utilities')


class DrProfilesListUi(DrDialog, FORM_CLASS):
    pass


# endregion


# region SHARED
FORM_CLASS = _get_ui_class('replace_in_file.ui')


class DrReplaceInFileUi(DrDialog, FORM_CLASS):
    pass


FORM_CLASS = _get_ui_class('dlg_lineedit.ui')


class DrLineeditUi(DrDialog, FORM_CLASS):
    pass

# endregion
