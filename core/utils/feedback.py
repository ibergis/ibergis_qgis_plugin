from qgis.core import QgsFeedback
from qgis.PyQt.QtCore import pyqtSignal
from ..threads.execute_model import lerp_progress


class Feedback(QgsFeedback):
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')
    progress_state = 1

    def __init__(self, start_progress=None, end_progress=None, max_progress=None):
        super().__init__()
        self.start_progress = start_progress
        self.end_progress = end_progress
        self.max_progress = max_progress

    def setProgressText(self, txt):
        self.progress_changed.emit("Import files", self.progress, txt, True)

    def pushWarning(self, txt):
        msg = "=" * 40 + "\n" + txt + "\n" + "=" * 40
        self.progress_changed.emit("Import files", self.progress, msg, True)
    
    def setProgress(self, progress):
        if self.start_progress is not None and self.end_progress is not None and self.max_progress is not None and progress == 100 and self.progress_state < 40:    
            lerp_num = lerp_progress(int(self.progress_state/self.max_progress*100), self.start_progress, self.end_progress)            
            self.progress_changed.emit(None, lerp_num, None, False)
            self.progress_state += 1
