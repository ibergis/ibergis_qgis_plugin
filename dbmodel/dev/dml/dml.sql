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
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground', 'features', 'ground', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground_roughness', 'features', 'ground_roughness', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground_losses', 'features', 'ground_losses', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('roof', 'features', 'roof', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_tin', 'features', 'elem_tin', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_edge', 'features', 'elem_edge', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_vertex', 'features', 'elem_vertex', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('link', 'features', 'link', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('gully', 'features', 'gully', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_raingage', 'features', 'inp_raingage', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_conduit', 'features', 'inp_conduit', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_subcatchment', 'features', 'inp_subcatchment', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_outlet', 'features', 'inp_outlet', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_orifice', 'features', 'inp_orifice', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_weir', 'features', 'inp_weir', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_pump', 'features', 'inp_pump', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_outfall', 'features', 'inp_outfall', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_divider', 'features', 'inp_divider', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_storage', 'features', 'inp_storage', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_junction', 'features', 'inp_junction', '', 0, 0, 0, 0, 0, <SRID_VALUE>);




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
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground_roughness', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground_losses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('roof', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_tin', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_edge', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_vertex', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('link', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('gully', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_conduit', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_subcatchment', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_outlet', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_orifice', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_weir', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_pump', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_outfall', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_divider', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_storage', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_junction', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_raingage', 0);


INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('sector', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground_roughness', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground_losses', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('roof', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_tin', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_edge', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_vertex', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('link', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('gully', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_conduit', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_subcatchment', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_outlet', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_orifice', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_weir', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_pump', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_outfall', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_divider', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_storage', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_junction', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_raingage', 'geom', 'POINT', <SRID_VALUE>, 0, 0);