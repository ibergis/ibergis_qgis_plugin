
from ..utils import mesh_parser
from ..utils.meshing_process import create_temp_mesh_layer
from .task import DrTask


class DrCreateTempMeshLayerTask(DrTask):
    def __init__(self, description, mesh, row=None):
        super().__init__(description)
        self.mesh = mesh
        self.row = row
        self.POST_FILE_PROGRESS = 5
        self.POST_LOAD_PROGRESS = 50
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()

        self.setProgress(self.POST_FILE_PROGRESS)

        if self.mesh is None and self.row is not None:
            self.mesh = mesh_parser.loads(self.row["iber2d"], self.row["roof"], self.row["losses"])

        self.setProgress(self.POST_LOAD_PROGRESS)

        self.layer = create_temp_mesh_layer(self.mesh)

        self.setProgress(self.POST_LAYER_PROGRESS)
        return True

    def update_polygon_progress(self, tri_progress: float):
        progress = (
            self.POST_LAYER_PROGRESS - self.POST_FILE_PROGRESS
        ) * tri_progress + self.POST_FILE_PROGRESS
        self.setProgress(progress)
