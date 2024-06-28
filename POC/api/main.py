# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine, Base
from db.models import UserModel, GenModel
from schemas.schemas import UserSchema, GenSchema
from db import crud

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_update: UserSchema, db: Session = Depends(get_db)):
    db_user = crud.update(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/all", response_model=list[UserSchema])
def get_all_users(db:Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return users

@app.post("/users/create", response_model=UserSchema)
def create_user(user_create:UserSchema,db:Session = Depends(get_db)):
    user = crud.create(db, user_create)
    return user
