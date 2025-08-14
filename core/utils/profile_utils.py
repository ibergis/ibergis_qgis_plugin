"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

@author: Esteban Sanudo

"""
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from qgis.PyQt.QtCore import QTimer

import pandas as pd

from swmm_api.input_file.macros.collection import nodes_dict, links_dict
from swmm_api.input_file.macros.graph import get_path_subgraph, links_connected
from swmm_api.input_file.sections import Outfall, Junction, Storage, Conduit, Weir, Orifice
from swmm_api.output_file import OBJECTS, VARIABLES


class COLS:
    INVERT_ELEV = 'SOK'
    IN_OFFSET = 'IN_OFF'
    OUT_OFFSET = 'OUT_OFF'
    CROWN_ELEV_IN = 'BUK_IN'
    CROWN_ELEV_OFF = 'BUK_OFF'
    GROUND_ELEV = 'GOK'  # rim elevation
    STATION = 'x'
    WATER = 'water'
    FLOODING = 'flooding'
    LABEL = 'label'


class ProfilePlotter:
    def __init__(self, inp=None, out=None, c_inv="black", c_ground_line="brown", ground_line_style="dashed", c_crown="black", c_ground="brown", c_water="blue", c_pipe="grey", lw=1, mh_width=0.5, offset_ymax=0.5, offsets=0, zero_node=None, depth_agg_func=None):
        self.inp = inp
        self.out = out
        self.c_inv = c_inv
        self.c_ground_line = c_ground_line
        self.ground_line_style = ground_line_style
        self.c_crown = c_crown
        self.c_ground = c_ground
        self.c_water = c_water
        self.c_pipe = c_pipe
        self.lw = lw
        self.mh_width = mh_width
        self.offset_ymax = offset_ymax
        self.offsets = offsets
        self.zero_node = zero_node
        self.depth_agg_func = depth_agg_func

    def get_longitudinal_data(self, start_node, end_node, timestamp):
        inp = self.inp
        out = self.out
        offsets = self.offsets
        zero_node = self.zero_node
        depth_agg_func = self.depth_agg_func

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
        nodes_depth = None  # noqa: F841
        nodes_flood = None  # noqa: F841
        if out is not None:
            if depth_agg_func is None:
                def depth_agg_func(s):
                    return s.mean()
            nodes_depth = depth_agg_func(out.get_part(OBJECTS.NODE, sub_list, VARIABLES.NODE.DEPTH)).to_dict()  # This gives me the maximums. # noqa: F841
            nodes_depth_dic = out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.DEPTH).to_dict()
            nodes_flooding = depth_agg_func(out.get_part(OBJECTS.NODE, sub_list, VARIABLES.NODE.FLOODING)).to_dict()  # noqa: F841
            nodes_flooding_dic = out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.FLOODING).to_dict()
        # ---------------
        stations_ = list(self.iter_over_inp_(sub_list, sub_graph))
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
                    water = None  # Or some default value in case the timestamp is missing
                    flooding = None  # Or some default value in case the timestamp is missing
            else:
                water = None
                flooding = None

            # Gets the conduits (Conduit, Weir, Orifice, etc.) connected to the node
            prior_conduit, following_conduit = links_connected(inp, node, sub_graph)

            if prior_conduit:
                prior_conduit = prior_conduit[0]
                if prior_conduit.name in inp.XSECTIONS:
                    profile_height = inp.XSECTIONS[prior_conduit.name].height
                else:
                    profile_height = 0

                # sok_ = sok
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

                # sok_ = sok
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
        return res  # Returns the dictionary with the longitudinal data

    def iter_over_inp_(self, sub_list, sub_graph):
        links = links_dict(self.inp)

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

    def iter_over_inp(self, start_node, end_node):
        sub_list, sub_graph = get_path_subgraph(self.inp, start=start_node, end=end_node)
        return self.iter_over_inp_(sub_list, sub_graph)

    def get_node_station(self, start_node, end_node, zero_node=None):
        stations = dict(self.iter_over_inp(start_node, end_node))
        if zero_node:
            return self.set_zero_node(stations, zero_node)
        return stations

    def set_zero_node(self, stations, zero_node):
        return {node: stations[node] - stations[zero_node] for node in stations}

    @staticmethod
    def interpolate_x_at_intersection(x1, y1a, x2, y2a, y1b, y2b):
        """
        Returns the x point where the two lines intersect.
        Line A: (x1, y1a)-(x2, y2a)
        Line B: (x1, y1b)-(x2, y2b)
        """
        dy_a = y2a - y1a
        dy_b = y2b - y1b
        dy = (y1b - y1a)  # initial difference

        # Avoid division by zero
        if dy_a == dy_b:
            return None  # líneas paralelas

        frac = dy / (dy_a - dy_b)
        x_int = x1 + frac * (x2 - x1)
        y_int = y1a + frac * (y2a - y1a)
        return x_int, y_int

    def plot_longitudinal(self, start_node, end_node, timestamp, ax=None, add_node_labels=False):
        res = self.get_longitudinal_data(start_node, end_node, timestamp)

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()

        ax.set_axisbelow(True)
        ax.plot(res[COLS.STATION], res[COLS.GROUND_ELEV], c=self.c_ground_line, lw=self.lw, ls=self.ground_line_style)

        for i in range(len(res[COLS.STATION]) - 1):

            x = res[COLS.STATION][i]
            invert_elev = res[COLS.INVERT_ELEV][i]
            ground_elev = res[COLS.GROUND_ELEV][i]
            water_elev = res[COLS.WATER][i]
            node_name = res[COLS.LABEL][i]  # Obtener el nombre del nodo
            node_type = self.out.model_properties[OBJECTS.NODE].get(node_name, {}).get("type")  # Acceder al tipo

            x1 = res[COLS.STATION][i]
            x2 = res[COLS.STATION][i + 1]

            diameter = res[COLS.CROWN_ELEV_OFF][i] - res[COLS.OUT_OFFSET][i]

            # Bottom of the conduit
            y1_down = res[COLS.OUT_OFFSET][i]
            y2_down = res[COLS.IN_OFFSET][i + 1]
            ax.plot([x1, x2], [y1_down, y2_down], c="black", lw=self.lw, zorder=12)

            # Top of the conduit
            y1_top = res[COLS.CROWN_ELEV_OFF][i]
            y2_top = res[COLS.CROWN_ELEV_IN][i + 1]
            ax.plot([x1, x2], [y1_top, y2_top], c="black", lw=self.lw, zorder=12)

            # Water elevation (clipped to the conduit)
            water_elev_up = res[COLS.WATER][i]
            water_elev_down = res[COLS.WATER][i + 1]
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

            # Water line
            ax.plot([x1, x2], [y1_w, y2_w], c=self.c_water, lw=self.lw)

            # Energy line
            if res[COLS.WATER][i] >= y1_top or res[COLS.WATER][i + 1] >= y2_top:
                y1_energy = res[COLS.WATER][i]
                y2_energy = res[COLS.WATER][i + 1]
                ax.plot([x1, x2], [y1_energy, y2_energy], c=self.c_water, lw=self.lw)

                # Do they cross?
                cross = (y1_energy - y1_top) * (y2_energy - y2_top) < 0

                if cross:
                    # If they cross, find the intersection point
                    x_int, y_int = self.interpolate_x_at_intersection(
                        x1, y1_energy, x2, y2_energy, y1_top, y2_top
                    )

                    # Left subsegment
                    if y1_energy > y1_top:
                        ax.fill_between([x1, x_int], [y1_down, y_int - diameter], [y1_top, y_int], color=self.c_water, alpha=1, zorder=10)
                    else:
                        ax.fill_between([x1, x_int], [y1_down, y_int - diameter], [y1_energy, y_int], color=self.c_water, alpha=1, zorder=10)
                        # Review

                    # Right subsegment
                    if y2_energy < y2_top:
                        ax.fill_between([x_int, x2], [y_int - diameter, y2_energy], [y_int, y2_energy], color=self.c_water, alpha=1, zorder=10)
                    else:
                        ax.fill_between([x_int, x2], [y_int, y2_down], [y_int, y2_top], color=self.c_water, alpha=1, zorder=10)
                        # Review

            # Fill between the water level and the bottom of the pipe
            ax.fill_between([x1, x2], [y1_down, y2_down], [y1_top, y2_top], color=self.c_pipe, alpha=1)
            ax.fill_between([x1, x2], [y1_w, y2_w], [y1_down, y2_down], color=self.c_water, alpha=1)

            bottom = ax.get_ylim()[0]

        # Draw manholes at all nodes
        for i in range(len(res[COLS.STATION])):
            x = res[COLS.STATION][i]
            invert_elev = res[COLS.INVERT_ELEV][i]
            ground_elev = res[COLS.GROUND_ELEV][i]
            water_elev = res[COLS.WATER][i]
            node_name = res[COLS.LABEL][i]
            node_type = self.out.model_properties[OBJECTS.NODE].get(node_name, {}).get("type")
            io_flooding = res[COLS.FLOODING][i]

            altura_total = ground_elev - invert_elev

            if node_type != "OUTFALL":
                rect = plt.Rectangle((x - self.mh_width / 2, invert_elev), self.mh_width, altura_total,
                                     edgecolor='black', facecolor=self.c_pipe, lw=self.lw, alpha=1, zorder=14)
                ax.add_patch(rect)

                rect_water = plt.Rectangle((x - self.mh_width / 2, invert_elev), self.mh_width, water_elev - invert_elev,
                                           edgecolor='black', facecolor=self.c_water, alpha=1, zorder=14)
                ax.add_patch(rect_water)

                # Add the text of the io_flooding value centered at the top of the manhole
                ax.text(x, ground_elev + 0.1, f"{io_flooding:.2f}",  # Ajusta el +0.1 según la escala de tu eje y
                        ha='center', va='bottom', fontsize=8, rotation=0, color='red', zorder=15)

        ax.fill_between(res[COLS.STATION], bottom, res[COLS.GROUND_ELEV], color=self.c_ground, alpha=0.7, zorder=0)

        ax.grid(True, zorder=-10)

        ax.set_xlim(res[COLS.STATION][0], res[COLS.STATION][-1])
        ax.set_ylim(bottom=bottom, top=(max(res[COLS.GROUND_ELEV]) + self.offset_ymax))

        secax = ax.secondary_xaxis('top')
        secax.set_xticks(res[COLS.STATION], minor=False)
        secax.set_xticklabels(res[COLS.LABEL], rotation=90, minor=False)
        secax.grid(axis='x', ls=':', color='grey', which='major')

        ax.set_title(f"Start node: {start_node}, End node: {end_node}\nTimestamp: {timestamp}")

        for x in res[COLS.STATION]:
            ax.axvline(x, color='black', linestyle=':', linewidth=1, zorder=15)
        return fig, ax

        fig.show()

    def show_with_slider(self, start_node, end_node, write_time_step, custom_start, custom_end):
        timestamp_range = pd.date_range(start=custom_start, end=custom_end, freq=write_time_step)
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.3)
        self.plot_longitudinal(start_node, end_node, timestamp_range[0], ax=ax)
        slider_ax = fig.add_axes((0.15, 0.1, 0.7, 0.03))
        slider = Slider(slider_ax, 'Timestep', 0, len(timestamp_range) - 1, valinit=0, valstep=1)

        play_ax = fig.add_axes((0.45, 0.02, 0.1, 0.05))
        play_button = Button(play_ax, 'Play')
        is_playing = {'value': False}

        timer = QTimer()
        timer.setInterval(200)  # ms

        def update(val):
            ax.clear()
            self.plot_longitudinal(start_node, end_node, timestamp_range[int(slider.val)], ax=ax)
            fig.canvas.draw_idle()

        slider.on_changed(update)

        def play(event):
            if not is_playing['value']:
                is_playing['value'] = True
                play_button.label.set_text('Pause')
                timer.start()
            else:
                is_playing['value'] = False
                play_button.label.set_text('Play')
                timer.stop()

        def advance():
            current = int(slider.val)
            if current < len(timestamp_range) - 1:
                slider.set_val(current + 1)
            else:
                is_playing['value'] = False
                play_button.label.set_text('Play')
                timer.stop()

        play_button.on_clicked(play)
        timer.timeout.connect(advance)
        plt.show()
