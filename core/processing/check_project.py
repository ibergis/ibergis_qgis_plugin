from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterBoolean, QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry
from typing import Any, Optional
from qgis.PyQt.QtCore import QCoreApplication, QVariant

from ...lib.tools_gpkgdao import DrGpkgDao
from ...lib import tools_qt, tools_db
from ... import global_vars
import re
from typing import Match


class DrCheckProjectAlgorithm(QgsProcessingAlgorithm):

    temporal_layers_to_add: list[QgsVectorLayer] = []

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return 'check_project'

    def displayName(self) -> str:
        return tools_qt.tr('Check Project')

    def createInstance(self) -> QgsProcessingAlgorithm:
        return DrCheckProjectAlgorithm()

    def initAlgorithm(self, config: dict[str, Any] | None = None) -> None:
        return

    def processAlgorithm(self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> dict[str, Any]:
        self.temporal_layers_to_add = []
        self.dao_data: Optional[DrGpkgDao] = global_vars.gpkg_dao_data
        self.dao_config: Optional[DrGpkgDao] = global_vars.gpkg_dao_config

        if self.dao_data is None or self.dao_config is None:
            return {}

        # Get messages from sys_message
        sql: str = "SELECT id, COALESCE(i18n_text, text) AS text FROM sys_message"
        sys_messages = self.dao_config.get_rows(sql)
        if not sys_messages:
            feedback.pushWarning(self.tr(f'ERROR: No sys messages found'))
            return {}

        # Get queries from checkproject_query table
        sql: str = "SELECT * FROM checkproject_query ORDER BY query_type"
        queries = self.dao_config.get_rows(sql)
        if not queries:
            feedback.pushWarning(self.tr(f'ERROR: No check project queries found'))
            return {}

        # Query params: id, query_type, table_name, columns, extra_condition, create_layer, geometry_type, message_id, except_lvl, query_text
        # Query types: GEOMETRIC, MANDATORY NULL
        for query in queries:
            query_type: str = query['query_type']
            if query_type == 'GEOMETRIC DUPLICATE' or query_type == 'GEOMETRIC ORPHAN':
                # Check geometrics
                if not query['query_text']:
                    feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error getting query_text on table[{query['table_name']}]'))
                    continue
                query_data = query['query_text']
                features = self.dao_data.get_rows(query_data)
                if not features:
                    continue

                # Get exception message
                exception_message: Optional[str] = None
                for msg in sys_messages:
                    if msg['id'] == query['message_id']:
                        exception_message = msg['text']
                if exception_message is None or exception_message == '':
                    feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Exception message not found for table[{query['table_name']}]'))
                    continue

                if query['create_layer']:
                    temporal_layer = QgsVectorLayer(f'{query['geometry_type']}', f'{query['query_type'].replace(" ", "_").lower()}_{query['table_name']}', 'memory')
                    temporal_layer.setCrs(QgsProject.instance().crs())
                    temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
                    temporal_layer.updateFields()
                    features_to_add: list[QgsFeature] = []

                # Build exception message
                for feature in features:
                    if query['create_layer'] and len(features) > 0:
                        new_feature = QgsFeature(temporal_layer.fields())
                        new_feature['Code'] = feature['code']
                        exception_msg: Optional[str] = None
                        if query['query_type'] == 'GEOMETRIC DUPLICATES':
                            exception_msg = 'Duplicated features'
                        else:
                            exception_msg = 'Orphan feature'
                        new_feature['Exception'] = exception_msg
                        geom_query = f'SELECT AsWKT(CastAutomagic(geom)) as geom FROM {query['table_name']} WHERE code == "{feature['code']}"'
                        row = self.dao_data.get_row(geom_query)
                        if not row:
                            feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error getting geometry for feature[{feature['code']}] on table[{query['table_name']}]'))
                            continue
                        new_feature.setGeometry(QgsGeometry.fromWkt(row['geom']))
                        features_to_add.append(new_feature)

                if query['create_layer'] and len(features) > 0 and temporal_layer is not None:
                    temporal_layer.startEditing()
                    temporal_layer.addFeatures(features_to_add)
                    temporal_layer.commitChanges()
                    self.temporal_layers_to_add.append(temporal_layer)

                msg = exception_message.format(query['table_name'], len(features))
                if query['except_lvl'] == 2:
                    feedback.pushWarning(self.tr(f'WARNING [{query['query_type']}] ' + msg))
                else:
                    feedback.setProgressText(self.tr(f'ERROR [{query['query_type']}] ' + msg))

            elif query_type == 'MANDATORY NULL':
                # Check mandatory fields in null
                query_data, columns = self.build_check_query(query)
                if query_data is None:
                    feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error building check query on table[{query['table_name']}]'))
                    continue
                if columns is None:
                    feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error getting mandatory columns on table[{query['table_name']}]'))
                    continue

                # Exectue check query
                features = self.dao_data.get_rows(query_data)
                if not features:
                    continue

                if query['create_layer']:
                    temporal_layer = QgsVectorLayer(f'{query['geometry_type']}', f'mandatory_null_{query['table_name']}', 'memory')
                    temporal_layer.setCrs(QgsProject.instance().crs())
                    temporal_layer.dataProvider().addAttributes([QgsField('Code', QVariant.String), QgsField('Exception', QVariant.String)])
                    temporal_layer.updateFields()
                    features_to_add: list[QgsFeature] = []

                columns_dict: dict[str,int] = {}

                # Check features
                for feature in features:
                    null_columns: list[str] = []
                    # Check feature fields
                    for column in columns:
                        # Check if feature field is None
                        if feature[column] in (None, 'NULL', 'null'):
                            null_columns.append(column)
                            if column in columns_dict.keys():
                                columns_dict[column] += 1
                            else:
                                columns_dict[column] = 1

                    if query['create_layer'] and len(null_columns) > 0:
                        new_feature = QgsFeature(temporal_layer.fields())
                        new_feature['Code'] = feature['code']
                        exception_msg: Optional[str] = None
                        for col in null_columns:
                            if exception_msg is None:
                                exception_msg = f'Null columns: {col}'
                            else:
                                exception_msg += f', {col}'
                        new_feature['Exception'] = exception_msg
                        geom_query = f'SELECT AsWKT(CastAutomagic(geom)) as geom FROM {query['table_name']} WHERE code == "{feature['code']}"'
                        row = self.dao_data.get_row(geom_query)
                        if not row:
                            feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error getting geometry for feature[{feature['code']}] on table[{query['table_name']}]'))
                            continue
                        new_feature.setGeometry(QgsGeometry.fromWkt(row['geom']))
                        features_to_add.append(new_feature)

                # Print check result if its negative
                if columns_dict:
                    if query['create_layer'] and len(features_to_add) > 0 and temporal_layer is not None:
                        temporal_layer.startEditing()
                        temporal_layer.addFeatures(features_to_add)
                        temporal_layer.commitChanges()
                        self.temporal_layers_to_add.append(temporal_layer)
                    # Get exception message
                    exception_message: Optional[str] = None
                    for msg in sys_messages:
                        if msg['id'] == query['message_id']:
                            exception_message = msg['text']
                    if exception_message is None or exception_message == '':
                        feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Exception message not found for table[{query['table_name']}]'))
                        continue
                    # Build exception message
                    for col in columns_dict.keys():
                        if query['extra_condition'] is None or query['extra_condition'] == "":
                            msg = exception_message.format(query['table_name'], col, columns_dict[col])
                        else:
                            conditions: Optional[Match[str]] = re.search(r'AND\s+(\w+)\s*==\s*"([^"]+)"', query['extra_condition'])
                            if conditions:
                                msg = exception_message.format(query['table_name'], col, conditions.group(1), conditions.group(2), columns_dict[col])
                            else:
                                feedback.pushWarning(self.tr(f'ERROR - [{query['query_type']}]: Error getting additional conditions for table[{query['table_name']}]'))
                                continue
                        if query['except_lvl'] == 2:
                            feedback.pushWarning(self.tr(f'WARNING [{query['query_type']}] ' + msg))
                        else:
                            feedback.setProgressText(self.tr(f'ERROR [{query['query_type']}] ' + msg))

        return {}

    def postProcessAlgorithm(self, context, feedback: QgsProcessingFeedback):
        """ Create temporal layers on main thread """
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

    def build_check_query(self, query) -> tuple[Optional[str], Optional[list[str]]]:
        """ Build query """

        check_query: Optional[str] = None
        columns_checked: Optional[list[str]] = None

        # Get columns
        if query['columns'] is None:
            #TODO error message
            return check_query
        columns = query['columns'].strip("{}").split(", ")
        columns_select: Optional[str] = None
        for col in columns:
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
            condition_select = query['extra_condition']

        if query['table_name']:
            check_query = f'SELECT * FROM {query['table_name']} WHERE ({columns_select}) '
            if condition_select is not None:
                check_query += condition_select

        return check_query, columns_checked

    def helpUrl(self):
        return "https://github.com/drain-iber"

    def tr(self, string: str):
        return QCoreApplication.translate('Processing', string)
