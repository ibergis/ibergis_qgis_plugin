<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.9-Firenze" styleCategories="Symbology|Symbology3D">
  <renderer-3d type="rulebased" layer="Mesh_Temp_Layer_e29679e0_d77e_4dab_bc4b_6312f49b6491">
    <vector-layer-3d-tiling show-bounding-boxes="0" zoom-levels-count="3"/>
    <rules key="{09c84888-a1ef-4052-90eb-22b3a2acbb06}">
      <rule description="Ground" filter="category='ground'" key="{23e2b2c7-367b-4d17-bd7e-0040348a6c41}">
        <symbol type="polygon" material_type="phong">
          <data alt-clamping="absolute" extrusion-height="0" add-back-faces="0" height="0" invert-normals="1" culling-mode="no-culling" rendered-facade="3" alt-binding="centroid"/>
          <material ambient="26,26,26,255" diffuse="230,230,230,255" specular="255,255,255,255" shininess="0" opacity="1">
            <data-defined-properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data-defined-properties>
          </material>
          <data-defined-properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="extrusionHeight">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="-z_max($geometry)" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data-defined-properties>
          <edges enabled="0" color="0,0,0,255" width="1"/>
        </symbol>
      </rule>
      <rule description="Roof" filter="category='roof'" key="{fcdd58bc-facb-4ed0-96c0-5b583155aad0}">
        <symbol type="polygon" material_type="phong">
          <data alt-clamping="absolute" extrusion-height="0" add-back-faces="0" height="0" invert-normals="1" culling-mode="no-culling" rendered-facade="3" alt-binding="centroid"/>
          <material ambient="179,130,62,255" diffuse="217,198,141,255" specular="255,255,255,255" shininess="0" opacity="1">
            <data-defined-properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data-defined-properties>
          </material>
          <data-defined-properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="extrusionHeight">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="-z_max($geometry)" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data-defined-properties>
          <edges enabled="0" color="0,0,0,255" width="1"/>
        </symbol>
      </rule>
    </rules>
  </renderer-3d>
  <renderer-v2 type="categorizedSymbol" symbollevels="0" attr="category" forceraster="0" enableorderby="0" referencescale="-1">
    <categories>
      <category type="string" render="true" value="ground" label="Ground" symbol="0"/>
      <category type="string" render="true" value="roof" label="Roof" symbol="1"/>
    </categories>
    <symbols>
      <symbol type="fill" frame_rate="10" force_rhr="0" is_animated="0" clip_to_extent="1" name="0" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="230,230,230,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="77,77,77,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" frame_rate="10" force_rhr="0" is_animated="0" clip_to_extent="1" name="1" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="217,198,141,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="179,130,62,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
