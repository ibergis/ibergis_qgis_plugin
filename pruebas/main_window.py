from qgis.PyQt.QtWidgets import QMainWindow, QPushButton
from qgis.core import QgsApplication


class MainWindow(QMainWindow):

    def __init__(self, title, text_button):
        super().__init__()
        self.resize(300, 200)
        self.move(100, 200)
        self.setWindowTitle(title)
        button = QPushButton(text_button, self)
        button.setCheckable(True)
        button.move(50, 80)
        button.clicked.connect(self.the_button_was_clicked)

    def the_button_was_clicked(self):
        print("Button clicked!")


if __name__ == '__main__':

    # Create a reference to the QgsApplication
    app = QgsApplication([], True)

    # Load providers
    app.initQgis()

    window = MainWindow("Window title", "Press Me!")
    window.show()

    # Execute custom application
    exitcode = app.exec_()

    # Remove the provider and layer registries from memory
    app.exitQgis()
    sys.exit(exitcode)