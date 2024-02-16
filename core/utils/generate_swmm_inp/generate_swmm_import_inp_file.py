# TODO: include attribuition to https://github.com/Jannik-Schilling/generate_swmm_inp/blob/main/generate_swmm_import_inp_file.py

import itertools
import numpy as np
import pandas as pd
from .g_s_defaults import (
    curve_cols_dict,
    def_sections_dict,
    def_sections_geoms_dict,
    def_tables_dict,
    pattern_times,
)
from .g_s_import_helpers import (
    adjust_column_types,
    adjust_line_length,
    build_df_for_section,
    build_df_from_vals_list,
    del_kw_from_list,
    extract_sections_from_text,
    insert_nan_after_kw,
    sect_list_import_handler,
)
from .g_s_links import get_inlet_from_inp
from .g_s_nodes import get_hydrogrphs
from .g_s_options import convert_options_format_for_import


def inp2dict(readfile, feedback):
    import_parameters_dict = {}

    # reading input text file
    feedback.setProgressText("reading inp ...")
    feedback.setProgress(3)
    encodings = ["utf-8", "windows-1250", "windows-1252"]  # add more
    for e in encodings:
        if feedback.isCanceled():
            return
        try:
            with open(readfile, "r", encoding=e) as f:
                inp_text = f.readlines()
        except UnicodeDecodeError:
            feedback.setProgressText(
                "got unicode error with %s , trying different encoding" % e
            )
        else:
            feedback.setProgressText("opening the file with encoding:  %s " % e)
            break

    # delete unused lines
    inp_text = [x for x in inp_text if x != "\n"]
    inp_text = [x for x in inp_text if x != "\r"]
    inp_text = [x for x in inp_text if not x.startswith(";;")]
    inp_text = [x.replace("\n", "") for x in inp_text]
    inp_text = [x.strip() for x in inp_text]

    # SWMM sections in the text file
    inp_text_sections = [i for i in inp_text if i.startswith("[") and i.endswith("]")]
    pos_start_list = [inp_text.index(sect) for sect in inp_text_sections]
    pos_end_list = pos_start_list[1:] + [len(inp_text)]

    # make a dict of sections to extract
    dict_search = {
        s[1:-1].upper(): [pos_start_list[i], pos_end_list[i]]
        for i, s in enumerate(inp_text_sections)
        if s[1:-1].upper() in def_sections_dict.keys()
    }

    # sections which are not available
    unknown_sections = [
        s for s in inp_text_sections if not s[1:-1].upper() in def_sections_dict.keys()
    ]
    if len(unknown_sections) > 0:
        feedback.pushWarning(
            "Warning: unknown sections in input file: "
            + (" ,").join(unknown_sections)
            + "These sections will be ignored"
        )

    if feedback.isCanceled():
        return

    # dict for raw values for every section
    dict_all_vals = {
        k: extract_sections_from_text(inp_text, dict_search[k], k)
        for k in dict_search.keys()
    }

    # sections which will be converted into tables
    # --------------------------------------------
    dict_res_table = {}

    # options section
    if "OPTIONS" in dict_all_vals.keys():
        section_name = "OPTIONS"
        feedback.setProgressText('Preparing section "' + section_name + '"')
        feedback.setProgress(5)

        df_options = build_df_for_section("OPTIONS", dict_all_vals)
        df_options_converted = convert_options_format_for_import(
            df_options, import_parameters_dict, feedback
        )
        # dict_res_table["OPTIONS"] = {"OPTIONS": df_options_converted}
        dict_res_table["OPTIONS"] = {"data": df_options_converted}

    if feedback.isCanceled():
        return

    # inflows section
    section_name = "INFLOWS"
    feedback.setProgressText('Preparing section "' + section_name + '"')
    feedback.setProgress(8)
    if "INFLOWS" in dict_all_vals.keys():
        df_inflows = build_df_for_section("INFLOWS", dict_all_vals)
    else:
        df_inflows = build_df_from_vals_list([], def_sections_dict["INFLOWS"])
    if "DWF" in dict_all_vals.keys():
        df_dry_weather = build_df_for_section("DWF", dict_all_vals)
    else:
        df_dry_weather = build_df_from_vals_list([], def_sections_dict["DWF"])
    if "HYDROGRAPHS" in dict_all_vals.keys():
        df_hydrographs_raw = build_df_for_section("HYDROGRAPHS", dict_all_vals)
        hg_name_list = np.unique(df_hydrographs_raw["Name"])
        df_hydrographs = pd.DataFrame()
        for hg_name in hg_name_list:
            df_hydrographs = pd.concat([df_hydrographs, get_hydrogrphs(hg_name)])
        df_hydrographs = df_hydrographs.reset_index(drop=True)
    else:
        df_hydrographs = build_df_from_vals_list(
            [], list(def_tables_dict["INFLOWS"]["tables"]["Hydrographs"].keys())
        )
    if "RDII" in dict_all_vals.keys():
        df_rdii = build_df_for_section("RDII", dict_all_vals)
    else:
        df_rdii = build_df_from_vals_list([], def_sections_dict["RDII"])
    dict_inflows = {
        "Direct": df_inflows,
        "Dry_Weather": df_dry_weather,
        "Hydrographs": df_hydrographs,
        "RDII": df_rdii,
    }
    # dict_res_table["INFLOWS"] = dict_inflows
    dict_res_table["INFLOWS"] = {"data": dict_inflows}

    pattern_types = list(def_tables_dict["PATTERNS"]["tables"].keys())
    pattern_cols = {
        k: list(v.keys()) for k, v in def_tables_dict["PATTERNS"]["tables"].items()
    }

    if feedback.isCanceled():
        return

    if "PATTERNS" in dict_all_vals.keys():
        section_name = "PATTERNS"
        feedback.setProgressText('Preparing section "' + section_name + '"')
        feedback.setProgress(12)
        all_patterns = build_df_for_section("PATTERNS", dict_all_vals)
        if len(all_patterns) == 0:
            all_patterns = dict()
        else:
            occuring_patterns_types = all_patterns.loc[
                all_patterns[1].isin(pattern_types), [0, 1]
            ].set_index(0)
            occuring_patterns_types.columns = ["PatternType"]
            all_patterns = all_patterns.fillna(np.nan)
            all_patterns = all_patterns.replace(
                {
                    "HOURLY": np.nan,
                    "DAILY": np.nan,
                    "MONTHLY": np.nan,
                    "WEEKEND": np.nan,
                }
            )

            def adjust_patterns_df(pattern_row):
                """
                reorders a list of the patterns section for the input file
                :param list pattern_row
                :return: pd.DataFrame
                """
                pattern_adjusted = [
                    [pattern_row[0], i] for i in pattern_row[1:] if pd.notna(i)
                ]
                return pd.DataFrame(pattern_adjusted, columns=["Name", "Factor"])

            all_patterns = pd.concat(
                [adjust_patterns_df(all_patterns.loc[i, :]) for i in all_patterns.index]
            )
            all_patterns = all_patterns.join(occuring_patterns_types, on="Name")
            all_patterns = {
                "data": v.iloc[:, :-1] for k, v in all_patterns.groupby("PatternType")
            }
    else:
        all_patterns = dict()

    def add_pattern_timesteps(pattern_type):
        """
        adds time strings from the pattern_times dict
        :param str pattern_row
        :return: list
        """
        timesteps = itertools.cycle(pattern_times[pattern_type])
        new_col = [next(timesteps) for _ in range(len(all_patterns[pattern_type]))]
        return new_col

    for pattern_type in pattern_cols.keys():
        if pattern_type in all_patterns.keys():
            all_patterns[pattern_type]["Time"] = add_pattern_timesteps(pattern_type)
            all_patterns[pattern_type] = all_patterns[pattern_type][
                ["Name", "Time", "Factor"]
            ]
            if pattern_type == "DAILY":
                all_patterns[pattern_type] = all_patterns[pattern_type].rename(
                    {"Time": "Day"}
                )
            if pattern_type == "MONTHLY":
                all_patterns[pattern_type] = all_patterns[pattern_type].rename(
                    {"Time": "Month"}
                )
            all_patterns[pattern_type]["Factor"] = [
                float(x) for x in all_patterns[pattern_type]["Factor"]
            ]
            all_patterns[pattern_type].columns = pattern_cols[pattern_type]
        else:
            all_patterns[pattern_type] = build_df_from_vals_list(
                [], pattern_cols[pattern_type]
            )
    # dict_res_table["PATTERNS"] = all_patterns
    dict_res_table["PATTERNS"] = {"data": all_patterns}

    if feedback.isCanceled():
        return

    # curves section
    if "CURVES" in dict_all_vals.keys():
        section_name = "CURVES"
        feedback.setProgressText('Preparing section "' + section_name + '"')
        feedback.setProgress(16)
        curve_type_dict = {
            x[0]: x[1]
            for x in dict_all_vals["CURVES"]["data"]
            if x[1].capitalize() in curve_cols_dict.keys()
        }
        occuring_curve_types = list(set(curve_type_dict.values()))
        all_curves = [
            del_kw_from_list(x, occuring_curve_types, 1)
            for x in dict_all_vals["CURVES"]["data"].copy()
        ]
        all_curves = build_df_from_vals_list(all_curves, def_sections_dict["CURVES"])
        all_curves["CurveType"] = [
            curve_type_dict[i].capitalize() for i in all_curves["Name"]
        ]  # capitalize as in curve_cols_dict
        all_curves["XVal"] = [float(x) for x in all_curves["XVal"]]
        all_curves["YVal"] = [float(x) for x in all_curves["YVal"]]
        all_curves = {
            k: v[["Name", "XVal", "YVal"]] for k, v in all_curves.groupby("CurveType")
        }
    else:
        all_curves = dict()
    for curve_type in curve_cols_dict.keys():
        if curve_type in all_curves.keys():
            all_curves[curve_type].columns = curve_cols_dict[curve_type]
        else:
            all_curves[curve_type] = build_df_from_vals_list(
                [], curve_cols_dict[curve_type]
            )

    dict_res_table["CURVES"] = all_curves

    if feedback.isCanceled():
        return

    # quality section
    feedback.setProgressText("Preparing QUALITY parameters")
    feedback.setProgress(20)
    quality_cols_dict = {
        k: def_sections_dict[k]
        for k in [
            "POLLUTANTS",
            "LANDUSES",
            "COVERAGES",
            "LOADINGS",
            "BUILDUP",
            "WASHOFF",
        ]
    }
    all_quality = {
        k: build_df_for_section(k, dict_all_vals) for k in quality_cols_dict.keys()
    }
    if (
        len(all_quality["BUILDUP"]) == 0
    ):  # fill with np.nan in order to facilitate join below
        if len(all_quality["LANDUSES"]) > 0:
            landuse_names = all_quality["LANDUSES"]["Name"]
            landuse_count = len(landuse_names)
            all_quality["BUILDUP"].loc[0:landuse_count, :] = np.nan
            all_quality["BUILDUP"]["Name"] = landuse_names
    landuses = (
        all_quality["BUILDUP"]
        .copy()
        .join(all_quality["LANDUSES"].copy().set_index("Name"), on="Name")
    )
    col_names = all_quality["LANDUSES"].columns.tolist()
    col_names.extend(all_quality["BUILDUP"].columns.tolist()[1:])
    landuses = landuses[col_names]
    landuses["join_name"] = landuses["Name"] + landuses["Pollutant"]
    all_quality["WASHOFF"]["join_name"] = (
        all_quality["WASHOFF"]["Name"] + all_quality["WASHOFF"]["Pollutant"]
    )
    all_quality["WASHOFF"] = all_quality["WASHOFF"].drop(columns=["Name", "Pollutant"])
    landuses = landuses.join(
        all_quality["WASHOFF"].set_index("join_name"), on="join_name"
    )
    landuses = landuses.drop(columns=["join_name"])
    all_quality["LANDUSES"] = landuses
    del all_quality["BUILDUP"]
    del all_quality["WASHOFF"]
    all_quality = {
        # k: adjust_column_types(v, def_tables_dict["QUALITY"]["tables"][k])
        "data": adjust_column_types(v, def_tables_dict["QUALITY"]["tables"][k])
        for k, v in all_quality.items()
    }
    dict_res_table["QUALITY"] = all_quality

    # timeseries section
    ts_cols_dict = def_tables_dict["TIMESERIES"]["tables"]["TIMESERIES"]
    if "TIMESERIES" in dict_all_vals.keys():
        all_time_series = [
            adjust_line_length(x, 1, 4)
            for x in dict_all_vals["TIMESERIES"]["data"].copy()
        ]
        # for external File
        all_time_series = [
            insert_nan_after_kw(x, 2, "FILE", [3, 4]) for x in all_time_series
        ]
        all_time_series = [del_kw_from_list(x, "FILE", 2) for x in all_time_series]
        all_time_series = build_df_from_vals_list(
            all_time_series, def_sections_dict["TIMESERIES"]
        )
    else:
        all_time_series = build_df_from_vals_list([], list(ts_cols_dict.keys()))
    # all_time_series = all_time_series.fillna('')
    all_time_series = adjust_column_types(all_time_series, ts_cols_dict)
    # dict_res_table["TIMESERIES"] = {"TIMESERIES": all_time_series}
    dict_res_table["TIMESERIES"] = {"data": all_time_series}

    if feedback.isCanceled():
        return

    # streets and inlets section
    if "STREETS" in dict_all_vals.keys() or "INLETS" in dict_all_vals.keys():
        section_name = "STREETS"
        feedback.setProgressText('Preparing section "' + section_name + '"')
        feedback.setProgress(25)
        street_data = {}
        street_data["STREETS"] = build_df_for_section("STREETS", dict_all_vals)
        if "INLETS" in dict_all_vals.keys():
            inl_list = [
                get_inlet_from_inp(inl_line)
                for inl_line in dict_all_vals["INLETS"]["data"]
            ]
            street_data["INLETS"] = build_df_from_vals_list(
                inl_list, def_sections_dict["INLETS"]
            )
        else:
            street_data["INLETS"] = build_df_for_section("INLETS", dict_all_vals)
        street_data["INLET_USAGE"] = build_df_for_section("INLET_USAGE", dict_all_vals)
        dict_res_table["STREETS"] = street_data

    if feedback.isCanceled():
        return

    # transects in hec2 format
    if "TRANSECTS" in dict_all_vals.keys():
        feedback.setProgress(1)
        transects_columns = [
            "TransectName",
            "RoughnessLeftBank",
            "RoughnessRightBank",
            "RoughnessChannel",
            "BankStationLeft",
            "BankStationRight",
            "ModifierMeander",
            "ModifierStations",
            "ModifierElevations",
        ]
        section_name = "TRANSECTS"
        feedback.setProgressText('Preparing section "' + section_name + '"')
        transects_list = dict_all_vals["TRANSECTS"]["data"].copy()
        tr_startp = [i for i, x in enumerate(transects_list) if x[0] == "NC"]
        n_trans = len(tr_startp)
        tr_endp = tr_startp[1:] + [len(transects_list)]

        def get_transects_data2(tr_i):
            tr_roughness = [float(x) for x in tr_i[0][1:]]
            tr_name = tr_i[1][1]
            tr_count = tr_i[1][2]
            tr_bankstat_left = float(tr_i[1][3])
            tr_bankstat_right = float(tr_i[1][4])
            tr_modifier = [float(x) for x in tr_i[1][7:10]]
            tr_data = (
                [tr_name]
                + tr_roughness
                + [tr_bankstat_left]
                + [tr_bankstat_right]
                + tr_modifier
            )
            tr_values = [del_kw_from_list(x, "GR", 0) for x in tr_i[2:]]
            tr_values = [x for sublist in tr_values for x in sublist]
            tr_values_splitted = [
                [
                    tr_name,
                    float(tr_values[x * 2]),  # split into list of lists of len 2
                    float(tr_values[(x * 2) + 1]),
                ]
                for x in range(int(tr_count))
            ]
            return tr_values_splitted, tr_data

        all_tr_vals = []
        all_tr_dats = []
        for i, x in enumerate(zip(tr_startp, tr_endp)):
            if feedback.isCanceled():
                return
            val, dat = get_transects_data2(transects_list[x[0] : x[1]])
            all_tr_vals = all_tr_vals + val
            all_tr_dats = all_tr_dats + [dat]
            feedback.setProgress(((i + 1) / n_trans) * 90)

        all_tr_vals_df = build_df_from_vals_list(
            all_tr_vals, ["TransectName", "Elevation", "Station"]
        )
        feedback.setProgress(92)
        all_tr_vals_df = all_tr_vals_df[
            ["TransectName", "Station", "Elevation"]
        ]  # order of columns according to swmm interface
        feedback.setProgress(93)
        all_tr_dats_df = build_df_from_vals_list(all_tr_dats, transects_columns)
        feedback.setProgress(94)
        all_tr_dats_df = all_tr_dats_df[
            [
                "TransectName",
                "RoughnessLeftBank",
                "RoughnessRightBank",
                "RoughnessChannel",
                "BankStationLeft",
                "BankStationRight",
                "ModifierStations",
                "ModifierElevations",
                "ModifierMeander",
            ]
        ]  # order of columns according to swmm interface
        # transects_dict = {"Data": all_tr_dats_df, "XSections": all_tr_vals_df}
        transects_dict = {"data": all_tr_dats_df, "XSections": all_tr_vals_df}
        feedback.setProgress(95)
        dict_res_table["TRANSECTS"] = transects_dict
        feedback.setProgress(100)

    if feedback.isCanceled():
        return

    # prepare sections with geometries
    feedback.setProgress(0)
    for section_name in def_sections_geoms_dict.keys():
        if section_name in dict_all_vals.keys():
            sect_list_import_handler(
                section_name, dict_all_vals, "geodata", feedback, import_parameters_dict
            )
        if feedback.isCanceled():
            return

    inp_dict = {}

    for key in dict_all_vals:
        inp_dict[key] = (
            dict_res_table[key] if key in dict_res_table else dict_all_vals[key]
        )

    return inp_dict
