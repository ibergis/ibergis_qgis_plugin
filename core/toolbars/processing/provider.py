from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .fix_vertex_edge import DrFixEdgeVertexAlgorithm


class DrProcessingProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        """ Load each algorithm into the current provider. """
        print('Loading algorithms...')
        self.addAlgorithm(DrFixEdgeVertexAlgorithm())

    def id(self) -> str:
        print('ID')
        return 'drain'

    def name(self) -> str:
        return 'Drain'

    def icon(self) -> QIcon:
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

