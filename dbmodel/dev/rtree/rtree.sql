/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- -------------------------
-- SPATIAL RTREE INDEX FOR GEOM TABLES
-- -------------------------


CREATE VIRTUAL TABLE rtree_sector_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_polygon_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_terrain_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_manzone_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_losszone_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_roof_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_elem_tin_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_elem_edge_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_elem_vertex_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_link_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_gully_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_raingage_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_conduit_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_subcatchment_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_outlet_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_orifice_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_weir_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_pump_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_outfall_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_divider_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_storage_geom USING rtree (id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_inp_junction_geom USING rtree (id, minx, maxx, miny, maxy);
