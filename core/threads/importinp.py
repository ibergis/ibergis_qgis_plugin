import traceback
import os

from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsCoordinateReferenceSystem, QgsProject, QgsFeature

from . import importinp_core as core
from .epa_file_manager import _tables_dict
from .task import DrTask
from ..utils.generate_swmm_inp.generate_swmm_import_inp_file import ImportInpFile
from ..utils import tools_dr
from ...lib import tools_qgis
from ... import global_vars


class DrImportInpTask(DrTask):
    def __init__(self, description, input_file, gpkg_path, save_folder, feedback):
        super().__init__(description)
        self.input_file = input_file
        self.gpkg_path = gpkg_path
        self.save_folder = save_folder
        self.feedback = feedback

    def cancel(self):
        super().cancel()
        self.feedback.cancel()

    def run(self):
        super().run()
        try:
            self.dao = global_vars.gpkg_dao_data.clone()
            output = self._import_file()
            if not output:
                return False
            # Get data from gpkg and import it to existing layers (changing the column names)
            self._import_to_project()
            return True
        except Exception:
            self.exception = traceback.format_exc()
            return False

    def _import_file(self):

        self.process = ImportInpFile()
        self.process.initAlgorithm(None)
        params = self._manage_params()
        context = QgsProcessingContext()
        self.output = self.process.processAlgorithm(params, context, self.feedback)

        # processing.run("GenSwmmInp:ImportInpFile", {'INP_FILE':'P:\\31_GISWATER\\313_DEV\\epa_importinp\\maspi_proves\\ud_bcn_prim_saved.inp','GEODATA_DRIVER':1,'SAVE_FOLDER':'C:\\Users\\usuario\\Desktop\\QGIS Projects\\drain\\importinp','PREFIX':'','DATA_CRS':QgsCoordinateReferenceSystem('EPSG:25831')})
        return True

    def _manage_params(self) -> dict:
        params = {
            "INP_FILE": self.input_file,
            "GEODATA_DRIVER": 1, # 1: GPKG
            "SAVE_FOLDER": self.save_folder,
            "PREFIX": "",
            "DATA_CRS": QgsCoordinateReferenceSystem("EPSG:25831"),
        }
        return params

    def _import_to_project(self):
        """ Import the data from the gpkg to the project """

        gpkgs = ['SWMM_junctions', 'SWMM_outfalls', 'SWMM_storages', 'SWMM_pumps', 'SWMM_orifices', 'SWMM_weirs',
                 'SWMM_outlets', 'SWMM_conduits', 'SWMM_raingages', 'SWMM_subcatchments']
        layermap = {
            'SWMM_conduits': 'inp_conduit',
            'SWMM_junctions': 'inp_junction',
            'SWMM_orifices': 'inp_orifice',
            'SWMM_outfalls': 'inp_outfall',
            'SWMM_outlets': 'inp_outlet',
            'SWMM_pumps': 'inp_pump',
            'SWMM_raingages': 'inp_raingage',
            'SWMM_storages': 'inp_storage',
            'SWMM_subcatchments': 'inp_subcatchment',
            'SWMM_weirs': 'inp_weir'
        }
        for gpkg in gpkgs:
            gpkg_file = f"{self.save_folder}{os.sep}{gpkg}.gpkg"

            if not os.path.exists(gpkg_file):
                print(f"Skipping {gpkg_file}, does not exist.")
                continue

            imported_layers = tools_dr.load_gpkg(str(gpkg_file))

            for layer_name, source_layer in imported_layers.items():
                dr_layername = layermap.get(layer_name)
                if not dr_layername:
                    print(f"Skipping {dr_layername}, not found in layermap.")
                    continue

                target_layer = tools_qgis.get_layer_by_tablename(dr_layername)

                if not target_layer:
                    print(f"Skipping {dr_layername}, not found in project.")
                    continue

                target_layer = target_layer
                field_map = _tables_dict[dr_layername]["mapper"]
                print(f"Importing {dr_layername} into project...")
                self._insert_data(source_layer, target_layer, field_map)

                print(f"Imported {dr_layername} into project.")

    def _insert_data(self, source_layer, target_layer, field_map):
        """Copies features from the source layer to the target layer with mapped fields."""

        features_to_add = []

        # Get the target field names in order
        target_field_names = [field.name() for field in target_layer.fields()]

        for feature in source_layer.getFeatures():
            new_feature = QgsFeature(target_layer.fields())

            # Map attributes efficiently
            attributes = [None] * len(target_field_names)
            for src_field, tgt_field in field_map.items():
                if tgt_field in target_field_names:
                    attributes[target_field_names.index(tgt_field)] = feature[src_field]
            new_feature.setAttributes(attributes)
            new_feature.setGeometry(feature.geometry())  # Preserve geometry
            features_to_add.append(new_feature)

        target_layer.startEditing()
        target_layer.addFeatures(features_to_add)
        target_layer.commitChanges()

