
/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/

---------------------------------------------------
-- TRIGGERS TO CREATE AN AUTOINDEX FOR EACH ELEMENT
-- ------------------------------------------------
create trigger "trigger_insert_code_inp_subcatchment" after insert on "inp_subcatchment" BEGIN update inp_subcatchment set code = 'H'||fid; END;
create trigger "trigger_insert_code_inp_raingage" after insert on "inp_raingage" BEGIN update inp_raingage set code = 'RG'||fid; END;

create trigger "trigger_insert_code_inp_outlet" after insert on "inp_outlet" BEGIN update inp_outlet set code = 'T'||fid; END;
create trigger "trigger_insert_code_inp_weir" after insert on "inp_weir" BEGIN update inp_weir set code = 'W'||fid;END;
create trigger "trigger_insert_code_inp_orifice" after insert on "inp_orifice" BEGIN update inp_orifice set code = 'R'||fid; END;
create trigger "trigger_insert_code_inp_pump" after insert on "inp_pump" BEGIN update inp_pump set code = 'P'||fid; END;
create trigger "trigger_insert_code_inp_conduit" after insert on "inp_conduit" BEGIN update inp_conduit set code = 'C'||fid; END;
create trigger "trigger_insert_code_inp_storage" after insert on "inp_storage" BEGIN update inp_storage set code = 'S'||fid; END;
create trigger "trigger_insert_code_inp_junction" after insert on "inp_junction" BEGIN update inp_junction set code = 'J'||fid; END;
create trigger "trigger_insert_code_inp_outfall" after insert on "inp_outfall" BEGIN update inp_outfall set code = 'O'||fid; END;
create trigger "trigger_insert_code_inp_divider" after insert on "inp_divider" BEGIN update inp_divider set code = 'D'||fid; END;




-- -------------------
-- ENABLE FOREIGN KEYS: enables insertion of data without using any restriction
-- -------------------

PRAGMA foreign_keys = ON;
