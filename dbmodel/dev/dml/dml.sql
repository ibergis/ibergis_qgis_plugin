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
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_scenario', 'attributes', 'cat_scenario', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_arc', 'attributes', 'cat_arc', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_curve', 'attributes', 'cat_curve', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_curve_value', 'attributes', 'cat_curve_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_timeseries', 'attributes', 'cat_timeseries', '',  0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_timeseries_value', 'attributes', 'cat_timeseries_value', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_landuses', 'attributes', 'cat_landuses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_grate', 'attributes', 'cat_grate', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('cat_pattern', 'attributes', 'cat_pattern', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_files', 'attributes', 'inp_files', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_arc', 'attributes', 'rpt_arc', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_arcflow_sum', 'attributes', 'rpt_arcflow_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_arcpolload_sum', 'attributes', 'rpt_arcpolload_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_arcpollutant_sum', 'attributes', 'rpt_arcpollutant_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_cat_result', 'attributes', 'rpt_cat_result', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_condsurcharge_sum', 'attributes', 'rpt_condsurcharge_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_continuity_errors', 'attributes', 'rpt_continuity_errors', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_control_actions_taken', 'attributes', 'rpt_control_actions_taken', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_critical_elements', 'attributes', 'rpt_critical_elements', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_flowclass_sum', 'attributes', 'rpt_flowclass_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_flowrouting_cont', 'attributes', 'rpt_flowrouting_cont', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_groundwater_cont', 'attributes', 'rpt_groundwater_cont', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_high_conterrors', 'attributes', 'rpt_high_conterrors', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_high_flowinest_ind', 'attributes', 'rpt_high_flowinest_ind', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_instability_index', 'attributes', 'rpt_instability_index', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_lidperformance_sum', 'attributes', 'rpt_lidperformance_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_node', 'attributes', 'rpt_node', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_nodedepth_sum', 'attributes', 'rpt_nodedepth_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_nodeflooding_sum', 'attributes', 'rpt_nodeflooding_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_nodeinflow_sum', 'attributes', 'rpt_nodeinflow_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_nodesurcharge_sum', 'attributes', 'rpt_nodesurcharge_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_outfallflow_sum', 'attributes', 'rpt_outfallflow_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_outfallload_sum', 'attributes', 'rpt_outfallload_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_pumping_sum', 'attributes', 'rpt_pumping_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_qualrouting_cont', 'attributes', 'rpt_qualrouting_cont', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_rainfall_dep', 'attributes', 'rpt_rainfall_dep', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_routing_timestep', 'attributes', 'rpt_routing_timestep', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_runoff_qual', 'attributes', 'rpt_runoff_qual', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_runoff_quant', 'attributes', 'rpt_runoff_quant', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_storagevol_sum', 'attributes', 'rpt_storagevol_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_subcatchment', 'attributes', 'rpt_subcatchment', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_subcatchrunoff_sum', 'attributes', 'rpt_subcatchrunoff_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_subcatchwashoff_sum', 'attributes', 'rpt_subcatchwashoff_sum', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_summary_arc', 'attributes', 'rpt_summary_arc', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_summary_crossection', 'attributes', 'rpt_summary_crossection', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_summary_node', 'attributes', 'rpt_summary_node', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_summary_raingage', 'attributes', 'rpt_summary_raingage', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_summary_subcatchment', 'attributes', 'rpt_summary_subcatchment', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_timestep_critelem', 'attributes', 'rpt_timestep_critelem', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('rpt_warning_summary', 'attributes', 'rpt_warning_summary', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_rpt_compare', 'attributes', 'selector_rpt_compare', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_rpt_compare_tstep', 'attributes', 'selector_rpt_compare_tstep', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_rpt_main', 'attributes', 'selector_rpt_main', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('selector_rpt_main_tstep', 'attributes', 'selector_rpt_main_tstep', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_curves', 'attributes', 'vi_curves', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_timeseries', 'attributes', 'vi_timeseries', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_patterns', 'attributes', 'vi_patterns', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_landuses', 'attributes', 'vi_landuses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_subareas', 'attributes', 'vi_subareas', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_losses', 'attributes', 'vi_losses', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_xsections', 'attributes', 'vi_xsections', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_dwf', 'attributes', 'vi_dwf', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_infiltration', 'attributes', 'vi_infiltration', '', 0, 0, 0, 0, 0, 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_raingages', 'attributes', 'vi_raingages', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_conduits', 'attributes', 'vi_conduits', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_subcatchments', 'attributes', 'vi_subcatchments', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_outlets', 'attributes', 'vi_outlets', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_orifices', 'attributes', 'vi_orifices', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_weirs', 'attributes', 'vi_weirs', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_pumps', 'attributes', 'vi_pumps', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_outfalls', 'attributes', 'vi_outfalls', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_dividers', 'attributes', 'vi_dividers', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_storage', 'attributes', 'vi_storage', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_junctions', 'attributes', 'vi_junctions', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_title', 'attributes', 'vi_title', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_files', 'attributes', 'vi_files', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('vi_options', 'attributes', 'vi_options', '', 0, 0, 0, 0, 0, <SRID_VALUE>);




INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('sector', 'features', 'sector', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground', 'features', 'ground', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground_roughness', 'features', 'ground_roughness', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('ground_losses', 'features', 'ground_losses', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('roof', 'features', 'roof', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_tin', 'features', 'mesh_tin', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_roof', 'features', 'mesh_roof', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_anchor_points', 'features', 'mesh_anchor_points', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('mesh_anchor_lines', 'features', 'mesh_anchor_lines', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
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
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('inp_dwf', 'features', 'inp_dwf', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('v_node', 'features', 'v_node', '', 0, 0, 0, 0, 0, <SRID_VALUE>);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id) VALUES('v_arc', 'features', 'v_arc', '', 0, 0, 0, 0, 0, <SRID_VALUE>);






INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_sector', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_scenario', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('config_param_user', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('edit_typevalue', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_scenario', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_arc', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_curve', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_curve_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_timeseries', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_timeseries_value', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_landuses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_grate', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('cat_pattern', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_files', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_arc', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_arcflow_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_arcpolload_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_arcpollutant_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_cat_result', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_condsurcharge_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_continuity_errors', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_control_actions_taken', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_critical_elements', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_flowclass_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_flowrouting_cont', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_groundwater_cont', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_high_conterrors', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_high_flowinest_ind', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_instability_index', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_lidperformance_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_node', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_nodedepth_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_nodeflooding_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_nodeinflow_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_nodesurcharge_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_outfallflow_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_outfallload_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_pumping_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_qualrouting_cont', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_rainfall_dep', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_routing_timestep', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_runoff_qual', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_runoff_quant', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_storagevol_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_subcatchment', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_subcatchrunoff_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_subcatchwashoff_sum', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_summary_arc', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_summary_crossection', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_summary_node', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_summary_raingage', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_summary_subcatchment', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_timestep_critelem', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('rpt_warning_summary', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_rpt_compare', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_rpt_compare_tstep', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_rpt_main', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('selector_rpt_main_tstep', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_conduits', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_subcatchments', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_outlets', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_orifices', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_weirs', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_pumps', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_outfalls', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_dividers', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_storage', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_junctions', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_raingages', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_curves', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_timeseries', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_patterns', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_landuses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_subareas', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_losses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_xsections', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_dwf', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_infiltration', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_title', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_files', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('vi_options', 0);


INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('sector', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground_roughness', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('ground_losses', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('roof', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_tin', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_roof', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_anchor_points', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('mesh_anchor_lines', 0);
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
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('inp_dwf', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('v_node', 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES('v_arc', 0);



INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('sector', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground_roughness', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('ground_losses', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('roof', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_tin', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_roof', 'geom', 'MULTIPOLYGON', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_anchor_points', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('mesh_anchor_lines', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);
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
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('inp_dwf', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('v_node', 'geom', 'POINT', <SRID_VALUE>, 0, 0);
INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES('v_arc', 'geom', 'LINESTRING', <SRID_VALUE>, 0, 0);