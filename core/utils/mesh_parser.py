import io


def dump(mesh, mesh_fp, roof_fp, losses_fp):
    mesh_fp.write("MATRIU\n")
    mesh_fp.write(f"  {len(mesh['polygons'])}\n")
    for i, tri in mesh["polygons"].items():
        v1, v2, v3, v4 = tri["vertice_ids"]
        try:
            manning_number = tri["roughness"]
        except KeyError:
            print(f"{tri=}")
        mesh_fp.write(f"    {v1} {v2} {v3} {v4} {manning_number} {i}\n")
    mesh_fp.write("VERTEXS\n")
    mesh_fp.write(f"  {len(mesh['vertices'])}\n")
    for i, v in mesh["vertices"].items():
        x, y = v["coordinates"]
        z = v["elevation"]
        mesh_fp.write(f"    {x} {y} {z} {i}\n")
    mesh_fp.write("CONDICIONS INICIALS\n")
    mesh_fp.write("CC: CONDICIONS CONTORN\n")
    for (pol_id, side), value in mesh["boundary_conditions"].items():
        bt = value["type"]

        if bt == "INLET TOTAL DISCHARGE (SUB)CRITICAL":
            for time, flow in value["timeseries"].items():
                mesh_fp.write(
                    f"{pol_id} {side} {time} -{flow} -1 -1 -41 2 1 {value['inlet']} -Hidrograma Q CriticoLento-\n"
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

    if len(mesh["roofs"]):
        roof_fp.write("Number of roofs\n")
        roof_fp.write(str(len(mesh["roofs"])) + "\n")
        roof_fp.write("Roofs properties\n")
        for roof_id, roof in mesh["roofs"].items():
            roof_fp.write(
                f"{roof['name']} {roof_id} {roof['slope'] or -9999} {roof['width'] or -9999} "
                f"{roof['roughness'] or -9999} {roof['isconnected'] or -9999} {roof['outlet_code'] or -9999} "
                f"{roof['outlet_vol'] or -9999} {roof['street_vol'] or -9999} {roof['infiltr_vol'] or -9999}\n"
            )
        roof_fp.write("\nRoof elements\n")
        for i, pol in mesh["polygons"].items():
            if pol["category"] == "roof":
                roof_fp.write(f"{i} {pol['roof_id']}\n")

    if "losses" in mesh:
        losses_config = mesh["losses"]

        # Infiltration losses OFF
        if losses_config["method"] == 0:
            losses_fp.write("0")

        # Infiltration losses - Manual / By Parameters - SCS
        elif losses_config["method"] == 2:
            losses_fp.write(
                f"2 {losses_config['cn_multiplier']} {losses_config['ia_coefficient']} {losses_config['start_time']}\n"
            )
            for i, pol in mesh["polygons"].items():
                if "scs_cn" in pol:
                    losses_fp.write(f"{i} {pol['scs_cn']}\n")


def dumps(mesh):
    with (
        io.StringIO() as mesh_buffer,
        io.StringIO() as roof_buffer,
        io.StringIO() as losses_buffer,
    ):
        dump(mesh, mesh_buffer, roof_buffer, losses_buffer)
        return mesh_buffer.getvalue(), roof_buffer.getvalue(), losses_buffer.getvalue()


def load(mesh_fp, roof_fp=None, losses_fp=None):
    mesh = {"polygons": {}, "vertices": {}, "roofs": {}, "boundary_conditions": {}}

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

            v1, v2, v3, v4, roughness, fid = tokens
            mesh["polygons"][fid] = {
                "vertice_ids": [v1, v2, v3, v4],
                "category": "ground",
                "roughness": float(roughness),
            }
            continue

        # VERTEXS section
        if section == "VERTEXS":
            # skip lines that don't have 4 itens
            # the count of polygons is also skipped
            if len(tokens) != 4:
                continue

            x, y, z, fid = tokens
            mesh["vertices"][fid] = {
                "coordinates": (float(x), float(y)),
                "elevation": float(z),
            }
            continue

        # CC: CONDICIONS CONTORN section
        if section == "CC: CONDICIONS CONTORN":
            # skip lines that have less than 2 items
            if len(tokens) < 2:
                continue

            # TODO: handle all boundary conditions parameters
            polygon, edge, *parameters = tokens
            edge = int(edge)
            mesh["boundary_conditions"][(polygon, edge)] = parameters
            continue

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

            # ignore lines before first section
            if not section:
                continue

            # 'Roof properties' section
            if section == "Roofs properties":
                tokens = line.split()

                # skip lines that don't have 4 itens
                if len(tokens) != 10:
                    continue

                (
                    roof_name,
                    fid,
                    slope,
                    width,
                    roughness,
                    isconnected,
                    outlet_code,
                    outlet_vol,
                    street_vol,
                    infiltr_vol,
                ) = tokens
                mesh["roofs"][fid] = {
                    "name": roof_name,
                    "slope": slope,
                    "width": width,
                    "roughness": roughness,
                    "isconnected": isconnected,
                    "outlet_code": outlet_code,
                    "outlet_vol": outlet_vol,
                    "street_vol": street_vol,
                    "infiltr_vol": infiltr_vol,
                }

            # 'Roof elements' section
            if section == "Roof elements":
                tokens = line.split()

                # skip lines that don't have 4 itens
                # the count of polygons is also skipped
                if len(tokens) != 2:
                    continue

                polygon_id, roof_id = tokens
                if polygon_id in mesh["polygons"]:
                    mesh["polygons"][polygon_id]["category"] = "roof"
                    mesh["polygons"][polygon_id]["roof_id"] = roof_id

    if losses_fp:
        first_line = True
        for line in losses_fp:
            if first_line:
                first_line = False
                configuration = line.split()

                # Infiltration losses OFF
                if configuration[0] == "0":
                    mesh["losses"] = {"method": 0}
                    break

                # Infiltration losses - Manual / By Parameters - SCS
                elif configuration[0] == "2":
                    mesh["losses"] = {
                        "method": 2,
                        "cn_multiplier": float(configuration[1]),
                        "ia_coefficient": float(configuration[2]),
                        "start_time": float(configuration[3]),
                    }
                    continue
            else:
                polygon_id, cn_value = line.split()
                mesh["polygons"][polygon_id]["scs_cn"] = cn_value

    return mesh


def loads(mesh_string, roof_string="", losses_string=""):
    with (
        io.StringIO(mesh_string) as mesh_file,
        io.StringIO(roof_string) as roof_file,
        io.StringIO(losses_string) as losses_file,
    ):
        return load(mesh_file, roof_file, losses_file)
