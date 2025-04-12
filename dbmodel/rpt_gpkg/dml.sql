/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


INSERT INTO tables_geom (table_name, isgeom, index_col) values
('rpt_arc', 'LINESTRING', 'code'),
('rpt_arcflow_sum', 'LINESTRING', 'code'),
('rpt_condsurcharge_sum', 'LINESTRING', 'code'),
('rpt_flowclass_sum', 'LINESTRING', 'code'),
('rpt_flowrouting_cont', 'LINESTRING', 'code'),
('arc', 'LINESTRING', 'code'),
('arc', 'LINESTRING', 'code'),
('arc', 'LINESTRING', 'code'),
('rpt_node', 'POINT', 'code'),
('rpt_nodedepth_sum', 'POINT', 'code'),
('rpt_nodeflooding_sum', 'POINT', 'code'),
('rpt_nodeinflow_sum', 'POINT', 'code'),
('rpt_nodesurcharge_sum', 'POINT', 'code'),
('rpt_outfallflow_sum', 'POINT', 'code'),
('rpt_pumping_sum', 'POINT', 'code'),
('rpt_storagevol_sum', 'POINT', 'code')