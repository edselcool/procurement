import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

# ✅ Change if needed
SQLITE_PATH = 'pms.db'
POSTGRES_URL = "postgresql://pms_db_y0d7_user:0ilfngw03Huds2gPPPd1ehM106Akx4yo@dpg-d3qalr56ubrc73fphnn0-a/pms_db_y0d7"

# Connect to both databases
sqlite_conn = sqlite3.connect(SQLITE_PATH)
pg_conn = psycopg2.connect(POSTGRES_URL)

sqlite_cur = sqlite_conn.cursor()
pg_cur = pg_conn.cursor()

# List of tables in migration order (to respect foreign key dependencies)
tables = [
    "user",
    "supplier",
    "item",
    "purchase_request",
    "line_item",
    "purchase_order",
    "approval_log",
    "balance"
]

for table in tables:
    print(f"Migrating table: {table}")
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()

    if not rows:
        continue

    # Get column names dynamically
    col_names = [description[0] for description in sqlite_cur.description]
    columns = ", ".join(f'"{c}"' for c in col_names)
    placeholders = ", ".join(["%s"] * len(col_names))

    # Batch insert into PostgreSQL
    query = f'INSERT INTO "{table}" ({columns}) VALUES %s'
    try:
        execute_values(pg_cur, query, rows)
        pg_conn.commit()
    except Exception as e:
        print(f"❌ Error migrating {table}: {e}")
        pg_conn.rollback()

print("✅ Migration complete!")

sqlite_conn.close()
pg_conn.close()
