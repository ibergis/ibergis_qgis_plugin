"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras


class GwPgDao(object):

    def __init__(self):

        self.last_error = None
        self.set_search_path = None
        self.conn = None
        self.cursor = None
        self.pid = None


    def get_cursor(self, aux_conn=None):

        if aux_conn:
            cursor = aux_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return cursor


    def get_rows(self, sql, commit=False):
        """ Get multiple rows from selected query """

        self.last_error = None
        rows = None
        try:
            cursor = self.get_cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            if commit:
                self.commit()
        except Exception as e:
            self.last_error = e
            if commit:
                self.rollback()
        finally:
            return rows


    def get_row(self, sql, commit=False, aux_conn=None):
        """ Get single row from selected query """

        self.last_error = None
        row = None
        try:
            if aux_conn is not None:
                cursor = self.get_cursor(aux_conn)
                cursor.execute(sql)
                row = cursor.fetchone()
            else:
                self.cursor.execute(sql)
                row = self.cursor.fetchone()
            if commit:
                self.commit(aux_conn)
        except Exception as e:
            self.last_error = e
            if commit:
                self.rollback(aux_conn)
        finally:
            return row


    def execute_sql(self, sql, commit=True):
        """ Execute selected query """

        self.last_error = None
        status = True
        try:
            cursor = self.get_cursor()
            cursor.execute(sql)
            if commit:
                self.commit()
        except Exception as e:
            self.last_error = e
            status = False
            if commit:
                self.rollback()
        finally:
            return status


    def commit(self, aux_conn=None):
        """ Commit current database transaction """

        try:
            if aux_conn is not None:
                aux_conn.commit()
                return
            self.conn.commit()
        except Exception:
            pass


    def rollback(self, aux_conn=None):
        """ Rollback current database transaction """

        try:
            if aux_conn is not None:
                aux_conn.rollback()
                return
            self.conn.rollback()
        except Exception:
            pass

