"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import shutil

from ...lib import tools_log, tools_qt, tools_qgis
from ... import global_vars


class GwGisFileCreate:

    def __init__(self, plugin_dir):

        self.plugin_dir = plugin_dir
        self.layer_source = None


    def gis_project_database(self, folder_path, filename, gpkg_file, srid, roletype='admin'):

        # Get locale of QGIS application
        locale = tools_qgis.get_locale()

        # Get folder with QGS templates
        gis_extension = "qgs"
        gis_folder = os.path.join(self.plugin_dir, "resources", "templates", "qgisproject")
        gis_locale_path = os.path.join(gis_folder, locale)

        # If QGIS template locale folder not found, use English one
        if not os.path.exists(gis_locale_path):
            tools_log.log_info("Locale gis folder not found", parameter=gis_locale_path)
            gis_locale_path = os.path.join(gis_folder, "en_US")

        # Check if template_path and folder_path exists
        template_path = os.path.join(gis_locale_path, f"{roletype}.{gis_extension}")
        if not os.path.exists(template_path):
            tools_qgis.show_warning("Template GIS file not found", parameter=template_path, duration=20)
            return False, None

        # Manage default parameters
        if folder_path is None:
            folder_path = gis_locale_path

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        # Set QGS file path
        qgs_path = folder_path + os.sep + filename + "." + gis_extension
        if os.path.exists(qgs_path):
            message = "Do you want to overwrite file?"
            answer = tools_qt.show_question(message, "overwrite file", force_action=True)
            if not answer:
                return False, qgs_path

        # Create destination file from template file
        tools_log.log_info(f"Creating GIS file... {qgs_path}")
        shutil.copyfile(template_path, qgs_path)

        # Set layer source parameters
        self.layer_source = {}
        if srid is None:
            srid = "25831"
        self.layer_source['srid'] = srid
        self.layer_source['gpkg_filepath'] = gpkg_file

        # Read file content
        with open(qgs_path) as f:
            content = f.read()

        content = self._replace_spatial_parameters(self.layer_source['srid'], content)
        content = self._replace_extent_parameters(content)
        content = self._replace_connection_parameters(content, self.layer_source['gpkg_filepath'])

        # Write contents and show message
        try:
            with open(qgs_path, "w") as f:
                f.write(content)
            tools_qgis.show_info("GIS file generated successfully", parameter=qgs_path)
            message = "Do you want to open GIS project?"
            answer = tools_qt.show_question(message, "GIS file generated successfully", force_action=True)
            if answer:
                return True, qgs_path
            return False, qgs_path
        except IOError:
            message = "File cannot be created. Check if it is already opened"
            tools_qgis.show_warning(message, parameter=qgs_path)


    # region private functions

    def _replace_spatial_parameters(self, srid, content):

        aux = content
        sql = (f"SELECT srid, auth_name || ':' || auth_id as auth_id "
               f"FROM srs "
               f"WHERE srid = '{srid}'")
        row = global_vars.gpkg_dao_config.get_row(sql)
        if row:
            aux = aux.replace("__SRSID__", str(row[0]))
            aux = aux.replace("__SRID__", str(row[0]))
            aux = aux.replace("__AUTHID__", row[1])
        else:
            tools_log.log_info(f"Database error: {global_vars.gpkg_dao_config.last_error}")

        return aux


    def _replace_extent_parameters(self, content):

        aux = content
        table_name = "polygon"
        sql = (f"SELECT max(ST_MaxX(geom)), min(ST_MinX(geom)), max(ST_MaxY(geom)), min(ST_MinY(geom)) "
               f"FROM {table_name}")
        row = global_vars.gpkg_dao_data.get_row(sql)
        if row:

            valor = row[0]
            if valor is None:
                valor = 1.555992
            aux = aux.replace("__XMAX__", str(valor))

            valor = row[1]
            if valor is None:
                valor = -1.555992
            aux = aux.replace("__XMIN__", str(valor))

            valor = row[2]
            if valor is None:
                valor = 1.000000
            aux = aux.replace("__YMAX__", str(valor))

            valor = row[3]
            if valor is None:
                valor = -1.000000
            aux = aux.replace("__YMIN__", str(valor))

        else:
            tools_log.log_info(f"Database error: {global_vars.gpkg_dao_data.last_error}")

        return aux


    def _replace_connection_parameters(self, content, filename):

        content = content.replace("__DATASOURCE__", filename)
        return content

    # endregion
