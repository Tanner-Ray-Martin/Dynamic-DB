from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Table, Boolean
from sqlalchemy.orm import DeclarativeBase
from pydantic import create_model, BaseModel
import os

this_file_path = __file__

def pydantic_to_sqlalchemy(pydantic_model:BaseModel):
    ...

def schema_to_pydantic(schema:BaseModel):
    ...

