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
            "Barrels": "barrels",
            "Culvert": "culvert",
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
