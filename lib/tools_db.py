"""
This file is part of IberGIS
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri

from .. import global_vars
from . import tools_log, tools_qt


def get_row(sql, log_info=True, log_sql=False, commit=True, aux_conn=None, is_thread=False):

    dao = global_vars.gpkg_dao_data
    if log_sql:
        tools_log.log_db(sql, bold='b', stack_level_increase=2)
    row = dao.get_row(sql, commit, aux_conn=aux_conn)
    global_vars.session_vars['last_error'] = dao.last_error

    if not row:
        # Check if any error has been raised
        if global_vars.session_vars['last_error'] and not is_thread:
            tools_qt.manage_exception_db(global_vars.session_vars['last_error'], sql)
        elif global_vars.session_vars['last_error'] is None and log_info:
            msg = "Any record found"
            tools_log.log_info(msg, parameter=sql, stack_level_increase=1)

    return row


def get_rows(sql, log_info=True, log_sql=False, commit=True, add_empty_row=False, is_thread=False):
    """ Execute SQL. Check its result in log tables, and show it to the user """

    dao = global_vars.gpkg_dao_data
    if log_sql:
        tools_log.log_db(sql, bold='b', stack_level_increase=2)
    rows = None
    rows2 = dao.get_rows(sql, commit)
    global_vars.session_vars['last_error'] = dao.last_error
    if not rows2:
        # Check if any error has been raised
        if global_vars.session_vars['last_error'] and not is_thread:
            tools_qt.manage_exception_db(global_vars.session_vars['last_error'], sql)
        elif global_vars.session_vars['last_error'] is None and log_info:
            msg = "Any record found"
            tools_log.log_info(msg, parameter=sql, stack_level_increase=1)
    else:
        if add_empty_row:
            rows = [('', '')]
            rows.extend(rows2)
        else:
            rows = rows2

    return rows


def execute_sql(sql, log_sql=False, log_error=False, commit=True, filepath=None, is_thread=False, show_exception=True):
    """ Execute SQL. Check its result in log tables, and show it to the user """

    dao = global_vars.gpkg_dao_data
    if log_sql:
        tools_log.log_db(sql, stack_level_increase=1)
    result = dao.execute_sql(sql, commit)
    global_vars.session_vars['last_error'] = dao.last_error
    if not result:
        if log_error:
            tools_log.log_info(sql, stack_level_increase=1)
        if show_exception and not is_thread:
            tools_qt.manage_exception_db(global_vars.session_vars['last_error'], sql, filepath=filepath)
        return False

    return True


def execute_sql_placeholder(sql, data, commit=True):
    """ Execute selected query """

    dao = global_vars.gpkg_dao_data
    dao.last_error = None
    status = True
    try:
        cursor = dao.get_cursor()
        cursor.execute(sql, data)
    except Exception as e:
        dao.last_error = e
        status = False
        dao.conn.rollback()
    finally:
        if status:
            dao.conn.commit()
        return status


def check_function(function_name, schema_name=None, commit=True, aux_conn=None):
    """ Check if @function_name exists in selected schema """

    if schema_name is None:
        schema_name = global_vars.schema_name

    schema_name = schema_name.replace('"', '')
    sql = (f"SELECT routine_name "
           f"FROM information_schema.routines "
           f"WHERE lower(routine_schema) = '{schema_name}' "
           f"AND lower(routine_name) = '{function_name}'")
    row = get_row(sql, commit=commit, aux_conn=aux_conn)
    return row


def get_uri():
    """ Set the component parts of a RDBMS data source URI
    :return: QgsDataSourceUri() with the connection established according to the parameters of the credentials.
    """

    uri = QgsDataSourceUri()
    if global_vars.dao_db_credentials['service']:
        uri.setConnection(global_vars.dao_db_credentials['service'], global_vars.dao_db_credentials['db'],
                          global_vars.dao_db_credentials['user'], global_vars.dao_db_credentials['password'])
    else:
        uri.setConnection(global_vars.dao_db_credentials['host'], global_vars.dao_db_credentials['port'],
                          global_vars.dao_db_credentials['db'], global_vars.dao_db_credentials['user'],
                          global_vars.dao_db_credentials['password'])

    return uri
