import pandas as pd

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
            "Length": "length",
            "Roughness": "roughness",
            "InOffset": "z1",
            "OutOffset": "z2",
            "InitFlow": "q0",
            "MaxFlow": "qmax",
        },
    },
    {
        "table_name": None,
        "section": "XSECTIONS",
        "mapper": {
            "Shape": "shape",
            "Geom1": "geom1",
            "Geom2": "geom2",
            "Geom3": "geom3",
            "Geom4": "geom4",
            "Barrels": "barrels",
            "Culvert": "culvert",
            "Shp_Trnsct": "descript",
        },
    },
    {
        "table_name": None,
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
            "CurveName": "curve",
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
            "CrestHeigh": "crest_height",
            "Qcoeff": "cd2",
            "FlapGate": "flap",
            "EndContrac": "ec",
            "EndCoeff": "end_coeff",
            "Surcharge": "surcharge",
            "RoadWidth": "road_width",
            "RoadSurf": "road_surf",
            "CoeffCurve": "curve",
            "Annotation": "annotation",
            "Height": "elev",
        },
    },
    {
        "table_name": "inp_pump",
        "section": "PUMPS",
        "mapper": {
            "Name": "code",
            "FromNode": "node_1",
            "ToNode": "node_2",
            "PumpCurve": "curve",
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
            "Curve_TS": "curve",
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
            "DivertLink": "divert_arc",
            "Type": "divider_type",
            # "CutoffFlow": "",
            "Curve": "curve",
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
            "Curve": "curve",
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
        "table_name": "cat_pattern_value",
        "section": "PATTERNS",
        "mapper": {
            "Name": "idval",
            "Time_Stamp": "pattern_type",
            "Factor": "value",
        },
    },
    {
        "table_name": "inp_dwf",
        "section": "DWF",
        "mapper": {
            "Node": "node_id",
            # "Constituent":
            "Average_Value": "avg_value",
            "Time_Pattern1": "pattern1",
            "Time_Pattern2": "pattern2",
            "Time_Pattern3": "pattern3",
            "Time_Pattern4": "pattern4",
        },
    },
    {
        "table_name": "inp_inflow",
        "section": "INFLOWS",
        "mapper": {
            "Name": "node_id",
            "Constituent": "format",
            "Baseline": "base",
            "Baseline_Pattern": "pattern",
            "Time_Series": "timeseries",
            "Scale_Factor": "sfactor",
            "Type": "type",
            "Units_Factor": "mfactor",
        },
    },
)


def get_dataframe(data, table_info, epsg):
    mapper = table_info["mapper"]
    df = data.rename(columns=mapper).applymap(null2none)

    if "geometry" not in df.columns:
        return df

    gs = gpd.GeoSeries.from_wkt(df["geometry"].apply(qgsgeo2wkt))
    gdf = gpd.GeoDataFrame(df[mapper.values()], geometry=gs, crs=f"EPSG:{epsg}")
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


def get_dataframes(inp_dict, epsg):
    dataframes = []

    # Section CURVES
    df = pd.DataFrame(columns=["curve_type", "idval", "xcoord", "ycoord"])
    for curve_type, curve_df in inp_dict["CURVES"].items():
        ct = curve_type.upper()
        curve_df.insert(0, "curve_type", ct)
        curve_df.columns = df.columns
        df = pd.concat([df, curve_df], ignore_index=True)
    curves = df[["idval", "curve_type"]].drop_duplicates()
    curve_values = df[["idval", "xcoord", "ycoord"]].rename(columns={"idval": "curve"})
    dataframes.append({"table": "cat_curve", "df": curves})
    dataframes.append({"table": "cat_curve_value", "df": curve_values})

    # Section TIMESERIES
    df = inp_dict["TIMESERIES"]["data"].rename(
        columns={
            "Name": "idval",
            "Date": "date",
            "Time": "time",
            "Value": "value",
            "File_Name": "fname",
        }
    )
    ts = df[["idval", "fname"]].drop_duplicates()
    ts_values = (
        df[["idval", "date", "time", "value"]]
        .rename(columns={"idval": "timeseries"})
        .dropna(subset=["date", "time"])
    )

    def timeseries_type(timeseries_name):
        sections = [
            ("INFLOWS", "INFLOW HYDROGRAPH"),
            ("ORIFICE", "ORIFICE"),
            ("RAINGAGE", "RAINFALL"),
        ]
        for section, tstype in sections:
            ts_column = []
            if section not in inp_dict:
                continue
            if section == "INFLOWS":
                ts_column = inp_dict[section]["data"]["Direct"]["Time_Series"]
            # TODO: if section == "ORIFICE"
            # TODO: if section == "RAINGAGE"
            if timeseries_name in ts_column.values:
                return tstype
        return "OTHER"

    def time_type(row):
        if not row.fname:
            return "FILE"
        dates = ts_values[ts_values["timeseries"] == row.idval]["date"]
        if (dates == "").all():
            return "RELATIVE"
        return "ABSOLUTE"

    ts["timser_type"] = pd.Series(
        {row.Index: timeseries_type(row.idval) for row in ts.itertuples()}
    )
    ts["times_type"] = pd.Series({row.Index: time_type(row) for row in ts.itertuples()})

    dataframes.append({"table": "cat_timeseries", "df": ts})
    dataframes.append({"table": "cat_timeseries_value", "df": ts_values})

    # Section TRANSECTS
    df = inp_dict["TRANSECTS"]["data"]
    df_sections = inp_dict["TRANSECTS"]["XSections"]

    transects = (
        df[["TransectName"]].drop_duplicates().rename(columns={"TransectName": "idval"})
    )

    tr_value_rows = []
    for row in df.itertuples():
        xsections = df_sections[df_sections["TransectName"] == row.TransectName]

        gr_line = ""
        for pair in xsections.itertuples():
            gr_line += f" {pair.Elevation} {pair.Station} "
        gr_line = gr_line.strip()

        tr_value_rows += [
            {
                "transect": row.TransectName,
                "data_group": "NC",
                "value": (
                    f"{row.RoughnessLeftBank} {row.RoughnessRightBank} "
                    f"{row.RoughnessChannel}"
                ),
            },
            {
                "transect": row.TransectName,
                "data_group": "X1",
                "value": (
                    f"{row.TransectName} {len(xsections)} {row.BankStationLeft} "
                    f"{row.BankStationRight} 0 0 0 {row.ModifierMeander}"
                    f"{row.ModifierStations} {row.ModifierElevations}"
                ),
            },
            {
                "transect": row.TransectName,
                "data_group": "GR",
                "value": gr_line,
            },
        ]

    transect_values = pd.DataFrame(tr_value_rows)
    dataframes.append({"table": "cat_transects", "df": transects})
    dataframes.append({"table": "cat_transects_value", "df": transect_values})

    # Tables that need to be merged before import
    tables_to_merge = {
        "inp_conduit": ("CONDUITS", "XSECTIONS", "LOSSES"),
        "inp_weir": ("WEIRS", "XSECTIONS"),
        "inp_orifice": ("ORIFICES", "XSECTIONS"),
    }

    for table, sections in tables_to_merge.items():
        df = get_merged_df(inp_dict, sections, epsg)

        if table in ("inp_weir", "inp_orifice"):
            # Drop columns 'barrels' and 'culvert' of df if they exist
            if "barrels" in df.columns:
                df.drop("barrels", axis=1, inplace=True)
            if "culvert" in df.columns:
                df.drop("culvert", axis=1, inplace=True)

        if table == "inp_orifice":
            # Drop columns 'geom3' and 'geom4' of df if they exist
            if "geom3" in df.columns:
                df.drop("geom3", axis=1, inplace=True)
            if "geom4" in df.columns:
                df.drop("geom4", axis=1, inplace=True)

        if not df.empty:
            dataframes.append({"table": table, "df": df})

    # Tables in the mapping _tables
    for table in _tables:
        if table["table_name"] in tables_to_merge:
            continue

        if table["table_name"] is None:
            continue

        section = table["section"]

        if section not in inp_dict:
            continue

        data = inp_dict[section]["data"]
        if type(data) in (dict, list):
            # print(section, ":")
            # print(f"{data}")
            continue
        df = get_dataframe(data, table, epsg)
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


def get_merged_df(inp_dict, sections, epsg):
    tables_to_merge = [tb for tb in _tables if tb["section"] in sections]

    merged_df = None

    for table in tables_to_merge:
        section = table["section"]

        if section not in inp_dict:
            continue

        df = get_dataframe(inp_dict[section]["data"], table, epsg)

        if merged_df is None:
            merged_df = df
            continue

        if "code" in merged_df.columns:
            merged_df = merged_df.merge(
                df, how="left", left_on="code", right_index=True
            )
        elif "code" in df.columns:
            merged_df = df.merge(
                merged_df, how="left", left_on="code", right_index=True
            )
        else:
            merged_df = merged_df.merge(
                df, how="outer", left_index=True, right_index=True
            )

    return merged_df


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
