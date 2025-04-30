from qgis.core import QgsFeedback
from qgis.PyQt.QtCore import pyqtSignal
from .tools_dr import lerp_progress
from typing import Optional


class Feedback(QgsFeedback):
    progressText = pyqtSignal(str)
    progress_changed = pyqtSignal(str, int, str, bool)  # (Process, Progress, Text, '\n')
    progress_state = 1

    def __init__(self, start_progress: Optional[int] = None, end_progress: Optional[int] = None, max_progress: Optional[int] = None):
        super().__init__()
        self.start_progress = start_progress
        self.end_progress = end_progress
        self.max_progress = max_progress

    def setProgressText(self, txt: str):
        self.progressText.emit(txt)
        self.progress_changed.emit(None, self.progress, txt, True)

    def pushWarning(self, txt: str):
        msg = "=" * 40 + "\n" + txt + "\n" + "=" * 40
        self.progressText.emit(msg)
        self.progress_changed.emit(None, self.progress, msg, True)

    def setProgress(self, progress: int):
        if None not in (self.start_progress, self.end_progress, self.max_progress) and progress == 100 and self.progress_state < 40:
            lerp_num = lerp_progress(int(self.progress_state/self.max_progress*100), self.start_progress, self.end_progress)
            self.progress_changed.emit(None, lerp_num, None, False)
            self.progress_state += 1
        elif None in (self.start_progress, self.end_progress, self.max_progress):
            self.progress_changed.emit(None, progress, None, False)
