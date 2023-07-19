/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- ---------------------------
-- INSERTS INTO SYS GPKG TABLES
-- ---------------------------

INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('sys_selector', 'attributes', 'sys_selector', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('sys_parameter', 'attributes', 'sys_parameter', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('sys_typevalue', 'attributes', 'sys_typevalue', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_scenario', 'attributes', 'cat_scenario', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_landuses', 'attributes', 'inp_landuses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_landuses_value', 'attributes', 'inp_landuses_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_curves', 'attributes', 'inp_curves', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_curves_value', 'attributes', 'inp_curves_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_timeseries', 'attributes', 'inp_timeseries', '',  0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_timeseries_value', 'attributes', 'inp_timeseries_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_losses', 'attributes', 'inp_losses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_losses_values', 'attributes', 'inp_losses_values', '', 0, 0, 0, 0, 0, 0);

INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('polygon', 'features', 'polygon', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('point', 'features', 'point', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('manzone', 'features', 'manzone', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('losszone', 'features', 'losszone', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('roof', 'features', 'roof', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('element', 'features', 'element', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('edge', 'features', 'edge', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vertex', 'features', 'vertex', '', 0, 0, 0, 0, 0, "SRID_VALUE");
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('raingage', 'features', 'raingage', '', 0, 0, 0, 0, 0, "SRID_VALUE");

INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('sys_selector', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('sys_parameter', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('sys_typevalue', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_scenario', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_landuses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_landuses_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_curves', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_curves_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_timeseries', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_timeseries_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_losses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_losses_values', 0);

INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('polygon', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('point', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('manzone', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('losszone', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('roof', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('element', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('edge', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vertex', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('raingage', 0);

INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('polygon', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('point', 'geom', 'POINT', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('manzone', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('losszone', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('roof', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('element', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('edge', 'geom', 'LINESTRING', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('vertex', 'geom', 'POINT', "SRID_VALUE", 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('raingage', 'geom', 'MULTIPOLYGON', "SRID_VALUE", 0, 0);