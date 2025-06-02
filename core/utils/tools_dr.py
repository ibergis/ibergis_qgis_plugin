"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import configparser
import inspect
import json
import os
import random
import re
import sys

if 'nt' in sys.builtin_module_names:
    import ctypes
from functools import partial

from qgis.PyQt.QtCore import Qt, QStringListModel, QVariant, QDate, QSettings, QLocale, QRegExp
from qgis.PyQt.QtGui import QColor, QFontMetrics, QStandardItemModel, QIcon, QStandardItem, QIntValidator, \
    QDoubleValidator, QRegExpValidator
from qgis.PyQt.QtWidgets import QSpacerItem, QSizePolicy, QLineEdit, QLabel, QComboBox, QGridLayout, QTabWidget, \
    QCompleter, QPushButton, QTableView, QCheckBox, QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit, QToolButton, \
    QWidget, QDockWidget
from qgis.core import QgsProject, QgsPointXY, QgsVectorLayer, QgsField, QgsFeature, QgsSymbol, \
    QgsSimpleFillSymbolLayer, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsCoordinateTransform, \
    QgsCoordinateReferenceSystem, QgsFieldConstraints, QgsEditorWidgetSetup, QgsRasterLayer, QgsSpatialIndex, \
    QgsWkbTypes
from qgis.gui import QgsDateTimeEdit, QgsRubberBand

from ..ui.dialog import DrDialog
from ..ui.main_window import DrMainWindow
from ..ui.docker import DrDocker
from . import tools_backend_calls, tools_fct
from ... import global_vars
from ...lib import tools_qgis, tools_qt, tools_log, tools_os, tools_db
from ...lib.tools_qt import DrHyperLinkLabel, DrHyperLinkLineEdit


def load_settings(dialog, plugin='core'):
    """ Load user UI settings related with dialog position and size """

    # Get user UI config file
    try:
        x = get_config_parser('dialogs_position', f"{dialog.objectName()}_x", "user", "session", plugin=plugin)
        y = get_config_parser('dialogs_position', f"{dialog.objectName()}_y", "user", "session", plugin=plugin)
        width = get_config_parser('dialogs_dimension', f"{dialog.objectName()}_width", "user", "session", plugin=plugin)
        height = get_config_parser('dialogs_dimension', f"{dialog.objectName()}_height", "user", "session", plugin=plugin)

        v_screens = ctypes.windll.user32
        screen_x = v_screens.GetSystemMetrics(78)  # Width of virtual screen
        screen_y = v_screens.GetSystemMetrics(79)  # Height of virtual screen
        monitors = v_screens.GetSystemMetrics(80)  # Will return an integer of the number of display monitors present.

        if None in (x, y) or ((int(x) < 0 and monitors == 1) or (int(y) < 0 and monitors == 1)):
            dialog.resize(int(width), int(height))
        else:
            if int(x) > screen_x:
                x = int(screen_x) - int(width)
            if int(y) > screen_y:
                y = int(screen_y)
            dialog.setGeometry(int(x), int(y), int(width), int(height))
    except Exception:
        pass


def save_settings(dialog, plugin='core'):
    """ Save user UI related with dialog position and size """

    # Ensure that 'plugin' parameter isn't being populated with int from signal
    try:
        plugin = int(plugin)
        plugin = 'core'
    except ValueError:
        pass

    try:
        x, y = dialog.geometry().x(), dialog.geometry().y()
        w, h = dialog.geometry().width(), dialog.geometry().height()
        set_config_parser('dialogs_dimension', f"{dialog.objectName()}_width", f"{w}", plugin=plugin)
        set_config_parser('dialogs_dimension', f"{dialog.objectName()}_height", f"{h}", plugin=plugin)
        set_config_parser('dialogs_position', f"{dialog.objectName()}_x", f"{x}", plugin=plugin)
        set_config_parser('dialogs_position', f"{dialog.objectName()}_y", f"{y}", plugin=plugin)
    except Exception:
        pass


def initialize_parsers():
    """ Initialize parsers of configuration files: init, session, giswater, user_params """

    for config in global_vars.list_configs:
        filepath, parser = _get_parser_from_filename(config)
        global_vars.configs[config][0] = filepath
        global_vars.configs[config][1] = parser


def get_config_parser(section: str, parameter: str, config_type, file_name, prefix=True, get_comment=False,
                      chk_user_params=True, get_none=False, force_reload=False, plugin='core') -> str:
    """ Load a simple parser value """

    if config_type not in ("user", "project"):
        msg = "{0}: Reference {1} = '{2}' it is not managed"
        msg_params = ("get_config_parser", "config_type", config_type,)
        tools_log.log_warning(msg, msg_params=msg_params)
        return None

    # Get configuration filepath and parser object
    path = global_vars.configs[file_name][0]
    parser = global_vars.configs[file_name][1]

    if plugin != 'core':
        path = f"{global_vars.user_folder_dir}{os.sep}{plugin}{os.sep}config{os.sep}{file_name}.config"
        parser = None
        chk_user_params = False

    # Needed to avoid errors with giswater plugins
    if path is None:
        msg = "{0}: Config file is not set"
        msg_params = ("get_config_parser",)
        tools_log.log_warning(msg, msg_params=msg_params)
        return None

    value = None
    raw_parameter = parameter
    try:
        if parser is None:
            if plugin == 'core':
                msg = "Creating parser for file: {0}"
                msg_params = (path,)
                tools_log.log_info(msg, msg_params=msg_params)
            parser = configparser.ConfigParser(comment_prefixes=";", allow_no_value=True, strict=False)
            parser.read(path)

        # If project has already been loaded and filename is 'init' or 'session', always read and parse file
        if force_reload or (global_vars.project_loaded and file_name in ('init', 'session')):
            parser = configparser.ConfigParser(comment_prefixes=";", allow_no_value=True, strict=False)
            parser.read(path)

        if config_type == 'user' and prefix and global_vars.project_type is not None:
            parameter = f"{global_vars.project_type}_{parameter}"

        if not parser.has_section(section) or not parser.has_option(section, parameter):
            if chk_user_params and config_type in "user":
                value = _check_user_params(section, raw_parameter, file_name, prefix=prefix)
                set_config_parser(section, raw_parameter, value, config_type, file_name, prefix=prefix, chk_user_params=False)
        else:
            value = parser[section][parameter]

        # If there is a value and you don't want to get the comment, it only gets the value part
        if value is not None and not get_comment:
            value = value.split('#')[0].strip()

        if not get_none and str(value) in "None":
            value = None

        # Check if the parameter exists in the inventory, if not creates it
        if chk_user_params and config_type in "user":
            _check_user_params(section, raw_parameter, file_name, prefix)
    except Exception as e:
        msg = "{0} exception [{1}]: {2}"
        msg_params = ("get_config_parser", type(e).__name__, e,)
        tools_log.log_warning(msg, msg_params=msg_params)

    return value


def set_config_parser(section: str, parameter: str, value: str = None, config_type="user", file_name="session",
                      comment=None, prefix=True, chk_user_params=True, plugin='core'):
    """ Save simple parser value """

    if config_type not in ("user", "project"):
        msg = "{0}: Reference {1} = '{2}' it is not managed"
        msg_params = ("set_config_parser", "config_type", config_type,)
        tools_log.log_warning(msg, msg_params=msg_params)
        return None

    # Get configuration filepath and parser object
    path = global_vars.configs[file_name][0]

    if plugin != 'core':
        path = f"{global_vars.user_folder_dir}{os.sep}{plugin}{os.sep}config{os.sep}{file_name}.config"
        chk_user_params = False

    try:

        parser = configparser.ConfigParser(comment_prefixes=";", allow_no_value=True, strict=False)
        parser.read(path)

        raw_parameter = parameter
        if config_type == 'user' and prefix and global_vars.project_type is not None:
            parameter = f"{global_vars.project_type}_{parameter}"

        # Check if section exists in file
        if section not in parser:
            parser.add_section(section)

        # Cast to str because parser only allow strings
        value = f"{value}"
        if value is not None:
            # Add the comment to the value if there is one
            if comment is not None:
                value += f" #{comment}"
            # If the previous value had an inline comment, don't remove it
            else:
                prev = get_config_parser(section, parameter, config_type, file_name, False, True, False)
                if prev is not None and "#" in prev:
                    value += f" #{prev.split('#')[1]}"
            parser.set(section, parameter, value)
            # Check if the parameter exists in the inventory, if not creates it
            if chk_user_params and config_type in "user":
                _check_user_params(section, raw_parameter, file_name, prefix)
        else:
            parser.set(section, parameter)  # This is just for writing comments

        with open(path, 'w') as configfile:
            parser.write(configfile)
            configfile.close()

    except Exception as e:
        msg = "{0} exception [{1}]: {2}"
        msg_params = ("set_config_parser", type(e).__name__, e,)
        tools_log.log_warning(msg, msg_params=msg_params)
        return


def save_current_tab(dialog, tab_widget, selector_name):
    """
    Save the name of current tab used by the user into QSettings()
        :param dialog: QDialog
        :param tab_widget: QTabWidget
        :param selector_name: Name of the selector (String)
    """

    try:
        index = tab_widget.currentIndex()
        tab = tab_widget.widget(index)
        if tab:
            tab_name = tab.objectName()
            dlg_name = dialog.objectName()
            set_config_parser('dialogs_tab', f"{dlg_name}_{selector_name}", f"{tab_name}")
    except Exception:
        pass


def open_dialog(dlg, dlg_name=None, stay_on_top=True, title=None, hide_config_widgets=False):
    """ Open dialog """

    # Manage translate
    if dlg_name:
        tools_qt.manage_translation(dlg_name, dlg)

    # Set window title
    if title is not None:
        dlg.setWindowTitle(title)

    # Manage stay on top, maximize/minimize button and information button
    flags = Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint

    if stay_on_top:
        flags |= Qt.WindowStaysOnTopHint

    dlg.setWindowFlags(flags)

    if hide_config_widgets:
        hide_widgets_form(dlg, dlg_name)

    # Create btn_help
    add_btn_help(dlg)

    # Open dialog
    if issubclass(type(dlg), DrDialog):
        dlg.open()
    elif issubclass(type(dlg), DrMainWindow):
        dlg.show()
    else:
        dlg.show()


def close_dialog(dlg, delete_dlg=True, plugin='core'):
    """ Close dialog """

    save_settings(dlg, plugin=plugin)
    dlg.close()
    if delete_dlg:
        try:
            dlg.deleteLater()
        except RuntimeError:
            pass


def connect_signal(obj, pfunc, section, signal_name):
    """
    Connects a signal like this -> obj.connect(pfunc) and stores it in global_vars.active_signals
    :param obj: the object to which the signal will be connected
    :param pfunc: the partial object containing the function to connect and the arguments if needed
    :param section: the name of the parent category
    :param signal_name: the name of the signal. Should be {functionname}_{obj}_{pfunc} like -> {replace_arc}_{xyCoordinates}_{mouse_move_arc}
    :return: the signal. If failed to connect it will return None
    """

    if section not in global_vars.active_signals:
        global_vars.active_signals[section] = {}
    # If the signal is already connected, don't reconnect it, just return it.
    if signal_name in global_vars.active_signals[section]:
        _, signal, _ = global_vars.active_signals[section][signal_name]
        return signal
    # Try to connect signal and save it in the dict
    try:
        signal = obj.connect(pfunc)
        global_vars.active_signals[section][signal_name] = (obj, signal, pfunc)
        return signal
    except Exception:
        pass
    return None


def disconnect_signal(section, signal_name=None, pop=True):
    """
    Disconnects a signal
        :param section: the name of the parent category
        :param signal_name: the name of the signal
        :param pop: should always be True, if False it won't remove the signal from the dict.
        :return: 2 things -> (object which had the signal connected, partial function that was connected with the signal)
                 (None, None) if it couldn't find the signal
    """

    if section not in global_vars.active_signals:
        return None, None

    if signal_name is None:
        old_signals = []
        for signal in global_vars.active_signals[section]:
            old_signals.append(disconnect_signal(section, signal, False))
        for signal in old_signals:
            global_vars.active_signals[section].pop(signal, None)
    if signal_name not in global_vars.active_signals[section]:
        return None, None

    obj, signal, pfunc = global_vars.active_signals[section][signal_name]
    try:
        obj.disconnect(signal)
    except Exception:
        pass
    finally:
        if pop:
            global_vars.active_signals[section].pop(signal_name, None)
            return obj, pfunc
        return signal_name


def create_body(form='', feature='', filter_fields='', extras=None):
    """ Create and return parameters as body to functions"""

    info_types = {'full': 1}
    info_type = info_types.get(global_vars.project_vars['info_type'])
    lang = QSettings().value('locale/globalLocale', QLocale().name())

    client = f'{{"client":{{"device":4, "lang":"{lang}"'
    if info_type is not None:
        client += f', "infoType":{info_type}'
    if global_vars.project_epsg is not None:
        client += f', "epsg":{global_vars.project_epsg}'
    client += '}, '

    form = f'"form":{{{form}}}, '
    feature = f'"feature":{{{feature}}}, '
    filter_fields = f'"filterFields":{{{filter_fields}}}'
    page_info = '"pageInfo":{}'
    data = f'"data":{{{filter_fields}, {page_info}'
    if extras is not None:
        data += ', ' + extras
    data += '}}'
    body = "" + client + form + feature + data

    return body


def draw_by_json(complet_result, rubber_band, margin=None, reset_rb=True, color=QColor(255, 0, 0, 100), width=3):

    try:
        if complet_result['body']['feature']['geometry'] is None:
            return
        if complet_result['body']['feature']['geometry']['st_astext'] is None:
            return
    except KeyError:
        return

    list_coord = re.search(r'\((.*)\)', str(complet_result['body']['feature']['geometry']['st_astext']))
    max_x, max_y, min_x, min_y = tools_qgis.get_max_rectangle_from_coords(list_coord)

    if reset_rb:
        reset_rubberband(rubber_band)
    if str(max_x) == str(min_x) and str(max_y) == str(min_y):
        point = QgsPointXY(float(max_x), float(max_y))
        tools_qgis.draw_point(point, rubber_band, color, width)
    else:
        points = tools_qgis.get_geometry_vertex(list_coord)
        tools_qgis.draw_polyline(points, rubber_band, color, width)
    if margin is not None:
        tools_qgis.zoom_to_rectangle(max_x, max_y, min_x, min_y, margin, change_crs=False)


def add_layer_database(tablename=None, the_geom="the_geom", field_id="id", group="GW Layers", sub_group=None,
                       style_id="-1", alias=None, sub_sub_group=None):
    """
    Put selected layer into TOC
        :param tablename: Postgres table name (String)
        :param the_geom: Geometry field of the table (String)
        :param field_id: Field id of the table (String)
        :param group: Name of the group that will be created in the toc (String)
        :param style_id: Id of the style we want to load (integer or String)
    """

    tablename_og = tablename
    schema_name = global_vars.dao_db_credentials['schema'].replace('"', '')
    uri = tools_db.get_uri()
    uri.setDataSource(schema_name, f'{tablename}', the_geom, None, field_id)
    if the_geom:
        try:
            uri.setSrid(f"{global_vars.data_epsg}")
        except:
            pass
    create_groups = get_config_parser("system", "force_create_qgis_group_layer", "user", "init", prefix=False)
    create_groups = tools_os.set_boolean(create_groups, default=False)
    if sub_group:
        sub_group = sub_group.capitalize()
    if sub_sub_group:
        sub_sub_group = sub_sub_group.capitalize()

    if the_geom == "rast":
        connString = f"PG: dbname={global_vars.dao_db_credentials['db']} host={global_vars.dao_db_credentials['host']} " \
                     f"user={global_vars.dao_db_credentials['user']} password={global_vars.dao_db_credentials['password']} " \
                     f"port={global_vars.dao_db_credentials['port']} mode=2 schema={global_vars.dao_db_credentials['schema']} " \
                     f"column={the_geom} table={tablename}"
        if alias: tablename = alias
        layer = QgsRasterLayer(connString, tablename)
        tools_qt.add_layer_to_toc(layer, group, sub_group, create_groups=create_groups)

    else:
        if alias: tablename = alias
        layer = QgsVectorLayer(uri.uri(), f'{tablename}', 'postgres')
        tools_qt.add_layer_to_toc(layer, group, sub_group, create_groups=create_groups, sub_sub_group=sub_sub_group)

        # The triggered function (action.triggered.connect(partial(...)) as the last parameter sends a boolean,
        # if we define style_id = None, style_id will take the boolean of the triggered action as a fault,
        # therefore, we define it with "-1"
        if style_id in (None, "-1"):
            # Get style_id from tablename
            sql = f"SELECT id FROM sys_style WHERE idval = '{tablename_og}'"
            row = tools_db.get_row(sql)
            if row:
                style_id = row[0]

        # Apply style to layer if it has one configured
        if style_id not in (None, "-1"):
            body = f'$${{"data":{{"style_id":"{style_id}"}}}}$$'
            style = execute_procedure('gw_fct_getstyle', body)
            if style is None or style['status'] == 'Failed':
                return
            if 'styles' in style['body']:
                if 'style' in style['body']['styles']:
                    qml = style['body']['styles']['style']
                    tools_qgis.create_qml(layer, qml)

        # Set layer config
        if tablename:
            feature = '"tableName":"' + str(tablename_og) + '", "isLayer":true'
            extras = '"infoType":"' + str(global_vars.project_vars['info_type']) + '"'
            body = create_body(feature=feature, extras=extras)
            json_result = execute_procedure('gw_fct_getinfofromid', body)
            config_layer_attributes(json_result, layer, alias)

    global_vars.iface.mapCanvas().refresh()


def add_layer_temp(dialog, data, layer_name, force_tab=True, reset_text=True, tab_idx=1, del_old_layers=True,
                   group='GW Temporal Layers', call_set_tabs_enabled=True, close=True):
    """
    Add QgsVectorLayer into TOC
        :param dialog: Dialog where to find the tab to be displayed and the textedit to be filled (QDialog or QMainWindow)
        :param data: Json with information
        :param layer_name: Name that will be given to the layer (String)
        :param force_tab: Boolean that tells us if we want to show the tab or not (bool)
        :param reset_text: It allows us to delete the text from the Qtexedit log, or add text below (bool)
        :param tab_idx: Log tab index (int)
        :param del_old_layers: Delete layers added in previous operations (bool)
        :param group: Name of the group to which we want to add the layer (String)
        :param call_set_tabs_enabled: set all tabs, except the last, enabled or disabled (bool).
        :param close: Manage buttons accept, cancel, close...  in function def fill_tab_log(...) (bool).
        :return: Dictionary with text as result of previuos data (String), and list of layers added (QgsVectorLayer).
    """

    text_result = None
    temp_layers_added = []
    srid = global_vars.data_epsg
    i = 0
    for k, v in list(data.items()):
        if str(k) == "info":
            text_result, change_tab = fill_tab_log(dialog, data, force_tab, reset_text, tab_idx, call_set_tabs_enabled, close)
        elif k in ('point', 'line', 'polygon'):
            if 'features' not in data[k]:
                continue
            counter = len(data[k]['features'])
            if counter > 0:
                counter = len(data[k]['features'])
                geometry_type = data[k]['geometryType']
                aux_layer_name = layer_name
                try:
                    if not layer_name:
                        aux_layer_name = data[k]['layerName']
                except KeyError:
                    aux_layer_name = str(k)
                if del_old_layers:
                    tools_qgis.remove_layer_from_toc(aux_layer_name, group)
                v_layer = QgsVectorLayer(f"{geometry_type}?crs=epsg:{srid}", aux_layer_name, 'memory')
                # This function already works with GeoJson
                fill_layer_temp(v_layer, data, k, counter, group=group, sort_val=i)

                # Increase iterator
                i = i + 1

                qml_path = data[k].get('qmlPath')
                category_field = data[k].get('category_field')
                if qml_path:
                    tools_qgis.load_qml(v_layer, qml_path)
                elif category_field:
                    cat_field = data[k]['category_field']
                    size = data[k].get('size', default=2)
                    color_values = {'NEW': QColor(0, 255, 0), 'DUPLICATED': QColor(255, 0, 0),
                                    'EXISTS': QColor(240, 150, 0)}
                    tools_qgis.set_layer_categoryze(v_layer, cat_field, size, color_values)
                else:
                    if geometry_type == 'Point':
                        v_layer.renderer().symbol().setSize(3.5)
                        v_layer.renderer().symbol().setColor(QColor("red"))
                    elif geometry_type == 'LineString':
                        v_layer.renderer().symbol().setWidth(1.5)
                        v_layer.renderer().symbol().setColor(QColor("red"))
                    v_layer.renderer().symbol().setOpacity(0.7)
                temp_layers_added.append(v_layer)
                global_vars.iface.layerTreeView().refreshLayerSymbology(v_layer.id())

    return {'text_result': text_result, 'temp_layers_added': temp_layers_added}


def load_gpkg(gpkg_file) -> dict:
    """ Loads all layers from the GPKG file into a dictionary """

    from osgeo import ogr

    layers = {}
    gpkg = ogr.Open(gpkg_file)

    for l in gpkg:
        layer = QgsVectorLayer(f"{gpkg_file}|layername={l.GetName()}", l.GetName(), 'ogr')
        if layer.isValid():
            layers[l.GetName()] = layer

    return layers


def config_layer_attributes(json_result, layer, layer_name, thread=None):

    for field in json_result['body']['data']['fields']:
        valuemap_values = {}

        # Get column index
        field_index = layer.fields().indexFromName(field['columnname'])

        # Hide selected fields according table config_form_fields.hidden
        if 'hidden' in field:
            config = layer.attributeTableConfig()
            columns = config.columns()
            for column in columns:
                if column.name == str(field['columnname']):
                    column.hidden = field['hidden']
                    break
            config.setColumns(columns)
            layer.setAttributeTableConfig(config)

        # Set alias column
        if field['label']:
            layer.setFieldAlias(field_index, field['label'])

        # widgetcontrols
        widgetcontrols = field.get('widgetcontrols')
        if type(widgetcontrols) == str:
            widgetcontrols = json.loads(widgetcontrols)

        if widgetcontrols:
            if widgetcontrols.get('setQgisConstraints') is True:
                layer.setFieldConstraint(field_index, QgsFieldConstraints.ConstraintNotNull,
                                         QgsFieldConstraints.ConstraintStrengthSoft)
                layer.setFieldConstraint(field_index, QgsFieldConstraints.ConstraintUnique,
                                         QgsFieldConstraints.ConstraintStrengthHard)

        if field.get('ismandatory') is True:
            layer.setFieldConstraint(field_index, QgsFieldConstraints.ConstraintNotNull,
                                     QgsFieldConstraints.ConstraintStrengthHard)
        else:
            layer.setFieldConstraint(field_index, QgsFieldConstraints.ConstraintNotNull,
                                     QgsFieldConstraints.ConstraintStrengthSoft)

        # Manage editability
        # Get layer config
        config = layer.editFormConfig()
        try:
            # Set field editability
            config.setReadOnly(field_index, not field['iseditable'])
        except KeyError:
            pass
        finally:
            # Set layer config
            layer.setEditFormConfig(config)

        # delete old values on ValueMap
        editor_widget_setup = QgsEditorWidgetSetup('ValueMap', {'map': valuemap_values})
        layer.setEditorWidgetSetup(field_index, editor_widget_setup)

        # Manage ValueRelation configuration
        use_vr = widgetcontrols and widgetcontrols.get('valueRelation')
        if use_vr:
            value_relation = widgetcontrols['valueRelation']
            if value_relation.get('activated'):
                try:
                    vr_layer = value_relation['layer']
                    vr_layer = tools_qgis.get_layer_by_tablename(vr_layer).id()  # Get layer id
                    vr_key_column = value_relation['keyColumn']  # Get 'Key'
                    vr_value_column = value_relation['valueColumn']  # Get 'Value'
                    vr_allow_nullvalue = value_relation['nullValue']  # Get null values
                    vr_filter_expression = value_relation['filterExpression']  # Get 'FilterExpression'
                    if vr_filter_expression is None:
                        vr_filter_expression = ''

                    # Create and apply ValueRelation config
                    editor_widget_setup = QgsEditorWidgetSetup('ValueRelation', {'Layer': f'{vr_layer}',
                                                                                 'Key': f'{vr_key_column}',
                                                                                 'Value': f'{vr_value_column}',
                                                                                 'AllowNull': f'{vr_allow_nullvalue}',
                                                                                 'FilterExpression': f'{vr_filter_expression}'})
                    layer.setEditorWidgetSetup(field_index, editor_widget_setup)

                except Exception as e:
                    if thread:
                        thread.exception = e
                        thread.vr_errors.add(layer_name)
                        if 'layer' in value_relation:
                            thread.vr_missing.add(value_relation['layer'])
                        thread.message = f"ValueRelation for {thread.vr_errors} switched to ValueMap because " \
                                         f"layers {thread.vr_missing} are not present on QGIS project"
                    use_vr = False

        if not use_vr:
            # Manage new values in ValueMap
            if field['widgettype'] == 'combo':
                if 'comboIds' in field:
                    # Set values
                    for i in range(0, len(field['comboIds'])):
                        valuemap_values[field['comboNames'][i]] = field['comboIds'][i]
                # Set values into valueMap
                editor_widget_setup = QgsEditorWidgetSetup('ValueMap', {'map': valuemap_values})
                layer.setEditorWidgetSetup(field_index, editor_widget_setup)
            elif field['widgettype'] == 'check':
                config = {'CheckedState': 'true', 'UncheckedState': 'false'}
                editor_widget_setup = QgsEditorWidgetSetup('CheckBox', config)
                layer.setEditorWidgetSetup(field_index, editor_widget_setup)
            elif field['widgettype'] == 'datetime':
                config = {'allow_null': True,
                          'calendar_popup': True,
                          'display_format': 'yyyy-MM-dd',
                          'field_format': 'yyyy-MM-dd',
                          'field_iso_format': False}
                editor_widget_setup = QgsEditorWidgetSetup('DateTime', config)
                layer.setEditorWidgetSetup(field_index, editor_widget_setup)
            elif field['widgettype'] == 'textarea':
                editor_widget_setup = QgsEditorWidgetSetup('TextEdit', {'IsMultiline': 'True'})
                layer.setEditorWidgetSetup(field_index, editor_widget_setup)
            else:
                editor_widget_setup = QgsEditorWidgetSetup('TextEdit', {'IsMultiline': 'False'})
                layer.setEditorWidgetSetup(field_index, editor_widget_setup)

        # multiline: key comes from widgecontrols, but it's used here in order to set false when key is missing
        if field['widgettype'] == 'text':
            if widgetcontrols and 'setMultiline' in widgetcontrols:
                editor_widget_setup = QgsEditorWidgetSetup('TextEdit',
                                                           {'IsMultiline': widgetcontrols['setMultiline']})
            else:
                editor_widget_setup = QgsEditorWidgetSetup('TextEdit', {'IsMultiline': False})
            layer.setEditorWidgetSetup(field_index, editor_widget_setup)

        if field['widgettype'] == 'hidden':
            editor_widget_setup = QgsEditorWidgetSetup('Hidden', {})
            layer.setEditorWidgetSetup(field_index, editor_widget_setup)


def fill_tab_log(dialog, data, force_tab=True, reset_text=True, tab_idx=1, call_set_tabs_enabled=True, close=True):
    """
    Populate txt_infolog QTextEdit widget
        :param dialog: QDialog
        :param data: Json
        :param force_tab: Force show tab (bool)
        :param reset_text: Reset(or not) text for each iteration (bool)
        :param tab_idx: index of tab to force (int)
        :param call_set_tabs_enabled: set all tabs, except the last, enabled or disabled (bool)
        :param close: Manage buttons accept, cancel, close... (bool)
        :return: Text received from data (String)
    """

    change_tab = False
    text = tools_qt.get_text(dialog, dialog.txt_infolog, return_string_null=False)

    if reset_text:
        text = ""
    if 'info' in data and 'values' in data['info']:
        for item in data['info']['values']:
            if 'message' in item:
                if item['message'] is not None:
                    text += str(item['message']) + "\n"
                    if force_tab:
                        change_tab = True
                else:
                    text += "\n"

    tools_qt.set_widget_text(dialog, 'txt_infolog', text + "\n")
    qtabwidget = dialog.findChild(QTabWidget, 'mainTab')
    if qtabwidget is not None:
        qtabwidget.setTabEnabled(qtabwidget.count() - 1, True)
        if change_tab and qtabwidget is not None:
            qtabwidget.setCurrentIndex(tab_idx)
        if call_set_tabs_enabled:
            set_tabs_enabled(dialog)
    if close:
        try:
            dialog.btn_accept.disconnect()
            dialog.btn_accept.hide()
        except AttributeError:
            pass

        try:
            if hasattr(dialog, 'btn_cancel'):
                dialog.btn_cancel.disconnect()
                dialog.btn_cancel.setText("Close")
                dialog.btn_cancel.clicked.connect(lambda: dialog.close())
            if hasattr(dialog, 'btn_close'):
                dialog.btn_close.disconnect()
                dialog.btn_close.setText("Close")
                dialog.btn_close.clicked.connect(lambda: dialog.close())
        except AttributeError:
            # Control if btn_cancel exist
            pass

    return text, change_tab


def disable_tab_log(dialog):

    qtabwidget = dialog.findChild(QTabWidget, 'mainTab')
    if qtabwidget and qtabwidget.widget(qtabwidget.count() - 1).objectName() in ('tab_info', 'tab_infolog', 'tab_loginfo', 'tab_info_log'):
        qtabwidget.setTabEnabled(qtabwidget.count() - 1, False)


def fill_layer_temp(virtual_layer, data, layer_type, counter, group='GW Temporal Layers', sort_val=None):
    """
    :param virtual_layer: Memory QgsVectorLayer (QgsVectorLayer)
    :param data: Json
    :param layer_type: point, line, polygon...(String)
    :param counter: control if json have values (int)
    :param group: group to which we want to add the layer (string)
    :return:
    """

    prov = virtual_layer.dataProvider()
    # Enter editing mode
    virtual_layer.startEditing()

    # Add headers to layer
    if counter > 0:
        for key, value in list(data[layer_type]['features'][0]['properties'].items()):
            if key == 'the_geom':
                continue
            prov.addAttributes([QgsField(str(key), QVariant.String)])

    for feature in data[layer_type]['features']:
        geometry = tools_qgis.get_geometry_from_json(feature)
        if not geometry:
            continue
        attributes = []
        fet = QgsFeature()
        fet.setGeometry(geometry)
        for key, value in feature['properties'].items():
            if key == 'the_geom':
                continue
            attributes.append(value)

        fet.setAttributes(attributes)
        prov.addFeatures([fet])

    # Commit changes
    virtual_layer.commitChanges()
    QgsProject.instance().addMapLayer(virtual_layer, False)
    root = QgsProject.instance().layerTreeRoot()
    my_group = root.findGroup(group)
    if my_group is None:
        my_group = root.insertGroup(0, group)
    my_group.insertLayer(sort_val, virtual_layer)


def set_stylesheet(field, widget, wtype='label'):

    if field.get('stylesheet') is not None:
        if wtype in field['stylesheet']:
            widget.setStyleSheet("QWidget{" + field['stylesheet'][wtype] + "}")
    return widget


def delete_selected_rows(widget, table_object):
    """ Delete selected objects of the table (by object_id) """

    # Get selected rows
    selected_list = widget.selectionModel().selectedRows()
    if len(selected_list) == 0:
        msg = "Any record selected"
        tools_qgis.show_warning(msg)
        return

    inf_text = ""
    list_id = ""
    field_object_id = "id"

    if table_object == "v_edit_element":
        field_object_id = "element_id"
    elif "v_ui_om_visitman_x_" in table_object:
        field_object_id = "visit_id"

    for i in range(0, len(selected_list)):
        row = selected_list[i].row()
        id_ = widget.model().record(row).value(str(field_object_id))
        inf_text += f"{id_}, "
        list_id += f"'{id_}', "
    inf_text = inf_text[:-2]
    list_id = list_id[:-2]
    msg = "Are you sure you want to delete these records?"
    title = "Delete records"
    answer = tools_qt.show_question(msg, title, inf_text)
    if answer:
        sql = (f"DELETE FROM {table_object} "
               f"WHERE {field_object_id} IN ({list_id})")
        tools_db.execute_sql(sql)
        widget.model().select()


def set_tabs_enabled(dialog):
    """ Disable all tabs in the dialog except the log one and change the state of the buttons
    :param dialog: Dialog where tabs are disabled (QDialog)
    :return:
    """

    qtabwidget = dialog.findChild(QTabWidget, 'mainTab')
    for x in range(0, qtabwidget.count() - 1):
        qtabwidget.widget(x).setEnabled(False)
    qtabwidget.setTabEnabled(qtabwidget.count()-1, True)

    btn_accept = dialog.findChild(QPushButton, 'btn_accept')
    if btn_accept:
        btn_accept.hide()

    btn_cancel = dialog.findChild(QPushButton, 'btn_cancel')
    if btn_cancel:
        msg = "Close"
        tools_qt.set_widget_text(dialog, btn_accept, msg)


def set_style_mapzones():
    """ Puts the received styles, in the received layers in the json sent by the gw_fct_getstylemapzones function """

    extras = '"mapzones":""'
    body = create_body(extras=extras)
    json_return = execute_procedure('gw_fct_getstylemapzones', body)
    if not json_return or json_return['status'] == 'Failed':
        return False

    for mapzone in json_return['body']['data']['mapzones']:

        # Loop for each mapzone returned on json
        lyr = tools_qgis.get_layer_by_tablename(mapzone['layer'])
        categories = []
        status = mapzone['status']
        if status == 'Disable':
            continue

        if lyr:
            # Loop for each id returned on json
            for id in mapzone['values']:
                # initialize the default symbol for this geometry type
                symbol = QgsSymbol.defaultSymbol(lyr.geometryType())
                try:
                    symbol.setOpacity(float(mapzone['transparency']))
                except KeyError:  # backwards compatibility for database < 3.5.030
                    symbol.setOpacity(float(mapzone['opacity']))

                # Setting simp
                R = random.randint(0, 255)
                G = random.randint(0, 255)
                B = random.randint(0, 255)
                if status == 'Stylesheet':
                    try:
                        R = id['stylesheet']['color'][0]
                        G = id['stylesheet']['color'][1]
                        B = id['stylesheet']['color'][2]
                    except (TypeError, KeyError):
                        R = random.randint(0, 255)
                        G = random.randint(0, 255)
                        B = random.randint(0, 255)

                elif status == 'Random':
                    R = random.randint(0, 255)
                    G = random.randint(0, 255)
                    B = random.randint(0, 255)

                # Setting sytle
                layer_style = {'color': '{}, {}, {}'.format(int(R), int(G), int(B))}
                symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)

                if symbol_layer is not None:
                    symbol.changeSymbolLayer(0, symbol_layer)
                category = QgsRendererCategory(id['id'], symbol, str(id['id']))
                categories.append(category)

                # apply symbol to layer renderer
                lyr.setRenderer(QgsCategorizedSymbolRenderer(mapzone['idname'], categories))

                # repaint layer
                lyr.triggerRepaint()


def build_dialog_options(dialog, row, pos, _json, temp_layers_added=None, module=sys.modules[__name__]):

    try:
        fields = row[pos]
    except:
        fields = row

    field_id = ''
    if 'fields' in fields:
        field_id = 'fields'
    elif fields.get('return_type') not in ('', None):
        field_id = 'return_type'

    if field_id == '':
        return

    if fields[field_id] is not None:
        for field in fields[field_id]:

            check_parameters(field)

            if field['layoutname'] is None or field['layoutorder'] is None:
                continue

            if field['label']:
                lbl = QLabel()
                lbl.setObjectName('lbl' + field['widgetname'])
                lbl.setText(field['label'])
                lbl.setMinimumSize(160, 0)
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                if 'tooltip' in field:
                    lbl.setToolTip(field['tooltip'])

                widget = None
                if field['widgettype'] == 'text' or field['widgettype'] == 'linetext':
                    widget = QLineEdit()
                    if 'isMandatory' in field:
                        widget.setProperty('ismandatory', field['isMandatory'])
                    else:
                        widget.setProperty('ismandatory', False)
                    if 'value' in field:
                        widget.setText(field['value'])
                        widget.setProperty('value', field['value'])
                    widgetcontrols = field.get('widgetcontrols')
                    if widgetcontrols and widgetcontrols.get('regexpControl') is not None:
                        pass
                    widget.editingFinished.connect(partial(get_dialog_changed_values, dialog, None, widget, field, _json))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    datatype = field.get('datatype')
                    if datatype == 'int':
                        widget.setValidator(QIntValidator())
                    elif datatype == 'float':
                        widget.setValidator(QDoubleValidator())
                elif field['widgettype'] == 'combo':
                    widget = add_combo(field)
                    widget.currentIndexChanged.connect(partial(get_dialog_changed_values, dialog, None, widget, field, _json))
                    signal = field.get('signal')
                    if signal:
                        widget.currentIndexChanged.connect(partial(getattr(module, signal), dialog))
                        getattr(module, signal)(dialog)
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'check':
                    widget = QCheckBox()
                    if field['value'] is not None and field['value'].lower() == "true":
                        widget.setChecked(True)
                    else:
                        widget.setChecked(False)
                    widget.stateChanged.connect(partial(get_dialog_changed_values, dialog, None, widget, field, _json))
                    widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                elif field['widgettype'] == 'datetime':
                    widget = QgsDateTimeEdit()
                    widget.setAllowNull(True)
                    widget.setCalendarPopup(True)
                    widget.setDisplayFormat('yyyy/MM/dd')
                    if global_vars.date_format in ("dd/MM/yyyy", "dd-MM-yyyy", "yyyy/MM/dd", "yyyy-MM-dd"):
                        widget.setDisplayFormat(global_vars.date_format)
                    widget.clear()
                    if field.get('value') not in ('', None, 'null'):
                        date = QDate.fromString(field['value'].replace('/', '-'), 'yyyy-MM-dd')
                        widget.setDate(date)
                    widget.valueChanged.connect(partial(get_dialog_changed_values, dialog, None, widget, field, _json))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'spinbox':
                    widget = QDoubleSpinBox()
                    widgetcontrols = field.get('widgetcontrols')
                    if widgetcontrols:
                        spinboxDecimals = widgetcontrols.get('spinboxDecimals')
                        if spinboxDecimals is not None:
                            widget.setDecimals(spinboxDecimals)
                        maximumNumber = widgetcontrols.get('maximumNumber')
                        if maximumNumber is not None:
                            widget.setMaximum(maximumNumber)
                    if field.get('value') not in (None, ""):
                        value = float(str(field['value']))
                        widget.setValue(value)
                    widget.valueChanged.connect(partial(get_dialog_changed_values, dialog, None, widget, field, _json))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'button':
                    kwargs = {"dialog": dialog, "field": field, "temp_layers_added": temp_layers_added}
                    widget = add_button(**kwargs)
                    widget = set_widget_size(widget, field)

                if widget is None:
                    continue

                # Set editable/readonly
                iseditable = field.get('iseditable')
                if type(widget) in (QLineEdit, QDoubleSpinBox):
                    if iseditable in (False, "False"):
                        widget.setReadOnly(True)
                        widget.setStyleSheet("QWidget {background: rgb(242, 242, 242);color: rgb(100, 100, 100)}")
                    if type(widget) == QLineEdit:
                        if 'placeholder' in field:
                            widget.setPlaceholderText(field['placeholder'])
                elif type(widget) in (QComboBox, QCheckBox):
                    if iseditable in (False, "False"):
                        widget.setEnabled(False)
                widget.setObjectName(field['widgetname'])
                if iseditable is not None:
                    widget.setEnabled(bool(iseditable))

                add_widget(dialog, field, lbl, widget)


def check_parameters(field):
    """ Check that all the parameters necessary to mount the form are correct """

    msg = ""
    if 'widgettype' not in field:
        msg += f"{tools_qt.tr('Widgettype not found.')} "

    if 'widgetname' not in field:
        msg += f"{tools_qt.tr('Widgetname not found.')} "

    if field.get('widgettype') not in ('text', 'linetext', 'combo', 'check', 'datetime', 'spinbox', 'button', 'tab'):
        msg += (f"{tools_qt.tr('Widgettype is wrongly configured. Needs to be in ')}"
                "('text', 'linetext', 'combo', 'check', 'datetime', 'spinbox', 'button', 'tab')")

    if 'layoutorder' not in field:
        msg += f"{tools_qt.tr('layoutorder not found.')} "

    if msg != "":
        tools_qgis.show_warning(msg)


def add_widget(dialog, field, lbl, widget):
    """ Insert widget into layout """

    layout = dialog.findChild(QGridLayout, field['layoutname'])
    if layout in (None, 'null', 'NULL', 'Null'):
        return
    row = int(field['layoutorder'])
    col = 0
    if lbl is None:
        col = row
        row = 0
    elif not isinstance(widget, QTableView):
        layout.addWidget(lbl, row, col)
        col = 1
    if type(widget) is QSpacerItem:
        layout.addItem(widget, row, col)
    else:
        layout.addWidget(widget, row, col)
    if lbl is not None:
        layout.setColumnStretch(col, 1)


def get_dialog_changed_values(dialog, chk, widget, field, list, value=None):

    elem = {}
    if type(widget) is QLineEdit:
        value = tools_qt.get_text(dialog, widget, return_string_null=False)
    elif type(widget) is QComboBox:
        value = tools_qt.get_combo_value(dialog, widget, 0)
    elif type(widget) is QCheckBox:
        value = tools_qt.is_checked(dialog, widget)
    elif type(widget) is QDateEdit:
        value = tools_qt.get_calendar_date(dialog, widget)

    # When the QDoubleSpinbox contains decimals, for example 2,0001 when collecting the value, the spinbox itself sends
    # 2.0000999999, as in reality we only want, maximum 4 decimal places, we round up, thus fixing this small failure
    # of the widget
    if type(widget) in (QSpinBox, QDoubleSpinBox):
        value = round(value, 4)

    elem['widget'] = str(widget.objectName())
    elem['value'] = value
    if chk is not None:
        if chk.isChecked():
            elem['chk'] = str(chk.objectName())
            elem['isChecked'] = str(tools_qt.is_checked(dialog, chk))

    if 'sys_role_id' in field:
        elem['sys_role_id'] = str(field['sys_role_id'])

    # Search for the widget and remove it if it's in the list
    idx_del = None
    for i in range(len(list)):
        if list[i]['widget'] == elem['widget']:
            idx_del = i
            break
    if idx_del is not None:
        list.pop(idx_del)

    list.append(elem)


def add_button(**kwargs):
    """
    :param dialog: (QDialog)
    :param field: Part of json where find info (Json)
    :param temp_layers_added: List of layers added to the toc
    :param module: Module where find 'function_name', if 'function_name' is not in this module
    :return: (QWidget)
    functions called in -> widget.clicked.connect(partial(getattr(module, function_name), **kwargs)) atm:
        module = tools_backend_calls -> def add_object(**kwargs)
        module = tools_backend_calls -> def delete_object(**kwargs):
        module = tools_backend_calls -> def manage_document(doc_id, **kwargs):
        module = tools_backend_calls -> def manage_element(element_id, **kwargs):
        module = tools_backend_calls -> def open_selected_element(**kwargs):
    """

    field = kwargs['field']
    module = tools_backend_calls
    widget = QPushButton()
    widget.setObjectName(field['widgetname'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    if 'value' in field:
        txt = field['value']
        if field.get('valueLabel'):
            txt = field.get('valueLabel')
        widget.setText(txt)
        widget.setProperty('value', field['value'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
        txt = field['widgetcontrols'].get('text')
        if txt:
            widget.setText(txt)
    if 'tooltip' in field:
        widget.setToolTip(field['tooltip'])

    widget.resize(widget.sizeHint().width(), widget.sizeHint().height())
    function_name = None
    real_name = widget.objectName()
    if 'data_' in widget.objectName():
        real_name = widget.objectName()[5:len(widget.objectName())]

    if field['stylesheet'] is not None and 'icon' in field['stylesheet']:
        icon = field['stylesheet']['icon']
        size = field['stylesheet']['size'] if 'size' in field['stylesheet'] else "20x20"
        add_icon(widget, f'{icon}', size)

    if 'widgetfunction' in field:
        if 'module' in field['widgetfunction']:
            module = globals()[field['widgetfunction']['module']]
        function_name = field['widgetfunction'].get('functionName')
        if function_name is not None:
            if function_name:
                exist = tools_os.check_python_function(module, function_name)
                if not exist:
                    msg = "widget {0} has associated function {1}, but {1} not exist"
                    msg_params = (real_name, function_name,)
                    tools_qgis.show_message(msg, 2, msg_params=msg_params)
                    return widget
            else:
                msg = "Parameter functionName is null for button"
                tools_qgis.show_message(msg, 2, parameter=widget.objectName())

    func_params = ""
    if 'widgetfunction' in field and field['widgetfunction'] and 'functionName' in field['widgetfunction']:
        function_name = field['widgetfunction']['functionName']
        exist = tools_os.check_python_function(module, function_name)
        if not exist:
            msg = "widget {0} has associated function {1}, but {1} not exist"
            msg_params = (real_name, function_name,)
            tools_qgis.show_message(msg, 2, msg_params=msg_params)
            return widget
        if 'parameters' in field['widgetfunction']:
            func_params = field['widgetfunction']['parameters']
    else:
        msg = "Parameter {0} is null for button"
        msg_params = ("widgetfunction.functionName",)
        tools_qgis.show_message(msg, 2, parameter=widget.objectName())
        return widget

    kwargs['widget'] = widget
    kwargs['message_level'] = 1
    kwargs['function_name'] = function_name
    kwargs['func_params'] = func_params
    if function_name:
        widget.clicked.connect(partial(getattr(module, function_name), **kwargs))

    return widget


def add_spinbox(**kwargs):

    field = kwargs['field']
    module = tools_backend_calls
    widget = None
    if field['widgettype'] == 'spinbox':
        widget = QSpinBox()
    elif field['widgettype'] == 'doubleSpinbox':
        widget = QDoubleSpinBox()
        if field.get('widgetcontrols') and 'spinboxDecimals' in field['widgetcontrols']:
            widget.setDecimals(field['widgetcontrols']['spinboxDecimals'])

    if 'min' in field['widgetcontrols']['maxMinValues']:
        widget.setMinimum(field['widgetcontrols']['maxMinValues']['min'])
    if 'max' in field['widgetcontrols']['maxMinValues']:
        widget.setMaximum(field['widgetcontrols']['maxMinValues']['max'])

    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    if 'value' in field:
        if field['widgettype'] == 'spinbox' and field['value'] != "":
            widget.setValue(int(field['value']))
        elif field['widgettype'] == 'doubleSpinbox' and field['value'] != "":
            widget.setValue(float(field['value']))
    if 'iseditable' in field:
        widget.setReadOnly(not field['iseditable'])
        if not field['iseditable']:
            widget.setStyleSheet("QDoubleSpinBox { background: rgb(0, 250, 0); color: rgb(100, 100, 100)}")

    return widget


def get_values(dialog, widget, _json=None, ignore_editability=False):

    value = None

    if type(widget) in (QDoubleSpinBox, QLineEdit, QSpinBox, QTextEdit, DrHyperLinkLineEdit):
        if widget.isReadOnly() and not ignore_editability:
            return _json
        value = tools_qt.get_text(dialog, widget, return_string_null=False)
    elif type(widget) is QComboBox:
        if not widget.isEnabled() and not ignore_editability:
            return _json
        value = tools_qt.get_combo_value(dialog, widget, 0)
    elif type(widget) is QCheckBox:
        if not widget.isEnabled() and not ignore_editability:
            return _json
        value = tools_qt.is_checked(dialog, widget)
        if value is not None:
            value = str(value).lower()
    elif type(widget) is QgsDateTimeEdit:
        if not widget.isEnabled() and not ignore_editability:
            return _json
        value = tools_qt.get_calendar_date(dialog, widget)

    key = str(widget.property('columnname')) if widget.property('columnname') else widget.objectName()
    if key == '' or key is None:
        return _json

    if _json is None:
        _json = {}

    if str(value) == '' or value is None:
        _json[key] = None
    else:
        _json[key] = str(value)
    return _json


def add_checkbox(**kwargs):

    dialog = kwargs.get('dialog')
    field = kwargs.get('field')
    is_tristate = kwargs.get('is_tristate')
    class_info = kwargs.get('class')
    connect_signal = kwargs.get('connectsignal')

    widget = QCheckBox()
    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    widget.setProperty('columnname', field['columnname'])
    if field.get('value') in ("t", "true", True):
        widget.setChecked(True)
    if is_tristate:
        widget.setTristate(is_tristate)
        if field.get('value') == "":
            widget.setCheckState(1)
    if 'iseditable' in field:
        widget.setEnabled(field['iseditable'])

    if connect_signal is not None and connect_signal is False:
        return widget

    if 'widgetfunction' in field:
        if 'module' in field['widgetfunction']:
            module = globals()[field['widgetfunction']['module']]
        function_name = field['widgetfunction'].get('functionName')
        if function_name is not None:
            if function_name:
                exist = tools_os.check_python_function(module, function_name)
                if not exist:
                    msg = "Widget {0} has associated function {1}, but {1} not exist"
                    msg_params = (field['widgetname'], function_name,)
                    tools_qgis.show_message(msg, 2, msg_params=msg_params)
                    return widget
            else:
                msg = "Parameter {0} is null for check"
                msg_params = ("functionName",)
                tools_qgis.show_message(msg, 2, parameter=widget.objectName())

    func_params = ""

    if 'widgetfunction' in field and field['widgetfunction'] and 'functionName' in field['widgetfunction']:
        function_name = field['widgetfunction']['functionName']

        exist = tools_os.check_python_function(module, function_name)
        if not exist:
            msg = "Widget {0} has associated function {1}, but {1} not exist"
            msg_params = (field['widgetname'], function_name,)
            tools_qgis.show_message(msg, 2, msg_params=msg_params)
            return widget
        if 'parameters' in field['widgetfunction']:
            func_params = field['widgetfunction']['parameters']
    else:
        return widget

    kwargs['widget'] = widget
    kwargs['message_level'] = 1
    kwargs['function_name'] = function_name
    kwargs['func_params'] = func_params
    if function_name:
        widget.stateChanged.connect(partial(getattr(module, function_name), **kwargs))
    else:
        widget.stateChanged.connect(partial(get_values, dialog, widget, class_info.my_json))
    return widget


def add_textarea(field):
    """ Add widgets QTextEdit type """

    widget = QTextEdit()
    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    if 'value' in field:
        widget.setText(field['value'])
        widget.setProperty('value', field['value'])

    # Set height as a function of text lines
    font = widget.document().defaultFont()
    fm = QFontMetrics(font)
    text_size = fm.size(0, widget.toPlainText())
    if text_size.height() < 26:
        widget.setMinimumHeight(36)
        widget.setMaximumHeight(36)
    else:
        # Need to modify to avoid scroll
        widget.setMaximumHeight(text_size.height() + 10)

    if 'iseditable' in field:
        widget.setReadOnly(not field['iseditable'])
        if not field['iseditable']:
            widget.setStyleSheet("QLineEdit { background: rgb(242, 242, 242); color: rgb(100, 100, 100)}")

    return widget


def add_hyperlink(field):
    """
    functions called in -> widget.clicked.connect(partial(getattr(tools_backend_calls, func_name), widget))
        module = tools_backend_calls -> def open_url(self, widget)

    """

    is_editable = field.get('iseditable')
    if is_editable:
        widget = DrHyperLinkLineEdit()
    else:
        widget = DrHyperLinkLabel()
    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    if 'value' in field:
        widget.setText(field['value'])
        widget.setProperty('value', field['value'])
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    widget.resize(widget.sizeHint().width(), widget.sizeHint().height())
    func_name = None
    real_name = widget.objectName()
    if 'data_' in widget.objectName():
        real_name = widget.objectName()[5:len(widget.objectName())]
    if 'widgetfunction' in field:
        func_name = field['widgetfunction'].get('functionName')
        if func_name is not None:
            if func_name:
                exist = tools_os.check_python_function(tools_backend_calls, func_name)
                if not exist:
                    msg = f"widget {real_name} have associated function {func_name}, but {func_name} not exist"
                    tools_qgis.show_message(msg, 2)
                    return widget
            else:
                msg = "Parameter {0} is null for widget hyperlink"
                msg_params = ("widgetfunction",)
                tools_qgis.show_message(msg, 2, parameter=real_name)
        else:
            tools_log.log_info(field['widgetfunction'])
    else:
        msg = "Parameter {0} not found for widget type hyperlink"
        msg_params = ("widgetfunction",)
        tools_qgis.show_message(msg, 2, parameter=real_name)

    if func_name is not None:
        # Call function-->func_name(widget) or def no_function_associated(self, widget=None, message_level=1)
        widget.clicked.connect(partial(getattr(tools_backend_calls, func_name), widget))

    return widget


def add_calendar(dlg, fld, **kwargs):

    module = tools_backend_calls
    widget = QgsDateTimeEdit()
    widget.setObjectName(fld['widgetname'])
    if 'widgetcontrols' in fld and fld['widgetcontrols']:
        widget.setProperty('widgetcontrols', fld['widgetcontrols'])
    if 'columnname' in fld:
        widget.setProperty('columnname', fld['columnname'])
    widget.setAllowNull(True)
    widget.setCalendarPopup(True)
    widget.setDisplayFormat('dd/MM/yyyy')
    if fld.get('value') not in ('', None, 'null'):
        date = QDate.fromString(fld['value'].replace('/', '-'), 'yyyy-MM-dd')
        tools_qt.set_calendar(dlg, widget, date)
    else:
        widget.clear()

    real_name = widget.objectName()

    function_name = None
    func_params = ""
    if 'widgetfunction' in fld:
        if 'module' in fld['widgetfunction']:
            module = globals()[fld['widgetfunction']['module']]
        if 'functionName' in fld['widgetfunction']:
            if fld['widgetfunction']['functionName']:
                function_name = fld['widgetfunction']['functionName']
                exist = tools_os.check_python_function(module, function_name)
                if not exist:
                    msg = "Widget {0} have associated function {1}, but {1} not exist"
                    msg_params = (real_name, function_name,)
                    tools_qgis.show_message(msg, 2, msg_params=msg_params)
                    return widget
                if 'parameters' in fld['widgetfunction']:
                    func_params = fld['widgetfunction']['parameters']
            else:
                msg = "Parameter {0} is null for button"
                msg_params = ("button_function",)
                tools_qgis.show_message(msg, 2, parameter=widget.objectName())

    kwargs['widget'] = widget
    kwargs['message_level'] = 1
    kwargs['function_name'] = function_name
    kwargs['func_params'] = func_params
    # if function_name:
    #     widget.dateChanged.connect(partial(getattr(module, function_name), **kwargs))

    btn_calendar = widget.findChild(QToolButton)
    btn_calendar.clicked.connect(partial(tools_qt.set_calendar_empty, widget))

    return widget


def set_typeahead(field, dialog, widget, completer, feature_id=None):

    if field['widgettype'] == 'typeahead':
        if 'queryText' not in field or 'queryTextFilter' not in field:
            return widget
        widget.setProperty('typeahead', True)
        model = QStringListModel()
        widget.textChanged.connect(partial(fill_typeahead, completer, model, field, dialog, widget, feature_id))

    return widget


def fill_typeahead(completer, model, field, dialog, widget, feature_id=None):
    """ Set autocomplete of widget @table_object + "_id"
        getting id's from selected @table_object.
        WARNING: Each QLineEdit needs their own QCompleter and their own QStringListModel!!!
    """

    if not widget:
        return
    parent_id = ""
    if 'parentId' in field:
        parent_id = field["parentId"]

    # Get parentValue from widget or from feature_id if parentWidget not configured
    if dialog.findChild(QWidget, "data_" + str(parent_id)):
        parent_value = tools_qt.get_text(dialog, "data_" + str(parent_id))
    else:
        parent_value = feature_id

    extras = f'"queryText":"{field["queryText"]}"'
    extras += f', "queryTextFilter":"{field["queryTextFilter"]}"'
    extras += f', "parentId":"{parent_id}"'
    extras += f', "parentValue":"{parent_value}"'
    extras += f', "textToSearch":"{tools_qt.get_text(dialog, widget)}"'
    body = create_body(extras=extras)
    complet_list = execute_procedure('gw_fct_gettypeahead', body)
    if not complet_list or complet_list['status'] == 'Failed':
        return False

    list_items = []
    for field in complet_list['body']['data']:
        list_items.append(field['idval'])
    tools_qt.set_completer_object(completer, model, widget, list_items)


def set_data_type(field, widget):

    widget.setProperty('datatype', field['datatype'])
    return widget


def set_widget_size(widget, field):

    if field.get('widgetcontrols') and field['widgetcontrols'].get('widgetdim'):
        widget.setMaximumWidth(field['widgetcontrols']['widgetdim'])
        widget.setMinimumWidth(field['widgetcontrols']['widgetdim'])

    return widget


def add_lineedit(field):
    """ Add widgets QLineEdit type """

    widget = QLineEdit()
    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    if 'placeholder' in field:
        widget.setPlaceholderText(field['placeholder'])
    if 'value' in field:
        widget.setText(field['value'])
        widget.setProperty('value', field['value'])
    if 'tooltip' in field:
        widget.setToolTip(field['tooltip'])
    if 'iseditable' in field:
        widget.setReadOnly(not field['iseditable'])
        if not field['iseditable']:
            widget.setStyleSheet("QLineEdit { background: rgb(242, 242, 242); color: rgb(100, 100, 100)}")
    if 'value' in field:
        widget.setText(field['value'])
    return widget


def add_tableview(complet_result, field, dialog, module=sys.modules[__name__], class_self=None):
    """
    Add widgets QTableView type.
        Function called in -> widget.doubleClicked.connect(partial(getattr(module, function_name), **kwargs))
            module = tools_backend_calls open_selected_path(**kwargs):
            module = tools_backend_calls open_selected_element(**kwargs):

    """
    widget = QTableView()
    widget.setObjectName(field['widgetname'])
    widget.setSortingEnabled(True)

    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field and field['columnname']:
        widget.setProperty('columnname', field['columnname'])
    if 'linkedobject' in field and field['linkedobject']:
        widget.setProperty('linkedobject', field['linkedobject'])

    function_name = 'no_function_asociated'
    real_name = widget.objectName()
    func_params = ""
    if 'data_' in widget.objectName():
        real_name = widget.objectName()[5:len(widget.objectName())]
    if 'widgetfunction' in field:
        if field['widgetfunction'].get('functionName') is not None:
            function_name = field['widgetfunction']['functionName']
            if 'module' in field['widgetfunction']:
                module = globals()[field['widgetfunction']['module']]
            exist = tools_os.check_python_function(module, function_name)
            if not exist:
                msg = "Widget {0} have associated function {1}, but {1} not exist"
                msg_params = (real_name, function_name,)
                tools_qgis.show_message(msg, 2, msg_params=msg_params)
                return widget
            if 'parameters' in field['widgetfunction']:
                func_params = field['widgetfunction']['parameters']

    # noinspection PyUnresolvedReferences
    if function_name and function_name not in ('', 'None', 'no_function_asociated'):
        kwargs = {"qtable": widget, "func_params": func_params, "complet_result": complet_result, "dialog": dialog, "class": class_self}
        widget.doubleClicked.connect(partial(getattr(module, function_name), **kwargs))

    return widget


def add_combo(field, dialog=None, complet_result=None):

    widget = QComboBox()
    widget.setObjectName(field['widgetname'])
    if 'widgetcontrols' in field and field['widgetcontrols']:
        widget.setProperty('widgetcontrols', field['widgetcontrols'])
    if 'columnname' in field:
        widget.setProperty('columnname', field['columnname'])
    widget = fill_combo(widget, field)
    if 'value' in field:
        tools_qt.set_combo_value(widget, field['value'], 0)
        widget.setProperty('selectedId', field['value'])
    else:
        widget.setProperty('selectedId', None)
    if 'iseditable' in field:
        widget.setEnabled(bool(field['iseditable']))
        if not field['iseditable']:
            widget.setStyleSheet("QComboBox { background: rgb(242, 242, 242); color: rgb(100, 100, 100)}")

    if 'widgetfunction' in field and field['widgetfunction']:
        widgetfunction = field['widgetfunction']
        if isinstance(widgetfunction, list):
            functions = widgetfunction
        else:
            if 'isfilter' in field and field['isfilter']:
                return widget
            functions = [widgetfunction]
        for f in functions:
            if 'isFilter' in f and f['isFilter']: continue
            columnname = field['columnname']
            parameters = f['parameters']

            kwargs = {"complet_result": complet_result, "dialog": dialog, "columnname": columnname, "widget": widget,
                      "func_params": parameters}
            if 'module' in f:
                module = globals()[f['module']]
            else:
                module = tools_backend_calls
            function_name = f.get('functionName')
            if function_name is not None:
                if function_name:
                    exist = tools_os.check_python_function(module, function_name)
                    if not exist:
                        msg = "Widget {0} has associated function {1}, but {1} not exist"
                        msg_params = (widget.property('widgetname'), function_name,)
                        tools_qgis.show_message(msg, 2, msg_params=msg_params)
                        return widget
                else:
                    msg = "Parameter {0} is null for button"
                    msg_params = ("functionName",)
                    tools_qgis.show_message(msg, 2, parameter=widget.objectName())
            widget.currentIndexChanged.connect(partial(getattr(module, function_name), **kwargs))

    return widget


def fill_combo(widget, field):

    # Generate list of items to add into combo

    widget.blockSignals(True)
    widget.clear()
    widget.blockSignals(False)
    combolist = []
    comboIds = []
    comboNames = []

    if field.get('comboIds') and field.get('comboNames'):
        if tools_os.set_boolean(field.get('isNullValue'), False):
            combolist.append(['', ''])
        for record in field['comboIds'].split(','):
            comboIds.append(record)
        for record in field['comboNames'].split(','):
            comboNames.append(record)
        for i in range(0, len(comboIds)):
            elem = [comboIds[i], comboNames[i]]
            combolist.append(elem)
    else:
        msg = f"Found combobox that has no values. HINT: WHERE id='{field['widgetname']}' " \
              f"AND widgettype='{field['widgettype']}'"
        tools_log.log_warning(msg)
    # Populate combo
    for record in combolist:
        widget.addItem(record[1], record)

    return widget


def fill_combo_child(dialog, combo_child):

    if 'widgetname' in combo_child:
        child = dialog.findChild(QComboBox, str(combo_child['widgetname']))
        if child is not None:
            fill_combo(child, combo_child)


def manage_combo_child(dialog, combo_parent, combo_child):

    if 'widgetname' in combo_child:
        child = dialog.findChild(QComboBox, str(combo_child['widgetname']))

        if child:
            child.setEnabled(True)

            fill_combo_child(dialog, combo_child)
            if 'widgetcontrols' not in combo_child or not combo_child['widgetcontrols'] or \
                    'enableWhenParent' not in combo_child['widgetcontrols']:
                return

            combo_value = tools_qt.get_combo_value(dialog, combo_parent, 0)
            if (str(combo_value) in str(combo_child['widgetcontrols']['enableWhenParent'])) \
                    and (combo_value not in (None, '')):
                # The keepDisbled property is used to keep the edition enabled or disabled,
                # when we activate the layer and call the "enable_all" function
                child.setProperty('keepDisbled', False)
                child.setEnabled(True)
            else:
                child.setProperty('keepDisbled', True)
                child.setEnabled(False)


def get_expression_filter(feature_type, list_ids=None, layers=None):
    """ Set an expression filter with the contents of the list.
        Set a model with selected filter. Attach that model to selected table
    """

    list_ids = list_ids[feature_type]
    field_id = feature_type + "_id"
    if len(list_ids) == 0:
        return None

    # Set expression filter with features in the list
    expr_filter = field_id + " IN ("
    for i in range(len(list_ids)):
        expr_filter += f"'{list_ids[i]}', "
    expr_filter = expr_filter[:-2] + ")"

    # Check expression
    (is_valid, expr) = tools_qt.check_expression_filter(expr_filter)
    if not is_valid:
        return None

    # Select features of layers applying @expr
    tools_qgis.select_features_by_ids(feature_type, expr, layers=layers)

    return expr_filter


def get_actions_from_json(json_result, sql):
    """
    Manage options for layers (active, visible, zoom and indexing)
    :param json_result: Json result of a query (Json)
    :param sql: query executed (String)
    :return: None
    """

    try:
        actions = json_result['body']['python_actions']
    except KeyError:
        return
    try:
        for action in actions:
            try:
                function_name = action['funcName']
                params = action['params']
                getattr(tools_backend_calls, f"{function_name}")(**params)
            except AttributeError as e:
                # If function_name not exist as python function
                msg = "Exception error: {0}"
                msg_params = (e,)
                tools_log.log_warning(msg, msg_params=msg_params)
            except Exception as e:
                msg = "{0}: {1}"
                msg_params = (type(e).__name__, e,)
                tools_log.log_debug(msg, msg_params=msg_params)
    except Exception as e:
        tools_qt.manage_exception(None, f"{type(e).__name__}: {e}", sql, global_vars.schema_name)


def execute_procedure(function_name, parameters=None, schema_name=None, commit=True, log_sql=True, rubber_band=None,
        aux_conn=None, is_thread=False, check_function=True):
    """ Manage execution database function
    :param function_name: Name of function to call (text)
    :param parameters: Parameters for function (json) or (query parameters)
    :param commit: Commit sql (bool)
    :param log_sql: Show query in qgis log (bool)
    :param aux_conn: Auxiliar connection to database used by threads (psycopg2.connection)
    :return: Response of the function executed (json)
    """

    # Check if function exists
    if check_function:
        exists = tools_os.check_python_function(tools_fct, function_name)
        if not exists:
            msg = "Function {0} not found in {1}"
            msg_params = (function_name, "tools_fct",)
            tools_qgis.show_warning(msg, parameter=function_name)
            return None

    if type(parameters) is str:
        parameters = json.loads(parameters)
    msg = "{0}.{1}({2})"
    msg_params = ("tools_fct", function_name, parameters,)
    tools_log.log_db(msg, bold='b', msg_params=msg_params)
    json_result = getattr(tools_fct, function_name)(parameters)
    if commit:
        global_vars.gpkg_dao_data.commit()

    # # Get log_sql for developers
    # dev_log_sql = get_config_parser('log', 'log_sql', "user", "init", False)
    # if dev_log_sql in ("True", "False"):
    #     log_sql = tools_os.set_boolean(dev_log_sql)

    header = "SERVER RESPONSE"
    tools_log.log_db(json_result, header=header)

    # All functions called from python should return 'status', if not, something has probably failed in postrgres
    if 'status' not in json_result:
        manage_json_exception(json_result)
        return False

    # If failed, manage exception
    if json_result.get('status') == 'Failed':
        manage_json_exception(json_result, is_thread=is_thread)
        return json_result

    try:
        if json_result["body"]["feature"]["geometry"] and global_vars.data_epsg != global_vars.project_epsg:
            json_result = manage_json_geometry(json_result)
    except Exception:
        pass

    if not is_thread:
        manage_json_response(json_result, rubber_band=rubber_band)

    return json_result


def manage_json_geometry(json_result):

    # Set QgsCoordinateReferenceSystem
    data_epsg = QgsCoordinateReferenceSystem(str(global_vars.data_epsg))
    project_epsg = QgsCoordinateReferenceSystem(str(global_vars.project_epsg))

    tform = QgsCoordinateTransform(data_epsg, project_epsg, QgsProject.instance())

    list_coord = re.search('\((.*)\)', str(json_result['body']['feature']['geometry']['st_astext']))
    points = tools_qgis.get_geometry_vertex(list_coord)

    for point in points:
        if str(global_vars.data_epsg) == '2052' and str(global_vars.project_epsg) == '102566':
            clear_list = list_coord.group(1)
            updated_list = list_coord.group(1).replace('-', '').replace(' ', ' -')
            json_result['body']['feature']['geometry']['st_astext'] = json_result['body']['feature']['geometry']['st_astext'].replace(clear_list, updated_list)
        elif str(global_vars.data_epsg) != str(global_vars.project_epsg):
            new_coords = tform.transform(point)
            json_result['body']['feature']['geometry']['st_astext'] = json_result['body']['feature']['geometry']['st_astext'].replace(str(point.x()), str(new_coords.x()))
            json_result['body']['feature']['geometry']['st_astext'] = json_result['body']['feature']['geometry']['st_astext'].replace(str(point.y()), str(new_coords.y()))

    return json_result


def manage_json_response(complet_result, sql=None, rubber_band=None):

    if complet_result not in (None, False):
        try:
            manage_json_return(complet_result, sql, rubber_band)
            manage_layer_manager(complet_result)
            get_actions_from_json(complet_result, sql)
        except Exception:
            pass


def manage_json_exception(json_result, sql=None, stack_level=2, stack_level_increase=0, is_thread=False):
    """ Manage exception in JSON database queries and show information to the user """

    try:

        if 'message' in json_result:
            level = 1
            if 'level' in json_result['message']:
                level = int(json_result['message']['level'])
            if 'text' in json_result['message']:
                msg = json_result['message']['text']
            else:
                msg = json_result['message']

            # Show exception message only if we are not in a task process
            if len(global_vars.session_vars['threads']) == 0:
                tools_qgis.show_message(msg, level)
            else:
                tools_log.log_info(msg)

        else:

            stack_level += stack_level_increase
            if stack_level >= len(inspect.stack()):
                stack_level = len(inspect.stack()) - 1
            module_path = inspect.stack()[stack_level][1]
            file_name = tools_os.get_relative_path(module_path, 2)
            function_line = inspect.stack()[stack_level][2]
            function_name = inspect.stack()[stack_level][3]

            # Set exception message details
            title = "Database execution failed"
            msg = ""
            msg += f"{tools_qt.tr('File name')}: {file_name}\n"
            msg += f"{tools_qt.tr('Function name')}: {function_name}\n"
            msg += f"{tools_qt.tr('Line number')}: {function_line}\n"
            if 'SQLERR' in json_result:
                msg += f"{tools_qt.tr('Detail')}: {json_result['SQLERR']}\n"
            elif 'NOSQLERR' in json_result:
                msg += f"{tools_qt.tr('Detail')}: {json_result['NOSQLERR']}\n"
            if 'SQLCONTEXT' in json_result:
                msg += f"{tools_qt.tr('Context')}: {json_result['SQLCONTEXT']}\n"
            if sql:
                msg += f"{tools_qt.tr('SQL')}: {sql}\n"
            if 'MSGERR' in json_result:
                msg += f"{tools_qt.tr('Message error')}: {json_result['MSGERR']}"
            global_vars.session_vars['last_error_msg'] = msg

            if is_thread:
                return

            tools_log.log_warning(msg, stack_level_increase=2)
            # Show exception message only if we are not in a task process
            if len(global_vars.session_vars['threads']) == 0:
                tools_qt.show_exception_message(title, msg)

    except Exception:
        tools_qt.manage_exception("Unhandled Error")


def manage_json_return(json_result, sql, rubber_band=None, i=None):
    """
    Manage options for layers (active, visible, zoom and indexing)
    :param json_result: Json result of a query (Json)
    :param sql: query executed (String)
    :return: None
    """

    try:
        return_manager = json_result['body']['returnManager']
    except KeyError:
        return

    srid = global_vars.data_epsg
    try:
        margin = None
        opacity = 100
        i = 0

        if 'zoom' in return_manager and 'margin' in return_manager['zoom']:
            margin = return_manager['zoom']['margin']

        if 'style' in return_manager and 'ruberband' in return_manager['style']:
            width = 3
            color = QColor(255, 0, 0, 125)
            if 'transparency' in return_manager['style']['ruberband']:
                opacity = return_manager['style']['ruberband']['transparency'] * 255
            if 'color' in return_manager['style']['ruberband']:
                color = return_manager['style']['ruberband']['color']
                color = QColor(int(color[0]), int(color[1]), int(color[2]), int(opacity))
            if 'width' in return_manager['style']['ruberband']:
                width = return_manager['style']['ruberband']['width']
            draw_by_json(json_result, rubber_band, margin, color=color, width=width)

        else:

            for key, value in list(json_result['body']['data'].items()):
                if key.lower() in ('point', 'line', 'polygon'):
                    if key not in json_result['body']['data']:
                        continue

                    # Remove the layer if it exists
                    layer_name = f'{key}'
                    if json_result['body']['data'][key].get('layerName'):
                        layer_name = json_result['body']['data'][key]['layerName']
                    tools_qgis.remove_layer_from_toc(layer_name, 'GW Temporal Layers')

                    if 'features' not in json_result['body']['data'][key]:
                        continue
                    if len(json_result['body']['data'][key]['features']) == 0:
                        continue

                    # Get values for create and populate layer
                    counter = len(json_result['body']['data'][key]['features'])
                    geometry_type = json_result['body']['data'][key]['geometryType']
                    v_layer = QgsVectorLayer(f"{geometry_type}?crs=epsg:{srid}", layer_name, 'memory')
                    fill_layer_temp(v_layer, json_result['body']['data'], key, counter, sort_val=i)

                    # Increase iterator
                    i = i+1

                    # Get values for set layer style
                    opacity = 100
                    style_type = json_result['body']['returnManager']['style']

                    if 'style' in return_manager and 'values' in return_manager['style'][key]:
                        if 'transparency' in return_manager['style'][key]['values']:
                            opacity = return_manager['style'][key]['values']['transparency']
                    if style_type[key]['style'] == 'categorized':
                        if 'transparency' in return_manager['style'][key]:
                            opacity = return_manager['style'][key]['transparency']
                        color_values = {}
                        for item in json_result['body']['returnManager']['style'][key].get('values', []):
                            color = QColor(item['color'][0], item['color'][1], item['color'][2], int(opacity * 255))
                            color_values[item['id']] = color
                        cat_field = str(style_type[key]['field'])
                        size = style_type[key]['width'] if style_type[key].get('width') else 2
                        tools_qgis.set_layer_categoryze(v_layer, cat_field, size, color_values)

                    elif style_type[key]['style'] == 'random':
                        size = style_type['width'] if style_type.get('width') else 2
                        if geometry_type == 'Point':
                            v_layer.renderer().symbol().setSize(size)
                        else:
                            v_layer.renderer().symbol().setWidth(size)
                        v_layer.renderer().symbol().setOpacity(opacity)

                    elif style_type[key]['style'] == 'qml':
                        style_id = style_type[key]['id']
                        extras = f'"style_id":"{style_id}"'
                        body = create_body(extras=extras)
                        style = execute_procedure('gw_fct_getstyle', body)
                        if style is None or style.get('status') == 'Failed':
                            return
                        if 'styles' in style['body']:
                            if 'style' in style['body']['styles']:
                                qml = style['body']['styles']['style']
                                tools_qgis.create_qml(v_layer, qml)

                    elif style_type[key]['style'] == 'unique':
                        color = style_type[key]['values']['color']
                        size = style_type['width'] if style_type.get('width') else 2
                        color = QColor(color[0], color[1], color[2])
                        if key == 'point':
                            v_layer.renderer().symbol().setSize(size)
                        elif key in ('line', 'polygon'):
                            v_layer.renderer().symbol().setWidth(size)
                        v_layer.renderer().symbol().setColor(color)
                        v_layer.renderer().symbol().setOpacity(opacity)

                    global_vars.iface.layerTreeView().refreshLayerSymbology(v_layer.id())
                    if margin:
                        tools_qgis.set_margin(v_layer, margin)

    except Exception as e:
        tools_qt.manage_exception(None, f"{type(e).__name__}: {e}", sql, global_vars.schema_name)
    finally:
        # Clean any broken temporal layers (left with no data)
        tools_qgis.clean_layer_group_from_toc('GW Temporal Layers')


def get_config_value(parameter='', columns='value', table='config_param_user', sql_added=None, log_info=True):

    sql = f"SELECT {columns} FROM {table} WHERE parameter = '{parameter}' "
    if sql_added:
        sql += sql_added
    if table == 'config_param_user':
        sql += " AND cur_user = current_user"
    sql += ";"
    row = tools_db.get_row(sql, log_info=log_info)
    return row


def manage_layer_manager(json_result, sql=None):
    """
    Manage options for layers (active, visible, zoom and indexing)
    :param json_result: Json result of a query (Json)
    :param sql: query executed (String)
    :return: None
    """

    try:
        layermanager = json_result['body']['layerManager']
    except KeyError:
        return

    try:

        # force visible and in case of does not exits, load it
        if 'visible' in layermanager:
            for lyr in layermanager['visible']:
                layer_name = [key for key in lyr][0]
                layer = tools_qgis.get_layer_by_tablename(layer_name)
                if layer is None:
                    the_geom = lyr[layer_name]['geom_field']
                    field_id = lyr[layer_name]['pkey_field']
                    if lyr[layer_name]['group_layer'] is not None:
                        group = lyr[layer_name]['group_layer']
                    else:
                        group = "GW Layers"
                    style_id = lyr[layer_name]['style_id']
                    add_layer_database(layer_name, the_geom, field_id, group=group, style_id=style_id)
                tools_qgis.set_layer_visible(layer)

        # force reload dataProvider in order to reindex.
        if 'index' in layermanager:
            for lyr in layermanager['index']:
                layer_name = [key for key in lyr][0]
                layer = tools_qgis.get_layer_by_tablename(layer_name)
                if layer:
                    tools_qgis.set_layer_index(layer)

        # Set active
        if 'active' in layermanager:
            layer = tools_qgis.get_layer_by_tablename(layermanager['active'])
            if layer:
                global_vars.iface.setActiveLayer(layer)

        # Set zoom to extent with a margin
        if 'zoom' in layermanager:
            layer = tools_qgis.get_layer_by_tablename(layermanager['zoom']['layer'])
            if layer:
                prev_layer = global_vars.iface.activeLayer()
                global_vars.iface.setActiveLayer(layer)
                global_vars.iface.zoomToActiveLayer()
                margin = layermanager['zoom']['margin']
                tools_qgis.set_margin(layer, margin)
                if prev_layer:
                    global_vars.iface.setActiveLayer(prev_layer)

    except Exception as e:
        tools_qt.manage_exception(None, f"{type(e).__name__}: {e}", sql, global_vars.schema_name)


def remove_selection(remove_groups=True, layers=None):
    """ Remove all previous selections """

    list_layers = ["v_edit_arc", "v_edit_node", "v_edit_connec", "v_edit_element"]
    if global_vars.project_type == 'ud':
        list_layers.append("v_edit_gully")

    for layer_name in list_layers:
        layer = tools_qgis.get_layer_by_tablename(layer_name)
        if layer:
            layer.removeSelection()

    if remove_groups and layers is not None:
        for key, elems in layers.items():
            for layer in layers[key]:
                if layer:
                    layer.removeSelection()

    global_vars.canvas.refresh()

    return layers


def docker_dialog(dialog):

    positions = {8: Qt.BottomDockWidgetArea, 4: Qt.TopDockWidgetArea,
                 2: Qt.RightDockWidgetArea, 1: Qt.LeftDockWidgetArea}
    try:
        global_vars.session_vars['dialog_docker'].setWindowTitle(dialog.windowTitle())
        global_vars.session_vars['dialog_docker'].setWidget(dialog)
        global_vars.session_vars['dialog_docker'].setWindowFlags(Qt.WindowContextHelpButtonHint)
        global_vars.iface.addDockWidget(positions[global_vars.session_vars['dialog_docker'].position],
                                        global_vars.session_vars['dialog_docker'])
    except RuntimeError as e:
        msg = "{0} --> {1}"
        msg_params = (type(e).__name__, e,)
        tools_log.log_warning(msg, msg_params=msg_params)


def init_docker(docker_param='qgis_info_docker'):
    """ Get user config parameter @docker_param """

    global_vars.session_vars['info_docker'] = True
    # Show info or form in docker?
    row = get_config_value(docker_param)
    if not row:
        global_vars.session_vars['dialog_docker'] = None
        global_vars.session_vars['docker_type'] = None
        return None
    value = row[0].lower()

    # Check if docker has dialog of type 'form' or 'main'
    if docker_param == 'qgis_info_docker':
        if global_vars.session_vars['dialog_docker']:
            if global_vars.session_vars['docker_type']:
                if global_vars.session_vars['docker_type'] != 'qgis_info_docker':
                    global_vars.session_vars['info_docker'] = False
                    return None

    if value == 'true':
        close_docker()
        global_vars.session_vars['docker_type'] = docker_param
        global_vars.session_vars['dialog_docker'] = DrDocker()
        global_vars.session_vars['dialog_docker'].dlg_closed.connect(partial(close_docker, option_name='position'))
        manage_docker_options()
    else:
        global_vars.session_vars['dialog_docker'] = None
        global_vars.session_vars['docker_type'] = None

    return global_vars.session_vars['dialog_docker']


def close_docker(option_name='position'):
    """ Save QDockWidget position (1=Left, 2=Right, 4=Top, 8=Bottom),
        remove from iface and del class
    """

    try:
        if global_vars.session_vars['dialog_docker']:
            if not global_vars.session_vars['dialog_docker'].isFloating():
                docker_pos = global_vars.iface.mainWindow().dockWidgetArea(global_vars.session_vars['dialog_docker'])
                widget = global_vars.session_vars['dialog_docker'].widget()
                if widget:
                    widget.close()
                    del widget
                    global_vars.session_vars['dialog_docker'].setWidget(None)
                    global_vars.session_vars['docker_type'] = None
                    set_config_parser('docker', option_name, f'{docker_pos}')
                global_vars.iface.removeDockWidget(global_vars.session_vars['dialog_docker'])
                global_vars.session_vars['dialog_docker'] = None
    except AttributeError:
        global_vars.session_vars['docker_type'] = None
        global_vars.session_vars['dialog_docker'] = None


def manage_docker_options(option_name='position'):
    """ Check if user want dock the dialog or not """

    # Load last docker position
    try:
        # Docker positions: 1=Left, 2=Right, 4=Top, 8=Bottom
        pos = int(get_config_parser('docker', option_name, "user", "session"))
        global_vars.session_vars['dialog_docker'].position = 2
        if pos in (1, 2, 4, 8):
            global_vars.session_vars['dialog_docker'].position = pos
    except Exception:
        global_vars.session_vars['dialog_docker'].position = 2


def set_tablemodel_config(dialog, widget, table_name, sort_order=0, isQStandardItemModel=False, schema_name=None):
    """ Configuration of tables. Set visibility and width of columns """

    widget = tools_qt.get_widget(dialog, widget)
    if not widget:
        return widget

    if schema_name is not None:
        config_table = f"{schema_name}.config_form_tableview"
    else:
        config_table = "config_form_tableview"

    # Set width and alias of visible columns
    columns_to_delete = []
    sql = (f"SELECT columnindex, width, alias, visible, style"
           f" FROM {config_table}"
           f" WHERE objectname = '{table_name}'"
           f" ORDER BY columnindex")
    rows = tools_db.get_rows(sql)

    if not rows:
        return widget

    for row in rows:
        if not row['visible']:
            columns_to_delete.append(row['columnindex'])
        else:
            style = row.get('style')
            if style:
                stretch = style.get('stretch')
                if stretch is not None:
                    stretch = 1 if stretch else 0
                    widget.horizontalHeader().setSectionResizeMode(row['columnindex'], stretch)
            width = row['width']
            if width is None:
                width = 100
            widget.setColumnWidth(row['columnindex'], width)
            if row['alias'] is not None:
                widget.model().setHeaderData(row['columnindex'], Qt.Horizontal, row['alias'])

    # Set order
    if isQStandardItemModel:
        widget.model().sort(0, sort_order)
    else:
        widget.model().setSort(0, sort_order)
        widget.model().select()
    # Delete columns
    for column in columns_to_delete:
        widget.hideColumn(column)

    return widget


def add_icon(widget, icon, sub_folder="20x20"):
    """ Set @icon to selected @widget """

    # Get icons folder
    icons_folder = os.path.join(global_vars.plugin_dir, f"icons{os.sep}dialogs{os.sep}{sub_folder}")
    icon_path = os.path.join(icons_folder, str(icon) + ".png")

    if os.path.exists(icon_path):
        widget.setIcon(QIcon(icon_path))
        if type(widget) is QPushButton:
            widget.setProperty('has_icon', True)
        return QIcon(icon_path)
    else:
        msg = "File not found: {0}"
        msg_params = (icon_path,)
        tools_log.log_info(msg, msg_params=msg_params)
        return False


def add_tableview_header(widget, field):

    model = widget.model()
    if model is None:
        model = QStandardItemModel()

    # Related by Qtable
    model.clear()
    widget.setModel(model)
    widget.horizontalHeader().setStretchLastSection(True)
    try:
        # Get headers
        headers = []
        for x in field['value'][0]:
            headers.append(x)
        # Set headers
        model.setHorizontalHeaderLabels(headers)
    except Exception:
        # if field['value'][0] is None
        pass

    return widget


def fill_tableview_rows(widget, field):

    if field is None or field['value'] is None: return widget
    model = widget.model()

    for item in field['value']:
        row = []
        for value in item.values():
            if value is None:
                value = ""
            if issubclass(type(value), dict):
                value = json.dumps(value)
            row.append(QStandardItem(str(value)))
        if len(row) > 0:
            model.appendRow(row)

    return widget


def set_completer_widget(tablename, widget, field_id, add_id=False):
    """ Set autocomplete of widget @table_object + "_id"
        getting id's from selected @table_object
    """

    if not widget:
        return
    if type(tablename) == list and type(field_id) == list:
        return set_multi_completer_widget(tablename, widget, field_id, add_id=add_id)
    if add_id:
        field_id += '_id'

    sql = (f"SELECT DISTINCT({field_id})"
           f" FROM {tablename}"
           f" ORDER BY {field_id}")
    rows = tools_db.get_rows(sql)
    tools_qt.set_completer_rows(widget, rows)


def set_multi_completer_widget(tablenames: list, widget, fields_id: list, add_id=False):
    """ Set autocomplete of widget @table_object + "_id"
        getting id's from selected @table_object
    """

    if not widget:
        return

    sql = ""
    idx = 0
    for tablename in tablenames:
        field_id = fields_id[idx]
        if add_id:
            field_id += '_id'
        if sql != "":
            sql += " UNION "
        sql += (f"SELECT DISTINCT({field_id}) as a"
                f" FROM {tablename}")
        idx += 1
    sql += " ORDER BY a"

    rows = tools_db.get_rows(sql)
    tools_qt.set_completer_rows(widget, rows)


def current_layer_changed(layer):
    if layer is None:
        return
    if not hasattr(layer, "featureAdded"):
        return

    disconnect_signal('layer_changed')
    connect_signal(layer.featureAdded, partial(check_topology), 'layer_changed', f'{layer.id()}')


def check_topology(fid):
    """ Checks that the inserted features are correct """

    node_layers_to_check = ['inp_storage', 'inp_outfall', 'inp_junction', 'inp_divider']
    arc_layers_to_check = ['inp_outlet', 'inp_weir', 'inp_orifice', 'inp_pump', 'inp_conduit']
    polygon_layers_to_check = []
    layers_to_check = node_layers_to_check + arc_layers_to_check + polygon_layers_to_check
    cur_layer = global_vars.iface.activeLayer()
    if cur_layer not in layers_to_check:
        return

    feature = cur_layer.getFeature(fid)
    feature_geom = feature.geometry()
    # Lines -- find node_1 & node_2 and set them as attributes
    if feature_geom.type() == QgsWkbTypes.LineGeometry:
        # If it already has node_1 & node_2 set don't do anything
        if feature['node_1'] not in (None, 'NULL', 'null') and feature['node_2'] not in (None, 'NULL', 'null'):
            return
        point_1 = feature_geom.vertexAt(0)
        vertices = len([n for n in feature_geom.vertices()])
        point_2 = feature_geom.vertexAt(vertices - 1)
        node_layers = []
        layers = tools_qgis.get_project_layers()
        for layer in layers:
            if tools_qgis.get_tablename_from_layer(layer) in node_layers_to_check:
                node_layers.append(layer)
        if not node_layers:
            print("node layers not found")
            return

        for node_layer in node_layers:
            spatial_index = QgsSpatialIndex(node_layer.getFeatures())
            node_1 = spatial_index.nearestNeighbor(QgsPointXY(point_1), 1, 2)
            node_2 = spatial_index.nearestNeighbor(QgsPointXY(point_2), 1, 2)
            print(f"{node_layer.name()}: {node_1=}, {node_2=}")
            if not node_1 or not node_2:
                continue

            # node_1
            node_fid = node_1[0]
            node = node_layer.getFeature(node_fid)
            feature.setAttribute('node_1', node['node_id'])

            # node_2
            node_fid = node_2[0]
            node = node_layer.getFeature(node_fid)
            feature.setAttribute('node_2', node['node_id'])
            break

    # Points
    elif feature_geom.type() == QgsWkbTypes.PointGeometry:
        pass
    # Polygons
    elif feature_geom.type() == QgsWkbTypes.PolygonGeometry:
        pass
    # Other / No geometry
    else:
        pass
    cur_layer.updateFeature(feature)


def create_rubberband(canvas, geometry_type=1):
    """ Creates a rubberband and adds it to the global list """

    rb = QgsRubberBand(canvas, geometry_type)
    global_vars.active_rubberbands.append(rb)
    return rb


def reset_rubberband(rb, geometry_type=None):
    """ Resets a rubberband and tries to remove it from the global list """

    if geometry_type:
        rb.reset(geometry_type)
    else:
        rb.reset()

    try:
        global_vars.active_rubberbands.remove(rb)
    except ValueError:
        pass


def set_epsg():

    epsg = tools_qgis.get_epsg()
    global_vars.project_epsg = epsg


def lerp_progress(subtask_progress: int, global_min: int, global_max: int) -> int:
    global_progress = global_min + ((subtask_progress - 0) / (100 - 0)) * (global_max - global_min)

    return int(global_progress)


def manage_current_selections_docker(result, open=False):
    """
    Manage labels for the current_selections docker
        :param result: looks the data in result['body']['data']['userValues']
        :param open: if it has to create a new docker or just update it
    """

    if not result or 'body' not in result or 'data' not in result['body']:
        return

    title = "Dr Selectors: "
    if 'userValues' in result['body']['data']:
        for user_value in result['body']['data']['userValues']:
            if user_value['parameter'] == 'plan_psector_vdefault' and user_value['value']:
                sql = f"SELECT name FROM plan_psector WHERE psector_id = {user_value['value']}"
                row = tools_db.get_row(sql, log_info=False)
                if row:
                    title += f"{row[0]} | "
            elif user_value['parameter'] == 'utils_workspace_vdefault' and user_value['value']:
                sql = f"SELECT name FROM cat_workspace WHERE id = {user_value['value']}"
                row = tools_db.get_row(sql, log_info=False)
                if row:
                    title += f"{row[0]} | "
            elif user_value['value']:
                title += f"{user_value['value']} | "

        if global_vars.session_vars['current_selections'] is None:
            global_vars.session_vars['current_selections'] = QDockWidget(title[:-3])
        else:
            global_vars.session_vars['current_selections'].setWindowTitle(title[:-3])
        if open:
            global_vars.iface.addDockWidget(Qt.LeftDockWidgetArea, global_vars.session_vars['current_selections'])


def manage_user_config_folder(user_folder_dir):
    """ Check if user config folder exists. If not create empty files init.config and session.config """

    try:
        config_folder = f"{user_folder_dir}{os.sep}config{os.sep}"
        if not os.path.exists(config_folder):
            msg = "Creating user config folder: {0}"
            msg_params = (config_folder,)
            tools_log.log_info(msg, msg_params=msg_params)
            os.makedirs(config_folder)

        # Check if config files exists. If not create them empty
        filepath = f"{config_folder}{os.sep}init.config"
        if not os.path.exists(filepath):
            open(filepath, 'a').close()
        filepath = f"{config_folder}{os.sep}session.config"
        if not os.path.exists(filepath):
            open(filepath, 'a').close()

    except Exception as e:
        msg = "{0}: {1}"
        msg_params = ("manage_user_config_folder", e,)
        tools_log.log_warning(msg, msg_params=msg_params)


def user_params_to_userconfig():
    """ Function to load all the variables from user_params.config to their respective user config files """

    parser = global_vars.configs['user_params'][1]
    if parser is None:
        return

    # Get the sections of the user params inventory
    inv_sections = parser.sections()

    # For each section (inventory)
    for section in inv_sections:

        file_name = section.split('.')[0]
        section_name = section.split('.')[1]
        parameters = parser.options(section)

        # For each parameter (inventory)
        for parameter in parameters:

            # Manage if parameter need prefix and project_type is not defined
            if parameter.startswith("_") and global_vars.project_type is None:
                continue
            if parameter.startswith("#"):
                continue

            _pre = False
            inv_param = parameter
            # If it needs a prefix
            if parameter.startswith("_"):
                _pre = True
                parameter = inv_param[1:]
            # If it's just a comment line
            if parameter.startswith("#"):
                # tools_log.log_info(f"set_config_parser: {file_name} {section_name} {parameter}")
                set_config_parser(section_name, parameter, None, "user", file_name, prefix=False, chk_user_params=False)
                continue

            # If it's a normal value
            # Get value[section][parameter] of the user config file
            value = get_config_parser(section_name, parameter, "user", file_name, _pre, True, False, True)

            # If this value (user config file) is None (doesn't exist, isn't set, etc.)
            if value is None:
                # Read the default value for that parameter
                value = get_config_parser(section, inv_param, "project", "user_params", False, True, False, True)
                # Set value[section][parameter] in the user config file
                set_config_parser(section_name, parameter, value, "user", file_name, None, _pre, False)
            else:
                value2 = get_config_parser(section, inv_param, "project", "user_params", False, True, False, True)
                if value2 is not None:
                    # If there's an inline comment in the inventory but there isn't one in the user config file, add it
                    if "#" not in value and "#" in value2:
                        # Get the comment (inventory) and set it (user config file)
                        comment = value2.split('#')[1]
                        set_config_parser(section_name, parameter, value.strip(), "user", file_name, comment, _pre, False)


def hide_widgets_form(dialog, dlg_name):

    row = get_config_value(parameter=f'qgis_form_{dlg_name}_hidewidgets', columns='value::text', table='config_param_system')
    if row:
        widget_list = dialog.findChildren(QWidget)
        for widget in widget_list:
            if widget.objectName() and f'"{widget.objectName()}"' in row[0]:
                lbl_widget = dialog.findChild(QLabel, f"lbl_{widget.objectName()}")
                if lbl_widget:
                    lbl_widget.setVisible(False)
                widget.setVisible(False)


def reset_position_dialog(show_message=False, plugin='core', file_name='session'):
    """ Reset position dialog x/y """

    try:
        parser = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True, strict=False)
        config_folder = f"{global_vars.user_folder_dir}{os.sep}{plugin}{os.sep}config"

        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        path = f"{config_folder}{os.sep}{file_name}.config"
        parser.read(path)
        # Check if section exists in file
        if "dialogs_position" in parser:
            parser.remove_section("dialogs_position")

        msg = "Reset position form done successfully."
        title = "Info"
        if show_message:
            tools_qt.show_info_box(msg, title)

        with open(path, 'w') as configfile:
            parser.write(configfile)
            configfile.close()
    except Exception as e:
        msg = "{0} exception [{1}]: {2}"
        msg_params = ("reset_position_dialog", type(e).__name__, e,)
        tools_log.log_warning(msg, msg_params=msg_params)
        return


def add_btn_help(dlg):
    """ Create and add btn_help in all dialogs """
    if tools_qt.get_widget(dlg, 'btn_help') is not None:
        return
    if not hasattr(dlg, 'lyt_buttons'):
        return
    if not hasattr(dlg.lyt_buttons, 'columnCount'):
        return

    btn_help_text_translated = tools_qt.tr("btn_help", "common", default="Help")
    btn_help = QPushButton(btn_help_text_translated)
    btn_help.setObjectName("btn_help") 
    btn_help.setToolTip(btn_help_text_translated)
    dlg.lyt_buttons.addWidget(btn_help, 0, dlg.lyt_buttons.columnCount())

    # Get formtype, formname & tabname
    context = dlg.property('context')
    uiname = dlg.property('uiname')
    tabname = 'tab_none'
    tab_widgets = dlg.findChildren(QTabWidget, "")
    if tab_widgets:
        tab_widget = tab_widgets[0]
        index_tab = tab_widget.currentIndex()
        tabname = tab_widget.widget(index_tab).objectName()

    btn_help.clicked.connect(partial(open_help_link, context, uiname, tabname))


def open_help_link(context, uiname, tabname=None):
    """ Opens the help link for the given dialog, or a default link if not found. """

    # Base URL for the documentation
    # domain = "https://docs.giswater.org" #TODO Change to drain domain
    # language = "es_CR" # TODO: get dynamic language
    # plugin_version = "testing" # TODO: get dynamic version

    # if plugin_version == "":
    #     plugin_version = "latest"

    # base_url = f"{domain}/{plugin_version}/{language}/docs/giswater/for-users" #TODO Change to drain path

    # uiname = uiname.replace("_", "-").replace(" ", "-").lower() + ".html" # sanitize uiname

    # # Construct the path dynamically
    # if uiname:
    #     file_path = f"{base_url}/dialogs/{uiname}"
    #     if tabname != 'tab_none':
    #         file_path += f"#{tabname}"  # Append tabname as an anchor if provided
    # else:
    #     # Fallback to the general manual link if context and uiname are missing
    #     file_path = f"{base_url}/index.html"

    file_path = "https://drain-iber.github.io/testing/en/docs/drain/for-users/user-manual/index.html"
    tools_os.open_file(file_path)


# region private functions

def _check_user_params(section, parameter, file_name, prefix=False):
    """ Check if a parameter exists in the config/user_params.config
        If it doesn't exist, it creates it and assigns 'None' as a default value
    """

    if section == "i18n_generator":
        return

    # Check if the parameter needs the prefix or not
    if prefix and global_vars.project_type is not None:
        parameter = f"_{parameter}"

    # Get the value of the parameter (the one get_config_parser is looking for) in the inventory
    check_value = get_config_parser(f"{file_name}.{section}", parameter, "project", "user_params", False,
                                    get_comment=True, chk_user_params=False)
    # If it doesn't exist in the inventory, add it with "None" as value
    if check_value is None:
        set_config_parser(f"{file_name}.{section}", parameter, None, "project", "user_params", prefix=False,
                          chk_user_params=False)
    else:
        return check_value


def _get_parser_from_filename(filename):
    """ Get parser of file @filename.config """

    if filename in ('init', 'session'):
        folder = f"{global_vars.user_folder_dir}{os.sep}core"
    elif filename in ('dev', 'drain', 'user_params'):
        folder = global_vars.plugin_dir
    else:
        return None, None

    parser = configparser.ConfigParser(comment_prefixes=";", allow_no_value=True, strict=False)
    filepath = f"{folder}{os.sep}config{os.sep}{filename}.config"
    if not os.path.exists(filepath):
        msg = "File not found: {0}"
        msg_params = (filepath,)
        tools_log.log_warning(msg, msg_params=msg_params)
        return filepath, None

    try:
        parser.read(filepath)
    except (configparser.DuplicateSectionError, configparser.DuplicateOptionError) as e:
        msg = "Error parsing file: {0}"
        msg_params = (filepath,)
        tools_log.log_warning(msg, msg_params=msg_params, parameter=e)
        return filepath, None

    return filepath, parser


# endregion


# region
def set_filter_listeners(complet_result, dialog, widget_list, columnname, widgetname, feature_id=None):
    """
    functions called in -> widget.textChanged.connect(partial(getattr(tools_backend_calls, widgetfunction), **kwargs))
                        -> widget.currentIndexChanged.connect(partial(getattr(tools_backend_calls, widgetfunction), **kwargs))
       module = tools_backend_calls -> def open_rpt_result(**kwargs)
                                    -> def filter_table(self, **kwargs)
     """

    model = None
    for widget in widget_list:
        if type(widget) is QTableView:
            model = widget.model()

    # Emitting the text changed signal of a widget slows down the process, so instead of emitting a signal for each
    # widget, we will emit only the one of the last widget. This is enough for the correct filtering of the
    # QTableView and we gain in performance
    last_widget = None
    for widget in widget_list:
        if widget.property('isfilter') is not True: continue
        module = tools_backend_calls
        functions = None
        if widget.property('widgetfunction') is not None and isinstance(widget.property('widgetfunction'), list):
            functions = []
            for function in widget.property('widgetfunction'):
                func_names = []
                widgetfunction = function['functionName']
                if 'isFilter' in function:
                    if function['isFilter']:
                        functions.append(function)

        if widget.property('widgetfunction') is not None and 'functionName' in widget.property('widgetfunction'):
            widgetfunction = widget.property('widgetfunction')['functionName']
            functions = [widget.property('widgetfunction')]
        if widgetfunction is False: continue

        linkedobject = ""
        if widget.property('linkedobject') is not None:
            linkedobject = widget.property('linkedobject')

        if feature_id is None:
            feature_id = ""

        if isinstance(widget.property('widgetfunction'), list):
            widgetfunction = widget.property('widgetfunction')
        else:
            widgetfunction = [widget.property('widgetfunction')]

        for i in range(len(functions)):
            kwargs = {"complet_result": complet_result, "model": model, "dialog": dialog, "linkedobject": linkedobject,
                      "columnname": columnname, "widget": widget, "widgetname": widgetname, "widget_list": widget_list,
                      "feature_id": feature_id, "func_params": functions[i]['parameters']}

            if functions[i] is not None:
                if 'module' in functions[i]:
                    module = globals()[functions[i]['module']]
                function_name = functions[i].get('functionName')
                if function_name is not None:
                    if function_name:
                        exist = tools_os.check_python_function(module, function_name)
                        if not exist:
                            msg = "Widget {0} has associated function {1}, but {1} not exist"
                            msg_params = (widget.property('widgetname'), function_name,)
                            tools_qgis.show_message(msg, 2, msg_params=msg_params)
                            return widget
                    else:
                        msg = "Parameter {0} is null for button"
                        msg_params = ("functionName",)
                        tools_qgis.show_message(msg, 2, parameter=widget.objectName())

            func_params = ""
            function_name = ""
            if widgetfunction[i] is not None and 'functionName' in widgetfunction[i]:
                function_name = widgetfunction[i]['functionName']

                exist = tools_os.check_python_function(module, function_name)
                if not exist:
                    msg = "Widget {0} has associated function {1}, but {1} not exist"
                    msg_params = (widget.property('widgetname'), function_name,)
                    tools_qgis.show_message(msg, 2, msg_params=msg_params)
                    return widget
                if 'parameters' in widgetfunction[i]:
                    func_params = widgetfunction[i]['parameters']

            kwargs['widget'] = widget
            kwargs['message_level'] = 1
            kwargs['function_name'] = function_name
            kwargs['func_params'] = func_params
            if function_name:
                if type(widget) is QLineEdit:
                    widget.textChanged.connect(partial(getattr(module, function_name), **kwargs))
                elif type(widget) is QComboBox:
                    widget.currentIndexChanged.connect(partial(getattr(module, function_name), **kwargs))
                elif type(widget) is QgsDateTimeEdit:
                    widget.setDate(QDate.currentDate())
                    widget.dateChanged.connect(partial(getattr(module, function_name), **kwargs))
                elif type(widget) is QSpinBox:
                    widget.valueChanged.connect(partial(getattr(module, function_name), **kwargs))
                else:
                    continue

            last_widget = widget

    # Emit signal changed
    if last_widget is not None:
        if type(last_widget) is QLineEdit:
            text = tools_qt.get_text(dialog, last_widget, False, False)
            last_widget.textChanged.emit(text)
        elif type(last_widget) is QComboBox:
            last_widget.currentIndexChanged.emit(last_widget.currentIndex())


def set_widgets(dialog, complet_result, field, tablename, class_info):
    """
    functions called in -> widget = getattr(self, f"manage_{field['widgettype']}")(**kwargs)
        def manage_text(self, **kwargs)
        def manage_typeahead(self, **kwargs)
        def manage_combo(self, **kwargs)
        def manage_check(self, **kwargs)
        def manage_datetime(self, **kwargs)
        def manage_button(self, **kwargs)
        def manage_hyperlink(self, **kwargs)
        def manage_hspacer(self, **kwargs)
        def manage_vspacer(self, **kwargs)
        def manage_textarea(self, **kwargs)
        def manage_spinbox(self, **kwargs)
        def manage_doubleSpinbox(self, **kwargs)
        def manage_tableview(self, **kwargs)
    """

    widget = None
    label = None
    if 'label' in field and field['label']:
        label = QLabel()
        label.setObjectName('lbl_' + field['widgetname'])
        label.setText(field['label'].capitalize())
        if 'stylesheet' in field and field['stylesheet'] is not None and 'label' in field['stylesheet']:
            label = set_stylesheet(field, label)
        if 'tooltip' in field:
            label.setToolTip(field['tooltip'])
        else:
            label.setToolTip(field['label'].capitalize())

    if 'widgettype' in field and not field['widgettype']:
        msg = "The field {0} is not configured for: {1}"
        msg_params = ("widgettype", f"formname:{tablename}, columnname:{field['columnname']}",)
        tools_qgis.show_message(msg, 2, msg_params=msg_params, dialog=dialog)
        return label, widget

    try:
        kwargs = {"dialog": dialog, "complet_result": complet_result, "field": field,
                  "class": class_info}
        widget = globals()[f"_manage_{field['widgettype']}"](**kwargs)
    except Exception as e:
        msg = (f"{type(e).__name__}: {e} {tools_qt.tr('Python function')}: tools_dr.set_widgets. WHERE: "
               f"columname='{field['columnname']}' AND widgetname='{field['widgetname']}' AND "
               f"widgettype='{field['widgettype']}'")
        tools_qgis.show_message(msg, 2, msg_params=msg_params, dialog=dialog)
        return label, widget

    try:
        widget.setProperty('isfilter', False)
        if 'isfilter' in field and field['isfilter'] is True:
            widget.setProperty('isfilter', True)

        widget.setProperty('widgetfunction', False)
        if 'widgetfunction' in field and field['widgetfunction'] is not None:
            widget.setProperty('widgetfunction', field['widgetfunction'])
        if 'linkedobject' in field and field['linkedobject']:
            widget.setProperty('linkedobject', field['linkedobject'])
        if field['widgetcontrols'] is not None and 'saveValue' in field['widgetcontrols']:
            if field['widgetcontrols']['saveValue'] is False:
                widget.setProperty('saveValue', False)
        if field['widgetcontrols'] is not None and 'isEnabled' in field['widgetcontrols']:
            if field['widgetcontrols']['isEnabled'] is False:
                widget.setEnabled(False)
    except Exception:
        # AttributeError: 'QSpacerItem' object has no attribute 'setProperty'
        pass

    return label, widget


def _manage_text(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"manage_{field['widgettype']}")(**kwargs)
    """

    field = kwargs['field']

    widget = add_lineedit(field)
    widget = set_widget_size(widget, field)
    widget = _set_min_max_values(widget, field)
    widget = _set_reg_exp(widget, field)
    widget = set_data_type(field, widget)
    widget = _set_max_length(widget, field)

    return widget


def _set_min_max_values(widget, field):
    """ Set max and min values allowed """

    if field['widgetcontrols'] and 'maxMinValues' in field['widgetcontrols']:
        if 'min' in field['widgetcontrols']['maxMinValues']:
            widget.setProperty('minValue', field['widgetcontrols']['maxMinValues']['min'])

    if field['widgetcontrols'] and 'maxMinValues' in field['widgetcontrols']:
        if 'max' in field['widgetcontrols']['maxMinValues']:
            widget.setProperty('maxValue', field['widgetcontrols']['maxMinValues']['max'])

    return widget


def _set_max_length(widget, field):
    """ Set max and min values allowed """

    if field['widgetcontrols'] and 'maxLength' in field['widgetcontrols']:
        if field['widgetcontrols']['maxLength'] is not None:
            widget.setProperty('maxLength', field['widgetcontrols']['maxLength'])

    return widget


def _set_reg_exp(widget, field):
    """ Set regular expression """

    if 'widgetcontrols' in field and field['widgetcontrols']:
        if field['widgetcontrols'] and 'regexpControl' in field['widgetcontrols']:
            if field['widgetcontrols']['regexpControl'] is not None:
                reg_exp = QRegExp(str(field['widgetcontrols']['regexpControl']))
                widget.setValidator(QRegExpValidator(reg_exp))

    return widget


def _manage_typeahead(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """

    dialog = kwargs['dialog']
    field = kwargs['field']
    complet_result = kwargs['complet_result']
    feature_id = complet_result['body']['feature']['id']
    completer = QCompleter()
    widget = _manage_text(**kwargs)
    widget = set_typeahead(field, dialog, widget, completer, feature_id=feature_id)
    return widget


def _manage_combo(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """
    dialog = kwargs['dialog']
    field = kwargs['field']
    complet_result = kwargs['complet_result']

    widget = add_combo(field, dialog, complet_result)
    widget = set_widget_size(widget, field)
    return widget


def _manage_check(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """

    dialog = kwargs['dialog']
    field = kwargs['field']
    class_info = kwargs['class']
    widget = add_checkbox(**kwargs)
    # widget.stateChanged.connect(partial(get_values, dialog, widget, class_info.my_json))
    return widget


def _manage_datetime(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """

    dialog = kwargs['dialog']
    field = kwargs['field']
    widget = add_calendar(dialog, field, **kwargs)
    return widget


def _manage_button(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """

    field = kwargs['field']
    stylesheet = field.get('stylesheet') or {}
    info_class = kwargs['class']
    # If button text is empty it's because node_1/2 is not present.
    # Then we create a QLineEdit to input a node to be connected.
    if not field.get('value') and stylesheet.get('icon') is None:
        widget = _manage_text(**kwargs)
        widget.editingFinished.connect(partial(info_class.run_settopology, widget, **kwargs))
        return widget
    widget = add_button(**kwargs)
    widget = set_widget_size(widget, field)
    return widget


def _manage_hyperlink(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """

    field = kwargs['field']
    widget = add_hyperlink(field)
    widget = set_widget_size(widget, field)
    return widget


def _manage_hspacer(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """

    widget = tools_qt.add_horizontal_spacer()
    return widget


def _manage_vspacer(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """

    widget = tools_qt.add_verticalspacer()
    return widget


def _manage_textarea(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """

    field = kwargs['field']
    widget = add_textarea(field)
    return widget


def _manage_spinbox(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
            widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
        """

    widget = add_spinbox(**kwargs)
    return widget


def _manage_doubleSpinbox(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """

    dialog = kwargs['dialog']
    field = kwargs['field']
    info = kwargs['info']
    widget = add_spinbox(**kwargs)
    return widget


def _manage_list(self, **kwargs):
    _manage_tableview(**kwargs)


def _manage_tableview(**kwargs):
    """ This function is called in def set_widgets(self, dialog, complet_result, field, new_feature)
        widget = getattr(self, f"_manage_{field['widgettype']}")(**kwargs)
    """
    complet_result = kwargs['complet_result']
    field = kwargs['field']
    dialog = kwargs['dialog']
    class_self = kwargs['class']
    module = tools_backend_calls
    widget = add_tableview(complet_result, field, dialog, module, class_self)
    widget = add_tableview_header(widget, field)
    widget = fill_tableview_rows(widget, field)
    widget = set_tablemodel_config(dialog, widget, field['columnname'], 1, True)
    tools_qt.set_tableview_config(widget)
    return widget

# endregion
