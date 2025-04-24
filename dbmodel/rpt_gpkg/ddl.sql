/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


CREATE TABLE rpt_arc (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	shape text unique check (typeof(shape) = 'text' or shape = null),
	geom1 real check (typeof(geom1)='real' or geom1=null),
	geom2 real check (typeof(geom2)='real' or geom2=null),
	geom3 real check (typeof(geom3)='real' or geom3=null),
	geom4 real check (typeof(geom4)='real' or geom4=null),
	resultdate text check (typeof(resultdate) = 'text' or resultdate = null),
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    flow real check (typeof(flow) = 'real' or flow = null),
    velocity real check (typeof(velocity) = 'real' or velocity = null),
    fullpercent real check (typeof(fullpercent) = 'real' or fullpercent = null),
    geom geometry
);

CREATE TABLE rpt_arcflow_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	shape text unique check (typeof(shape) = 'text' or shape = null),
	geom1 real check (typeof(geom1)='real' or geom1=null),
	geom2 real check (typeof(geom2)='real' or geom2=null),
	geom3 real check (typeof(geom3)='real' or geom3=null),
	geom4 real check (typeof(geom4)='real' or geom4=null),
    flow real check (typeof(flow) = 'real' or flow = null),
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
    time_min text check (typeof(time_min) = 'text' or time_min = null),
    geom geometry
);


CREATE TABLE rpt_condsurcharge_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	shape text unique check (typeof(shape) = 'text' or shape = null),
	geom1 real check (typeof(geom1)='real' or geom1=null),
	geom2 real check (typeof(geom2)='real' or geom2=null),
	geom3 real check (typeof(geom3)='real' or geom3=null),
	geom4 real check (typeof(geom4)='real' or geom4=null),
    flow real check (typeof(flow) = 'real' or flow = null),
    both_ends real check (typeof(both_ends) = 'real' or both_ends = null),
    upstream real check (typeof(upstream) = 'real' or upstream = null),
    dnstream real check (typeof(dnstream) = 'real' or dnstream = null),
    hour_nflow real check (typeof(hour_nflow) = 'real' or hour_nflow = null),
    hour_limit real check (typeof(hour_limit) = 'real' or hour_limit = null),
    geom geometry
);


CREATE TABLE rpt_flowclass_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	shape text unique check (typeof(shape) = 'text' or shape = null),
	geom1 real check (typeof(geom1)='real' or geom1=null),
	geom2 real check (typeof(geom2)='real' or geom2=null),
	geom3 real check (typeof(geom3)='real' or geom3=null),
	geom4 real check (typeof(geom4)='real' or geom4=null),
    flow real check (typeof(flow) = 'real' or flow = null),
    length real check (typeof(length) = 'real' or length = null),
    dry real check (typeof(dry) = 'real' or dry = null),
    up_dry real check (typeof(up_dry) = 'real' or up_dry = null),
    down_dry real check (typeof(down_dry) = 'real' or down_dry = null),
    sub_crit real check (typeof(sub_crit) = 'real' or sub_crit = null),
    sub_crit_1 real check (typeof(sub_crit_1) = 'real' or sub_crit_1 = null),
    up_crit real check (typeof(up_crit) = 'real' or up_crit = null),
    down_crit real check (typeof(down_crit) = 'real' or down_crit = null),
    froud_numb real check (typeof(froud_numb) = 'real' or froud_numb = null),
    flow_chang real check (typeof(flow_chang) = 'real' or flow_chang = null),
    geom geometry
);

CREATE TABLE rpt_flowrouting_cont (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	shape text unique check (typeof(shape) = 'text' or shape = null),
	geom1 real check (typeof(geom1)='real' or geom1=null),
	geom2 real check (typeof(geom2)='real' or geom2=null),
	geom3 real check (typeof(geom3)='real' or geom3=null),
	geom4 real check (typeof(geom4)='real' or geom4=null),
    flow real check (typeof(flow) = 'real' or flow = null),
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
    seepage_losses real check (typeof(seepage_losses) = 'real' or seepage_losses = null),
    geom geometry
);

CREATE TABLE rpt_node (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    resultdate text check (typeof(resultdate) = 'text' or resultdate = null),
    resulttime text check (typeof(resulttime) = 'text' or resulttime = null),
    flooding real check (typeof(flooding) = 'real' or flooding = null),
    depth real check (typeof("depth") = 'real' or "depth" = null),
    head real check (typeof(head) = 'real' or head = null),
    inflow real check (typeof(inflow) = 'real' or inflow = null),
    geom geometry
);

CREATE TABLE rpt_nodedepth_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    aver_depth real check (typeof(aver_depth) = 'real' or aver_depth = null),
    max_depth real check (typeof(max_depth) = 'real' or max_depth = null),
    max_hgl real check (typeof(max_hgl) = 'real' or max_hgl = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    geom geometry

);

CREATE TABLE rpt_nodeflooding_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    hour_flood real check (typeof(hour_flood) = 'real' or hour_flood = null),
    max_rate real check (typeof(max_rate) = 'real' or max_rate = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    tot_flood real check (typeof(tot_flood) = 'real' or tot_flood = null),
    max_ponded real check (typeof(max_ponded) = 'real' or max_ponded = null),
    geom geometry
);

CREATE TABLE rpt_nodeinflow_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    max_latinf real check (typeof(max_latinf) = 'real' or max_latinf = null),
    max_totinf real check (typeof(max_totinf) = 'real' or max_totinf = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    latinf_vol real check (typeof(latinf_vol) = 'real' or latinf_vol = null),
    totinf_vol real check (typeof(totinf_vol) = 'real' or totinf_vol = null),
    flow_balance_error real check (typeof(flow_balance_error) = 'real' or flow_balance_error = null),
    other_info text check (typeof(other_info) = 'text' or other_info = null),
    geom geometry
);

CREATE TABLE rpt_nodesurcharge_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    swnod_type text check (typeof(swnod_type) = 'text' or swnod_type = null),
    hour_surch real check (typeof(hour_surch) = 'real' or hour_surch = null),
    max_height real check (typeof(max_height) = 'real' or max_height = null),
    min_depth real check (typeof(min_depth) = 'real' or min_depth = null),
    geom geometry
);

CREATE TABLE rpt_outfallflow_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    flow_freq real check (typeof(flow_freq) = 'real' or flow_freq = null),
    avg_flow real check (typeof(avg_flow) = 'real' or avg_flow = null),
    max_flow real check (typeof(max_flow) = 'real' or max_flow = null),
    total_vol real check (typeof(total_vol) = 'real' or total_vol = null),
    geom geometry
);

CREATE TABLE rpt_pumping_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
    percent real check (typeof("percent") = 'real' or "percent" = null),
    num_startup integer check (typeof(num_startup) = 'integer' or num_startup = null),
    min_flow real check (typeof(min_flow) = 'real' or min_flow = null),
    avg_flow real check (typeof(avg_flow) = 'real' or avg_flow = null),
    max_flow real check (typeof(max_flow) = 'real' or max_flow = null),
    vol_ltr real check (typeof(vol_ltr) = 'real' or vol_ltr = null),
    powus_kwh real check (typeof(powus_kwh) = 'real' or powus_kwh = null),
    timoff_min real check (typeof(timoff_min) = 'real' or timoff_min = null),
    timoff_max real check (typeof(timoff_max) = 'real' or timoff_max = null),
    geom geometry
);


CREATE TABLE rpt_storagevol_sum (
	fid integer primary key,
    code text unique check (typeof(code) = 'text' or code = null),
	epa_type text unique check (typeof(epa_type) = 'text' or epa_type = null),
	ymax real check (typeof(ymax)='real' or ymax=null),
	elev real check (typeof(elev)='real' or elev=null),
	y0 real check (typeof(y0)='real' or y0=null),
	ysur real check (typeof(ysur)='real' or ysur=null),
    aver_vol real check (typeof(aver_vol) = 'real' or aver_vol = null),
    avg_full real check (typeof(avg_full) = 'real' or avg_full = null),
    ei_loss real check (typeof(ei_loss) = 'real' or ei_loss = null),
    max_vol real check (typeof(max_vol) = 'real' or max_vol = null),
    max_full real check (typeof(max_full) = 'real' or max_full = null),
    time_days text check (typeof(time_days) = 'text' or time_days = null),
    time_hour text check (typeof(time_hour) = 'text' or time_hour = null),
    max_out real check (typeof(max_out) = 'real' or max_out = null),
    geom geometry
);

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
