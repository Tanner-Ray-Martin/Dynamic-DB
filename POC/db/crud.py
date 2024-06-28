# crud.py
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from models import UserModel, GenModel
from api.schemas.schemas import UserSchema, GenSchema
from pydantic import BaseModel

model_schema_map = {
    "user": {"model": UserModel, "schema": UserSchema},
    "gen": {"model": GenModel, "schema": GenSchema},
}

def get_model(model_schema_name:str)->DeclarativeMeta:
    ms_map = model_schema_map.get(model_schema_name)
    if ms_map:
        return ms_map.get('model')
    
def get_schema(model_schema_name:str)->BaseModel:
    ms_map = model_schema_map.get(model_schema_name)
    if ms_map:
        return ms_map.get('schema')
    
def get_model_and_schema(model_schema_name:str):
    return get_model(model_schema_name), get_schema(model_schema_name)

def create(db: Session, schema: UserSchema | GenSchema):
    if isinstance(schema, UserSchema):
        model = UserModel
    elif isinstance(schema, GenSchema):
        model = GenModel
    new_model = model(**schema.model_dump())
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model


def read(db: Session, id: int, model_schema_name: str):
    model, schema = get_model_and_schema(model_schema_name)
    existing_model = db.query(model).filter(model.id == id).first()
    return existing_model


def update(db: Session, id: int, schema: UserSchema | GenSchema): ...


def delete(db: Session, id: int, schema: UserSchema | GenSchema): ...
