/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- ---------------------------
-- INSERTS INTO SYS GPKG TABLES
-- ---------------------------

INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_sector', 'attributes', 'selector_sector', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_scenario', 'attributes', 'selector_scenario', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('config_param_user', 'attributes', 'config_param_user', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('edit_typevalue', 'attributes', 'edit_typevalue', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_scenario', 'attributes', 'cat_scenario', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_curve', 'attributes', 'cat_curve', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_curve_value', 'attributes', 'cat_curve_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_timeseries', 'attributes', 'cat_timeseries', '',  0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_timeseries_value', 'attributes', 'cat_timeseries_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_landuses', 'attributes', 'cat_landuses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_grate', 'attributes', 'cat_grate', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_pattern', 'attributes', 'cat_pattern', '', 0, 0, 0, 0, 0, 0);

INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('sector', 'features', 'sector', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('polygon', 'features', 'polygon', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('terrain', 'features', 'terrain', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('manzone', 'features', 'manzone', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('losszone', 'features', 'losszone', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('roof', 'features', 'roof', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('elem_tin', 'features', 'elem_tin', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('elem_edge', 'features', 'elem_edge', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('elem_vertex', 'features', 'elem_vertex', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('raingage', 'features', 'raingage', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('link', 'features', 'link', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('gully', 'features', 'gully', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('conduit', 'features', 'conduit', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('subcatchment', 'features', 'subcatchment', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('outlet', 'features', 'outlet', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('orifice', 'features', 'orifice', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('weir', 'features', 'weir', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('pump', 'features', 'pump', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('outfall', 'features', 'outfall', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('divider', 'features', 'divider', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('storage', 'features', 'storage', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('junction', 'features', 'junction', '', 0, 0, 0, 0, 0, <SRID_VALUE>);




INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_sector', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_scenario', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('config_param_user', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('edit_typevalue', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_scenario', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_curve', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_curve_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_timeseries', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_timeseries_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_landuses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_grate', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_pattern', 0);

INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('sector', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('polygon', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('terrain', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('manzone', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('losszone', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('roof', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('elem_tin', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('elem_edge', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('elem_vertex', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('raingage', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('link', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('gully', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('conduit', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('subcatchment', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('outlet', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('orifice', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('weir', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('pump', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('outfall', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('divider', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('storage', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('junction', 0);


INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('sector', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('polygon', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('terrain', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('manzone', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('losszone', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('roof', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('elem_tin', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('elem_edge', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('elem_vertex', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('raingage', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('link', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('gully', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('conduit', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('subcatchment', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('outlet', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('orifice', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('weir', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('pump', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('outfall', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('divider', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('storage', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('junction', 'geom', 'POINT', <SRID_VALUE>, 0, 0);

