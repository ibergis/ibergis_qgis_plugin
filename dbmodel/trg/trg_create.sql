
/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/



---------------------------------------------------
-- TRIGGERS TO CREATE AN AUTOINDEX FOR EACH ELEMENT
-- ------------------------------------------------
create trigger "trg_ins_code_inp_outlet" AFTER INSERT on "inp_outlet" FOR EACH ROW BEGIN update inp_outlet set code = 'T'||fid; END;
create trigger "trg_ins_code_inp_weir" AFTER INSERT on "inp_weir" FOR EACH ROW BEGIN update inp_weir set code = 'W'||fid;END;
create trigger "trg_ins_code_inp_orifice" AFTER INSERT on "inp_orifice" FOR EACH ROW BEGIN update inp_orifice set code = 'R'||fid; END;
create trigger "trg_ins_code_inp_pump" AFTER INSERT on "inp_pump" FOR EACH ROW BEGIN update inp_pump set code = 'P'||fid; END;
create trigger "trg_ins_code_inp_conduit" AFTER INSERT on "inp_conduit" FOR EACH ROW BEGIN update inp_conduit set code = 'C'||fid; END;
create trigger "trg_ins_code_inp_storage" AFTER INSERT on "inp_storage" FOR EACH ROW BEGIN update inp_storage set code = 'S'||fid; END;
create trigger "trg_ins_code_inp_junction" AFTER INSERT on "inp_junction" FOR EACH ROW BEGIN update inp_junction set code = 'J'||fid; END;
create trigger "trg_ins_code_inp_outfall" AFTER INSERT on "inp_outfall" FOR EACH ROW BEGIN update inp_outfall set code = 'O'||fid; END;
create trigger "trg_ins_code_inp_divider" AFTER INSERT on "inp_divider" FOR EACH ROW BEGIN update inp_divider set code = 'D'||fid; END;
create trigger "trg_ins_code_roof" AFTER INSERT on "roof" FOR EACH ROW BEGIN update roof set code = 'RF'||fid; END;
create trigger "trg_ins_code_ground" AFTER INSERT on "ground" FOR EACH ROW BEGIN update ground set code = 'GR'||fid; END;
create trigger "trg_ins_code_inlet" AFTER INSERT on "inlet" FOR EACH ROW BEGIN UPDATE inlet SET code = 'IN'||fid; END;
create trigger "trg_ins_code_hyetograph" AFTER INSERT on "hyetograph" FOR EACH ROW BEGIN UPDATE hyetograph SET code = 'RG'||fid; END;
create trigger "trg_ins_code_culvert" AFTER INSERT on "culvert" FOR EACH ROW BEGIN UPDATE culvert SET code = 'CU'||fid; END;


------------------------------------------------
-- TRIGGERS TO MANAGE TOPOLOGY WITH FOREIGN KEYS
------------------------------------------------

-- nodes
CREATE TRIGGER trg_ins_inp_junction AFTER INSERT ON inp_junction FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_junction'); END;
CREATE TRIGGER trg_ins_inp_storage AFTER INSERT ON inp_storage FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_storage'); END;
CREATE TRIGGER trg_ins_inp_outfall AFTER INSERT ON inp_outfall FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_outfall'); END;
CREATE TRIGGER trg_ins_inp_divider AFTER INSERT ON inp_divider FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_divider'); END;
CREATE TRIGGER trg_ins_inp_inlet AFTER INSERT ON inlet FOR EACH ROW BEGIN INSERT INTO node (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inlet'); END;

CREATE TRIGGER trg_upd_code_inp_junction AFTER UPDATE of code on inp_junction FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_junction'; END;
CREATE TRIGGER trg_upd_code_inp_storage AFTER UPDATE of code on inp_storage FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_storage'; END;
CREATE TRIGGER trg_upd_code_inp_outfall AFTER UPDATE of code on inp_outfall FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_outfall'; END;
CREATE TRIGGER trg_upd_code_inp_divider AFTER UPDATE of code on inp_divider FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_divider'; END;
CREATE TRIGGER trg_upd_code_inp_inlet AFTER UPDATE of code on inlet FOR EACH ROW BEGIN update node set code = NEW.code where table_fid = NEW.fid and table_name = 'inlet'; END;

CREATE TRIGGER trg_del_inp_junction AFTER DELETE on inp_junction FOR EACH ROW BEGIN delete from node where code = OLD.code and table_name = 'inp_junction'; END;
CREATE TRIGGER trg_del_inp_storage AFTER DELETE on inp_storage FOR EACH ROW BEGIN delete from node where code = OLD.code and table_name = 'inp_storage'; END;
CREATE TRIGGER trg_del_inp_outfall AFTER DELETE on inp_outfall FOR EACH ROW BEGIN delete from node where code = OLD.code and table_name = 'inp_outfall'; END;
CREATE TRIGGER trg_del_inp_divider AFTER DELETE on inp_divider FOR EACH ROW BEGIN delete from node where code = OLD.code and table_name = 'inp_divider'; END;
CREATE TRIGGER trg_del_inp_inlet AFTER DELETE on inlet FOR EACH ROW BEGIN delete from node where code = OLD.code and table_name = 'inlet'; END;


-- arcs
CREATE TRIGGER trg_ins_inp_outlet AFTER INSERT ON inp_outlet FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_outlet'); END;
CREATE TRIGGER trg_ins_inp_weir AFTER INSERT ON inp_weir FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_weir'); END;
CREATE TRIGGER trg_ins_inp_orifice AFTER INSERT ON inp_orifice FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_orifice'); END;
CREATE TRIGGER trg_ins_inp_pump AFTER INSERT ON inp_pump FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_pump'); END;
CREATE TRIGGER trg_ins_inp_conduit AFTER INSERT ON inp_conduit FOR EACH ROW BEGIN INSERT INTO arc (table_fid, code, geom, table_name) VALUES (NEW.fid, NEW.code, NEW.geom, 'inp_conduit'); END;

CREATE TRIGGER trg_upd_code_inp_outlet AFTER UPDATE of code on inp_outlet FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_outlet'; END;
CREATE TRIGGER trg_upd_code_inp_weir AFTER UPDATE of code on inp_weir FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_weir'; END;
CREATE TRIGGER trg_upd_code_inp_orifice AFTER UPDATE of code on inp_orifice FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_orifice'; END;
CREATE TRIGGER trg_upd_code_inp_pump AFTER UPDATE of code on inp_pump FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_pump'; END;
CREATE TRIGGER trg_upd_code_inp_conduit AFTER UPDATE of code on inp_conduit FOR EACH ROW BEGIN update arc set code = NEW.code where table_fid = NEW.fid and table_name = 'inp_conduit'; END;

CREATE TRIGGER trg_del_inp_outlet AFTER DELETE on inp_outlet FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_outlet'; END;
CREATE TRIGGER trg_del_inp_orifice AFTER DELETE on inp_orifice FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_orifice'; END;
CREATE TRIGGER trg_del_inp_conduit AFTER DELETE on inp_conduit FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_conduit'; END;
CREATE TRIGGER trg_del_inp_weir AFTER DELETE on inp_weir FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_weir'; END;
CREATE TRIGGER trg_del_inp_pump AFTER DELETE on inp_pump FOR EACH ROW BEGIN delete from arc where code = OLD.code and table_name = 'inp_pump'; END;



--------------------------------------------------------------------------------------------------------------
-- TOPOCONTROL TRIGGERS: SET node_1 AND node_2 TO ARCS BY PROXIMITY (conduits, pumps, outlets, orifices, weir)
-- -----------------------------------------------------------------------------------------------------------

---- inp_conduit
CREATE TRIGGER trg_ins_nodes_inp_conduit AFTER INSERT ON inp_conduit FOR EACH ROW
BEGIN
    UPDATE inp_conduit SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_conduit AFTER UPDATE OF geom ON inp_conduit FOR EACH ROW
BEGIN
    UPDATE inp_conduit SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.1), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_weir
CREATE TRIGGER trg_ins_nodes_inp_weir AFTER INSERT ON inp_weir FOR EACH ROW
BEGIN
    UPDATE inp_weir SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_weir AFTER UPDATE OF geom ON inp_weir FOR EACH ROW
BEGIN
    UPDATE inp_weir SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_pump
CREATE TRIGGER trg_ins_nodes_inp_pump AFTER INSERT ON inp_pump FOR EACH ROW
BEGIN
    UPDATE inp_pump SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_pump AFTER UPDATE OF geom ON inp_pump FOR EACH ROW
BEGIN
    UPDATE inp_pump SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_orifice
CREATE TRIGGER trg_ins_nodes_inp_orifice AFTER INSERT ON inp_orifice FOR EACH ROW
BEGIN
    UPDATE inp_orifice SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_orifice AFTER UPDATE OF geom ON inp_orifice FOR EACH ROW
BEGIN
    UPDATE inp_orifice SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;


---- inp_outlet
CREATE TRIGGER trg_ins_nodes_inp_outlet AFTER INSERT ON inp_outlet FOR EACH ROW
BEGIN
    UPDATE inp_outlet SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE fid = NEW.fid;
END;

CREATE TRIGGER trg_upd_nodes_inp_outlet AFTER UPDATE OF geom ON inp_outlet FOR EACH ROW
BEGIN
    UPDATE inp_outlet SET
        node_2 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_EndPoint(NEW.geom)) LIMIT 1),
        node_1 = (SELECT node.code FROM node WHERE ST_Intersects(ST_Buffer(node.geom, 0.01), ST_StartPoint(NEW.geom)) LIMIT 1)
    WHERE geom = NEW.geom;
END;

PRAGMA foreign_keys = ON;
