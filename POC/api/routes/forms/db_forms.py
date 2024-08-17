from typing import Annotated
from fastui import FastUI, components as c, AnyComponent
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from typing import Sequence
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    DbInfo,
    DbInfoModel,
    db_engine,
    AddFieldForm,
    FieldInfoModel,
)

router = APIRouter()


@router.get(
    "/create",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def create_new_database() -> list[AnyComponent]:
    print("creating new database form")
    return [
        c.Page(
            components=[
                c.Heading(text="Dynamic-DB", level=2),
                c.Paragraph(
                    text="Welcome! Here you will begin creating a new database."
                ),
                c.Markdown(text="---"),
                c.Div(
                    components=[
                        c.Heading(
                            text="Step 1. Basic Database Information",
                            level=3,
                            class_name="text-center",
                        ),
                        c.Markdown(text="---"),
                        c.ModelForm(
                            loading=[c.Text(text="Submitting")],
                            model=DbInfoForm,
                            submit_url="/forms/databases/create",
                        ),
                    ]
                ),
                c.Markdown(text="---"),
            ]
        )
    ]


@router.post(
    "/create",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def submit_database_form(
    form: Annotated[DbInfoForm, fastui_form(DbInfoForm)],
) -> list[AnyComponent]:
    with Session(db_engine) as session:
        valid_db = DbInfo(**form.model_dump())
        db = DbInfoModel(**valid_db.model_dump())
        session.add(db)
        session.commit()
        database_id = db.id  # Get the newly created database id
    return [
        c.Paragraph(text=f"Name: {db.name}"),
        c.Paragraph(text=f"Description: {db.description}"),
        c.Paragraph(text=f"Category: {db.category}"),
        c.Paragraph(text=f"Id: {db.id}"),
        c.Paragraph(text=f"Updated: {db.updated_at}"),
        c.Paragraph(text=f"Created: {db.created_at}"),
        c.Paragraph(text=f"Status: {db.status}"),
        c.Heading(
            text=" ",
            level=3,
            class_name="text-center",
        ),
        c.Markdown(text="---"),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url=f"/forms/fields/create/{database_id}",
        ),
    ]


@router.get(
    "/read/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def display_database(database_id: int) -> list[AnyComponent]:
    with Session(db_engine) as session:
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")

        display_db = DbInfo(**db.model_dump())
        fields_statement = select(FieldInfoModel).where(
            FieldInfoModel.db_id == database_id
        )
        db_fields = session.exec(fields_statement).all()

    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Heading(
                            text=f"Database: {display_db.display_name}",
                            level=3,
                            class_name="text-center",
                        ),
                        c.Heading(
                            text=" ",
                            level=3,
                            class_name="text-center",
                        ),
                        c.Markdown(text="---"),
                        c.ModelForm(
                            submit_url="/forms/databases/read",
                            display_mode="inline",
                            initial=display_db.model_dump(mode="json"),  # mode="json"),
                            model=DbInfo,
                        ),
                        c.Heading(
                            text=f"{display_db.display_name}: Fields",
                            level=3,
                            class_name="text-center",
                        ),
                        c.Heading(
                            text=" ",
                            level=3,
                            class_name="text-center",
                        ),
                        c.Markdown(text="---"),
                        c.Table(data=db_fields)
                        if db_fields
                        else c.Text(text="No fields found"),
                    ]
                ),
            ]
        )
    ]


@router.get(
    "/read",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def display_all_databases() -> list[AnyComponent]:
    with Session(db_engine) as session:
        # statement = select(DbInfo).where(DbInfo.status != "deleted")
        statement = select(DbInfoModel)
        dbs: Sequence[DbInfoModel] = session.exec(statement).all()

    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Heading(
                            text=" ",
                        ),
                        c.Button(
                            text=db.name,
                            on_click=GoToEvent(url=f"/databases/read/{db.id}"),
                        ),
                    ]
                )
                for db in dbs
            ]
        )
    ]


@router.get(
    "/update/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def get_update_database_form(database_id: int) -> list[AnyComponent]:
    with Session(db_engine) as session:
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        if db is not None:
            db_info: DbInfoForm = DbInfoForm(**db.model_dump())

    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Markdown(text="---"),
                        c.ModelForm(
                            submit_url=f"/forms/databases/update/{database_id}",
                            initial=db_info.model_dump(),
                            loading=[c.Text(text="Submitting")],
                            model=DbInfoForm,
                        ),
                    ]
                ),
                c.Markdown(text="---"),
            ]
        )
    ]


@router.post(
    "/update/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def submit_update_database_form(
    database_id: int, form: Annotated[DbInfoForm, fastui_form(DbInfoForm)]
) -> list[AnyComponent]:
    db_info = DbInfo(**form.model_dump())
    with Session(db_engine) as session:
        statement = select(DbInfoModel).where(DbInfoModel.id == database_id)
        db: DbInfoModel | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")

        db.short_name = db_info.short_name
        db.display_name = db_info.display_name
        db.category = db_info.category
        db.alias = db_info.alias
        db.description = db_info.description
        db.updated_at = db_info.updated_at
        session.add(db)
        session.commit()
        session.refresh(db)
    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Heading(text=f"Updated: {db.name}", level=3),
                        c.Table(data=[db]),
                    ]
                ),
            ]
        )
    ]
