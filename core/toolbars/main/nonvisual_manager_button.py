"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from ..dialog import DrAction
from ...shared.nonvisual import DrNonVisual
from ...utils import tools_dr


class DrNonVisualManagerButton(DrAction):
    """ Button 218: Non visual objects manager """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.nonvisual = DrNonVisual()

    def clicked_event(self):
        # Return if theres one nonvisual manager dialog already open
        if tools_dr.check_if_already_open('manager_dlg', self.nonvisual):
            return
        self.nonvisual.manage_nonvisual()
