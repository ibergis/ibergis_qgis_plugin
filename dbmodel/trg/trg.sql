
/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

---------------------------------------------------
-- TRIGGERS TO CREATE AN AUTOINDEX FOR EACH ELEMENT
-- ------------------------------------------------

create trigger "trg_ins_code_inp_outlet" after insert on "inp_outlet" BEGIN update inp_outlet set code = 'T'||fid; END;
create trigger "trg_ins_code_inp_weir" after insert on "inp_weir" BEGIN update inp_weir set code = 'W'||fid;END;
create trigger "trg_ins_code_inp_orifice" after insert on "inp_orifice" BEGIN update inp_orifice set code = 'R'||fid; END;
create trigger "trg_ins_code_inp_pump" after insert on "inp_pump" BEGIN update inp_pump set code = 'P'||fid; END;
create trigger "trg_ins_code_inp_conduit" after insert on "inp_conduit" BEGIN update inp_conduit set code = 'C'||fid; END;
create trigger "trg_ins_code_inp_storage" after insert on "inp_storage" BEGIN update inp_storage set code = 'S'||fid; END;
create trigger "trg_ins_code_inp_junction" after insert on "inp_junction" BEGIN update inp_junction set code = 'J'||fid; END;
create trigger "trg_ins_code_inp_outfall" after insert on "inp_outfall" BEGIN update inp_outfall set code = 'O'||fid; END;
create trigger "trg_ins_code_inp_divider" after insert on "inp_divider" BEGIN update inp_divider set code = 'D'||fid; END;
create trigger "trg_ins_code_inp_inflow" after insert on "inp_inflow" BEGIN update inp_inflow set code = 'F'||fid; END;


----------------------------------------------------------------------------------------
-- SET node_1 AND node_2 TO ARCS BY PROXIMITY (conduits, pumps, outlets, orifices, weir)
-- -------------------------------------------------------------------------------------

---- inp_conduit
CREATE TRIGGER trg_ins_nodes_inp_conduit after INSERT ON inp_conduit FOR EACH ROW
BEGIN
    UPDATE inp_conduit SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_conduit AFTER UPDATE OF geom ON inp_conduit FOR EACH ROW
BEGIN
    UPDATE inp_conduit SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_weir
CREATE TRIGGER trg_ins_nodes_inp_weir after INSERT ON inp_weir FOR EACH ROW
BEGIN
    UPDATE inp_weir SET 
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_weir AFTER UPDATE OF geom ON inp_weir FOR EACH ROW
BEGIN
    UPDATE inp_weir SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_pump
CREATE TRIGGER trg_ins_nodes_inp_pump after INSERT ON inp_pump FOR EACH ROW
BEGIN
    UPDATE inp_pump SET 
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_pump AFTER UPDATE OF geom ON inp_pump FOR EACH ROW
BEGIN
    UPDATE inp_pump SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_orifice
CREATE TRIGGER trg_ins_nodes_inp_orifice after INSERT ON inp_orifice FOR EACH ROW
BEGIN
    UPDATE inp_orifice SET 
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_orifice AFTER UPDATE OF geom ON inp_orifice FOR EACH ROW
BEGIN
    UPDATE inp_orifice SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_outlet
CREATE TRIGGER trg_ins_nodes_inp_outlet after INSERT ON inp_outlet FOR EACH ROW
BEGIN
    UPDATE inp_outlet SET 
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_outlet AFTER UPDATE OF geom ON inp_outlet FOR EACH ROW
BEGIN
    UPDATE inp_outlet SET
        node_2 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT v_node.code FROM v_node WHERE ST_Intersects(ST_Buffer(v_node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


-- -------------------
-- ENABLE FOREIGN KEYS: enables insertion of data without using any restriction
-- -------------------

PRAGMA foreign_keys = OFF;
