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
    QgsVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProject,
    QgsField,
    QgsSymbol,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsFeature,
    QgsFeatureRequest,
    QgsProcessingFeatureSourceDefinition
)
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtWidgets import QApplication
from ...lib import tools_qgis, tools_gpkgdao
from ..utils import tools_dr
from ...lib.tools_gpkgdao import DrGpkgDao
from ..utils import Feedback
from typing import Optional, List
import processing


class SetOutletForInlets(QgsProcessingAlgorithm):
    """
    Class to set outlet for inlet/pinlet.
    """
    FILE_INLETS = 'FILE_INLETS'
    FILE_PINLETS = 'FILE_PINLETS'
    FILE_OUTLETS = 'FILE_OUTLETS'
    BOOL_FORCE_BELOWS = 'BOOL_FORCE_BELOWS'
    BOOL_SELECTED_INLET_FEATURES = 'BOOL_SELECTED_INLET_FEATURES'
    BOOL_SELECTED_PINLET_FEATURES = 'BOOL_SELECTED_PINLET_FEATURES'

    nearest_valid_inlet_outlets: Optional[dict[str, Optional[str]]] = None
    nearest_valid_pinlet_outlets: Optional[dict[str, Optional[str]]] = None

    file_inlets: QgsVectorLayer = None
    file_pinlets: QgsVectorLayer = None
    bool_force_belows: bool = False
    skipped_inlets: list[str] = []
    skipped_pinlets: list[str] = []
    below_inlets: list[str] = []
    below_pinlets: list[str] = []
    skipped_from_near_inlet: int = 0
    skipped_from_near_pinlet: int = 0
    bool_selected_inlet_features: bool = False
    bool_selected_pinlet_features: bool = False

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

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SELECTED_INLET_FEATURES,
            description=self.tr('Selected features only'),
            defaultValue=False
        ))

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

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SELECTED_PINLET_FEATURES,
            description=self.tr('Selected features only'),
            defaultValue=False
        ))

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

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_FORCE_BELOWS,
            description=self.tr('Force the inlets/pinlets which are below'),
            defaultValue=False
        ))

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        self.skipped_inlets = []
        self.skipped_pinlets = []
        self.below_inlets = []
        self.below_pinlets = []

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        self.file_inlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_INLETS, context)
        self.file_pinlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_PINLETS, context)
        file_outlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_OUTLETS, context)
        self.bool_force_belows: bool = self.parameterAsBoolean(parameters, self.BOOL_FORCE_BELOWS, context)
        self.bool_selected_inlet_features: bool = self.parameterAsBoolean(parameters, self.BOOL_SELECTED_INLET_FEATURES, context)
        self.bool_selected_pinlet_features: bool = self.parameterAsBoolean(parameters, self.BOOL_SELECTED_PINLET_FEATURES, context)
        feedback.setProgress(10)

        neighbor_limit: int = 10

        # Generate the nearest outlet for each inlet and pinlet with QGIS processing algorithm: Join by nearest
        if not self.file_inlets and not self.file_pinlets:
            feedback.pushWarning(self.tr("Is required at least one layer selected to Inlet or Pinlet."))
            return {}

        if self.file_inlets:
            try:
                if not self.bool_selected_inlet_features:
                    nearest_inlet_outlets: QgsVectorLayer = processing.run("native:joinbynearest", {
                        'INPUT': self.file_inlets,
                        'INPUT_2': file_outlets,
                        'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                        'NEIGHBORS': neighbor_limit, 'MAX_DISTANCE': None, 'OUTPUT': 'memory:'
                    })['OUTPUT']
                else:
                    nearest_inlet_outlets: QgsVectorLayer = processing.run("native:joinbynearest", {
                        'INPUT': QgsProcessingFeatureSourceDefinition(self.file_inlets.source(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                        'INPUT_2': file_outlets,
                        'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                        'NEIGHBORS': neighbor_limit, 'MAX_DISTANCE': None, 'OUTPUT': 'memory:'
                    })['OUTPUT']
                self.nearest_valid_inlet_outlets = self.getNearestValidOutlets(nearest_inlet_outlets, feedback, True)
            except Exception:
                self.nearest_valid_inlet_outlets = None
        if self.file_pinlets:
            try:
                if not self.bool_selected_pinlet_features:
                    nearest_pinlet_outlets = processing.run("native:joinbynearest", {
                        'INPUT': self.file_pinlets,
                        'INPUT_2': file_outlets,
                        'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                        'NEIGHBORS': neighbor_limit, 'MAX_DISTANCE': None, 'OUTPUT': 'memory:'
                    })['OUTPUT']
                else:
                    nearest_pinlet_outlets = processing.run("native:joinbynearest", {
                        'INPUT': QgsProcessingFeatureSourceDefinition(self.file_pinlets.source(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                        'INPUT_2': file_outlets,
                        'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                        'NEIGHBORS': neighbor_limit, 'MAX_DISTANCE': None, 'OUTPUT': 'memory:'
                    })['OUTPUT']
                self.nearest_valid_pinlet_outlets = self.getNearestValidOutlets(nearest_pinlet_outlets, feedback, False)
            except Exception:
                self.nearest_valid_pinlet_outlets = None
        if feedback.isCanceled():
            return {}

        # Check nearest valid outlets
        if self.file_inlets and not self.nearest_valid_inlet_outlets:
            feedback.pushWarning(self.tr("Error getting nearest valid outlet for inlets."))
        elif self.file_inlets and self.nearest_valid_inlet_outlets and 'result' in self.nearest_valid_inlet_outlets.keys() and self.nearest_valid_inlet_outlets['result'] == 'blank':
            feedback.setProgressText(self.tr("No inlets without outlet assigned."))
            self.nearest_valid_inlet_outlets = {}
        elif self.file_inlets and self.nearest_valid_inlet_outlets and 'result' not in self.nearest_valid_inlet_outlets.keys():
            feedback.setProgressText(self.tr(f"Inlets without outlet assigned: {len(self.nearest_valid_inlet_outlets)}"))

        if self.file_pinlets and not self.nearest_valid_pinlet_outlets:
            feedback.pushWarning(self.tr("Error getting nearest valid outlet for pinlets."))
        elif self.file_pinlets and self.nearest_valid_pinlet_outlets and 'result' in self.nearest_valid_pinlet_outlets.keys() and self.nearest_valid_pinlet_outlets['result'] == 'blank':
            feedback.setProgressText(self.tr("No pinlets without outlet assigned."))
            self.nearest_valid_pinlet_outlets = {}
        elif self.file_pinlets and self.nearest_valid_pinlet_outlets:
            feedback.setProgressText(self.tr(f"Pinlets without outlet assigned: {len(self.nearest_valid_pinlet_outlets)}"))
        feedback.setProgress(80)

        return {}

    def postProcessAlgorithm(self, context, feedback: Feedback, batch_size: int = 5000):
        """ Update features and create temporal layers """

        current_updated_inlets: int = 0
        current_updated_pinlets: int = 0
        updated_inlets: int = 0
        updated_pinlets: int = 0
        inlet_progress_index: int = 0
        pinlet_progress_index: int = 0

        inlet_features: dict[str, QgsFeature] = {}
        for feature in self.file_inlets.getFeatures():
            inlet_features[feature['code']] = feature

        pinlet_features: dict[str, QgsFeature] = {}
        for feature in self.file_pinlets.getFeatures():
            pinlet_features[feature['code']] = feature

        # Set outlet code for inlet and pinlet
        if self.nearest_valid_inlet_outlets is not None:
            self.file_inlets.startEditing()
            for inlet_code, outlet_code in self.nearest_valid_inlet_outlets.items():
                if feedback.isCanceled():
                    self.file_inlets.rollBack()
                    return {}
                if outlet_code is None:
                    self.skipped_inlets.append(str(inlet_code))
                    continue

                if not self.file_inlets.isEditable():
                    self.file_inlets.startEditing()
                # Update outlet code in inlet layer
                try:
                    if inlet_code in inlet_features.keys():
                        inlet_features[inlet_code]['outlet_node'] = outlet_code
                        self.file_inlets.updateFeature(inlet_features[inlet_code])
                        current_updated_inlets += 1
                        updated_inlets += 1
                        if current_updated_inlets >= batch_size:
                            self.file_inlets.commitChanges()
                            current_updated_inlets = 0
                            feedback.setProgressText(self.tr(f"Inlets updated with batch of {batch_size}[{updated_inlets}/{len(self.nearest_valid_inlet_outlets)}]"))
                            feedback.setProgress(tools_dr.lerp_progress(int(((inlet_progress_index + 1) / (len(self.nearest_valid_inlet_outlets.keys()) / batch_size)) * 100), 80, 89))
                            inlet_progress_index += 1
                            QApplication.processEvents()
                except Exception as e:
                    self.file_inlets.rollBack()
                    feedback.pushWarning(self.tr(f"Error updating inlet {inlet_code}: {str(e)}"))
                    self.skipped_inlets.append(str(inlet_code))
            if self.file_inlets.isEditable():
                self.file_inlets.commitChanges()
            self.skipped_inlets = list(dict.fromkeys(self.skipped_inlets))
            self.below_inlets = list(dict.fromkeys(self.below_inlets))
            feedback.setProgressText(self.tr(f"Inlets skipped: ({len(self.skipped_inlets)})"))
            feedback.setProgressText(self.tr(f"Inlets setted below: ({len(self.below_inlets)})"))
            feedback.setProgressText(self.tr(f"Inlets updated[{len(self.nearest_valid_inlet_outlets) - len(self.skipped_inlets)}/{len(self.nearest_valid_inlet_outlets)}]"))
            feedback.setProgressText(self.tr("Outlets assigned for inlets."))

        if self.nearest_valid_pinlet_outlets is not None:
            self.file_pinlets.startEditing()
            for pinlet_code, outlet_code in self.nearest_valid_pinlet_outlets.items():
                if feedback.isCanceled():
                    self.file_pinlets.rollBack()
                    return {}
                if outlet_code is None:
                    self.skipped_pinlets.append(str(pinlet_code))
                    continue
                if not self.file_pinlets.isEditable():
                    self.file_pinlets.startEditing()
                # Update outlet code in pinlet layer
                try:
                    if pinlet_code in pinlet_features.keys():
                        pinlet_features[pinlet_code]['outlet_node'] = outlet_code
                        self.file_pinlets.updateFeature(pinlet_features[pinlet_code])
                        current_updated_pinlets += 1
                        updated_pinlets += 1
                        if current_updated_pinlets >= batch_size:
                            self.file_pinlets.commitChanges()
                            current_updated_pinlets = 0
                            feedback.setProgressText(self.tr(f"Pinlets updated with batch of {batch_size}[{updated_pinlets}/{len(self.nearest_valid_pinlet_outlets)}]"))
                            feedback.setProgress(tools_dr.lerp_progress(int((((pinlet_progress_index + 1) / (len(self.nearest_valid_pinlet_outlets.keys()) / batch_size)) * 100)), 89, 98))
                            pinlet_progress_index += 1
                            QApplication.processEvents()
                except Exception as e:
                    self.file_pinlets.rollBack()
                    feedback.pushWarning(self.tr(f"Error updating pinlet {pinlet_code}: {str(e)}"))
                    self.skipped_pinlets.append(str(pinlet_code))
            if self.file_pinlets.isEditable():
                self.file_pinlets.commitChanges()
            self.skipped_pinlets = list(dict.fromkeys(self.skipped_pinlets))
            self.below_pinlets = list(dict.fromkeys(self.below_pinlets))
            feedback.setProgressText(self.tr(f"Pinlets skipped: ({len(self.skipped_pinlets)})"))
            feedback.setProgressText(self.tr(f"Pinlets setted below: ({len(self.below_pinlets)})"))
            feedback.setProgressText(self.tr(f"Pinlets updated[{len(self.nearest_valid_pinlet_outlets) - len(self.skipped_pinlets)}/{len(self.nearest_valid_pinlet_outlets)}]"))
            feedback.setProgressText(self.tr("Outlets assigned for pinlets."))

        if len(self.skipped_inlets) > 0 or len(self.below_inlets) > 0:
            # Create a temporal layer with skipped features and load it on QGIS
            srid = QgsProject.instance().crs().authid()
            temporal_features_layer: QgsVectorLayer = QgsVectorLayer(f"Point?crs={srid}", "inlet_features", "memory")
            temporal_features_layer.dataProvider().addAttributes(self.file_inlets.fields())
            temporal_features_layer.dataProvider().addAttributes([QgsField("action", QVariant.String)])
            temporal_features_layer.updateFields()
            temporal_features_layer.startEditing()
            for feature in self.file_inlets.getFeatures():
                if feature['code'] in self.skipped_inlets:
                    new_feature = QgsFeature(temporal_features_layer.fields())
                    new_feature.setGeometry(feature.geometry())
                    attrs = feature.attributes()
                    extra_value = "SKIPPED"
                    attrs.append(extra_value)
                    new_feature.setAttributes(attrs)
                    temporal_features_layer.addFeature(new_feature)
                elif feature['code'] in self.below_inlets:
                    new_feature = QgsFeature(temporal_features_layer.fields())
                    new_feature.setGeometry(feature.geometry())
                    attrs = feature.attributes()
                    extra_value = "BELOW"
                    attrs.append(extra_value)
                    new_feature.setAttributes(attrs)
                    temporal_features_layer.addFeature(new_feature)
            temporal_features_layer.commitChanges()

            symbol_skipped = QgsSymbol.defaultSymbol(temporal_features_layer.geometryType())
            symbol_skipped.setColor(QColor("purple"))

            symbol_below = QgsSymbol.defaultSymbol(temporal_features_layer.geometryType())
            symbol_below.setColor(QColor("red"))

            category_skipped = QgsRendererCategory("SKIPPED", symbol_skipped, "skipped_inlets")
            category_below = QgsRendererCategory("BELOW", symbol_below, "below_inlets")

            renderer = QgsCategorizedSymbolRenderer("action", [category_skipped, category_below])
            temporal_features_layer.setRenderer(renderer)

            group_name = "TEMPORAL"
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            if group is None:
                QgsProject.instance().layerTreeRoot().addGroup(group_name)
                group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            QgsProject.instance().addMapLayer(temporal_features_layer, False)
            group.addLayer(temporal_features_layer)

        if len(self.skipped_pinlets) > 0 or len(self.below_pinlets) > 0:
            # Create a temporal layer with skipped features and load it on QGIS
            srid = QgsProject.instance().crs().authid()
            temporal_features_layer: QgsVectorLayer = QgsVectorLayer(f"MultiPolygon?crs={srid}", "pinlet_features", "memory")
            temporal_features_layer.dataProvider().addAttributes(self.file_pinlets.fields())
            temporal_features_layer.dataProvider().addAttributes([QgsField("action", QVariant.String)])
            temporal_features_layer.updateFields()
            temporal_features_layer.startEditing()
            for feature in self.file_pinlets.getFeatures():
                if feature['code'] in self.skipped_pinlets:
                    new_feature = QgsFeature(temporal_features_layer.fields())
                    new_feature.setGeometry(feature.geometry())
                    attrs = feature.attributes()
                    extra_value = "SKIPPED"
                    attrs.append(extra_value)
                    new_feature.setAttributes(attrs)
                    temporal_features_layer.addFeature(new_feature)
                elif feature['code'] in self.below_pinlets:
                    new_feature = QgsFeature(temporal_features_layer.fields())
                    new_feature.setGeometry(feature.geometry())
                    attrs = feature.attributes()
                    extra_value = "BELOW"
                    attrs.append(extra_value)
                    new_feature.setAttributes(attrs)
                    temporal_features_layer.addFeature(new_feature)
            temporal_features_layer.commitChanges()

            symbol_skipped = QgsSymbol.defaultSymbol(temporal_features_layer.geometryType())
            symbol_skipped.setColor(QColor("purple"))

            symbol_below = QgsSymbol.defaultSymbol(temporal_features_layer.geometryType())
            symbol_below.setColor(QColor("red"))

            category_skipped = QgsRendererCategory("SKIPPED", symbol_skipped, "skipped_pinlets")
            category_below = QgsRendererCategory("BELOW", symbol_below, "below_pinlets")

            renderer = QgsCategorizedSymbolRenderer("action", [category_skipped, category_below])
            temporal_features_layer.setRenderer(renderer)

            group_name = "TEMPORAL"
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            if group is None:
                QgsProject.instance().layerTreeRoot().addGroup(group_name)
                group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            QgsProject.instance().addMapLayer(temporal_features_layer, False)
            group.addLayer(temporal_features_layer)

        feedback.setProgress(100)
        return {}

    def getNearestValidOutlets(self, nearest_layer: QgsVectorLayer, feedback: Feedback, isInlet: bool = True) -> Optional[dict[str, Optional[str]]]:
        """
        Get nearest valid outlet for each inlet/pinlet from nearest layer.
        """
        nearest_outlets: dict[str, Optional[str]] = {}
        nearest_outlets_list = {}
        min_progress = 10
        max_progress = 80

        if isInlet:
            min_progress = 10
            max_progress = 45
        else:
            min_progress = 45
            max_progress = 80

        # Group nearest outlets by inlet/pinlet code
        necessary_fields: List[str] = ['code', 'code_2', 'elev', 'top_elev', 'distance']
        skipped_near_features: list[str] = []
        for index, feature in enumerate(nearest_layer.getFeatures()):
            feedback.setProgress(tools_dr.lerp_progress(int(((index + 1) / nearest_layer.featureCount()) * 100), min_progress, int(max_progress / 2)))
            valid_attributes = True
            if feedback.isCanceled():
                return None
            # Check if fields are None
            for field in necessary_fields:
                if field not in feature.attributeMap().keys():
                    feedback.pushWarning(self.tr(f"Field {field} not found in inlet, pinlet or outlet."))
                    return None
                if str(feature[field]) == 'NULL' or feature[field] is None:
                    if field == 'code':
                        return None
                    else:
                        if feature['code'] in skipped_near_features:
                            valid_attributes = False
                            break
                        else:
                            feedback.pushWarning(self.tr(f"Field {field} is None in inlet, pinlet or outlet."))
                            skipped_near_features.append(feature['code'])
                            if isInlet:
                                self.skipped_inlets.remove(str(feature['code']))
                                self.skipped_from_near_inlet += 1
                            else:
                                self.skipped_pinlets.remove(str(feature['code']))
                                self.skipped_from_near_pinlet += 1
                        valid_attributes = False
                        break
            if str(feature['outlet_node']) != 'NULL' or not valid_attributes:
                continue

            inlet_code: str = feature['code']
            outlet_values = {'code': feature['code_2'], 'elev': feature['elev'], 'distance': feature['distance']}

            if inlet_code in nearest_outlets_list.keys():
                nearest_outlets_list[inlet_code]['outlets'].append(outlet_values)
            else:
                nearest_outlets_list[inlet_code] = {'elev': feature['top_elev'], 'outlets': [outlet_values]}
            if inlet_code in skipped_near_features and inlet_code in nearest_outlets_list:
                if nearest_outlets_list[inlet_code] is not None:
                    if isInlet:
                        self.skipped_inlets.remove(str(feature['code']))
                        self.skipped_from_near_inlet -= 1
                    else:
                        self.skipped_pinlets.remove(str(feature['code']))
                        self.skipped_from_near_pinlet -= 1

        # Get nearest valid outlet for each inlet/pinlet
        for index, (inlet_code, values) in enumerate(nearest_outlets_list.items()):
            feedback.setProgress(tools_dr.lerp_progress(int(((index + 1) / len(nearest_outlets_list.keys())) * 100), int(max_progress / 2), max_progress))
            if feedback.isCanceled():
                return None
            if len(values['outlets']) == 1:
                nearest_outlets[inlet_code] = values['outlets'][0]['code']
            else:
                # Sort outlets by distance and take the valid elevation one
                values['outlets'].sort(key=lambda x: x['distance'])
                min_outlet = None
                for outlet in values['outlets']:
                    if outlet['elev'] >= values['elev'] and self.bool_force_belows:
                        if min_outlet is None or min_outlet['elev'] > outlet['elev']:
                            min_outlet = outlet
                        continue
                    elif outlet['elev'] >= values['elev'] and not self.bool_force_belows:
                        continue
                    else:
                        nearest_outlets[inlet_code] = outlet['code']
                        break
                if inlet_code not in nearest_outlets.keys():
                    # Set outlet as None or set the minimum one. Depends on checkbox parameter "bool_set_nones"
                    if self.bool_force_belows and min_outlet is not None:
                        nearest_outlets[inlet_code] = min_outlet['code']
                        if isInlet:
                            self.below_inlets.append(inlet_code)
                        else:
                            self.below_pinlets.append(inlet_code)
                    else:
                        nearest_outlets[inlet_code] = None
        if not nearest_outlets:
            return {'result': 'blank'}
        return nearest_outlets

    def checkParameterValues(self, parameters, context):
        """ Check if parameters are valid """

        error_message = ''
        inlet_layer = parameters[self.FILE_INLETS]
        pinlet_layer = parameters[self.FILE_PINLETS]
        outlet_layer = parameters[self.FILE_OUTLETS]

        if inlet_layer is None:
            error_message += self.tr('Inlet layer not found in this schema.\n\n')

        if pinlet_layer is None:
            error_message += self.tr('Pinlet layer not found in this schema.\n\n')

        if outlet_layer is None:
            error_message += self.tr('Outlet layer not found in this schema.\n\n')

        if inlet_layer is None and pinlet_layer is None:
            return False, 'Is required at least one layer selected to Inlet or Pinlet.'
        elif (inlet_layer is not None or pinlet_layer is not None) and outlet_layer is not None:
            error_message = ''

        if len(error_message) > 0:
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""Assigns the nearest valid outlet to inlet and pinlet features that do not have an outlet set. 
                       Works with inlet, pinlet, and outlet layers, and offers an option to force assignment even if only a lower outlet is available. 
                       Use this tool to quickly connect inlets and pinlets to their appropriate outlets.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'SetOutletForInlets'

    def displayName(self):
        return self.tr('Set Outlet For Inlets')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SetOutletForInlets()
