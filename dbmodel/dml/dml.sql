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

INSERT INTO tables_geom (table_name, isgeom) values
('ground', 'MULTIPOLYGON'),
('roof', 'MULTIPOLYGON'),
('mesh_anchor_points', 'POINT'),
('mesh_anchor_lines', 'LINESTRING'),
('boundary_conditions', 'MULTILINESTRING'),
('inlet', 'POINT'),
('inp_conduit', 'LINESTRING'),
('inp_outlet', 'LINESTRING'),
('inp_orifice', 'LINESTRING'),
('inp_weir', 'LINESTRING'),
('inp_pump', 'LINESTRING'),
('inp_outfall', 'POINT'),
('inp_divider', 'POINT'),
('inp_storage', 'POINT'),
('inp_junction', 'POINT'),
('inp_dwf', 'POINT'),
('v_node', 'POINT'),
('v_arc', 'LINESTRING'),
('vi_conduits', 'LINESTRING'),
('vi_outlets', 'LINESTRING'),
('vi_orifices', 'LINESTRING'),
('vi_weirs', 'LINESTRING'),
('vi_pumps', 'LINESTRING'),
('vi_outfalls', 'POINT'),
('vi_dividers', 'POINT'),
('vi_storage', 'POINT'),
('vi_junctions', 'POINT');



insert into tables_nogeom (table_name) values
('config_param_user'),
('cat_bscenario'),
('cat_file'),
('cat_landuses'),
('cat_transects'),
('cat_curve'),
('cat_curve_value'),
('cat_timeseries'),
('cat_timeseries_value'),
('cat_pattern'),
('cat_pattern_value'),
('cat_raster'),
('cat_raster_value'),
('cat_controls'),
('inp_files'),
('inp_inflow'),
('rpt_arc'),
('rpt_arcflow_sum'),
('rpt_cat_result'),
('rpt_condsurcharge_sum'),
('rpt_continuity_errors'),
('rpt_control_actions_taken'),
('rpt_critical_elements'),
('rpt_flowclass_sum'),
('rpt_flowrouting_cont'),
('rpt_groundwater_cont'),
('rpt_high_conterrors'),
('rpt_high_flowinest_ind'),
('rpt_instability_index'),
('rpt_node'),
('rpt_nodedepth_sum'),
('rpt_nodeflooding_sum'),
('rpt_nodeinflow_sum'),
('rpt_nodesurcharge_sum'),
('rpt_outfallflow_sum'),
('rpt_pumping_sum'),
('rpt_qualrouting_cont'),
('rpt_routing_timestep'),
('rpt_storagevol_sum'),
('rpt_timestep_critelem'),
('rpt_warning_summary'),
('vi_curves'),
('vi_timeseries'),
('vi_patterns'),
('vi_losses'),
('vi_xsections'),
('vi_dwf'),
('vi_title'),
('vi_files'),
('vi_options'),
('vi_controls'),
('vi_inflows'),
('vi_transects'),
('vi_report'),
('v_ui_file');
