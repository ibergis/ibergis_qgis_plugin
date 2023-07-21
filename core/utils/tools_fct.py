"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from ... import global_vars
from ...lib import tools_gpkgdao, tools_qgis, tools_qt, tools_db


def getconfig(p_input: dict) -> dict:
    accepted: bool = True
    v_return: dict = {}
    v_sql: str
    v_raw_widgets: list
    v_widgets: list
    v_raw_values: list

    try:
        print(f"getconfig")
        print(f"{p_input}")

        # get widgets from sys_param_user
        column_names = ['id', 'label', 'descript', 'datatype', 'widgettype', 'layoutname', 'layoutorder', 'vdefault',
                        'isenabled', 'ismandatory', 'iseditable', 'placeholder', 'id AS widgetname', 'false AS isparent']
        v_sql = f"SELECT {', '.join(column_names)} " \
                f"FROM sys_param_user " \
                f"ORDER BY layoutname, layoutorder, id"
        v_raw_widgets = global_vars.gpkg_dao_config.get_rows(v_sql)
        print(f"{v_raw_widgets=}")
        print(f"{global_vars.gpkg_dao_config.last_error=}")
        # format widgets as a json
        v_widgets = []
        for row in v_raw_widgets:
            widget_dict = {}
            for i, value in enumerate(row):
                key = column_names[i]
                if ' AS ' in key:
                    key = key.split(' AS ')[1]
                widget_dict[key] = value
            v_widgets.append(widget_dict)

        # put values into widgets
        v_sql = f"SELECT parameter_id, parameter, value " \
                f"FROM config_param_user " \
                f"ORDER BY parameter, parameter_id"
        v_raw_values = global_vars.gpkg_dao_data.get_rows(v_sql)
        print(f"{v_raw_values=}")
        print(f"{global_vars.gpkg_dao_config.last_error=}")

        # Iterate through the raw values and update the corresponding widgets in v_widgets
        for row in v_raw_values:
            parameter_id, parameter, value = row
            for widget in v_widgets:
                if widget['id'] == parameter:
                    widget['value'] = value
                    break

        # return
        v_return["body"] = {"data": {}, "form": {}}
        v_return["body"]["data"] = {
            "fields": v_widgets
        }
        v_return["body"]["form"]["formTabs"] = [
            {
                "fields": v_widgets
            }
        ]
    except Exception as e:
        print(f"EXCEPTION IN getconfig: {e}")
        accepted = False

    v_return = _create_return(v_return, accepted=accepted)
    return v_return


def _create_return(p_data: dict, accepted: bool = True, message: str = "") -> dict:
    """ Creates a return json & ensures that the format is consistent """

    v_return: dict = p_data
    v_message: dict = {"level": 1 if accepted else 2, "message": message}

    # status
    v_return.setdefault("status", "Accepted" if accepted else "Failed")
    # message
    if message:
        v_return.setdefault("message", v_message)
    # body
    v_return.setdefault("body", {"form": {}, "feature": {}, "data": {}})
    # form
    v_return["body"].setdefault("form", {})
    # feature
    v_return["body"].setdefault("feature", {})
    # data
    v_return["body"].setdefault("data", {})

    return v_return
