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
    value text CHECK (typeof(value)='text' OR value=NULL)
);

CREATE TABLE sys_message (
	id integer primary key,
	text text CHECK (typeof(text)='text' OR text = NULL)
);

CREATE TABLE config_form_fields (
	formname TEXT NULL CHECK (typeof(formname) = 'text' OR formname IS NULL),
	formtype TEXT NULL CHECK (typeof(formtype) = 'text' OR formtype IS NULL),
	tabname TEXT NULL CHECK (typeof(tabname) = 'text' OR tabname IS NULL),
	columnname TEXT NULL CHECK (typeof(columnname) = 'text' OR columnname IS NULL),
	layoutname TEXT NULL CHECK (typeof(layoutname) = 'text' OR layoutname IS NULL),
	layoutorder INTEGER NULL CHECK (typeof(layoutorder) = 'integer' OR layoutorder IS NULL),
	datatype TEXT NULL CHECK (typeof(datatype) = 'text' OR datatype IS NULL),
	widgettype TEXT NULL CHECK (typeof(widgettype) = 'text' OR widgettype IS NULL),
	label TEXT NULL CHECK (typeof(label) = 'text' OR label IS NULL),
	placeholder TEXT NULL CHECK (typeof(placeholder) = 'text' OR placeholder IS NULL),
	ismandatory INTEGER NULL CHECK (typeof(ismandatory) = 'integer' OR ismandatory IS NULL),
	iseditable INTEGER NULL CHECK (typeof(iseditable) = 'integer' OR iseditable IS NULL),
	dv_querytext TEXT NULL CHECK (typeof(dv_querytext) = 'text' OR dv_querytext IS NULL),
	dv_orderby_id INTEGER NULL CHECK (typeof(dv_orderby_id) = 'integer' OR dv_orderby_id IS NULL),
	dv_isnullvalue INTEGER NULL CHECK (typeof(dv_isnullvalue) = 'integer' OR dv_isnullvalue IS NULL),
	hidden INTEGER NOT NULL DEFAULT false CHECK (typeof(hidden) = 'integer'),
	tooltip TEXT NULL CHECK (typeof(tooltip) = 'text' OR tooltip IS NULL),
	addparam JSON NULL CHECK (typeof(addparam) = 'text' OR addparam IS NULL),
	vdefault TEXT NULL CHECK (typeof(vdefault) = 'text' OR vdefault IS NULL),
	descript TEXT NULL CHECK (typeof(descript) = 'text' OR descript IS NULL),
	widgetcontrols JSON NULL CHECK (typeof(widgetcontrols) = 'text' OR widgetcontrols IS NULL),
	widgetfunction JSON NULL CHECK (typeof(widgetfunction) = 'text' OR widgetfunction IS NULL),
    PRIMARY KEY (formname, formtype, tabname, columnname)
);


CREATE TABLE config_csv (
	id INTEGER PRIMARY KEY,
	alias TEXT CHECK (typeof(alias) = 'text' OR alias IS NULL),
	descript TEXT CHECK (typeof(descript) = 'text' OR descript IS NULL),
	functionname TEXT CHECK (typeof(functionname) = 'text' OR functionname IS NULL),
	orderby INTEGER CHECK (typeof(orderby) = 'integer' OR orderby IS NULL),
	addparam TEXT CHECK (typeof(addparam) = 'text' OR addparam IS NULL)
);

CREATE TABLE edit_typevalue (
	rowid integer not null primary key,
	typevalue text check (typeof(typevalue)='text' or typevalue is not null),
	id text check (typeof(id)='text' or id is null),
	idval text check (typeof(idval)='text' or idval is null),
	descript text check (typeof(descript)='text' or descript is null),
	addparam text check (typeof(addparam)='text' or addparam is null)
);

create table checkproject_query (
	id integer primary key,
	query_type text check (typeof(query_type) in ('text', null) and query_type in ('GEOMETRIC DUPLICATE', 'GEOMETRIC ORPHAN', 'MANDATORY NULL', 'OUTLAYER')),
	table_name text CHECK (typeof(table_name)='text' OR table_name = NULL),
	columns text CHECK (typeof(columns)='text' OR columns = NULL),
	extra_condition text CHECK (typeof(extra_condition)='text' OR extra_condition = NULL),
	create_layer boolean CHECK (typeof(create_layer) IN (0,1,NULL)) DEFAULT  0,
	geometry_type text check (typeof(geometry_type) in ('text', null) and geometry_type in ('Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon')),
	error_message_id integer CHECK (typeof(error_message_id)='integer' OR error_message_id = NULL),
	info_message_id integer CHECK (typeof(info_message_id)='integer' OR info_message_id = NULL),
	except_lvl integer CHECK (typeof(except_lvl) in ('integer', NULL) AND except_lvl IN (1, 2, 3)),
	error_code integer CHECK (typeof(error_code)='integer' OR error_code = NULL),
	FOREIGN KEY (error_message_id) references sys_message (id) on update cascade on delete restrict,
	FOREIGN KEY (info_message_id) references sys_message (id) on update cascade on delete restrict
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
    name text unique check (typeof(name)='text' OR name=NULL),
    timestamp datetime CHECK (typeof(timestamp)='datetime' OR timestamp=NULL),
    elements integer CHECK (typeof(elements)='integer' OR elements=NULL),
    iber2d text null,
	roof text null,
    losses text null,
    bridge text null
);

CREATE TABLE cat_landuses (
	id integer primary key,
	idval text unique check (typeof(idval)='text') NOT NULL,
    descript text check (typeof(descript)='text' or typeof(descript)=null),
	manning real check (typeof(manning)='real' or typeof(manning)=null)
);


CREATE TABLE cat_transects (
    id integer primary key,
    idval text unique check (typeof(idval) = 'text') NOT NULL,
    descript text check (typeof(descript = 'text') or descript = null)
);

CREATE TABLE cat_transects_value (
    id integer primary key,
    transect text,
    data_group text,
    value text,
    FOREIGN KEY (transect) references cat_transects (idval) on update cascade on delete restrict
);

CREATE TABLE cat_curve (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    curve_type text check (typeof(curve_type) in ('text', null) and curve_type in ('CONTROL', 'DIVERSION', 'PUMP1', 'PUMP2', 'PUMP3', 'PUMP4', 'RATING', 'SHAPE', 'STORAGE', 'TIDAL')),
    descript text check (typeof(descript)='text' or typeof(descript)=null)
);

CREATE TABLE cat_curve_value (
    id integer primary key,
    curve text NOT NULL,
    xcoord real CHECK (typeof(xcoord)='real' OR xcoord = NULL),
    ycoord real CHECK (typeof(ycoord)='real' OR ycoord = NULL),
    FOREIGN KEY (curve) references cat_curve (idval) on update cascade on delete restrict
);

CREATE TABLE cat_timeseries (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    timser_type text check (typeof(timser_type) in ('text', null) and timser_type in ('EVAPORATION', 'INFLOW HYDROGRAPH', 'ORIFICE', 'OTHER', 'RAINFALL', 'TEMPERATURE', 'BC ELEVATION', 'BC FLOW')),
    times_type text CHECK (typeof(times_type) in ('text', null) and times_type in ('ABSOLUTE', 'FILE', 'RELATIVE')),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    fname text check (typeof(fname)='text' or fname = null)
);

CREATE TABLE cat_timeseries_value (
    id integer primary key,
    timeseries text NOT NULL,
    date datetime CHECK (typeof(date)='datetime' OR date=NULL),
    time datetime CHECK (typeof(time)='datetime' OR time=NULL),
    value real CHECK (typeof(value)='real' OR value=NULL),
    FOREIGN KEY (timeseries) references cat_timeseries(idval) on update cascade on delete restrict
);

CREATE TABLE cat_pattern (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    pattern_type text check (typeof(pattern_type) in ('text', null) and pattern_type in ('DAILY', 'HOURLY', 'MONTHLY', 'WEEKEND')),
    descript text check (typeof(descript) = 'text' or descript = null)
);

CREATE TABLE cat_pattern_value (
    id integer primary key,
    pattern text NOT NULL,
    timestep datetime CHECK (typeof(timestep)='datetime' OR timestep=NULL),
    value real CHECK (typeof(value)='real' OR value=NULL),
    FOREIGN KEY (pattern) references cat_pattern(idval) on update cascade on delete restrict
);

CREATE TABLE cat_controls (
    id integer primary key,
    descript text check (typeof(descript = 'text') or descript = null)
);

CREATE TABLE cat_raster (
    id integer primary key,
    idval text unique check (typeof(idval)='text') NOT NULL,
    raster_type text check (typeof(raster_type) in ('text', null) and raster_type in ('Intensity', 'Volume'))
);

CREATE TABLE cat_raster_value (
    id integer primary key,
    raster text NOT NULL,
    time integer CHECK (typeof(time)='integer' OR time=NULL),
	fname text check (typeof(fname)='text' or fname = null),
    FOREIGN KEY (raster) references cat_raster(idval) on update cascade on delete restrict
);

CREATE TABLE cat_tsgraph (
    id integer primary key,
    "name" text unique NOT NULL CHECK (typeof("name") = 'text' OR "name" = NULL),
    config json NOT NULL CHECK (typeof(config) = 'text' OR config = NULL)
);


-- -----------
-- GEOM TABLES
-- -----------

CREATE TABLE ground (
    fid integer PRIMARY KEY,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    cellsize real CHECK (typeof(cellsize)='real' OR cellsize = NULL) DEFAULT 10.0,
    annotation text check (typeof(annotation) = 'text' or annotation = null),
	landuse text CHECK (typeof(landuse)='text' OR landuse=NULL),
    custom_roughness real CHECK (typeof(custom_roughness)='real' OR custom_roughness=NULL),
    scs_cn real CHECK (typeof(scs_cn)='real' OR scs_cn=NULL),
	geom geometry,
    FOREIGN KEY (landuse) REFERENCES cat_landuses(idval) on update cascade on delete restrict
);

CREATE TABLE roof (
    fid integer PRIMARY KEY,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text CHECK (typeof(descript)='text' OR descript=NULL),
    slope real CHECK (typeof(slope)='real' OR slope=NULL),
    width real CHECK (typeof(width)='real' OR width=NULL),
    roughness real CHECK (typeof(roughness)='real' OR roughness=NULL),
    isconnected integer CHECK (typeof(isconnected) in ('integer', NULL) AND isconnected IN (1, 2, 3)),
    outlet_code text CHECK (typeof(outlet_code)='text' OR outlet_code=NULL),
    outlet_vol real CHECK (typeof(outlet_vol) = 'real' OR outlet_vol=NULL),
    street_vol real CHECK (typeof(street_vol) = 'real' OR street_vol=NULL),
    infiltr_vol real CHECK (typeof(infiltr_vol) = 'real' OR infiltr_vol=NULL),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry
    --FOREIGN KEY (outlet_code) REFERENCES node(code) on update cascade on delete restrict
);


CREATE TABLE mesh_anchor_points (
    fid integer PRIMARY KEY,
    geom geometry,
    cellsize real CHECK (typeof(cellsize)='real' OR cellsize = NULL) DEFAULT 1.0,
    z_value real CHECK (typeof(z_value)='real' OR z_value = NULL)
);

CREATE TABLE mesh_anchor_lines (
    fid integer PRIMARY KEY,
    geom geometry,
    cellsize real CHECK (typeof(cellsize)='real' OR cellsize = NULL) DEFAULT 1.0
);

CREATE TABLE inlet (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
   	outlet_node text check (typeof(outlet_node) = 'text' or outlet_node = null),
    outlet_type text check (typeof(outlet_type) in ('text', null) and outlet_type in ('SINK', 'TO NETWORK')),
    top_elev real check (typeof(top_elev) = 'real' or top_elev = null),
  	width real check (typeof(width) = 'real' or width = null),
    length real check (typeof(length) = 'real' or length = null),
    depth real check (typeof(depth) = 'real' or depth = null),
    method text check (typeof(method) in ('text', null) and method in ('UPC', 'W_O')),
    weir_cd real check (typeof(weir_cd) = 'real' or weir_cd = null),
    orifice_cd real check (typeof(orifice_cd) = 'real' or orifice_cd = null),
    a_param real check (typeof(a_param) = 'real' or a_param = null),
    b_param real check (typeof(b_param) = 'real' or b_param = null),
    efficiency real check (typeof(efficiency) = 'real' or efficiency = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (outlet_node) references node (code) on update cascade on delete restrict
);

CREATE TABLE hyetograph (
    fid integer primary key,
    code text unique check (typeof(code)='text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    timeseries text CHECK (typeof(timeseries)='text' OR timeseries=NULL),
	geom geometry,
    FOREIGN KEY (timeseries) references cat_timeseries (idval) on update cascade on delete restrict
);

create table boundary_conditions (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    bscenario text check (typeof(bscenario)='text' or bscenario=null),
    boundary_type text check (typeof(boundary_type) in ('text', null) and boundary_type in (
        "INLET TOTAL DISCHARGE (SUB)CRITICAL", "INLET WATER ELEVATION", "OUTLET (SUPER)CRITICAL", "OUTLET SUBCRITICAL WEIR HEIGHT", "OUTLET SUBCRITICAL WEIR ELEVATION", "OUTLET SUBCRITICAL GIVEN LEVEL"
    )),
    timeseries text check (typeof(timeseries)='text' or timeseries=null),
    other1 real,
    other2 real,
    geom geometry,
    FOREIGN KEY (bscenario) REFERENCES cat_bscenario(idval) on update cascade on delete restrict,
    FOREIGN KEY (timeseries) REFERENCES cat_timeseries(idval) on update cascade on delete restrict
);

create table culvert (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    culvert_type text CHECK (typeof(culvert_type) in ('text', null) and culvert_type in ('CIRCULAR', 'RECTANGULAR')),
    geom1 real CHECK (typeof(geom1)='real' OR geom1 = NULL),
    geom2 real CHECK (typeof(geom2)='real' OR geom2 = NULL),
    z_start real CHECK (typeof(z_start)='real' OR z_start = NULL),
    z_end real CHECK (typeof(z_end)='real' OR z_end = NULL),
    manning real CHECK (typeof(manning)='real' OR manning = NULL),
    iscalculate boolean CHECK (typeof(iscalculate) IN (0,1,NULL)) DEFAULT  1,
    collapse_moment real CHECK (typeof(collapse_moment)='real' OR collapse_moment = NULL),
    geom geometry
);

CREATE TABLE pinlet (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
   	outlet_node text check (typeof(outlet_node) = 'text' or outlet_node = null),
    outlet_type text check (typeof(outlet_type) in ('text', null) and outlet_type in ('SINK', 'TO NETWORK')),
    top_elev real check (typeof(top_elev) = 'real' or top_elev = null),
  	width real check (typeof(width) = 'real' or width = null),
    length real check (typeof(length) = 'real' or length = null),
    depth real check (typeof(depth) = 'real' or depth = null),
    method text check (typeof(method) in ('text', null) and method in ('UPC', 'W_O')),
    weir_cd real check (typeof(weir_cd) = 'real' or weir_cd = null),
    orifice_cd real check (typeof(orifice_cd) = 'real' or orifice_cd = null),
    a_param real check (typeof(a_param) = 'real' or a_param = null),
    b_param real check (typeof(b_param) = 'real' or b_param = null),
    efficiency real check (typeof(efficiency) = 'real' or efficiency = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (outlet_node) references node (code) on update cascade on delete restrict
);

create table bridge (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    deck_cd real CHECK (typeof(deck_cd)='real' OR deck_cd = NULL) DEFAULT 1.7 NOT NULL,
    freeflow_cd real CHECK (typeof(freeflow_cd)='real' OR freeflow_cd = NULL) DEFAULT 0.6 NOT NULL,
    sumergeflow_cd real CHECK (typeof(sumergeflow_cd)='real' OR sumergeflow_cd = NULL) DEFAULT 0.8 NOT NULL,
	length real CHECK (typeof(length)='real' OR length = NULL),
    descript text unique check (typeof(descript) = 'text' or descript = null),
    geom geometry
);

create table bridge_value (
    id integer primary key,
    bridge_code text CHECK (typeof(bridge_code)='text' OR bridge_code = NULL) NOT NULL,
    distance real check (typeof(distance) = 'real' or distance = null) NOT NULL,
    topelev real CHECK (typeof(topelev)='real' OR topelev = NULL) DEFAULT 0 NOT NULL,
    lowelev real CHECK (typeof(lowelev)='real' OR lowelev = NULL) DEFAULT 0 NOT NULL,
    openingval real CHECK (typeof(openingval)='real' OR openingval = NULL) DEFAULT 100 NOT NULL,
    FOREIGN KEY (bridge_code) references bridge(code) on update cascade on delete cascade
);


-- ----------
-- INP TABLES
-- ----------
CREATE TABLE inp_conduit (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    shape text check (typeof(shape) = 'text' and shape in ('ARCH', 'BASKETHANDLE', 'CIRCULAR', 'CUSTOM', 'DUMMY', 'EGG', 'FILLED_CIRCULAR', 'FORCE_MAIN', 'HORIZ_ELLIPSE', 'HORSESHOE', 'IRREGULAR', 'MODBASKETHANDLE', 'PARABOLIC', 'POWER', 'RECT_CLOSED', 'RECT_OPEN', 'RECT_ROUND', 'RECT_TRIANGULAR', 'SEMICIRCULAR', 'SEMIELLIPTICAL', 'TRAPEZOIDAL', 'TRIANGULAR', 'VERT_ELLIPSE', 'VIRTUAL')) NOT NULL,
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null),
    geom3 real check (typeof(geom3) = 'real' or geom3 = null),
    geom4 real check (typeof(geom4) = 'real' or geom4 = null),
    curve_transect text check (typeof(curve_transect) = 'text' or curve_transect=null),
    roughness real check (typeof(roughness) = 'real' or roughness = null),
    length real check (typeof(length) = 'real' or length = null),
    z1 real check (typeof(z1) = 'real' or z1 = null),
    z2 real check (typeof(z2) = 'real' or z2 = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    barrels real check (typeof(barrels) = 'real' or barrels = null) DEFAULT 1,
    culvert text check (typeof(culvert) = 'text' or culvert = null),
    kentry real check (typeof(kentry) = 'real' or kentry = null),
    kexit real check (typeof(kexit) = 'real' or kexit = null),
    kavg real check (typeof(kavg) = 'real' or kavg = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    seepage real check (typeof(seepage) = 'real' or seepage = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (node_1) REFERENCES node (code) on update cascade on delete restrict,
    FOREIGN KEY (node_2) REFERENCES node (code) on update cascade on delete restrict
);

CREATE TABLE inp_outlet (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript)='text' or descript= null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    outlet_type text check (typeof(outlet_type) in ('text', null) and outlet_type in ('FUNCTIONAL/DEPTH', 'FUNCTIONAL/HEAD', 'TABULAR/DEPTH', 'TABULAR/HEAD')),
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    cd1 real check (typeof(cd1)='real' or cd1= null) default 1,
    cd2 real check (typeof(cd2)='real' or cd2= null) default 1,
    curve text check (typeof(curve)='text' or curve= null),
    annotation text check (typeof(annotation)='real' or annotation= null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve (idval) on update cascade on delete restrict,
    FOREIGN KEY (node_1) REFERENCES node (code) on update cascade on delete restrict,
    FOREIGN KEY (node_2) REFERENCES node (code) on update cascade on delete restrict
);


CREATE TABLE inp_orifice (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    ori_type text check (typeof(ori_type) in ('text', null) and ori_type in ('BOTTOM', 'SIDE')),
    shape text check (typeof(shape) in ('text', null) and shape in ('CIRCULAR', 'RECT_CLOSED')) DEFAULT 'CIRCULAR' NOT NULL,
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null)  DEFAULT 0.00,
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    cd1 real check (typeof(cd1) = 'real' or cd1 = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    close_time real check (typeof(close_time) = 'real' or close_time = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (node_1) REFERENCES node (code) on update cascade on delete restrict,
    FOREIGN KEY (node_2) REFERENCES node (code) on update cascade on delete restrict
);

CREATE TABLE inp_weir (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    weir_type text check (typeof(weir_type) in ('text', null) and weir_type in ('ROADWAY', 'SIDEFLOW', 'TRANSVERSE', 'TRAPEZOIDAL', 'V-NOTCH')),
    offsetval real check (typeof(offsetval) = 'real' or offsetval = null),
    geom1 real check (typeof(geom1) = 'real' or geom1 = null),
    geom2 real check (typeof(geom2) = 'real' or geom2 = null)  DEFAULT 0.00,
    geom3 real check (typeof(geom3) = 'real' or geom3 = null)  DEFAULT 0.00,
    geom4 real check (typeof(geom4) = 'real' or geom4 = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    cd real check (typeof(cd) = 'real' or cd = null),
    cd2 real check (typeof(cd2) = 'real' or cd2 = null),
    flap text check (typeof(flap) in ('text', null) and flap in ('YES', 'NO')),
    ec integer check (typeof(ec) = 'integer' or ec = null),
    surcharge text check (typeof(surcharge) = 'text' or surcharge = null),
    road_width real check (typeof(road_width) = 'real' or road_width = null),
    road_surf text check (typeof(road_surf) in ('text', null) and road_surf in ('PAVED', 'GRAVEL')),
    curve text check (typeof(curve) = 'text' or curve = null),
    crest_height real check (typeof(crest_height)='real' or crest_height = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve(idval) on update cascade on delete restrict,
    FOREIGN KEY (node_1) REFERENCES node (code) on update cascade on delete restrict,
    FOREIGN KEY (node_2) REFERENCES node (code) on update cascade on delete restrict
);

CREATE TABLE inp_pump (
    fid integer primary key,
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    code text unique check (typeof(code) = 'text' or code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    node_1 text check (typeof(node_1) = 'text' or node_1 = null),
    node_2 text check (typeof(node_2) = 'text' or node_2 = null),
    curve text check (typeof( curve) = 'text' or  curve = null),
    state text check (typeof(state) in ('text', null) and state in ('OFF', 'ON')),
    startup real check (typeof(startup) = 'real' or startup = null),
    shutoff real check (typeof(shutoff) = 'real' or shutoff = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve(idval) on update cascade on delete restrict,
    FOREIGN KEY (node_1) REFERENCES node (code) on update cascade on delete restrict,
    FOREIGN KEY (node_2) REFERENCES node (code) on update cascade on delete restrict
);

CREATE TABLE inp_outfall (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    gate text check (typeof(gate) in ('text', null) and gate in ('YES', 'NO')),
    outfall_type text check (typeof(outfall_type) in ('text', null) and outfall_type in ('FIXED', 'FREE', 'NORMAL', 'TIDAL', 'TIMESERIES')),
    stage real check (typeof(stage) = 'real' or stage = null),
    curve text check (typeof(curve) = 'text' or curve = null),
    timeseries text check (typeof(timeseries) = 'text' or timeseries = null),
    routeto text check (typeof(routeto) = 'text' or routeto = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve(idval) on update cascade on delete restrict
    FOREIGN KEY (timeseries) references cat_timeseries(idval) on update cascade on delete restrict
);

CREATE TABLE inp_divider (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    apond real check (typeof(apond) = 'real' or apond = null),
    divert_arc text check(typeof(divert_arc)='text' or divert_arc=null),
    divider_type text check (typeof(divider_type) IN ('text', null) and divider_type in ('CUTOFF', 'OVERFLOW', 'TABULAR', 'WEIR')),
    cutoff_flow real check (typeof(cutoff_flow) = 'real' or cutoff_flow = null),
    qmin real check (typeof(qmin) = 'real' or qmin = null),
    curve text check (typeof(curve) = 'text' or curve = null),
    q0 real check (typeof(q0) = 'real' or q0 = null),
    qmax real check (typeof(qmax) = 'real' or qmax = null),
    annotation text check (typeof(annotation) = 'real' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve(idval) on update cascade on delete restrict
    FOREIGN KEY (divert_arc) references inp_conduit(code) on update cascade on delete restrict
);

CREATE TABLE inp_storage (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
    y0 real check (typeof(y0) = 'real' or y0 = null),
    ysur real check (typeof(ysur) = 'real' or ysur = null),
    storage_type text check (typeof(storage_type) in ('text', null) and storage_type in ('FUNCTIONAL', 'TABULAR')),
    curve text check (typeof(curve) = 'text' or curve = null),
    a1 real check (typeof(a1) = 'real' or a1 = null),
    a2 real check (typeof(a2) = 'real' or a2 = null),
    a0 real check (typeof(a0) = 'real' or a0 = null),
    fevap real check (typeof(fevap) = 'real' or fevap = null),
    psi real check (typeof(psi) = 'real' or psi = null),
    ksat real check (typeof(ksat) = 'real' or ksat = null),
    imd real check (typeof(imd) = 'real' or imd = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    geom geometry,
    FOREIGN KEY (curve) references cat_curve(idval) on update cascade on delete restrict
);

CREATE TABLE inp_junction (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    elev real check (typeof(elev) = 'real' or elev = null),
    ymax real check (typeof(ymax) = 'real' or ymax = null),
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
    descript text CHECK (typeof(descript)='text' OR descript=NULL)
);

create table inp_dwf (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    format text check (typeof(format) = 'text' or format=null) default 'FLOW',
    avg_value real check (typeof(avg_value)='real' or avg_value = null) DEFAULT 0.0001,
    pattern1 text check (typeof(pattern1) = 'text' or pattern1 = null),
    pattern2 text check (typeof(pattern2) = 'text' or pattern2 = null),
    pattern3 text check (typeof(pattern3) = 'text' or pattern3 = null),
    pattern4 text check (typeof(pattern4) = 'text' or pattern4 = null),
    annotation text check (typeof(annotation) = 'text' or annotation = null),
    FOREIGN KEY (pattern1) REFERENCES cat_pattern(idval) on update cascade on delete restrict
    FOREIGN KEY (pattern2) REFERENCES cat_pattern(idval) on update cascade on delete restrict
    FOREIGN KEY (pattern3) REFERENCES cat_pattern(idval) on update cascade on delete restrict
    FOREIGN KEY (pattern4) REFERENCES cat_pattern(idval) on update cascade on delete restrict
);

create table inp_inflow (
    fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
    custom_code text unique check (typeof(custom_code) = 'text' or custom_code = null),
    descript text check (typeof(descript) = 'text' or descript = null),
    timeseries text check (typeof(timeseries) = 'text' or timeseries = null),
    format text check (typeof(format) = 'text' or format =null) default 'FLOW',
    mfactor real check (typeof(mfactor) = 'real' or mfactor=null) default 1,
    sfactor real check (typeof(sfactor)='real' or sfactor=null) default 1,
    ufactor real check (typeof(ufactor)='real' or ufactor=null) default 1,
    base real check (typeof(base)='real' or base=null) default 0,
    pattern text check (typeof(pattern) = 'integer' or pattern=null),
    type text check(typeof(type)='text' or type=null),
    FOREIGN KEY (pattern) REFERENCES cat_pattern(idval) on update cascade on delete restrict
    FOREIGN KEY (timeseries) REFERENCES cat_timeseries(idval) on update cascade on delete restrict
);

-------------
-- lid tables
-------------

CREATE TABLE inp_lid (
	id integer primary key,
	idval text unique check (typeof(idval) = 'text' or idval = null),
	lid_type text unique check (typeof(lid_type) = 'text' or lid_type = null),
	observ text unique check (typeof(observ) = 'text' or observ = null)
);

CREATE TABLE inp_lid_value (
	id integer primary key,
	lid text unique check (typeof(lid) = 'text' or lid = null),
	lidlayer text unique check (typeof(lidlayer) = 'text' or lidlayer = null),
	value_2 real CHECK (typeof(value_2)='real' OR value_2 = NULL),
	value_3 real CHECK (typeof(value_3)='real' OR value_3 = NULL),
	value_4 real CHECK (typeof(value_4)='real' OR value_4 = NULL),
	value_5 real CHECK (typeof(value_5)='real' OR value_5 = NULL),
	value_6 text unique check (typeof(value_6) = 'text' or value_6 = null),
	value_7 text unique check (typeof(value_7) = 'text' or value_7 = null),
	value_8 text unique check (typeof(value_8) = 'text' or value_8 = null),
    FOREIGN KEY (lid) references inp_lid(idval) on update cascade on delete restrict
);

CREATE TABLE inp_lid_roof (
	id integer primary key,
	lid text unique check (typeof(lid) = 'text' or lid = null),
	roof text unique check (typeof(roof) = 'text' or roof = null),
	numelem real CHECK (typeof(numelem)='real' OR numelem = NULL),
	area real CHECK (typeof(area)='area' OR area = NULL),
	width real CHECK (typeof(width)='real' OR width = NULL),
	initsat real CHECK (typeof(initsat)='real' OR initsat = NULL),
	fromimp real CHECK (typeof(fromimp)='real' OR fromimp = NULL),
	toperv real CHECK (typeof(toperv)='real' OR toperv = NULL),
	descript text unique check (typeof(descript) = 'text' or descript = null),
    FOREIGN KEY (lid) references inp_lid(idval) on update cascade on delete restrict,
	FOREIGN KEY (roof) references roof(code) on update cascade on delete restrict
);

CREATE TABLE inp_lid_ground (
	id integer primary key,
	lid text unique check (typeof(lid) = 'text' or lid = null),
	ground text unique check (typeof(ground) = 'text' or ground = null),
	numelem real CHECK (typeof(numelem)='real' OR numelem = NULL),
	area real CHECK (typeof(area)='area' OR area = NULL),
	width real CHECK (typeof(width)='real' OR width = NULL),
	initsat real CHECK (typeof(initsat)='real' OR initsat = NULL),
	fromimp real CHECK (typeof(fromimp)='real' OR fromimp = NULL),
	toperv real CHECK (typeof(toperv)='real' OR toperv = NULL),
	descript text unique check (typeof(descript) = 'text' or descript = null),
    FOREIGN KEY (lid) references inp_lid(idval) on update cascade on delete restrict,
	FOREIGN KEY (ground) references ground(code) on update cascade on delete restrict
);


-- ------------
-- VI_EXPORT_INP
-- -----------
create view if not exists vi_title as select parameter, value from config_param_user where parameter like 'project_%';

create view if not exists vi_files as select fname as Name from inp_files;

create view if not exists vi_options as
select
  parameter as Option,
  case
    when parameter in ('inp_options_start_date', 'inp_options_end_date', 'inp_options_report_start_date')
      then strftime('%m/%d/%Y', value)
    else value
  end as Value
from config_param_user
where parameter like 'inp_options%';

create view if not exists vi_report as select parameter as Option, value as Value from config_param_user where parameter like 'inp_report%' and value is not null;

create view if not exists vi_conduits as
    select
    code as Name,
    node_1 as FromNode,
    node_2 as ToNode,
    length as Length,
    roughness as Roughness,
    z1 as InOffset,
    z2 as OutOffset,
    q0 as InitFlow,
    qmax as MaxFlow,
    shape as Shape,
    geom1 as Geom1,
    geom2 as Geom2,
    geom3 as Geom3,
    geom4 as Geom4,
    barrels as Barrels,
    culvert as Culvert,
    curve_transect as Shp_Trnsct,
    kentry as Kentry,
    kexit as Kexit,
    kavg as Kavg,
    flap as FlapGate,
    seepage as Seepage,
    annotation as Annotation,
    geom
    from inp_conduit;

create view if not exists vi_outlets as
    select
    code as Name,
    node_1 as FromNode,
    node_2 as ToNode,
    offsetval as InOffset,
    outlet_type as RateCurve,
    cd1 as Qcoeff,
    cd2 as Qexpon,
    flap as FlapGate,
    curve as CurveName,
    annotation as Annotation,
    geom
    from inp_outlet;

create view if not exists vi_orifices as
    select code as Name,
    node_1 as FromNode,
    node_2 as ToNode,
    ori_type as Type,
    offsetval as InOffset,
    cd1 as Qcoeff,
    flap as FlapGate,
    close_time as CloseTime,
    annotation as Annotation,
    shape as Shape,
    geom1 as Height,
    geom2 as Width,
    geom
    from inp_orifice;

create view if not exists vi_weirs as
    select
    code as Name,
    node_1 as FromNode,
    node_2 as ToNode,
    weir_type as Type,
    crest_height as CrestHeigh,
    cd as Qcoeff,
    cd2 as EndCoeff,
    flap as FlapGate,
    ec as EndContrac,
    surcharge as Surcharge,
    road_width as RoadWidth,
    road_surf as RoadSurf,
    curve as CoeffCurve,
    annotation as Annotation,
    geom1 as Height,
    geom2 as Length,
    geom3 as SideSlope,
    geom
    from inp_weir;

create view if not exists vi_pumps as
    select
    code as Name,
    node_1 as FromNode,
    node_2 as ToNode,
    curve as PumpCurve,
    state as Status,
    startup as Startup,
    shutoff as Shutoff,
    annotation as Annotation,
    geom
    from inp_pump;

create view if not exists vi_outfalls as
    select
    code as Name,
    elev as Elevation,
    routeto as RouteTo,
    outfall_type as Type,
    case
        when outfall_type = 'FIXED' then stage
        else null
    end as FixedStage,
    case
        when outfall_type = 'TIMESERIES' then timeseries
        when outfall_type = 'TIDAL' then curve
        else null
    end as Curve_TS,
    gate as FlapGate,
    annotation as Annotation,
    geom
    from inp_outfall;

create view if not exists vi_dividers as
    select
    code as Name,
    elev as Elevation,
    divert_arc as DivertLink,
    divider_type as Type,
    cutoff_flow as CutoffFlow,
    curve as Curve,
    qmin as WeirMinFlo,
    qmax as WeirMaxDep,
    q0 as WeirCoeff,
    ymax as MaxDepth,
    y0 as InitDepth,
    ysur as SurDepth,
    apond as Aponded,
    annotation as Annotation,
    geom
    from inp_divider;

create view if not exists vi_storage as
    select
    code as Name,
    elev as Elevation,
    ymax as MaxDepth,
    y0 as InitDepth,
    storage_type as Type,
    curve as Curve,
    a1 as Coeff,
    a2 as Exponent,
    a0 as Constant,
    ysur as SurDepth,
    fevap as Fevap,
    psi as Psi,
    ksat as Ksat,
    imd as IMD,
    annotation as Annotation,
    geom
    from inp_storage;

create view if not exists vi_junctions as
    SELECT
    code as Name,
    elev as Elevation,
    ymax as MaxDepth,
    y0 as InitDepth,
    ysur as SurDepth,
    apond as Aponded,
    annotation as Annotation,
    geom
    from inp_junction;

CREATE VIEW vi_curves as
    WITH qt AS (
        SELECT
        ccv.id,
        ccv.curve,
        case when (ROW_NUMBER() OVER (PARTITION BY curve ORDER BY curve))=1 then c.curve_type end as curve_type,
        ccv.xcoord,
        ccv.ycoord
        FROM cat_curve c
        JOIN cat_curve_value ccv ON c.idval= ccv.curve
    )
    SELECT qt.curve as Name,
    qt.curve_type as Type,
    qt.xcoord as "X-Value",
    qt.ycoord as "Y-value" FROM qt ORDER BY qt.id;

create view if not exists vi_timeseries as
    SELECT t.idval as timser_id,
    t.other1,
    t.other2,
    t.other3
    FROM (
        SELECT ctv.id,
            c.idval,
            ctv.date AS other1,
            ctv.time AS other2,
            ctv.value AS other3
            FROM cat_timeseries_value ctv
            JOIN cat_timeseries c ON ctv.timeseries = c.id
            WHERE c.times_type = 'ABSOLUTE' UNION
        SELECT ctv.id,
            c.idval,
            'FILE'||' '||c.fname AS other1,
            time AS other2,
            value AS other3
            FROM cat_timeseries_value ctv
            JOIN cat_timeseries c ON ctv.timeseries = c.id
            WHERE c.times_type = 'FILE' UNION
        SELECT ctv.id,
            c.idval,
            NULL AS other1,
            ctv."time" AS other2,
            ctv.value AS other3
            FROM cat_timeseries_value ctv
            JOIN cat_timeseries c ON ctv.timeseries = c.id
            WHERE c.times_type = 'RELATIVE'
        ) t
    ORDER BY t.id;

create view if not exists vi_patterns as
    select
    pattern as Name,
    "time" as "Time",
    value as Factor
    from cat_pattern_value;

create view if not exists vi_losses as
    select
    code as Name,
    kentry as Kentry,
    kexit as Kexit,
    kavg as Kavg,
    flap as FlapGate,
    seepage as Seepage
    from inp_conduit;

create view if not exists vi_dwf as
    select
    code as Name,
    format as Constituent,
    avg_value as Average_Value,
    pattern1 as Time_Pattern1,
    pattern2 as Time_Pattern2,
    pattern3 as Time_Pattern3,
    pattern4 as Time_Pattern4
    from inp_dwf;

create view if not exists vi_controls as
    select descript AS "text" from cat_controls;

create view if not exists vi_transects as
    select data_group, value from cat_transects_value order by id;
create view if not exists vi_report as
    select parameter, value from config_param_user where parameter like '%inp_report_%';

create view if not exists vi_inflows as
    select
    code as Name,
    format as Constituent,
    base as Baseline,
    pattern as Baseline_Pattern,
    timeseries as Time_Series,
    mfactor as Units_Factor,
    sfactor as Scale_Factor,
    type as Type
    from inp_inflow;

create view if not exists vi_xsections as
    select code as Link, shape as Shape, geom1 as Geom1, curve_transect as Geom2, 0 as Geom3, 0 as Geom4, barrels, culvert from inp_conduit where shape ='CUSTOM' union
    select code as Link, shape as Shape, curve_transect as Geom1, 0 as Geom2, 0 as Geom3, 0 as Geom4 , barrels, culvert from inp_conduit where shape='IRREGULAR'union
    select code as Link, shape as Shape, geom1 as Geom1, geom2 as Geom2, geom3 as Geom3 , geom4 as Geom4, barrels, culvert from inp_conduit where shape not in ('CUSTOM', 'IRREGULAR') union
    select code as Link, shape as Shape, geom1 as Geom1, geom2 as Geom2, null as Geom3, null as Geom4, null as barrels, null as culvert from inp_orifice union
    select code as Link, shape as Shape, geom1 as Geom1, geom2 as Geom2, null as Geom3, null as Geom4, null as barrels, null as culvert from inp_weir;

CREATE VIEW IF NOT EXISTS vi_inlet AS
SELECT code,
    outlet_type,
   	outlet_node,
   	ST_X(geom) AS xcoord,
   	ST_Y(geom) AS ycoord,
   	top_elev,
  	width,
    length,
    depth,
    method,
    weir_cd,
    orifice_cd,
    a_param,
    b_param,
    efficiency,
    geom
FROM inlet;

CREATE TABLE node (
    fid integer primary key,
    code text unique,
    table_name text,
    table_fid integer,
    custom_code text,
    geom geometry
);

CREATE TABLE arc (
    fid integer primary key,
    code text unique,
    table_name text,
    table_fid integer,
    custom_code text,
    geom geometry
);


CREATE VIEW if not exists v_ui_file AS
    SELECT name, elements, timestamp as creation_date FROM cat_file ORDER BY name ASC;


CREATE VIEW vi_roof2junction as
SELECT r.code, r.outlet_code, setsrid(MakeLine(centroid(r.geom), j.geom), <SRID_VALUE>) AS geom
    FROM roof r
    JOIN inp_junction j ON r.outlet_code = j.code;


CREATE VIEW vi_inlet2junction as
SELECT i.code, i.outlet_node, i.top_elev, j.elev,
       (i.top_elev - j.elev) as elev_diff,
       CASE WHEN (i.top_elev - j.elev) > 0 THEN 0 ELSE 1 END as inverted_slope,
       SetSRID(MakeLine(i.geom, j.geom), <SRID_VALUE>) AS geom
    FROM inlet i
    JOIN inp_junction j ON i.outlet_node = j.code
UNION
SELECT pi.code, pi.outlet_node, pi.top_elev, j.elev,
       (pi.top_elev - j.elev) as elev_diff,
       CASE WHEN (pi.top_elev - j.elev) > 0 THEN 0 ELSE 1 END as inverted_slope,
       SetSRID(MakeLine(ST_Centroid(pi.geom), j.geom), <SRID_VALUE>) AS geom
    FROM pinlet pi
    JOIN inp_junction j ON pi.outlet_node = j.code;


-- ----------------------------------------
-- CREATE SYS GPKG REQUIREMENTS DYNAMICALLY
-- ----------------------------------------
create table tables_nogeom (table_name text primary key, index_col text);
create table tables_geom (table_name text primary key, isgeom text NOT NULL, index_col text);


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
