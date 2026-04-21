"""Build the PostgreSQL DB from ../ddl/schema.sql + ../ddl/data.sql.

Connection settings can be overridden via env vars:
  PGHOST (default: localhost)
  PGPORT (default: 5432)
  PGUSER (default: postgres)
  PGPASSWORD (default: empty)
  PGDATABASE (default: nutricompare)

Run: python setup_db.py
"""
import os

import psycopg2
from psycopg2 import sql

HERE = os.path.dirname(os.path.abspath(__file__))
DDL_DIR = os.path.join(HERE, "..", "ddl")

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", os.environ.get("USER", "postgres"))
PG_PASSWORD = os.environ.get("PGPASSWORD", "")
PG_DATABASE = os.environ.get("PGDATABASE", "nutricompare")


def connect(dbname):
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, user=PG_USER,
        password=PG_PASSWORD, dbname=dbname,
    )


def recreate_database():
    """DROP + CREATE the target database (connect to 'postgres' to do this)."""
    conn = connect("postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(PG_DATABASE))
    )
    cur.execute(
        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(PG_DATABASE))
    )
    cur.close()
    conn.close()
    print(f"Recreated database '{PG_DATABASE}'.")


def load_sql_file(cur, path, label):
    with open(path, encoding="utf-8") as f:
        cur.execute(f.read())
    print(f"{label} loaded from {os.path.basename(path)}.")


def main():
    recreate_database()

    conn = connect(PG_DATABASE)
    cur = conn.cursor()

    load_sql_file(cur, os.path.join(DDL_DIR, "schema.sql"), "Schema")
    load_sql_file(cur, os.path.join(DDL_DIR, "data.sql"), "Data")
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM food")
    print(f"  food: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM food_category")
    print(f"  food_category: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM food_nutrient")
    print(f"  food_nutrient: {cur.fetchone()[0]}")

    cur.close()
    conn.close()
    print(f"DB ready: postgresql://{PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}")


if __name__ == "__main__":
    main()
