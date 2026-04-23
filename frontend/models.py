"""SQLAlchemy models mirroring ddl/schema.sql.

These models are read-only mappers — the canonical schema lives in schema.sql
and is loaded by setup_db.py. We don't call db.create_all() here.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserAccount(db.Model):
    __tablename__ = "user_account"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class FoodCategory(db.Model):
    __tablename__ = "food_category"
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class UserPreference(db.Model):
    __tablename__ = "user_preference"
    preference_id = db.Column(db.Integer, primary_key=True)
    preference_key = db.Column(db.String(255), nullable=False)
    preference_value = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.user_id"))


class Food(db.Model):
    __tablename__ = "food"
    fdc_id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("food_category.category_id")
    )
    category = db.relationship("FoodCategory")


class FoodNutrient(db.Model):
    __tablename__ = "food_nutrient"
    food_nutrient_id = db.Column(db.Integer, primary_key=True)
    nutrient = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float)
    fdc_id = db.Column(db.Integer, db.ForeignKey("food.fdc_id"))


class SavedComparisonFood(db.Model):
    __tablename__ = "saved_comparison_food"
    food_comparison_id = db.Column(db.Integer, primary_key=True)
    sort_order = db.Column(db.Integer, nullable=False)
    fdc_id = db.Column(db.Integer, db.ForeignKey("food.fdc_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.user_id"))
