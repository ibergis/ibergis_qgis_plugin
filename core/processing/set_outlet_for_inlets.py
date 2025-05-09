"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ..utils import Feedback
from typing import Optional, List
import processing


class SetOutletForInlets(QgsProcessingAlgorithm):
    """
    Class to import ground geometries from another layer.
    """
    FILE_INLETS = 'FILE_INLETS'
    FILE_PINLETS = 'FILE_PINLETS'
    FILE_OUTLETS = 'FILE_OUTLETS'

    nearest_valid_inlet_outlets: Optional[dict[str,Optional[str]]] = None
    nearest_valid_pinlet_outlets: Optional[dict[str,Optional[str]]] = None

    file_inlets: QgsVectorLayer = None
    file_pinlets: QgsVectorLayer = None

    dao: DrGpkgDao = tools_gpkgdao.DrGpkgDao()

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        inlet_layer: QgsVectorLayer = tools_qgis.get_layer_by_tablename('inlet')
        inlet_layer_param = QgsProcessingParameterVectorLayer(
                name=self.FILE_INLETS,
                description=self.tr('Inlets layer'),
                types=[QgsProcessing.SourceType.VectorPoint],
                optional=True
            )
        if inlet_layer:
            inlet_layer_param.setDefaultValue(inlet_layer)
        self.addParameter(inlet_layer_param)

        pinlet_layer: QgsVectorLayer = tools_qgis.get_layer_by_tablename('pinlet')
        pinlet_layer_param = QgsProcessingParameterVectorLayer(
                name=self.FILE_PINLETS,
                description=self.tr('Pinlets layer'),
                types=[QgsProcessing.SourceType.VectorPolygon],
                optional=True
            )
        if pinlet_layer:
            pinlet_layer_param.setDefaultValue(pinlet_layer)
        self.addParameter(pinlet_layer_param)

        outlet_layer: QgsVectorLayer = tools_qgis.get_layer_by_tablename('inp_junction')
        outlet_layer_param = QgsProcessingParameterVectorLayer(
                name=self.FILE_OUTLETS,
                description=self.tr('Outlets layer'),
                types=[QgsProcessing.SourceType.VectorPoint],
                optional=False
            )
        if outlet_layer:
            outlet_layer_param.setDefaultValue(outlet_layer)
        self.addParameter(outlet_layer_param)

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        self.file_inlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_INLETS, context)
        self.file_pinlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_PINLETS, context)
        file_outlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_OUTLETS, context)
        feedback.setProgress(10)

        neighbor_limit: int = 10

        # Generate the nearest outlet for each inlet and pinlet with the QGIS processing algorithm: Join by nearest
        if not self.file_inlets and not self.file_pinlets:
            feedback.pushWarning(self.tr("Is required at least one layer selected to Inlet or Pinlet."))
            return {}

        if self.file_inlets:
            nearest_inlet_outlets: QgsVectorLayer = processing.run("native:joinbynearest", {
                'INPUT': self.file_inlets,
                'INPUT_2': file_outlets,
                'FIELDS_TO_COPY':[],'DISCARD_NONMATCHING':False,'PREFIX':'',
                'NEIGHBORS':neighbor_limit,'MAX_DISTANCE':None,'OUTPUT':'memory:'})['OUTPUT']
            self.nearest_valid_inlet_outlets = self.getNearestValidOutlets(nearest_inlet_outlets, feedback)
        if self.file_pinlets:
            nearest_pinlet_outlets = processing.run("native:joinbynearest", {
                'INPUT': self.file_pinlets,
                'INPUT_2': file_outlets,
                'FIELDS_TO_COPY':[],'DISCARD_NONMATCHING':False,'PREFIX':'',
                'NEIGHBORS':neighbor_limit,'MAX_DISTANCE':None,'OUTPUT':'memory:'})['OUTPUT']
            self.nearest_valid_pinlet_outlets = self.getNearestValidOutlets(nearest_pinlet_outlets, feedback)

        if feedback.isCanceled():
            return {}

        # Check nearest valid outlets
        if self.file_inlets and not self.nearest_valid_inlet_outlets:
            feedback.pushWarning(self.tr("Error getting nearest valid outlet for inlets."))
        elif self.file_inlets and self.nearest_valid_inlet_outlets and 'result' in self.nearest_valid_inlet_outlets.keys() and self.nearest_valid_inlet_outlets['result'] == 'blank':
            feedback.setProgressText(self.tr(f"No inlets without outlet assigned."))
            self.nearest_valid_inlet_outlets = {}
        elif self.file_inlets and self.nearest_valid_inlet_outlets and 'result' not in self.nearest_valid_inlet_outlets.keys():
            feedback.setProgressText(self.tr(f"Inlets without outlet assigned: {len(self.nearest_valid_inlet_outlets)}"))

        if self.file_pinlets and not self.nearest_valid_pinlet_outlets:
            feedback.pushWarning(self.tr("Error getting nearest valid outlet for pinlets."))
        elif self.file_pinlets and self.nearest_valid_pinlet_outlets and 'result' in self.nearest_valid_pinlet_outlets.keys() and self.nearest_valid_pinlet_outlets['result'] == 'blank':
            feedback.setProgressText(self.tr(f"No pinlets without outlet assigned."))
            self.nearest_valid_pinlet_outlets = {}
        elif self.file_pinlets and self.nearest_valid_pinlet_outlets:
            feedback.setProgressText(self.tr(f"Pinlets without outlet assigned: {len(self.nearest_valid_pinlet_outlets)}"))
        feedback.setProgress(60)

        return {}

    def postProcessAlgorithm(self, context, feedback: Feedback):
        skipped_inlets: List[str] = []
        skipped_pinlets: List[str] = []
        # Set the outlet code in the inlet and pinlet layer
        if self.nearest_valid_inlet_outlets is not None:
            self.file_inlets.startEditing()
            for inlet_code, outlet_code in self.nearest_valid_inlet_outlets.items():
                if feedback.isCanceled():
                    self.file_inlets.rollBack()
                    return {}
                if outlet_code is None:
                    skipped_inlets.append(str(inlet_code))
                    continue
                # Update the outlet code in the inlet layer
                for feature in self.file_inlets.getFeatures():
                    try:
                        if feature['code'] == inlet_code:
                            feature['outlet_node'] = outlet_code
                            self.file_inlets.updateFeature(feature)
                            break
                    except Exception as e:
                        self.file_inlets.rollBack()
                        feedback.pushWarning(self.tr(f"Error updating inlet {feature.id()}: {str(e)}"))
                        skipped_inlets.append(str(inlet_code))
            if self.file_inlets.isEditable():
                self.file_inlets.commitChanges()
            feedback.setProgressText(self.tr(f"Inlets skipped[{len(skipped_inlets)}]: {skipped_inlets}"))
            feedback.setProgressText(self.tr(f"Inlets updated[{len(self.nearest_valid_inlet_outlets)-len(skipped_inlets)}/{len(self.nearest_valid_inlet_outlets)}]"))

        if self.nearest_valid_pinlet_outlets is not None:
            self.file_pinlets.startEditing()
            for pinlet_code, outlet_code in self.nearest_valid_pinlet_outlets.items():
                if feedback.isCanceled():
                    self.file_pinlets.rollBack()
                    return {}
                if outlet_code is None:
                    skipped_pinlets.append(str(pinlet_code))
                    continue
                # Update the outlet code in the inlet layer
                for feature in self.file_pinlets.getFeatures():
                    try:
                        if feature['code'] == pinlet_code:
                            feature['outlet_node'] = outlet_code
                            self.file_pinlets.updateFeature(feature)
                            break
                    except Exception as e:
                        self.file_pinlets.rollBack()
                        feedback.pushWarning(self.tr(f"Error updating pinlet {feature.id()}: {str(e)}"))
            if self.file_pinlets.isEditable():
                self.file_pinlets.commitChanges()
            feedback.setProgressText(self.tr(f"Pinlets skipped({len(skipped_pinlets)}): {skipped_pinlets}"))
            feedback.setProgressText(self.tr(f"Pinlets updated({len(self.nearest_valid_pinlet_outlets)-len(skipped_pinlets)}/{len(self.nearest_valid_pinlet_outlets)})"))

        feedback.setProgressText(self.tr(f"Outlets assigned to inlets and pinlets."))
        feedback.setProgress(100)
        return {}

    def getNearestValidOutlets(self, nearest_layer: QgsVectorLayer, feedback: Feedback) -> Optional[dict[str,Optional[str]]]:
        """
        Get the nearest valid outlet for each inlet from the nearest layer.
        """
        nearest_outlets: dict[str,Optional[str]] = {}
        nearest_outlets_list = {}

        # Group nearest outlets by inlet id
        necessary_fields: List[str] = ['code', 'code_2', 'elev', 'top_elev', 'distance']
        for feature in nearest_layer.getFeatures():
            if feedback.isCanceled():
                return None
            for field in necessary_fields:
                if field not in feature.attributeMap().keys():
                    feedback.pushWarning(self.tr(f"Field {field} not found in inlet, pinlet or outlet."))
                    return None
                if str(feature[field]) == 'NULL' or feature[field] is None:
                    feedback.pushWarning(self.tr(f"Field {field} is None in inlet, pinlet or outlet."))
                    return None
            if str(feature['outlet_node']) != 'NULL':
                continue

            inlet_code: str = feature['code']
            outlet_values = {'code': feature['code_2'], 'elev': feature['elev'], 'distance': feature['distance']}

            if inlet_code in nearest_outlets_list.keys():
                nearest_outlets_list[inlet_code]['outlets'].append(outlet_values)
            else:
                nearest_outlets_list[inlet_code] = {'elev' : feature['top_elev'], 'outlets': [outlet_values]}

        # Get the nearest valid outlet for each inlet
        for inlet_code, values in nearest_outlets_list.items():
            if feedback.isCanceled():
                return None
            if len(values['outlets']) == 1:
                nearest_outlets[inlet_code] = values['outlets'][0]['code']
            else:
                # Sort outlets by distance and take the one with the highest elevation
                values['outlets'].sort(key=lambda x: x['distance'])
                for outlet in values['outlets']:
                    if outlet['elev'] >= values['elev']:
                        continue
                    else:
                        nearest_outlets[inlet_code] = outlet['code']
                        break
                if inlet_code not in nearest_outlets.keys():
                    nearest_outlets[inlet_code] = None
        if not nearest_outlets:
            return {'result': 'blank'}
        return nearest_outlets

    def checkParameterValues(self, parameters, context):
        error_message = ''
        inlet_layer = parameters[self.FILE_INLETS]
        pinlet_layer = parameters[self.FILE_PINLETS]
        outlet_layer = parameters[self.FILE_OUTLETS]

        if inlet_layer is None and pinlet_layer is None:
            return False, 'Is required at least one layer selected to Inlet or Pinlet.'

        expected_inlet_layer = tools_qgis.get_layer_by_tablename('inlet')
        if expected_inlet_layer and inlet_layer != expected_inlet_layer.id():
            error_message += self.tr(f'Wrong inlet layer selected. \nExpected layer: {expected_inlet_layer.name()} - Path: {expected_inlet_layer.source()}\n\n')
        elif expected_inlet_layer is None:
            error_message += self.tr(f'Wrong inlet layer selected. Expected layer not found\n')


        expected_pinlet_layer = tools_qgis.get_layer_by_tablename('pinlet')
        if expected_pinlet_layer and pinlet_layer != expected_pinlet_layer.id():
            error_message += self.tr(f'Wrong pinlet layer selected. \nExpected layer: {expected_pinlet_layer.name()} - Path: {expected_pinlet_layer.source()}\n\n')
        elif expected_pinlet_layer is None:
            error_message += self.tr(f'Wrong pinlet layer selected. Expected layer not found\n')

        expected_outlet_layer = tools_qgis.get_layer_by_tablename('inp_junction')
        if expected_outlet_layer and outlet_layer != expected_outlet_layer.id():
            error_message += self.tr(f'Wrong outlet layer selected. \nExpected layer: {expected_outlet_layer.name()} - Path: {expected_outlet_layer.source()}\n\n')
        elif expected_outlet_layer is None:
            error_message += self.tr(f'Wrong outlet layer selected. Expected layer not found\n')

        if len(error_message) > 0:
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""This tool allows you to set the nearest and valid outlet to the inlet and pinlet features which do not have an outlet assigned.\n
        This algorithm will only work if the Drain Junction layer and Drain Inlet or Drain Pinlet layers are loaded on the project.\n
        There are some attributes that cannot be None from Inlet(code, top_elev), Pinlet(code, top_elev) and Junction(code, elev).""")

    def name(self):
        return 'SetOutletForInlets'

    def displayName(self):
        return self.tr('Set Outlet for Inlets')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SetOutletForInlets()
