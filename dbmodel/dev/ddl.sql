/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


-- --------------------
-- TABLAS NO-GEOM
-----------------------

CREATE TABLE sys_selector (
    selector_id integer PRIMARY KEY,
    parameter text,
    value integer CHECK (typeof(value)='integer')
);

CREATE TABLE sys_parameter (
    parameter_id integer PRIMARY KEY,
	parameter text,
    value text
);

CREATE TABLE sys_typevalue (
    typevalue_id integer PRIMARY KEY,
	typevalue text,
    id text,
    idval text,
    descript text,
    active boolean CHECK (typeof(active) IN (0,1) OR typeof(active)=NULL)
);

CREATE TABLE cat_scenario (
    scenario_id integer PRIMARY KEY,
    name text NULL,
    descript text NULL,
    active boolean CHECK (typeof(active) IN (0,1,NULL) OR typeof(active)=NULL)
);

CREATE TABLE inp_landuses (
    landuses_id  integer PRIMARY KEY,
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    name text,
    manning double CHECK (typeof(manning)='double'),
    active  boolean CHECK (typeof(active) IN (0,1) OR typeof(active)=NULL)
);

--CREATE TABLE inp_landuses_value (

--);

CREATE TABLE inp_curves (
    curve_id integer PRIMARY KEY,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    active boolean CHECK (typeof(active) IN (0,1) OR typeof(active)=NULL)
);

CREATE TABLE inp_curves_value (
    curve_id integer PRIMARY KEY,
    xval real,
    yval real
);

CREATE TABLE inp_timeseries (
    timser_id integer PRIMARY KEY,
    name text,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    descript text,
    timser_type text,
    active boolean CHECK (typeof(active) IN (0,1) OR typeof(active)=NULL)
);

CREATE TABLE inp_timeseries_value (
    rid integer PRIMARY KEY,
    timser_id text,
    date datetime,
    time datetime,
    val real
);


-- ------------------------
-- TABLAS GEOM
-- ----------------------
CREATE TABLE polygon (
    fid integer PRIMARY KEY,
    pol_id integer CHECK (typeof(pol_id)='integer'),
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    dmax double CHECK (typeof(dmax)='double'),
    structured boolean CHECK (typeof(structured) IN (0,1) OR typeof(structured)=NULL),
    descript text
);

CREATE TABLE point (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    elevation double CHECK (typeof(elevation)='double')
);

CREATE TABLE manzone (
    fid integer PRIMARY KEY,
    manzone_id integer CHECK (typeof(manzone_id)='integer'),
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    name text,
    source text,
    descript text,
    land_use integer CHECK (typeof(land_use)='integer'),
    custom_manning double CHECK (typeof(custom_manning)='double')
);

CREATE TABLE losszone (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    name text,
    source text,
    descript text,
    losslin_aparam double CHECK (typeof(losslin_aparam)='double'),
    losslin_bparam double CHECK (typeof(losslin_bparam)='double'),
    lossscs_aparam double CHECK (typeof(lossscs_aparam)='double'),
    lossscs_bparam double CHECK (typeof(lossscs_bparam)='double'),
    losshort_aparam double CHECK (typeof(losshort_aparam)='double'),
    losshort_bparam double CHECK (typeof(losshort_bparam)='double'),
    lossgreen_aparam double CHECK (typeof(lossgreen_aparam)='double'),
    lossgreen_bparam double CHECK (typeof(lossgreen_bparam)='double')
);

CREATE TABLE roof (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    name text,
    source text,
    descript text,
    slope double CHECK (typeof(slope)='double'),
    width double CHECK (typeof(width)='double'),
    manning double CHECK (typeof(manning)='double'),
    outlet_type text,
    outlet_id integer CHECK (typeof(outlet_id)='integer'),
    totalvol double CHECK (typeof(totalvol)='double'),
    inletvol double CHECK (typeof(inletvol)='double'),
    lossvol double CHECK (typeof(lossvol)='double')
);

CREATE TABLE element (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer NULL CHECK (typeof(sector_id)='integer'),
    scenario_id integer NULL CHECK (typeof(scenario_id)='integer'),
    manzone_id integer NULL CHECK (typeof(manzone_id)='integer'),
    losszone_id integer NULL CHECK (typeof(losszone_id)='integer'),
    roof_id integer NULL CHECK (typeof(roof_id)='integer'),
    source text NULL,
    vertex_id1 real NULL,
    vertex_id2 real NULL,
    vertex_id3 real NULL,
    vertex_id4 real NULL,
    ini_vx real NULL,
    ini_vy real NULL,
    ini_type real NULL, 
    ini_value real NULL 
);

CREATE TABLE edge (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    source text,
    vertex_id1 integer CHECK (typeof(vertex_id1)='integer'),
    vertex_id2 integer CHECK (typeof(vertex_id2)='integer')
);

CREATE TABLE vertex (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    scenario_id integer CHECK (typeof(scenario_id)='integer'),
    source text,
    elevation double CHECK (typeof(elevation)='double')
);

CREATE TABLE raingage (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer'),
    descript text,
    name text,
    rain_type boolean CHECK (typeof(rain_type) IN (0,1) OR typeof(rain_type)=NULL),
    timeseries_id integer CHECK (typeof(timeseries_id)='integer')
);


