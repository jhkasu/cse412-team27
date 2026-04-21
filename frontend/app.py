"""NutriCompare — DoorDash-style frontend for the USDA nutrition database.

Connection settings via env vars (same as setup_db.py):
  PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
"""
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, g, jsonify, render_template, request

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", os.environ.get("USER", "postgres"))
PG_PASSWORD = os.environ.get("PGPASSWORD", "")
PG_DATABASE = os.environ.get("PGDATABASE", "nutricompare")

app = Flask(__name__)


def db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, user=PG_USER,
            password=PG_PASSWORD, dbname=PG_DATABASE,
        )
    return g.db


def query(sql, params=()):
    cur = db().cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/categories")
def categories():
    """Top categories by food count. Excludes 'Unknown' / 'Not included'."""
    limit = int(request.args.get("limit", 25))
    rows = query(
        """
        SELECT c.category_id, c.name, COUNT(f.fdc_id) AS food_count
        FROM food_category c
        JOIN food f ON f.category_id = c.category_id
        WHERE c.name NOT IN ('Unknown', 'Not included in a food category')
        GROUP BY c.category_id, c.name
        ORDER BY food_count DESC
        LIMIT %s
        """,
        (limit,),
    )
    return jsonify([dict(r) for r in rows])


@app.route("/api/foods")
def foods_by_category():
    category_id = request.args.get("category_id", type=int)
    if not category_id:
        return jsonify({"error": "category_id required"}), 400
    rows = query(
        """
        SELECT f.fdc_id, f.description, f.data_type, c.name AS category_name
        FROM food f
        JOIN food_category c ON c.category_id = f.category_id
        WHERE f.category_id = %s
        ORDER BY f.description
        LIMIT 100
        """,
        (category_id,),
    )
    return jsonify([dict(r) for r in rows])


@app.route("/api/search")
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    rows = query(
        """
        SELECT f.fdc_id, f.description, f.data_type, c.name AS category_name
        FROM food f
        LEFT JOIN food_category c ON c.category_id = f.category_id
        WHERE f.description ILIKE %s
        ORDER BY f.description
        LIMIT 50
        """,
        (f"%{q}%",),
    )
    return jsonify([dict(r) for r in rows])


@app.route("/api/food/<int:fdc_id>")
def food_detail(fdc_id):
    food = query(
        """
        SELECT f.fdc_id, f.description, f.data_type, c.name AS category_name
        FROM food f
        LEFT JOIN food_category c ON c.category_id = f.category_id
        WHERE f.fdc_id = %s
        """,
        (fdc_id,),
    )
    if not food:
        return jsonify({"error": "not found"}), 404
    nutrients = query(
        """
        SELECT nutrient, amount
        FROM food_nutrient
        WHERE fdc_id = %s
        ORDER BY nutrient
        """,
        (fdc_id,),
    )
    return jsonify({**dict(food[0]), "nutrients": [dict(n) for n in nutrients]})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
