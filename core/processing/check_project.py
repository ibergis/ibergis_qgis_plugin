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
from qgis.PyQt.QtCore import QCoreApplication, QVariant

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt
from ..utils import tools_dr
from ... import global_vars
import re
from typing import Match


class DrCheckProjectAlgorithm(QgsProcessingAlgorithm):

    BOOL_SHOW_ONLY_ERRORS = 'BOOL_SHOW_ONLY_ERRORS'
    temporal_layers_to_add: list[QgsVectorLayer] = []
    outlayer_values: dict[str, dict[str, Any]] = {}

    error_messages: list[str] = []
    warning_messages: list[str] = []
    info_messages: list[str] = []

    bool_show_only_errors: bool = False

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
        self.dao_data: Optional[DrGpkgDao] = global_vars.gpkg_dao_data.clone()
        self.dao_config: Optional[DrGpkgDao] = global_vars.gpkg_dao_config.clone()
        self.bool_show_only_errors = self.parameterAsBool(parameters, self.BOOL_SHOW_ONLY_ERRORS, context)

        if self.dao_data is None or self.dao_config is None:
            feedback.pushWarning(self.tr('ERROR: No dao found for data or config'))
            return {}

        # Get messages from sys_message
        sql: str = "SELECT id, COALESCE(i18n_text, text) AS text FROM sys_message"
        sys_messages = self.dao_config.get_rows(sql)
        sys_messages_dict: dict[int, str] = {}
        if not sys_messages:
            feedback.pushWarning(self.tr('ERROR: No sys messages found'))
            return {}
        for msg in sys_messages:
            sys_messages_dict[msg['id']] = msg['text']

        # Get queries from checkproject_query table
        sql: str = "SELECT * FROM checkproject_query ORDER BY query_type, id"
        queries = self.dao_config.get_rows(sql)
        if not queries:
            feedback.pushWarning(self.tr('ERROR: No check project queries found'))
            return {}

        # Create harcoded queries
        harcoded_queries: dict[int, str] = {
            101: f"""SELECT DISTINCT a1.fid as fid, a1.code as code, AsWKT(CastAutomagic(a1.geom)) as geom_WKT FROM arc a1 JOIN arc a2 ON a1.fid <> a2.fid AND st_equals(CastAutomagic(a1.geom), CastAutomagic(a2.geom))""",
            102: f"""SELECT DISTINCT n1.fid as fid, n1.code as code, AsWKT(CastAutomagic(n1.geom)) as geom_WKT FROM node n1 JOIN node n2 ON n1.fid <> n2.fid AND st_distance(CastAutomagic(n1.geom), CastAutomagic(n2.geom)) <= 0.10""",
            103: f"""SELECT n.*, AsWKT(CastAutomagic(n.geom)) as geom_WKT FROM node n LEFT JOIN arc a ON ST_Distance(CastAutomagic(n.geom), ST_StartPoint(CastAutomagic(a.geom))) <= 0.10 OR ST_Distance(CastAutomagic(n.geom), ST_EndPoint(CastAutomagic(a.geom))) <= 0.10 WHERE a.fid IS NULL AND n.table_name not like 'inlet'""",
            104: f"""SELECT DISTINCT i1.fid as fid, i1.code as code, AsWKT(CastAutomagic(i1.geom)) as geom_WKT FROM inlet i1 JOIN inlet i2 ON i1.fid <> i2.fid AND st_distance(CastAutomagic(i1.geom), CastAutomagic(i2.geom)) <= 0.10"""
        }

        # Create outlayer values map
        self.outlayer_values = {
            # TODO get values from config
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

        for index, query in enumerate(queries):
            query_type: str = query['query_type']

            # region HARCODED QUERIES
            if query_type == 'GEOMETRIC DUPLICATE' or query_type == 'GEOMETRIC ORPHAN':
                self.check_geometrical_duplicate_or_orphan(query, harcoded_queries, sys_messages_dict, feedback)
            # endregion HARCODED QUERIES

            # region BUILDED QUERIES
            elif query_type == 'MANDATORY NULL' or query_type == 'OUTLAYER':
                self.check_mandatory_null_or_outlayer(query, harcoded_queries, sys_messages_dict, feedback)
            # endregion MANDATORY NULL
            feedback.setProgress(tools_dr.lerp_progress(int(index+1/len(queries)*100), 0, 90))

        self.dao_data.close_db()
        self.dao_config.close_db()
        return {}

    def check_geometrical_duplicate_or_orphan(self, query, harcoded_queries: dict[int, str], sys_messages_dict: dict[int, str], feedback: QgsProcessingFeedback):
        """ Check geometrical duplicate or orphan """

        # Get exception message
        exception_message: Optional[str] = sys_messages_dict[query['error_message_id']]
        info_message: Optional[str] = sys_messages_dict[query['info_message_id']]
        if exception_message is None or exception_message == '' or info_message is None or info_message == '':
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): No messages found for table "{query['table_name']}"'))
            return

        # Check geometrics
        if not query['error_code'] in harcoded_queries.keys():
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): No query found for table "{query['table_name']}"'))
            return
        query_data = harcoded_queries[query['error_code']]
        features = self.dao_data.get_rows(query_data)
        if not features and self.dao_data.last_error is None:
            # Save info message
            self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message))
            return
        elif not features and self.dao_data.last_error is not None:
            # Print error message
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error getting features for table "{query['table_name']}". {self.dao_data.last_error}'))
            return

        if query['create_layer']:
            # Create temporal layer
            temporal_layer = QgsVectorLayer(f'{query['geometry_type']}', f'{query['query_type'].replace(" ", "_").lower()}_{query['table_name']}', 'memory')
            temporal_layer.setCrs(QgsProject.instance().crs())
            temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
            temporal_layer.updateFields()
            features_to_add: list[QgsFeature] = []

        # Build exception message
        for feature in features:
            if query['create_layer']:
                # Create new feature
                new_feature = QgsFeature(temporal_layer.fields())
                new_feature['Code'] = feature['code']
                exception_msg: Optional[str] = None
                if query['query_type'] == 'GEOMETRIC DUPLICATE':
                    exception_msg = 'Duplicated feature'
                else:
                    exception_msg = 'Orphan feature'
                new_feature['Exception'] = exception_msg
                if not feature['geom_WKT']:
                    feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error getting geometry for feature "{feature['code']}" on table "{query['table_name']}"'))
                    continue
                new_feature.setGeometry(QgsGeometry.fromWkt(feature['geom_WKT']))
                features_to_add.append(new_feature)

        if query['create_layer'] and len(features) > 0 and temporal_layer is not None:
            # Add features to temporal layer
            temporal_layer.startEditing()
            temporal_layer.addFeatures(features_to_add)
            temporal_layer.commitChanges()
            self.temporal_layers_to_add.append(temporal_layer)

        msg = exception_message.format(len(features))
        if query['except_lvl'] == 2:
            # Save warning message
            self.warning_messages.append(self.tr(f'WARNING-{query['error_code']} ({query['table_name']}) ({query['query_type']}): ' + msg))
        else:
            # Save error message
            self.error_messages.append(self.tr(f'ERROR-{query['error_code']} ({query['table_name']}) ({query['query_type']}): ' + msg))

    def check_mandatory_null_or_outlayer(self, query, harcoded_queries: dict[int, str], sys_messages_dict: dict[int, str], feedback: QgsProcessingFeedback):
        """ Check mandatory null or outlayer """

        # Get exception message
        exception_message: Optional[str] = sys_messages_dict[query['error_message_id']]
        info_message: Optional[str] = sys_messages_dict[query['info_message_id']]
        if exception_message is None or exception_message == '' or info_message is None or info_message == '':
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']}({query['query_type']}): Error getting messages for table "{query['table_name']}"'))
            return

        # Build check query
        query_data, query_data_nogeom, columns = self.build_check_query(query, feedback)
        if query_data is None:
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error building check query on table "{query['table_name']}"'))
            return
        if columns is None:
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error getting mandatory columns on table "{query['table_name']}"'))
            return

        # Exectue check query
        features = self.dao_data.get_rows(query_data)
        if not features and self.dao_data.last_error is not None:
            features = self.dao_data.get_rows(query_data_nogeom)
            if not features and self.dao_data.last_error is not None:
                # Print error message
                feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error getting features for table "{query['table_name']}". {self.dao_data.last_error}'))
                return
        if not features and self.dao_data.last_error is None:
            # Save info message
            if query['query_type'] == 'MANDATORY NULL' and (query['extra_condition'] == '' or query['extra_condition'] is None):
                self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(f'{columns}')))
            elif query['query_type'] == 'MANDATORY NULL' and query['extra_condition'] is not None and query['extra_condition'] != '':
                # Get additional conditions
                conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                if conditions:
                    self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(f'{columns}', conditions.group(1), conditions.group(2))))
                else:
                    feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['table_name']}) ({query['query_type']}): Error getting additional conditions for table "{query['table_name']}"'))
                    return
            elif query['query_type'] == 'OUTLAYER':
                self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(self.outlayer_values[columns[0]]['min'], self.outlayer_values[columns[0]]['max'], f'{columns}')))
            return

        if query['create_layer']:
            # Create temporal layer
            temporal_layer = QgsVectorLayer(f'{query['geometry_type']}', f'{query['query_type'].replace(" ", "_").lower()}_{query['table_name']}', 'memory')
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
                if query['query_type'] == 'MANDATORY NULL':
                    # Check if feature field is None
                    if feature[column] in (None, 'NULL', 'null'):
                        invalid_columns.append(column)
                        columns_dict[column] += 1
                elif query['query_type'] == 'OUTLAYER':
                    value = feature[column]
                    min_val = self.outlayer_values[column]['min']
                    max_val = self.outlayer_values[column]['max']
                    include_min = self.outlayer_values[column]['include_min']
                    include_max = self.outlayer_values[column]['include_max']

                    # Check if value is outside bounds considering inclusion flags
                    is_below_min = value < min_val if include_min else value <= min_val
                    is_above_max = value > max_val if include_max else value >= max_val

                    if is_below_min or is_above_max:
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
                    feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): Error getting geometry for feature "{feature['code']}" on table "{query['table_name']}"'))
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
                                feedback.pushWarning(self.tr(f'ERROR-{query['error_code']}: Error getting additional conditions for table[{query['table_name']}]'))
                                continue
                    else:
                        valid_columns.append(col)

                # Save error message
                if error_msg != '':
                    if query['except_lvl'] == 2:
                        self.warning_messages.append(self.tr(f'WARNING-{query['error_code']}/{index+1} ({query['table_name']}) ({query['query_type']}): ' + error_msg))
                    else:
                        self.error_messages.append(self.tr(f'ERROR-{query['error_code']}/{index+1} ({query['table_name']}) ({query['query_type']}): ' + error_msg))

            # Save info message for valid columns
            if len(valid_columns) > 0:
                if query['query_type'] == 'OUTLAYER':
                    for col in valid_columns:
                        self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(self.outlayer_values[col]['min'], self.outlayer_values[col]['max'], col)))
                else:
                    if query['extra_condition'] is None or query['extra_condition'] == "":
                        self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(valid_columns)))
                    else:
                        conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                        if conditions:
                            self.info_messages.append(self.tr(f'INFO ({query["table_name"]}): ' + info_message.format(valid_columns, conditions.group(1), conditions.group(2))))
                        else:
                            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['table_name']}) ({query['query_type']}): Error getting additional conditions for table[{query['table_name']}]'))
                            return

    def postProcessAlgorithm(self, context, feedback: QgsProcessingFeedback):
        """ Create temporal layers on main thread """

        feedback.setProgressText(self.tr('\nERRORS\n----------'))
        for msg in self.error_messages:
            feedback.setProgressText(msg)
        feedback.setProgressText(self.tr('\nWARNINGS\n--------------'))
        for msg in self.warning_messages:
            feedback.setProgressText(msg)
        if not self.bool_show_only_errors:
            feedback.setProgressText(self.tr('\nINFO\n------'))
            for msg in self.info_messages:
                feedback.setProgressText(msg)

        if len(self.temporal_layers_to_add) > 0:
            group_name = "Check Project Temporal Layers"
            group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            if group is None:
                QgsProject.instance().layerTreeRoot().insertGroup(0, group_name)
                group = QgsProject.instance().layerTreeRoot().findGroup(group_name)
            for layer in self.temporal_layers_to_add:
                QgsProject.instance().addMapLayer(layer, False)
                group.addLayer(layer)
        return {}

    def build_check_query(self, query, feedback: QgsProcessingFeedback) -> tuple[Optional[str], Optional[str], Optional[list[str]]]:
        """ Build check query and return columns to check """

        check_query: Optional[str] = None
        check_query_nogeom: Optional[str] = None
        columns_checked: Optional[list[str]] = None

        # Get columns
        if query['columns'] is None:
            feedback.pushWarning(self.tr(f'ERROR-{query['error_code']} ({query['query_type']}): No columns found for table "{query['table_name']}"'))
            return None, None, None
        columns = query['columns'].strip("{}").split(", ")
        columns_select: Optional[str] = None
        for col in columns:
            # Add column conditions to check query WHERE clause
            if query['query_type'] == 'OUTLAYER':
                max_operator = ">=" if self.outlayer_values[col]["include_max"] else ">"
                min_operator = "<=" if self.outlayer_values[col]["include_min"] else "<"
                if columns_select is None:
                    columns_select = f'''({col} {max_operator} {self.outlayer_values[col]["max"]} OR {col} {min_operator} {self.outlayer_values[col]["min"]})'''
                else:
                    columns_select += f''' OR ({col} {max_operator} {self.outlayer_values[col]["max"]} OR {col} {min_operator} {self.outlayer_values[col]["min"]})'''
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

        if query['table_name']:
            if condition_select is not None:
                # Build check query with WHERE clause and additional conditions
                check_query = f'SELECT *, AsWKT(CastAutomagic(geom)) as geom_wkt FROM {query['table_name']} WHERE ({columns_select}) '
                check_query_nogeom = f'SELECT * FROM {query['table_name']} WHERE ({columns_select}) '
                check_query += condition_select
            else:
                # Build check query with WHERE clause
                check_query = f'SELECT *, AsWKT(CastAutomagic(geom)) as geom_wkt FROM {query['table_name']} WHERE {columns_select} '
                check_query_nogeom = f'SELECT * FROM {query['table_name']} WHERE {columns_select} '

        return check_query, check_query_nogeom, columns_checked

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)
