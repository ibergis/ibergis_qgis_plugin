

from ..utils.meshing_process import create_temp_mesh_layer
from .task import DrTask


class DrCreateTempMeshLayerTask(DrTask):
    def __init__(self, description, mesh):
        super().__init__(description)
        self.mesh = mesh
        self.POST_FILE_PROGRESS = 5
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()

        self.setProgress(self.POST_FILE_PROGRESS)

        self.layer = create_temp_mesh_layer(self.mesh)

        self.setProgress(self.POST_LAYER_PROGRESS)
        return True

    def update_polygon_progress(self, tri_progress: float):
        progress = (
            self.POST_LAYER_PROGRESS - self.POST_FILE_PROGRESS
        ) * tri_progress + self.POST_FILE_PROGRESS
        self.setProgress(progress)
