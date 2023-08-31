import geopandas as gpd

_tables = (
    {
        "table_name": "vi_conduits",
        "section": "CONDUITS",
        "mapper": {
            "Name": "Name",
            "FromNode": "FromNode",
            "ToNode": "ToNode",
            "Length": "Length",
            "Roughness": "Roughness",
            "InOffset": "InOffset",
            "OutOffset": "OutOffset",
            "InitFlow": "InitFlow",
            "MaxFlow": "MaxFlow",
            "Shape": "Shape",
            "Geom1": "Geom1",
            "Geom2": "Geom2",
            "Geom3": "Geom3",
            "Geom4": "Geom4",
            "Barrels": "Barrels",
            "Culvert": "Culvert",
            "Shp_Trnsct": "Shp_Trnsct",
            "Kentry": "Kentry",
            "Kexit": "Kexit",
            "Kavg": "Kavg",
            "FlapGate": "FlapGate",
            "Seepage": "Seepage",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_subcatchments",
        "section": "SUBCATCHMENTS",
        "mapper": {
            "Name": "Name",
            "RainGage": "RainGage",
            "Outlet": "Outlet",
            "Area": "Area",
            "Imperv": "Imperv",
            "Width": "Width",
            "Slope": "Slope",
            "CurbLen": "CurbLen",
            # "SnowPack": "snow_id",
            "Annotation": "Annotation",
            "N_Imperv": "N_Imperv",
            "N_Perv": "N_Perv",
            "S_Imperv": "S_Imperv",
            "S_Perv": "S_Perv",
            "PctZero": "PctZero",
            "RouteTo": "RouteTo",
            "PctRouted": "PctRouted",
            "CurveNum": "CurveNum",
            "Conductiv": "Conductiv",
            "DryTime": "DryTime",
            "InfMethod": "InfMethod",
            "SuctHead": "SuctHead",
            "InitDef": "InitDef",
            "MaxRate": "MaxRate",
            "MinRate": "MinRate",
            "Decay": "Decay",
            "MaxInf": "MaxInf",
        },
    },
    {
        "table_name": "vi_outlets",
        "section": "OUTLETS",
        "mapper": {
            "Name": "Name",
            "FromNode": "FromNode",
            "ToNode": "ToNode",
            "InOffset": "InOffset",
            "RateCurve": "RateCurve",
            "Qcoeff": "Qcoeff",
            "Qexpon": "Qexpon",
            "FlapGate": "FlapGate",
            "CurveName": "CurveName",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_orifices",
        "section": "ORIFICES",
        "mapper": {
            "Name": "Name",
            "FromNode": "FromNode",
            "ToNode": "ToNode",
            "Type": "Type",
            "InOffset": "InOffset",
            "Qcoeff": "Qcoeff",
            "FlapGate": "FlapGate",
            "CloseTime": "CloseTime",
            "Annotation": "Annotation",
            "Shape": "Shape",
            "Height": "Height",
            "Width": "Width",
        },
    },
    {
        "table_name": "vi_weirs",
        "section": "WEIRS",
        "mapper": {
            "Name": "Name",
            "FromNode": "FromNode",
            "ToNode": "ToNode",
            "Type": "Type",
            "CrestHeigh": "InOffset",
            "Qcoeff": "Qcoeff",
            "FlapGate": "FlapGate",
            "EndContrac": "EndContrac",
            # "EndCoeff": "",
            "Surcharge": "Surcharge",
            "RoadWidth": "RoadWidth",
            "RoadSurf": "RoadSurf",
            "CoeffCurve": "CoeffCurve",
            "Annotation": "Annotation",
            "Height": "Height",
            "Length": "Length",
            "SideSlope": "SideSlope",
        },
    },
    {
        "table_name": "vi_pumps",
        "section": "PUMPS",
        "mapper": {
            "Name": "Name",
            "FromNode": "FromNode",
            "ToNode": "ToNode",
            "PumpCurve": "PumpCurve",
            "Status": "Status",
            "Startup": "Startup",
            "Shutoff": "Shutoff",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_outfalls",
        "section": "OUTFALLS",
        "mapper": {
            "Name": "Name",
            "Elevation": "Elevation",
            "Type": "Type",
            "FixedStage": "FixedStage",
            "Curve_TS": "Curve_TS",
            "FlapGate": "FlapGate",
            "RouteTo": "RouteTo",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_dividers",
        "section": "DIVIDERS",
        "mapper": {
            "Name": "Name",
            "Elevation": "Elevation",
            "DivertLink": "DivertLink",
            "Type": "Type",
            # "CutoffFlow": "",
            "Curve": "Curve",
            "WeirMinFlo": "WeirMinFlo",
            "WeirMaxDep": "WeirMaxDep",
            "WeirCoeff": "WeirCoeff",
            "MaxDepth": "MaxDepth",
            "InitDepth": "InitDepth",
            "SurDepth": "SurDepth",
            "Aponded": "Aponded",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_storage",
        "section": "STORAGE",
        "mapper": {
            "Name": "Name",
            "Elevation": "Elevation",
            "MaxDepth": "MaxDepth",
            "InitDepth": "InitDepth",
            "Type": "Type",
            "Curve": "Curve",
            "Coeff": "Coeff",
            "Exponent": "Exponent",
            "Constant": "Constant",
            # "MajorAxis": "",
            # "MinorAxis": "",
            # "SideSlope": "",
            # "SurfHeight": "",
            "SurDepth": "SurDepth",
            "Fevap": "Fevap",
            "Psi": "Psi",
            "Ksat": "Ksat",
            "IMD": "IMD",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_junctions",
        "section": "JUNCTIONS",
        "mapper": {
            "Name": "Name",
            "Elevation": "Elevation",
            "MaxDepth": "MaxDepth",
            "InitDepth": "InitDepth",
            "SurDepth": "SurDepth",
            "Aponded": "Aponded",
            "Annotation": "Annotation",
        },
    },
    {
        "table_name": "vi_raingages",
        "section": "RAINGAGE",
        "mapper": {
            "Name": "Name",
            "Format": "Format",
            "Interval": "Interval",
            "SCF": "SCF",
            "DataSource": "DataSource",
            "SeriesName": "SeriesName",
            "FileName": "FileName",
            "StationID": "StationID",
            "RainUnits": "RainUnits",
            "Annotation": "Annotation",
        },
    },
)


def get_dataframe(data, sector_id, scenario_id, table_info, columns, epsg):
    mapper = table_info["mapper"]
    df = data.rename(columns=mapper).applymap(null2none)
    gs = gpd.GeoSeries.from_wkt(df["geometry"].apply(qgsgeo2wkt))
    gdf = gpd.GeoDataFrame(df[mapper.values()], geometry=gs, crs=f"EPSG:{epsg}")
    gdf["sector_id"] = sector_id
    gdf["scenario_id"] = scenario_id
    missing_columns = columns - set(gdf.columns)
    for column in missing_columns:
        gdf[column] = None
    return gdf


def get_dataframes(dicts, sector_id, scenario_id, columns, epsg):
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
        df = get_dataframe(
            the_dict[section]["data"],
            sector_id,
            scenario_id,
            table,
            columns[table_name],
            epsg,
        )
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
