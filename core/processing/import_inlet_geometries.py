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
    QgsProcessingParameterField,
    QgsFeature,
    QgsProcessingParameterDefinition,
    QgsProject,
    QgsVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingFeatureSourceDefinition,
    QgsFeatureRequest
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ...core.utils import tools_dr, Feedback
from ... import global_vars
from typing import Optional
import os
import processing


class ImportInletGeometries(QgsProcessingAlgorithm):
    """
    Class to import inlet geometries from another layer.
    """
    FILE_SOURCE = 'FILE_SOURCE'
    FILE_TARGET = 'FILE_TARGET'
    FIELD_TOP_ELEV = 'FIELD_TOP_ELEV'
    BOOL_SELECTED_FEATURES = 'BOOL_SELECTED_FEATURES'

    bool_selected_features: bool = False

    dao: DrGpkgDao = tools_gpkgdao.DrGpkgDao()

    converted_geometries_layer: Optional[QgsVectorLayer] = None
    file_target: Optional[QgsVectorLayer] = None
    field_map: Optional[dict] = None
    unique_fields: Optional[dict] = None

    def initAlgorithm(self, config):
        """
        inputs and output of the algorithm
        """
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.FILE_SOURCE,
                self.tr('Source layer'),
                types=[QgsProcessing.SourceType.VectorPoint, QgsProcessing.SourceType.VectorPolygon]
            )
        )
        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SELECTED_FEATURES,
            description=self.tr('Selected features only'),
            defaultValue=False
        ))
        target_layer: QgsVectorLayer = tools_qgis.get_layer_by_tablename('inlet')
        target_layer_param = QgsProcessingParameterVectorLayer(
            self.FILE_TARGET,
            self.tr('Target layer (inlet or pinlet)'),
            types=[QgsProcessing.SourceType.VectorPoint, QgsProcessing.SourceType.VectorPolygon]
        )
        if target_layer:
            target_layer_param.setDefaultValue(target_layer)
        self.addParameter(target_layer_param)
        top_elev = QgsProcessingParameterField(
            self.FIELD_TOP_ELEV,
            self.tr('Select *top_elev* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        top_elev.setFlags(top_elev.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(top_elev)


    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        file_source: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_SOURCE, context)

        self.field_map = {
            "custom_code": None,
            "descript": None,
            "outlet_node": None,
            "outlet_type": None,
            "top_elev": next(iter(self.parameterAsFields(parameters, self.FIELD_TOP_ELEV, context)), None),
            "width": None,
            "length": None,
            "depth": None,
            "method": None,
            "weir_cd": None,
            "orifice_cd": None,
            "a_param": None,
            "b_param": None,
            "efficiency": None,
            "annotation": None
        }

        feedback.setProgressText(self.tr('done \n'))
        feedback.setProgress(12)

        # get inlet layer
        self.file_target = self.parameterAsVectorLayer(parameters, self.FILE_TARGET, context)
        if self.file_target is None:
            feedback.reportError(self.tr('Target layer not found.'))
            return {}
        feedback.setProgressText(self.tr('Target layer found.'))

        self.bool_selected_features: bool = self.parameterAsBoolean(parameters, self.BOOL_SELECTED_FEATURES, context)

        # check layer types
        feedback.setProgressText(self.tr('Checking layer types.'))
        feedback.setProgress(13)
        if file_source.geometryType() != self.file_target.geometryType():
            feedback.reportError(self.tr('Layer types do not match.'))
            return

        # set unique fields
        feedback.setProgress(15)
        self.unique_fields = {'custom_code': []}

        # delete innecesary values from geometry
        if self.bool_selected_features:
            result = processing.run("native:dropmzvalues", {
                'INPUT': QgsProcessingFeatureSourceDefinition(file_source.source(),
                                                              selectedFeaturesOnly=True, featureLimit=-1,
                                                              geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                'DROP_M_VALUES': True, 'DROP_Z_VALUES': True,
                'OUTPUT': 'memory:'
            })
        else:
            result = processing.run("native:dropmzvalues", {
                'INPUT': file_source, 'DROP_M_VALUES': True, 'DROP_Z_VALUES': True, 'OUTPUT': 'memory:'
            })
        self.converted_geometries_layer = result['OUTPUT']

        return {}

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """ Import features """

        if self.converted_geometries_layer is None or self.file_target is None or self.field_map is None or self.unique_fields is None:
            return {}

        db_filepath: str = f"{global_vars.project_vars['project_gpkg']}"
        db_filepath: str = f"{QgsProject.instance().absolutePath()}{os.sep}{db_filepath}"
        self.dao.init_db(db_filepath)

        if not self._insert_data(self.converted_geometries_layer, self.file_target, self.field_map, self.unique_fields, feedback, batch_size=5000):
            feedback.reportError(self.tr('Error during import.'))
            self.dao.close_db()
            return {}
        self.dao.close_db()
        feedback.setProgressText(self.tr("Importing process finished."))
        feedback.setProgress(100)
        return {}

    def _insert_data(self, source_layer: QgsVectorLayer, target_layer: QgsVectorLayer, field_map: dict, unique_fields: dict, feedback: Feedback, batch_size: int = 1000):
        """Copies features from the source layer to the target layer with mapped fields, committing in batches."""

        num_features: int = source_layer.featureCount()
        imported_features: int = 0
        feature_index: int = 1
        skiped_features: list[int] = list()

        feedback.setProgressText(self.tr(f"Importing {num_features} features from {source_layer.name()}..."))

        # Get the target field names in order
        target_field_names: list[str] = [field.name() for field in target_layer.fields()]

        for feature in target_layer.getFeatures():
            for field in unique_fields.keys():
                if field in target_field_names and str(feature[field]) != 'NULL':
                    unique_fields[field].append(feature[field])

        features_to_add: list[QgsFeature] = list()

        for feature in source_layer.getFeatures():
            repeated_params: bool = False
            new_feature: QgsFeature = QgsFeature(target_layer.fields())

            # Map attributes efficiently
            attributes: list = [None] * len(target_field_names)
            for tgt_field, src_field in field_map.items():
                if src_field is None:
                    src_field = tgt_field
                if tgt_field in target_field_names:
                    src_value = None
                    if isinstance(src_field, list):
                        for field in src_field:
                            src_value = feature[field]
                            if src_value is not None:
                                if tgt_field in unique_fields.keys():
                                    if feature[field] in unique_fields[field]:
                                        src_value = None
                                        skiped_features.append(feature.id())
                                break
                    else:
                        try:
                            if tgt_field in unique_fields.keys():
                                if feature[src_field] in unique_fields[tgt_field]:
                                    repeated_params = True
                                    skiped_features.append(feature.id())
                                    break
                            src_value = feature[src_field]
                        except KeyError:
                            src_value = None
                    attributes[target_field_names.index(tgt_field)] = src_value
            feedback.setProgress(tools_dr.lerp_progress(int(feature_index*100/num_features), 16, 90))
            feature_index += 1
            if (repeated_params):
                continue
            new_feature.setAttributes(attributes)
            if not feature.geometry().isGeosValid():
                feedback.reportError(self.tr(f"Invalid geometry for feature ID {feature.id()}"))
                skiped_features.append(feature.id())
                continue

            new_feature.setGeometry(feature.geometry())  # Preserve geometry
            features_to_add.append(new_feature)

            # Commit in batches
            if len(features_to_add) >= batch_size:
                try:
                    # disable inlet triggers
                    if not self.enable_triggers(feedback, False):
                        return
                    # add features
                    if not target_layer.isEditable():
                        target_layer.startEditing()
                    target_layer.addFeatures(features_to_add)
                    target_layer.commitChanges()
                    imported_features += len(features_to_add)
                    # update code
                    if not self.execute_after_import_fct(feedback):
                        return False
                    # enable inlet triggers
                    if not self.enable_triggers(feedback, True):
                        return False
                    feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}"))
                    if len(skiped_features) > 0:
                        feedback.setProgressText(self.tr(f"Skipped features: ({len(skiped_features)})"))
                    features_to_add.clear()
                except Exception as e:
                    feedback.reportError(self.tr(f"Error adding features: {e}"))
                    target_layer.rollBack()
                    return False
        # Commit any remaining features
        if features_to_add:
            try:
                # disable inlet triggers
                if not self.enable_triggers(feedback, False):
                    return
                # add features
                if not target_layer.isEditable():
                    target_layer.startEditing()
                target_layer.addFeatures(features_to_add)
                target_layer.commitChanges()
                imported_features += len(features_to_add)
                # update code
                if not self.execute_after_import_fct(feedback):
                    return False
                # enable inlet triggers
                if not self.enable_triggers(feedback, True):
                    return False
                feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}"))
                if len(skiped_features) > 0:
                    feedback.setProgressText(self.tr(f"Skipped features: ({len(skiped_features)})"))
            except Exception as e:
                feedback.reportError(self.tr(f"Error adding features: {e}"))
                target_layer.rollBack()
                return False
        return True

    def enable_triggers(self, feedback: Feedback, enable: bool):
        """Enable or disable triggers."""
        trg_path: str = os.path.join(global_vars.plugin_dir, 'dbmodel', 'trg')
        if enable:
            f_to_read: str = os.path.join(trg_path, 'trg_create.sql')
            with open(f_to_read, 'r', encoding="utf8") as f:
                sql: str = f.read()
        else:
            f_to_read: str = os.path.join(trg_path, 'trg_delete.sql')
            with open(f_to_read, 'r', encoding="utf8") as f:
                sql: str = f.read()
        status = self.dao.execute_script_sql(str(sql))
        if not status:
            feedback.setProgressText(self.tr(f"Error {f_to_read} not executed"))
            return False
        feedback.setProgressText(self.tr(f"File {f_to_read} executed"))
        return True

    def execute_after_import_fct(self, feedback: Feedback):
        """Execute the function after import."""
        fct_path: str = os.path.join(global_vars.plugin_dir, 'dbmodel', 'fct', 'fct_after_import_inlet_geometries.sql')
        with open(fct_path, 'r', encoding="utf8") as f:
            sql: str = f.read()
        status = self.dao.execute_script_sql(str(sql))
        if not status:
            feedback.setProgressText(self.tr(f"Error {fct_path} not executed"))
            return False
        feedback.setProgressText(self.tr(f"File {fct_path} executed"))
        return True

    def checkParameterValues(self, parameters, context):
        """ Check if parameters are valid """

        error_message = ''
        source_layer : QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_SOURCE, context)
        target_layer : QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_TARGET, context)
        inlet_layer = tools_qgis.get_layer_by_tablename('inlet')
        pinlet_layer = tools_qgis.get_layer_by_tablename('pinlet')

        if source_layer is None:
            error_message += self.tr('Source layer not found in this schema.\n\n')
        if target_layer is None:
            error_message += self.tr('Target layer not found in this schema.\n\n')
        if inlet_layer is None:
            error_message += self.tr('Inlet layer not found in this schema.\n\n')
        if pinlet_layer is None:
            error_message += self.tr('Pinlet layer not found in this schema.\n\n')

        if len(error_message) > 0:
            return False, error_message

        if source_layer.geometryType() != target_layer.geometryType():
            error_message += self.tr('Source and target layer types do not match.\n\n')
            return False, error_message

        if target_layer != inlet_layer and target_layer != pinlet_layer:
            error_message += self.tr('Target layer is not an inlet or pinlet layer.\n\n')
            return False, error_message

        if len(error_message) > 0:
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""Imports features from a source layer into the project's Drain-Inlet or Drain-Pinlet layer, with options to map fields and avoid duplicates. 
                       Only valid geometries are imported, and the process is optimized for large datasets. 
                       Use this tool to quickly transfer and match inlet features from other layers.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'ImportInletGeometries'

    def displayName(self):
        return self.tr('Import Inlet Geometries')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportInletGeometries()
