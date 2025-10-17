/*
This file is part of IberGIS project software
The program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This version of IberGIS is provided by IberGIS Team
*/

-- ----------------------------------------------
-- CREATE SYS GPKG TABLE IF NOT CREATED
-- ----------------------------------------------

CREATE TABLE IF NOT EXISTS gpkg_ogr_contents (
    table_name TEXT NOT NULL PRIMARY KEY,
    feature_count INTEGER DEFAULT NULL 
);