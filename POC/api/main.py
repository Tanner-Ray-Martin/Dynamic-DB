from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastui import FastUI, prebuilt_html, components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel
from sqlmodel import Session
from POC.db.database import User, engine
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    DbInfo,
    FieldInfoForm,
    FieldInfo,
    AddFieldForm,
    db_engine,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    users = [
        User(id=1, name="John", dob=date(1990, 1, 1)),
        User(id=2, name="Jack", dob=date(1991, 1, 1)),
        User(id=3, name="Jill", dob=date(1992, 1, 1)),
        User(id=4, name="Jane", dob=date(1993, 1, 1)),
    ]
    with Session(engine) as session:
        for user in users:
            db_user = session.get(User, user.id)
            if db_user is not None:
                continue
            session.add(user)
        session.commit()
    yield


app = FastAPI(lifespan=lifespan)


class DeleteUserForm(BaseModel):
    confirm: bool


class Successful(BaseModel):
    success: bool


def get_success_button():
    return [
        c.Page(
            components=[
                c.Heading(text="Success!", level=2),
                c.Button(text="Home", on_click=GoToEvent(url="/")),
            ]
        )
    ]


@app.get(
    "/api/forms/create/database",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_new_database():
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
                            submit_url="/api/forms/create/database",
                        ),
                    ]
                ),
                c.Markdown(text="---"),
            ]
        )
    ]


@app.post(
    "/api/forms/create/database",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_database(form: Annotated[DbInfoForm, fastui_form(DbInfoForm)]):
    with Session(db_engine) as session:
        db = DbInfo(**form.model_dump())
        session.add(db)
        session.commit()
        database_id = db.id  # Get the newly created database id
    return [
        c.Text(text="Database Info Created!"),
        # make a simple view of the db info
        c.Heading(text="Database Info", level=3),
        c.Paragraph(text=f"Name: {db.name}"),
        c.Paragraph(text=f"Description: {db.description}"),
        c.Paragraph(text=f"Category: {db.category}"),
        c.Paragraph(text=f"Id: {db.id}"),
        c.Paragraph(text=f"Updated: {db.updated_at}"),
        c.Paragraph(text=f"Created: {db.created_at}"),
        c.Paragraph(text=f"Status: {db.status}"),
        c.Heading(
            text="New Field Info.",
            level=3,
            class_name="text-center",
        ),
        c.Markdown(text="---"),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url=f"/api/forms/create/databaseField/{database_id}",
        ),
    ]


@app.get(
    "/api/forms/create/databaseField/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_new_database_field(database_id: int):
    return [
        c.Heading(
            text="New Field Info.",
            level=3,
            class_name="text-center",
        ),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=FieldInfoForm,
            submit_url=f"/api/forms/create/databaseField/{database_id}",
        ),
    ]


@app.post(
    "/api/forms/create/databaseField/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_database_field(
    form: Annotated[FieldInfoForm, fastui_form(FieldInfoForm)], database_id: int
):
    with Session(db_engine) as session:
        db = FieldInfo(**form.model_dump(), db_id=database_id)
        session.add(db)
        session.commit()
        session.refresh(db)

    return [
        c.Text(text="Field Info Created!"),
        c.Markdown(text="---"),
        c.Paragraph(text="New Field Info."),
        c.Paragraph(text=f"Name: {db.name}"),
        c.Paragraph(text=f"Data Type: {db.data_type}"),
        c.Paragraph(text=f"Required: {db.required}"),
        c.Paragraph(text=f"Default: {db.default}"),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url=f"/api/forms/create/databaseField/{database_id}",
        ),
    ]


@app.get("/api/", response_class=RedirectResponse)
async def home_redirect_backend() -> RedirectResponse:
    return RedirectResponse("/openapi.json", status_code=302)


@app.get("/", response_class=RedirectResponse)
async def home_redirect() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=302)


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, reload=True)
