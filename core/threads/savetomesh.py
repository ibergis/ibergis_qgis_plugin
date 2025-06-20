import traceback
from itertools import chain, tee


from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsField,
    QgsFields,
    QgsProcessingContext,
    QgsProcessingFeedback,
)
from qgis.PyQt.QtCore import QVariant

from .task import DrTask
from ..utils import mesh_parser
from ..utils.join_boundaries import SetBoundaryConditonsToMeshBoundaries
from ... import global_vars


def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class DrSaveToMeshTask(DrTask):
    def __init__(
        self,
        description,
        bc_scenario,
        mesh_name,
        mesh: mesh_parser.Mesh,
        feedback=None,
    ):
        super().__init__(description)
        self.bc_scenario = bc_scenario
        self.mesh_name = mesh_name
        self.mesh = mesh
        self.feedback = feedback
        self.message = None

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.feedback.setProgressText("Starting process!")
            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

            self.feedback.setProgressText("Loading data...")
            dao = global_vars.gpkg_dao_data.clone()
            db_file_path = dao.db_filepath
            bc_path = f"{db_file_path}|layername=boundary_conditions|subset=bscenario = '{self.bc_scenario}'"
            bc_layer = QgsVectorLayer(bc_path, "boundary_conditions", "ogr")

            # Create a layer with mesh edges exclusive to only one polygon
            poly_df = self.mesh.polygons
            boundary_edges = {}
            for pol in poly_df[poly_df["category"] == "ground"].itertuples():
                vert = [pol.v1, pol.v2, pol.v3, pol.v4]
                # Add last and first vertices as a edge if they are distinct
                last_edge = [(vert[-1], vert[0])] if vert[-1] != vert[0] else []
                edges = chain(pairwise(vert), last_edge)
                for side, verts in enumerate(edges, start=1):
                    edge = frozenset(verts)
                    if edge in boundary_edges:
                        del boundary_edges[edge]
                    else:
                        boundary_edges[edge] = (pol.Index, side)

                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False

            layer = QgsVectorLayer("LineString", "boundary_edges", "memory")
            layer.setCrs(bc_layer.crs())
            provider = layer.dataProvider()

            fields = QgsFields()
            fields.append(QgsField("pol_id", QVariant.String))
            fields.append(QgsField("side", QVariant.Int))
            provider.addAttributes(fields)
            layer.updateFields()

            features = []
            for edge, (pol_id, side) in boundary_edges.items():
                coords = [self.mesh.vertices.loc[vert, ["x", "y"]].to_numpy() for vert in edge]
                # coords = [self.mesh["vertices"][vert]["coordinates"] for vert in edge]
                feature = QgsFeature()
                feature.setGeometry(
                    QgsGeometry.fromPolyline([QgsPoint(*coord) for coord in coords])
                )
                feature.setAttributes([pol_id, side])
                features.append(feature)

                if self.feedback.isCanceled():
                    self.message = "Task canceled."
                    return False

            provider.addFeatures(features)
            layer.updateExtents()

            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

            # Get geometry of the boundary
            self.feedback.setProgressText("Executing geoprocess...")
            self.feedback.setProgress(15)
            get_boundary_conditions = SetBoundaryConditonsToMeshBoundaries()
            get_boundary_conditions.initAlgorithm()
            params = {
                "boundary_conditions": bc_layer,
                "bc_scenario": self.bc_scenario,
                "mesh_boundaries": layer,
                "Mesh_boundary_conditions": "TEMPORARY_OUTPUT",
            }
            context = QgsProcessingContext()
            feedback = QgsProcessingFeedback()
            results = get_boundary_conditions.processAlgorithm(
                params, context, feedback
            )
            result_layer = context.getMapLayer(results["Mesh_boundary_conditions"])

            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

            # TODO: Handle empty results

            # Create a dict of configuration for each boundary condition
            sql = f"""
                SELECT fid, boundary_type, timeseries, other1, other2
                FROM boundary_conditions
                WHERE bscenario = '{self.bc_scenario}'
            """
            rows = dao.get_rows(sql)
            if rows is None:
                self.message = "No boundary conditions found for this scenario"
                return False

            def get_timeseries(timeseries_id):
                sql = f"""
                    SELECT time, value
                    FROM cat_timeseries_value
                    WHERE timeseries IN (
                        SELECT idval
                        FROM cat_timeseries
                        WHERE idval = '{timeseries_id}'
                    )
                """
                rows = dao.get_rows(sql)
                if rows is None:
                    self.message = f"Timeseries idval {timeseries_id} is empty."
                    return False
                timeseries_dict = {}
                for row in rows:
                    hours, minutes = map(int, row["time"].split(":"))
                    seconds = hours * 3600 + minutes * 60
                    timeseries_dict[seconds] = row["value"]
                return timeseries_dict

            bc_dict = {}
            for row in rows:
                bt = row["boundary_type"]

                if bt == "INLET TOTAL DISCHARGE (SUB)CRITICAL":
                    bc_dict[row["fid"]] = {
                        "type": "INLET TOTAL DISCHARGE (SUB)CRITICAL",
                        "timeseries": get_timeseries(row["timeseries"]),
                        "inlet": row["fid"],
                    }
                elif bt == "INLET WATER ELEVATION":
                    bc_dict[row["fid"]] = {
                        "type": "INLET WATER ELEVATION",
                        "timeseries": get_timeseries(row["timeseries"]),
                    }
                elif bt == "OUTLET (SUPER)CRITICAL":
                    bc_dict[row["fid"]] = {
                        "type": "OUTLET (SUPER)CRITICAL",
                        "outlet": row["fid"],
                    }
                elif bt == "OUTLET SUBCRITICAL WEIR HEIGHT":
                    bc_dict[row["fid"]] = {
                        "type": "OUTLET SUBCRITICAL WEIR HEIGHT",
                        "weir_coefficient": row["other1"],
                        "height": row["other2"],
                        "outlet": row["fid"],
                    }
                elif bt == "OUTLET SUBCRITICAL WEIR ELEVATION":
                    bc_dict[row["fid"]] = {
                        "type": "OUTLET SUBCRITICAL WEIR ELEVATION",
                        "weir_coefficient": row["other1"],
                        "elevation": row["other2"],
                        "outlet": row["fid"],
                    }
                elif bt == "OUTLET SUBCRITICAL GIVEN LEVEL":
                    bc_dict[row["fid"]] = {
                        "type": "OUTLET SUBCRITICAL GIVEN LEVEL",
                        "timeseries": get_timeseries(row["timeseries"]),
                        "outlet": row["fid"],
                    }

            # Save boundary conditions to mesh dict
            self.mesh.boundary_conditions = {}
            for feature in result_layer.getFeatures():
                # TODO handle bc cases
                self.mesh.boundary_conditions[
                    (feature["pol_id"], feature["side"])
                ] = bc_dict[feature["bc_fid"]]

            new_mesh_str, new_roof_str, new_losses_str, new_bridges_str = mesh_parser.dumps(self.mesh)

            if self.feedback.isCanceled():
                self.message = "Task canceled."
                return False

            self.feedback.setProgressText("Saving the result...")
            self.feedback.setProgress(80)

            # Delete old mesh
            sql = f"DELETE FROM cat_file WHERE name = '{self.mesh_name}'"
            dao.execute_sql(sql)

            # Save mesh
            sql = f"""
              INSERT INTO cat_file (name, iber2d, roof, losses)
              VALUES
                  ('{self.mesh_name}', '{new_mesh_str}', '{new_roof_str}', '{new_losses_str}')
            """
            dao.execute_sql(sql)

            self.feedback.setProgressText("Process finished!!!")
            self.feedback.setProgress(100)
            return True

        except Exception:
            self.exception = traceback.format_exc()
            self.message = (
                "Task failed. See the Log Messages Panel for more information."
            )
            return False
