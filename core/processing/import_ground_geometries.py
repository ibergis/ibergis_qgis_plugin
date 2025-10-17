"""
This file is part of IberGIS
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
    QgsFeatureRequest,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ...core.utils import tools_dr, Feedback
from ... import global_vars
from typing import Optional
import os
import processing


class ImportGroundGeometries(QgsProcessingAlgorithm):
    """
    Class to import ground geometries from another layer.
    """
    FILE_SOURCE = 'FILE_SOURCE'
    FIELD_CUSTOM_CODE = 'FIELD_CUSTOM_CODE'
    FIELD_DESCRIPT = 'FIELD_DESCRIPT'
    FIELD_CELLSIZE = 'FIELD_CELLSIZE'
    FIELD_ANNOTATION = 'FIELD_ANNOTATION'
    FIELD_LANDUSE = 'FIELD_LANDUSE'
    FIELD_CUSTOM_ROUGHNESS = 'FIELD_CUSTOM_ROUGHNESS'
    FIELD_SCS_CN = 'FIELD_SCS_CN'
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
                types=[QgsProcessing.SourceType.VectorPolygon]
            )
        )
        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SELECTED_FEATURES,
            description=self.tr('Selected features only'),
            defaultValue=False
        ))
        custom_code = QgsProcessingParameterField(
            self.FIELD_CUSTOM_CODE,
            self.tr('Select *custom code* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional=True
        )
        custom_code.setFlags(custom_code.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        descript = QgsProcessingParameterField(
            self.FIELD_DESCRIPT,
            self.tr('Select *descript* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional=True
        )
        descript.setFlags(descript.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        cellsize = QgsProcessingParameterField(
            self.FIELD_CELLSIZE,
            self.tr('Select *cell size* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        cellsize.setFlags(cellsize.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        annotation = QgsProcessingParameterField(
            self.FIELD_ANNOTATION,
            self.tr('Select *annotation* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional=True
        )
        annotation.setFlags(annotation.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        landuse = QgsProcessingParameterField(
            self.FIELD_LANDUSE,
            self.tr('Select *landuse* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional=True
        )
        landuse.setFlags(landuse.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        custom_roughness = QgsProcessingParameterField(
            self.FIELD_CUSTOM_ROUGHNESS,
            self.tr('Select *custom roughness* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        custom_roughness.setFlags(custom_roughness.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        scs_cn = QgsProcessingParameterField(
            self.FIELD_SCS_CN,
            self.tr('Select *scs_cn* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        scs_cn.setFlags(scs_cn.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(custom_code)
        self.addParameter(descript)
        self.addParameter(cellsize)
        self.addParameter(annotation)
        self.addParameter(landuse)
        self.addParameter(custom_roughness)
        self.addParameter(scs_cn)

    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        self.converted_geometries_layer = None
        self.file_target = None
        self.field_map = None
        self.unique_fields = None

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        file_source: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_SOURCE, context)

        self.field_map = {
            "custom_code": next(iter(self.parameterAsFields(parameters, self.FIELD_CUSTOM_CODE, context)), None),
            "descript": next(iter(self.parameterAsFields(parameters, self.FIELD_DESCRIPT, context)), None),
            "cellsize": next(iter(self.parameterAsFields(parameters, self.FIELD_CELLSIZE, context)), None),
            "annotation": next(iter(self.parameterAsFields(parameters, self.FIELD_ANNOTATION, context)), None),
            "landuse": next(iter(self.parameterAsFields(parameters, self.FIELD_LANDUSE, context)), None),
            "custom_roughness": next(iter(self.parameterAsFields(parameters, self.FIELD_CUSTOM_ROUGHNESS, context)), None),
            "scs_cn": next(iter(self.parameterAsFields(parameters, self.FIELD_SCS_CN, context)), None)
        }

        feedback.setProgressText(self.tr('done \n'))
        feedback.setProgress(12)

        # get ground layer
        self.file_target = tools_qgis.get_layer_by_tablename('ground')
        if self.file_target is None:
            feedback.reportError(self.tr('Target layer not found.'))
            return
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
            result = processing.run("native:dropmzvalues", {'INPUT': file_source, 'DROP_M_VALUES': True, 'DROP_Z_VALUES': True, 'OUTPUT': 'memory:'})
        self.converted_geometries_layer = result['OUTPUT']

        return {}

    def _get_landuse_types(self, feedback: Feedback) -> list[str]:
        """Get landuse types from database."""
        landuse_types: list[str] = list()
        sql: str = "SELECT idval FROM cat_landuses;"
        landuse_types_sql: Optional[list] = self.dao.get_rows(sql)
        if not landuse_types_sql:
            feedback.setProgressText(self.tr("No landuses found."))
        else:
            for item in landuse_types_sql:
                for subItem in item:
                    landuse_types.append(subItem)
        return landuse_types

    def _validate_landuse_types(self, source_layer: QgsVectorLayer, field_map: dict, landuse_types: list[str], feedback: Feedback) -> bool:
        """Check landuse types on source layer and report any unexistent ones."""
        unexistent_landuses: list[str] = list()
        field_map_name: str = 'landuse'
        if field_map['landuse'] is not None:
            field_map_name = field_map['landuse']

        for feature in source_layer.getFeatures():
            if field_map_name in feature.attributes() and feature[field_map_name] not in landuse_types and feature[field_map_name] not in unexistent_landuses and feature[field_map_name] not in ['NULL', None, 'null']:
                unexistent_landuses.append(feature[field_map_name])

        # check if there are unexistent landuses
        if len(unexistent_landuses) > 0:
            feedback.reportError(self.tr(f"Landuse types not found in database: {unexistent_landuses}."))
            return False
        return True

    def _build_unique_fields_dict(self, target_layer: QgsVectorLayer, unique_fields: dict, target_field_names: list[str]):
        """Build unique fields dictionary from existing target layer features."""
        for feature in target_layer.getFeatures():
            for field in unique_fields.keys():
                if field in target_field_names and str(feature[field]) != 'NULL':
                    unique_fields[field].append(feature[field])

    def _map_feature_attributes(self, feature: QgsFeature, target_layer: QgsVectorLayer, field_map: dict, target_field_names: list[str], unique_fields: dict, skiped_features: list[int]) -> tuple[QgsFeature, bool]:
        """Map attributes from source feature to target feature. Returns (new_feature, should_skip)."""
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

        new_feature.setAttributes(attributes)
        return new_feature, repeated_params

    def _commit_feature_batch(self, features_to_add: list[QgsFeature], target_layer: QgsVectorLayer, feedback: Feedback) -> bool:
        """Commit a batch of features to the target layer."""
        try:
            # disable ground triggers
            if not self.enable_triggers(feedback, False):
                return False
            # add features
            if not target_layer.isEditable():
                target_layer.startEditing()
            target_layer.addFeatures(features_to_add)
            target_layer.commitChanges()
            # update code
            if not self.execute_after_import_fct(feedback):
                return False
            # enable ground triggers
            if not self.enable_triggers(feedback, True):
                return False
            return True
        except Exception as e:
            feedback.reportError(self.tr(f"Error adding features: {e}"))
            target_layer.rollBack()
            return False

    def _insert_data(self, source_layer: QgsVectorLayer, target_layer: QgsVectorLayer, field_map: dict, unique_fields: dict, feedback: Feedback, batch_size: int = 1000):
        """Copies features from the source layer to the target layer with mapped fields, committing in batches."""

        num_features: int = source_layer.featureCount()
        imported_features: int = 0
        feature_index: int = 1
        skiped_features: list[int] = list()

        # get landuse types
        landuse_types: list[str] = self._get_landuse_types(feedback)

        # validate landuse types
        if not self._validate_landuse_types(source_layer, field_map, landuse_types, feedback):
            return False

        feedback.setProgressText(self.tr(f"Importing {num_features} features from {source_layer.name()}..."))

        # Get the target field names in order
        target_field_names: list[str] = [field.name() for field in target_layer.fields()]

        # Build unique fields dictionary
        self._build_unique_fields_dict(target_layer, unique_fields, target_field_names)

        features_to_add: list[QgsFeature] = list()

        for feature in source_layer.getFeatures():
            new_feature, repeated_params = self._map_feature_attributes(feature, target_layer, field_map, target_field_names, unique_fields, skiped_features)

            feedback.setProgress(tools_dr.lerp_progress(int(feature_index * 100 / num_features), 16, 90))
            feature_index += 1

            if repeated_params:
                continue

            if not feature.geometry().isGeosValid():
                feedback.reportError(self.tr(f"Invalid geometry for feature ID {feature.id()}"))
                skiped_features.append(feature.id())
                continue

            new_feature.setGeometry(feature.geometry())  # Preserve geometry
            features_to_add.append(new_feature)

            # Commit in batches
            if len(features_to_add) >= batch_size:
                if not self._commit_feature_batch(features_to_add, target_layer, feedback):
                    return False
                imported_features += len(features_to_add)
                feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}"))
                if len(skiped_features) > 0:
                    feedback.setProgressText(self.tr(f"Skipped features: ({len(skiped_features)})"))
                features_to_add.clear()

        # Commit any remaining features
        if features_to_add:
            if not self._commit_feature_batch(features_to_add, target_layer, feedback):
                return False
            imported_features += len(features_to_add)
            feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}"))
            if len(skiped_features) > 0:
                feedback.setProgressText(self.tr(f"Skipped features: ({len(skiped_features)})"))
        return True

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """ Import featues """

        if self.converted_geometries_layer is None or self.file_target is None or self.field_map is None or self.unique_fields is None:
            return {}

        db_filepath: str = f"{global_vars.project_vars['project_gpkg_path']}"
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
        fct_path: str = os.path.join(global_vars.plugin_dir, 'dbmodel', 'fct', 'fct_after_import_ground_geometries.sql')
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
        source_layer: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_SOURCE, context)
        target_layer = tools_qgis.get_layer_by_tablename('ground')

        if source_layer is None:
            error_message += self.tr('Source layer not found in this schema.\n\n')
        if target_layer is None:
            error_message += self.tr('Target layer not found in this schema.\n\n')

        if len(error_message) > 0:
            return False, error_message

        # get geometry types
        source_geom_type = QgsWkbTypes.displayString(source_layer.wkbType())
        target_geom_type = QgsWkbTypes.displayString(target_layer.wkbType())

        # check if source and target layer types match
        if source_geom_type != target_geom_type:
            error_message += self.tr(f'Source layer must be a single polygon layer. Found: {source_geom_type}.')
            return False, error_message
        return True, ''

    def shortHelpString(self):
        return self.tr("""Imports features from a source polygon layer into the project's Drain-Ground layer, with options to map fields and avoid duplicates. 
                       Only valid geometries are imported, and the process is optimized for large datasets. 
                       Use this tool to quickly transfer and match ground features from other layers.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'ImportGroundGeometries'

    def displayName(self):
        return self.tr('Import Ground Geometries')

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportGroundGeometries()
