"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
import sqlite3

# Path to the GeoPackage file
gpkg_path = "C:\\Users\\Usuario\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\drain_plugin\\core\\i18n\\drain_i18n.gpkg"

# Connect to the GeoPackage
conn = sqlite3.connect(gpkg_path)
cursor = conn.cursor()
table_names = ["pydialog", "pymessage", "cat_language", "pytoolbar"]

for table_name in table_names:
    query = f"DROP TABLE IF EXISTS {table_name}"
    cursor.execute(query)

    if table_name == "pydialog":
        query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_code TEXT DEFAULT 'drain' CHECK (typeof(source_code) = 'text' OR source_code IS NULL),
                    toolbar_name TEXT CHECK (typeof(toolbar_name)='text' OR toolbar_name IS NULL),
                    dialog_name TEXT CHECK (typeof(dialog_name)='text' OR dialog_name IS NULL),
                    source TEXT CHECK (typeof(source)='text' OR source IS NULL),
                    lastupdate TEXT DEFAULT (datetime('now')),  -- ISO timestamp of last update
                    lastupdate_user TEXT CHECK (typeof(lastupdate_user)='text' OR lastupdate_user IS NULL),
                    lb_en_us TEXT CHECK (typeof(lb_en_us)='text' OR lb_en_us IS NULL),
                    tt_en_us TEXT CHECK (typeof(tt_en_us)='text' OR tt_en_us IS NULL),
                    UNIQUE (source_code, toolbar_name, dialog_name, source)
                );
                """
    elif table_name == "pymessage":
        query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_code TEXT DEFAULT 'drain' CHECK (typeof(source_code) = 'text' OR source_code IS NULL),
                        source TEXT CHECK (typeof(source)='text' OR source IS NULL),
                        lastupdate TEXT DEFAULT (datetime('now')),
                        lastupdate_user TEXT CHECK (typeof(lastupdate_user)='text' OR lastupdate_user IS NULL),
                        ms_en_us TEXT CHECK (typeof(ms_en_us)='text' OR ms_en_us IS NULL),
                        UNIQUE (source_code, source)  
                    );
                """
    elif table_name == "cat_language":
        query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id TEXT PRIMARY KEY,
                    language TEXT CHECK (typeof(language)='text' OR language IS NULL)
                );
                """
        cursor.execute(query)
        query = f"INSERT OR IGNORE INTO {table_name} (id, language) VALUES ('en_US', 'English (USA)')"

    elif table_name == "pytoolbar":
        query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_code TEXT DEFAULT 'drain' CHECK (typeof(source_code) = 'text' OR source_code IS NULL),
                        source TEXT CHECK (typeof(source)='text' OR source IS NULL),
                        lastupdate TEXT DEFAULT (datetime('now')),
                        lastupdate_user TEXT CHECK (typeof(lastupdate_user)='text' OR lastupdate_user IS NULL),
                        lb_en_us TEXT CHECK (typeof(lb_en_us)='text' OR lb_en_us IS NULL), 
                        UNIQUE (source_code, source) 
                    );
                """

    cursor.execute(query)

    query = f"""
            INSERT OR IGNORE INTO gpkg_contents (
                table_name, data_type, identifier, description, last_change
            ) VALUES (
                '{table_name}', 'attributes', '{table_name}', '', datetime('now')
            );
        """
    cursor.execute(query)

cursor.execute("SELECT * FROM gpkg_contents ;")

tables = cursor.fetchall()
print(tables)

conn.commit()
conn.close()