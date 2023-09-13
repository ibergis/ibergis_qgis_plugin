"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
import json

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

        # get widgets from sys_param_user
        column_names = ['id', 'label', 'descript', 'datatype', 'widgettype', 'layoutname', 'layoutorder', 'vdefault',
                        'placeholder', 'id AS widgetname', 'false AS isparent', 'tabname', 'dv_querytext',
                        'dv_orderby_id', 'dv_isnullvalue',
                        'CASE WHEN iseditable = 1 THEN True ELSE False END AS iseditable',
                        'CASE WHEN ismandatory = 1 THEN True ELSE False END AS ismandatory',
                        'CASE WHEN isenabled = 1 THEN True ELSE False END AS isenabled',
                        ]
        v_sql = f"SELECT {', '.join(column_names)} " \
                f"FROM sys_param_user " \
                f"ORDER BY layoutname, layoutorder, id"
        v_raw_widgets = global_vars.gpkg_dao_config.get_rows(v_sql)

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
        v_sql = f"SELECT parameter, value " \
                f"FROM config_param_user " \
                f"ORDER BY parameter"
        v_raw_values = global_vars.gpkg_dao_data.get_rows(v_sql)

        # Iterate through the raw values and update the corresponding widgets in v_widgets
        for row in v_raw_values:
            parameter, value = row
            for widget in v_widgets:
                if widget['widgettype'] == 'combo':
                    cmb_ids = []
                    cmb_names = []
                    if widget['dv_querytext']:
                        v_querystring = widget['dv_querytext'].replace('SELECT id, idval', 'SELECT group_concat(id)')
                        cmb_ids = global_vars.gpkg_dao_config.get_row(v_querystring)
                        v_querystring = widget['dv_querytext'].replace('SELECT id, idval', 'SELECT group_concat(idval)')
                        cmb_names = global_vars.gpkg_dao_config.get_row(v_querystring)
                    widget['comboIds'] = cmb_ids
                    widget['comboNames'] = cmb_names

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


def setconfig(p_input: dict) -> dict:
    accepted: bool = True
    v_return: dict = {}
    v_sql: str

    try:
        v_table = 'config_param_user'
        for field in p_input['data']['fields']:
            v_querystring = f"SELECT * FROM {v_table} WHERE parameter = '{field['widget']}'"
            result = global_vars.gpkg_dao_data.get_row(v_querystring)
            if result:
                v_sql = f"UPDATE {v_table} SET value = '{field['value']}' WHERE parameter = '{field['widget']}'"
                global_vars.gpkg_dao_data.execute_sql(v_sql)
            else:
                v_sql = f"INSERT INTO {v_table} (parameter, value) VALUES ('{field['widget']}', '{field['value']}')"
                global_vars.gpkg_dao_data.execute_sql(v_sql)
    except Exception as e:
        print(f"EXCEPTION IN setconfig: {e}")
        accepted = False

    v_return = _create_return(v_return, accepted=accepted)
    return v_return


def getselectors(p_input: dict) -> dict:
    accepted: bool = True
    v_return: dict = {}
    v_sql: str
    v_message: str
    v_fields_aux: {}
    v_fields: list
    v_raw_values: list

    try:

        v_return = _create_return(v_return, accepted=True, message="Process done successfully")
        v_return["body"]["form"]["currentTab"] = "tab_scenario"
        v_return["body"]["form"]["formTabs"] = []

        v_sql = f"SELECT parameter, value from config_param_user WHERE parameter like 'basic_selector_%'"
        rows = global_vars.gpkg_dao_data.get_rows(v_sql)

        for row in rows:
            tab_json = json.loads(row[1].replace('/',''))
            tabname = row[0].replace("basic_selector_", "")
            tabLabel = tabname.replace("tab_", "")
            table = tab_json["table"]
            selector = tab_json["selector"]
            table_id = tab_json["table_id"]
            selector_id = tab_json["selector_id"]
            label = tab_json["label"]
            orderBy = tab_json["orderBy"]
            manageAll = tab_json["manageAll"]
            query_filter = tab_json["query_filter"]
            typeaheadFilter = tab_json.get("typeaheadFilter")
            typeaheadForced = tab_json["typeaheadForced"]

            v_sql = f"SELECT {table_id} as {table_id}, {label} AS label, {orderBy} AS orderBy, {orderBy} AS name," \
                    f" cast({table_id} as text) AS widgetname, '{selector_id}' AS columnname, 'check' AS type, 'boolean' AS dataType, " \
                    f" CASE WHEN {table_id} IN (SELECT * FROM {selector}) THEN 'true' ELSE 'false' END AS value" \
                    f" from {table}"
            column_names = [f'{table_id}', 'label', 'orderBy', 'name', 'widgetname', 'columnname', 'type',
                            'dataType', 'value' ]
            rows_fields = global_vars.gpkg_dao_data.get_rows(v_sql)

            v_fields = []
            for row in rows_fields:
                widget_dict = {}
                for i, value in enumerate(row):
                    key = column_names[i]
                    widget_dict[key] = value
                v_fields.append(widget_dict)


            v_fields_aux = {
                'fields':v_fields,
                'tabName':f'{tabname}',
                'tableName':f'{selector}',
                'tabLabel': f'{tabLabel.capitalize()}',
                'tooltip': f'{tabLabel.capitalize()}',
                'selectorType': 'selector_basic',
                'manageAll': f'{manageAll}',
                'selectionMode': 'keepPrevious',
                'typeaheadForced':f'{typeaheadForced}'
            }

            if typeaheadFilter:
                v_fields_aux["typeaheadFilter"] = typeaheadFilter

            v_return["body"]["form"]["formTabs"].append(v_fields_aux)

        v_message="Process done succesfully."

    except Exception as e:
        print(f"EXCEPTION IN getselectors: {e}")
        accepted = False
        v_message = f"{e}"

    v_return = _create_return(v_return, accepted=accepted, message=v_message)
    return v_return


def setselectors(p_input: dict) -> dict:
    accepted: bool = True
    v_return: dict = {}
    v_sql: str
    v_message: str

    try:
        v_return = _create_return(v_return, accepted=True, message="Process done successfully")

        p_input = json.loads(p_input)
        checkAll = p_input['data'].get('checkAll')
        tabName = p_input['data'].get('tabName')
        id = p_input['data'].get('id')
        value = p_input['data'].get('value')

        v_sql = f"SELECT value from config_param_user WHERE parameter like 'basic_selector_{tabName}'"
        row = global_vars.gpkg_dao_data.get_row(v_sql)
        config_json = json.loads(row[0].replace('/', ''))

        selector_table = config_json["selector"]
        column_id = f"{selector_table.removeprefix('selector_')}_id"
        data_table = config_json["table"]
        data_table_id = config_json["table_id"]

        if checkAll is None and id:
            if value == 'True':
                v_sql = f"INSERT INTO {selector_table} VALUES({id})"
                global_vars.gpkg_dao_data.execute_sql(v_sql)
            else:
                v_sql = f"DELETE FROM {selector_table} WHERE {column_id}={id}"
                global_vars.gpkg_dao_data.execute_sql(v_sql)
        else:
            if checkAll == 'True':
                v_sql =f"INSERT INTO {selector_table} SELECT {data_table_id} FROM {data_table}"
                global_vars.gpkg_dao_data.execute_sql(v_sql)
            else:
                v_sql = f"DELETE FROM {selector_table} WHERE {column_id} IN (SELECT {data_table_id} FROM {data_table})"
                global_vars.gpkg_dao_data.execute_sql(v_sql)


        v_sql =f"SELECT {column_id} FROM {selector_table}"
        rows = global_vars.gpkg_dao_data.get_rows(v_sql)
        id_list = [row[0] for row in rows]

        v_return["body"]["data"]["filter_ids"] = id_list
        v_return["body"]["data"]["column_id"] = column_id

        v_message = "Process done succesfully."

    except Exception as e:
        print(f"EXCEPTION IN setselectors: {e}")
        accepted = False
        v_message = f"{e}"

    v_return = _create_return(v_return, accepted=accepted, message=v_message)
    return v_return

def get_sectors():
    sectors = 'NULL'

    sql = f'SELECT sector_id FROM selector_sector'
    rows = global_vars.gpkg_dao_data.get_rows(sql)
    if rows:
        sectors = ", ".join(str(x[0]) for x in rows)

    return sectors

def get_scenarios():
    scenarios = 'NULL'

    sql = f'SELECT scenario_id FROM selector_scenario'
    rows = global_vars.gpkg_dao_data.get_rows(sql)
    if rows:
        scenarios = ", ".join(str(x[0]) for x in rows)

    return scenarios

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
