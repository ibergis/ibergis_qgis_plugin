from qgis.core import QgsFeedback
from qgis.PyQt.QtCore import pyqtSignal


class Feedback(QgsFeedback):
    progressText = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def setProgressText(self, txt):
        self.progressText.emit(txt)

    def pushWarning(self, txt):
        msg = "=" * 40 + "\n" + txt + "\n" + "=" * 40
        self.progressText.emit(msg)
