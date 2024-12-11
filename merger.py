import sqlite3
import os

def merge_databases(out_db, in_db1, in_db2):
    # Connect to output database
    conn_out = sqlite3.connect(out_db)
    
    # Attach input databases
    conn_out.execute("ATTACH '{}' AS db1".format(in_db1))
    conn_out.execute("ATTACH '{}' AS db2".format(in_db2))
    
    # Get list of tables in the first database
    cursor_out = conn_out.cursor()
    cursor_out.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor_out.fetchall()]
    
    # Copy tables from db2 to out_db
    for table in tables:
        cursor_out.execute("INSERT OR REPLACE INTO {} SELECT * FROM db2.{}".format(table, table))
    
    # Detach attached databases
    conn_out.execute("DETACH DATABASE db1")
    conn_out.execute("DETACH DATABASE db2")
    
    conn_out.commit()
    conn_out.close()

# Usage
out_db = "merged_database.sqlite3"
in_db1 = "emails-2018.sqlite3"
in_db2 = "emails-2019.sqlite3"

merge_databases(out_db, in_db1, in_db2)
