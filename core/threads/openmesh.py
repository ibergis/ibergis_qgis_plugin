from pathlib import Path


from .task import DrTask
from ..utils import mesh_parser
from ..utils.meshing_process import create_temp_mesh_layer


class DrOpenMeshTask(DrTask):
    def __init__(self, description, folder_path):
        super().__init__(description)
        self.folder_path = folder_path
        self.INITIAL_PROGRESS = 1
        self.POST_FILE_PROGRESS = 5
        self.POST_LAYER_PROGRESS = 95

    def run(self):
        super().run()
        self.setProgress(self.INITIAL_PROGRESS)

        MESH_FILE = "Iber2D.dat"
        mesh_path = Path(self.folder_path) / MESH_FILE

        ROOF_FILE = "Iber_SWMM_roof.dat"
        roof_path = Path(self.folder_path) / ROOF_FILE

        with open(mesh_path) as mesh_file:
            if roof_path.exists():
                with open(roof_path) as roof_file:
                    mesh = mesh_parser.load(mesh_file, roof_file)
            else:
                mesh = mesh_parser.load(mesh_file)

        self.setProgress(self.POST_FILE_PROGRESS)
        temp_layer = create_temp_mesh_layer(mesh)
        self.setProgress(self.POST_LAYER_PROGRESS)

        self.layer = temp_layer
        return True

    def update_polygon_progress(self, tri_progress: float):
        progress = (
            self.POST_LAYER_PROGRESS - self.POST_FILE_PROGRESS
        ) * tri_progress + self.POST_FILE_PROGRESS
        self.setProgress(progress)
