import geopandas as gpd

_tables = (
    {
        "table_name": "inp_conduit",
        "section": "CONDUITS",
        "mapper": {
            "Name": "code",
            "FromNode": "node1",
            "ToNode": "node2",
            "Length": "custom_length",
            "Roughness": "custom_roughness",
            "InOffset": "z1",
            "OutOffset": "z2",
            "InitFlow": "q0",
            "MaxFlow": "qmax",
            "Shape": "shape",
            "Geom1": "geom1",
            "Geom2": "geom2",
            "Geom3": "geom3",
            "Geom4": "geom4",
            "Barrels": "barrels",
            "Culvert": "culvert",
            "Shp_Trnsct": "shape_trnsct",
            "Kentry": "kentry",
            "Kexit": "kexit",
            "Kavg": "kavg",
            "FlapGate": "flap",
            "Seepage": "seepage",
            "Annotation": "annotation",
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
            "Annotation": "annotation",
            "N_Imperv": "nimp",
            "N_Perv": "nperv",
            "S_Imperv": "simp",
            "S_Perv": "sperv",
            "PctZero": "zero",
            "RouteTo": "routeto",
            "PctRouted": "rted",
            "CurveNum": "curveno",
            "Conductiv": "conduct",
            "DryTime": "drytime",
            "InfMethod": "method",
            "SuctHead": "suction",
            "InitDef": "initdef",
            "MaxRate": "maxrate",
            "MinRate": "minrate",
            "Decay": "decay",
            "MaxInf": "maxinfl",
        },
    },
    {
        "table_name": "inp_outlet",
        "section": "OUTLETS",
        "mapper": {
            "Name": "code",
            "FromNode": "node1",
            "ToNode": "node2",
            # "InOffset": "",
            # "RateCurve": "outlet_type",
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
            "FromNode": "node1",
            "ToNode": "node2",
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
            "FromNode": "node1",
            "ToNode": "node2",
            "Type": "weir_type",
            # "CrestHeigh": "",
            # "Qcoeff": "",
            "FlapGate": "flap",
            # "EndContrac": "",
            # "EndCoeff": "",
            "Surcharge": "surcharge",
            "RoadWidth": "road_width",
            "RoadSurf": "road_surf",
            "CoeffCurve": "curve_id",
            "Annotation": "annotation",
            # "Height": "",
            # "Length": "",
            # "SideSlope": "",
            # geom1
            # geom2
            # geom3
            # elev
            # custom_elev
            # cd2
            # ec
        },
    },
    {
        "table_name": "inp_pump",
        "section": "PUMPS",
        "mapper": {
            "Name": "code",
            "FromNode": "node1",
            "ToNode": "node2",
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
            # custom_elev
            # timeser_id
            "Type": "outfall_type",
            "FixedStage": "stage",
            "Curve_TS": "curve_id",
            # "FlapGate": "gate",
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
            # custom_elev
            # node_id
            # "DivertLink": "",
            "Type": "divider_type",
            # "CutoffFlow": "",
            "Curve": "curve_id",
            # "WeirMinFlo": "qmin",
            # "WeirMaxDep": "qmax",
            # "WeirCoeff": "q0",
            # "MaxDepth": "ymax",
            # custom_ymax
            # "InitDepth": "y0",
            # "SurDepth": "ysur",
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
            # custom_elev
            "MaxDepth": "ymax",
            # custom_ymax
            "InitDepth": "y0",
            "Type": "storage_type",
            "Curve": "curve_id",
            # a1
            # a2
            # a0
            # "Coeff": "",
            # "Exponent": "",
            # "Constant": "",
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
            # custom_elev
            "MaxDepth": "ymax",
            # custom_ymax
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
            # rg_id
            # "Format": "form_type",
            "Interval": "intvl",
            "SCF": "scf",
            # "DataSource": "source",
            "SeriesName": "timser_id",
            "FileName": "fname",
            "StationID": "sta",
            "RainUnits": "units",
            "Annotation": "annotation",
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
        df = get_dataframe(the_dict[section]["data"], table, columns[table_name], epsg)
        dataframes.append({"table": table["table_name"], "df": df})
    return dataframes


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
    return (table["table_name"] for table in _tables)
