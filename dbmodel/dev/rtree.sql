/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- -------------------------
-- SPATIAL RTREE INDEX FOR GEOM TABLES
-- -------------------------


CREATE VIRTUAL TABLE rtree_polygon_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_point_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_manzone_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_losszone_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_roof_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_element_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_edge_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_vertex_geom USING rtree(id, minx, maxx, miny, maxy);
CREATE VIRTUAL TABLE rtree_raingage_geom USING rtree(id, minx, maxx, miny, maxy);
