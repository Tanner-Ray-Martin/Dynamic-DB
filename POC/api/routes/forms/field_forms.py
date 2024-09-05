from typing import Annotated
from fastui import FastUI, components as c, AnyComponent
from fastui.forms import fastui_form
from fastapi import APIRouter
from sqlmodel import Session, select
from datetime import datetime as dt
from POC.db.models.stock_models.db_models import (
    FieldInfoForm,
    FieldInfo,
    FieldInfoModel,
    db_engine,
    AddFieldForm,
    DbInfoModel,
)

router = APIRouter()


@router.get(
    "/create/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def get_field_form(database_id: int) -> list[AnyComponent]:
    return [
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=FieldInfoForm,
            submit_url=f"/forms/fields/create/{database_id}",
        ),
    ]


@router.post(
    "/create/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def submit_field_form(
    field_form: Annotated[FieldInfoForm, fastui_form(FieldInfoForm)], database_id: int
) -> list[AnyComponent]:
    with Session(db_engine) as session:
        db_statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db = session.exec(db_statement).first()
        if db is None:
            raise ValueError("Database not found")
        db.updated_at = dt.now()
        session.add(db)
        field_info = FieldInfo(**field_form.model_dump())
        field_info.db_id = database_id
        db_field = FieldInfoModel(**field_info.model_dump())
        session.add(db_field)
        session.commit()
        session.refresh(db_field)
    with Session(db_engine) as session:
        field_statement = select(FieldInfoModel).where(
            FieldInfoModel.db_id == database_id
        )
        db_fields = session.exec(field_statement).all()
        display_db_fields = [FieldInfoForm(**field.model_dump()) for field in db_fields]

    return [
        c.Div(
            components=[
                c.Table(data=display_db_fields)
                if len(display_db_fields) > 0
                else c.Text(text="No fields found"),
            ]
        ),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url=f"/forms/fields/create/{database_id}",
        ),
    ]


@router.get(
    "/read",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def display_all_fields() -> list[AnyComponent]:
    with Session(db_engine) as session:
        field_statement = select(FieldInfoModel)
        db_fields = session.exec(field_statement).all()

    return [
        c.Div(
            components=[
                c.Table(data=db_fields)
                if len(db_fields) > 0
                else c.Text(text="No fields found"),
            ]
        ),
    ]


@router.get(
    "/read/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def display_database_fields(database_id: int) -> list[AnyComponent]:
    with Session(db_engine) as session:
        field_statement = select(FieldInfoModel).where(
            FieldInfoModel.db_id == database_id
        )
        db_fields = session.exec(field_statement).all()

    return [
        c.Div(
            components=[
                c.Table(data=db_fields)
                if len(db_fields) > 0
                else c.Text(text="No fields found"),
            ]
        ),
    ]
