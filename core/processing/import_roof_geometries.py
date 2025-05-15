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
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication
from ...lib import tools_qgis, tools_gpkgdao
from ...lib.tools_gpkgdao import DrGpkgDao
from ...core.utils import tools_dr, Feedback
from ... import global_vars
from typing import Optional
import os
import processing


class ImportRoofGeometries(QgsProcessingAlgorithm):
    """
    Class to import roof geometries from another layer.
    """
    FILE_SOURCE = 'FILE_SOURCE'
    FIELD_CUSTOM_CODE = 'FIELD_CUSTOM_CODE'
    FIELD_DESCRIPT = 'FIELD_DESCRIPT'
    FIELD_SLOPE = 'FIELD_SLOPE'
    FIELD_WIDTH = 'FIELD_WIDTH'
    FIELD_ROUGHNESS = 'FIELD_ROUGHNESS'
    FIELD_ISCONNECTED = 'FIELD_ISCONNECTED'
    FIELD_OUTLET_TYPE = 'FIELD_OUTLET_TYPE'
    FIELD_OUTLET_CODE = 'FIELD_OUTLET_CODE'
    FIELD_OUTLET_VOL = 'FIELD OUTLET_VOL'
    FIELD_STREET_VOL = 'FIELD_STREET_VOL'
    FIELD_INFILTR_VOL = 'FIELD_INFILTR_VOL'
    FIELD_ANNOTATION = 'FIELD_ANNOTATION'

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

        slope= QgsProcessingParameterField(
            self.FIELD_SLOPE,
            self.tr('Select *slope* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        slope.setFlags(slope.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        width= QgsProcessingParameterField(
            self.FIELD_WIDTH,
            self.tr('Select *width* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional=True
        )
        width.setFlags(width.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        roughness=QgsProcessingParameterField(
            self.FIELD_ROUGHNESS,
            self.tr('Select *roughness* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional= True
        )
        roughness.setFlags(roughness.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        isconnected=QgsProcessingParameterField(
            self.FIELD_ISCONNECTED,
            self.tr('Select *isconnected* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional= True
        )
        isconnected.setFlags(isconnected.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        outlet_type=QgsProcessingParameterField(
            self.FIELD_OUTLET_TYPE,
            self.tr('Select *outlet_type* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional= True
        )
        outlet_type.setFlags(outlet_type.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        outlet_code=QgsProcessingParameterField(
            self.FIELD_OUTLET_CODE,
            self.tr('Select *outlet_code* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.String,
            optional= True
        )
        outlet_code.setFlags(outlet_code.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        outlet_vol=QgsProcessingParameterField(
            self.FIELD_OUTLET_VOL,
            self.tr('Select *outlet_vol* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional= True
        )
        outlet_vol.setFlags(outlet_vol.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        street_vol=QgsProcessingParameterField(
            self.FIELD_STREET_VOL,
            self.tr('Select *street_vol* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional= True
        )
        street_vol.setFlags(street_vol.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        infiltr_vol=QgsProcessingParameterField(
            self.FIELD_INFILTR_VOL,
            self.tr('Select *Infiltr_vol* reference'),
            parentLayerParameterName=self.FILE_SOURCE,
            type=QgsProcessingParameterField.Numeric,
            optional= True
        )
        infiltr_vol.setFlags(infiltr_vol.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        annotation = QgsProcessingParameterField(
                self.FIELD_ANNOTATION,
                self.tr('Select *annotation* reference'),
                parentLayerParameterName=self.FILE_SOURCE,
                type=QgsProcessingParameterField.String,
                optional=True
            )
        annotation.setFlags(annotation.flags() | QgsProcessingParameterDefinition.FlagAdvanced)


        self.addParameter(custom_code)
        self.addParameter(descript)
        self.addParameter(slope)
        self.addParameter(width)
        self.addParameter(roughness)
        self.addParameter(isconnected)
        self.addParameter(outlet_type)
        self.addParameter(outlet_code)
        self.addParameter(outlet_vol)
        self.addParameter(street_vol)
        self.addParameter(infiltr_vol)
        self.addParameter(annotation)


    def processAlgorithm(self, parameters, context, feedback: Feedback):
        """
        main process algorithm of this tool
        """

        # reading geodata
        feedback.setProgressText(self.tr('Reading geodata and mapping fields:'))
        feedback.setProgress(1)

        file_source: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.FILE_SOURCE, context)

        self.field_map = {
            "custom_code": next(iter(self.parameterAsFields(parameters, self.FIELD_CUSTOM_CODE, context)), None),
            "descript": next(iter(self.parameterAsFields(parameters, self.FIELD_DESCRIPT, context)), None),
            "slope": next(iter(self.parameterAsFields(parameters, self.FIELD_SLOPE, context)), None),
            "width": next(iter(self.parameterAsFields(parameters, self.FIELD_WIDTH, context)), None),
            "roughness": next(iter(self.parameterAsFields(parameters, self.FIELD_ROUGHNESS, context)), None),
            "isconnected": next(iter(self.parameterAsFields(parameters, self.FIELD_ISCONNECTED, context)), None),
            "outlet_type": next(iter(self.parameterAsFields(parameters, self.FIELD_OUTLET_TYPE, context)), None),
            "outlet_code": next(iter(self.parameterAsFields(parameters, self.FIELD_OUTLET_CODE, context)), None),
            "outlet_vol": next(iter(self.parameterAsFields(parameters, self.FIELD_OUTLET_VOL, context)), None),
            "street_vol": next(iter(self.parameterAsFields(parameters, self.FIELD_STREET_VOL, context)), None),
            "infiltr_vol": next(iter(self.parameterAsFields(parameters, self.FIELD_INFILTR_VOL, context)), None),
            "annotation": next(iter(self.parameterAsFields(parameters, self.FIELD_ANNOTATION, context)), None)
        }

        feedback.setProgressText(self.tr('done \n'))
        feedback.setProgress(12)

        # get roof layer
        self.file_target = tools_qgis.get_layer_by_tablename('roof')
        if self.file_target is not None and global_vars.gpkg_dao_data is not None:
            expected_schema_path: str = self.file_target.source().split('|')[0]
            if(os.path.normpath(expected_schema_path) != os.path.normpath(global_vars.gpkg_dao_data.db_filepath)):
                feedback.pushWarning(self.tr(f'Wrong Roof layer found: {self.file_target.source()}'))
                return {}
        else:
            feedback.pushWarning(self.tr(f'Error getting expected roof layer'))
            return {}
        if self.file_target is None:
            feedback.reportError(self.tr('Target layer not found.'))
            return {}
        feedback.setProgressText(self.tr('Target layer found.'))

        # check layer types
        feedback.setProgressText(self.tr('Checking layer types.'))
        feedback.setProgress(13)
        if file_source.geometryType() != self.file_target.geometryType():
            feedback.reportError(self.tr('Layer types do not match.'))
            return

        # set unique fields
        feedback.setProgress(15)
        self.unique_fields = {'custom_code':[]}

        # delete innecesary values from geometry
        result = processing.run("native:dropmzvalues", {'INPUT': file_source, 'DROP_M_VALUES':True, 'DROP_Z_VALUES':True,'OUTPUT':'memory:'})
        self.converted_geometries_layer = result['OUTPUT']

        return {}

    def postProcessAlgorithm(self, context, feedback: Feedback):
        """ Import features """

        if self.converted_geometries_layer is None or self.file_target is None or self.field_map is None or self.unique_fields is None:
            return {}

        db_filepath: str = f"{global_vars.project_vars['project_gpkg']}"
        db_filepath: str = f"{QgsProject.instance().absolutePath()}{os.sep}{db_filepath}"
        self.dao.init_db(db_filepath)

        if not self._insert_data(self.converted_geometries_layer, self.file_target, self.field_map, self.unique_fields, feedback, batch_size=50000):
            feedback.reportError(self.tr('Error during import.'))
            self.dao.close_db()
            return {}
        self.dao.close_db()
        feedback.setProgressText(self.tr(f"Importing process finished."))
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
                        except KeyError as e:
                            src_value = None
                    attributes[target_field_names.index(tgt_field)] = src_value
            feedback.setProgress(tools_dr.lerp_progress(int(feature_index*100/num_features), 16, 90))
            feature_index += 1
            if(repeated_params):
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
                    # disable roof triggers
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
                    # enable roof triggers
                    if not self.enable_triggers(feedback, True):
                        return False
                    feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}."))
                    if len(skiped_features) > 0:
                        feedback.setProgressText(self.tr(f"Skipped {len(skiped_features)} features with id: {skiped_features}."))
                    features_to_add.clear()
                except Exception as e:
                    feedback.reportError(self.tr(f"Error adding features: {e}"))
                    target_layer.rollBack()
                    return False
        # Commit any remaining features
        if features_to_add:
            try:
                # disable roof triggers
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
                # enable roof triggers
                if not self.enable_triggers(feedback, True):
                    return False
                feedback.setProgressText(self.tr(f"Imported {imported_features}/{num_features} features into {target_layer.name()}."))
                if len(skiped_features) > 0:
                    feedback.setProgressText(self.tr(f"Skipped {len(skiped_features)} features with id: {skiped_features}."))
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
        fct_path: str = os.path.join(global_vars.plugin_dir, 'dbmodel', 'fct', 'fct_after_import_roof_geometries.sql')
        with open(fct_path, 'r', encoding="utf8") as f:
            sql: str = f.read()
        status = self.dao.execute_script_sql(str(sql))
        if not status:
            feedback.setProgressText(self.tr(f"Error {fct_path} not executed"))
            return False
        feedback.setProgressText(self.tr(f"File {fct_path} executed"))
        return True

    def shortHelpString(self):
        return self.tr("""This tool allows you to import features from a source polygon layer into the Drain-Roof layer of your project.\n
        You must first select the source layer and the target Roof layer. Optionally, you can map fields from the source layer to specific fields in the target layer, such as custom code, annotation, or roughness.\n
        Only features with geometry will be copied. If a source field value already exists in the target layer, it will be skipped to avoid duplicates.\n
        The tool performs the import in batches to optimize performance.""")

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def name(self):
        return 'ImportRoofGeometries'

    def displayName(self):
        return self.tr('Import Roof geometries')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportRoofGeometries()