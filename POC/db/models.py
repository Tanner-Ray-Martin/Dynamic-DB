# models.py
from sqlalchemy import Column, Integer, String
from database import Base


class UserModel(Base):
    __tablename__ = "user_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


class GenModel(Base):
    __tablename__ = "gen_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    display_name = Column(String, index=True, unique=True)
    description = Column(String, index=True)
