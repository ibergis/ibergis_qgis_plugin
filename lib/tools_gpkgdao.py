"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import sqlite3

from qgis.PyQt.QtSql import QSqlDatabase


class GwGpkgDao(object):

    def __init__(self):

        self.last_error = None
        self.db_filepath = None
        self.conn = None
        self.cursor = None
        self.db_qsql = None


    def init_db(self, filename, enable_spatial=True):
        """ Initializes database connection (sqlite3) """

        if filename is None:
            self.last_error = f"Database file path is not set"
            return False
        if not os.path.exists(filename):
            self.last_error = f"Database not found: {filename}"
            return False

        self.db_filepath = filename
        try:
            self.conn = sqlite3.connect(filename)
            if enable_spatial:
                self.conn.enable_load_extension(True)
                self.conn.execute("SELECT load_extension('mod_spatialite')")
                self.conn.enable_load_extension(False)
            self.cursor = self.get_cursor()
            status = True
        except Exception as e:
            self.last_error = e
            status = False

        return status


    def close_db(self):
        """ Close database connection """

        try:
            status = True
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            del self.cursor
            del self.conn
        except Exception as e:
            self.last_error = e
            status = False

        return status


    def get_cursor(self):

        cursor = self.conn.cursor()
        return cursor


    def check_cursor(self):
        """ Check if cursor is closed """

        status = True
        if self.cursor.closed:
            self.init_db()
            status = not self.cursor.closed

        return status


    def cursor_execute(self, sql):
        """ Check if cursor is closed before execution """

        if self.check_cursor():
            self.cursor.execute(sql)


    def get_rows(self, sql, commit=False):
        """ Get multiple rows from selected query """

        self.last_error = None
        rows = None
        try:
            cursor = self.get_cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception as e:
            self.last_error = e
        finally:
            return rows


    def get_row(self, sql, commit=False, aux_conn=None):
        """ Get single row from selected query """

        self.last_error = None
        row = None
        try:
            self.cursor_execute(sql)
            row = self.cursor.fetchone()
        except Exception as e:
            self.last_error = e
        finally:
            return row


    def execute_sql(self, sql, commit=True):
        """ Execute selected query """

        self.last_error = None
        status = True
        try:
            cursor = self.get_cursor()
            cursor.execute(sql)
        except Exception as e:
            self.last_error = e
            status = False
        finally:
            return status

    def execute_script_sql(self, sql, commit=True):
        """ Execute selected query """

        self.last_error = None
        status = True
        try:
            cursor = self.get_cursor()
            cursor.executescript(sql)
        except Exception as e:
            self.last_error = e
            status = False
        finally:
            return status


    def init_qsql_db(self, filepath, database_name):
        """ Initializes database connection (QSqlDatabase) """

        # Add the GeoPackage database to QSqlDatabase
        db_qsql = QSqlDatabase.addDatabase("QSQLITE", database_name)
        db_qsql.setDatabaseName(filepath)
        db_qsql.open()
        status = db_qsql.isOpen()
        if not status:
            error = db_qsql.lastError()
            self.last_error = error.text()

        self.db_qsql = db_qsql
        return status, db_qsql

