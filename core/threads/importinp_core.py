try:
    import geopandas as gpd
except ImportError:
    pass

_tables = (
    {
        "table_name": "inp_conduit",
        "section": "CONDUITS",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "Length": "custom_length",
            "Roughness": "custom_roughness",
            "InOffset": "z1",
            "OutOffset": "z2",
            "InitFlow": "q0",
            "MaxFlow": "qmax",
        },
    },
    {
        "table_name": "inp_conduit",
        "section": "XSECTIONS",
        "mapper": {
            "Shape": "shape",
            "Geom1": "geom1",
            "Geom2": "geom2",
            "Geom3": "geom3",
            "Geom4": "geom4",
            "Barrels": "barrels",
            "Culvert": "culvert",
            "Shp_Trnsct": "shape_trnsct",
        },
    },
    {
        "table_name": "inp_conduit",
        "section": "LOSSES",
        "mapper": {
            "Kentry": "kentry",
            "Kexit": "kexit",
            "Kavg": "kavg",
            "FlapGate": "flap",
            "Seepage": "seepage",
        },
    },
    {
        "table_name": "inp_subcatchment",
        "section": "SUBCATCHMENTS",
        "mapper": {
            "Name": "code",
            "RainGage": "rg_id",
            "Outlet": "outlet_id",
            "Area": "area",
            "Imperv": "imperv",
            "Width": "width",
            "Slope": "slope",
            "CurbLen": "clength",
            "SnowPack": "snow_id",
        },
    },
    {
        "table_name": "inp_subcatchment",
        "section": "INFILTRATION",
        "mapper": {
            "InfMethod": "method",
            "MaxRate": "maxrate",
            "MinRate": "minrate",
            "Decay": "decay",
            "DryTime": "drytime",
            "MaxInf": "maxinfl",
            "SuctHead": "suction",
            "Conductiv": "conduct",
            "InitDef": "initdef",
            "CurveNum": "curveno",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_subcatchment",
        "section": "SUBAREAS",
        "mapper": {
            "Subcatchment": "subc_id",
            "N_Imperv": "nimp",
            "N_Perv": "nperv",
            "S_Imperv": "simp",
            "S_Perv": "sperv",
            "PctZero": "zero",
            "RouteTo": "routeto",
            "PctRouted": "rted",
        },
    },
    {
        "table_name": "inp_outlet",
        "section": "OUTLETS",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "InOffset": "offsetval",
            "RateCurve": "outlet_type",
            "Qcoeff": "cd1",
            "Qexpon": "cd2",
            "FlapGate": "flap",
            "CurveName": "curve_id",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_orifice",
        "section": "ORIFICES",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "Type": "ori_type",
            "InOffset": "offsetval",
            "Qcoeff": "cd1",
            "FlapGate": "flap",
            "CloseTime": "close_time",
            "Annotation": "annotation",
            "Shape": "shape",
            "Height": "geom1",
            "Width": "geom2",
        },
    },
    {
        "table_name": "inp_weir",
        "section": "WEIRS",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "Type": "weir_type",
            # "CrestHeigh": "",
            "Qcoeff": "cd2",
            "FlapGate": "flap",
            "EndContrac": "ec",
            # "EndCoeff": "",
            "Surcharge": "surcharge",
            "RoadWidth": "road_width",
            "RoadSurf": "road_surf",
            "CoeffCurve": "curve_id",
            "Annotation": "annotation",
            "Height": "elev",
            "Length": "geom1",
            "SideSlope": "geom3",
        },
    },
    {
        "table_name": "inp_pump",
        "section": "PUMPS",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "PumpCurve": "curve_id",
            "Status": "state",
            "Startup": "startup",
            "Shutoff": "shutoff",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_outfall",
        "section": "OUTFALLS",
        "mapper": {
            "Name": "code",
            "Elevation": "elev",
            "Type": "outfall_type",
            "FixedStage": "stage",
            "Curve_TS": "curve_id",
            "FlapGate": "gate",
            "RouteTo": "routeto",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_divider",
        "section": "DIVIDERS",
        "mapper": {
            "Name": "code",
            "Elevation": "elev",
            "DivertLink": "node_id",
            "Type": "divider_type",
            # "CutoffFlow": "",
            "Curve": "curve_id",
            "WeirMinFlo": "qmin",
            "WeirMaxDep": "qmax",
            "WeirCoeff": "q0",
            "MaxDepth": "ymax",
            "InitDepth": "y0",
            "SurDepth": "ysur",
            "Aponded": "apond",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_storage",
        "section": "STORAGE",
        "mapper": {
            "Name": "code",
            "Elevation": "elev",
            "MaxDepth": "ymax",
            "InitDepth": "y0",
            "Type": "storage_type",
            "Curve": "curve_id",
            "Coeff": "a1",
            "Exponent": "a2",
            "Constant": "a0",
            # "MajorAxis": "",
            # "MinorAxis": "",
            # "SideSlope": "",
            # "SurfHeight": "",
            "SurDepth": "ysur",
            "Fevap": "fevap",
            "Psi": "psi",
            "Ksat": "ksat",
            "IMD": "imd",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_junction",
        "section": "JUNCTIONS",
        "mapper": {
            "Name": "code",
            "Elevation": "elev",
            "MaxDepth": "ymax",
            "InitDepth": "y0",
            "SurDepth": "ysur",
            "Aponded": "apond",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "inp_raingage",
        "section": "RAINGAGE",
        "mapper": {
            "Name": "code",
            "Format": "form_type",
            "Interval": "intvl",
            "SCF": "scf",
            "DataSource": "data_source",
            "SeriesName": "timeseries_id",
            "FileName": "fname",
            "StationID": "sta",
            "RainUnits": "units",
            "Annotation": "annotation",
        },
    },
    {
        "table_name": "cat_curve",
        "section": "CURVES",
        "mapper": {
            "Name": "idval",
            #"Type": 
            "Depth": "xcoord",
            "Area": "ycoord",
            # "Annotation": 
        },
    },
    {
        "table_name": "cat_timeseries_value",
        "section": "TIMESERIES",
        "mapper": {
            "Name": "idval",
            "Date": "date",
            "Time": "time",
            "Value": "value",
            # "File_Name":
        },
    },
    {
        "table_name": "cat_pattern_value",
        "section": "PATTERNS",
        "mapper": {
            "Name": "idval",
            "Time_Stamp": "pattern_type",
            "Factor": "value",
        },
    },
    {
        "table_name": "cat_landuses",
        "section": "LANDUSES",
        "mapper": {
            "Name": "idval",
            "SweepingInterval": "sweepint",
            "SweepingFractionAvailable": "availab",
            # "LastSwept":
            # "Pollutant":
            # "BuildupFunction":
            # "BuildupMax":
            # "BuildupRateConstant":
            # "BuildupExponent_SatConst":
            # "BuilupPerUnit":
            # "WashoffFunction":
            # "WashoffCoefficient":
            # "WashoffExponent":
            # "WashoffCleaninfEfficiency":
            # "WashoffBmpEfficiency":
        },
    },
    {
        "table_name": "inp_dwf",
        "section": "DWF",
        "mapper": {
            "Node": "node_id",
            #"Constituent":
            "Average_Value": "avg_value",
            "Time_Pattern1": "pat1",
            "Time_Pattern2": "pat2",
            "Time_Pattern3": "pat3",
            "Time_Pattern4": "pat4",
        },
    },
    {
        "table_name": "cat_transects",
        "section": "TRANSECTS",
        "mapper": {
            "TransectName": "idval",
            "RoughnessLeftBlank": "text",
            "RoughnessRightBlank": "text",
            "RoughnessChannel": "text",
            "BankStationLeft": "text",
            "BankStationRight": "text",
            "ModifierStations": "text",
            "ModifierElevations": "text",
            "ModifierMeander": "text",
        },
    },
    {
        "table_name": "inp_inflow",
        "section": "INFLOWS",
        "mapper": {
            "Name": "node_id",
            "Constituent": "format",
            "Baseline": "base",
            "Baseline_Pattern": "pattern_id",
            "Time_Series": "timeser_id",
            "Scale_Factor": "sfactor",
            # "Type":
            "Units_Factor": "mfactor",
        },
    },
)


def get_dataframe(data, table_info, columns, epsg):
    mapper = table_info["mapper"]
    df = data.rename(columns=mapper).applymap(null2none)
    gs = gpd.GeoSeries.from_wkt(df["geometry"].apply(qgsgeo2wkt))
    gdf = gpd.GeoDataFrame(df[mapper.values()], geometry=gs, crs=f"EPSG:{epsg}")
    missing_columns = columns - set(gdf.columns)
    for column in missing_columns:
        gdf[column] = None
    return gdf

    # mapper = table_info["mapper"]
    # gdf = None

    # ##TODO: Check this
    # if type(data) not in (dict, list):
    #     print(f"DATA IF  -------------------- {data}")
    #     df = data.rename(columns=mapper).applymap(null2none)
    #     if 'geometry' in df:
    #         gs = gpd.GeoSeries.from_wkt(df["geometry"].apply(qgsgeo2wkt))
    #         gdf = gpd.GeoDataFrame(df[mapper.values()], geometry=gs, crs=f"EPSG:{epsg}")
    #     else:
    #         gdf = df[mapper.values()]
    #     missing_columns = columns - set(gdf.columns)
    #     for column in missing_columns:
    #         gdf[column] = None

    # else:
    #     print(f"DATA ELSE -------------------- {data}")
    #     return
    #     for key in data:
    #         # print(f"KEY -> {key}")
    #         # print(f"data_frame -> {data[key]}")

    #         df = data[key].rename(columns=mapper).applymap(null2none)
    #         if 'geometry' not in df:
    #             return None
    #         gs = gpd.GeoSeries.from_wkt(df["geometry"].apply(qgsgeo2wkt))
    #         gdf = gpd.GeoDataFrame(df[mapper.values()], geometry=gs, crs=f"EPSG:{epsg}")
    #         # gdf["scenario_id"] = scenario_id
    #         missing_columns = columns - set(gdf.columns)
    #         for column in missing_columns:
    #             gdf[column] = None

    # return gdf

def get_dataframes(dicts, columns, epsg):
    dict_all, dict_text_tables = dicts
    dataframes = []
    for table in _tables:
        table_name = table["table_name"]
        section = table["section"]
        if section in dict_text_tables:
            the_dict = dict_text_tables
        elif section in dict_all:
            the_dict = dict_all
        else:
            continue
        data = the_dict[section]["data"]
        if type(data) in (dict, list) or "geometry" not in data.columns:
            continue
        df = get_dataframe(
            the_dict[section]["data"],
            table,
            columns[table_name],
            epsg,
        )
        dataframes.append({"table": table["table_name"], "df": df})
    return dataframes

    # dict_all, dict_text_tables = dicts
    # dataframes = {}

    # for table in _tables:
    #     table_name = table["table_name"]
    #     section = table["section"]

    #     if section in dict_text_tables:
    #         the_dict = dict_text_tables
    #     elif section in dict_all:
    #         the_dict = dict_all
    #     else:
    #         continue

    #     # TODO Handle CURVES section
    #     if section == "CURVES":
    #         continue

    #     df = get_dataframe(
    #         the_dict[section]["data"],
    #         table,
    #         columns[table_name],
    #         epsg,
    #     )

    #     if table_name in dataframes:
    #         print(f"Merging in {section}")
    #         df = df.dropna(how='all', axis='columns')
    #         old_df = dataframes[table_name]["df"].dropna(how='all', axis='columns')
    #         new_df = old_df.merge(df, left_on="code", right_index=True)
    #         missing_columns = columns[table_name] - set(new_df.columns)
    #         for column in missing_columns:
    #             new_df[column] = None
    #         dataframes[table_name]["df"] = new_df
    #     else:
    #         dataframes[table_name] = {"table": table_name, "df": df}
            
    # return dataframes


def null2none(value):
    if hasattr(value, "isNull") and value.isNull():
        return None
    return value


def qgsgeo2wkt(value):
    if not hasattr(value, "asWkt"):
        return None
    # Checks if geometry is "Polygon" and converts to "Multipolygon"
    if value.wkbType() == 3:
        value.convertToMultiType()
    return value.asWkt()


def tables():
    return {table["table_name"] for table in _tables}
