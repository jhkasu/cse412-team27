"""NutriCompare — DoorDash-style frontend for the USDA nutrition database.

Connection settings via env vars:
  PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

Run: uvicorn app:app --port 5001 --reload
"""
import hashlib
import hmac
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from models import Food, FoodCategory, FoodNutrient, UserAccount

try:
    from pydantic import BaseModel, EmailStr
except ImportError:
    from pydantic.v1 import BaseModel, EmailStr

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


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    parts = encoded.split(":", 1)
    if len(parts) != 2:
        return False
    salt_hex, digest_hex = parts
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


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


@app.post("/api/signup")
def signup(payload: AuthRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password or ""
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    exists = db.query(UserAccount).filter(UserAccount.email == email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered.")
    user = UserAccount(email=email, password=_hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.user_id, "email": user.email}


@app.post("/api/signin")
def signin(payload: AuthRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password or ""
    user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if not user or not _verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"user_id": user.user_id, "email": user.email}


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
