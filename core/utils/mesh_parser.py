def dump():
    pass


def dumps():
    pass


def load(mesh_fp, roof_fp=None):
    mesh = {"polygons": {}, "vertices": {}}

    section = ""
    for line in mesh_fp:
        tokens = line.split()

        # skip empty lines
        if not len(tokens):
            continue

        # section lines
        if tokens[0] in ["MATRIU", "VERTEXS", "CONDICIONS"]:
            section = tokens[0]

        # ignore lines before first section
        if not section:
            continue

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
