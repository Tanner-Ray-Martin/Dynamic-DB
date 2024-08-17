from typing import Sequence
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    DbInfo,
    DbInfoModel,
    db_engine,
)

router = APIRouter()


@router.post(
    "/create",
    response_model=DbInfoModel,
    response_model_exclude_none=True,
    tags=["databases"],
    summary="Create basic information for a new database",
    description="Create a new database with the provided information.\ncreated_at, updated_at, and status are automatically set.",
)
async def api_create_database(new_db: DbInfoForm) -> DbInfoModel:
    db_info = DbInfo(**new_db.model_dump())
    with Session(db_engine) as session:
        db = DbInfoModel(**db_info.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
    return db


@router.get(
    "/read/{database_id}",
    response_model=DbInfoModel,
    tags=["databases"],
)
async def api_get_database(database_id: int) -> DbInfoModel:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")

    return db


@router.get(
    "/read",
    response_model=Sequence[DbInfoModel],
    tags=["databases"],
)
async def api_get_all_databases() -> Sequence[DbInfoModel]:
    with Session(db_engine) as session:
        # statement = select(DbInfo).where(DbInfo.status != "deleted")
        statement = select(DbInfoModel)
        dbs: Sequence[DbInfoModel] = session.exec(statement).all()

    return dbs


@router.put(
    "/update/{database_id}",
    response_model=DbInfoModel,
    response_model_exclude_none=True,
    tags=["databases"],
)
async def api_update_database(database_id: int, db: DbInfoForm) -> DbInfoModel:
    db_info = DbInfo(**db.model_dump(), db_id=database_id)
    with Session(db_engine) as session:
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        old_db: DbInfoModel | None = session.exec(statement).first()
        if old_db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        old_db.name = db_info.name
        old_db.description = db_info.description
        old_db.category = db_info.category
        old_db.updated_at = db_info.updated_at
        session.add(old_db)
        session.commit()
        session.refresh(old_db)

    return old_db


@router.delete(
    "/delete/{database_id}",
    response_model=DbInfoModel,
    tags=["databases"],
)
async def api_delete_database(database_id: int) -> DbInfoModel:
    with Session(db_engine) as session:
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        db.status = "deleted"
        session.add(db)
        session.commit()
        session.refresh(db)
    return db
