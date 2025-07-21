/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- ----------------------------
-- SRID
-- ----------------------------
INSERT INTO gpkg_spatial_ref_sys (srs_name, srs_id, organization, organization_coordsys_id, definition) VALUES('USER SRID', <SRID_VALUE>, 'EPSG', <SRID_VALUE>, 'user_srid');




-- ---------------------------
-- INSERTS INTO SYS GPKG TABLES
-- ---------------------------

INSERT INTO tables_geom (table_name, isgeom, index_col) values
('ground', 'MULTIPOLYGON', 'code'),
('roof', 'MULTIPOLYGON', 'code'),
('mesh_anchor_points', 'POINT', null),
('mesh_anchor_lines', 'LINESTRINGZ', null),
('boundary_conditions', 'MULTILINESTRING', 'code'),
('inlet', 'POINT', 'code'),
('inp_conduit', 'LINESTRING', 'code'),
('inp_outlet', 'LINESTRING', 'code'),
('inp_orifice', 'LINESTRING', 'code'),
('inp_weir', 'LINESTRING', 'code'),
('inp_pump', 'LINESTRING', 'code'),
('inp_outfall', 'POINT', 'code'),
('inp_divider', 'POINT', 'code'),
('inp_storage', 'POINT', 'code'),
('inp_junction', 'POINT','code'),
('node', 'POINT', 'fid'),
('arc', 'LINESTRING', 'fid'),
('vi_conduits', 'LINESTRING', null),
('vi_outlets', 'LINESTRING', null),
('vi_orifices', 'LINESTRING', null),
('vi_weirs', 'LINESTRING', null),
('vi_pumps', 'LINESTRING', null),
('vi_outfalls', 'POINT', null),
('vi_dividers', 'POINT', null),
('vi_storage', 'POINT', null),
('vi_junctions', 'POINT', null),
('vi_roof2junction', 'LINESTRING', null),
('vi_inlet2junction', 'LINESTRING', null),
('hyetograph', 'POINT', null),
('vi_inlet', 'POINT', null),
('culvert', 'LINESTRING', 'code'),
('pinlet', 'MULTIPOLYGON', 'code'),
('bridge', 'LINESTRING', 'code');



insert into tables_nogeom (table_name, index_col) values
('config_param_user', null),
('cat_bscenario', 'idval'),
('cat_file', null),
('cat_landuses', 'idval'),
('cat_transects', 'idval'),
('cat_transects_value', 'id'),
('cat_curve', 'idval'),
('cat_curve_value', null),
('cat_timeseries', 'idval'),
('cat_timeseries_value', null),
('cat_pattern', 'idval'),
('cat_pattern_value', null),
('cat_raster', 'idval'),
('cat_raster_value', null),
('cat_controls', null),
('inp_files', 'idval'),
('inp_dwf', 'code'),
('inp_inflow', 'code'),
('rpt_arc', null),
('rpt_arcflow_sum', null),
('rpt_cat_result', null),
('rpt_condsurcharge_sum', null),
('rpt_continuity_errors', null),
('rpt_control_actions_taken', null),
('rpt_critical_elements', null),
('rpt_flowclass_sum', null),
('rpt_flowrouting_cont', null),
('rpt_groundwater_cont', null),
('rpt_high_conterrors', null),
('rpt_high_flowinest_ind', null),
('rpt_instability_index', null),
('rpt_node', null),
('rpt_nodedepth_sum', null),
('rpt_nodeflooding_sum', null),
('rpt_nodeinflow_sum', null),
('rpt_nodesurcharge_sum', null),
('rpt_outfallflow_sum', null),
('rpt_pumping_sum', null),
('rpt_qualrouting_cont', null),
('rpt_routing_timestep', null),
('rpt_storagevol_sum', null),
('rpt_timestep_critelem', null),
('rpt_warning_summary', null),
('vi_curves', null),
('vi_timeseries', null),
('vi_patterns', null),
('vi_losses', null),
('vi_xsections', null),
('vi_dwf', null),
('vi_title', null),
('vi_files', null),
('vi_options', null),
('vi_controls', null),
('vi_inflows', null),
('vi_transects', null),
('vi_report', null),
('v_ui_file', null),
('inp_lid', 'idval'),
('inp_lid_value', 'id'),
('inp_lid_ground', 'id'),
('inp_lid_roof', 'id'),
('bridge_value', null),
('config_form_fields', null),
('config_csv', null),
('edit_typevalue', null),
('sys_message', null);


-- --------------------------------------------------------------------------------------------
-- INSERTS INTO NO-GEOM TABLES: config_form_fields, config_csv, edit_typevalue, sys_message
-- --------------------------------------------------------------------------------------------


INSERT INTO checkproject_query
(id, query_type, table_name, columns, extra_condition, create_layer, geometry_type, error_message_id, info_message_id, except_lvl, error_code)
VALUES
(1, 'MANDATORY NULL', 'cat_bscenario', '{descript}', NULL, 0, NULL, 1, 10, 3, 119),
(2, 'MANDATORY NULL', 'boundary_conditions', '{bscenario, boundary_type}', NULL, 0, 'MultiLineString', 1, 10, 3, 105),
(3, 'MANDATORY NULL', 'cat_controls', '{descript}', NULL, 0, NULL, 1, 10, 3, 120),
(4, 'MANDATORY NULL', 'cat_curve', '{curve_type}', NULL, 0, NULL, 1, 10, 3, 121),
(5, 'MANDATORY NULL', 'cat_curve_value', '{curve, xcoord, ycoord}', NULL, 0, NULL, 1, 10, 3, 122),
(6, 'MANDATORY NULL', 'cat_landuses', '{idval, manning}', NULL, 0, NULL, 1, 10, 3, 123),
(7, 'MANDATORY NULL', 'cat_pattern', '{idval, pattern_type}', NULL, 0, NULL, 1, 10, 3, 124),
(8, 'MANDATORY NULL', 'cat_pattern_value', '{pattern, timestep, value}', NULL, 0, NULL, 1, 10, 3, 125),
(9, 'MANDATORY NULL', 'cat_raster', '{idval, raster_type}', NULL, 0, NULL, 1, 10, 3, 126),
(10, 'MANDATORY NULL', 'cat_raster_value', '{time, fname}', NULL, 0, NULL, 1, 10, 3, 127),
(11, 'MANDATORY NULL', 'cat_timeseries', '{timser_type, times_type}', NULL, 0, NULL, 1, 10, 3, 128),
(12, 'MANDATORY NULL', 'cat_timeseries_value', '{time, value}', NULL, 0, NULL, 1, 10, 3, 129),
(13, 'MANDATORY NULL', 'ground', '{code, cellsize}', NULL, 0, 'MultiPolygon', 1, 10, 3, 106),
(14, 'MANDATORY NULL', 'hyetograph', '{code}', NULL, 0, 'Point', 1, 10, 3, 107),
(15, 'MANDATORY NULL', 'inlet', '{code, outlet_node, top_elev, width, length, method, efficiency}', NULL, 1, 'Point', 1, 10, 3, 108),
(16, 'MANDATORY NULL', 'inp_conduit', '{code, shape, geom1, roughness, length, z1, z2, node_1, node_2}', NULL, 0, 'LineString', 1, 10, 3, 109),
(17, 'MANDATORY NULL', 'inp_divider', '{code, elev, ymax, divider_type, divert_arc, y0, ysur}', NULL, 0, 'Point', 1, 10, 3, 110),
(18, 'MANDATORY NULL', 'inp_dwf', '{code, format, avg_value}', NULL, 0, NULL, 1, 10, 3, 130),
(19, 'MANDATORY NULL', 'inp_inflow', '{code, timeseries, format, mfactor, sfactor, ufactor, base}', NULL, 0, NULL, 1, 10, 3, 131),
(20, 'MANDATORY NULL', 'inp_junction', '{code, elev, ymax, y0, ysur}', NULL, 1, 'Point', 1, 10, 3, 111),
(21, 'MANDATORY NULL', 'inp_outfall', '{code, elev, gate, outfall_type}', NULL, 0, 'Point', 1, 10, 3, 112),
(22, 'MANDATORY NULL', 'inp_orifice', '{code, ori_type, shape, geom1, offsetval, cd1, flap, node_1, node_2}', NULL, 0, 'LineString', 1, 10, 3, 113),
(23, 'MANDATORY NULL', 'inp_outlet', '{code, flap, outlet_type, offsetval, cd1, cd2, node_1, node_2}', NULL, 0, 'LineString', 1, 10, 3, 114),
(24, 'MANDATORY NULL', 'inp_pump', '{code, state, startup, shutoff, node_1, node_2}', NULL, 0, 'LineString', 1, 10, 3, 115),
(25, 'MANDATORY NULL', 'inp_storage', '{code, elev, ymax, y0, ysur, storage_type}', NULL, 0, 'Point', 1, 10, 3, 116),
(26, 'MANDATORY NULL', 'inp_weir', '{code, flap, weir_type, geom1, geom2, cd2, ec, node_1, node_2}', NULL, 0, 'LineString', 1, 10, 3, 117),
(27, 'MANDATORY NULL', 'roof', '{code, slope, width, roughness, isconnected, outlet_code, outlet_vol, street_vol, infiltr_vol}', NULL, 0, 'MultiPolygon', 1, 10, 3, 118),
(28, 'GEOMETRIC DUPLICATE', 'arc', NULL, NULL, 1, 'LineString', 3, 7, 3, 101),
(29, 'GEOMETRIC DUPLICATE', 'node', NULL, NULL, 1, 'Point', 4, 8, 3, 102),
(30, 'GEOMETRIC ORPHAN', 'node', NULL, NULL, 1, 'Point', 5, 9, 3, 103),
(31, 'GEOMETRIC DUPLICATE', 'inlet', NULL, NULL, 1, 'Point', 4, 8, 3, 104),
(33, 'MANDATORY NULL', 'inlet', '{weir_cd, orifice_cd}', 'AND method == "UPC"', 0, NULL, 2, 11, 3, 133),
(34, 'MANDATORY NULL', 'inp_outfall', '{stage}', 'AND outfall_type == "FIXED"', 0, NULL, 2, 11, 3, 134),
(35, 'MANDATORY NULL', 'inp_outfall', '{curve}', 'AND outfall_type == "TIDAL"', 0, NULL, 2, 11, 3, 135),
(36, 'MANDATORY NULL', 'inp_outfall', '{timeseries}', 'AND outfall_type == "TIMESERIES"', 0, NULL, 2, 11, 3, 136),
(37, 'MANDATORY NULL', 'inp_storage', '{curve}', 'AND storage_type == "TABULAR"', 0, NULL, 2, 11, 3, 137),
(38, 'OUTLAYER', 'cat_landuses', '{manning}', NULL, 0, NULL, 6, 12, 3, 138),
(39, 'OUTLAYER', 'inp_conduit', '{roughness}', NULL, 0, NULL, 6, 12, 3, 139),
(40, 'OUTLAYER', 'ground', '{cellsize}', NULL, 0, NULL, 6, 12, 3, 140),
(41, 'OUTLAYER', 'inp_inflow', '{mfactor, sfactor, ufactor}', NULL, 0, NULL, 6, 12, 3, 141),
(42, 'OUTLAYER', 'roof', '{slope}', NULL, 0, NULL, 6, 12, 2, 142),
(43, 'OUTLAYER', 'roof', '{roughness, outlet_vol, street_vol}', NULL, 0, NULL, 6, 12, 3, 143),
(44, 'MANDATORY NULL', 'inp_storage', '{a1, a2, a0}', 'AND storage_type == "FUNCTIONAL"', 0, NULL, 2, 11, 3, 144);


INSERT INTO sys_message (id, "text") VALUES
(1,'Items with null values in "{0}" column ({1})'),
(2,'Items with null values in "{0}" column when "{1}" is "{2}" ({3})'),
(3,'Items duplicated ({0})'),
(4,'Items duplicated with a tolerance of 10 cm ({0})'),
(5,'Orphan nodes ({0})'),
(6,'Items with values out of range({0}-{1}) in "{2}" column ({3})'),
(7,'No items duplicated'),
(8,'No items duplicated with a tolerance of 10 cm'),
(9,'All nodes are connected'),
(10,'No items with null values in {0} columns'),
(11,'No items with null values in {0} columns when "{1}" is "{2}"'),
(12,'No items with values out of range({0}-{1}) in {2} columns');


INSERT INTO config_csv
(id, alias, descript, functionname, orderby, addparam)
VALUES
(386, 'Import inp patterns', 'Function to automatize the import of inp patterns files. 
The csv file must containts next columns on same position: 
pattern_id, pattern_type, factor1,.......,factorn. 
For WS use up factor18, repeating rows if you like. 
For UD use up factor24. More than one row for pattern is not allowed', 'gw_fct_import_inp_pattern', 9, NULL);

INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(1, 'nullvalue', '0', 'UNDEFINED', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(2, 'options_order', '0', 'Order 0', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(3, 'options_order', '1', 'Order 1', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(4, 'options_order', '10', 'Order 10', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(5, 'options_order', '101', 'Order 101', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(6, 'options_simulation_new', '0', 'New simulation', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(7, 'options_simulation_new', '1', 'Continue simulation', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(8, 'options_losses_method_', '1', 'Linear', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(9, 'options_losses_method', '2', 'SCS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(10, 'options_losses_method_', '3', 'Horton', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(11, 'options_losses_method_', '4', 'Green ampt', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(12, 'options_losses_method_', '5', 'SCSC', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(13, 'options_rain_class', '0', 'No_rain', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(14, 'options_rain_class', '1', 'Hyetogram', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(15, 'options_rain_class', '2', 'Raster', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(17, 'options_rain_format', '0', 'Intensity', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(18, 'options_rain_format', '1', 'Volume', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(19, 'plg_swmm_options', '0', 'Only gullies', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(20, 'plg_swmm_options', '1', 'Complete network', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(21, 'inp_value_yesno', 'YES', 'YES', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(22, 'inp_value_yesno', 'NO', 'NO', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(25, 'inp_options_force_main_eq', 'H-W', 'H-W', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(26, 'inp_options_force_main_eq', 'D-W', 'D-W', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(27, 'inp_options_inertial_damping', 'FULL', 'FULL', NULL, '');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(28, 'inp_options_inertial_damping', 'NONE', 'NONE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(29, 'inp_options_normal_flow_limited', 'BOTH', 'BOTH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(30, 'inp_options_normal_flow_limited', 'FLOWDE', 'FLOWDE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(31, 'inp_options_normal_flow_limited', 'ccccc', 'bbbbb', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(32, 'inp_options_hydro_scenario', '1', 'Infiltration default value', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(33, 'inp_options_hydro_scenario', '0', 'UNDEFINED', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(34, 'inp_options_flow_units', 'CFS', 'CFS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(35, 'inp_options_flow_units', 'CMS', 'CMS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(36, 'inp_options_flow_units', 'GPM', 'GPM', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(37, 'inp_options_flow_units', 'LPS', 'LPS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(38, 'inp_options_flow_units', 'MGD', 'MGD', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(39, 'inp_options_flow_units', 'MLD', 'MLD', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(40, 'inp_options_flow_routing', 'DYNWAVE', 'DYNWAVE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(41, 'inp_options_flow_routing', 'KINWAVE', 'KINWAVE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(42, 'inp_options_flow_routing', 'STEADY', 'STEADY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(43, 'inp_options_link_offsets', 'ELEVATION', 'ELEVATION', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(44, 'inp_options_link_offsets', 'DEPTH', 'DEPTH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(45, 'inp_options_networkmode', '1D', '1D SWMM', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(46, 'inp_options_networkmode', '1D2D', '1D/2D SWMM_IBER', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(47, 'inp_timeseries_type', 'EVAPORATION', 'EVAPORATION', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(48, 'inp_timeseries_type', 'INFLOW HYDROGRAPH', 'INFLOW HYDROGRAPH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(49, 'inp_timeseries_type', 'RAINFALL', 'RAINFALL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(50, 'inp_timeseries_type', 'TEMPERATURE', 'TEMPERATURE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(51, 'inp_timeseries_type', 'ORIFICE', 'ORIFICE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(52, 'inp_timeseries_type', 'BC ELEVATION', 'BC ELEVATION', NULL, '{"header": ["", "Time\n(H:M)", "Elevation (m)"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(53, 'inp_timeseries_type', 'BC FLOW', 'BC FLOW', NULL, '{"header": ["", "Time\n(H:M)", "Q (m3/s)"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(54, 'inp_timeseries_timestype', 'ABSOLUTE', 'ABSOLUTE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(55, 'inp_timeseries_timestype', 'FILE', 'FILE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(56, 'inp_timeseries_timestype', 'RELATIVE', 'RELATIVE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(57, 'inp_curve_type', 'CONTROL', 'CONTROL', NULL, '{"header": ["Value", "Setting"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(58, 'inp_curve_type', 'DIVERSION', 'DIVERSION', NULL, '{"header": ["Inflow", "Outflow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(59, 'inp_curve_type', 'PUMP1', 'PUMP1', NULL, '{"header": ["Volume", "Flow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(60, 'inp_curve_type', 'PUMP2', 'PUMP2', NULL, '{"header": ["Depth", "Flow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(61, 'inp_curve_type', 'PUMP3', 'PUMP3', NULL, '{"header": ["Head", "Flow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(62, 'inp_curve_type', 'PUMP4', 'PUMP4', NULL, '{"header": ["Depth", "Flow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(63, 'inp_curve_type', 'RATING', 'RATING', NULL, '{"header": ["Head", "Outflow"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(64, 'inp_curve_type', 'SHAPE', 'SHAPE', NULL, '{"header": ["Depth/\nFull Depth", "Width/\nFull Depth"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(65, 'inp_curve_type', 'STORAGE', 'STORAGE', NULL, '{"header": ["Depth", "Area"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(66, 'inp_curve_type', 'TIDAL', 'TIDAL', NULL, '{"header": ["Hour", "Stage"]}');
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(67, 'inp_typevalue_pattern', 'DAILY', 'DAILY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(68, 'inp_typevalue_pattern', 'HOURLY', 'HOURLY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(69, 'inp_typevalue_pattern', 'WEEKEND', 'WEEKEND', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(70, 'inp_typevalue_pattern', 'MONTHLY', 'MONTHLY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(71, 'inp_rain_format', 'Intensity', 'Intensity', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(72, 'inp_rain_format', 'Volume', 'Volume', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(73, 'options_losses_method', '0', 'NO LOSSES', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(74, 'dlg_options_layout', 'lyt_main_1_1', 'Project details', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(75, 'dlg_options_layout', 'lyt_main_1_2', 'Numerical scheme', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(76, 'dlg_options_layout', 'lyt_main_2_1', 'Time && Simulation control', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(77, 'dlg_options_layout', 'lyt_main_2_2', 'Hydrological processes', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(78, 'inp_typevalue_outfall_type', 'FREE', 'FREE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(79, 'inp_typevalue_outfall_type', 'NORMAL', 'NORMAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(80, 'inp_typevalue_outfall_type', 'FIXED', 'FIXED', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(81, 'inp_typevalue_outfall_type', 'TIDAL', 'TIDAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(82, 'inp_typevalue_outfall_type', 'TIMESERIES', 'TIMESERIES', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(83, 'inp_typevalue_inlet_outlet_type', 'SINK', 'SINK', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(84, 'inp_typevalue_inlet_outlet_type', 'TO NETWORK', 'TO NETWORK', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(85, 'inp_typevalue_boundary_type', 'INLET TOTAL DISCHARGE (SUB)CRITICAL', 'INLET TOTAL DISCHARGE (SUB)CRITICAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(86, 'inp_typevalue_boundary_type', 'INLET WATER ELEVATION', 'INLET WATER ELEVATION', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(87, 'inp_typevalue_boundary_type', 'OUTLET (SUPER)CRITICAL', 'OUTLET (SUPER)CRITICAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(88, 'inp_typevalue_boundary_type', 'OUTLET SUBCRITICAL WEIR HEIGHT', 'OUTLET SUBCRITICAL WEIR HEIGHT', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(89, 'inp_typevalue_boundary_type', 'OUTLET SUBCRITICAL WEIR ELEVATION', 'OUTLET SUBCRITICAL WEIR ELEVATION', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(90, 'inp_typevalue_boundary_type', 'OUTLET SUBCRITICAL GIVEN LEVEL', 'OUTLET SUBCRITICAL GIVEN LEVEL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(91, 'inp_typevalue_shape', 'ARCH', 'ARCH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(92, 'inp_typevalue_shape', 'BASKETHANDLE', 'BASKETHANDLE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(93, 'inp_typevalue_shape', 'CIRCULAR', 'CIRCULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(94, 'inp_typevalue_shape', 'CUSTOM', 'CUSTOM', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(95, 'inp_typevalue_shape', 'DUMMY', 'DUMMY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(96, 'inp_typevalue_shape', 'EGG', 'EGG', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(97, 'inp_typevalue_shape', 'FILLED_CIRCULAR', 'FILLED_CIRCULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(98, 'inp_typevalue_shape', 'FORCE_MAIN', 'FORCE_MAIN', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(99, 'inp_typevalue_shape', 'HORIZ_ELLIPSE', 'HORIZ_ELLIPSE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(100, 'inp_typevalue_shape', 'HORSESHOE', 'HORSESHOE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(101, 'inp_typevalue_shape', 'IRREGULAR', 'IRREGULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(102, 'inp_typevalue_shape', 'MODBASKETHANDLE', 'MODBASKETHANDLE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(103, 'inp_typevalue_shape', 'PARABOLIC', 'PARABOLIC', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(104, 'inp_typevalue_shape', 'POWER', 'POWER', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(105, 'inp_typevalue_shape', 'RECT_CLOSED', 'RECT_CLOSED', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(106, 'inp_typevalue_shape', 'RECT_OPEN', 'RECT_OPEN', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(107, 'inp_typevalue_shape', 'RECT_ROUND', 'RECT_ROUND', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(108, 'inp_typevalue_shape', 'RECT_TRIANGULAR', 'RECT_TRIANGULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(109, 'inp_typevalue_shape', 'SEMICIRCULAR', 'SEMICIRCULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(110, 'inp_typevalue_shape', 'SEMIELLIPTICAL', 'SEMIELLIPTICAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(111, 'inp_typevalue_shape', 'TRAPEZOIDAL', 'TRAPEZOIDAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(112, 'inp_typevalue_shape', 'TRIANGULAR', 'TRIANGULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(113, 'inp_typevalue_shape', 'VERT_ELLIPSE', 'VERT_ELLIPSE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(114, 'inp_typevalue_shape', 'VIRTUAL', 'VIRTUAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(115, 'inp_typevalue_method', 'UPC', 'UPC', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(116, 'inp_typevalue_method', 'W_O', 'W_O', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(117, 'inp_typevalue_outlet_type', 'FUNCTIONAL/DEPTH', 'FUNCTIONAL/DEPTH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(118, 'inp_typevalue_outlet_type', 'FUNCTIONAL/HEAD', 'FUNCTIONAL/HEAD', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(119, 'inp_typevalue_outlet_type', 'TABULAR/DEPTH', 'TABULAR/DEPTH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(120, 'inp_typevalue_outlet_type', 'TABULAR/HEAD', 'TABULAR/HEAD', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(121, 'inp_typevalue_ori_type', 'BOTTOM', 'BOTTOM', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(122, 'inp_typevalue_ori_type', 'SIDE', 'SIDE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(123, 'inp_typevalue_weir_type', 'ROADWAY', 'ROADWAY', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(124, 'inp_typevalue_weir_type', 'SIDEFLOW', 'SIDEFLOW', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(125, 'inp_typevalue_weir_type', 'TRANSVERSE', 'TRANSVERSE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(126, 'inp_typevalue_weir_type', 'TRAPEZOIDAL', 'TRAPEZOIDAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(127, 'inp_typevalue_weir_type', 'V-NOTCH', 'V-NOTCHV-NOTCH', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(128, 'inp_typevalue_road_surf', 'PAVED', 'PAVED', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(129, 'inp_typevalue_road_surf', 'GRAVEL', 'GRAVEL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(130, 'inp_typevalue_state_pump', 'OFF', 'OFF', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(131, 'inp_typevalue_state_pump', 'ON', 'ON', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(132, 'inp_typevalue_divider_type', 'CUTOFF', 'CUTOFF', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(133, 'inp_typevalue_divider_type', 'OVERFLOW', 'OVERFLOW', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(134, 'inp_typevalue_divider_type', 'TABULAR', 'TABULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(135, 'inp_typevalue_divider_type', 'WEIR', 'WEIR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(136, 'inp_typevalue_storage_type', 'FUNCTIONAL', 'FUNCTIONAL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(137, 'inp_typevalue_storage_type', 'TABULAR', 'TABULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(138, 'inp_typevalue_file_action', 'SAVE', 'SAVE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(139, 'inp_typevalue_file_action', 'USE', 'USE', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(140, 'inp_typevalue_file_type', 'HOTSTART', 'HOTSTART', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(141, 'inp_typevalue_file_type', 'INFLOWS', 'INFLOWS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(142, 'inp_typevalue_file_type', 'OUTFLOWS', 'OUTFLOWS', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(143, 'inp_typevalue_file_type', 'RAINFALL', 'RAINFALL', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(144, 'inp_typevalue_file_type', 'RDII', 'RDII', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(145, 'inp_typevalue_file_type', 'RUNOFF', 'RUNOFF', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(146, 'result_results_raster', '0', 'No raster results', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(147, 'result_results_raster', '1', 'Linear interpolation', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(148, 'result_results_raster', '2', 'Nearest interpolation', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(149, 'options_mesh_losses_vdefault', '65', 'Default value for losses when creating the mesh', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(150, 'options_mesh_roughness_vdefault', '0.02', 'Default value for roughness when creating the mesh', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(151, 'culvert_type', 'CIRCULAR', 'CIRCULAR', NULL, NULL);
INSERT INTO edit_typevalue
(rowid, typevalue, id, idval, descript, addparam)
VALUES(152, 'culvert_type', 'RECTANGULAR', 'RECTANGULAR', NULL, NULL);


INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'landuse', NULL, NULL, 'text', 'combo', 'landuse', 'idval of cat_landuses', 0, 1, 'SELECT idval as id, idval FROM cat_landuses', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, '{"setMultiline": false,"valueRelation": {"activated": true, "layer": "cat_landuse", "nullValue": false, "keyColumn": "id", "valueColumn": "idval", "filterExpression": null}}
');
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'outlet_code', NULL, NULL, 'text', 'text', 'outlet_code', 'code of inp_junction', 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, '{"setMultiline": false,"valueRelation": {"activated": true, "layer": "inp_junction", "nullValue": false, "keyColumn": "fid", "valueColumn": "code", "filterExpression": null}}');
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'cellsize', NULL, NULL, 'real', 'text', 'cellsize', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'custom_roughness', NULL, NULL, 'real', 'text', 'custom_roughness', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'scs_cn', NULL, NULL, 'real', 'text', 'scs_cn', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, '65', NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'decript', NULL, NULL, 'test', 'text', 'decript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'cellsize', NULL, NULL, 'real', 'text', 'cellsize', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'slope', NULL, NULL, 'real', 'text', 'slope', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'width', NULL, NULL, 'real', 'text', 'width', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'roughness', NULL, NULL, 'real', 'text', 'roughness', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'isconnected', NULL, NULL, 'integer', 'text', 'isconnected', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('ground', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'fname', NULL, NULL, 'text', 'text', 'fname', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('mesh_anchor_points', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('mesh_anchor_lines', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'outlet_type', NULL, NULL, 'text', 'text', 'outlet_type', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'outlet_vol', NULL, NULL, 'text', 'text', 'outlet_vol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'street_vol', NULL, NULL, 'real', 'text', 'street_vol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'infiltr_vol', NULL, NULL, 'real', 'text', 'infiltr_vol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'totalvol', NULL, NULL, 'real', 'text', 'totalvol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'inletvol', NULL, NULL, 'real', 'text', 'inletvol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'lossvol', NULL, NULL, 'real', 'text', 'lossvol', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, '0.2', NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'flap', NULL, NULL, 'text', 'combo', 'flap', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'close_time', NULL, NULL, 'real', 'text', 'close_time', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve_value', 'form_feature', 'tabdata', 'ycoord', NULL, NULL, 'real', 'text', 'ycoord', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'ec', NULL, NULL, 'integer', 'text', 'ec', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'surcharge', NULL, NULL, 'text', 'text', 'surcharge', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'y0', NULL, NULL, 'real', 'text', 'y0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'ysur', NULL, NULL, 'real', 'text', 'ysur', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'apond', NULL, NULL, 'real', 'text', 'apond', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'actio_type', NULL, NULL, 'text', 'combo', 'actio_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_file_action''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'file_type', NULL, NULL, 'text', 'combo', 'file_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_file_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_file', 'form_feature', 'tabdata', 'roof', NULL, NULL, 'text', 'text', 'roof', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_file', 'form_feature', 'tabdata', 'losses', NULL, NULL, 'text', 'text', 'losses', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('mesh_anchor_lines', 'form_feature', 'tabdata', 'cellsize', NULL, NULL, 'real', 'text', 'cellsize', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'boundary_type', NULL, NULL, 'text', 'combo', 'boundary_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_boundary_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'other1', NULL, NULL, 'real', 'text', 'other1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'other2', NULL, NULL, 'real', 'text', 'other2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_eri', 'form_feature', 'tabdata', 'shape', NULL, NULL, 'text', 'text', 'shape', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'weir_cd', NULL, NULL, 'integer', 'text', 'weir_cd', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'ymax', NULL, NULL, 'real', 'text', 'ymax', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'divert_arc', NULL, NULL, 'text', 'text', 'divert_arc', 'code of inp_conduit', 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', 'idval of cat_curve', 0, 1, 'SELECT idval as id, idval FROM cat_curve', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'y0', NULL, NULL, 'real', 'text', 'y0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'ysur', NULL, NULL, 'real', 'text', 'ysur', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'storage_type', NULL, NULL, 'text', 'combo', 'storage_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_storage_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'a1', NULL, NULL, 'real', 'text', 'a1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'a2', NULL, NULL, 'real', 'text', 'a2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'a0', NULL, NULL, 'real', 'text', 'a0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'geom1', NULL, NULL, 'real', 'text', 'geom1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'geom2', NULL, NULL, 'real', 'text', 'geom2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'geom3', NULL, NULL, 'real', 'text', 'geom3', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'geom4', NULL, NULL, 'real', 'text', 'geom4', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'cd2', NULL, NULL, 'real', 'text', 'cd2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'orifice_cd', NULL, NULL, 'integer', 'text', 'orifice_cd', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'cd1', NULL, NULL, 'real', 'text', 'cd1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern', 'form_feature', 'tabdata', 'pattern_type', NULL, NULL, 'text', 'text', 'pattern_type', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern_value', 'form_feature', 'tabdata', 'timestep', NULL, NULL, 'datetime', 'text', 'timestep', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'gate', NULL, NULL, 'text', 'combo', 'gate', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'outfall_type', NULL, NULL, 'text', 'combo', 'outfall_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_outfall_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'stage', NULL, NULL, 'real', 'text', 'stage', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'routeto', NULL, NULL, 'text', 'text', 'routeto', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'ymax', NULL, NULL, 'real', 'text', 'ymax', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'y0', NULL, NULL, 'real', 'text', 'y0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'ysur', NULL, NULL, 'real', 'text', 'ysur', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'apond', NULL, NULL, 'real', 'text', 'apond', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'divider_type', NULL, NULL, 'text', 'combo', 'divider_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_divider_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'node_1', NULL, NULL, 'text', 'text', 'node_1', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'node_2', NULL, NULL, 'text', 'text', 'node_2', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('hyetograph', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'weir_type', NULL, NULL, 'text', 'combo', 'weir_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_weir_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'offsetval', NULL, NULL, 'real', 'text', 'offsetval', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('hyetograph', 'form_feature', 'tabdata', 'timeseries', NULL, NULL, 'text', 'combo', 'timeseries', 'idval of cat_timeseries', 0, 1, 'SELECT idval as id, idval FROM cat_timeseries', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', 'idval of cat_curve', 0, 1, 'SELECT idval as id, idval FROM cat_curve', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', 'idval of cat_curve', 0, 1, 'SELECT idval as id, idval FROM cat_curve', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'pattern', NULL, NULL, 'text', 'combo', 'pattern', 'idval of cat_pattern', 0, 1, 'SELECT idval as id, idval FROM cat_pattern', 0, 0, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'road_width', NULL, NULL, 'real', 'text', 'road_width', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'road_surf', NULL, NULL, 'text', 'combo', 'road_surf', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_road_surf''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'crest_height', NULL, NULL, 'real', 'text', 'crest_height', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'end_coeff', NULL, NULL, 'real', 'text', 'end_coeff', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'sfactor', NULL, NULL, 'real', 'text', 'sfactor', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'ufactor', NULL, NULL, 'real', 'text', 'ufactor', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'base', NULL, NULL, 'real', 'text', 'base', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('hyetograph', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_bscenario', 'form_feature', 'tabdata', 'name', NULL, NULL, 'text', 'text', 'name', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_bscenario', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_file', 'form_feature', 'tabdata', 'name', NULL, NULL, 'text', 'text', 'name', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_landuses', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, 1, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'roughness', NULL, NULL, 'real', 'text', 'roughness', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'fid', NULL, NULL, 'integer', 'text', 'fid', NULL, 1, 0, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'type', NULL, NULL, 'text', 'text', 'type', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_bscenario', 'form_feature', 'tabdata', 'active', NULL, NULL, 'integer', 'text', 'active', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_file', 'form_feature', 'tabdata', 'iber2d', NULL, NULL, 'text', 'text', 'iber2d', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'a_param', NULL, NULL, 'integer', 'text', 'a_param', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'b_param', NULL, NULL, 'integer', 'text', 'b_param', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'efficiency', NULL, NULL, 'integer', 'text', 'efficiency', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'node_1', NULL, NULL, 'text', 'text', 'node_1', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'node_2', NULL, NULL, 'text', 'text', 'node_2', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'node_1', NULL, NULL, 'text', 'text', 'node_1', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'node_2', NULL, NULL, 'text', 'text', 'node_2', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'ori_type', NULL, NULL, 'text', 'combo', 'ori_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_ori_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'shape', NULL, NULL, 'text', 'combo', 'shape', NULL, 1, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_shape'' AND id IN (''CIRCULAR'', ''RECT_CLOSED'')', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'geom1', NULL, NULL, 'real', 'text', 'geom1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'geom2', NULL, NULL, 'real', 'text', 'geom2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'offsetval', NULL, NULL, 'real', 'text', 'offsetval', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_landuses', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern_value', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_controls', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve_value', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster_value', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries_value', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects_value', 'form_feature', 'tabdata', 'id', NULL, NULL, 'integer', 'text', 'id', NULL, 1, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'length', NULL, NULL, 'real', 'text', 'length', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'z1', NULL, NULL, 'real', 'text', 'z1', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'z2', NULL, NULL, 'real', 'text', 'z2', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'q0', NULL, NULL, 'real', 'text', 'q0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'qmax', NULL, NULL, 'real', 'text', 'qmax', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_controls', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster_value', 'form_feature', 'tabdata', 'fname', NULL, NULL, 'text', 'text', 'fname', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'barrels', NULL, NULL, 'real', 'text', 'barrels', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, 0, 0, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern_value', 'form_feature', 'tabdata', 'value', NULL, NULL, 'real', 'text', 'value', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster', 'form_feature', 'tabdata', 'raster_type', NULL, NULL, 'text', 'text', 'raster_type', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'culvert', NULL, NULL, 'text', 'text', 'culvert', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('config_param_user', 'form_feature', 'tabdata', 'parameter', NULL, NULL, 'text', 'text', 'parameter', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('config_param_user', 'form_feature', 'tabdata', 'value', NULL, NULL, 'text', 'text', 'value', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('config_param_user', 'form_feature', 'tabdata', 'isconflictive', NULL, NULL, 'integer', 'text', 'isconflictive', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve', 'form_feature', 'tabdata', 'curve_type', NULL, NULL, 'text', 'combo', 'curve_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_curve_type''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve_value', 'form_feature', 'tabdata', 'xcoord', NULL, NULL, 'real', 'text', 'xcoord', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'state', NULL, NULL, 'text', 'combo', 'state', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_state_pump''', 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'startup', NULL, NULL, 'real', 'text', 'startup', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'shutoff', NULL, NULL, 'real', 'text', 'shutoff', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'cutoff_flow', NULL, NULL, 'real', 'text', 'cutoff_flow', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'qmin', NULL, NULL, 'real', 'text', 'qmin', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'q0', NULL, NULL, 'real', 'text', 'q0', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'elev', NULL, NULL, 'real', 'text', 'elev', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'ymax', NULL, NULL, 'real', 'text', 'ymax', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'avg_value', NULL, NULL, 'real', 'text', 'avg_value', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'baseline', NULL, NULL, 'text', 'text', 'baseline', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'format', NULL, NULL, 'text', 'text', 'format', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'mfactor', NULL, NULL, 'real', 'text', 'mfactor', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'project_name', 'lyt_main_1_1', 1, 'string', 'text', 'Project name:', NULL, 1, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, 'Name of the project', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'project_descript', 'lyt_main_1_1', 2, 'string', 'text', 'Description:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, 'Description of the project', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'project_user', 'lyt_main_1_1', 3, 'string', 'text', 'User:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, 'Nombre de usuario', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'project_tstamp', 'lyt_main_1_1', 4, 'date', 'datetime', 'Creation date:', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, 'Fecha de creación', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'project_version', 'lyt_main_1_1', 5, 'string', 'text', 'Version:', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, 'Versión del proyecto', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_delta_time', 'lyt_main_1_2', 3, 'integer', 'text', 'Delta time:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '1', 'Increase of maximum time', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_tmax', 'lyt_main_2_1', 2, 'integer', 'text', 'Tmax:', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '10800', 'Maximum time of simulation', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_rank_results', 'lyt_main_2_1', 3, 'integer', 'text', 'Rank results:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '300', 'Rank of results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_order', 'lyt_main_1_2', 1, 'integer', 'combo', 'Equation order:', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''options_order''', 0, 0, 0, NULL, NULL, '10', 'Equation order', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_cfl', 'lyt_main_1_2', 2, 'integer', 'text', 'CFL:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.45', 'CFL', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_wetdry_edge', 'lyt_main_1_2', 4, 'double', 'text', 'Wet-dry edge:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.0001', 'Wet-dry edge', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_viscosity_coeff', 'lyt_main_1_2', 5, 'double', 'text', 'Viscosity coefficient:', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '0.00001', 'Viscosity coefficient', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_t0', 'lyt_main_2_1', 1, 'integer', 'text', 'Initial time:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Initial time', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_simulation_details', 'lyt_main_2_1', 5, 'boolean', 'check', 'Simulation details are written:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Simulation details are written or not', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_simulation_new', 'lyt_main_2_1', 6, 'integer', 'combo', 'New simulation or current simulation:', NULL, 0, 0, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''options_simulation_new''', 0, 0, 0, NULL, NULL, '0', 'Continue simulation or create a new one', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_plan_id', 'lyt_main_2_1', 8, 'integer', 'text', 'Plan ID:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Plan ID', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_simulation_plan', 'lyt_main_2_1', 7, 'boolean', 'check', 'Enable or disable simulation plan:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, 'Disabled', 'Enable or disable simulation plan', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_timeseries', 'lyt_main_2_1', 4, 'integer', 'text', 'Timeseries rank results:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '300', 'Rank results of time series', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_losses_method', 'lyt_main_2_2', 5, 'integer', 'combo', 'Method used for losses:', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''options_losses_method''', 0, 0, 0, NULL, NULL, '2', 'Method used for losses (0 disabled, 2-SCS)', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_rain_class', 'lyt_main_2_2', 2, 'integer', 'combo', 'Type of rain:', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''options_rain_class''', 0, 0, 0, NULL, NULL, '0', 'Type of rain', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_depth', 'lyt_rpt_iber_1_1', 1, 'boolean', 'check', 'Depth', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '1', 'Depth of the results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_vel', 'lyt_rpt_iber_1_1', 2, 'boolean', 'check', 'Velocity', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '1', 'Velocity of the results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_specific_discharge', 'lyt_rpt_iber_1_1', 3, 'boolean', 'check', 'Specific discharge', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Specific discharge of the results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_water_elevation', 'lyt_rpt_iber_1_1', 4, 'boolean', 'check', 'Water elevation', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Water elevation of the results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_fronde_number', 'lyt_rpt_iber_1_3', 2, 'boolean', 'check', 'Froude number', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Fronde number', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_localtime_step', 'lyt_rpt_iber_1_3', 3, 'boolean', 'check', 'Local time step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Local time step', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_manning_coefficient', 'lyt_rpt_iber_3_1', 20, 'boolean', 'check', 'Manning coefficient:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Manning coefficient', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_critical_diameter', 'lyt_rpt_iber_3_1', 40, 'boolean', 'check', 'Critial diameter:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Critial diameter', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_depth', 'lyt_rpt_iber_1_2', 1, 'boolean', 'check', 'Maximum depth', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Maximum depth', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_vel', 'lyt_rpt_iber_1_2', 2, 'boolean', 'check', 'Maximum velocity', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Maximum velocity', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_spec_discharge', 'lyt_rpt_iber_1_2', 3, 'boolean', 'check', 'Maximum specific discharge', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Maximum specific discharge', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_water_elev', 'lyt_rpt_iber_1_2', 4, 'boolean', 'check', 'Maximum water elevation', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Maximum water elevation', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_localtime_step', 'lyt_rpt_iber_1_3', 4, 'boolean', 'check', 'Maximum local time step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Maximum localtime step', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_critical_diameter', 'lyt_rpt_iber_3_1', 10, 'boolean', 'check', 'Maximum critical diameter:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Maximum critical diameter', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_hazard_rd9_2008', 'lyt_rpt_iber_2_1', 1, 'boolean', 'check', 'Hazard RD9/2008', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Spanish national legislation [RD 9/2008]', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_hazard_aca2003', 'lyt_rpt_iber_2_1', 2, 'boolean', 'check', 'Hazard ACA 2003', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Catalan regional legislation [Catalan Water Agency 2003]', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_depth_vector', 'lyt_rpt_iber_3_1', 30, 'boolean', 'check', 'Depth vector:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Depth vector', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_bed_shear_stress', 'lyt_rpt_iber_3_1', 50, 'boolean', 'check', 'Bed shear stress:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Bed shear stress', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_max_bed_shear_stress', 'lyt_rpt_iber_3_1', 60, 'boolean', 'check', 'Maximum bed shear stress:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Maximum bed shear stress', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_energy', 'lyt_rpt_iber_1_3', 1, 'boolean', 'check', 'Energy', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Energy', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_steamlines', 'lyt_rpt_iber_3_1', 70, 'boolean', 'check', 'Steamlines:', NULL, 0, 0, NULL, NULL, NULL, 1, NULL, NULL, '0', 'Steamlines', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm', 'lyt_plugins_1_1', 1, 'boolean', 'check', NULL, NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_options', 'lyt_plugins_1_1', 2, 'integer', 'combo', 'Only gullies or complete network:', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''plg_swmm_options''', 0, 0, 0, NULL, NULL, '1', 'Only gullies or complete network', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_outlet', 'lyt_plugins_1_1', 3, 'boolean', 'check', 'Enable or disable outlet loss:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Enables outlet loss', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_result_dis1', 'lyt_plugins_1_2', 1, 'integer', 'text', NULL, NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_result_dis2', 'lyt_plugins_1_2', 2, 'integer', 'text', NULL, NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_result_dis3', 'lyt_plugins_1_2', 3, 'integer', 'text', NULL, NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_plugins', 'plg_swmm_result_dis4', 'lyt_plugins_1_2', 4, 'integer', 'text', NULL, NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_routing_step', 'lyt_swmm_inp_3_1', 1, 'string', 'linetext', 'Routing step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:00:02', 'Value of routing step, which is the time step length in seconds used for routing flows and water quality constituents through the conveyance system', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_start_date', 'lyt_swmm_inp_3_1', 2, 'date', 'datetime', 'Start date', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '2017-01-01', 'Value of start date, which is the date when the simulation begins', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_report_start_date', 'lyt_swmm_inp_3_1', 3, 'date', 'datetime', 'Report start date', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '2017-01-01', 'Value of report start date, which is the date when reporting of results is to begin', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_end_date', 'lyt_swmm_inp_3_1', 4, 'date', 'datetime', 'End date', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '2017-01-01', 'Value of end date, which is the date when the simulation is to end', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_report_step', 'lyt_swmm_inp_3_2', 1, 'string', 'linetext', 'Report step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:05:00', 'Value of report step, which is the time interval for reporting of computed results', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_start_time', 'lyt_swmm_inp_3_2', 2, 'string', 'linetext', 'Start time', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:00:00', 'Value of start time, which is the time of day on the starting date when the simulation begins', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_end_time', 'lyt_swmm_inp_3_2', 3, 'string', 'linetext', 'End time', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '03:00:00', 'Value of end time, which is the time of day on the ending date when the simulation will end', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_report_start_time', 'lyt_swmm_inp_3_2', 4, 'string', 'linetext', 'Report start time', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:00:00', 'Value of report start time, which is the time of day on the report starting date when reporting is to begin', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_skip_steady_state', 'lyt_swmm_inp_1_1', 1, 'string', 'combo', 'Skip steady state', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of skip steady state, which should be set to YES if flow routing computations should be skipped during steady state periods of a simulation during which the last set of computed flows will be used', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_allow_ponding', 'lyt_swmm_inp_1_1', 2, 'string', 'combo', 'Allow ponding', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'YES', 'Value of pounding, which determines whether excess water is allowed to collect atop nodes and be re-introduced into the system as conditions permit', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_min_slope', 'lyt_swmm_inp_1_1', 3, 'double', 'spinbox', 'Min slope', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.00', 'Value of minimum slope, which is the minimum value allowed for a conduit�s slope (%)', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_flow_units', 'lyt_swmm_inp_1_1', 5, 'string', 'combo', 'Flow units', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_flow_units''', 0, 0, 0, NULL, NULL, 'CMS', 'Value of flow units, makes a choice of flow units', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_flow_routing', 'lyt_swmm_inp_1_1', 6, 'string', 'combo', 'Flow routing', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_flow_routing''', 0, 0, 0, NULL, NULL, 'DYNWAVE', 'Value of  flow routing,which determines which method is used to route flows through the drainage system', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_link_offsets', 'lyt_swmm_inp_1_1', 7, 'string', 'combo', 'Link offsets', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_link_offsets''', 0, 0, 0, NULL, NULL, 'ELEVATION', 'Value of link offsets, which determines the convention used to specify the position of a link offset above the invert of its connecting node', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_ignore_groundwater', 'lyt_swmm_inp_1_2', 1, 'string', 'combo', 'Ignore groundwater', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of head tolerance, which is set to YES if groundwater calculations should be ignored when a project file contains aquifer objects. ', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_ignore_rainfall', 'lyt_swmm_inp_1_2', 2, 'string', 'combo', 'Ignore rainfall', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of ignore rainfall, which is set to YES if all rainfall data and runoff calculations should be ignored', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_ignore_routing', 'lyt_swmm_inp_1_2', 3, 'string', 'combo', 'Ignore routing', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of ignore routing, which is set to YES if only runoff should be computed even if the project contains drainage system links and nodes', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_ignore_snowmelt', 'lyt_swmm_inp_1_2', 4, 'string', 'combo', 'Ignore snowmelt', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of ignore snowmelt, which is set to YES if snowmelt calculations should be ignored when a project file contains snow pack objects', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_ignore_quality', 'lyt_swmm_inp_1_2', 5, 'string', 'combo', 'Ignore quality', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of ignore quality, which is set to YES if pollutant washoff, routing, and treatment should be ignored in a project that has pollutants defined', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_tempdir', 'lyt_swmm_inp_1_2', 6, 'string', 'linetext', 'Tempdir', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '', 'Value of tempdir, which provides the name of a file directory (or folder) where SWMM writes its temporary files', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_force_main_equation', 'lyt_swmm_inp_2_1', 1, 'string', 'combo', 'Force main equation', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_force_main_eq''', 0, 0, 0, NULL, NULL, 'H-W', 'Value of force main equation, which establishes whether the Hazen-Williams (H-W) or the Darcy-Weisbach (D-W) equation will be used to compute friction losses for pressurized flow in conduits that have been assigned a Circular Force Main crosssection shape', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_inertial_damping', 'lyt_swmm_inp_2_1', 2, 'string', 'combo', 'Inertial damping', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_inertial_damping''', 0, 0, 0, NULL, NULL, 'NONE', 'Value of inertial damping, which indicates how the inertial terms in the Saint Venant momentum equation will be handled under dynamic wave flow routing', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_lat_flow_tol', 'lyt_swmm_inp_2_1', 3, 'integer', 'linetext', 'Lat flow tol', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '5', 'Lateral flow tolerance used on the computation', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_lengthening_step', 'lyt_swmm_inp_2_1', 4, 'double', 'spinbox', 'Lengthening step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '1', 'Value of lengthening step, which is a time step, in seconds, used to lengthen conduits under dynamic wave routing, so that they meet the Courant stability criterion under fullflow conditions', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_wet_step', 'lyt_swmm_inp_2_1', 5, 'string', 'linetext', 'Wet step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:05:00', 'Value of wet step, which is the time step length used to compute runoff from subcatchments during periods of rainfall or when ponded water still remains on the surface', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_sweep_start', 'lyt_swmm_inp_2_1', 6, 'string', 'linetext', 'Sweep start', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '01/01', 'Value of sweep start, which is the day of the year (month/day) when street sweeping operations begin', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_head_tolerance', 'lyt_swmm_inp_2_2', 5, 'double', 'spinbox', 'Head tolerance', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.000', 'Value of head tolerance, which defines then tolerance of head on computation', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_rule_step', 'lyt_swmm_inp_2_1', 8, 'text', 'linetext', 'Rule step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '00:00:00', 'Rule step control', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_variable_step', 'lyt_swmm_inp_2_1', 9, 'double', 'linetext', 'Variable step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.75', 'Value of variable step, which is a safety factor applied to a variable time step computed for each time period under dynamic wave flow routing', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_normal_flow_limited', 'lyt_swmm_inp_2_2', 1, 'string', 'combo', 'Normal flow limited', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_options_normal_flow_limited''', 0, 0, 0, NULL, NULL, 'BOTH', 'Value of normal flow limited, which specifies which condition is checked to determine if flow in a conduit is supercritical and should thus be limited to the normal flow', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_min_surfarea', 'lyt_swmm_inp_2_2', 2, 'double', 'spinbox', 'Min surfarea', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.00', 'Value of minimum surfarea, which is a minimum surface area used at nodes when computing changes in water depth under dynamic wave routing', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_dry_days', 'lyt_swmm_inp_2_2', 3, 'integer', 'linetext', 'Dry days', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '10', 'Value of dry days, which is the number of days with no rainfall prior to the start of the simulation. ', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_dry_step', 'lyt_swmm_inp_2_2', 4, 'string', 'linetext', 'Dry step', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '01:00:00', 'Value of dry step, which is the time step length used for runoff computations (consisting essentially of pollutant buildup) during periods when there is no rainfall and no ponded water. ', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_sweep_end', 'lyt_swmm_inp_2_1', 7, 'string', 'linetext', 'Sweep end', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '12/31', 'Value of sweep end, which is the day of the year (month/day) when street sweeping operations end', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_max_trials', 'lyt_swmm_inp_2_2', 6, 'integer', 'linetext', 'Max trials', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Value of trials, which are the maximum number of trials used to solve network hydraulics at each hydraulic time step of a simulation. ', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_sys_flow_tol', 'lyt_swmm_inp_2_2', 7, 'integer', 'linetext', 'Sys flow tol', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '5', 'Flow tolerance used on the computation', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_threads', 'lyt_swmm_inp_2_2', 8, 'integer', 'linetext', 'Threads', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '1', 'Threads control', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_inp_swmm', 'inp_options_minimum_step', 'lyt_swmm_inp_2_2', 9, 'integer', 'linetext', 'Minimum step:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.5', 'Value of minimum step for routing timestep.', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_continuity', 'lyt_swmm_rpt_1_1', 1, 'string', 'combo', 'Continuity', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'YES', 'Value of continuity, which specifies whether continuity checks should be reported or not', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_flowstats', 'lyt_swmm_rpt_1_1', 2, 'string', 'combo', 'Flowstats', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'YES', 'Value of flowstats, which specifies whether summary flow statistics should be reported or not', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_controls', 'lyt_swmm_rpt_1_1', 3, 'string', 'combo', 'Controls', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'YES', 'Value of controls, which specifies whether all control actions taken during a simulation should be listed or not', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_input', 'lyt_swmm_rpt_1_1', 4, 'string', 'combo', 'Input', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''inp_value_yesno''', 0, 0, 0, NULL, NULL, 'NO', 'Value of input, which specifies whether or not a summary of the input data should be provided in the output report', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_subcatchments', 'lyt_swmm_rpt_1_2', 1, 'string', 'linetext', 'Timestep detailed subcatchments', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '', 'Value of subcatchments, which gives a list of subcatchments whose results are to be reported', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_nodes', 'lyt_swmm_rpt_1_2', 2, 'string', 'linetext', 'Timestep detailed nodesI-(max.40):', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '', 'Value of node, which gives a list of nodes whose results are to be reported', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_nodes_2', 'lyt_swmm_rpt_1_2', 3, 'string', 'linetext', 'Timestep detailed nodesII-(max.40):', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, '', 'Value of node, which gives a list of nodes whose results are to be reported', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_swmm', 'inp_report_links', 'lyt_swmm_rpt_1_2', 4, 'string', 'linetext', 'Timestep detailed links', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '', 'Value of links, which  gives a list of links whose results are to be reported', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_setallhyetografs', 'lyt_main_2_2', 3, 'integer', 'combo', 'Set rainfall for all hyetografs', NULL, 0, 1, 'SELECT group_concat(idval) AS id, group_concat(idval) AS idval from cat_timeseries WHERE times_type =''RELATIVE'' AND timser_type = ''RAINFALL'' ', 0, 1, 1, 'Rainfall timeseries (from cat_timeseries table)', '{"execute_on": "data"}', NULL, 'Set rainfall timeseries for all hyetografs', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_setrainfall_raster', 'lyt_main_2_2', 4, 'integer', 'combo', 'Set rainfall raster', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from cat_raster WHERE id is not null', 0, 1, 0, 'Raster (from cat_raster table)', '{"execute_on": "data"}', NULL, 'Set rainfall raster', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_losses_starttime', 'lyt_main_2_2', 1, 'date', 'text', 'Start time:', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Start time for losses method', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_losses_scs_cn_multiplier', 'lyt_main_2_2', 6, 'double', 'text', 'CN multiplier', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '1', 'CN multiplier  (tool to calibrate)', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_main', 'options_losses_scs_ia_coefficient', 'lyt_main_2_2', 7, 'double', 'text', 'Ia', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0.2', 'Ia coefficient', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects_value', 'form_feature', 'tabdata', 'transect', NULL, NULL, 'text', 'combo', 'transect', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects_value', 'form_feature', 'tabdata', 'data_group', NULL, NULL, 'text', 'text', 'data_group', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_transects_value', 'form_feature', 'tabdata', 'value', NULL, NULL, 'text', 'text', 'value', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_curve_value', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'timser_type', NULL, NULL, 'text', 'text', 'timser_type
times_type
descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'times_type', NULL, NULL, 'text', 'text', 'timser_type
times_type
descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'timser_type
times_type
descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries_value', 'form_feature', 'tabdata', 'timeseries', NULL, NULL, 'text', 'combo', 'timeseries', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries_value', 'form_feature', 'tabdata', 'date', NULL, NULL, 'text', 'text', 'date', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries_value', 'form_feature', 'tabdata', 'time', NULL, NULL, 'text', 'text', 'time', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_timeseries_value', 'form_feature', 'tabdata', 'value', NULL, NULL, 'text', 'text', 'value', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_pattern_value', 'form_feature', 'tabdata', 'pattern', NULL, NULL, 'text', 'combo', 'pattern', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster_value', 'form_feature', 'tabdata', 'raster', NULL, NULL, 'text', 'combo', 'raster', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('cat_raster_value', 'form_feature', 'tabdata', 'time', NULL, NULL, 'text', 'text', 'time', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('roof', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'outlet_node', NULL, NULL, 'text', 'text', 'outlet_node', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'outlet_type', NULL, NULL, 'text', 'combo', 'outlet_type', NULL, NULL, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_inlet_outlet_type''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'top_elev', NULL, NULL, 'real', 'text', 'top_elev', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'width', NULL, NULL, 'real', 'text', 'width', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'length', NULL, NULL, 'real', 'text', 'length', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'depth', NULL, NULL, 'real', 'text', 'depth', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inlet', 'form_feature', 'tabdata', 'method', NULL, NULL, 'text', 'combo', 'method', NULL, NULL, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_method''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('hyetograph', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'text', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'bscenario', NULL, NULL, 'text', 'combo', 'bscenario', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_bscenario', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('boundary_conditions', 'form_feature', 'tabdata', 'timeseries', NULL, NULL, 'text', 'combo', 'timeseries', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_timeseries', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', 'autonumeric', 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'node_1', NULL, NULL, 'text', 'text', 'node_1', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'node_2', NULL, NULL, 'text', 'text', 'node_2', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'shape', NULL, NULL, 'text', 'combo', 'shape', NULL, 1, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_shape''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'geom1', NULL, NULL, 'real', 'text', 'geom1', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'geom2', NULL, NULL, 'real', 'text', 'geom2', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'geom3', NULL, NULL, 'real', 'text', 'geom3', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'geom4', NULL, NULL, 'real', 'text', 'geom4', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'curve_transect', NULL, NULL, 'text', 'combo', 'curve_transect', NULL, 0, 1, 'SELECT idval as id, idval from cat_transects', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'kentry', NULL, NULL, 'real', 'text', 'kentry', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'kexit', NULL, NULL, 'real', 'text', 'kexit', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'kavg', NULL, NULL, 'real', 'text', 'kavg', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'flap', NULL, NULL, 'text', 'combo', 'flap', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_value_yesno''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_conduit', 'form_feature', 'tabdata', 'seepage', NULL, NULL, 'text', 'text', 'seepage', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'node_1', NULL, NULL, 'text', 'text', 'node_1', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'node_2', NULL, NULL, 'text', 'text', 'node_2', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'flap', NULL, NULL, 'text', 'combo', 'flap', NULL, NULL, 1, 'SELECT id, idval FROM inp_typevalue WHERE typevalue = ''inp_typevalue_yesno''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'outlet_type', NULL, NULL, 'text', 'combo', 'outlet_type', NULL, NULL, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_outlet_type''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'offsetval', NULL, NULL, 'real', 'text', 'offsetval', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'cd1', NULL, NULL, 'real', 'text', 'cd1', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'cd2', NULL, NULL, 'real', 'text', 'cd2', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_curve', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outlet', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_orifice', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'shape', NULL, NULL, 'text', 'combo', 'shape', NULL, 1, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_shape'' AND id IN (''RECT_OPEN'', ''TRIANGULAR'', ''TRAPEZOIDAL'');', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_weir', 'form_feature', 'tabdata', 'flap', NULL, NULL, 'text', 'combo', 'flap', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_value_yesno''', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_pump', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_curve', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_outfall', 'form_feature', 'tabdata', 'timeseries', NULL, NULL, 'text', 'combo', 'timeseries', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_timeseries', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'curve', NULL, NULL, 'text', 'combo', 'curve', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_curve', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_divider', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'fevap', NULL, NULL, 'real', 'text', 'fevap', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'psi', NULL, NULL, 'real', 'text', 'psi', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'ksat', NULL, NULL, 'real', 'text', 'ksat', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'imd', NULL, NULL, 'real', 'text', 'imd', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_storage', 'form_feature', 'tabdata', 'geom', NULL, NULL, 'geometry', 'text', 'geom', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_junction', 'form_feature', 'tabdata', 'annotation', NULL, NULL, 'text', 'text', 'annotation', NULL, 0, 1, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'id', NULL, NULL, 'text', 'text', 'id', NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'idval', NULL, NULL, 'text', 'text', 'idval', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_files', 'form_feature', 'tabdata', 'fname', NULL, NULL, 'text', 'text', 'fname', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'format', NULL, NULL, 'text', 'text', 'format', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'pattern1', NULL, NULL, 'text', 'combo', 'pattern1', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_pattern', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'pattern2', NULL, NULL, 'text', 'combo', 'pattern2', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_pattern', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'pattern3', NULL, NULL, 'text', 'combo', 'pattern3', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_pattern', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_dwf', 'form_feature', 'tabdata', 'pattern4', NULL, NULL, 'text', 'combo', 'pattern4', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_pattern', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'code', NULL, NULL, 'text', 'text', 'code', NULL, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'descript', NULL, NULL, 'text', 'text', 'descript', NULL, NULL, 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('inp_inflow', 'form_feature', 'tabdata', 'timeseries', NULL, NULL, 'text', 'combo', 'timeseries', NULL, NULL, 1, 'SELECT idval as id, idval FROM cat_timeseries', NULL, NULL, 0, NULL, '{"execute_on": "data"}', NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster', 'lyt_rpt_iber_2_2', 1, 'string', 'combo', 'Raster results', NULL, 0, 1, 'SELECT group_concat(id) AS id, group_concat(idval) AS idval from edit_typevalue WHERE typevalue = ''result_results_raster''', NULL, NULL, 0, NULL, NULL, '0', 'Results 2 raster', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster_cell', 'lyt_rpt_iber_2_2', 2, 'real', 'text', 'Cell size [m]', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '100', 'Size of the pixel [m]', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('culvert', 'form_feature', 'tabdata', 'culvert_type', NULL, NULL, 'text', 'combo', 'culvert_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''culvert_type''', 0, 1, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('pinlet', 'form_feature', 'tabdata', 'outlet_type', NULL, NULL, 'text', 'combo', 'outlet_type', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_inlet_outlet_type''', 0, 1, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('pinlet', 'form_feature', 'tabdata', 'method', NULL, NULL, 'text', 'combo', 'method', NULL, 0, 1, 'SELECT id, idval FROM edit_typevalue WHERE typevalue = ''inp_typevalue_method''', 0, 1, 0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_hazard_pedestrians', 'lyt_rpt_iber_2_1', 3, 'boolean', 'check', 'Pedestrians', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Stability criteria for pedestrians (Martínez-Gomariz et al. 2016)', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_hazard_vehicles', 'lyt_rpt_iber_2_1', 4, 'boolean', 'check', 'Vehicles', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Stability criteria for stationary vehicles (Shand et al. 2011)', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster_maxs', 'lyt_rpt_iber_2_2', 3, 'boolean', 'check', 'Maximums at the end', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Only writes the raster of maximums at the end of the simulation [envelope]', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster_frame', 'lyt_rpt_iber_2_2', 4, 'boolean', 'check', 'Raster frame', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0', 'Generate raster only in a frame', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster_xymin', 'lyt_rpt_iber_2_2', 5, 'string', 'text', 'XYmin', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0,0', 'Type coordinates separed by a comma', NULL);
INSERT INTO config_form_fields
(formname, formtype, tabname, columnname, layoutname, layoutorder, datatype, widgettype, label, placeholder, ismandatory, iseditable, dv_querytext, dv_orderby_id, dv_isnullvalue, hidden, tooltip, addparam, vdefault, descript, widgetcontrols)
VALUES('dlg_options', 'form_options', 'tab_rpt_iber', 'result_results_raster_xymax', 'lyt_rpt_iber_2_2', 6, 'string', 'text', 'XYmax', NULL, 0, 1, NULL, NULL, NULL, 0, NULL, NULL, '0,0', 'Type coordinates separed by a comma', NULL);