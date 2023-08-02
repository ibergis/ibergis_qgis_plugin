/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


-- --------------
-- NO-GEOM TABLES
-----------------

CREATE TABLE sys_selector (
    selector_id integer PRIMARY KEY,
    parameter text CHECK (typeof(parameter)='text' OR parameter=NULL),
    value integer CHECK (typeof(value)='integer' OR value=NULL)
);

CREATE TABLE selector_sector (
    sector_id integer primary key,
    idval text unique check (typeof(idval)='text' or idval = not null),
);

CREATE TABLE selector_scenario (
    scenario_id integer primary key,
    idval text unique check (typeof(idval)='text' or idval = not null),
);

CREATE TABLE config_param_user (
	parameter_id text primary key,	
	value text CHECK (typeof(value)='text' OR value=NULL)
);

CREATE TABLE cat_landuses (
	id integer primary key,
	idval text check (typeof(idval)='text' or typeof(idval)=null),
	sector_id check (typeof(sector_id)='integer' or typeof(sector_id)= null),
	scenario_id check (typeof(scenario_id)='integer' or typeof(scenario_id)= null),
    descript text check (typeof(descript)='text' or typeof(descript)=null),
	manning real check (typeof(manning)='real' or typeof(manning)=null),
	active boolean check (typeof(active) in (0,1, null))
);

CREATE TABLE cat_scenario (
    id integer primary key,
    idval text check (typeof(idval)='text' or typeof(idval)=null),
    sector_id check (typeof(sector_id)='integer' or typeof(sector_id)= null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) --unique idval
);

CREATE TABLE cat_grate (
    id integer primary key,
    idval text check (typeof(idval)='text' or typeof(idval)=null),
    length real check (typeof(length) = 'real' or length = null),
    width real check (typeof(width) = 'real' or width = null),
    a_param real check (typeof(a_param) = 'real' or a_param = null),
    b_param real check (typeof(b_param) = 'real' or b_param = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE cat_curve (
    id integer primary key,
    idval text unique check (typeof(idval)='text' or typeof(idval)=null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer check (typeof(scenario_id)='integer' or scenario_id=null),
    descript text check (typeof(descript)='text' or typeof(descript)=null),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE cat_curve_value (
    id integer primary key,
    idval text unique check (typeof(idval)='text' or idval = not null),
    xcoord real CHECK (typeof(xcoord)='real' OR xcoord=NULL),
    ycoord real CHECK (typeof(ycoord)='real' OR ycoord=NULL)
);

CREATE TABLE cat_timeseries (
    id integer primary key,
    idval text check (typeof(idval)='text' or typeof(idval)=null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer check (typeof(scenario_id)='integer' or scenario_id=null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    timeseries_type text CHECK (typeof(timeseries_type)='text' OR timeseries_type=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE cat_timeseries_value (
    id integer primary key,
    idval text unique check (typeof(idval)='text' or idval = not null),
    date datetime CHECK (typeof(date)='datetime' OR date=NULL),
    time datetime CHECK (typeof(time)='datetime' OR time=NULL),
    value real CHECK (typeof(value)='real' OR value=NULL)
);

CREATE TABLE cat_pattern (
    id integer primary key,
    idval text unique check (typeof(idval)='text' or idval = not null),
    descript text check (typeof(descript) = 'text' or descript = null),
    active boolean check (typeof(active) in (0, 1, null))
);

-- -----------
-- GEOM TABLES
-- -----------

create table sector (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text check (typeof(descript) = 'text' or descript = null),
    stylesheet text check (typeof(stylesheet) = 'text' or stylesheet = null),
    active boolean check (typeof(active) in (0, 1, null)),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE polygon (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    cellsize real CHECK (typeof(cellsize)='real' OR cellsize=NULL),
    structured boolean CHECK (typeof(structured) IN (0,1,NULL)),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE manzone (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    manzone_id integer CHECK (typeof(manzone_id)='integer' OR manzone_id=NULL),
    land_use integer CHECK (typeof(land_use)='integer' OR land_use=NULL),
    custom_manning real CHECK (typeof(custom_manning)='real' OR custom_manning=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE losszone (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    losslin_aparam real CHECK (typeof(losslin_aparam)='real' OR losslin_aparam=NULL),
    losslin_bparam real CHECK (typeof(losslin_bparam)='real' OR losslin_bparam=NULL),
    lossscs_aparam real CHECK (typeof(lossscs_aparam)='real' OR lossscs_aparam=NULL),
    lossscs_bparam real CHECK (typeof(lossscs_bparam)='real' OR lossscs_bparam=NULL),
    losshort_aparam real CHECK (typeof(losshort_aparam)='real' OR losshort_aparam=NULL),
    losshort_bparam real CHECK (typeof(losshort_bparam)='real' OR losshort_bparam=NULL),
    lossgreen_aparam real CHECK (typeof(lossgreen_aparam)='real' OR lossgreen_aparam=NULL),
    lossgreen_bparam real CHECK (typeof(lossgreen_bparam)='real' OR lossgreen_bparam=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE roof (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    slope real CHECK (typeof(slope)='real' OR slope=NULL),
    width real CHECK (typeof(width)='real' OR width=NULL),
    manning real CHECK (typeof(manning)='real' OR manning=NULL),
    outlet_type text CHECK (typeof(outlet_type)='text' OR outlet_type=NULL),
    outlet_id integer CHECK (typeof(outlet_id)='integer' OR outlet_id=NULL),
    totalvol real CHECK (typeof(totalvol)='real' OR totalvol=NULL),
    inletvol real CHECK (typeof(inletvol)='real' OR inletvol=NULL),
    lossvol real CHECK (typeof(lossvol)='real' OR lossvol=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE elem_tin (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    manzone_id integer CHECK (typeof(manzone_id)='integer' OR manzone_id=NULL),
    losszone_id integer NULL CHECK (typeof(losszone_id)='integer' OR losszone_id=NULL),
    roof_id integer CHECK (typeof(roof_id)='integer' OR roof_id=NULL),
    vertex_id1 real CHECK (typeof(vertex_id1)='real' OR vertex_id1=NULL),
    vertex_id2 real CHECK (typeof(vertex_id2)='real' OR vertex_id2=NULL),
    vertex_id3 real CHECK (typeof(vertex_id3)='real' OR vertex_id3=NULL),
    vertex_id4 real CHECK (typeof(vertex_id4)='real' OR vertex_id4=NULL),
    ini_vx real CHECK (typeof(ini_vx)='real' OR ini_vx=NULL),
    ini_vy real CHECK (typeof(ini_vy)='real' OR ini_vy=NULL),
    ini_type real CHECK (typeof(ini_type)='real' OR ini_type=NULL),
    ini_value real CHECK (typeof(ini_value)='real' OR ini_value=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE elem_edge (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    vertex_id1 integer CHECK (typeof(vertex_id1)='integer' OR vertex_id1=NULL),
    vertex_id2 integer CHECK (typeof(vertex_id2)='integer' OR vertex_id2=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE elem_vertex (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    elevation real CHECK (typeof(elevation)='real' OR elevation=NULL),
	latitude real CHECK (typeof(latitude)='real' OR latitude=NULL),
	longitude real CHECK (typeof(longitude)='real' OR longitude=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE raingage (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer CHECK (typeof(sector_id)='integer' OR sector_id=NULL),
    scenario_id integer CHECK (typeof(scenario_id)='integer' OR scenario_id=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    rain_type boolean CHECK (typeof(rain_type) IN (0,1,NULL)),
    form_type text check (typeof(form_type) = 'text' or form_type = null),
    timeseries_id integer CHECK (typeof(timeseries_id)='integer' OR timeseries_id=NULL),
    rg_id text check (typeof(rg_id) = 'text' or rg_id = null),
    intvl text check (typeof(intvl) = 'text' or intvl = null),
    scf real check (typeof(scf) = 'real' or scf = null),
    fname text check (typeof(fname) = 'text' or fname = null),
    sta text check (typeof(sta) = 'text' or sta = null),
    units text check (typeof(units) = 'text' or units = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE link (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_d integer check (typeof(scenario_d) = 'integer' or scenario_d = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    feature_type text check (typeof(feature_type) = 'text' or feature_type = null),
    feature_id text check (typeof(feature_id) = 'text' or feature_id = null),
    exit_type text check (typeof(exit_type) = 'text' or exit_type = null),
    exit_id text check (typeof(exit_id) = 'text' or exit_id = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE gully (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_d integer check (typeof(scenario_d) = 'integer' or scenario_d = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    outlet_type text check (typeof(outlet_type) = 'text' or outlet_type = null),
    node_id text check (typeof(node_id) = 'text' or node_id = null),
    top_elev real check (typeof(top_elev) = 'real' or top_elev = null),
    custom_top_elev real check (typeof(custom_top_elev) = 'real' or custom_top_elev = null),
    gratecat_id text check (typeof(gratecat_id) = 'text' or gratecat_id = null),
    custom_width real check (typeof(custom_width) = 'real' or custom_width = null),
    custom_length real check (typeof(custom_length) = 'real' or custom_length = null),
    method text check (typeof(method) = 'text' or method = null),
    weir_cd real check (typeof(weir_cd) = 'real' or weir_cd = null),
    orifice_cd real check (typeof(orifice_cd) = 'real' or orifice_cd = null),
    custom_a_param real check (typeof(custom_a_param) = 'real' or custom_a_param = null),
    custom_b_param real check (typeof(custom_b_param) = 'real' or custom_b_param = null),
    efficiency real check (typeof(efficiency) = 'real' or efficiency = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE conduit (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node1 text check (typeof(node1) = 'text' or node1 = null),
    node2 text check (typeof(node2) = 'text' or node2 = null),
    shape text check (typeof(shape) = 'text' or shape = null),
    shape_trnsct text check (typeof(shape_trnsct) = 'text' or shape_trnsct = null),
    custom_length real check (typeof(custom_length) = 'real' or custom_length = null),
    matcat_id text check (typeof(matcat_id) = 'text' or matcat_id = null),
    custom_roughness real check (typeof(custom_roughness) = 'real' or custom_roughness = null),
    z1 real check (typeof(z1) = 'real' or z1 = null),
    custom_z1 real check (typeof(custom_z1) = 'real' or custom_z1 = null),
    z2 real check (typeof(z2) = 'real' or z2 = null),
    custom_z2 real check (typeof(custom_z2) = 'real' or custom_z2 = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null),
    geom3 real check (typeof(geom3) = 'real' or geom3 = null),
    geom4 real check (typeof(geom4) = 'real' or geom4 = null),
    barrels real check (typeof(barrels) = 'real' or barrels = null),
    culvert text check (typeof(culvert) = 'text' or culvert = null),
    kentry real check (typeof(kentry) = 'real' or kentry = null),
    kexit real check (typeof(kexit) = 'real' or kexit = null),
    kavg real check (typeof(kavg) = 'real' or kavg = null),
    flap text check (typeof(flap) = 'text' or flap = null),
    seepage real check (typeof(seepage) = 'real' or seepage = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE subcatchment ( 
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    rg_id text check (typeof(rg_id) = 'text' or rg_id = null),
    outlet_id text check (typeof(outlet_id) = 'text' or outlet_id = null),
    area real check (typeof(area) = 'real' or area = null),
    imperv real check (typeof(imperv) = 'real' or imperv = null),
    width real check (typeof(width) = 'real' or width = null),
    slope real check (typeof(slope) = 'real' or slope = null),
    clength real check (typeof(clength) = 'real' or clength = null),
    snow_id text check (typeof(snow_id) = 'text' or snow_id = null),
    nimp real check (typeof(nimp) = 'real' or nimp = null),
    nperv real check (typeof(nperv) = 'real' or nperv = null),
    simp real check (typeof(simp) = 'real' or simp = null),
    sperv real check (typeof(sperv) = 'real' or sperv = null),
    zero real check (typeof(zero) = 'real' or zero = null),
    routeto text check (typeof(routeto) = 'text' or routeto = null),
    rted real check (typeof(rted) = 'real' or rted = null),
    method text check (typeof(method) = 'text' or method = null),
    maxrate real check (typeof(maxrate) = 'real' or maxrate = null),
    minrate real check (typeof(minrate) = 'real' or minrate = null),
    decay real check (typeof(decay) = 'real' or decay = null),
    drytime real check (typeof(drytime) = 'real' or drytime = null),
    maxinfl real check (typeof(maxinfl) = 'real' or maxinfl = null),
    suction real check (typeof(suction) = 'real' or suction = null),
    conduct real check (typeof(conduct) = 'real' or conduct = null),
    initdef real check (typeof(initdef) = 'real' or initdef = null),
    curveno real check (typeof(curveno) = 'real' or curveno = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE outlet (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id)='integer' or sector_id= null),
    scenario_id integer check (typeof(scenario_id)='integer' or scenario_id= null),
    descript text check (typeof(descript)='text' or descript= null),
    node1 text check (typeof(node1)='text' or node1= null),
    node2 text check (typeof(node2)='text' or node2= null),
    flap text check (typeof(flap)='text' or flap= null),
    outlet_type text check (typeof(outlet_type)='text' or outlet_type= null),
    cd1 real check (typeof(cd1)='real' or cd1= null),
    cd2 real check (typeof(cd2)='real' or cd2= null),
    curve_id real check (typeof(curve_id)='real' or curve_id= null),
    annotation real check (typeof(annotation)='real' or annotation= null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE orifice (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node1 text check (typeof(node1) = 'text' or node1 = null),
    node2 text check (typeof(node2) = 'text' or node2 = null),
    ori_type text check (typeof(ori_type) = 'text' or ori_type = null),
    shape real check (typeof(shape) = 'real' or shape = null),
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null),
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    cd1 real check (typeof(cd1) = 'real' or cd1 = null),
    flap text check (typeof(flap) = 'text' or flap = null),
    close_time datetime check (typeof(close_time) = 'datetime' or close_time = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE weir (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node1 text check (typeof(node1) = 'text' or node1 = null),
    node2 text check (typeof(node2) = 'text' or node2 = null),
    weir_type text check (typeof(weir_type) = 'text' or weir_type = null),
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null),
    geom3 real check (typeof(geom3) = 'real' or geom3 = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    cd2 real check (typeof(cd2) = 'real' or cd2 = null),
    flap boolean check (typeof(flap) = 'boolean' or flap = null),
    ec integer check (typeof(ec) = 'integer' or ec = null),
    surcharge text check (typeof(surcharge) = 'text' or surcharge = null),
    road_width real check (typeof(road_width) = 'real' or road_width = null),
    road_surf real check (typeof(road_surf) = 'real' or road_surf = null),
    curve_id real check (typeof(curve_id) = 'real' or curve_id = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE pump (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript  check (typeof(descript) = '' or descript = null),
    node1 text check (typeof(node1) = 'text' or node1 = null),
    node2 text check (typeof(node2) = 'text' or node2 = null),
    curve_id text check (typeof( curve_id) = 'text' or  curve_id = null),
    state text check (typeof(state) = 'text' or state = null),
    startup rea check (typeof(startup) = 'rea' or startup = null),
    shutoff real check (typeof(shutoff) = 'real' or shutoff = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE outfall (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    gate text check (typeof(gate) = 'text' or gate = null),
    routeto text check (typeof(routeto) = 'text' or routeto = null),
    outfall_type text check (typeof(outfall_type) = 'text' or outfall_type = null),
    stage real check (typeof(stage) = 'real' or stage = null),
    curve_id text check (typeof(curve_id) = 'text' or curve_id = null),
    timeser_id text check (typeof(timeser_id) = 'text' or timeser_id = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE divider (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    node_id text check (typeof(node_id) = 'text' or node_id = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    apond real check (typeof(apond) = 'real' or apond = null),
    divider_type text check (typeof(divider_type) = 'text' or divider_type = null),
    qmin real check (typeof(qmin) = 'real' or qmin = null),
    curve_id text check (typeof(curve_id) = 'text' or curve_id = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    annotation real check (typeof(annotation) = 'real' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE storage (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    storage_type text check (typeof(storage_type) = 'text' or storage_type = null),
    curve_id text check (typeof(curve_id) = 'text' or curve_id = null),
    a1 real check (typeof(a1) = 'real' or a1 = null),
    a2 real check (typeof(a2) = 'real' or a2 = null),
    a0 real check (typeof(a0) = 'real' or a0 = null),
    fevap real check (typeof(fevap) = 'real' or fevap = null),
    psi real check(typeof(psi) = 'real' or psi = null),
    ksat real check (typeof(ksat) = 'real' or ksat = null),
    imd real check (typeof(imd) = 'real' or imd = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE junction (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    sector_id integer check (typeof(sector_id) = 'integer' or sector_id = null),
    scenario_id integer check (typeof(scenario_id) = 'integer' or scenario_id = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    apond real check (typeof(apond) = 'real' or apond = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);