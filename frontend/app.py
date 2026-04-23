"""NutriCompare — DoorDash-style frontend for the USDA nutrition database.

Connection settings via env vars:
  PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
"""
import os

from flask import Flask, jsonify, render_template, request
from sqlalchemy import func

from models import Food, FoodCategory, FoodNutrient, db

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", os.environ.get("USER", "postgres"))
PG_PASSWORD = os.environ.get("PGPASSWORD", "")
PG_DATABASE = os.environ.get("PGDATABASE", "nutricompare")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def serialize_food(f):
    return {
        "fdc_id": f.fdc_id,
        "description": f.description,
        "data_type": f.data_type,
        "category_name": f.category.name if f.category else None,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/categories")
def categories():
    """Top categories by food count. Excludes 'Unknown' / 'Not included'."""
    limit = int(request.args.get("limit", 25))
    rows = (
        db.session.query(
            FoodCategory.category_id,
            FoodCategory.name,
            func.count(Food.fdc_id).label("food_count"),
        )
        .join(Food, Food.category_id == FoodCategory.category_id)
        .filter(FoodCategory.name.notin_(
            ["Unknown", "Not included in a food category"]
        ))
        .group_by(FoodCategory.category_id, FoodCategory.name)
        .order_by(func.count(Food.fdc_id).desc())
        .limit(limit)
        .all()
    )
    return jsonify([
        {"category_id": r.category_id, "name": r.name, "food_count": r.food_count}
        for r in rows
    ])


@app.route("/api/foods")
def foods_by_category():
    category_id = request.args.get("category_id", type=int)
    if not category_id:
        return jsonify({"error": "category_id required"}), 400
    foods = (
        Food.query.filter_by(category_id=category_id)
        .order_by(Food.description)
        .limit(100)
        .all()
    )
    return jsonify([serialize_food(f) for f in foods])


@app.route("/api/search")
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    foods = (
        Food.query.filter(Food.description.ilike(f"%{q}%"))
        .order_by(Food.description)
        .limit(50)
        .all()
    )
    return jsonify([serialize_food(f) for f in foods])


@app.route("/api/food/<int:fdc_id>")
def food_detail(fdc_id):
    food = db.session.get(Food, fdc_id)
    if not food:
        return jsonify({"error": "not found"}), 404
    nutrients = (
        FoodNutrient.query.filter_by(fdc_id=fdc_id)
        .order_by(FoodNutrient.nutrient)
        .all()
    )
    return jsonify({
        **serialize_food(food),
        "nutrients": [
            {"nutrient": n.nutrient, "amount": n.amount} for n in nutrients
        ],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
