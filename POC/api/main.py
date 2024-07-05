from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional, Literal
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field as DanticField

app = FastAPI()
fast_ui = FastUI(app)

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

field_types = Literal["string", "integer", "float", "date", "datetime", "relationship", "email", "phone"]

class CreationModelField(SQLModel, table=True):
    field_name:str
    field_type:field_types
    access_level:int

class CreationModel(SQLModel, table=True):
    id: int
    model_name:str
    parent_names:list[str]
    child_names:list[str]
    basic_schema:list[CreationModelField]


class UserModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

class User(BaseModel):
    id: Optional[int] = DanticField(default=None, primary_key=True)
    name: str
    email: str

SQLModel.metadata.create_all(engine)

@app.get("/users/", response_model=FastUI, response_model_exclude_none=True)
def get_all_users()->list[AnyComponent]:
    # return a table of all users
    ...


@app.get("/users/{user_id}", response_model=FastUI, response_model_exclude_none=True)
def read_user(user_id: int) -> list[AnyComponent]:
    #get user by id and return a fastui view of the users profile
    ...


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='FastUI Demo'))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
