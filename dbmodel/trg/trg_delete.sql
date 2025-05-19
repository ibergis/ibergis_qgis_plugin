
/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

PRAGMA foreign_keys = OFF;

---------------------------------------------------
-- TRIGGERS TO CREATE AN AUTOINDEX FOR EACH ELEMENT
-- ------------------------------------------------
DROP TRIGGER IF EXISTS "trg_ins_code_inp_outlet";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_weir";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_orifice";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_pump";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_conduit";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_storage";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_junction";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_outfall";
DROP TRIGGER IF EXISTS "trg_ins_code_inp_divider";
DROP TRIGGER IF EXISTS "trg_ins_code_roof";
DROP TRIGGER IF EXISTS "trg_ins_code_ground";
DROP TRIGGER IF EXISTS "trg_ins_code_inlet";
DROP TRIGGER IF EXISTS "trg_ins_code_hyetograph";
DROP TRIGGER IF EXISTS "trg_ins_code_culvert";
DROP TRIGGER IF EXISTS "trg_ins_code_pinlet";
DROP TRIGGER IF EXISTS "trg_ins_code_boundary_condition";
DROP TRIGGER IF EXISTS "trg_ins_code_bridge";

------------------------------------------------
-- TRIGGERS TO MANAGE TOPOLOGY WITH FOREIGN KEYS
------------------------------------------------

-- nodes
DROP TRIGGER IF EXISTS "trg_ins_inp_junction";
DROP TRIGGER IF EXISTS "trg_ins_inp_storage";
DROP TRIGGER IF EXISTS "trg_ins_inp_outfall";
DROP TRIGGER IF EXISTS "trg_ins_inp_divider";
DROP TRIGGER IF EXISTS "trg_ins_inp_inlet";

DROP TRIGGER IF EXISTS "trg_upd_code_inp_junction";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_storage";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_outfall";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_divider";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_inlet";

DROP TRIGGER IF EXISTS "trg_del_inp_junction";
DROP TRIGGER IF EXISTS "trg_del_inp_storage";
DROP TRIGGER IF EXISTS "trg_del_inp_outfall";
DROP TRIGGER IF EXISTS "trg_del_inp_divider";
DROP TRIGGER IF EXISTS "trg_del_inp_inlet";



-- arcs
DROP TRIGGER IF EXISTS "trg_ins_inp_outlet";
DROP TRIGGER IF EXISTS "trg_ins_inp_weir";
DROP TRIGGER IF EXISTS "trg_ins_inp_orifice";
DROP TRIGGER IF EXISTS "trg_ins_inp_pump";
DROP TRIGGER IF EXISTS "trg_ins_inp_conduit";

DROP TRIGGER IF EXISTS "trg_upd_code_inp_outlet";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_weir";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_orifice";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_pump";
DROP TRIGGER IF EXISTS "trg_upd_code_inp_conduit";

DROP TRIGGER IF EXISTS "trg_del_inp_outlet";
DROP TRIGGER IF EXISTS "trg_del_inp_orifice";
DROP TRIGGER IF EXISTS "trg_del_inp_conduit";
DROP TRIGGER IF EXISTS "trg_del_inp_weir";
DROP TRIGGER IF EXISTS "trg_del_inp_pump";


--------------------------------------------------------------------------------------------------------------
-- TOPOCONTROL TRIGGERS: SET node_1 AND node_2 TO ARCS BY PROXIMITY (conduits, pumps, outlets, orifices, weir)
-- -----------------------------------------------------------------------------------------------------------

---- inp_conduit
DROP TRIGGER IF EXISTS trg_ins_nodes_inp_conduit;
DROP TRIGGER IF EXISTS trg_upd_nodes_inp_conduit;

---- inp_weir
DROP TRIGGER IF EXISTS trg_ins_nodes_inp_weir;
DROP TRIGGER IF EXISTS trg_upd_nodes_inp_weir;

---- inp_pump
DROP TRIGGER IF EXISTS trg_ins_nodes_inp_pump;
DROP TRIGGER IF EXISTS trg_upd_nodes_inp_pump;

---- inp_orifice
DROP TRIGGER IF EXISTS trg_ins_nodes_inp_orifice;
DROP TRIGGER IF EXISTS trg_upd_nodes_inp_orifice;

---- inp_outlet
DROP TRIGGER IF EXISTS trg_ins_nodes_inp_outlet;
DROP TRIGGER IF EXISTS trg_upd_nodes_inp_outlet;
