
/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

-- ----------------------------------------
-- TRIGGERS FOR SYS GPKG TABLESPACE
-- ----------------------------------------

CREATE TRIGGER "trigger_delete_feature_count_sys_selector" AFTER DELETE ON "sys_selector" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('sys_selector'); END;
CREATE TRIGGER "trigger_delete_feature_count_sys_parameter" AFTER DELETE ON "sys_parameter" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('sys_parameter'); END;
CREATE TRIGGER "trigger_delete_feature_count_sys_typevalue" AFTER DELETE ON "sys_typevalue" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('sys_typevalue'); END;
CREATE TRIGGER "trigger_delete_feature_count_cat_scenario" AFTER DELETE ON "cat_scenario" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('cat_scenario'); END;
CREATE TRIGGER "trigger_delete_feature_count_inp_landuses" AFTER DELETE ON "inp_landuses" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('inp_landuses'); END;
CREATE TRIGGER "trigger_delete_feature_count_inp_curves" AFTER DELETE ON "inp_curves" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('inp_curves'); END;
CREATE TRIGGER "trigger_delete_feature_count_inp_curves_value" AFTER DELETE ON "inp_curves_value" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('inp_curves_value'); END;
CREATE TRIGGER "trigger_delete_feature_count_inp_timeseries" AFTER DELETE ON "inp_timeseries" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('inp_timeseries'); END;
CREATE TRIGGER "trigger_delete_feature_count_inp_timeseries_value" AFTER DELETE ON "inp_timeseries_value" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('inp_timeseries_value'); END;
CREATE TRIGGER "trigger_delete_feature_count_cat_landuses" AFTER DELETE ON "cat_landuses" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('cat_landuses'); END;

CREATE TRIGGER "trigger_delete_feature_count_polygon" AFTER DELETE ON "polygon"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('polygon'); END;
CREATE TRIGGER "trigger_delete_feature_count_point" AFTER DELETE ON "point"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('point'); END;
CREATE TRIGGER "trigger_delete_feature_count_manzone" AFTER DELETE ON "manzone"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('manzone'); END;
CREATE TRIGGER "trigger_delete_feature_count_losszone" AFTER DELETE ON "losszone"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('losszone'); END;
CREATE TRIGGER "trigger_delete_feature_count_roof" AFTER DELETE ON "roof" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('roof'); END;
CREATE TRIGGER "trigger_delete_feature_count_element" AFTER DELETE ON "element"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('element'); END;
CREATE TRIGGER "trigger_delete_feature_count_edge" AFTER DELETE ON "edge" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('edge'); END;
CREATE TRIGGER "trigger_delete_feature_count_vertex" AFTER DELETE ON "vertex" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('vertex'); END;
CREATE TRIGGER "trigger_delete_feature_count_raingage" AFTER DELETE ON "raingage" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('raingage'); END;

CREATE TRIGGER "trigger_insert_feature_count_sys_selector" AFTER INSERT ON "sys_selector" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('sys_selector'); END;
CREATE TRIGGER "trigger_insert_feature_count_sys_parameter" AFTER INSERT ON "sys_parameter" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('sys_parameter'); END;
CREATE TRIGGER "trigger_insert_feature_count_sys_typevalue" AFTER INSERT ON "sys_typevalue" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('sys_typevalue'); END;
CREATE TRIGGER "trigger_insert_feature_count_cat_scenario" AFTER INSERT ON "cat_scenario" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('cat_scenario'); END;
CREATE TRIGGER "trigger_insert_feature_count_inp_landuses" AFTER INSERT ON "inp_landuses" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('inp_landuses'); END;
CREATE TRIGGER "trigger_insert_feature_count_inp_curves" AFTER INSERT ON "inp_curves" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('inp_curves'); END;
CREATE TRIGGER "trigger_insert_feature_count_inp_curves_value" AFTER INSERT ON "inp_curves_value" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('inp_curves_value'); END;
CREATE TRIGGER "trigger_insert_feature_count_inp_timeseries" AFTER INSERT ON "inp_timeseries" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('inp_timeseries'); END;
CREATE TRIGGER "trigger_insert_feature_count_inp_timeseries_value" AFTER INSERT ON "inp_timeseries_value" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('inp_timeseries_value'); END;
CREATE TRIGGER "trigger_insert_feature_count_cat_landuses" AFTER INSERT ON "cat_landuses" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('cat_landuses'); END;

CREATE TRIGGER "trigger_insert_feature_count_polygon" AFTER INSERT ON "polygon"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('polygon'); END;
CREATE TRIGGER "trigger_insert_feature_count_point" AFTER INSERT ON "point"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('point'); END;
CREATE TRIGGER "trigger_insert_feature_count_manzone" AFTER INSERT ON "manzone"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('manzone'); END;
CREATE TRIGGER "trigger_insert_feature_count_losszone" AFTER INSERT ON "losszone" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('losszone'); END;
CREATE TRIGGER "trigger_insert_feature_count_roof" AFTER INSERT ON "roof" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('roof'); END;
CREATE TRIGGER "trigger_insert_feature_count_element" AFTER INSERT ON "element"	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('element'); END;
CREATE TRIGGER "trigger_insert_feature_count_edge" AFTER INSERT ON "edge" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('edge'); END;
CREATE TRIGGER "trigger_insert_feature_count_vertex" AFTER INSERT ON "vertex" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('vertex'); END;
CREATE TRIGGER "trigger_insert_feature_count_raingage" AFTER INSERT ON "raingage" BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('raingage'); END;


CREATE TRIGGER "rtree_polygon_geom_delete" AFTER DELETE ON "polygon" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_polygon_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_point_geom_delete" AFTER DELETE ON "point" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_point_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_manzone_geom_delete" AFTER DELETE ON "manzone" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_manzone_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_losszone_geom_delete" AFTER DELETE ON "losszone" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_losszone_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_roof_geom_delete" AFTER DELETE ON "roof" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_roof_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_element_geom_delete" AFTER DELETE ON "element" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_element_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_edge_geom_delete" AFTER DELETE ON "edge" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_edge_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_vertex_geom_delete" AFTER DELETE ON "vertex" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_vertex_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_raingage_geom_delete" AFTER DELETE ON "raingage" WHEN old."geom" NOT NULL BEGIN DELETE FROM "rtree_raingage_geom" WHERE id= OLD."fid"; END;

CREATE TRIGGER "rtree_polygon_geom_insert" AFTER INSERT ON "polygon" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_polygon_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_point_geom_insert" AFTER INSERT ON "point" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_point_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_manzone_geom_insert" AFTER INSERT ON "manzone" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_manzone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_losszone_geom_insert" AFTER INSERT ON "losszone" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_losszone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_roof_geom_insert" AFTER INSERT ON "roof" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_roof_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_element_geom_insert" AFTER INSERT ON "element" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_element_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_edge_geom_insert" AFTER INSERT ON "edge" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_edge_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_vertex_geom_insert" AFTER INSERT ON "vertex" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_vertex_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;
CREATE TRIGGER "rtree_raingage_geom_insert" AFTER INSERT ON "raingage" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom")) BEGIN INSERT OR REPLACE INTO "rtree_raingage_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;

CREATE TRIGGER "rtree_polygon_geom_update1" AFTER UPDATE OF "geom" ON "polygon" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_polygon_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_point_geom_update1" AFTER UPDATE OF "geom" ON "point" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_point_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_manzone_geom_update1" AFTER UPDATE OF "geom" ON "manzone" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_manzone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_losszone_geom_update1" AFTER UPDATE OF "geom" ON "losszone" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_losszone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_roof_geom_update1" AFTER UPDATE OF "geom" ON "roof" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_roof_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_element_geom_update1" AFTER UPDATE OF "geom" ON "element" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_element_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_edge_geom_update1" AFTER UPDATE OF "geom" ON "edge" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_edge_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_vertex_geom_update1" AFTER UPDATE OF "geom" ON "vertex" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_vertex_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_raingage_geom_update1" AFTER UPDATE OF "geom" ON "raingage" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN INSERT OR REPLACE INTO "rtree_raingage_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;

CREATE TRIGGER "rtree_polygon_geom_update2" AFTER UPDATE OF "geom" ON "polygon" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_polygon_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_point_geom_update2" AFTER UPDATE OF "geom" ON "point" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_point_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_manzone_geom_update2" AFTER UPDATE OF "geom" ON "manzone" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_manzone_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_losszone_geom_update2" AFTER UPDATE OF "geom" ON "losszone" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_losszone_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_roof_geom_update2" AFTER UPDATE OF "geom" ON "roof" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_roof_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_element_geom_update2" AFTER UPDATE OF "geom" ON "element" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_element_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_edge_geom_update2" AFTER UPDATE OF "geom" ON "edge" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_edge_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_vertex_geom_update2" AFTER UPDATE OF "geom" ON "vertex" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_vertex_geom" WHERE id= OLD."fid"; END;
CREATE TRIGGER "rtree_raingage_geom_update2" AFTER UPDATE OF "geom" ON "raingage" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_raingage_geom" WHERE id= OLD."fid"; END;

CREATE TRIGGER "rtree_polygon_geom_update3" AFTER UPDATE ON "polygon" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_polygon_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_polygon_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_point_geom_update3" AFTER UPDATE ON "point" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_point_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_point_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_manzone_geom_update3" AFTER UPDATE ON "manzone" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_manzone_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_manzone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_losszone_geom_update3" AFTER UPDATE ON "losszone" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_losszone_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_losszone_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_roof_geom_update3" AFTER UPDATE ON "roof" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_roof_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_roof_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_element_geom_update3" AFTER UPDATE ON "element" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_element_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_element_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_edge_geom_update3" AFTER UPDATE ON "edge" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_edge_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_edge_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_vertex_geom_update3" AFTER UPDATE ON "vertex" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_vertex_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_vertex_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_raingage_geom_update3" AFTER UPDATE ON "raingage" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_raingage_geom" WHERE id= OLD."fid"; INSERT OR REPLACE INTO "rtree_raingage_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;

CREATE TRIGGER "rtree_polygon_geom_update4" AFTER UPDATE ON "polygon" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_polygon_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_point_geom_update4" AFTER UPDATE ON "point" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_point_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_manzone_geom_update4" AFTER UPDATE ON "manzone" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_manzone_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_losszone_geom_update4" AFTER UPDATE ON "losszone" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_losszone_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_roof_geom_update4" AFTER UPDATE ON "roof" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_roof_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_element_geom_update4" AFTER UPDATE ON "element" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_element_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_edge_geom_update4" AFTER UPDATE ON "edge" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_edge_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_vertex_geom_update4" AFTER UPDATE ON "vertex" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_vertex_geom" WHERE id IN (OLD."fid", NEW."fid"); END;
CREATE TRIGGER "rtree_raingage_geom_update4" AFTER UPDATE ON "raingage" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) BEGIN DELETE FROM "rtree_raingage_geom" WHERE id IN (OLD."fid", NEW."fid"); END;







