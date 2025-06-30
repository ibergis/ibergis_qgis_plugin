"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

@author: Esteban Sanudo

"""
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

import pandas as pd

from swmm_api import __version__ as swmm_api_version
from swmm_api import read_inp_file
from swmm_api import read_out_file
from swmm_api import out2frame

from swmm_api.input_file.macros.collection import nodes_dict, links_dict
from swmm_api.input_file.macros.graph import get_path_subgraph, links_connected
from swmm_api.input_file.sections import Outfall, Junction, Storage, Conduit, Weir, Orifice
from swmm_api.output_file import OBJECTS, VARIABLES

# import imageio.v2 as imageio
import os
import sys

class COLS:
    INVERT_ELEV = 'SOK'
    IN_OFFSET = 'IN_OFF'
    OUT_OFFSET = 'OUT_OFF'
    CROWN_ELEV_IN = 'BUK_IN'
    CROWN_ELEV_OFF = 'BUK_OFF'
    GROUND_ELEV = 'GOK'  # rim elevation
    STATION = 'x'
    WATER = 'water'
    FLOODING ='flooding'
    LABEL = 'label'

def get_longitudinal_data(inp, start_node, end_node, timestamp, offsets, out=None, zero_node=None, depth_agg_func=None):

    sub_list, sub_graph = get_path_subgraph(inp, start=start_node, end=end_node)

    if zero_node is None:
        zero_node = start_node

    keys = [COLS.STATION, COLS.IN_OFFSET, COLS.OUT_OFFSET, COLS.INVERT_ELEV, COLS.CROWN_ELEV_IN, COLS.CROWN_ELEV_OFF, COLS.GROUND_ELEV, COLS.WATER, COLS.FLOODING, COLS.LABEL]

    res = {k: [] for k in keys}

    def _update_res(*args):
        for k, v in zip(keys, args):
            res[k].append(v)

    # ---------------
    nodes = nodes_dict(inp)
    # ---------------
    profile_height = 0
    in_off = 0
    out_off = 0
    # ---------------
    nodes_depth = None
    nodes_flood = None
    if out is not None:
        if depth_agg_func is None:
            depth_agg_func = lambda s: s.mean()
        nodes_depth = depth_agg_func(out.get_part(OBJECTS.NODE, sub_list, VARIABLES.NODE.DEPTH)).to_dict() #Esto me da los máximos.
        nodes_depth_dic = out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.DEPTH).to_dict()
        nodes_flooding = depth_agg_func(out.get_part(OBJECTS.NODE, sub_list, VARIABLES.NODE.FLOODING)).to_dict()
        nodes_flooding_dic = out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.FLOODING).to_dict()
    # ---------------
    stations_ = list(iter_over_inp_(inp, sub_list, sub_graph))
    stations = dict(stations_)

    for node, x in stations_:
        n = nodes[node]  # type: swmm_api.input_file.sections.node._Node
        sok = n.elevation
        # ---------------
        gok = sok
        if isinstance(n, Outfall):
            gok += profile_height
        elif isinstance(n, (Storage, Junction)):
            gok += n.depth_max

        if nodes_depth_dic is not None:
            node_depth = nodes_depth_dic[node]
            node_flooding = nodes_flooding_dic[node]
            if timestamp in node_depth:
                water = sok + node_depth[timestamp]
                flooding = node_flooding[timestamp]
            else:
                water = None  # O algún valor predeterminado en caso de que falte el timestamp
                floooding = None  # O algún valor predeterminado en caso de que falte el timestamp
        else:
            water = None
            floooding = None

        # Obtiene las conducciones (Conduit, Weir, Orifice, etc.) conectadas al nodo
        prior_conduit, following_conduit = links_connected(inp, node, sub_graph)

        if prior_conduit:
            prior_conduit = prior_conduit[0]
            if prior_conduit.name in inp.XSECTIONS:
                profile_height = inp.XSECTIONS[prior_conduit.name].height
            else:
                profile_height = 0

            #sok_ = sok
            if isinstance(prior_conduit, Weir):
                pass
            elif isinstance(prior_conduit, Orifice):
                pass
            elif isinstance(prior_conduit, Conduit):
                if offsets == 0:
                    in_off = sok + prior_conduit.offset_downstream
                elif offsets == 1:
                    in_off = prior_conduit.offset_downstream
                    # print(f"Offsets down {following_conduit.offset_downstream}")
        else:
            in_off = sok


        buk_in = profile_height + in_off
            # _update_res(x - stations[zero_node], sok, in_off, out_off, buk, gok, water, node)

        if following_conduit:
            following_conduit = following_conduit[0]
            if following_conduit.name in inp.XSECTIONS:
                profile_height = inp.XSECTIONS[following_conduit.name].height
            else:
                profile_height = 0

            #sok_ = sok
            if isinstance(following_conduit, Weir):
                out_off = following_conduit.height_crest
            elif isinstance(following_conduit, Orifice):
                out_off = sok + following_conduit.offset
            elif isinstance(following_conduit, Conduit):
                if offsets == 0:
                    out_off = sok + following_conduit.offset_upstream
                if offsets == 1:
                    out_off = following_conduit.offset_upstream
                    # print(f"Offsets ups {following_conduit.offset_upstream}")

            buk_off = profile_height + out_off

        _update_res(x - stations[zero_node], in_off, out_off, sok, buk_in, buk_off, gok, water, flooding, node)


        # print(res)
    return res  # Devuelve el diccionario con los datos longitudinales


def iter_over_inp_(inp, sub_list, sub_graph):
    links = links_dict(inp)

    x = 0
    for node in sub_list:
        yield node, x
        # ------------------
        out_edges = list(sub_graph.out_edges(node))
        if out_edges:
            following_link_label = sub_graph.get_edge_data(*out_edges[0])['label']
            if isinstance(following_link_label, list):
                following_link_label = following_link_label[0]
            following_link = links[following_link_label]
            if isinstance(following_link, Conduit):
                x += following_link.length


def iter_over_inp(inp, start_node, end_node):
    sub_list, sub_graph = get_path_subgraph(inp, start=start_node, end=end_node)
    return iter_over_inp_(inp, sub_list, sub_graph)


def get_node_station(inp, start_node, end_node, zero_node=None):
    stations = dict(iter_over_inp(inp, start_node, end_node))
    if zero_node:
        return set_zero_node(stations, zero_node)
    return stations


def set_zero_node(stations, zero_node):
    return {node: stations[node] - stations[zero_node] for node in stations}

def interpolate_x_at_intersection(x1, y1a, x2, y2a, y1b, y2b):
    """
    Devuelve el punto x donde las dos líneas se cruzan.
    Línea A: (x1, y1a)-(x2, y2a)
    Línea B: (x1, y1b)-(x2, y2b)
    """
    dy_a = y2a - y1a
    dy_b = y2b - y1b
    dy = (y1b - y1a)  # diferencia inicial

    # Evitamos división por cero
    if dy_a == dy_b:
        return None  # líneas paralelas

    frac = dy / (dy_a - dy_b)
    x_int = x1 + frac * (x2 - x1)
    y_int = y1a + frac * (y2a - y1a)
    return x_int, y_int


def plot_longitudinal(inp, start_node, end_node, c_inv, c_ground_line, c_crown, c_ground, c_water, c_pipe, lw, mh_width, timestamp, offset_ymax,
                      offsets, out=None, ax=None, zero_node=None, depth_agg_func=None, add_node_labels=False):

    res = get_longitudinal_data(inp, start_node, end_node, timestamp, offsets, out, zero_node=zero_node, depth_agg_func=depth_agg_func)

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    ax.plot(res[COLS.STATION], res[COLS.GROUND_ELEV], c=c_ground_line, lw=lw)

    for i in range(len(res[COLS.STATION]) - 1):

        x = res[COLS.STATION][i]
        invert_elev = res[COLS.INVERT_ELEV][i]
        ground_elev = res[COLS.GROUND_ELEV][i]
        water_elev = res[COLS.WATER][i]
        node_name = res[COLS.LABEL][i]  # Obtener el nombre del nodo
        node_type = out.model_properties[OBJECTS.NODE].get(node_name, {}).get("type")  # Acceder al tipo

        x1 = res[COLS.STATION][i]
        x2 = res[COLS.STATION][i + 1]

        diameter = res[COLS.CROWN_ELEV_OFF][i]-res[COLS.OUT_OFFSET][i]

        # Fondo del conducto
        y1_down = res[COLS.OUT_OFFSET][i]
        y2_down = res[COLS.IN_OFFSET][i + 1]
        ax.plot([x1, x2], [y1_down, y2_down], c="black", lw=lw, zorder=12)

        # Cima del conducto
        y1_top = res[COLS.CROWN_ELEV_OFF][i]
        y2_top = res[COLS.CROWN_ELEV_IN][i + 1]
        ax.plot([x1, x2], [y1_top, y2_top], c="black", lw=lw, zorder=12)

        # Elevación del agua (recortada al conducto)
        water_elev_up = res[COLS.WATER][i]
        water_elev_down = res[COLS.WATER][i+1]
        if water_elev_up <= y1_down:
            water_elev_up = y1_down
        if water_elev_down <= y2_down:
            water_elev_down = y2_down
        if water_elev_up >= y1_top:
            water_elev_up = y1_top
        if water_elev_down >= y2_top:
            water_elev_down = y2_top

        y1_w = water_elev_up
        y2_w = water_elev_down


        # Línea de agua
        ax.plot([x1, x2], [y1_w, y2_w], c=c_water, lw=lw)

        # Línea de energia
        if res[COLS.WATER][i] >= y1_top or res[COLS.WATER][i+1] >= y2_top:
            y1_energy = res[COLS.WATER][i]
            y2_energy = res[COLS.WATER][i+1]
            ax.plot([x1, x2], [y1_energy, y2_energy], c=c_water, lw=lw)


            # ¿Se cruzan?
            cross = (y1_energy - y1_top) * (y2_energy - y2_top) < 0

            if cross:
                # Sí se cruzan encontrar punto de intersección
                x_int, y_int = interpolate_x_at_intersection(
                    x1, y1_energy, x2, y2_energy, y1_top, y2_top
                )

                # Subtramo izquierdo
                if y1_energy > y1_top:
                    ax.fill_between([x1, x_int], [y1_down, y_int-diameter], [y1_top, y_int], color=c_water, alpha=1, zorder =10)
                else:
                    ax.fill_between([x1, x_int], [y1_down, y_int-diameter], [y1_energy, y_int], color=c_water, alpha=1, zorder =10)
                    #Revisar

                # Subtramo derecho
                if y2_energy < y2_top:
                    ax.fill_between([x_int, x2], [y_int-diameter, y2_energy], [y_int, y2_energy], color=c_water, alpha=1, zorder =10)
                else:
                    ax.fill_between([x_int, x2], [y_int, y2_down], [y_int, y2_top], color=c_water, alpha=1, zorder =10)
                    #Revisar

        # Relleno entre el nivel del agua y el fondo de la tubería
        ax.fill_between([x1, x2], [y1_down, y2_down], [y1_top, y2_top], color=c_pipe, alpha=1)
        ax.fill_between([x1, x2], [y1_w, y2_w], [y1_down, y2_down], color=c_water, alpha=1)

        bottom = ax.get_ylim()[0]

    # Dibuja pozos de registro en todos los nodos
    for i in range(len(res[COLS.STATION])):
        x = res[COLS.STATION][i]
        invert_elev = res[COLS.INVERT_ELEV][i]
        ground_elev = res[COLS.GROUND_ELEV][i]
        water_elev = res[COLS.WATER][i]
        node_name = res[COLS.LABEL][i]
        node_type = out.model_properties[OBJECTS.NODE].get(node_name, {}).get("type")
        io_flooding = res[COLS.FLOODING][i]

        altura_total = ground_elev - invert_elev

        if node_type != "OUTFALL":
            rect = plt.Rectangle((x - mh_width/2, invert_elev), mh_width, altura_total,
                                 edgecolor='black', facecolor=c_pipe, lw=lw, alpha=1, zorder=14)
            ax.add_patch(rect)

            rect_water = plt.Rectangle((x - mh_width/2, invert_elev), mh_width, water_elev - invert_elev,
                                       edgecolor='black', facecolor=c_water, alpha=1, zorder=14)
            ax.add_patch(rect_water)

            # Añadir el texto del valor io_flooding centrado en la parte superior del pozo
            ax.text(x, ground_elev + 0.1, f"{io_flooding:.2f}",  # Ajusta el +0.1 según la escala de tu eje y
                    ha='center', va='bottom', fontsize=8, rotation=0, color='red', zorder=15)


    ax.fill_between(res[COLS.STATION], bottom, res[COLS.GROUND_ELEV], color=c_ground, alpha=0.9, zorder=0)


    ax.set_xlim(res[COLS.STATION][0], res[COLS.STATION][-1])
    ax.set_ylim(bottom=bottom, top = (max(res[COLS.GROUND_ELEV]) + offset_ymax))

    secax = ax.secondary_xaxis('top')
    secax.set_xticks(res[COLS.STATION], minor=False)
    secax.set_xticklabels(res[COLS.LABEL], rotation=90, minor=False)
    secax.grid(axis='x', ls=':', color='grey', which='major')

    ax.set_title(f"Start node: {start_node}, End node: {end_node}\nTimestamp: {timestamp}")

    for x in res[COLS.STATION]:
        ax.axvline(x, color='black', linestyle=':', linewidth=1, zorder=15)
    return fig, ax

    fig.show()

def create_gif(start_node, end_node, write_time_step, out, custom_start, custom_end, fps=10):
    # Establece los parámetros
    timestamp_range = pd.date_range(start=custom_start, end=custom_end, freq=write_time_step)

    images = []
    temp_files = []  # Lista para almacenar nombres de archivos temporales
    save_path = r"C:\python_scripts\animation.gif"

    for timestamp in timestamp_range:
        # Genera el gráfico para cada timestamp
        fig, ax = plot_longitudinal(
            inp, start_node, end_node, c_inv, c_ground_line, c_crown, c_ground, c_water, c_pipe, lw, mh_width, timestamp, offset_ymax,
            offsets, out=out, depth_agg_func=lambda x: x.max(), add_node_labels=False
        )

        # Convierte el timestamp a un formato seguro para nombres de archivo
        safe_timestamp = timestamp.strftime("%Y%m%d_%H%M%S")
        temp_path = f"temp_{safe_timestamp}.png"
        print(temp_path)

        # Ajusta el layout antes de guardar
        fig.tight_layout()

        # Guarda la imagen y almacena el nombre
        fig.savefig(temp_path)
        temp_files.append(temp_path)
        plt.show()
        plt.close(fig)

    # Cargar las imágenes correctamente
    # for temp_path in temp_files:
    #     images.append(imageio.imread(temp_path))  # Lee las imágenes correctamente

    # # Guarda todas las imágenes como un GIF
    # imageio.mimsave(save_path, images, fps=fps)

    # # Elimina las imágenes temporales correctamente
    # for temp_path in temp_files:
    #     os.remove(temp_path)

    # print(f"GIF guardado en: {save_path}")


# # INICIO PROGRAMA

# # Definir la ruta de los ficheros
# inputfile   = r"E:\Test1_street-scale_B.SurchagedConditions_IberPlus_HR.gid\Iber_SWMM.inp"
# inifile     = r"E:\Test1_street-scale_B.SurchagedConditions_IberPlus_HR.gid\Iber_SWMM.ini"
# outputfile  = r"E:\Test1_street-scale_B.SurchagedConditions_IberPlus_HR.gid\Iber_SWMM.out"

# # Cargar la simulación
# inp = read_inp_file(inputfile)
# out = read_out_file(outputfile)

# res_out = out.to_frame()

# # Versiones de SWMM API y librería de SWMM. Informativo.
# print(f'SWMM API version - {swmm_api_version}')
# swmm_version = out.swmm_version
# print(f'SWMM version - {swmm_version}')

# # Dataframe con todos los resultados
# # db_out = out2frame(outputfile)

# # Parámetros temporales
# write_time_step = out.report_interval
# start_date = out.start_date
# end_date = start_date + out.n_periods * out.report_interval

# print(f"Start date = {start_date}")
# print(f"End date   = {end_date}")


# # Tipo de gráfico: 0 - Estático, 1 - Dinámico (serie temporal)
# plot_type = 0

# # Resultado en tiempo concreto 0 - Estático
# timestamp = pd.Timestamp('2021-06-10 00:30:00')

# # Periodo de resultados, 1 - Dinámico (serie temporal)
# custom_start = pd.Timestamp('2021-06-10 00:01:00')
# custom_end   = pd.Timestamp('2021-06-10 00:59:00')

# # Nodos
# start_node  ='MH1'
# end_node    ='O5'

# # Parámetros de visualización
# c_inv = "black"
# c_ground_line = "brown"
# c_crown = "black"
# c_ground = "brown"
# lw = 1
# c_water = "blue"
# c_pipe = "grey"
# mh_width = 0.5
# offset_ymax = 0.5

# offsets = 0 # 0 - Depth, # 1 - Elevation

# if plot_type == 0:
#     # Verificación para timestamp
#     if not (start_date <= timestamp <= end_date):
#         print("Warning: The selected time must be within the simulation period.")
#         sys.exit(1)
#     _, ax = plot_longitudinal(inp, start_node, end_node, c_inv, c_ground_line, c_crown, c_ground, c_water, c_pipe, lw, mh_width, timestamp, offset_ymax,
#             offsets, out=out, depth_agg_func=lambda x: x.max(), add_node_labels=False)

# elif plot_type == 1:
#     # Verificación para custom_start y custom_end
#     if not (start_date <= custom_start <= end_date) or not (start_date <= custom_end <= end_date):
#         print("Warning: The selected time range must be within the simulation period.")
#         sys.exit(1)
#     elif custom_end <= custom_start:
#         print("Warning: The end time must be bigger than the start time.")
#         sys.exit(1)
#     create_gif(start_node, end_node, write_time_step, out, custom_start, custom_end)
