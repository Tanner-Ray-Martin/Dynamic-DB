from typing import Annotated, Sequence
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
from fastui import FastUI, prebuilt_html, components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from sqlmodel import Session, select
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    DbInfo,
    FieldInfoForm,
    FieldInfo,
    AddFieldForm,
    DbInfoDisplay,
    db_engine,
)
import logging
from datetime import datetime as dt
from datetime import date
from datetime import time
from typing import Any
from pydantic import (
    BaseModel,
    model_validator,
)


logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)


class MyTestModel(BaseModel):
    dob: date = date.today()
    tob: time = time(5, 15, 30)
    dob_dt: dt = dt.now()
    name: str = "Tanner"

    @model_validator(mode="before")
    @classmethod
    def remove_ms_from_dt(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for field_name, field_value in data.items():
                if isinstance(field_value, dt):
                    data.update({field_name: field_value.replace(microsecond=0)})
            else:
                assert isinstance(data, dict)
        return data


app = FastAPI()


def get_success_button():
    return [
        c.Page(
            components=[
                c.Heading(text="Success!", level=2),
                c.Button(text="Home", on_click=GoToEvent(url="/")),
            ]
        )
    ]


### DATABASE CRUD ENDPOINTS


@app.get(
    "/api/forms/read/testmodel",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
    tags=["test"],
)
async def display_test_model():
    my_test_model = MyTestModel(dob_dt=dt.now())  # name="Hello")
    # my_test_model = MyTestModel(**my_test_model.model_dump())
    # my_test_model.dob = date(2024, 3, 28)
    # my_test_model = remove_ms_from_dt(my_test_model)
    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.ModelForm(
                            submit_url="/",
                            initial=my_test_model.model_dump(mode="json"),
                            model=MyTestModel,
                        )
                    ]
                )
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
async def submit_database_form(form: Annotated[DbInfoForm, fastui_form(DbInfoForm)]):
    with Session(db_engine) as session:
        db = DbInfo(**form.model_dump())
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
            submit_url=f"/api/forms/create/databaseField/{database_id}",
        ),
    ]


@app.post(
    "/api/backend/create/database",
    response_model=DbInfo,
    response_model_exclude_none=True,
    tags=["Database"],
)
async def api_create_database(new_db: DbInfoForm):
    with Session(db_engine) as session:
        db = DbInfo(**new_db.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
    return db


@app.get(
    "/api/forms/read/database/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def display_database(database_id: int):
    with Session(db_engine) as session:
        statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")

        display_db = DbInfoDisplay(**db.model_dump())

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
                            submit_url="/forms/read/database",
                            display_mode="inline",
                            initial=display_db.model_dump(mode="json"),  # mode="json"),
                            model=DbInfoDisplay,
                        ),
                    ]
                ),
            ]
        )
    ]


@app.get(
    "/api/backend/read/database/{database_id}",
    response_model=DbInfo,
    tags=["Database"],
)
async def api_get_database(database_id: int) -> DbInfo:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")

    return db


@app.get(
    "/api/forms/read/database",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def display_all_databases():
    with Session(db_engine) as session:
        # statement = select(DbInfo).where(DbInfo.status != "deleted")
        statement = select(DbInfo)
        dbs: Sequence[DbInfo] = session.exec(statement).all()

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
                            on_click=GoToEvent(url=f"/forms/read/database/{db.id}"),
                        ),
                    ]
                )
                for db in dbs
            ]
        )
    ]


@app.get(
    "/api/backend/read/database",
    response_model=Sequence[DbInfo],
    tags=["Database"],
)
async def api_get_all_databases() -> Sequence[DbInfo]:
    with Session(db_engine) as session:
        # statement = select(DbInfo).where(DbInfo.status != "deleted")
        statement = select(DbInfo)
        dbs: Sequence[DbInfo] = session.exec(statement).all()

    return dbs


@app.get(
    "/api/forms/update/database/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def get_update_database_form(database_id: int):
    with Session(db_engine) as session:
        statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(statement).first()
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
                            submit_url=f"/api/forms/update/database/{database_id}",
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


@app.post(
    "/api/forms/update/database/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def submit_update_database_form(
    database_id: int, form: Annotated[DbInfoForm, fastui_form(DbInfoForm)]
):
    with Session(db_engine) as session:
        statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        db.short_name = form.short_name
        db.display_name = form.display_name
        db.category = form.category
        db.alias = form.alias
        db.description = form.description
        db.updated_at = dt.now()
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


@app.put(
    "/api/backend/update/database/{database_id}",
    response_model=DbInfo,
    response_model_exclude_none=True,
    tags=["Database"],
)
async def api_update_database(database_id: int, db: DbInfoForm):
    with Session(db_engine) as session:
        statement = select(DbInfo).where(DbInfo.id == database_id)
        old_db: DbInfo | None = session.exec(statement).first()
        if old_db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        old_db.name = db.name
        old_db.description = db.description
        old_db.category = db.category
        session.add(old_db)
        session.commit()
        session.refresh(old_db)

    return old_db


@app.delete(
    "/api/backend/delete/database/{database_id}",
    response_model=DbInfo,
    tags=["Database"],
)
async def api_delete_database(database_id: int):
    with Session(db_engine) as session:
        statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Database not found")
        db.status = "deleted"
        session.add(db)
        session.commit()
        session.refresh(db)
    return db


### FIELD CRUD ENDPOINTS


@app.get(
    "/api/forms/create/databaseField/{database_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def get_field_form(database_id: int):
    return [
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
async def submit_field_form(
    field_form: Annotated[FieldInfoForm, fastui_form(FieldInfoForm)], database_id: int
):
    with Session(db_engine) as session:
        db_field = FieldInfo(**field_form.model_dump(), db_id=database_id)
        session.add(db_field)
        session.commit()
        session.refresh(db_field)
    with Session(db_engine) as session:
        field_statement = select(FieldInfo).where(FieldInfo.db_id == database_id)
        db_fields = session.exec(field_statement).all()
        display_db_fields = [FieldInfoForm(**field.model_dump()) for field in db_fields]

    return [
        c.Div(
            components=[
                c.Table(data=display_db_fields),
            ]
        ),
        c.ModelForm(
            loading=[c.Text(text="Submitting")],
            model=AddFieldForm,
            method="GET",
            submit_url=f"/api/forms/create/databaseField/{database_id}",
        ),
    ]


@app.post(
    "/api/backend/create/databaseField/{database_id}",
    response_model=FieldInfo,
    response_model_exclude_none=True,
    tags=["Field"],
)
async def api_create_field(form: FieldInfoForm, database_id: int):
    with Session(db_engine) as session:
        db = FieldInfo(**form.model_dump(), db_id=database_id)
        session.add(db)
        session.commit()
        session.refresh(db)

    return db


@app.get(
    "/api/backend/read/databaseField/{database_id}/{field_id}",
    response_model=FieldInfo,
    tags=["Field"],
)
async def api_get_field(database_id: int, field_id: int) -> FieldInfo:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(FieldInfo).where(
            FieldInfo.id == field_id and FieldInfo.db_id == database_id
        )
        db: FieldInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Field not found")
    return db


@app.get(
    "/api/backend/read/databaseField",
    response_model=Sequence[FieldInfo],
    tags=["Field"],
)
async def api_get_all_fields() -> Sequence[FieldInfo]:
    with Session(db_engine) as session:
        statement = select(FieldInfo).where(FieldInfo.is_active)
        dbs: Sequence[FieldInfo] = session.exec(statement).all()

    return dbs


@app.get(
    "/api/backend/read/databaseField/{database_id}",
    response_model=Sequence[FieldInfo],
    tags=["Field"],
)
async def api_get_fields(database_id: int) -> Sequence[FieldInfo]:
    with Session(db_engine) as session:
        # db: DbInfo = session.query(DbInfo).filter(DbInfo.id == database_id).first()
        statement = select(FieldInfo).where(
            FieldInfo.db_id == database_id and FieldInfo.is_active
        )
        dbs: Sequence[FieldInfo] = session.exec(statement).all()
    return dbs


@app.put(
    "/api/backend/update/databaseField/{database_id}/{field_id}",
    response_model=FieldInfo,
    response_model_exclude_none=True,
    tags=["Field"],
)
async def api_update_field(database_id: int, field_id: int, db: FieldInfoForm):
    with Session(db_engine) as session:
        statement = select(FieldInfo).where(
            FieldInfo.id == field_id and FieldInfo.db_id == database_id
        )
        old_db: FieldInfo | None = session.exec(statement).first()
        if old_db is None:
            raise HTTPException(status_code=404, detail="Field not found")
        old_db.name = db.name
        old_db.data_type = db.data_type
        old_db.required = db.required
        old_db.default = db.default

        session.add(old_db)
        session.commit()
        session.refresh(old_db)

    return old_db


@app.delete(
    "/api/backend/delete/databaseField/{database_id}/{field_id}",
    response_model=FieldInfo,
    tags=["Field"],
)
async def api_delete_field(database_id: int, field_id: int):
    with Session(db_engine) as session:
        statement = select(FieldInfo).where(
            FieldInfo.id == field_id and FieldInfo.db_id == database_id
        )
        db: FieldInfo | None = session.exec(statement).first()
        if db is None:
            raise HTTPException(status_code=404, detail="Field not found")
        db.is_active = False
        session.add(db)
        session.commit()
        session.refresh(db)
    return db


@app.delete(
    "/api/backend/delete/databaseField/{database_id}",
    response_model=Sequence[FieldInfo],
    tags=["Field"],
)
async def api_delete_fields(database_id: int) -> Sequence[FieldInfo]:
    with Session(db_engine) as session:
        db_statement = select(DbInfo).where(DbInfo.id == database_id)
        db: DbInfo | None = session.exec(db_statement).first()
        if db is None or db.status == "deleted":
            statement = select(FieldInfo).where(
                FieldInfo.db_id == database_id and FieldInfo.is_active
            )
            db_fields: Sequence[FieldInfo] = session.exec(statement).all()
            if db_fields is not None and len(db_fields) > 0:
                for field in db_fields:
                    field.is_active = False
                session.add_all(db_fields)
                session.commit()
    return db_fields


### DEFAULT ENDPOINTS AND REDIRECTS
@app.get(
    "/api/welcome",
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def welcome():
    form_routes: list[Route] = [
        route
        for route in app.routes
        if isinstance(route, Route)
        and "forms" in route.path
        and "{" not in route.path
        and route.methods is not None
        and "GET" in route.methods
    ]

    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Heading(
                            text=" ",
                        ),
                        c.Button(
                            text=route.name,
                            on_click=GoToEvent(url=route.path.replace("/api", "")),
                        ),
                    ]
                )
                for route in form_routes
            ]
        )
    ]


@app.get("/api/", response_class=RedirectResponse, tags=["Redirects"])
async def home_redirect_backend() -> RedirectResponse:
    return RedirectResponse("/openapi.json", status_code=302)


@app.get("/", response_class=RedirectResponse, tags=["Redirects"])
async def home_redirect() -> RedirectResponse:
    return RedirectResponse("/welcome", status_code=302)


@app.get("/{path:path}", tags=["FastUI HTML"])
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, reload=True)
