def dump():
    pass


def dumps():
    pass


def load(mesh_fp, roof_fp=None):
    mesh = {"polygons": {}, "vertices": {}, "boundary_conditions": {}}

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

            # TODO: process 'Roofs properties' section

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


def loads():
    pass
