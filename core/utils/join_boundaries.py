"""
Model exported as python.
Name : Set Boundary Conditons to Mesh Boundaries
Group : Drain
With QGIS : 32809
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis import processing


class SetBoundaryConditonsToMeshBoundaries(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString('bc_scenario', 'bc_scenario', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterVectorLayer('boundary_conditions', 'boundary_conditions', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('mesh_boundaries', 'mesh_boundaries', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mesh_boundary_conditions', 'mesh_boundary_conditions', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Extract by attribute
        alg_params = {
            'FIELD': 'bscenario',
            'INPUT': parameters['boundary_conditions'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['bc_scenario'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttribute'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.1,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByAttribute']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': parameters['mesh_boundaries'],
            'JOIN': outputs['Buffer']['OUTPUT'],
            'JOIN_FIELDS': ['fid'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [5],  # are within
            'PREFIX': 'bc_',
            'OUTPUT': parameters['Mesh_boundary_conditions']
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Mesh_boundary_conditions'] = outputs['JoinAttributesByLocation']['OUTPUT']
        return results

    def name(self):
        return 'Set Boundary Conditons to Mesh Boundaries'

    def displayName(self):
        return 'Set Boundary Conditons to Mesh Boundaries'

    def group(self):
        return 'Drain'

    def groupId(self):
        return ''

    def createInstance(self):
        return SetBoundaryConditonsToMeshBoundaries()
