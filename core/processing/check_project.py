from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsProcessingParameterBoolean
)
from typing import Any, Optional
from qgis.PyQt.QtCore import QVariant

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt, tools_qgis
from ..utils import tools_dr
from ... import global_vars
import re
from typing import Match
import geopandas as gpd
from shapely.geometry import shape, Point
from ..threads import validatemesh


class DrCheckProjectAlgorithm(QgsProcessingAlgorithm):

    BOOL_SHOW_ONLY_ERRORS = 'BOOL_SHOW_ONLY_ERRORS'
    temporal_layers_to_add: list[QgsVectorLayer] = []
    validation_temporal_layers_to_add: list[QgsVectorLayer] = []
    outlayer_values: dict[str, dict[str, Any]] = {}

    error_messages: list[str] = []
    warning_messages: list[str] = []
    info_messages: list[str] = []

    bool_show_only_errors: bool = False
    txt_infolog = None
    bool_error_on_execution: bool = False

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'check_project'

    def displayName(self) -> str:
        return tools_qt.tr('Check Project')

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrCheckProjectAlgorithm()

    def initAlgorithm(self, config: dict[str, Any] | None = None) -> None:
        self.addParameter(QgsProcessingParameterBoolean(
            name=self.BOOL_SHOW_ONLY_ERRORS,
            description=self.tr('Show only errors'),
            defaultValue=False
        ))

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        self.error_messages = []
        self.warning_messages = []
        self.info_messages = []
        self.temporal_layers_to_add = []
        self.validation_temporal_layers_to_add = []
        self.txt_infolog = parameters['TXT_INFOLOG'] if 'TXT_INFOLOG' in parameters else None
        self.dao_data: Optional[DrGpkgDao] = global_vars.gpkg_dao_data.clone()
        self.dao_config: Optional[DrGpkgDao] = global_vars.gpkg_dao_config.clone()
        self.bool_show_only_errors = self.parameterAsBool(parameters, self.BOOL_SHOW_ONLY_ERRORS, context)
        self.bool_error_on_execution = False

        if self.dao_data is None or self.dao_config is None:
            feedback.pushWarning(self.tr('ERROR: No dao found for data or config'))
            self.bool_error_on_execution = True
            return {}

        # Get messages from sys_message
        sql: str = "SELECT id, text FROM sys_message"
        sys_messages = self.dao_data.get_rows(sql)
        sys_messages_dict: dict[int, str] = {}
        if not sys_messages:
            msg = 'ERROR: No sys messages found'
            feedback.pushWarning(self.tr(msg))
            self.bool_error_on_execution = True
            return {}
        for msg in sys_messages:
            sys_messages_dict[msg['id']] = msg['text']

        # Get queries from checkproject_query table
        sql: str = "SELECT * FROM checkproject_query ORDER BY query_type, id"
        queries = self.dao_data.get_rows(sql)
        if not queries:
            msg = 'ERROR: No check project queries found'
            feedback.pushWarning(self.tr(msg))
            self.bool_error_on_execution = True
            return {}

        # Create outlayer values map
        self.default_outlayer_values = {
            'manning': {
                'min': 0,
                'max': 1,
                'include_min': True,
                'include_max': True
            },
            'roughness': {
                'min': 0,
                'max': 1,
                'include_min': True,
                'include_max': True
            },
            'cellsize': {
                'min': 0,
                'max': 1000,
                'include_min': True,
                'include_max': True
            },
            'mfactor': {
                'min': 0,
                'max': 1,
                'include_min': True,
                'include_max': True
            },
            'sfactor': {
                'min': 0,
                'max': 1,
                'include_min': True,
                'include_max': True
            },
            'ufactor': {
                'min': 0,
                'max': 1,
                'include_min': True,
                'include_max': True
            },
            'slope': {
                'min': 0,
                'max': 20,
                'include_min': True,
                'include_max': True
            },
            'outlet_vol': {
                'min': 0,
                'max': 100,
                'include_min': True,
                'include_max': True
            },
            'street_vol': {
                'min': 0,
                'max': 100,
                'include_min': True,
                'include_max': True
            }
        }
        self.outlayer_values = self._get_outlayer_values()
        if not self.outlayer_values:
            msg = 'ERROR: Error getting outlayer values'
            feedback.pushWarning(self.tr(msg))
            self.bool_error_on_execution = True
            return {}

        # Execute checkproject queries
        for index, query in enumerate(queries):
            query_type: str = query['query_type']
            msg = 'Executing: {0} - {1}'
            msg_params = (query_type, query['table_name'])
            feedback.setProgressText(self.tr(msg, list_params=msg_params))

            # region HARCODED QUERIES
            if query_type == 'GEOMETRIC DUPLICATE' or query_type == 'GEOMETRIC ORPHAN':
                self.check_geometrical_duplicate_or_orphan(query, sys_messages_dict, feedback)
            # endregion HARCODED QUERIES

            # region BUILDED QUERIES
            elif query_type == 'MANDATORY NULL' or query_type == 'OUTLAYER':
                self.check_mandatory_null_or_outlayer(query, sys_messages_dict, feedback)
            # endregion MANDATORY NULL

            feedback.setProgress(tools_dr.lerp_progress(int(index + 1 / len(queries) * 100), 0, 70))

        # Hardcoded checks
        feedback.setProgressText('Executing: hardcoded checks')
        # Roof volumes
        roof_volume_layer = self.check_roof_volumes(feedback)
        if roof_volume_layer is not None:
            if roof_volume_layer.featureCount() > 0:
                self.temporal_layers_to_add.append(roof_volume_layer)
                msg = 'ERROR (roof): Volume errors detected ({0})'
                msg_params = (roof_volume_layer.featureCount(),)
                self.error_messages.append(self.tr(msg, list_params=msg_params))
            else:
                msg = 'INFO (roof): No volume errors detected'
                self.info_messages.append(self.tr(msg))
        # Rain options
        missing_rain_options: Optional[str] = self.check_rain_options(feedback)
        if missing_rain_options is not None:
            msg = 'WARNING (rain): Missing rain options ({0})'
            msg_params = (missing_rain_options,)
            self.warning_messages.append(self.tr(msg, list_params=msg_params))
        else:
            msg = 'INFO (rain): Necessary rain options found'
            self.info_messages.append(self.tr(msg))
        # Bridge checks
        bridge_checks_layer = self.check_bridge_checks(feedback)
        if bridge_checks_layer is not None:
            if bridge_checks_layer.featureCount() > 0:
                self.temporal_layers_to_add.append(bridge_checks_layer)
                msg = 'ERROR (bridge): Bridge errors detected ({0})'
                msg_params = (bridge_checks_layer.featureCount(),)
                self.error_messages.append(self.tr(msg, list_params=msg_params))
            else:
                msg = 'INFO (bridge): No bridge errors detected'
                self.info_messages.append(self.tr(msg))

        # Mesh validations
        ground_layer = tools_qgis.get_layer_by_tablename('ground')
        roof_layer = tools_qgis.get_layer_by_tablename('roof')

        if ground_layer is None or roof_layer is None:
            msg = 'ERROR: Could not find ground or roof layers'
            feedback.pushWarning(self.tr(msg))
            self.bool_error_on_execution = True
            return {}

        validations = {
            'check_null_geometries_ground': {
                'method': 'validate_null_geometry',
                'input_layers': 'ground',
                'layer': None
            },
            'check_null_geometries_roof': {
                'method': 'validate_null_geometry',
                'input_layers': 'roof',
                'layer': None
            },
            'check_geometry_validity_ground': {
                'method': 'validate_validity',
                'input_layers': 'ground',
            },
            'check_geometry_validity_roof': {
                'method': 'validate_validity',
                'input_layers': 'roof',
                'layer': None
            },
            'check_groundroughness_params': {
                'method': 'validate_ground_layer',
                'input_layers': 'ground',
                'layer': None
            },
            'check_roof_params': {
                'method': 'validate_roof_layer',
                'input_layers': 'roof',
                'layer': None
            },
            'check_intersections': {
                'method': 'validate_intersect',
                'input_layers': None,
                'layer': None
            }
        }

        feedback.setProgressText('Executing: mesh validations')
        for index, validation in enumerate(validations):
            validation_config = validations[validation]
            method_name = validation_config['method']
            input_layers = validation_config['input_layers']

            # Get the validation function from validatemesh module
            if hasattr(validatemesh, method_name):
                validation_func = getattr(validatemesh, method_name)

                # Call the validation function with appropriate parameters
                if input_layers == 'ground':
                    temporal_layer = validation_func(ground_layer, feedback)
                elif input_layers == 'roof':
                    temporal_layer = validation_func(roof_layer, feedback)
                elif input_layers is None:
                    # For validations that need both layers
                    temporal_layer = validation_func({
                        'ground': ground_layer,
                        'roof': roof_layer
                    }, feedback)
                else:
                    msg = 'Unknown input_layers configuration: {0}'
                    msg_params = (input_layers,)
                    feedback.pushWarning(self.tr(msg, list_params=msg_params))
                    continue

                # Add temporal layer to validation_temporal_layers_to_add
                info_message: bool = True
                if temporal_layer is not None:
                    if isinstance(temporal_layer, tuple):
                        if temporal_layer[0] is not None and temporal_layer[0].featureCount() > 0:
                            self.validation_temporal_layers_to_add.append(temporal_layer[0])
                            info_message = False
                        if temporal_layer[1] is not None and temporal_layer[1].featureCount() > 0 and temporal_layer[1] not in self.validation_temporal_layers_to_add:
                            self.validation_temporal_layers_to_add.append(temporal_layer[1])
                            info_message = False
                    else:
                        if temporal_layer is not None and temporal_layer.featureCount() > 0:
                            self.validation_temporal_layers_to_add.append(temporal_layer)
                            info_message = False
                    # Add error or info message
                    if info_message:
                        msg = 'INFO (validatemesh - {0}): No errors detected'
                        msg_params = (validation,)
                        self.info_messages.append(self.tr(msg, list_params=msg_params))
                    else:
                        msg = 'ERROR (validatemesh - {0}): Errors detected ({1})'
                        msg_params = (validation, temporal_layer.featureCount())
                        self.error_messages.append(self.tr(msg, list_params=msg_params))
            else:
                msg = 'Validation method {0} not found in validatemesh module'
                msg_params = (method_name,)
                feedback.pushWarning(self.tr(msg, list_params=msg_params))

            feedback.setProgress(tools_dr.lerp_progress(int(index + 1 / len(validations) * 100), 80, 90))

        self.dao_data.close_db()
        self.dao_config.close_db()
        return {}

    def check_geometrical_duplicate_or_orphan(self, query, sys_messages_dict: dict[int, str], feedback: QgsProcessingFeedback):
        """ Check geometrical duplicate or orphan """

        # Get exception message
        exception_message: Optional[str] = sys_messages_dict[query['error_message_id']]
        info_message: Optional[str] = sys_messages_dict[query['info_message_id']]
        if exception_message is None or exception_message == '' or info_message is None or info_message == '':
            msg = 'ERROR-{0} ({1}): No messages found for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        # Check geometrics
        if query['query_type'] == 'GEOMETRIC DUPLICATE':
            temporal_layer = self.check_duplicates(query, feedback)
        elif query['query_type'] == 'GEOMETRIC ORPHAN':
            temporal_layer = self.check_orphans(query, feedback)
        else:
            msg = 'ERROR-{0} ({1}): No query found for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'],)
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        if temporal_layer is None:
            msg = 'ERROR-{0} ({1}): Error creating temporal layer for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        if query['create_layer'] and temporal_layer.featureCount() > 0:
            self.temporal_layers_to_add.append(temporal_layer)

        if temporal_layer.featureCount() == 0:
            table_name = query["table_name"]
            self.info_messages.append(self.tr(f'INFO ({table_name}): ' + info_message))
            return

        msg_text = exception_message.format((temporal_layer.featureCount()))
        if query['except_lvl'] == 2:
            # Save warning message
            msg = 'WARNING-{0} ({1}) ({2}): {3}'
            msg_params = (query['error_code'], query['table_name'], query['query_type'], msg_text)
            self.warning_messages.append(self.tr(msg, list_params=msg_params))
        else:
            # Save error message
            msg = 'ERROR-{0} ({1}) ({2}): {3}'
            msg_params = (query['error_code'], query['table_name'], query['query_type'], msg_text)
            self.error_messages.append(self.tr(msg, list_params=msg_params))

    def check_mandatory_null_or_outlayer(self, query, sys_messages_dict: dict[int, str], feedback: QgsProcessingFeedback):
        """ Check mandatory null or outlayer """

        # Get exception message
        exception_message: Optional[str] = sys_messages_dict[query['error_message_id']]
        info_message: Optional[str] = sys_messages_dict[query['info_message_id']]
        if exception_message is None or exception_message == '' or info_message is None or info_message == '':
            msg = 'ERROR-{0} ({1}): Error getting messages for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        # Build check query
        query_data, query_data_nogeom, columns = self._build_check_query(query, feedback)
        if query_data is None:
            msg = 'ERROR-{0} ({1}): Error building check query on table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return
        if columns is None:
            msg = 'ERROR-{0} ({1}): Error getting mandatory columns on table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        # Execute check query
        features = self.dao_data.get_rows(query_data)
        if not features and self.dao_data.last_error is not None:
            features = self.dao_data.get_rows(query_data_nogeom)
            if not features and self.dao_data.last_error is not None:
                # Print error message
                msg = 'ERROR-{0} ({1}): Error getting features for table "{2}". {3}'
                msg_params = (query['error_code'], query['query_type'], query['table_name'], self.dao_data.last_error)
                feedback.pushWarning(self.tr(msg, list_params=msg_params))
                return
        if not features and self.dao_data.last_error is None:
            # Save info message
            if query['query_type'] == 'MANDATORY NULL' and (query['extra_condition'] == '' or query['extra_condition'] is None):
                msg = 'INFO ({0}): {1}'
                msg_params = (query['table_name'], info_message.format(f'{columns}'),)
                self.info_messages.append(self.tr(msg, list_params=msg_params))
            elif query['query_type'] == 'MANDATORY NULL' and query['extra_condition'] is not None and query['extra_condition'] != '':
                # Get additional conditions
                conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                if conditions:
                    msg = 'INFO ({0}): {1}'
                    msg_params = (query['table_name'], info_message.format(f'{columns}', conditions.group(1), conditions.group(2)))
                    self.info_messages.append(self.tr(msg, list_params=msg_params))
                else:
                    msg = 'ERROR-{0} ({1}) ({2}): Error getting additional conditions for table "{3}"'
                    msg_params = (query['error_code'], query['table_name'], query['query_type'], query['table_name'])
                    feedback.pushWarning(self.tr(msg, list_params=msg_params))
                    return
            elif query['query_type'] == 'OUTLAYER':
                for column in columns:
                    if column in self.outlayer_values.keys():
                        msg = 'INFO ({0}): {1}'
                        msg_params = (query['table_name'], info_message.format(self.outlayer_values[column]['min'], self.outlayer_values[column]['max'], f'{column}'))
                        self.info_messages.append(self.tr(msg, list_params=msg_params))
                    else:
                        msg = 'ERROR-{0} ({1}) ({2}): Error getting outlayer values for column "{3}" on table "{4}"'
                        msg_params = (query['error_code'], query['table_name'], query['query_type'], column, query['table_name'])
                        feedback.pushWarning(self.tr(msg, list_params=msg_params))
                        return
            return

        if query['create_layer']:
            # Create temporal layer
            geometry_type = query["geometry_type"]
            query_type = query["query_type"].replace(" ", "_").lower()
            table_name = query["table_name"]
            temporal_layer = QgsVectorLayer(geometry_type, f'{query_type}_{table_name}', 'memory')
            temporal_layer.setCrs(QgsProject.instance().crs())
            temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
            temporal_layer.updateFields()
            features_to_add: list[QgsFeature] = []

        columns_dict: dict[str, int] = {}

        # Check features
        for feature in features:
            invalid_columns: list[str] = []
            # Check feature fields
            for column in columns:
                if column not in columns_dict.keys():
                    columns_dict[column] = 0

                # Check if this specific column is actually null for this feature
                # sqlite3.Row objects can be accessed like dictionaries
                try:
                    column_value = feature[column]
                except (KeyError, IndexError):
                    column_value = None

                is_null = column_value is None or column_value == '' or str(column_value).upper() in ['NULL', 'NONE']

                if query['query_type'] == 'MANDATORY NULL' and is_null:
                    invalid_columns.append(column)
                    columns_dict[column] += 1
                elif query['query_type'] == 'OUTLAYER':
                    # For OUTLAYER, check if value is outside the valid range
                    if column in self.outlayer_values and column_value is not None:
                        try:
                            numeric_value = float(column_value)
                            min_val = self.outlayer_values[column]['min']
                            max_val = self.outlayer_values[column]['max']
                            include_min = self.outlayer_values[column]['include_min']
                            include_max = self.outlayer_values[column]['include_max']

                            is_out_of_range = False
                            if include_min and numeric_value < min_val:
                                is_out_of_range = True
                            elif not include_min and numeric_value <= min_val:
                                is_out_of_range = True
                            elif include_max and numeric_value > max_val:
                                is_out_of_range = True
                            elif not include_max and numeric_value >= max_val:
                                is_out_of_range = True

                            if is_out_of_range:
                                invalid_columns.append(column)
                                columns_dict[column] += 1
                        except (ValueError, TypeError):
                            # If value can't be converted to float, treat as invalid
                            invalid_columns.append(column)
                            columns_dict[column] += 1

            if query['create_layer'] and len(invalid_columns) > 0:
                # Create new feature
                new_feature = QgsFeature(temporal_layer.fields())
                new_feature['Code'] = feature['code']
                exception_msg: Optional[str] = None
                for col in invalid_columns:
                    if exception_msg is None:
                        exception_msg = f'Null columns: {col}'
                    else:
                        exception_msg += f', {col}'
                new_feature['Exception'] = exception_msg
                if not feature['geom_wkt']:
                    msg = 'ERROR-{0} ({1}): Error getting geometry for feature "{2}" on table "{3}"'
                    msg_params = (query['error_code'], query['query_type'], feature['code'], query['table_name'])
                    feedback.pushWarning(self.tr(msg, list_params=msg_params))
                    continue
                new_feature.setGeometry(QgsGeometry.fromWkt(feature['geom_wkt']))
                features_to_add.append(new_feature)

        # Print check result if its negative
        if columns_dict:
            if query['create_layer'] and len(features_to_add) > 0 and temporal_layer is not None:
                # Add features to temporal layer
                temporal_layer.startEditing()
                temporal_layer.addFeatures(features_to_add)
                temporal_layer.commitChanges()
                self.temporal_layers_to_add.append(temporal_layer)
            valid_columns: list[str] = []

            for index, col in enumerate(columns_dict.keys()):
                # Build exception message
                error_msg: str = ''
                if query['query_type'] == 'OUTLAYER':
                    if columns_dict[col] > 0:
                        error_msg = exception_message.format(self.outlayer_values[col]['min'], self.outlayer_values[col]['max'], col, columns_dict[col])
                    else:
                        valid_columns.append(col)
                else:
                    if columns_dict[col] > 0:
                        if query['extra_condition'] is None or query['extra_condition'] == "":
                            error_msg = exception_message.format(col, columns_dict[col])
                        else:
                            # Get additional conditions
                            conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                            if conditions:
                                error_msg = exception_message.format(col, conditions.group(1), conditions.group(2), columns_dict[col])
                            else:
                                msg = 'ERROR-{0}: Error getting additional conditions for table[{1}]'
                                msg_params = (query['error_code'], query['table_name'])
                                feedback.pushWarning(self.tr(msg, list_params=msg_params))
                                continue
                    else:
                        valid_columns.append(col)

                # Save error message
                if error_msg != '':
                    if query['except_lvl'] == 2:
                        msg = 'WARNING-{0}/{1} ({2}) ({3}): {4}'
                        msg_params = (query['error_code'], index + 1, query['table_name'], query['query_type'], error_msg)
                        self.warning_messages.append(self.tr(msg, list_params=msg_params))
                    else:
                        msg = 'ERROR-{0}/{1} ({2}) ({3}): {4}'
                        msg_params = (query['error_code'], index + 1, query['table_name'], query['query_type'], error_msg)
                        self.error_messages.append(self.tr(msg, list_params=msg_params))

            # Save info message for valid columns
            if len(valid_columns) > 0:
                if query['query_type'] == 'OUTLAYER':
                    for col in valid_columns:
                        msg = 'INFO ({0}): {1}'
                        msg_params = (query['table_name'], info_message.format(self.outlayer_values[col]['min'], self.outlayer_values[col]['max'], col))
                        self.info_messages.append(self.tr(msg, list_params=msg_params))
                else:
                    if query['extra_condition'] is None or query['extra_condition'] == "":
                        msg = 'INFO ({0}): {1}'
                        msg_params = (query['table_name'], info_message.format(valid_columns))
                        self.info_messages.append(self.tr(msg, list_params=msg_params))
                    else:
                        conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                        if conditions:
                            msg = 'INFO ({0}): {1}'
                            msg_params = (query['table_name'], info_message.format(valid_columns, conditions.group(1), conditions.group(2)))
                            self.info_messages.append(self.tr(msg, list_params=msg_params))
                        else:
                            msg = 'ERROR-{0} ({1}) ({2}): Error getting additional conditions for table[{3}]'
                            msg_params = (query['error_code'], query['table_name'], query['query_type'], query['table_name'])
                            feedback.pushWarning(self.tr(msg, list_params=msg_params))
                            return

    def postProcessAlgorithm(self, context, feedback: QgsProcessingFeedback):
        """ Create temporal layers on main thread """

        # Clear text edit
        if self.txt_infolog is not None and not self.bool_error_on_execution:
            self.txt_infolog.clear()

        # Print errors
        if len(self.error_messages) > 0:
            msg = '\nERRORS\n----------'
            feedback.setProgressText(self.tr(msg))
            for msg in self.error_messages:
                feedback.setProgressText(msg)

        # Print warnings
        if len(self.warning_messages) > 0:
            msg = '\nWARNINGS\n--------------'
            feedback.setProgressText(self.tr(msg))
            for msg in self.warning_messages:
                feedback.setProgressText(msg)

        # Print info
        if not self.bool_show_only_errors and len(self.info_messages) > 0:
            msg = '\nINFO\n------'
            feedback.setProgressText(self.tr(msg))
            for msg in self.info_messages:
                feedback.setProgressText(msg)

        # Add temporal layers
        group_name = "CHECK PROJECT TEMPORAL LAYERS"
        mesh_group = None
        group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
        if group is None and (len(self.temporal_layers_to_add) > 0 or len(self.validation_temporal_layers_to_add) > 0):
            QgsProject.instance().layerTreeRoot().insertGroup(0, group_name)
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            mesh_group = group.findGroup("MESH VALIDATIONS")
        elif group is not None:
            group.removeAllChildren()
        if mesh_group is None and len(self.validation_temporal_layers_to_add) > 0:
            group.insertGroup(0, "MESH VALIDATIONS")
            mesh_group = group.findGroup("MESH VALIDATIONS")
        elif mesh_group is not None:
            mesh_group.removeAllChildren()

        if group is not None and len(self.temporal_layers_to_add) > 0:
            for layer in self.temporal_layers_to_add:
                QgsProject.instance().addMapLayer(layer, False)
                group.addLayer(layer)
        if mesh_group is not None and len(self.validation_temporal_layers_to_add) > 0:
            for layer in self.validation_temporal_layers_to_add:
                QgsProject.instance().addMapLayer(layer, False)
                mesh_group.addLayer(layer)

        return {}

    def _build_check_query(self, query, feedback: QgsProcessingFeedback) -> tuple[Optional[str], Optional[str], Optional[list[str]]]:
        """ Build check query and return columns to check """

        check_query: Optional[str] = None
        check_query_nogeom: Optional[str] = None
        columns_checked: Optional[list[str]] = None

        # Get columns
        if query['columns'] is None:
            msg = 'ERROR-{0} ({1}): No columns found for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return None, None, None
        columns = query['columns'].strip("{}").split(", ")
        columns_select: Optional[str] = None
        for col in columns:
            # Add column conditions to check query WHERE clause
            if query['query_type'] == 'OUTLAYER':
                max_operator = ">" if self.outlayer_values[col]["include_max"] else ">="
                min_operator = "<" if self.outlayer_values[col]["include_min"] else "<="
                max_val = self.outlayer_values[col]["max"]
                min_val = self.outlayer_values[col]["min"]
                if columns_select is None:
                    columns_select = f'({col} {min_operator} {min_val} OR {col} {max_operator} {max_val})'
                else:
                    columns_select += f' OR ({col} {min_operator} {min_val} OR {col} {max_operator} {max_val})'
            else:
                if columns_select is None:
                    columns_select = col + ' ISNULL'
                else:
                    columns_select += ' OR ' + col + ' ISNULL'
            if columns_checked is None:
                columns_checked = [col]
            else:
                columns_checked.append(col)

        # Get additional conditions
        condition_select: Optional[str] = None
        if query['extra_condition']:
            condition_select = query['extra_condition'].replace('"', "'")

        table_name = query['table_name']
        if table_name:
            if query['geometry_type'] is None:
                geom = ''
            else:
                geom = ', AsWKT(CastAutomagic(geom)) as geom_wkt'
            if condition_select is not None:
                # Build check query with WHERE clause and additional conditions
                check_query = f"SELECT *{geom} FROM {table_name} WHERE ({columns_select}) "
                check_query_nogeom = f"SELECT * FROM {table_name} WHERE ({columns_select}) "
                check_query += condition_select
            else:
                # Build check query with WHERE clause
                check_query = f"SELECT *{geom} FROM {table_name} WHERE {columns_select} "
                check_query_nogeom = f"SELECT * FROM {table_name} WHERE {columns_select} "

        return check_query, check_query_nogeom, columns_checked

    def check_duplicates(self, query, feedback: QgsProcessingFeedback) -> Optional[QgsVectorLayer]:
        """ Check duplicates using GeoPandas for faster geometry comparison """

        temporal_layer: Optional[QgsVectorLayer] = None
        tolerance: float = 0

        if query['error_code'] and query['error_code'] in [102, 104]:
            tolerance = 0.10
        elif query['error_code'] is None:
            msg = 'ERROR ({0}): No error code found for table "{1}"'
            msg_params = (query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))

        table_name = query['table_name']
        if table_name in ['arc', 'node']:
            db_filepath = global_vars.gpkg_dao_data.db_filepath
            source_layer = QgsVectorLayer(f'{db_filepath}|layername={table_name}', table_name, 'ogr')
        else:
            source_layer = tools_qgis.get_layer_by_tablename(table_name)
        if source_layer is None:
            msg = 'ERROR-{0} ({1}): No layer found for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        # Convert QGIS layer to GeoPandas DataFrame
        features = list(source_layer.getFeatures())
        geometries = []
        codes = []

        for feature in features:
            if feature.geometry() is None:
                continue
            if query['table_name'] == 'node' and feature['table_name'] == 'inlet':
                continue

            geometries.append(shape(feature.geometry()))
            codes.append(feature['code'])

        gdf = gpd.GeoDataFrame({'code': codes}, geometry=geometries)

        # Find duplicates using GeoPandas
        if tolerance > 0:
            # For tolerance > 0, use buffer and contains
            gdf['buffer'] = gdf.geometry.buffer(tolerance)
            duplicates = []

            # Use spatial index for faster intersection checks
            spatial_index = gdf.sindex

            for idx, row in gdf.iterrows():
                # Get potential candidates using spatial index
                possible_matches = list(spatial_index.intersection(row.buffer.bounds))

                # Check each potential match
                for match_idx in possible_matches:
                    if idx != match_idx:  # Don't compare with self
                        if row.buffer.contains(gdf.iloc[match_idx].geometry):
                            duplicates.append(idx)
                            duplicates.append(match_idx)
        else:
            # For tolerance = 0, use exact geometry comparison
            duplicates = []
            # Use spatial index for faster intersection checks
            spatial_index = gdf.sindex

            for idx, row in gdf.iterrows():
                # Get potential candidates using spatial index
                possible_matches = list(spatial_index.intersection(row.geometry.bounds))

                # Check each potential match
                for match_idx in possible_matches:
                    if idx != match_idx:  # Don't compare with self
                        if row.geometry.equals(gdf.iloc[match_idx].geometry):
                            duplicates.append(idx)
                            duplicates.append(match_idx)

        # Remove duplicates from the list
        duplicates = list(set(duplicates))

        # Create temporal layer
        geometry_type = query["geometry_type"]
        query_type = query["query_type"].replace(" ", "_").lower()
        table_name = query["table_name"]
        temporal_layer = QgsVectorLayer(geometry_type, f'{query_type}_{table_name}', 'memory')
        if temporal_layer is None:
            msg = 'ERROR-{0} ({1}): Error creating temporal layer for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        temporal_layer.setCrs(QgsProject.instance().crs())
        temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
        temporal_layer.updateFields()

        # Add duplicated features to temporal layer
        features_to_add: list[QgsFeature] = []
        for idx in duplicates:
            new_feature = QgsFeature(temporal_layer.fields())
            new_feature['Code'] = gdf.iloc[idx]['code']
            new_feature['Exception'] = f'Duplicated feature (tolerance: {tolerance}m)' if tolerance > 0 else 'Duplicated feature'
            new_feature.setGeometry(QgsGeometry.fromWkt(gdf.iloc[idx].geometry.wkt))
            features_to_add.append(new_feature)

        if features_to_add:
            temporal_layer.startEditing()
            temporal_layer.addFeatures(features_to_add)
            temporal_layer.commitChanges()

        return temporal_layer

    def check_orphans(self, query, feedback: QgsProcessingFeedback) -> Optional[QgsVectorLayer]:
        """ Check orphans using both database relationships (node1/node2 fields) and geometric vertex proximity """

        temporal_layer: Optional[QgsVectorLayer] = None

        # Get node and arc layers
        node_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=node', 'node', 'ogr')
        arc_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=arc', 'arc', 'ogr')

        if node_layer is None or arc_layer is None:
            msg = 'ERROR-{0} ({1}): No layers found for node or arc tables'
            msg_params = (query['error_code'], query['query_type'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        # Get all node codes that are not 'inlet' type
        node_codes = set()
        node_features = list(node_layer.getFeatures())

        for feature in node_features:
            if feature['table_name'] != 'inlet':
                node_codes.add(feature['code'])

        # CHECK 1: Database relationship check - Get all node codes referenced in arc tables (node1 and node2 fields)
        referenced_node_codes_db = set()

        # Get all arc tables from arc features
        arc_tables = set()
        for feature in arc_layer.getFeatures():
            if feature['table_name']:
                arc_tables.add(feature['table_name'])

        for table_name in arc_tables:
            try:
                table_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername={table_name}', table_name, 'ogr')
                if table_layer is None:
                    continue

                # Check if the layer has node1 and node2 fields
                field_names = [field.name() for field in table_layer.fields()]
                if 'node_1' in field_names and 'node_2' in field_names:
                    for feature in table_layer.getFeatures():
                        if feature['node_1']:
                            referenced_node_codes_db.add(feature['node_1'])
                        if feature['node_2']:
                            referenced_node_codes_db.add(feature['node_2'])
            except Exception as e:
                msg = 'Warning: Could not check table {0}: {1}'
                msg_params = (table_name, str(e))
                feedback.pushWarning(self.tr(msg, list_params=msg_params))
                continue

        # CHECK 2: Geometric vertex check - Find nodes that are not on any arc vertex
        referenced_node_codes_geom = set()

        # Convert nodes to GeoPandas for spatial operations
        node_geometries = []
        node_codes_list = []

        for feature in node_features:
            if feature.geometry() is None or feature.geometry().isEmpty():
                continue
            if feature['table_name'] == 'inlet':
                continue

            node_geometries.append(shape(feature.geometry()))
            node_codes_list.append(feature['code'])

        nodes_gdf = gpd.GeoDataFrame({'code': node_codes_list}, geometry=node_geometries)

        # Convert arcs to GeoPandas
        arc_features = list(arc_layer.getFeatures())
        arc_geometries = []

        for feature in arc_features:
            if feature.geometry() is None or feature.geometry().isEmpty():
                continue
            arc_geometries.append(shape(feature.geometry()))

        arcs_gdf = gpd.GeoDataFrame(geometry=arc_geometries)

        # Create spatial index for arcs
        arcs_sindex = arcs_gdf.sindex

        # Check each node against arc vertices
        tolerance = 0
        for idx, node in nodes_gdf.iterrows():
            # Get potential intersecting arcs using spatial index
            possible_matches = list(arcs_sindex.intersection(node.geometry.bounds))

            # Check if node is on any arc vertex (start or end point)
            is_connected = False
            for arc_idx in possible_matches:
                arc_geom = arcs_gdf.iloc[arc_idx].geometry

                # Check distance to start and end points of the arc
                if arc_geom.geom_type == 'LineString':
                    start_point = arc_geom.coords[0]
                    end_point = arc_geom.coords[-1]

                    # Check if node is on start or end point
                    if (node.geometry.distance(Point(start_point)) <= tolerance or
                        node.geometry.distance(Point(end_point)) <= tolerance):
                        is_connected = True
                        break

                elif arc_geom.geom_type == 'MultiLineString':
                    # Handle MultiLineString case
                    for line in arc_geom.geoms:
                        start_point = line.coords[0]
                        end_point = line.coords[-1]

                        if (node.geometry.distance(Point(start_point)) <= tolerance or
                            node.geometry.distance(Point(end_point)) <= tolerance):
                            is_connected = True
                            break
                    if is_connected:
                        break

            if is_connected:
                referenced_node_codes_geom.add(node['code'])

        # Combine results: nodes that are orphaned in BOTH database and geometric checks
        orphan_node_codes_db = node_codes - referenced_node_codes_db
        orphan_node_codes_geom = node_codes - referenced_node_codes_geom

        # Nodes that are orphaned in both checks
        orphan_node_codes_both = orphan_node_codes_db & orphan_node_codes_geom

        # Nodes that are orphaned in database check only
        orphan_node_codes_db_only = orphan_node_codes_db - orphan_node_codes_geom

        # Nodes that are orphaned in geometric check only
        orphan_node_codes_geom_only = orphan_node_codes_geom - orphan_node_codes_db

        # Create temporal layer
        query_type = query["query_type"].replace(" ", "_").lower()
        table_name = query["table_name"]
        temporal_layer = QgsVectorLayer('Point', f'{query_type}_{table_name}', 'memory')
        if temporal_layer is None:
            msg = 'ERROR-{0} ({1}): Error creating temporal layer for table "{2}"'
            msg_params = (query['error_code'], query['query_type'], query['table_name'])
            feedback.pushWarning(self.tr(msg, list_params=msg_params))
            return

        temporal_layer.setCrs(QgsProject.instance().crs())
        temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
        temporal_layer.updateFields()

        # Add orphan features to temporal layer
        features_to_add: list[QgsFeature] = []

        # Add nodes orphaned in both checks
        for node_code in orphan_node_codes_both:
            for feature in node_features:
                if feature['code'] == node_code:
                    new_feature = QgsFeature(temporal_layer.fields())
                    new_feature['Code'] = node_code
                    new_feature['Exception'] = 'Orphan node (not referenced in arcs AND not on arc vertices)'
                    new_feature.setGeometry(feature.geometry())
                    features_to_add.append(new_feature)
                    break

        # Add nodes orphaned in database check only
        for node_code in orphan_node_codes_db_only:
            for feature in node_features:
                if feature['code'] == node_code:
                    new_feature = QgsFeature(temporal_layer.fields())
                    new_feature['Code'] = node_code
                    new_feature['Exception'] = 'Orphan node (not referenced in arc node1/node2 fields)'
                    new_feature.setGeometry(feature.geometry())
                    features_to_add.append(new_feature)
                    break

        # Add nodes orphaned in geometric check only
        for node_code in orphan_node_codes_geom_only:
            for feature in node_features:
                if feature['code'] == node_code:
                    new_feature = QgsFeature(temporal_layer.fields())
                    new_feature['Code'] = node_code
                    new_feature['Exception'] = 'Orphan node (not on any arc vertex)'
                    new_feature.setGeometry(feature.geometry())
                    features_to_add.append(new_feature)
                    break

        if features_to_add:
            temporal_layer.startEditing()
            temporal_layer.addFeatures(features_to_add)
            temporal_layer.commitChanges()

        return temporal_layer

    def check_roof_volumes(self, feedback: QgsProcessingFeedback):
        """ Check roof volumes """

        # Get roof layer
        roof_layer = tools_qgis.get_layer_by_tablename('roof')
        if roof_layer is None:
            msg = 'ERROR-1000 (check_roof_volumes): No roof layer found'
            feedback.pushWarning(self.tr(msg))
            return

        temporal_layer = QgsVectorLayer('MultiPolygon', 'roof_volumes', 'memory')
        if temporal_layer is None:
            msg = 'ERROR (roof_volumes): Error creating temporal layer for roof volumes check'
            feedback.pushWarning(self.tr(msg))
            return

        temporal_layer.setCrs(QgsProject.instance().crs())
        temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
        temporal_layer.updateFields()

        features_to_add: list[QgsFeature] = []

        # Check roof volumes
        for feature in roof_layer.getFeatures():
            outlet_vol = feature['outlet_vol'] if feature['outlet_vol'] not in (None, 'NULL', 'null') else 0
            street_vol = feature['street_vol'] if feature['street_vol'] not in (None, 'NULL', 'null') else 0
            infiltr_vol = feature['infiltr_vol'] if feature['infiltr_vol'] not in (None, 'NULL', 'null') else 0

            # Check if outlet or street volume is null
            if outlet_vol + street_vol + infiltr_vol != 100:
                new_feature = QgsFeature(temporal_layer.fields())
                new_feature['Code'] = feature['code']
                msg = 'The sum of all volumes is not 100 (current volume: {0})'
                msg_params = (outlet_vol + street_vol + infiltr_vol,)
                new_feature['Exception'] = self.tr(msg, list_params=msg_params)
                new_feature.setGeometry(feature.geometry())
                features_to_add.append(new_feature)

        if features_to_add:
            temporal_layer.startEditing()
            temporal_layer.addFeatures(features_to_add)
            temporal_layer.commitChanges()

        return temporal_layer

    def check_rain_options(self, feedback: QgsProcessingFeedback):
        """ Check rain options """

        wrong_options: list[str] = []
        rain_options: dict[str, dict[str, Any]] = {
            'options_rain_class': {
                'widget': 'combo',
                'wrong_value': ['0', None]
            },
            'result_results_raster': {
                'widget': 'combo',
                'wrong_value': ['0', None]
            },
            'result_results_raster_cell': {
                'widget': 'text',
                'type': 'integer'
            },
            'options_setrainfall_raster': {
                'widget': 'combo',
                'wrong_value': ['0', None],
                'parent': 'options_rain_class',
                'parent_value': '2'
            }
        }

        # Check options
        for option in rain_options.keys():
            sql = f"SELECT value FROM config_param_user WHERE parameter = '{option}'"
            row = self.dao_data.get_row(sql)
            if row:
                value = row[0]
                if rain_options[option]['widget'] == 'combo':
                    if rain_options[option].get('parent') and rain_options[option]['parent'] in rain_options.keys():
                        sql = f"SELECT value FROM config_param_user WHERE parameter = '{rain_options[option]['parent']}'"
                        row = self.dao_data.get_row(sql)
                        if row and row[0] != rain_options[option]['parent_value']:
                            continue
                    if value in rain_options[option]['wrong_value']:
                        wrong_options.append(option)
                elif rain_options[option]['widget'] == 'text':
                    if rain_options[option].get('wrong_value') and value in rain_options[option]['wrong_value']:
                        wrong_options.append(option)
                    elif rain_options[option].get('type') == 'integer' and not value.isdigit():
                        wrong_options.append(option)

        # Return wrong options as string
        if wrong_options:
            for index, option in enumerate(wrong_options):
                sql = f"SELECT label FROM config_form_fields WHERE columnname = '{option}'"
                row = self.dao_data.get_row(sql)
                if row:
                    wrong_options[index] = row[0]
            return ', '.join(wrong_options)
        else:
            return None

    def check_bridge_checks(self, feedback: QgsProcessingFeedback):
        """ Check bridges """

        bridge_layer = tools_qgis.get_layer_by_tablename('bridge')
        if bridge_layer is None:
            bridge_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=bridge', 'bridge', 'ogr')
        ground_layer = tools_qgis.get_layer_by_tablename('ground')
        if ground_layer is None:
            ground_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=ground', 'ground', 'ogr')
        roof_layer = tools_qgis.get_layer_by_tablename('roof')
        if roof_layer is None:
            roof_layer = QgsVectorLayer(f'{global_vars.gpkg_dao_data.db_filepath}|layername=roof', 'roof', 'ogr')

        # Check if layers exist and are valid
        if bridge_layer is None or not bridge_layer.isValid():
            feedback.pushWarning(self.tr('ERROR: Bridge layer not found or invalid'))
            return None
        if ground_layer is None or not ground_layer.isValid():
            feedback.pushWarning(self.tr('ERROR: Ground layer not found or invalid'))
            return None
        if roof_layer is None or not roof_layer.isValid():
            feedback.pushWarning(self.tr('ERROR: Roof layer not found or invalid'))
            return None

        # Create temporal layer for bridges that touch edges
        temporal_layer = QgsVectorLayer('LineString', 'bridge_edge_touches', 'memory')
        temporal_layer.setCrs(QgsProject.instance().crs())
        temporal_layer.dataProvider().addAttributes([
            QgsField('Code', QVariant.String),
            QgsField('Exception', QVariant.String)
        ])
        temporal_layer.updateFields()

        features_to_add = []

        # Convert layers to GeoPandas
        bridge_geometries = []
        bridge_codes = []

        for feature in bridge_layer.getFeatures():
            if feature.geometry() is None or feature.geometry().isEmpty():
                continue
            bridge_geometries.append(shape(feature.geometry()))
            bridge_codes.append(feature['code'])

        if not bridge_geometries:
            return temporal_layer

        bridges_gdf = gpd.GeoDataFrame({'code': bridge_codes}, geometry=bridge_geometries)

        # Get ground and roof layer boundaries
        ground_geometries = []
        roof_geometries = []

        for feature in ground_layer.getFeatures():
            if feature.geometry() is None or feature.geometry().isEmpty():
                continue
            ground_geometries.append(shape(feature.geometry()))

        for feature in roof_layer.getFeatures():
            if feature.geometry() is None or feature.geometry().isEmpty():
                continue
            roof_geometries.append(shape(feature.geometry()))

        if not ground_geometries and not roof_geometries:
            return temporal_layer

        # Check for bridges touching edges
        for idx, bridge_row in bridges_gdf.iterrows():
            bridge_geom = bridge_row.geometry
            bridge_code = bridge_row['code']
            touching_issues = []

            # Check against ground layer boundaries
            for ground_geom in ground_geometries:
                if hasattr(ground_geom, 'boundary'):
                    ground_boundary = ground_geom.boundary
                    if bridge_geom.touches(ground_boundary) or bridge_geom.intersects(ground_boundary):
                        touching_issues.append('ground layer edge')
                        break

            # Check against roof layer boundaries
            for roof_geom in roof_geometries:
                if hasattr(roof_geom, 'boundary'):
                    roof_boundary = roof_geom.boundary
                    if bridge_geom.touches(roof_boundary) or bridge_geom.intersects(roof_boundary):
                        touching_issues.append('roof layer edge')
                        break

            # If bridge touches any edges, add to error features
            if touching_issues:
                new_feature = QgsFeature()
                new_feature.setAttributes([
                    bridge_code,
                    f'Bridge touches: {", ".join(touching_issues)}'
                ])
                new_feature.setGeometry(QgsGeometry.fromWkt(bridge_geom.wkt))
                features_to_add.append(new_feature)

        # Add features to temporal layer
        if features_to_add:
            temporal_layer.dataProvider().addFeatures(features_to_add)
            temporal_layer.updateExtents()

        # TODO: Check cellsize of the ground depending on the distance between ground and the bridge

        return temporal_layer

    def _get_outlayer_values(self):
        """ Get outlayer values from config_param_user """

        outlayer_values = {}
        sql = "SELECT parameter, value FROM config_param_user WHERE parameter LIKE 'outlayer_%'"
        result = self.dao_data.get_rows(sql)
        for row in result:
            parameter, value = row
            split_parameter = parameter.split('_')
            name = None
            for name in self.default_outlayer_values.keys():
                if name in parameter:
                    name = name
                    break
            if name is None:
                return None
            param = split_parameter[-1]
            if param == 'include':
                param = f"{split_parameter[-1]}_{split_parameter[-2]}"
                if value == '1':
                    value = True
                else:
                    value = False
            else:
                value = float(value)
            if name not in outlayer_values.keys():
                outlayer_values[name] = {}
            outlayer_values[name][param] = value
        # Validate values and set default values if needed
        for name in self.default_outlayer_values.keys():
            if name not in self.default_outlayer_values.keys():
                outlayer_values[name] = self.default_outlayer_values[name]
            try:
                min_value = outlayer_values[name].get('min', self.default_outlayer_values[name]['min'])
                max_value = outlayer_values[name].get('max', self.default_outlayer_values[name]['max'])
                if min_value > max_value:
                    outlayer_values[name]['min'] = self.default_outlayer_values[name]['min']
                    outlayer_values[name]['max'] = self.default_outlayer_values[name]['max']
            except Exception:
                print(f"Error getting values for {name}. Using default values...")
                outlayer_values[name] = self.default_outlayer_values[name]
        return outlayer_values

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def shortHelpString(self):
        msg = """Checks your project for common data issues such as duplicate or orphan geometries, missing required values, and out-of-range attributes. 
                       Results are shown as errors, warnings, or info messages, and problematic features can be highlighted on the map. 
                       Use this tool to quickly validate and improve your project's data quality."""
        return self.tr(msg)

    def tr(self, string: str, list_params: list[Any] = None):
        return tools_qt.tr(string, list_params=list_params)
