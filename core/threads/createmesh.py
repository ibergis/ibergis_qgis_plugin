import traceback

from .task import GwTask
from ... import global_vars


class GwCreateMeshTask(GwTask):
    def __init__(self, description, feedback):
        super().__init__(description)
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao = global_vars.gpkg_dao_data.clone()
            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False
