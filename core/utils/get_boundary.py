"""
Model exported as python.
Name : Get Boundary
Group : Drain
With QGIS : 32809
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis import processing


class GetBoundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('ground_layer', 'Ground Layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('polygon_id', 'Polygon ID', type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('roof_layer', 'Roof Layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('OUTPUT', 'Boundary', type=QgsProcessing.TypeVectorLine, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Extract by attribute
        alg_params = {
            'FIELD': 'fid',
            'INPUT': parameters['ground_layer'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['polygon_id'],
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttribute'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': None,
            'LAYERS': [parameters['roof_layer'],outputs['ExtractByAttribute']['FAIL_OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Delete holes
        alg_params = {
            'INPUT': outputs['ExtractByAttribute']['OUTPUT'],
            'MIN_AREA': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteHoles'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 1,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['DeleteHoles']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'INTERSECT': outputs['Buffer']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Convert geometry type (Polygon)
        alg_params = {
            'INPUT': outputs['DeleteHoles']['OUTPUT'],
            'TYPE': 3,  # Multilinestrings
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertGeometryTypePolygon'] = processing.run('qgis:convertgeometrytype', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Convert geometry type (Layer)
        alg_params = {
            'INPUT': outputs['ExtractByLocation']['OUTPUT'],
            'TYPE': 3,  # Multilinestrings
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertGeometryTypeLayer'] = processing.run('qgis:convertgeometrytype', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['ConvertGeometryTypePolygon']['OUTPUT'],
            'OVERLAY': outputs['ConvertGeometryTypeLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Merge lines
        alg_params = {
            'INPUT': outputs['Difference']['OUTPUT'],
            'OUTPUT': parameters['OUTPUT']
        }
        outputs['MergeLines'] = processing.run('native:mergelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OUTPUT'] = outputs['MergeLines']['OUTPUT']
        return results

    def name(self):
        return 'Get Boundary'

    def displayName(self):
        return 'Get Boundary'

    def group(self):
        return 'Drain'

    def groupId(self):
        return 'Drain'

    def createInstance(self):
        return GetBoundary()
