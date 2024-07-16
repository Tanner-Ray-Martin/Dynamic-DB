from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel
from sqlmodel import Session, select
from POC.db.database import User, UserForm, engine
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    FieldForm,
    AddFieldForm,
    db_engine,
    DbInfo,
    FieldInfo,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # define some users
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
                c.Heading(text="Succsess!", level=2),
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


@app.get(
    "/api/forms/create/databaseField",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_new_database_field():
    return [
        c.Heading(
            text="New Field Info.",
            level=3,
            class_name="text-center",
        ),
        c.ModelForm(
            display_mode="default",
            loading=[c.Text(text="Submitting")],
            model=FieldForm,
            submit_url="/api/forms/create/databaseField",
        ),
    ]


@app.get(
    "/api/forms/create/user",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def add_user():
    return [
        c.Page(
            components=[
                c.Heading(text="Add User", level=2),
                c.Paragraph(text="Add a user to the system"),
                c.ModelForm(
                    loading=[c.Text(text="Submitting")],
                    display_mode="default",
                    model=UserForm,
                    submit_url="/api/forms/create/user",
                ),
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
    return [
        c.Text(text="Database Info Created!"),
        c.Markdown(text="---"),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url="/api/forms/create/databaseField",
        ),
    ]


@app.post(
    "/api/forms/create/databaseField",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def create_database_field(form: Annotated[FieldForm, fastui_form(FieldForm)]):
    with Session(db_engine) as session:
        field = FieldInfo(**form.model_dump())
        session.add(field)
        session.commit()
    return [
        c.Text(text="Field Info Created!"),
        c.Markdown(text="---"),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url="/api/forms/create/databaseField",
        ),
    ]


@app.post(
    "/api/forms/create/user",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def add_user_submit(
    form: Annotated[UserForm, fastui_form(UserForm)],
):
    user_id = None
    with Session(engine) as session:
        user = User(**form.model_dump())
        session.add(user)
        session.commit()
        user_id = user.id
    return [c.FireEvent(event=GoToEvent(url=f"/forms/read/user/{user_id}"))]


@app.post("/api/backend/create/user", response_model=User)
async def add_user_submit_backend(form: UserForm):
    with Session(engine) as session:
        user = User(**form.model_dump())
        session.add(user)
        session.commit()
    return user


@app.get(
    "/api/forms/read/user",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def users_table() -> list[AnyComponent]:
    with Session(engine) as session:
        users = session.exec(select(User)).all()

    return [
        c.Page(  # Page provides a basic container for components
            components=[
                c.Heading(text="Users", level=2),  # renders `<h2>Users</h2>`
                c.Table(  # c.Table is a generic component parameterized with the model used for rows
                    data=users,
                    # define two columns for the table
                    columns=[
                        # the first is the users, name rendered as a link to their profile
                        DisplayLookup(
                            field="name",
                            on_click=GoToEvent(url="/forms/read/user/{id}"),
                        ),
                        # the second is the date of birth, rendered as a date
                        DisplayLookup(field="dob", mode=DisplayMode.date),
                    ],
                ),
                c.Div(
                    components=[
                        c.Link(
                            components=[c.Button(text="Add User")],
                            on_click=GoToEvent(url="/forms/create/user"),
                        ),
                    ]
                ),
            ]
        ),
    ]


@app.get("/api/backend/read/user", response_model=list[User])
async def users_table_backend() -> list[User]:
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users


@app.get(
    "/api/forms/read/user/{user_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def user_profile(user_id: int) -> list[AnyComponent]:
    """
    User profile page, the frontend will fetch this when the user visits `/user/{id}/`.
    """
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            return [c.FireEvent(event=GoToEvent(url="/forms/read/user"))]

    return [
        c.Page(
            components=[
                c.Heading(text=user.name, level=2),
                c.Link(
                    components=[c.Text(text="Back")],
                    on_click=GoToEvent(url="/forms/read/user"),
                ),
                c.Details(data=user),
                c.Div(
                    components=[
                        c.Heading(text="Delete User?", level=4),
                        c.ModelForm(
                            loading=[c.Text(text="Submitting")],
                            model=DeleteUserForm,
                            submit_url=f"/api/forms/delete/user/{user_id}",
                            method="POST",
                            class_name="text-left",
                        ),
                    ],
                    class_name="card p-4 col-4",
                ),
            ]
        ),
    ]


@app.get("/api/backend/read/user/{user_id}", response_model=User)
async def user_profile_backend(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post(
    "/api/forms/delete/user/{user_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def delete_user(user_id: int):
    """
    Handle user deletion and redirect to the user list page.
    """
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(user)
        session.commit()
    return [c.FireEvent(event=GoToEvent(url="/forms/read/user"))]


@app.post("/api/backend/delete/user/{user_id}", response_model=Successful)
async def delete_user_backend(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is not None:
            session.delete(user)
            session.commit()
    return Successful(success=True)


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
