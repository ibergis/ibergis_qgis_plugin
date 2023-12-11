import io


def dump(mesh, mesh_fp, roof_fp):
    mesh_fp.write("MATRIU\n")
    mesh_fp.write(f"  {len(mesh['polygons'])}\n")
    for i, tri in mesh["polygons"].items():
        v1, v2, v3, v4 = tri["vertice_ids"]
        manning_number = 0.0180
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
        # TODO: Handle BC cases
        mesh_fp.write(
            f"{pol_id} {side} 0      0 0 0 -40 1 1 0 1  -Salida en Critico/Rapido -\n"
        )

    if not len(mesh["roofs"]):
        return

    roof_fp.write("Number of roofs\n")
    roof_fp.write(str(len(mesh["roofs"])) + "\n")
    roof_fp.write("Roofs properties\n")
    for roof_id, roof in mesh["roofs"].items():
        roof_fp.write(
            f"{roof['name']} {roof_id} {roof['slope']} {roof['width']} "
            f"{roof['roughness']} {roof['isconnected']} {roof['outlet_id']} "
            f"{roof['outlet_vol']} {roof['street_vol']} {roof['infiltr_vol']}\n"
        )
    roof_fp.write("\nRoof elements\n")
    for i, pol in mesh["polygons"].items():
        if pol["category"] == "roof":
            roof_fp.write(f"{i} {pol['roof_id']}\n")


def dumps(mesh):
    mesh_buffer = io.StringIO()
    roof_buffer = io.StringIO()
    dump(mesh, mesh_buffer, roof_buffer)
    mesh_str = mesh_buffer.getvalue()
    mesh_buffer.close()
    roof_str = roof_buffer.getvalue()
    roof_buffer.close()
    return mesh_str, roof_str


def load(mesh_fp, roof_fp=None):
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
            if section == "Roof properties":
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
                    outlet_id,
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
                    "outlet_id": outlet_id,
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

    return mesh


def loads(mesh_string, roof_string=None):
    mesh_file = io.StringIO(mesh_string)
    roof_file = io.StringIO(roof_string) if roof_string else io.StringIO("")
    mesh = load(mesh_file, roof_file)
    mesh_file.close()
    roof_file.close()
    return mesh
