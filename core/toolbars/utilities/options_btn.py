"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from ..dialog import DrAction
from ...shared.options import DrOptions


class DrOptionsButton(DrAction):
    """ Button 99: Options """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):

        self._open_options()

    # region private functions

    def _open_options(self):

        self.options = DrOptions()
        self.options.open_options_dlg()

    # endregion
