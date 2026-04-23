"""NutriCompare — DoorDash-style frontend for the USDA nutrition database.

Connection settings via env vars:
  PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

Run: uvicorn app:app --port 5001 --reload
"""
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from models import Food, FoodCategory, FoodNutrient

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", os.environ.get("USER", "postgres"))
PG_PASSWORD = os.environ.get("PGPASSWORD", "")
PG_DATABASE = os.environ.get("PGDATABASE", "nutricompare")

DATABASE_URL = (
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="NutriCompare")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def serialize_food(f: Food) -> dict:
    return {
        "fdc_id": f.fdc_id,
        "description": f.description,
        "data_type": f.data_type,
        "category_name": f.category.name if f.category else None,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/categories")
def categories(limit: int = 25, db: Session = Depends(get_db)):
    """Top categories by food count. Excludes 'Unknown' / 'Not included'."""
    rows = (
        db.query(
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
    return [
        {"category_id": r.category_id, "name": r.name, "food_count": r.food_count}
        for r in rows
    ]


@app.get("/api/foods")
def foods_by_category(category_id: int, db: Session = Depends(get_db)):
    foods = (
        db.query(Food)
        .filter(Food.category_id == category_id)
        .order_by(Food.description)
        .limit(100)
        .all()
    )
    return [serialize_food(f) for f in foods]


@app.get("/api/search")
def search(q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    if not q:
        return []
    foods = (
        db.query(Food)
        .filter(Food.description.ilike(f"%{q}%"))
        .order_by(Food.description)
        .limit(50)
        .all()
    )
    return [serialize_food(f) for f in foods]


@app.get("/api/food/{fdc_id}")
def food_detail(fdc_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, fdc_id)
    if not food:
        raise HTTPException(status_code=404, detail="not found")
    nutrients = (
        db.query(FoodNutrient)
        .filter(FoodNutrient.fdc_id == fdc_id)
        .order_by(FoodNutrient.nutrient)
        .all()
    )
    return {
        **serialize_food(food),
        "nutrients": [
            {"nutrient": n.nutrient, "amount": n.amount} for n in nutrients
        ],
    }
