
/*
-- --------------------------
-- SWMM-IBER DB MODEL V1
-- --------------------------

LAST UPDATE
19/04/2023 - Maria Guzmán


CONTENTS:

0. Create table gpkg_ogr_contents
1. Create table no-geom
2. Inserts into gpkg system tables for the no-geom table
3. Create mandatory triggers for no-geom table
4. Create table geom
5. Inserts into gpkg system tables for the geom table
6. Create mandatory triggers for the geom tables


REQUIREMENTS:
*It is recommended to use DBeaver instead of SQLite Studio, although the Geopackage is a Sqlite.
*You can replace 'tablname' by the name of your no-geom table, and 'tablgeo' by the name of your table that contains
 geometry.
*You can create a geopackage by 2 ways: 1) downloading the template from the official web page of Geopackage
 (http://www.geopackage.org/guidance/getting-started.html) or  2) creating an empty geopackage from QGIS. 
 We do not use the second option, as the ST_ functions don't work properly. Instead, we downloaded the official
 template of the Geopackage in which ST_functions work poperly but only 1 system table is missing (gpkg_ogr_contents). 
 Then, before start, we need to create the missing system table.
*/

--0. CREATE GPKG_OGR_CONTENTS

CREATE TABLE gpkg_ogr_contents (
    table_name    TEXT    NOT NULL
                          PRIMARY KEY,
    feature_count INTEGER DEFAULT NULL 
);

/* 1. Create table no-geom
It is important to set an integer as primary key in order to allow you to edit the table. The datatype 'integer' also
works as a serial autonumeric. Accepts multiple primary key. For each datatype (except for integer, text and real),
you must restrict the data type to its data type with the constraint CHECK and function typeof() */

CREATE TABLE tablname (
	tablname_id INTEGER PRIMARY KEY,
	descript text,
	text text,
	active BOOLEAN CHECK (typeof(active) IN (0,1) OR typeof(active)=NULL),
	fieldt text,
	fieldnum real,
	parameter text
);

--2. INSERTS INTO GPKG SYSTEM TABLES
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, min_x, min_y, max_x, max_y, srs_id) 
	VALUES('tablname', 'attributes', 'tablname', '', NULL, NULL, NULL, NULL, 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) 
	VALUES('tablname', 0);

--3. CREATE (mandatory) TRIGGERS FOR THE TABLE
CREATE TRIGGER "trigger_delete_feature_count_tablname" AFTER DELETE ON "tablname" 
	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('tablname'); END;
CREATE TRIGGER "trigger_insert_feature_count_tablname" AFTER INSERT ON "tablname" 
	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('tablname'); END;



--4. CREATE TABLE GEOM
--It is mandatory to name the primary key of the geom-table as 'fid'. Do not accept multiple primary keys.
CREATE TABLE tablgeo (
	fid integer primary key,
	geom	geometry,
	sector_id	integer CHECK (typeof(sector_id) = 'integer'),,
	scenario_id	integer CHECK (typeof(scenario_id) = 'integer'),
	name	text,
	source	text,
	descript	text,
	slope	double CHECK (typeof(slope) = 'double'),
	width	double CHECK (typeof(width) = 'double'),
	manning	double CHECK (typeof(manning) = 'double'),
	outlet_type	text,
	outlet_id	integer CHECK (typeof(outlet_id) = 'integer'),
	totalvol	double CHECK (typeof(totalvol) = 'double'),
	inletvol	double CHECK (typeof(inletvol) = 'double'),
	lossvol	double CHECK (typeof(lossvol) = 'double')
);

--5. CREATE RTREE INDEX. 3 more tables will be created automatically.
--Do not modify '(id, minx, maxx, miny, maxy)' as the rtree table will not work properly.

CREATE VIRTUAL TABLE rtree_tablgeo_geom USING rtree(id, minx, maxx, miny, maxy);

/*
--6 INSERTS INTO GPKG SYSTEM TABLES: 
--TIP: for gpkg_geometry_columns table, it is defined the name of the table, the field of that table that contains the geometry, 
the type of geometry and the SRID. Check that de table name and SRID is okay, as they are fkey for 'gpkg_geometry_columns' and
'gpkg_spatial_ref_sys'. */

INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) 
	VALUES('tablgeo', 'geom', 'POINT', 4326, 0, 0);
INSERT INTO gpkg_ogr_contents (table_name, feature_count) 
	VALUES('tablgeo', 0);
INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change, min_x, min_y, max_x, max_y, srs_id) 
	VALUES('tablgeo', 'features', 'tablgeo', '', 0, 0, 0, 0, 0, 4326);


---Create the triggers for the geom table. 
---These are necessary for the rtree to work properly as an spatial index

CREATE TRIGGER "rtree_tablgeo_geom_delete" AFTER DELETE ON "tablgeo" WHEN old."geom" NOT NULL 
	BEGIN DELETE FROM "rtree_tablgeo_geom" WHERE id = OLD."fid"; END;
CREATE TRIGGER "rtree_tablgeo_geom_insert" AFTER INSERT ON "tablgeo" WHEN (new."geom" NOT NULL AND NOT ST_IsEmpty(NEW."geom"))
	BEGIN INSERT OR REPLACE INTO "rtree_tablgeo_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom") ); END;


CREATE TRIGGER "rtree_tablgeo_geom_update1" AFTER UPDATE OF "geom" ON "tablgeo" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) 
	BEGIN INSERT OR REPLACE INTO "rtree_tablgeo_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_tablgeo_geom_update2" AFTER UPDATE OF "geom" ON "tablgeo" WHEN OLD."fid" = NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) 
	BEGIN DELETE FROM "rtree_tablgeo_geom" WHERE id = OLD."fid"; END;
CREATE TRIGGER "rtree_tablgeo_geom_update3" AFTER UPDATE ON "tablgeo" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" NOTNULL AND NOT ST_IsEmpty(NEW."geom") ) 
	BEGIN DELETE FROM "rtree_tablgeo_geom" WHERE id = OLD."fid"; INSERT OR REPLACE INTO "rtree_tablgeo_geom" VALUES (NEW."fid", ST_MinX(NEW."geom"), ST_MaxX(NEW."geom"), ST_MinY(NEW."geom"), ST_MaxY(NEW."geom")); END;
CREATE TRIGGER "rtree_tablgeo_geom_update4" AFTER UPDATE ON "tablgeo" WHEN OLD."fid" != NEW."fid" AND (NEW."geom" ISNULL OR ST_IsEmpty(NEW."geom") ) 
	BEGIN DELETE FROM "rtree_tablgeo_geom" WHERE id IN (OLD."fid", NEW."fid"); END;

CREATE TRIGGER "trigger_delete_feature_count_tablgeo" AFTER DELETE ON "tablgeo" 
	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 WHERE lower(table_name) = lower('tablgeo'); END;
CREATE TRIGGER "trigger_insert_feature_count_tablgeo" AFTER INSERT ON "tablgeo" 
	BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 WHERE lower(table_name) = lower('tablgeo'); END;

