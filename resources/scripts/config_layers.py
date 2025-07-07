from qgis.core import QgsProject, QgsEditorWidgetSetup

value_relations_dict = {
    # "layer_1": {
    #     "valueRelation": [
    #         {
    #             "keyColumn": "macroexpl_id",
    #             "valueColumn": "name",
    #             "targerLayer": "v_edit_exploitation",
    #             "targetColumn": "macroexpl_id",
    #             "nullValue": False,
    #             "filterExpression": None
    #         }
    #     ]
    # },
}


def get_tablename_from_layer(layer):
    """ Gets tablename of a layer """
    layer_tablename = layer.name()

    uri = layer.dataProvider().uri().uri()
    # Get the actual layername
    for part in uri.split("|"):
        if 'layername' in part:
            layer_tablename = part.split("=")[1].strip("'")

    return layer_tablename


def get_project_layers():
    """ Return layers in the same order as listed in TOC """

    layers = [layer.layer() for layer in QgsProject.instance().layerTreeRoot().findLayers()]

    return layers


def get_layer_by_tablename(tablename, layers=None, show_warning_=False):
    """ Iterate over all layers and get the one with selected @tablename """

    # Check if we have any layer loaded
    if layers is None:
        layers = get_project_layers()
    if len(layers) == 0:
        return None

    # Iterate over all layers
    layer = None
    for cur_layer in layers:
        cur_layer_tablename = get_tablename_from_layer(cur_layer)

        if cur_layer_tablename == tablename:
            layer = cur_layer
            break

    if layer is None and show_warning_:
        print(f"Layer not found: {tablename}")

    return layer


def config_layers():
    # Get a list of all map layers in the project
    map_layers = get_project_layers()

    # Iterate through each layer and print its name and type
    for layer in map_layers:
        layer_name = layer.name()
        layer_tablename = get_tablename_from_layer(layer)
        
        print(f"Layer Name: {layer_name}, Table name: {layer_tablename}")
        # Manage valueRelation
        valueRelation = None
        valueRelation = value_relations_dict.get(layer_name)
        # sql = f"SELECT addparam FROM sys_table WHERE id = '{tablename_og}'"
        # row = tools_db.get_row(sql)
        # if row:
        #     valueRelation = row[0]
        #     if valueRelation:
        #         valueRelation = valueRelation.get('valueRelation')
        if valueRelation:
            for vr in valueRelation:
                vr_layer = get_layer_by_tablename(vr['targerLayer'], map_layers)  # Get 'Layer'
                field_index = vr_layer.fields().indexFromName(vr['targetColumn'])   # Get 'Column' index
                vr_key_column = vr['keyColumn']  # Get 'Key'
                vr_value_column = vr['valueColumn']  # Get 'Value'
                vr_allow_nullvalue = vr['nullValue']  # Get null values
                vr_filter_expression = vr['filterExpression']  # Get 'FilterExpression'
                if vr_filter_expression is None:
                    vr_filter_expression = ''

                # Create and apply ValueRelation config
                editor_widget_setup = QgsEditorWidgetSetup('ValueRelation', {'Layer': f'{layer.id()}',
                                                                                'Key': f'{vr_key_column}',
                                                                                'Value': f'{vr_value_column}',
                                                                                'AllowNull': f'{vr_allow_nullvalue}',
                                                                                'FilterExpression': f'{vr_filter_expression}'
                                                                                })
                vr_layer.setEditorWidgetSetup(field_index, editor_widget_setup)


if __name__ == '__main__':
    config_layers()
