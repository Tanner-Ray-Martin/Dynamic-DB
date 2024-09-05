from typing import Sequence
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime as dt
from POC.db.models.stock_models.db_models import (
    FieldInfoForm,
    FieldInfo,
    FieldInfoModel,
    DbInfoModel,
    db_engine,
)

router = APIRouter()


@router.post(
    "/create/{database_id}",
    response_model=FieldInfoModel,
    response_model_exclude_none=True,
    tags=["fields"],
)
async def api_create_field(form: FieldInfoForm, database_id: int) -> FieldInfoModel:
    field_info = FieldInfo(**form.model_dump(), db_id=database_id)
    with Session(db_engine) as session:
        db_statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db = session.exec(db_statement).first()
        if db is None:
            raise ValueError("Database not found")
        db.updated_at = dt.now()
        session.add(db)
        field = FieldInfoModel(**field_info.model_dump())
        field.db_id = database_id
        session.add(field)
        session.commit()
        session.refresh(field)

    return field


@router.get(
    "/read/{database_id}/{field_id}",
    response_model=FieldInfoModel,
    tags=["fields"],
)
async def api_get_field(database_id: int, field_id: int) -> FieldInfoModel:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(FieldInfoModel).where(
            FieldInfoModel.id == field_id and FieldInfoModel.db_id == database_id
        )
        db: FieldInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Field not found")
    return db


@router.get(
    "/read",
    response_model=Sequence[FieldInfoModel],
    tags=["fields"],
)
async def api_get_all_fields() -> Sequence[FieldInfoModel]:
    with Session(db_engine) as session:
        statement = select(FieldInfoModel).where(FieldInfoModel.is_active)
        dbs: Sequence[FieldInfoModel] = session.exec(statement).all()

    return dbs


@router.get(
    "/read/{database_id}",
    response_model=Sequence[FieldInfoModel],
    tags=["fields"],
)
async def api_get_fields(database_id: int) -> Sequence[FieldInfoModel]:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(FieldInfoModel).where(
            FieldInfoModel.db_id == database_id and FieldInfoModel.is_active
        )
        dbs: Sequence[FieldInfoModel] = session.exec(statement).all()
    return dbs


@router.put(
    "/update/{database_id}/{field_id}",
    response_model=FieldInfoModel,
    response_model_exclude_none=True,
    tags=["fields"],
)
async def api_update_field(
    database_id: int, field_id: int, field_form: FieldInfoForm
) -> FieldInfoModel:
    field_info = FieldInfo(**field_form.model_dump())
    with Session(db_engine) as session:
        db_statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db = session.exec(db_statement).first()
        if db is None:
            raise ValueError("Database not found")
        db.updated_at = dt.now()
        session.add(db)
        statement = select(FieldInfoModel).where(
            FieldInfoModel.id == field_id and FieldInfoModel.db_id == database_id
        )
        old_db: FieldInfoModel | None = session.exec(statement).first()
        if old_db is None:
            raise HTTPException(status_code=404, detail="Field not found")
        old_db.name = field_info.name
        old_db.data_type = field_info.data_type
        old_db.required = field_info.required
        old_db.default = field_info.default
        old_db.updated_at = field_info.updated_at
        session.add(old_db)
        session.commit()
        session.refresh(old_db)

    return old_db


@router.delete(
    "/delete/{database_id}/{field_id}",
    response_model=FieldInfo,
    tags=["fields"],
)
async def api_delete_field(database_id: int, field_id: int) -> FieldInfo:
    with Session(db_engine) as session:
        statement = select(FieldInfoModel).where(
            FieldInfoModel.id == field_id and FieldInfoModel.db_id == database_id
        )
        db: FieldInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Field not found")
        db.is_active = False
        session.add(db)
        session.commit()
        session.refresh(db)
    return db


@router.delete(
    "/delete/{database_id}",
    response_model=Sequence[FieldInfoModel],
    tags=["fields"],
)
async def api_delete_fields(database_id: int) -> Sequence[FieldInfoModel]:
    with Session(db_engine) as session:
        db_statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(db_statement).first()
        if db is None or db.status == "deleted":
            statement = select(FieldInfoModel).where(
                FieldInfoModel.db_id == database_id and FieldInfoModel.is_active
            )
            db_fields: Sequence[FieldInfoModel] = session.exec(statement).all()
            if db_fields is not None and len(db_fields) > 0:
                for field in db_fields:
                    field.is_active = False
                session.add_all(db_fields)
                session.commit()
    return db_fields
