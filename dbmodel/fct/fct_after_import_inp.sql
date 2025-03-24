/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/



-- ---------------------------------------
-- PASS THE CODE TO THE CUSTOM_CODE COLUMN
-- ---------------------------------------
UPDATE inp_outlet SET custom_code = code;
UPDATE inp_weir SET custom_code = code;
UPDATE inp_orifice SET custom_code = code;
UPDATE inp_pump SET custom_code = code;
UPDATE inp_conduit SET custom_code = code;
UPDATE inp_storage SET custom_code = code;
UPDATE inp_junction SET custom_code = code;
UPDATE inp_outfall SET custom_code = code;
UPDATE inp_divider SET custom_code = code;
UPDATE roof SET custom_code = code;
UPDATE ground SET custom_code = code;
UPDATE inlet SET custom_code = code;


-- -------------------
-- USE DRAIN CORE-CODE
-- -------------------
UPDATE inp_outlet SET code = 'T'||fid;
UPDATE inp_weir SET code = 'W'||fid
UPDATE inp_orifice SET code = 'R'||fid;
UPDATE inp_pump SET code = 'P'||fid;
UPDATE inp_conduit SET code = 'C'||fid;
UPDATE inp_storage SET code = 'S'||fid;
UPDATE inp_junction SET code = 'J'||fid;
UPDATE inp_outfall SET code = 'O'||fid;
UPDATE inp_divider SET code = 'D'||fid;
UPDATE roof SET code = 'RF'||fid;
UPDATE ground SET code = 'GR'||fid;
UPDATE inlet SET code = 'GR'||fid;
