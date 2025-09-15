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

-- ----------------------------
-- INSERTS INTO SYS GPKG TABLES
-- ----------------------------
INSERT INTO tables_geom (table_name, isgeom, index_col) VALUES
('rpt_arc', 'LINESTRING', 'code'),
('rpt_arcflow_sum', 'LINESTRING', 'code'),
('rpt_condsurcharge_sum', 'LINESTRING', 'code'),
('rpt_flowclass_sum', 'LINESTRING', 'code'),
('rpt_flowrouting_cont', 'LINESTRING', 'code'),
('rpt_node', 'POINT', 'code'),
('rpt_nodedepth_sum', 'POINT', 'code'),
('rpt_nodeflooding_sum', 'POINT', 'code'),
('rpt_nodeinflow_sum', 'POINT', 'code'),
('rpt_nodesurcharge_sum', 'POINT', 'code'),
('rpt_outfallflow_sum', 'POINT', 'code'),
('rpt_pumping_sum', 'LINESTRING', 'code'),
('rpt_storagevol_sum', 'POINT', 'code');

-- ----------------------------
-- FIX EXTENT OF LAYERS
-- ----------------------------
-- Update gpkg_contents with actual extents from geometries
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_arc WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_arc';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_arcflow_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_arcflow_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_condsurcharge_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_condsurcharge_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_flowclass_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_flowclass_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_flowrouting_cont WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_flowrouting_cont';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_node WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_node';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_nodedepth_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_nodedepth_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_nodeflooding_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_nodeflooding_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_nodeinflow_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_nodeinflow_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_nodesurcharge_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_nodesurcharge_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_outfallflow_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_outfallflow_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_pumping_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_pumping_sum';
UPDATE gpkg_contents SET min_x = a.min_x, min_y = a.min_y, max_x = a.max_x, max_y = a.max_y FROM (SELECT MIN(st_minx(geom)) AS min_x, MIN(st_miny(geom)) AS min_y, MAX(st_maxx(geom)) AS max_x, MAX(st_maxy(geom)) AS max_y FROM rpt_storagevol_sum WHERE geom IS NOT NULL)a WHERE table_name = 'rpt_storagevol_sum';