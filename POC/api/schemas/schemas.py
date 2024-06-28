# schemas.py
from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str

class GenSchema(BaseModel):
    name:str
    display_name:str
    description:str