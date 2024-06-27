# crud.py
from sqlalchemy.orm import Session
from models import User
from schemas import UserUpdate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    user = get_user(db, user_id)
    if user:
        user.name = user_update.name
        user.email = user_update.email
        db.commit()
        db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user_create: UserUpdate):
    user = User(name=user_create.name, email=user_create.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

