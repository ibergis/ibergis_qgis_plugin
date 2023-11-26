from ..dialog import GwAction
from ...ui.ui_manager import GwBCScenarioManagerUi
from ...utils import tools_gw


class GwBCScenarioManagerButton(GwAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dlg = GwBCScenarioManagerUi()
        tools_gw.open_dialog(self.dlg, dlg_name="bc_scenario_manager")
