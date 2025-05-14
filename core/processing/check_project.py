from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterBoolean, QgsProject, QgsVectorLayer
from typing import Any

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt
from ... import global_vars

from .check_project_queries import get_queries


class DrCheckProjectAlgorithm(QgsProcessingAlgorithm):

    def __init__(self) -> None:
        super().__init__()
        self.queries = get_queries()

    def name(self) -> str:
        return 'check_project'

    def displayName(self) -> str:
        return tools_qt.tr('Check Project')

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrCheckProjectAlgorithm()

    def initAlgorithm(self, configuration: dict[str, Any] | None = None) -> None:
        for query in self.queries:
            self.addParameter(
                QgsProcessingParameterBoolean(
                    query.short_name,
                    tools_qt.tr(query.description),
                    defaultValue=True,
                )
            )

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback | None) -> dict[str, Any]:
        self.dao: DrGpkgDao = global_vars.gpkg_dao_data.clone()

        for query in self.queries:
            if feedback and feedback.isCanceled():
                break

            if not self.parameterAsBoolean(parameters, query.short_name, context):
                continue

            result = query.execute(self.dao)
            if isinstance(result, QgsVectorLayer):
                QgsProject.instance().addMapLayer(result)
                # TODO: - Add layer to group
                #       - Display the number of found features if show_layer
            elif isinstance(result, int):
                if feedback:
                    feedback.setProgressText(f"{query.description}: {result} geometries")

        return {}
