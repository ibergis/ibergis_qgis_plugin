/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


-- --------------
-- NO-GEOM TABLES
-----------------

CREATE TABLE config_param_user (
    parameter text primary key,  
    value text CHECK (typeof(value)='text' OR value=NULL),
    isconflictive boolean check (isconflictive in (0, 1) or isconflictive is null)
);

create table config_csv (
    id integer primary key,
    alias text check (typeof(alias) = 'text' or alias = null),
    descript text check (typeof(descript)='text' or descript = null),
    functionname text check (typeof(functionname)='text' or functionname=null),
    active boolean check (typeof(active) in (0, 1, null)),
    orderby integer check (typeof(orderby) = 'integer' or orderby = null),
    addparam text check (typeof(addparam) = 'text' or addparam=null)
);

create table config_typevalue (
    rowid integer primary key,
    typevalue text check (typeof(typevalue) = 'text') not null,
    id text check (typeof(id) = 'text' or id = null),
    idval text check (typeof(idval) = 'text' or idval = null),
    addparam text check (typeof(addparam) = 'text' or addparam = null)
);

-- ---------
-- SELECTORS
-- ---------

CREATE TABLE selector_scenario (
    scenario_id integer primary key
);


-- --------
-- CATALOGS
-- --------

CREATE TABLE cat_bscenario (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    name text check (typeof(name)='text' OR name=NULL),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT  1
);

CREATE TABLE cat_file (
    id integer primary key,
    name text check (typeof(name)='text' OR name=NULL),
    file_name text null,
    content text null
);

CREATE TABLE cat_landuses (
	id integer primary key,
	idval text unique check (typeof(idval)='text') NOT NULL,
    descript text check (typeof(descript)='text' or typeof(descript)=null),
	manning real check (typeof(manning)='real' or typeof(manning)=null),
    sweepint real check (typeof(sweepint) = 'real' or sweepint = null),
    availab real check (typeof(availab) = 'real' or availab = null),
    lastsweep real check (typeof(lastsweep) = 'real' or lastsweep = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT  1
);

CREATE TABLE cat_grate (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    length real check (typeof(length) = 'real' or length = null) DEFAULT 0.00,
    width real check (typeof(width) = 'real' or width = null) DEFAULT 0.00,
    a_param real check (typeof(a_param) = 'real' or a_param = null) DEFAULT 0.00,
    b_param real check (typeof(b_param) = 'real' or b_param = null) DEFAULT 0.00,
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT  1
);

CREATE TABLE cat_arc (
    id integer primary key,
    idval text unique check (typeof(idval) = 'text') NOT NULL,
    shape text check (typeof(shape) = 'text' and shape in ('ARCH', 'BASKETHANDLE', 'CIRCULAR', 'CUSTOM', 'DUMMY', 'EGG', 'FILLED_CIRCULAR', 'FORCE_MAIN', 'HORIZ_ELLIPSE', 'HORSESHOE', 'IRREGULAR', 'MODBASKETHANDLE', 'PARABOLIC', 'POWER', 'RECT_CLOSED', 'RECT_OPEN', 'RECT_ROUND', 'RECT_TRIANGULAR', 'SEMICIRCULAR', 'SEMIELLIPTICAL', 'TRAPEZOIDAL', 'TRIANGULAR', 'VERT_ELLIPSE', 'VIRTUAL')) NOT NULL,
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null),
    geom3 real check (typeof(geom3) = 'real' or geom3 = null),
    geom4 real check (typeof(geom4) = 'real' or geom4 = null),
    curve_id text check (typeof(curve_id) = 'text' or curve_id=null),
    descript text check (typeof(descript) = 'text' or descript = null),
    z1 real check (typeof(z1) = 'real' or z1 = null),
    z2 real check (typeof(z2) = 'real' or z2 = null),
    width real check (typeof(width) = 'real' or width = null),
    area real check (typeof(area) = 'real' or area = null),
    estimated_depth real check (typeof(estimated_depth) = 'real' or estimated_depth = null),
    bulk real check (typeof(bulk) = 'real' or bulk = null),
    arc_type text check (typeof(arc_type) = 'text' or arc_type = null),
    active boolean check (typeof(active) in (0, 1, null)) default 1
);

CREATE TABLE cat_transects (
    id integer primary key,
    idval text unique check (typeof(idval) = 'text') NOT NULL,
    "text" text check (typeof("text" = 'text') or "text" = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);

CREATE TABLE cat_curve (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    curve_type text check (typeof(curve_type) in ('text', null) and curve_type in ('CONTROL', 'DIVERSION', 'PUMP1', 'PUMP2', 'PUMP3', 'PUMP4', 'RATING', 'SHAPE', 'STORAGE', 'TIDAL')),
    descript text check (typeof(descript)='text' or typeof(descript)=null),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT  1
);

CREATE TABLE cat_curve_value (
    id integer primary key,
    idval integer NOT NULL,
    xcoord real CHECK (typeof(xcoord)='real') NOT NULL,
    ycoord real CHECK (typeof(ycoord)='real') NOT NULL,
    FOREIGN KEY (idval) references cat_curve (id) on update cascade
);

CREATE TABLE cat_timeseries (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    timser_type text check (typeof(timser_type) in ('text', null) and timser_type in ('EVAPORATION', 'INFLOW_HYDROGRAPH', 'INFLOW_POLLUTOGRAPH', 'ORIFICE', 'OTHER', 'RAINFALL', 'TEMPERATURE')),
    times_type text CHECK (typeof(times_type) in ('text', null) and times_type in ('ABSOLUTE', 'FILE', 'RELATIVE')),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    fname text check (typeof(fname)='text' or fname = null),
    "log" text check (typeof("log")='text' or "log" = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT  1
);

CREATE TABLE cat_timeseries_value (
    id integer primary key,
    idval integer NOT NULL,
    date datetime CHECK (typeof(date)='datetime' OR date=NULL),
    time datetime CHECK (typeof(time)='datetime' OR time=NULL),
    value real CHECK (typeof(value)='real' OR value=NULL),
    FOREIGN KEY (idval) references cat_timeseries(id) on update cascade
);

CREATE TABLE cat_pattern (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    pattern_type text check (typeof(pattern_type) in ('text', null) and pattern_type in ('DAILY', 'HOURLY', 'MONTHLY', 'WEEKEND')),
    descript text check (typeof(descript) = 'text' or descript = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL)) DEFAULT 1
);

CREATE TABLE cat_pattern_value (
    id integer primary key,
    idval integer NOT NULL,
    timestep datetime CHECK (typeof(timestep)='datetime' OR timestep=NULL),
    value real CHECK (typeof(value)='real' OR value=NULL),
    FOREIGN KEY (idval) references cat_pattern(id) on update cascade
);

CREATE TABLE cat_controls (
    id integer primary key,
    "text" text check (typeof("text" = 'text') or "text" = null),
    active boolean CHECK (typeof(active) IN (0,1,NULL))
);
-- -----------
-- GEOM TABLES
-- -----------

CREATE TABLE ground (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    cellsize real CHECK (typeof(cellsize)='real') NOT NULL DEFAULT 1.0,
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    source_fid integer check (typeof(source_fid) = 'integer' or source_fid = null),
    geom geometry
);

CREATE TABLE ground_roughness (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    landuse integer CHECK (typeof(landuse)='integer' OR landuse=NULL),
    custom_roughness real CHECK (typeof(custom_roughness)='real' OR custom_roughness=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
);

CREATE TABLE ground_losses (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    method_id text check (typeof(method_id) in ('text', null) and method_id in ('LINEAL,', 'SCS', 'SCSC', 'HORTON', 'GREENAMPT', 'NONE')),
    lin_ia real CHECK (typeof(lin_ia)='real' OR lin_ia=NULL),
    lin_fi real CHECK (typeof(lin_fi)='real' OR lin_fi=NULL),
    scs_cn real CHECK (typeof(scs_cn)='real' OR scs_cn=NULL),
    hort_f0 real CHECK (typeof(hort_f0)='real' OR hort_f0=NULL),
    hort_fc real CHECK (typeof(hort_fc)='real' OR hort_fc=NULL),
    ga_suction real CHECK (typeof(ga_suction)='real' OR ga_suction=NULL),
    ga_porosity real CHECK (typeof(ga_porosity)='real' OR ga_porosity=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
);

CREATE TABLE roof (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    cellsize real CHECK (typeof(cellsize)='real') NOT NULL DEFAULT 1.0,
    elev real CHECK (typeof(elev)='real' OR elev = NULL),
    slope real CHECK (typeof(slope)='real' OR slope=NULL),
    width real CHECK (typeof(width)='real' OR width=NULL),
    roughness real CHECK (typeof(roughness)='real' OR roughness=NULL),
    isconnected integer CHECK (typeof(isconnected) in ('integer', NULL) AND isconnected IN (1, 2, 3)),
    outlet_type text CHECK (typeof(outlet_type)='text' OR outlet_type=NULL),
    outlet_id integer CHECK (typeof(outlet_id)='integer' OR outlet_id=NULL),
    outlet_vol real CHECK (typeof(outlet_vol) = 'real' OR outlet_vol=NULL),
    street_vol real CHECK (typeof(street_vol) = 'real' OR street_vol=NULL),
    infiltr_vol real CHECK (typeof(infiltr_vol) = 'real' OR infiltr_vol=NULL),
    totalvol real CHECK (typeof(totalvol)='real' OR totalvol=NULL),
    inletvol real CHECK (typeof(inletvol)='real' OR inletvol=NULL),
    lossvol real CHECK (typeof(lossvol)='real' OR lossvol=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (outlet_id) REFERENCES inp_outlet(fid) on update cascade
);

CREATE TABLE mesh_tin (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    roughness_id integer CHECK (typeof(roughness_id) in ('integer', not null)),
    custom_roughness real CHECK (typeof(custom_roughness)='real' OR custom_roughness = NULL),
    losses_id integer CHECK (typeof(losses_id)='integer' OR losses_id=NULL),
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
    geom geometry,
    FOREIGN KEY (roughness_id) references ground_losses(fid) on update cascade
);

CREATE TABLE mesh_roof (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    roughness_id integer CHECK (typeof(roughness_id) in ('integer', not null)),
    custom_roughness real CHECK (typeof(custom_roughness)='real' OR custom_roughness = NULL),
    losses_id integer CHECK (typeof(losses_id)='integer' OR losses_id=NULL),
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
    geom geometry,
    FOREIGN KEY (roughness_id) references ground_losses(fid) on update cascade,
    FOREIGN KEY (roof_id) REFERENCES roof(fid) on update cascade
);

CREATE TABLE mesh_anchor_points (
    fid integer PRIMARY KEY,
    geom geometry
);

CREATE TABLE mesh_anchor_lines (
    fid integer PRIMARY KEY,
    geom geometry
);

CREATE TABLE link (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    feature_type text check (typeof(feature_type) = 'text' or feature_type = null),
    feature_id text check (typeof(feature_id) = 'text' or feature_id = null),
    exit_type text check (typeof(exit_type) = 'text' or exit_type = null),
    exit_id text check (typeof(exit_id) = 'text' or exit_id = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
);

CREATE TABLE gully (
    fid integer primary key,
	arc_id text unique,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    outlet_type text check (typeof(outlet_type) in ('text', null) and outlet_type in ('SINK', 'TO NETWORK')),
    top_elev real check (typeof(top_elev) = 'real' or top_elev = null),
    custom_top_elev real check (typeof(custom_top_elev) = 'real' or custom_top_elev = null),
    gratecat_id integer check (typeof(gratecat_id) = 'integer' or gratecat_id = null),
    custom_width real check (typeof(custom_width) = 'real' or custom_width = null),
    custom_length real check (typeof(custom_length) = 'real' or custom_length = null),
    method text check (typeof(method) in ('text', null) and method in ('UPC', 'W_O')),
    weir_cd real check (typeof(weir_cd) = 'real' or weir_cd = null),
    orifice_cd real check (typeof(orifice_cd) = 'real' or orifice_cd = null),
    custom_a_param real check (typeof(custom_a_param) = 'real' or custom_a_param = null),
    custom_b_param real check (typeof(custom_b_param) = 'real' or custom_b_param = null),
    efficiency real check (typeof(efficiency) = 'real' or efficiency = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (gratecat_id) references cat_grate (id) on update cascade
);


-- ----------
-- INP TABLES
-- ----------

CREATE TABLE inp_raingage (
    fid integer PRIMARY KEY,
    code text check (typeof(code) = 'text' or code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    rain_type boolean CHECK (typeof(rain_type) IN (0,1,NULL)),
    form_type text check (typeof(form_type) = 'text' and form_type in ('CUMULATIVE', 'INTENSITY', 'VOLUME')),
    data_source text check (typeof(data_source) in ('text', null) and data_source in ('FILE', 'TIMESERIES')),
    timeseries_id integer CHECK (typeof(timeseries_id)='integer' OR timeseries_id=NULL),
    intvl text check (typeof(intvl) = 'text' or intvl = null),
    scf real check (typeof(scf) = 'real' or scf = null),
    fname text check (typeof(fname) = 'text' or fname = null),
    sta text check (typeof(sta) = 'text' or sta = null),
    units text check (typeof(units) = 'text' or units = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (timeseries_id) references cat_timeseries (id) on update cascade
);

CREATE TABLE inp_conduit (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    arccat_id integer check (typeof(arccat_id) = 'integer' or arccat_id = null),
    matcat_id text check (typeof(matcat_id)='text' or matcat_id=null),
    custom_length real check (typeof(custom_length) = 'real' or custom_length = null),
    custom_roughness real check (typeof(custom_roughness) = 'real' or custom_roughness = null),
    shape text check (typeof(shape) = 'text' and shape in ('ARCH', 'BASKETHANDLE', 'CIRCULAR', 'CUSTOM', 'DUMMY', 'EGG', 'FILLED_CIRCULAR', 'FORCE_MAIN', 'HORIZ_ELLIPSE', 'HORSESHOE', 'IRREGULAR', 'MODBASKETHANDLE', 'PARABOLIC', 'POWER', 'RECT_CLOSED', 'RECT_OPEN', 'RECT_ROUND', 'RECT_TRIANGULAR', 'SEMICIRCULAR', 'SEMIELLIPTICAL', 'TRAPEZOIDAL', 'TRIANGULAR', 'VERT_ELLIPSE', 'VIRTUAL')) NOT NULL,
    shape_trnsct text check (typeof(shape_trnsct) = 'text' or shape_trnsct = null),
    z1 real check (typeof(z1) = 'real' or z1 = null),
    custom_z1 real check (typeof(custom_z1) = 'real' or custom_z1 = null),
    z2 real check (typeof(z2) = 'real' or z2 = null),
    custom_z2 real check (typeof(custom_z2) = 'real' or custom_z2 = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    barrels real check (typeof(barrels) = 'real' or barrels = null),
    culvert text check (typeof(culvert) = 'text' or culvert = null),
    kentry real check (typeof(kentry) = 'real' or kentry = null),
    kexit real check (typeof(kexit) = 'real' or kexit = null),
    kavg real check (typeof(kavg) = 'real' or kavg = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    seepage real check (typeof(seepage) = 'real' or seepage = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (arccat_id) references cat_arc(id) on update cascade
);

CREATE TABLE inp_outlet (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript)='text' or descript= null),
    node_1 text check (typeof(node_1)='text' or node_1= null),
    node_2 text check (typeof(node_2)='text' or node_2= null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    outlet_type text check (typeof(outlet_type) in ('text', null) and outlet_type in ('FUNCTIONAL/DEPTH', 'FUNCTIONAL/HEAD', 'TABULAR/DEPTH', 'TABULAR/HEAD')),
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    cd1 real check (typeof(cd1)='real' or cd1= null),
    cd2 real check (typeof(cd2)='real' or cd2= null),
    curve_id integer check (typeof(curve_id)='integer' or curve_id= null),
    annotation real check (typeof(annotation)='real' or annotation= null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve (id) on update cascade
);

CREATE TABLE inp_subcatchment ( 
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    rg_id integer check (typeof(rg_id) = 'integer' or rg_id = null),
    outlet_id integer check (typeof(outlet_id) = 'integer' or outlet_id = null),
    area real check (typeof(area) = 'real' or area = null),
    imperv real check (typeof(imperv) = 'real' or imperv = null),
    width real check (typeof(width) = 'real' or width = null),
    slope real check (typeof(slope) = 'real' or slope = null),
    clength real check (typeof(clength) = 'real' or clength = null),
    snow_id text check (typeof(snow_id) in ('text', null) and snow_id in ('IMPERVIOUS', 'PERVIOUS', 'PLOWABLE', 'REMOVAL')),
    nimp real check (typeof(nimp) = 'real' or nimp = null) DEFAULT 0.01,
    nperv real check (typeof(nperv) = 'real' or nperv = null) DEFAULT 0.01,
    simp real check (typeof(simp) = 'real' or simp = null) DEFAULT 0.05,
    sperv real check (typeof(sperv) = 'real' or sperv = null) DEFAULT 0.05,
    zero real check (typeof(zero) = 'real' or zero = null) DEFAULT 25,
    routeto text check (typeof(routeto) in ('text', null) and routeto in ('IMPERVIOUS', 'OUTLET', 'PERVIOUS')),
    rted real check (typeof(rted) = 'real' or rted = null) DEFAULT 100,
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
    geom geometry,
    FOREIGN KEY (rg_id) references inp_raingage (fid) on update cascade,
    FOREIGN KEY (outlet_id) references inp_outlet (fid) on update cascade
);

CREATE TABLE inp_orifice (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    ori_type text check (typeof(ori_type) in ('text', null) and ori_type in ('BOTTOM', 'SIDE')),
    shape text check (typeof(shape) in ('text', null) and shape in ('CIRCULAR', 'RECT_CLOSED')) NOT NULL,
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null)  DEFAULT 0.00,
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    cd1 real check (typeof(cd1) = 'real' or cd1 = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    close_time real check (typeof(close_time) = 'real' or close_time = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
);

CREATE TABLE inp_weir (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    weir_type text check (typeof(weir_type) in ('text', null) and weir_type in ('ROADWAY', 'SIDEFLOW', 'TRANSVERSE', 'TRAPEZOIDAL', 'V-NOTCH')),
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null)  DEFAULT 0.00,
    geom3 real check (typeof(geom3) = 'real' or geom3 = null)  DEFAULT 0.00,
    geom4 real check (typeof(geom4) = 'real' or geom4 = null),
    shape text check (typeof(shape) in ('text', null) and shape in ('CIRCULAR', 'RECT_CLOSED')) NOT NULL,
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    cd2 real check (typeof(cd2) = 'real' or cd2 = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    ec integer check (typeof(ec) = 'integer' or ec = null),
    surcharge text check (typeof(surcharge) = 'text' or surcharge = null),
    road_width real check (typeof(road_width) = 'real' or road_width = null),
    road_surf text check (typeof(road_surf) in ('text', null) and road_surf in ('PAVED', 'GRAVEL')),
    curve_id integer check (typeof(curve_id) = 'integer' or curve_id = null),
    crest_heigh real check (typeof(crest_heigh)='real' or crest_heigh = null),
    end_coeff real check (typeof(end_coeff)='real' or end_coeff = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve(id) on update cascade
);

CREATE TABLE inp_pump (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    curve_id integer check (typeof( curve_id) = 'integer' or  curve_id = null),
    state text check (typeof(state) in ('text', null) and state in ('OFF', 'ON')),
    startup real check (typeof(startup) = 'real' or startup = null),
    shutoff real check (typeof(shutoff) = 'real' or shutoff = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve(id) on update cascade
);

CREATE TABLE inp_outfall (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    gate text check (typeof(gate) in ('text', null) and gate in ('YES', 'NO')),
    routeto text check (typeof(routeto) in ('text', null) and routeto in ('IMPERVIOUS', 'OUTLET', 'PERVIOUS')),
    outfall_type text check (typeof(outfall_type) in ('text', null) and outfall_type in ('FIXED', 'FREE', 'NORMAL', 'TIDAL', 'TIMESERIES')),
    stage real check (typeof(stage) = 'real' or stage = null),
    curve_id integer check (typeof(curve_id) = 'integer' or curve_id = null),
    timeser_id integer check (typeof(timeser_id) = 'integer' or timeser_id = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve(id) on update cascade,
    FOREIGN KEY (timeser_id) references cat_timeseries(id)
);

CREATE TABLE inp_divider (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    apond real check (typeof(apond) = 'real' or apond = null),
    divert_link text check(typeof(divert_link='text' or divert_link=null)),
    divider_type text check (typeof(divider_type) IN ('text', null) and divider_type in ('CUTOFF', 'OVERFLOW', 'TABULAR', 'WEIR')),
    qmin real check (typeof(qmin) = 'real' or qmin = null),
    curve_id integer check (typeof(curve_id) = 'integer' or curve_id = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    annotation real check (typeof(annotation) = 'real' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve(id) on update cascade
);

CREATE TABLE inp_storage (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    storage_type text check (typeof(storage_type) in ('text', null) and storage_type in ('FUNCTIONAL', 'TABULAR')),
    curve_id integer check (typeof(curve_id) = 'integer' or curve_id = null),
    a1 real check (typeof(a1) = 'real' or a1 = null),
    a2 real check (typeof(a2) = 'real' or a2 = null),
    a0 real check (typeof(a0) = 'real' or a0 = null),
    fevap real check (typeof(fevap) = 'real' or fevap = null),
    psi real check (typeof(psi) = 'real' or psi = null),
    ksat real check (typeof(ksat) = 'real' or ksat = null),
    imd real check (typeof(imd) = 'real' or imd = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve_id) references cat_curve(id) on update cascade
);

CREATE TABLE inp_junction (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    custom_elev real check (typeof(custom_elev) = 'real' or custom_elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    custom_ymax real check (typeof(custom_ymax) = 'real' or custom_ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    apond real check (typeof(apond) = 'real' or apond = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
);

create table inp_files (
    id integer primary key,
    idval text unique,
    actio_type text check (typeof(actio_type) in ('text', null) and actio_type in ('SAVE', 'USE')),
    file_type text check (typeof(file_type) in ('text', null) and file_type in ('HOTSTART', 'INFLOWS', 'OUTFLOWS', 'RAINFALL', 'RDII', 'RUNOFF')),
    fname text check (typeof(fname) = 'text' or fname = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    active boolean check (typeof(active) in (0, 1, null))
);

create table inp_dwf (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    avg_value real check (typeof(avg_value)='real' or avg_value = null),
    pat1 integer check (typeof(pat1) = 'integer' or pat1 = null),
    pat2 integer check (typeof(pat1) = 'integer' or pat2 = null),
    pat3 integer check (typeof(pat1) = 'integer' or pat3 = null),
    pat4 integer check (typeof(pat1) = 'integer' or pat4 = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (pat1) REFERENCES cat_pattern(id) on update cascade,
    FOREIGN KEY (pat2) REFERENCES cat_pattern(id) on update cascade,
    FOREIGN KEY (pat3) REFERENCES cat_pattern(id) on update cascade,
    FOREIGN KEY (pat4) REFERENCES cat_pattern(id) on update cascade
);

create table inp_inflow (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    timeser_id text check (typeof(timeser_id) = 'text' or timeser_id = null),
    format text check (typeof(format) = 'text' or format =null) default 'FLOW',
    mfactor real check (typeof(mfactor) = 'real' or mfactor=null) default 1,
    sfactor real check (typeof(sfactor)='real' or sfactor=null) default 1,
    ufactor real check (typeof(ufactor)='real' or ufactor=null) default 1,
    base real check (typeof(base)='real' or base=null) default 0,
    pattern_id integer check (typeof(pattern_id) = 'integer' or pattern_id=null),
    type text check(typeof(type)='text' or type=null),
    geom geometry,
    FOREIGN KEY (pattern_id) REFERENCES cat_pattern(id) on update cascade
);

create table boundary_conditions (
    fid integer primary key,
    code text check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    bscenario_id integer check (typeof(bscenario_id)='integer' or bscenario_id=null),
    boundary_type text check (typeof(boundary_type) = 'text' or boundary_type=null),
    mesh_id text check (typeof(mesh_id) = 'text' or mesh_id=null),
    tin_id integer null,
    edge_id text check (typeof(edge_id) = 'text' or edge_id=null),
    geom geometry,
    FOREIGN KEY (bscenario_id) REFERENCES cat_bscenario(id) on update cascade
);


-- ----------
-- RPT_TABLES
-- ----------

CREATE TABLE rpt_arc (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id =null),
    resultdate text check (typeof(resultdate) = 'text' or resultdate = null),
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    flow real check (typeof(flow) = 'real' or flow = null),
    velocity real check (typeof(velocity) = 'real' or velocity = null),
    fullpercent real check (typeof(fullpercent) = 'real' or fullpercent = null)
);

CREATE TABLE rpt_arcflow_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    arc_type text check (typeof(arc_type) = 'text' or arc_type = null),
    max_flow real check (typeof(max_flow) = 'real' or max_flow = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    max_veloc real check (typeof(max_veloc) = 'real' or max_veloc = null),
    mfull_flow real check (typeof(mfull_flow) = 'real' or mfull_flow = null),
    mfull_dept real check (typeof(mfull_dept) = 'real' or mfull_dept = null),
    max_shear real check (typeof(max_shear) = 'real' or max_shear = null),
    max_hr real check (typeof(max_hr) = 'real' or max_hr = null),
    max_slope real check (typeof(max_slope) = 'real' or max_slope = null),
    day_max text check (typeof(day_max) = 'text' or day_max = null),
    time_max text check (typeof(time_max) = 'text 'or time_max = null),
    min_shear real check (typeof(min_shear) = 'real' or min_shear = null),
    day_min text check (typeof(day_min) = 'text' or day_min = null),
    time_min text check (typeof(time_min) = 'text' or time_min = null)
);

CREATE TABLE rpt_arcpolload_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null)
);

CREATE TABLE rpt_arcpollutant_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null),
    value real check (typeof(value) = 'real' or value = null)
);

CREATE TABLE rpt_cat_result (
    result_id integer primary key,
    result text check (typeof(result) = 'text' or result = null),
    flow_units text check (typeof(flow_units) = 'text' or flow_units = null),
    rain_runof text check (typeof(rain_runof) = 'text' or rain_runof = null),
    snowmelt text check (typeof(snowmelt) = 'text' or snowmelt = null),
    groundw text check (typeof(groundw) = 'text' or groundw = null),
    flow_rout text check (typeof(flow_rout) = 'text' or flow_rout = null),
    pond_all text check (typeof(pond_all) = 'text' or pond_all = null),
    water_q text check (typeof(water_q) = 'text' or water_q = null),
    infil_m text check (typeof(infil_m) = 'text' or infil_m = null),
    flowrout_m text check (typeof(flowrout_m) = 'text' or flowrout_m = null),
    start_date text check (typeof(start_date) = 'text' or start_date = null),
    end_date text check (typeof(end_date) = 'text' or end_date = null),
    dry_days real check (typeof(dry_days) = 'real' or dry_days = null),
    rep_tstep text check (typeof(rep_tstep) = 'text' or rep_tstep = null),
    wet_tstep text check (typeof(wet_tstep) = 'text' or wet_tstep = null),
    dry_tstep text check (typeof(dry_tstep) = 'text' or dry_tstep = null),
    rout_tstep text check (typeof(rout_tstep) = 'text' or rout_tstep = null),
    var_time_step text check (typeof(var_time_step) = 'text' or var_time_step = null),
    max_trials real check (typeof(max_trials) = 'real' or max_trials = null),
    head_tolerance text check (typeof(head_tolerance) = 'text' or head_tolerance = null),
    exec_date timestamp check (typeof(exec_date) = 'timestamp' or exec_date = null),
    cur_user text check (typeof(cur_user) = 'text' or cur_user = null),
    inp_options json text check (typeof(inp_options) = 'json' or inp_options = null),
    rpt_stats json text check (typeof(rpt_stats) = 'json' or rpt_stats = null),
    export_options text json check (typeof(export_options) = 'text' or export_options = null),
    network_stats json check (typeof(network_stats) = 'json' or network_stats = null),
    status int2 text check (typeof(status) = 'int2' or status = null)
);

CREATE TABLE rpt_condsurcharge_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    both_ends real check (typeof(both_ends) = 'real' or both_ends = null),
    upstream real check (typeof(upstream) = 'real' or upstream = null),
    dnstream real check (typeof(dnstream) = 'real' or dnstream = null),
    hour_nflow real check (typeof(hour_nflow) = 'real' or hour_nflow = null),
    hour_limit real check (typeof(hour_limit) = 'real' or hour_limit = null)
);

CREATE TABLE rpt_continuity_errors (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_control_actions_taken (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_critical_elements (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_flowclass_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    length real check (typeof(length) = 'real' or length = null),
    dry real check (typeof(dry) = 'real' or dry = null),
    up_dry real check (typeof(up_dry) = 'real' or up_dry = null),
    down_dry real check (typeof(down_dry) = 'real' or down_dry = null),
    sub_crit real check (typeof(sub_crit) = 'real' or sub_crit = null),
    sub_crit_1 real check (typeof(sub_crit_1) = 'real' or sub_crit_1 = null),
    up_crit real check (typeof(up_crit) = 'real' or up_crit = null),
    down_crit real check (typeof(down_crit) = 'real' or down_crit = null),
    froud_numb real check (typeof(froud_numb) = 'real' or froud_numb = null),
    flow_chang real check (typeof(flow_chang) = 'real' or flow_chang = null)
);

CREATE TABLE rpt_flowrouting_cont (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    dryw_inf real check (typeof(dryw_inf) = 'real' or dryw_inf = null),
    wetw_inf real check (typeof(wetw_inf) = 'real' or wetw_inf = null),
    ground_inf real check (typeof(ground_inf) = 'real' or ground_inf = null),
    rdii_inf real check (typeof(rdii_inf) = 'real' or rdii_inf = null),
    ext_inf real check (typeof(ext_inf) = 'real' or ext_inf = null),
    ext_out real check (typeof(ext_out) = 'real' or ext_out = null),
    int_out real check (typeof(int_out) = 'real' or int_out = null),
    stor_loss real check (typeof(stor_loss) = 'real' or stor_loss = null),
    initst_vol real check (typeof(initst_vol) = 'real' or initst_vol = null),
    finst_vol real check (typeof(finst_vol) = 'real' or finst_vol = null),
    cont_error real check (typeof(cont_error) = 'real' or cont_error = null),
    evap_losses real check (typeof(evap_losses) = 'real' or evap_losses = null),
    seepage_losses real check (typeof(seepage_losses) = 'real' or seepage_losses = null)
);

CREATE TABLE rpt_groundwater_cont (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    init_stor real check (typeof(init_stor) = 'real' or init_stor = null),
    infilt real check (typeof(infilt) = 'real' or infilt = null),
    upzone_et real check (typeof(upzone_et) = 'real' or upzone_et = null),
    lowzone_et real check (typeof(lowzone_et) = 'real' or lowzone_et = null),
    deep_perc real check (typeof(deep_perc) = 'real' or deep_perc = null),
    groundw_fl real check (typeof(groundw_fl) = 'real' or groundw_fl = null),
    final_stor real check (typeof(final_stor) = 'real' or final_stor = null),
    cont_error real check (typeof(cont_error) = 'real' or cont_error = null)
);

CREATE TABLE rpt_high_conterrors (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_high_flowinest_ind (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_instability_index (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_lidperformance_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    subc_id text check (typeof(subc_id) = 'text' or subc_id = null),
    lidco_id text check (typeof(lidco_id) = 'text' or lidco_id = null),
    tot_inflow real check (typeof(tot_inflow) = 'real' or tot_inflow = null),
    evap_loss real check (typeof(evap_loss) = 'real' or evap_loss = null),
    infil_loss real check (typeof(infil_loss) = 'real' or infil_loss = null),
    surf_outf real check (typeof(surf_outf) = 'real' or surf_outf = null),
    drain_outf real check (typeof(drain_outf) = 'real' or drain_outf = null),
    init_stor real check (typeof(init_stor) = 'real' or init_stor = null),
    final_stor real check (typeof(final_stor) = 'real' or final_stor = null),
    per_error real check (typeof(per_error) = 'real' or per_error = null)
);

CREATE TABLE rpt_node (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    resultdate text check (typeof(resultdate) = 'text' or resultdate = null),
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    flooding real check (typeof(flooding) = 'real' or flooding = null),
    depth real check (typeof("depth") = 'real' or "depth" = null),
    head real check (typeof(head) = 'real' or head = null),
    inflow real check (typeof(inflow) = 'real' or inflow = null)
);

CREATE TABLE rpt_nodedepth_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    aver_depth real check (typeof(aver_depth) = 'real' or aver_depth = null),
    max_depth real check (typeof(max_depth) = 'real' or max_depth = null),
    max_hgl real check (typeof(max_hgl) = 'real' or max_hgl = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null)
);

CREATE TABLE rpt_nodeflooding_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    hour_flood real check (typeof(hour_flood) = 'real' or hour_flood = null),
    max_rate real check (typeof(max_rate) = 'real' or max_rate = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    tot_flood real check (typeof(tot_flood) = 'real' or tot_flood = null),
    max_ponded real check (typeof(max_ponded) = 'real' or max_ponded = null)
);

CREATE TABLE rpt_nodeinflow_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    max_latinf real check (typeof(max_latinf) = 'real' or max_latinf = null),
    max_totinf real check (typeof(max_totinf) = 'real' or max_totinf = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    latinf_vol real check (typeof(latinf_vol) = 'real' or latinf_vol = null),
    totinf_vol real check (typeof(totinf_vol) = 'real' or totinf_vol = null),
    flow_balance_error real check (typeof(flow_balance_error) = 'real' or flow_balance_error = null),
    other_info text check (typeof(other_info) = 'text' or other_info = null)
);

CREATE TABLE rpt_nodesurcharge_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    hour_surch real check (typeof(hour_surch) = 'real' or hour_surch = null),
    max_height real check (typeof(max_height) = 'real' or max_height = null),
    min_depth real check (typeof(min_depth) = 'real' or min_depth = null)
);

CREATE TABLE rpt_outfallflow_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    flow_freq real check (typeof(flow_freq) = 'real' or flow_freq = null),
    avg_flow real check (typeof(avg_flow) = 'real' or avg_flow = null),
    max_flow real check (typeof(max_flow) = 'real' or max_flow = null),
    total_vol real check (typeof(total_vol) = 'real' or total_vol = null)
);

CREATE TABLE rpt_outfallload_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null),
    value real check (typeof(value) = 'real' or value = null)
);

CREATE TABLE rpt_pumping_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    percent real check (typeof("percent") = 'real' or "percent" = null),
    num_startup integer check (typeof(num_startup) = 'integer' or num_startup = null),
    min_flow real check (typeof(min_flow) = 'real' or min_flow = null),
    avg_flow real check (typeof(avg_flow) = 'real' or avg_flow = null),
    max_flow real check (typeof(max_flow) = 'real' or max_flow = null),
    vol_ltr real check (typeof(vol_ltr) = 'real' or vol_ltr = null),
    powus_kwh real check (typeof(powus_kwh) = 'real' or powus_kwh = null),
    timoff_min real check (typeof(timoff_min) = 'real' or timoff_min = null),
    timoff_max real check (typeof(timoff_max) = 'real' or timoff_max = null)
);

CREATE TABLE rpt_qualrouting_cont (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null),
    dryw_inf real check (typeof(dryw_inf) = 'real' or dryw_inf = null),
    wetw_inf real check (typeof(wetw_inf) = 'real' or wetw_inf = null),
    ground_inf real check (typeof(ground_inf) = 'real' or ground_inf = null),
    rdii_inf real check (typeof(rdii_inf) = 'real' or rdii_inf = null),
    ext_inf real check (typeof(ext_inf) = 'real' or ext_inf = null),
    int_inf real check (typeof(int_inf) = 'real' or int_inf = null),
    ext_out real check (typeof(ext_out) = 'real' or ext_out = null),
    mass_reac real check (typeof(mass_reac) = 'real' or mass_reac = null),
    initst_mas real check (typeof(initst_mas) = 'real' or initst_mas = null),
    finst_mas real check (typeof(finst_mas) = 'real' or finst_mas = null),
    cont_error real check (typeof(cont_error) = 'real' or cont_error = null)
);

CREATE TABLE rpt_rainfall_dep (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    sewer_rain real check (typeof(sewer_rain) = 'real' or sewer_rain = null),
    rdiip_prod real check (typeof(rdiip_prod) = 'real' or rdiip_prod = null),
    rdiir_rat real check (typeof(rdiir_rat) = 'real' or rdiir_rat = null)
);

CREATE TABLE rpt_routing_timestep (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_runoff_qual (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null),
    init_buil real check (typeof(init_buil) = 'real' or init_buil = null),
    surf_buil real check (typeof(surf_buil) = 'real' or surf_buil = null),
    wet_dep real check (typeof(wet_dep) = 'real' or wet_dep = null),
    sweep_re real check (typeof(sweep_re) = 'real' or sweep_re = null),
    infil_loss real check (typeof(infil_loss) = 'real' or infil_loss = null),
    bmp_re real check (typeof(bmp_re) = 'real' or bmp_re = null),
    surf_runof real check (typeof(surf_runof) = 'real' or surf_runof = null),
    rem_buil real check (typeof(rem_buil) = 'real' or rem_buil = null),
    cont_error real check (typeof(cont_error) = 'real' or cont_error = null)
);

CREATE TABLE rpt_runoff_quant (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    initsw_co real check (typeof(initsw_co) = 'real' or initsw_co = null),
    total_prec real check (typeof(total_prec) = 'real' or total_prec = null),
    evap_loss real check (typeof(evap_loss) = 'real' or evap_loss = null),
    infil_loss real check (typeof(infil_loss) = 'real' or infil_loss = null),
    surf_runof real check (typeof(surf_runof) = 'real' or surf_runof = null),
    snow_re real check (typeof(snow_re) = 'real' or snow_re = null),
    finalsw_co real check (typeof(finalsw_co) = 'real' or finalsw_co = null),
    finals_sto real check (typeof(finals_sto) = 'real' or finals_sto = null),
    cont_error real check (typeof(cont_error) = 'real' or cont_error = null),
    initlid_sto real check (typeof(initlid_sto) = 'real' or initlid_sto = null)
);

CREATE TABLE rpt_storagevol_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    aver_vol real check (typeof(aver_vol) = 'real' or aver_vol = null),
    avg_full real check (typeof(avg_full) = 'real' or avg_full = null),
    ei_loss real check (typeof(ei_loss) = 'real' or ei_loss = null),
    max_vol real check (typeof(max_vol) = 'real' or max_vol = null),
    max_full real check (typeof(max_full) = 'real' or max_full = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    max_out real check (typeof(max_out) = 'real' or max_out = null)
);

CREATE TABLE rpt_subcatchment (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    subc_id text check (typeof(subc_id) = 'text' or subc_id = null),
    resultdate text check (typeof(resultdate) = 'text' or resultdate = null),
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    precip real check (typeof(precip) = 'real' or precip = null),
    losses real check (typeof(losses) = 'real' or losses = null),
    runoff real check (typeof(runoff) = 'real' or runoff = null)
);

CREATE TABLE rpt_subcatchrunoff_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    subc_id text check (typeof(subc_id) = 'text' or subc_id = null),
    tot_precip real check (typeof(tot_precip) = 'real' or tot_precip = null),
    tot_runon real check (typeof(tot_runon) = 'real' or tot_runon = null),
    tot_evap real check (typeof(tot_evap) = 'real' or tot_evap = null),
    tot_infil real check (typeof(tot_infil) = 'real' or tot_infil = null),
    tot_runoff real check (typeof(tot_runoff) = 'real' or tot_runoff = null),
    tot_runofl real check (typeof(tot_runofl) = 'real' or tot_runofl = null),
    peak_runof real check (typeof(peak_runof) = 'real' or peak_runof = null),
    runoff_coe real check (typeof(runoff_coe) = 'real' or runoff_coe = null),
    vxmax real check (typeof(vxmax) = 'real' or vxmax = null),
    vymax real check (typeof(vymax) = 'real' or vymax = null),
    "depth" real check (typeof("depth") = 'real' or "depth" = null),
    vel real check (typeof(vel) = 'real' or vel = null),
    vhmax real check (typeof(vhmax) = 'real' or vhmax = null)
);

CREATE TABLE rpt_subcatchwashoff_sum (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    subc_id text check (typeof(subc_id) = 'text' or subc_id = null),
    poll_id text check (typeof(poll_id) = 'text' or poll_id = null),
    value real check (typeof(value) = 'real' or value = null)
);

CREATE TABLE rpt_summary_arc (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    epa_type text check (typeof(epa_type) = 'text' or epa_type = null),
    length real check (typeof(length) = 'real' or length = null),
    slope real check (typeof(slope) = 'real' or slope = null),
    roughness real check (typeof(roughness) = 'real' or roughness = null)
);

CREATE TABLE rpt_summary_crossection (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    shape text check (typeof(shape) = 'text' or shape = null),
    fulldepth real check (typeof(fulldepth) = 'real' or fulldepth = null),
    fullarea real check (typeof(fullarea) = 'real' or fullarea = null),
    hydrad real check (typeof(hydrad) = 'real' or hydrad = null),
    maxwidth real check (typeof(maxwidth) = 'real' or maxwidth = null),
    barrels integer check (typeof(barrels) = 'integer' or barrels = null),
    fullflow real check (typeof(fullflow) = 'real' or fullflow = null)
);

CREATE TABLE rpt_summary_node (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    epa_type text check (typeof(epa_type) = 'text' or epa_type = null),
    elevation real check (typeof(elevation) = 'real' or elevation = null),
    maxdepth real check (typeof(maxdepth) = 'real' or maxdepth = null),
    pondedarea real check (typeof(pondedarea) = 'real' or pondedarea = null),
    externalinf text check (typeof(externalinf) = 'text' or externalinf = null)
);

CREATE TABLE rpt_summary_raingage (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    rg_id text check (typeof(rg_id) = 'text' or rg_id = null),
    data_source text check (typeof(data_source) = 'text' or data_source = null),
    data_type text check (typeof(data_type) = 'text' or data_type = null),
    "interval" text check (typeof("interval") = 'text' or "interval" = null)
);

CREATE TABLE rpt_summary_subcatchment (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    subc_id text check (typeof(subc_id) = 'text' or subc_id = null),
    area real check (typeof(area) = 'real' or area = null),
    width real check (typeof(width) = 'real' or width = null),
    imperv real check (typeof(imperv) = 'real' or imperv = null),
    slope real check (typeof(slope) = 'real' or slope = null),
    rg_id text check (typeof(rg_id) = 'text' or rg_id = null),
    outlet text check (typeof(outlet) = 'text' or outlet = null)
);

CREATE TABLE rpt_timestep_critelem (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE rpt_warning_summary (
    id integer primary key,
    result_id text check (typeof(result_id) = 'text' or result_id = null),
    warning_number text check (typeof(warning_number) = 'text' or warning_number = null),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE selector_rpt_compare (
    result_id integer primary key,
    cur_user text check (typeof(cur_user) = 'text' or cur_user = null)
);

CREATE TABLE selector_rpt_compare_tstep (
    resultdate integer primary key,
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    cur_user text check (typeof(cur_user) = 'text' or cur_user = null)
);

CREATE TABLE selector_rpt_main (
    result_id integer primary key,
    cur_user text check (typeof(cur_user) = 'text' or cur_user = null)
);

CREATE TABLE selector_rpt_main_tstep (
    resultdate integer primary key,
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    cur_user text check (typeof(cur_user) = 'text' or cur_user = null)
);


-- ------------
-- VI_IMPORT_INP
-- -----------
create view if not exists vi_title as select parameter, value from config_param_user where parameter like 'project_%';
create view if not exists vi_files as select fname as Name from inp_files;
create view if not exists vi_options as select parameter as Option, value as Value from config_param_user where parameter like 'inp_options%';

create view if not exists vi_conduits as select code as Name, node_1 as FromNode, node_2 as ToNode, custom_length as Length, custom_roughness as Roughness, z1 as InOffset, z2 as OutOffset, q0 as InitFlow, qmax as MaxFlow, shape as Shape, geom1 as Geom1, geom2 as Geom2, geom3 as Geom3, geom4 as Geom4, barrels as Barrels, culvert as Culvert, shape_trnsct as Shp_Trnsct, kentry as Kentry, kexit as Kexit, kavg as Kavg, flap as FlapGate, seepage as Seepage, annotation as Annotation from inp_conduit;
create view if not exists vi_subcatchments as select subc_id as Name, rg_id as RainGage, outlet_id as Outlet, area as Area, imperv as Imperv, width as Width, slope as Slope, clength as CurbLen, annotation as Annotation, nimp as N_Imperv, nperv as N_Perv, simp as S_Imperv, sperv as S_Perv, zero as PctZero, routeto as RouteTo, rted as PctRouted, curveno as CurveNum, conduct as Conductiv, drytime as DryTime, method as InfMethod, suction as SuctHead, initdef as InitDef, maxrate as MaxRatefrom, minrate as MinRate, decay as Decay, maxinfl as MaxInf from inp_subcatchment;
create view if not exists vi_outlets as select code as Name, node_1 as FromNode, node_2 as ToNode, offsetval as InOffset, outlet_type as RateCurve, cd1 as Qcoeff, cd2 as Qexpon, flap as FlapGate, curve_id as CurveName, annotation as Annotation from inp_outlet;
create view if not exists vi_orifices as select code as Name, node_1 as FromNode, node_2 as ToNode, ori_type as Type, offsetval as InOffset, cd1 as Qcoeff, flap as FlapGate, close_time as CloseTime, annotation as Annotation, shape as Shape, geom1 as Height, geom2 as Width from inp_orifice;
create view if not exists vi_weirs as select code as Name, node_1 as FromNode, node_2 as ToNode, weir_type as Type, offsetval as CrestHight, cd2 as Qcoeff, flap as FlapGate, ec as EndContrac, cd2 as Qcoeff, surcharge as Surcharge, road_width as RoadWidth, road_surf as RoadSurf, curve_id as CoeffCurve, annotation as Annotation, geom1 as Hight, geom3 as Length, geom4 as SideSlope from inp_weir;
create view if not exists vi_pumps as select code as Name, node_1 as FromNode, node_2 as ToNode, curve_id as PumpCurve, state as Status, startup as Startup, shutoff as Shutoff, annotation as Annotation from inp_pump;
create view if not exists vi_outfalls as select code as Name, elev as Elevation, outfall_type as Type, stage as FixedStage, curve_id as Curve_TS, gate as FlapGate, routeto as RouteTo, annotation as Annotation from inp_outfall;
create view if not exists vi_dividers as select code as Name, elev as Elevation, divert_link as DivertLink, divider_type as Type, curve_id as Curve, qmin as WeirMinFlo, qmax as WeirMaxDep, q0 as WeirCoeff, ymax as MaxDepth, y0 as InitDepth, ysur as SurDepth, apond as Aponded, annotation as Annotation from inp_divider;
create view if not exists vi_storage as select code as Name, elev as Elevation, ymax as MaxDepth, y0 as InitDepth, storage_type as Type, curve_id as Curve, a1 as Coeff, a2 as Exponent, a0 as Constant, ysur as SurDepth, fevap as Fevap, psi as Psi, ksat as Ksat, imd as IMD, annotation as Annotation from inp_storage;
create view if not exists vi_junctions as SELECT code as Name, elev as Elevation, ymax as MaxDepth, y0 as InitDepth, ysur as SurDepth, apond as Aponded, annotation as Annotation from inp_junction;
create view if not exists vi_raingages as select code as Name, form_type as Format, intvl as Interval, scf as SCF, data_source as DataSource, timeseries_id as SeriesName, fname as FileName, sta as StationID, units as RainUnits, annotation as Annotation from inp_raingage;

create view if not exists vi_curves as select c.idval as Name, c.curve_type, cv.xcoord as Depth, cv.ycoord as Flow from cat_curve c, cat_curve_value cv;
create view if not exists vi_timeseries as select idval as Name, "date" as "Date", "time" as "Time", value as Value, file as File_Name from cat_timeseries_value;
create view if not exists vi_patterns as select idval as Name, "time" as "Time", value as Factor from cat_pattern_value where active = 1;
create view if not exists vi_landuses as select idval as Name, sweepint as SweepingInterval, availab as SweepingFractionAvailable, lastsweep as LastSwept from cat_landuses;
create view if not exists vi_subareas as select nimp as N_Imperv, nperv as N_Perv, simp as S_Imperv, sperv as S_Perv, zero as PctZero, routeto as RouteTo, rted as PctRouted from inp_subcatchment;
create view if not exists vi_losses as select code as Name, kentry as Kentry, kexit as Kexit, kavg as Kavg, flap as FlapGate, seepage as Seepage from inp_conduit;
create view if not exists vi_dwf as select code as Name, 'FLOW' as Constituent, avg_value as Average_Value, pat1 as Time_Pattern1, pat2 as Time_Pattern2, pat3 as Time_Pattern3, pat4 as Time_Pattern4 from inp_dwf;
create view if not exists vi_infiltration as select method as InfMethod, maxrate as MaxRate, minrate as MinRate, decay as Decay, maxinfl as MaxInf, suction as SuctHead, conduct as Conductiv, initdef as InitDef, curveno as CurveNum, annotation as Annotation from inp_subcatchment;
create view if not exists vi_controls as select "text" from cat_controls;
create view if not exists vi_transects as select "text" from cat_transects;
create view if not exists vi_report as select parameter, value from config_param_user where parameter like '%inp_report_%';
create view if not exists vi_inflows as select code as Name, format as Constituent, base as Baseline, cat_pattern.idval as Baseline_Pattern, timeser_id as Time_Series, mfactor as Units_Factor, sfactor as Scale_Factor, type as Type from inp_inflow join cat_pattern on inp_inflow.pattern_id=cat_pattern.id;
create view if not exists vi_xsections as
    select code as Link, shape as Shape, geom1 as other1, geom2 as other2, 0 as other3, 0 as other4, barrels as other5, null as other6 from inp_conduit where shape ='CUSTOM' union
    select code as Link, shape as Shape, shape_trnsct as other1, 0 as other2, 0 as other3, 0 as other4, barrels as other5, NULL AS other6 from inp_conduit where shape='IRREGULAR'union
    select code as Link, shape as Shape, geom1 as other1, geom2 as other2, geom3 as other3, geom4 as other4, barrels as other5, culvert as other6 from inp_conduit where shape not in ('CUSTOM', 'IRREGULAR') union
    select code as Link, shape as Shape, geom1 as other1, geom2 as other2, null as other3, null as other4, null as other5, null as other6 from inp_orifice union
    select code as Link, shape as Shape, geom1 as other1, geom2 as other2, null as other3, null as other4, null as other5, null as other6 from inp_weir;

CREATE VIEW if not exists v_node as
    select code, geom from inp_storage union
    select code, geom from inp_outfall union
    select code, geom from inp_junction union
    select code, geom from inp_divider;
CREATE VIEW if not exists v_arc as
    select code, geom from inp_outlet union
    select code, geom from inp_weir union
    select code, geom from inp_orifice union
    select code, geom from inp_pump union
    select code, geom from inp_conduit;


create table tables_nogeom (table_name text primary key);
create table tables_geom (table_name text primary key, isgeom text NOT NULL);


create trigger "trigger_tables_nogeom" after insert on "tables_nogeom"
BEGIN 
    select new.table_name from tables_nogeom;

    INSERT INTO gpkg_ogr_contents (table_name, feature_count) 
    VALUES(new.table_name, 0);
    
    insert into gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id)
    values (new.table_name, 'attributes', new.table_name, '', 0, 0, 0, 0, 0, 0);
END;



create trigger trigger_tables_geom after insert on "tables_geom"
BEGIN 
    select new.table_name, new.isgeom from tables_geom;

    INSERT INTO gpkg_ogr_contents (table_name, feature_count) 
    VALUES(new.table_name, 0);
    
    insert into gpkg_contents (table_name, data_type, identifier, description, last_change,  min_x, min_y, max_x, max_y, srs_id)
    values (new.table_name, 'features', new.table_name, '', 0, 0, 0, 0, 0, <SRID_VALUE>);

    insert into gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES(new.table_name, 'geom', new.isgeom, <SRID_VALUE>, 0, 0);

END;