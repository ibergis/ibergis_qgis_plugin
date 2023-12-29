"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os

from qgis.core import QgsProject
from qgis.PyQt import uic, QtCore

from .dialog import GwDialog
from .main_window import GwMainWindow
from ...lib import tools_qgis, tools_qt

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
class GwGo2EpaUI(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('go2epa_options.ui', 'main')
class GwGo2EpaOptionsUi(GwDialog, FORM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_curve.ui', 'main')
class GwNonVisualCurveUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_controls.ui', 'main')
class GwNonVisualControlsUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_manager.ui', 'main')
class GwNonVisualManagerUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_pattern_ws.ui', 'main')
class GwNonVisualPatternWSUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_print.ui', 'main')
class GwNonVisualPrint(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_rules.ui', 'main')
class GwNonVisualRulesUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_pattern_ud.ui', 'main')
class GwNonVisualPatternUDUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_timeseries.ui', 'main')
class GwNonVisualTimeseriesUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_lids.ui', 'main')
class GwNonVisualLidsUi(GwDialog, FROM_CLASS):
    pass
FROM_CLASS = _get_ui_class('nonvisual_raster.ui', 'main')
class GwNonVisualRasterUi(GwDialog, FROM_CLASS):
    pass
FORM_CLASS = _get_ui_class('csv.ui', 'utilities')
class GwCsvUi(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('toolbox_reports.ui', 'utilities')
class GwToolboxReportsUi(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('import_inp.ui', 'utilities')
class GwImportInpUi(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('execute_model.ui', 'utilities')
class GwExecuteModelUi(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('mesh_selector.ui', 'utilities')
class GwMeshSelectorUi(GwDialog, FORM_CLASS):
    pass
FORM_CLASS = _get_ui_class('create_mesh.ui', 'utilities')
class GwCreateMeshUi(GwDialog, FORM_CLASS):
    pass
# endregion


# region ADMIN
FORM_CLASS = _get_ui_class('admin_ui.ui', 'admin')
class GwAdminUi(GwMainWindow, FORM_CLASS):
    dlg_closed = QtCore.pyqtSignal()

FORM_CLASS = _get_ui_class('toolbox.ui', 'utilities')
class GwToolboxUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('toolbox_tool.ui', 'utilities')
class GwToolboxManagerUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('bc_scenario_manager.ui', 'utilities')
class GwBCScenarioManagerUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('bc_scenario.ui', 'utilities')
class GwBCScenarioUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('bc_form.ui', 'utilities')
class GwBCFormUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('mesh_manager.ui', 'utilities')
class GwMeshManagerUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = _get_ui_class('project_check.ui', 'utilities')
class GwProjectCheckUi(GwDialog, FORM_CLASS):
    pass
# endregion


# region SHARED
FORM_CLASS = _get_ui_class('replace_in_file.ui')
class GwReplaceInFileUi(GwDialog, FORM_CLASS):
    pass

# endregion
