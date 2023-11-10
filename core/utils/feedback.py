from qgis.PyQt.QtCore import pyqtSignal, QObject


class Feedback(QObject):
    progressText = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.canceled = False

    def cancel(self):
        self.canceled = True

    def setProgressText(self, txt):
        self.progressText.emit(txt)

    def setProgress(self, value):
        self.progress.emit(int(value))

    def pushWarning(self, txt):
        msg = "=" * 40 + "\n" + txt + "\n" + "=" * 40
        self.progressText.emit(msg)

    def isCanceled(self):
        return True if self.canceled else False
