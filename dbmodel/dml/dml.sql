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
('mesh_anchor_lines', 'LINESTRING', null),
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
('v_node', 'POINT', null),
('v_arc', 'LINESTRING', null),
('vi_conduits', 'LINESTRING', null),
('vi_outlets', 'LINESTRING', null),
('vi_orifices', 'LINESTRING', null),
('vi_weirs', 'LINESTRING', null),
('vi_pumps', 'LINESTRING', null),
('vi_outfalls', 'POINT', null),
('vi_dividers', 'POINT', null),
('vi_storage', 'POINT', null),
('vi_junctions', 'POINT', null),
('hyetograph', 'POINT', null),
('vi_inlet', 'POINT', null);



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
('v_ui_file', null);
