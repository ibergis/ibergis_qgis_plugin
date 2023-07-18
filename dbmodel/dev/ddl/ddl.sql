/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


-- --------------------
-- NO-GEOM TABLES
-----------------------

CREATE TABLE sys_parameter (
    parameter_id integer PRIMARY KEY,
    parameter text CHECK (typeof(parameter)='text' OR parameter=NULL),
    value text CHECK (typeof(value)='text' OR value=NULL)
);

CREATE TABLE sys_typevalue (
    typevalue_id integer PRIMARY KEY,
    typevalue text CHECK (typeof(typevalue)='text' OR typevalue=NULL),
    id text CHECK (typeof(id)='text' OR id=NULL),
    idval text CHECK (typeof(idval)='text' OR idval=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE cat_scenario (
    scenario_id integer PRIMARY KEY,
    name text CHECK (typeof(name)='text' OR name=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE inp_landuses (
    landuses_id  integer PRIMARY KEY,
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    name text CHECK (typeof(name)='text' OR name=NULL),
    manning real CHECK (typeof(manning)='real' OR manning=NULL),
    active  boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE inp_curves (
    curve_id integer PRIMARY KEY,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE inp_curves_value (
    curve_id integer PRIMARY KEY,
    xval real CHECK (typeof(xval)='real' OR xval=NULL),
    yval real CHECK (typeof(yval)='real' OR yval=NULL)
);

CREATE TABLE inp_timeseries (
    timser_id integer PRIMARY KEY,
    name text CHECK (typeof(name)='text' OR name=NULL),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    timser_type text CHECK (typeof(timser_type)='text' OR timser_type=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE inp_timeseries_value (
    rid integer PRIMARY KEY,
    timser_id text CHECK (typeof(timser_id)='text' OR timser_id=NULL),
    date datetime CHECK (typeof(date)='datetime' OR date=NULL),
    time datetime CHECK (typeof(time)='datetime' OR time=NULL),
    val real CHECK (typeof(val)='real' OR val=NULL)
);


-- ------------------------
-- GEOM TABLES
-- ----------------------
CREATE TABLE polygon (
    fid integer PRIMARY KEY,
    pol_id integer CHECK (typeof(pol_id)='integer' OR pol_id=NULL),
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    dmax real CHECK (typeof(dmax)='real' OR dmax=NULL),
    structured boolean CHECK (typeof(structured) IN (0,1,NULL)),
    descript text CHECK (typeof(descript)='text' OR descript=NULL)
);

CREATE TABLE point (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    elevation real CHECK (typeof(elevation)='real' OR elevation = NULL)
);

CREATE TABLE manzone (
    fid integer PRIMARY KEY,
    manzone_id integer CHECK (typeof(manzone_id)='integer' OR manzone_id=NULL),
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    name text CHECK (typeof(name)='text' OR name=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    land_use integer CHECK (typeof(land_use)='integer' OR land_use=NULL),
    custom_manning real CHECK (typeof(custom_manning)='real' OR custom_manning=NULL)
);

CREATE TABLE losszone (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    name text CHECK (typeof(name)='text' OR name=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    losslin_aparam real CHECK (typeof(losslin_aparam)='real' OR losslin_aparam=NULL),
    losslin_bparam real CHECK (typeof(losslin_bparam)='real' OR losslin_bparam=NULL),
    lossscs_aparam real CHECK (typeof(lossscs_aparam)='real' OR lossscs_aparam=NULL),
    lossscs_bparam real CHECK (typeof(lossscs_bparam)='real' OR lossscs_bparam=NULL),
    losshort_aparam real CHECK (typeof(losshort_aparam)='real' OR losshort_aparam=NULL),
    losshort_bparam real CHECK (typeof(losshort_bparam)='real' OR losshort_bparam=NULL),
    lossgreen_aparam real CHECK (typeof(lossgreen_aparam)='real' OR lossgreen_aparam=NULL),
    lossgreen_bparam real CHECK (typeof(lossgreen_bparam)='real' OR lossgreen_bparam=NULL)
);

CREATE TABLE roof (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    name text CHECK (typeof(name)='text' OR name=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    slope real CHECK (typeof(slope)='real' OR slope=NULL),
    width real CHECK (typeof(width)='real' OR width=NULL),
    manning real CHECK (typeof(manning)='real' OR manning=NULL),
    outlet_type text CHECK (typeof(outlet_type)='text' OR outlet_type=NULL),
    outlet_id integer CHECK (typeof(outlet_id)='integer' OR outlet_id=NULL),
    totalvol real CHECK (typeof(totalvol)='real' OR totalvol=NULL),
    inletvol real CHECK (typeof(inletvol)='real' OR inletvol=NULL),
    lossvol real CHECK (typeof(lossvol)='real' OR lossvol=NULL)
);

CREATE TABLE element (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    manzone_id integer CHECK (typeof(manzone_id)='integer' OR manzone_id=NULL),
    losszone_id integer NULL CHECK (typeof(losszone_id)='integer' OR losszone_id=NULL),
    roof_id integer CHECK (typeof(roof_id)='integer' OR roof_id=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    vertex_id1 real CHECK (typeof(vertex_id1)='real' OR vertex_id1=NULL),
    vertex_id2 real CHECK (typeof(vertex_id2)='real' OR vertex_id2=NULL),
    vertex_id3 real CHECK (typeof(vertex_id3)='real' OR vertex_id3=NULL),
    vertex_id4 real CHECK (typeof(vertex_id4)='real' OR vertex_id4=NULL),
    ini_vx real CHECK (typeof(ini_vx)='real' OR ini_vx=NULL),
    ini_vy real CHECK (typeof(ini_vy)='real' OR ini_vy=NULL),
    ini_type real CHECK (typeof(ini_type)='real' OR ini_type=NULL),
    ini_value real CHECK (typeof(ini_value)='real' OR ini_value=NULL)
);

CREATE TABLE edge (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    vertex_id1 integer CHECK (typeof(vertex_id1)='integer' OR vertex_id1=NULL),
    vertex_id2 integer CHECK (typeof(vertex_id2)='integer' OR vertex_id2=NULL)
);

CREATE TABLE vertex (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    source text CHECK (typeof(source)='text' OR source=NULL),
    elevation real CHECK (typeof(elevation)='real' OR elevation=NULL)
);

CREATE TABLE raingage (
    fid integer PRIMARY KEY,
    geom geometry,
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    name text CHECK (typeof(name)='text' OR name=NULL),
    rain_type boolean CHECK (typeof(rain_type) IN (0,1,NULL)),
    timeseries_id integer CHECK (typeof(timeseries_id)='integer' OR timeseries_id=NULL)
);


