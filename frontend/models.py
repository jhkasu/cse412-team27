"""SQLAlchemy models mirroring ddl/schema.sql.

The canonical schema lives in schema.sql and is loaded by setup_db.py.
We don't call Base.metadata.create_all() here.
"""
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserAccount(Base):
    __tablename__ = "user_account"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class FoodCategory(Base):
    __tablename__ = "food_category"
    category_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class UserPreference(Base):
    __tablename__ = "user_preference"
    preference_id = Column(Integer, primary_key=True)
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.user_id"))


class Food(Base):
    __tablename__ = "food"
    fdc_id = Column(Integer, primary_key=True)
    data_type = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("food_category.category_id"))
    category = relationship("FoodCategory")


class FoodNutrient(Base):
    __tablename__ = "food_nutrient"
    food_nutrient_id = Column(Integer, primary_key=True)
    nutrient = Column(String(255), nullable=False)
    amount = Column(Float)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id"))


class SavedComparisonFood(Base):
    __tablename__ = "saved_comparison_food"
    food_comparison_id = Column(Integer, primary_key=True)
    sort_order = Column(Integer, nullable=False)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id"))
    user_id = Column(Integer, ForeignKey("user_account.user_id"))
