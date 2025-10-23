import sqlite3
import psycopg2
from psycopg2 import sql
import os

# === EDIT THESE ===
SQLITE_DB = "pms.db"
POSTGRES_URL = "postgresql://pms_db_y0d7_user:0ilfngw03Huds2gPPPd1ehM106Akx4yo@dpg-d3qalr56ubrc73fphnn0-a.render.com/pms_db_y0d7"

# === Connect to both databases ===
sqlite_conn = sqlite3.connect(SQLITE_DB)
pg_conn = psycopg2.connect(POSTGRES_URL)
pg_cur = pg_conn.cursor()

print("Connected to both databases successfully!")

# Get all tables from SQLite
sqlite_cur = sqlite_conn.cursor()
sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in sqlite_cur.fetchall() if t[0] != 'sqlite_sequence']

for table in tables:
    print(f"Transferring data from {table}...")

    # Get table columns
    sqlite_cur.execute(f"PRAGMA table_info({table});")
    columns = [info[1] for info in sqlite_cur.fetchall()]
    col_names = ", ".join(columns)

    # Read data from SQLite
    sqlite_cur.execute(f"SELECT {col_names} FROM {table};")
    rows = sqlite_cur.fetchall()

    if not rows:
        continue

    placeholders = ", ".join(["%s"] * len(columns))
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table),
        sql.SQL(col_names),
        sql.SQL(placeholders)
    )

    for row in rows:
        try:
            pg_cur.execute(insert_query, row)
        except Exception as e:
            print(f"Skipping row in {table}: {e}")

pg_conn.commit()
print("✅ Migration complete!")

sqlite_conn.close()
pg_cur.close()
pg_conn.close()
