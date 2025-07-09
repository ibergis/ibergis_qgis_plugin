import io
import pandas as pd
import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class Mesh:
    polygons: pd.DataFrame
    vertices: pd.DataFrame
    roofs: pd.DataFrame
    losses: Optional[dict]
    boundary_conditions: dict
    bridges: pd.DataFrame


def dump(mesh: Mesh, mesh_fp: io.TextIOWrapper, roof_fp: io.TextIOWrapper, losses_fp: io.TextIOWrapper, bridges_fp: io.TextIOWrapper):
    mesh_fp.write("MATRIU\n")
    mesh_fp.write(f"  {len(mesh.polygons)}\n")
    for tri in mesh.polygons.itertuples():
        try:
            manning_number = float(tri.roughness)

            if manning_number != 0:
                manning_number = f'{round(manning_number, 4):>9.4f}'
            else:
                manning_number = f'{-9999:>9d}'  # Default value
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error processing roughness for triangle {tri}: {e}")
            manning_number = f'{-9999:>9d}'  # Default value

        mesh_fp.write(f"    {tri.v1:8d} {tri.v2:8d} {tri.v3:8d} {tri.v4:8d} {manning_number} {tri.Index:8d}\n")
    mesh_fp.write("VERTEXS\n")
    mesh_fp.write(f"  {len(mesh.vertices)}\n")
    for v in mesh.vertices.itertuples():
        mesh_fp.write(f"    {v.x:>20.5f} {v.y:>20.5f} {v.z:>20.5f} {v.Index:>8d}\n")
    mesh_fp.write("CONDICIONS INICIALS\n")
    mesh_fp.write("CC: CONDICIONS CONTORN\n")
    for (pol_id, side), value in mesh.boundary_conditions.items():
        bt = value["type"]

        if bt == "INLET TOTAL DISCHARGE (SUB)CRITICAL":
            for time, flow in value["timeseries"].items():
                mesh_fp.write(
                    f"{pol_id} {side} {time} -{flow} -1 1 -41 2 1 {value['inlet']} -Hidrograma Q CriticoLento-\n"
                )
        elif bt == "INLET WATER ELEVATION":
            for time, elevation in value["timeseries"].items():
                mesh_fp.write(
                    f"{pol_id} {side} {time} 0 0 {elevation} -34 1 1 3 -Nivel dado-\n"
                )
        elif bt == "OUTLET (SUPER)CRITICAL":
            mesh_fp.write(
                f"{pol_id} {side} 0 0 0 0 -40 1 1 0 {value['outlet']} -Salida en Critico/Rapido -\n"
            )
        elif bt == "OUTLET SUBCRITICAL WEIR HEIGHT":
            mesh_fp.write(
                f"{pol_id} {side} 0 0 0 {value['height']} {value['weir_coefficient']} 1 1 0 {value['outlet']} -Salida Vertedero Altura-\n"
            )
        elif bt == "OUTLET SUBCRITICAL WEIR ELEVATION":
            mesh_fp.write(
                f"{pol_id} {side} 0 0 0 {value['elevation']} {value['weir_coefficient']} 3 1 0 {value['outlet']} -Salida Vertedero Cota-\n"
            )
        elif bt == "OUTLET SUBCRITICAL GIVEN LEVEL":
            for time, elevation in value["timeseries"].items():
                mesh_fp.write(
                    f"{pol_id} {side} {time} 0 0 {elevation} -34 1 1 0 {value['outlet']} -Salida Nivel Dado-\n"
                )
    mesh_fp.write("123456789\n")

    if len(mesh.roofs):
        roof_fp.write("Number of roofs\n")
        roof_fp.write(str(len(mesh.roofs)) + "\n")
        roof_fp.write("Roofs properties\n")
        for roof in mesh.roofs.itertuples():
            roof_fp.write(
                f"{roof.name} {roof.fid} {-9999 if roof.slope is None else roof.slope} {-9999 if roof.width is None else roof.width} "
                f"{-9999 if roof.roughness is None else round(roof.roughness, 4)} {-9999 if roof.isconnected is None else roof.isconnected} {-9999 if roof.outlet_code is None else roof.outlet_code} "
                f"{-9999 if roof.outlet_vol is None else roof.outlet_vol} {-9999 if roof.street_vol is None else roof.street_vol} {-9999 if roof.infiltr_vol is None else roof.infiltr_vol}\n"
            )
        roof_fp.write("\nRoof elements\n")
        for pol in mesh.polygons[mesh.polygons["category"] == "roof"].itertuples():
            roof_fp.write(f"{pol.Index} {pol.roof_id}\n")

    if len(mesh.bridges):
        for bridge in mesh.bridges.itertuples():
            bridges_fp.write(
                f"{bridge.element_id} {bridge.side} {bridge.num1} {bridge.num2} "
                f"{bridge.lowerdeckelev} {bridge.bridgeopeningpercent} {bridge.freepressureflowcd} "
                f"{bridge.topelevn} {bridge.num3} {bridge.deckcd} {bridge.sumergeflowcd} {bridge.gaugenumber} "
                f"{bridge.num4} {bridge.num5} {bridge.num6} {bridge.num7} {bridge.num8}\n"
            )

    if mesh.losses is not None:
        losses_config = mesh.losses

        # Infiltration losses OFF
        if losses_config["method"] == 0:
            losses_fp.write("0")

        # Infiltration losses - Manual / By Parameters - SCS
        elif losses_config["method"] == 2:
            losses_fp.write(
                f"2 {losses_config['cn_multiplier']} {losses_config['ia_coefficient']} {losses_config['start_time']}\n"
            )

            for index, scs_cn in mesh.polygons["scs_cn"].dropna().items():
                losses_fp.write(f"{index} {scs_cn}\n")


def dumps(mesh):
    with (
        io.StringIO() as mesh_buffer,
        io.StringIO() as roof_buffer,
        io.StringIO() as losses_buffer,
        io.StringIO() as bridges_buffer,
    ):
        dump(mesh, mesh_buffer, roof_buffer, losses_buffer, bridges_buffer)
        return mesh_buffer.getvalue(), roof_buffer.getvalue(), losses_buffer.getvalue(), bridges_buffer.getvalue()


def load(mesh_fp: io.StringIO, roof_fp=None, losses_fp=None, bridges_fp=None):

    polygon_rows = []
    vertices_rows = []
    boundary_conditions = {}

    section = ""
    for line in mesh_fp:
        line = line.strip()

        # skip empty lines
        if not line:
            continue

        # section lines
        section_headers = [
            "MATRIU",
            "VERTEXS",
            "CONDICIONS INICIALS",
            "CC: CONDICIONS CONTORN",
        ]
        if line in section_headers:
            section = line
            continue

        # ignore lines before first section
        if not section:
            continue

        tokens = line.split()

        # MATRIU section
        if section == "MATRIU":
            # skip lines that don't have 6 itens
            # the count of polygons is also skipped
            if len(tokens) != 6:
                continue

            polygon_rows.append(tokens)
            continue

        # VERTEXS section
        if section == "VERTEXS":
            # skip lines that don't have 4 itens
            # the count of polygons is also skipped
            if len(tokens) != 4:
                continue

            vertices_rows.append(tokens)
            continue

        # CC: CONDICIONS CONTORN section
        if section == "CC: CONDICIONS CONTORN":
            # skip lines that have less than 2 items
            if len(tokens) < 2:
                continue

            # TODO: handle all boundary conditions parameters
            polygon, edge, *parameters = tokens
            edge = int(edge)
            boundary_conditions[(polygon, edge)] = parameters
            continue

    polygons_df = pd.DataFrame(polygon_rows, columns=['v1', 'v2', 'v3', 'v4', 'roughness', 'fid'])
    polygons_df[['v1', 'v2', 'v3', 'v4']] = polygons_df[['v1', 'v2', 'v3', 'v4']].astype(np.uint32)
    polygons_df['roughness'] = polygons_df['roughness'].astype(np.float32)
    polygons_df['fid'] = polygons_df['fid'].astype(np.uint32)
    polygons_df['category'] = "ground"
    polygons_df["roof_id"] = -1
    polygons_df["scs_cn"] = np.nan
    polygons_df = polygons_df.set_index('fid')

    vertices_df = pd.DataFrame(vertices_rows, columns=['x', 'y', 'z', 'fid'])
    vertices_df[['x', 'y', 'z']] = vertices_df[['x', 'y', 'z']].astype(np.float64)
    vertices_df['fid'] = vertices_df['fid'].astype(np.uint32)
    vertices_df = vertices_df.set_index('fid')

    roof_rows = []
    if roof_fp:
        section = ""
        for line in roof_fp:
            line = line.strip()

            # skip empty lines
            if not line:
                continue

            # section lines
            section_headers = [
                "Number of roofs",
                "Roofs properties",
                "Roof elements",
            ]
            if line in section_headers:
                section = line
                continue

            # ignore lines before first section
            if not section:
                continue

            # 'Roof properties' section
            if section == "Roofs properties":
                tokens = line.split()

                # skip lines that don't have 4 itens
                if len(tokens) != 10:
                    continue

                roof_rows.append(tokens)

            # 'Roof elements' section
            if section == "Roof elements":
                tokens = line.split()

                # skip lines that don't have 4 itens
                # the count of polygons is also skipped
                if len(tokens) != 2:
                    continue

                polygon_id, roof_id = map(int, tokens)
                if polygon_id in polygons_df.index:
                    polygons_df.loc[polygon_id, "category"] = "roof"
                    polygons_df.loc[polygon_id, "roof_id"] = roof_id

    roofs_df = pd.DataFrame(roof_rows, columns=[
        'name',
        'fid',
        'slope',
        'width',
        'roughness',
        'isconnected',
        'outlet_code',
        'outlet_vol',
        'street_vol',
        'infiltr_vol'
    ])

    float_columns = [
        'slope',
        'width',
        'roughness',
        'outlet_vol',
        'street_vol',
        'infiltr_vol'
    ]
    roofs_df[float_columns] = roofs_df[float_columns].astype(np.float32)
    roofs_df['isconnected'] = roofs_df['isconnected'].astype(np.int32)
    # roofs_df['outlet_code'] = roofs_df['outlet_code'].astype(???)
    roofs_df['fid'] = roofs_df['fid'].astype(np.uint32)
    roofs_df.index = roofs_df['fid']  # type: ignore

    bridge_rows = []
    if bridges_fp:
        section = ""
        for line in bridges_fp:
            line = line.strip()

            # skip empty lines
            if not line:
                continue

            # section lines
            section_headers = [
                "Number of bridges",
                "Bridges properties",
                "Bridge elements",
            ]
            if line in section_headers:
                section = line
                continue

            # ignore lines before first section
            if not section:
                continue

            # 'Bridge properties' section
            if section == "Bridges properties":
                tokens = line.split()

                # skip lines that don't have 5 items
                if len(tokens) != 5:
                    continue

                bridge_rows.append(tokens)

            # 'Bridge elements' section
            if section == "Bridge elements":
                tokens = line.split()

                # skip lines that don't have 2 items
                if len(tokens) != 2:
                    continue

                polygon_id, bridge_id = map(int, tokens)
                if polygon_id in polygons_df.index:
                    polygons_df.loc[polygon_id, "category"] = "bridge"
                    polygons_df.loc[polygon_id, "bridge_id"] = bridge_id

    bridges_df = pd.DataFrame(bridge_rows, columns=[
        'element_id',
        'side',
        'num1',
        'num2',
        'lowerdeckelev',
        'bridgeopeningpercent',
        'freepressureflowcd',
        'topelevn',
        'num3',
        'deckcd',
        'sumergeflowcd',
        'gaugenumber',
        'num4',
        'num5',
        'num6',
        'num7',
        'num8'
    ])

    float_columns = [
        'lowerdeckelev',
        'bridgeopeningpercent',
        'freepressureflowcd',
        'topelevn',
        'deckcd',
        'sumergeflowcd',
        'gaugenumber'
    ]
    bridges_df[float_columns] = bridges_df[float_columns].astype(np.float32)
    bridges_df['element_id'] = bridges_df['element_id'].astype(np.uint32)
    bridges_df['side'] = bridges_df['side'].astype(np.uint32)
    # bridges_df.index = bridges_df['fid'] # type: ignore

    losses = None
    if losses_fp:
        first_line = True
        for line in losses_fp:
            if first_line:
                first_line = False
                configuration = line.split()

                # Infiltration losses OFF
                if configuration[0] == "0":
                    losses = {"method": 0}
                    break

                # Infiltration losses - Manual / By Parameters - SCS
                elif configuration[0] == "2":
                    losses = {
                        "method": 2,
                        "cn_multiplier": float(configuration[1]),
                        "ia_coefficient": float(configuration[2]),
                        "start_time": float(configuration[3]),
                    }
                    continue
            else:
                polygon_id, cn_value = line.split()
                polygons_df.loc[int(polygon_id), "scs_cn"] = float(cn_value)

    mesh = Mesh(
        polygons=polygons_df,
        vertices=vertices_df,
        boundary_conditions=boundary_conditions,
        roofs=roofs_df,
        losses=losses,
        bridges=bridges_df
    )

    return mesh


def loads(mesh_string, roof_string="", losses_string="", bridges_string=""):
    with (
        io.StringIO(mesh_string) as mesh_file,
        io.StringIO(roof_string) as roof_file,
        io.StringIO(losses_string) as losses_file,
        io.StringIO(bridges_string) as bridges_file,
    ):
        return load(mesh_file, roof_file, losses_file, bridges_file)
