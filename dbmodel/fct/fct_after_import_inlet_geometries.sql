/*
This file is part of drain project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of Giswater is provided by Giswater Association
*/


-- -------------------
-- USE DRAIN CORE-CODE
-- -------------------
UPDATE inlet SET code = 'IN'||fid;
UPDATE pinlet SET code = 'PI'||fid;