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
    QgsProcessingParameterRasterLayer,
    QgsRasterLayer,
    QgsProject,
    QgsProcessingParameterBoolean,
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
from ...lib.tools_gpkgdao import DrGpkgDao
from ..utils import Feedback, tools_dr
from typing import Optional, List
import processing


class SetOutletForRoofs(QgsProcessingAlgorithm):
    """
    Class to set outlet for roof.
    """
    FILE_ROOFS = 'FILE_ROOFS'
    FILE_ELEV_RASTER = 'FILE_ELEV_RASTER'
    FILE_OUTLETS = 'FILE_OUTLETS'
    BOOL_FORCE_BELOWS = 'BOOL_FORCE_BELOWS'
    BOOL_SELECTED_FEATURES = 'BOOL_SELECTED_FEATURES'

    nearest_valid_roof_outlets: Optional[dict[str, Optional[str]]] = None

    file_roofs: QgsVectorLayer = None
    roof_elev_layer: QgsVectorLayer = None
    bool_force_belows: bool = False
    skipped_roofs: list[str] = []
    below_roofs: list[str] = []
    skipped_from_near: int = 0
    bool_selected_features: bool = False

    dao: DrGpkgDao = tools_gpkgdao.DrGpkgDao()

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        roof_layer: QgsVectorLayer = tools_qgis.get_layer_by_tablename('roof')
        roof_layer_param = QgsProcessingParameterVectorLayer(
            name=self.FILE_ROOFS,
            description=self.tr('Roof layer'),
            types=[QgsProcessing.SourceType.VectorPolygon],
            optional=True
        )
        if roof_layer:
            roof_layer_param.setDefaultValue(roof_layer)
        self.addParameter(roof_layer_param)

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SELECTED_FEATURES,
            description=self.tr('Selected features only'),
            defaultValue=False
        ))

        elev_raster_layer: QgsRasterLayer = tools_qgis.get_layer_by_layername('dem')
        elev_raster_layer_param = QgsProcessingParameterRasterLayer(
            name=self.FILE_ELEV_RASTER,
            description=self.tr('Elevation raster layer'),
            optional=True
        )
        if elev_raster_layer:
            elev_raster_layer_param.setDefaultValue(elev_raster_layer)
        self.addParameter(elev_raster_layer_param)

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
            description=self.tr('Force the roofs which are below'),
            defaultValue=False
        ))

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        self.skipped_roofs = []
        self.below_roofs = []
        self.skipped_from_near = 0

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        self.file_roofs: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_ROOFS, context)
        file_elev_raster: QgsRasterLayer = self.parameterAsRasterLayer(parameters, self.FILE_ELEV_RASTER, context)
        file_outlets: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_OUTLETS, context)
        self.bool_force_belows: bool = self.parameterAsBoolean(parameters, self.BOOL_FORCE_BELOWS, context)
        self.bool_selected_features: bool = self.parameterAsBoolean(parameters, self.BOOL_SELECTED_FEATURES, context)
        feedback.setProgress(10)

        # Get roof layer with minimum elevation for each feature
        self.roof_elev_layer = self.getRoofElevationFromRaster(self.file_roofs, file_elev_raster)

        if self.roof_elev_layer is None:
            feedback.pushWarning(self.tr("Error getting minimum roof elevation"))
            return {}

        neighbor_limit: int = 10

        # Generate the nearest outlet for each roof with QGIS processing algorithm: Join by nearest
        if self.file_roofs:
            try:
                nearest_roof_outlets: QgsVectorLayer = processing.run("native:joinbynearest", {
                    'INPUT': self.roof_elev_layer,
                    'INPUT_2': file_outlets,
                    'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                    'NEIGHBORS': neighbor_limit, 'MAX_DISTANCE': None, 'OUTPUT': 'memory:'
                })['OUTPUT']
                self.nearest_valid_roof_outlets = self.getNearestValidOutlets(nearest_roof_outlets, feedback)
            except:
                self.nearest_valid_roof_outlets = None

        if feedback.isCanceled():
            return {}

        # Check nearest valid outlets
        if self.file_roofs and self.nearest_valid_roof_outlets is None:
            feedback.pushWarning(self.tr("Error getting nearest valid outlet for roofs."))
        elif self.file_roofs and self.nearest_valid_roof_outlets is not None and 'result' in self.nearest_valid_roof_outlets.keys() and self.nearest_valid_roof_outlets['result'] == 'blank':
            feedback.setProgressText(self.tr("No roofs without outlet assigned."))
            self.nearest_valid_roof_outlets = {}
        elif self.file_roofs and self.nearest_valid_roof_outlets is not None and 'result' not in self.nearest_valid_roof_outlets.keys():
            feedback.setProgressText(self.tr(f"Roofs without outlet assigned: {len(self.nearest_valid_roof_outlets)}"))

        feedback.setProgress(80)

        return {}

    def getRoofElevationFromRaster(self, roof_layer: QgsVectorLayer, raster_layer: QgsRasterLayer) -> Optional[QgsVectorLayer]:
        """ Return roof_layer with the minimum elvation for each roof """
        roof_elev_layer: Optional[QgsVectorLayer] = None

        if raster_layer is None:
            return roof_layer

        try:
            if not self.bool_selected_features:
                result = processing.run("native:zonalstatisticsfb", {
                    'INPUT': roof_layer,
                    'INPUT_RASTER': raster_layer,
                    'RASTER_BAND': 1, 'COLUMN_PREFIX': 'elev_', 'STATISTICS': [5], 'OUTPUT': 'memory:'
                })
            else:
                result = processing.run("native:zonalstatisticsfb", {
                    'INPUT': QgsProcessingFeatureSourceDefinition(roof_layer.source(),
                                                                  selectedFeaturesOnly=True, featureLimit=-1,
                                                                  geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'INPUT_RASTER': raster_layer,
                    'RASTER_BAND': 1, 'COLUMN_PREFIX': 'elev_', 'STATISTICS': [5], 'OUTPUT': 'memory:'
                })
            if result:
                roof_elev_layer = result['OUTPUT']
        except Exception:
            roof_elev_layer = None

        return roof_elev_layer

    def postProcessAlgorithm(self, context, feedback: Feedback, batch_size: int = 5000):
        """ Update features and create temporal layers """

        current_updated_roofs: int = 0
        updated_roofs: int = 0
        progress_index: int = 0

        roof_features: dict[str, QgsFeature] = {}
        for feature in self.file_roofs.getFeatures():
            roof_features[feature['code']] = feature

        # Set outlet code for roof
        if self.nearest_valid_roof_outlets is not None:
            self.file_roofs.startEditing()
            for roof_code, outlet_code in self.nearest_valid_roof_outlets.items():
                if feedback.isCanceled():
                    self.file_roofs.rollBack()
                    return {}
                if outlet_code is None:
                    self.skipped_roofs.append(str(roof_code))
                    continue
                if not self.file_roofs.isEditable():
                    self.file_roofs.startEditing()
                # Update outlet code in the roof layer
                try:
                    if roof_code in roof_features.keys():
                        roof_features[roof_code]['outlet_code'] = outlet_code
                        self.file_roofs.updateFeature(roof_features[roof_code])
                        current_updated_roofs += 1
                        updated_roofs += 1
                        if current_updated_roofs >= batch_size:
                            self.file_roofs.commitChanges()
                            current_updated_roofs = 0
                            feedback.setProgressText(self.tr(f"Roofs updated with a batch of {batch_size} [{(updated_roofs+self.skipped_from_near)}/{len(self.nearest_valid_roof_outlets)+self.skipped_from_near}]"))
                            feedback.setProgress(tools_dr.lerp_progress(int(((progress_index+1)/(len(self.nearest_valid_roof_outlets.keys())/batch_size))*100), 80, 98))
                            progress_index += 1
                            QApplication.processEvents()
                except Exception as e:
                    self.file_roofs.rollBack()
                    feedback.pushWarning(self.tr(f"Error updating roof {roof_code}: {str(e)}"))
                    self.skipped_roofs.append(str(roof_code))
            if self.file_roofs.isEditable():
                self.file_roofs.commitChanges()
            self.skipped_roofs = list(dict.fromkeys(self.skipped_roofs))
            self.below_roofs = list(dict.fromkeys(self.below_roofs))
            feedback.setProgressText(self.tr(f"Roofs skipped: ({len(self.skipped_roofs)})"))
            feedback.setProgressText(self.tr(f"Roofs setted below: ({len(self.below_roofs)})"))
            feedback.setProgressText(self.tr(f"Roofs updated[{(len(self.nearest_valid_roof_outlets)+self.skipped_from_near)-len(self.skipped_roofs)}/{len(self.nearest_valid_roof_outlets)+self.skipped_from_near}]"))
            feedback.setProgressText(self.tr("Outlets assigned for roofs."))

            if len(self.skipped_roofs) > 0 or len(self.below_roofs) > 0:
                # Create a temporal layer with skipped features and load it on QGIS
                temporal_features_layer: QgsVectorLayer = QgsVectorLayer("MultiPolygon?crs=EPSG:25831", "roof_features", "memory")
                temporal_features_layer.dataProvider().addAttributes(self.roof_elev_layer.fields())
                temporal_features_layer.dataProvider().addAttributes([QgsField("action", QVariant.String)])
                temporal_features_layer.updateFields()
                temporal_features_layer.startEditing()
                for feature in self.roof_elev_layer.getFeatures():
                    if feature['code'] in self.skipped_roofs:
                        new_feature = QgsFeature(temporal_features_layer.fields())
                        new_feature.setGeometry(feature.geometry())
                        attrs = feature.attributes()
                        extra_value = "SKIPPED"
                        attrs.append(extra_value)
                        new_feature.setAttributes(attrs)
                        temporal_features_layer.addFeature(new_feature)
                    elif feature['code'] in self.below_roofs:
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

                category_skipped = QgsRendererCategory("SKIPPED", symbol_skipped, "skipped_roofs")
                category_below = QgsRendererCategory("BELOW", symbol_below, "below_roofs")

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

    def getNearestValidOutlets(self, nearest_layer: QgsVectorLayer, feedback: Feedback) -> Optional[dict[str, Optional[str]]]:
        """
        Get nearest valid outlet for each roof from nearest layer.
        """
        nearest_outlets: dict[str, Optional[str]] = {}
        nearest_outlets_list = {}
        min_progress = 10
        max_progress = 80

        # Group nearest outlets by roof code
        necessary_fields: List[str] = ['code', 'code_2', 'elev', 'elev_min', 'distance']
        skipped_near_features: list[str] = []
        for index, feature in enumerate(nearest_layer.getFeatures()):
            feedback.setProgress(tools_dr.lerp_progress(int(((index+1)/nearest_layer.featureCount())*100), min_progress, max_progress))
            valid_attributes = True
            has_elevation_data = True
            if feedback.isCanceled():
                return None
            # Check if fields are None
            for field in necessary_fields:
                if field != 'elev_min' and field not in feature.attributeMap().keys():
                    feedback.pushWarning(self.tr(f"Field {field} not found in roof or outlet."))
                    return None
                fields = [field.name() for field in nearest_layer.fields()]
                if not field in fields or str(feature[field]) == 'NULL' or feature[field] is None:
                    if field == 'code':
                        return None
                    elif field in ['elev', 'elev_min']:
                        # Mark as having no elevation data but continue processing
                        has_elevation_data = False
                    else:
                        if feature['code'] in skipped_near_features:
                            valid_attributes = False
                            break
                        else:
                            feedback.pushWarning(self.tr(f"Field {field} is None in roof or outlet."))
                            skipped_near_features.append(feature['code'])
                            self.skipped_roofs.append(str(feature['code']))
                            self.skipped_from_near += 1
                        valid_attributes = False
                        break
            if str(feature['outlet_code']) != 'NULL' or not valid_attributes:
                continue

            roof_code: str = feature['code']
            outlet_values = {
                'code': feature['code_2'],
                'elev': feature['elev'] if has_elevation_data else None,
                'distance': feature['distance']
            }

            if roof_code in nearest_outlets_list.keys():
                nearest_outlets_list[roof_code]['outlets'].append(outlet_values)
            else:
                nearest_outlets_list[roof_code] = {
                    'elev': feature['elev_min'] if has_elevation_data else None,
                    'outlets': [outlet_values],
                    'has_elevation_data': has_elevation_data
                }
            if roof_code in skipped_near_features and roof_code in nearest_outlets_list:
                if nearest_outlets_list[roof_code] is not None:
                    self.skipped_roofs.remove(str(feature['code']))
                    self.skipped_from_near -= 1

        # Get nearest valid outlet for each roof
        for index, (roof_code, values) in enumerate(nearest_outlets_list.items()):
            feedback.setProgress(tools_dr.lerp_progress(int(((index+1)/len(nearest_outlets_list.keys()))*100), min_progress, max_progress))
            if feedback.isCanceled():
                return None
            if len(values['outlets']) == 1:
                nearest_outlets[roof_code] = values['outlets'][0]['code']
            else:
                # Sort outlets by distance
                values['outlets'].sort(key=lambda x: x['distance'])

                # If no elevation data available, just pick the nearest outlet
                if not values.get('has_elevation_data', True):
                    nearest_outlets[roof_code] = values['outlets'][0]['code']
                else:
                    # Apply elevation constraints when elevation data is available
                    min_outlet = None
                    for outlet in values['outlets']:
                        if outlet['elev'] is None:
                            # If this specific outlet has no elevation data, pick it as nearest
                            nearest_outlets[roof_code] = outlet['code']
                            break
                        elif outlet['elev'] >= values['elev'] and self.bool_force_belows:
                            if min_outlet is None or min_outlet['elev'] > outlet['elev']:
                                min_outlet = outlet
                            continue
                        elif outlet['elev'] >= values['elev'] and not self.bool_force_belows:
                            continue
                        else:
                            nearest_outlets[roof_code] = outlet['code']
                            break
                    if roof_code not in nearest_outlets.keys():
                        # Set outlet as None or set the minimum one. Depends on checkbox parameter "bool_force_belows"
                        if self.bool_force_belows and min_outlet is not None:
                            nearest_outlets[roof_code] = min_outlet['code']
                            self.below_roofs.append(roof_code)
                        else:
                            nearest_outlets[roof_code] = None
        if len(nearest_outlets.keys()) == 0:
            return {'result': 'blank'}
        return nearest_outlets

    def checkParameterValues(self, parameters, context):
        """ Check if parameters are valid """

        error_message = ''
        roof_layer = parameters[self.FILE_ROOFS]
        outlet_layer = parameters[self.FILE_OUTLETS]

        if roof_layer is None:
            error_message += self.tr('Roof layer not found in this schema.\n\n')

        if outlet_layer is None:
            error_message += self.tr('Outlet layer not found in this schema.\n\n')

        if len(error_message) > 0:
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""Assigns the nearest valid outlet to roof features that do not have an outlet set, using elevation data if available. 
                       Works with roof, outlet, and elevation raster layers, and offers an option to force assignment even if only a lower outlet is available. 
                       Use this tool to quickly connect roofs to their appropriate outlets.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'SetOutletForRoofs'

    def displayName(self):
        return self.tr('Set Outlet For Roofs')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SetOutletForRoofs()
