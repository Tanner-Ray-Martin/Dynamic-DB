from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlmodel import Field, SQLModel, create_engine
from typing import Optional, Literal
from fastui import FastUI, AnyComponent, prebuilt_html
from pydantic import BaseModel, Field as DanticField

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

field_types = Literal[
    "string", "integer", "float", "date", "datetime", "relationship", "email", "phone"
]



class UserModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str


class User(BaseModel):
    id: Optional[int]
    name: str
    email: str


SQLModel.metadata.create_all(engine)


@app.get("/users/", response_model=FastUI, response_model_exclude_none=True)
def get_all_users() -> list[AnyComponent]:
    # return a table of all users
    ...


@app.get("/users/{user_id}", response_model=FastUI, response_model_exclude_none=True)
def read_user(user_id: int) -> list[AnyComponent]:
    # get user by id and return a fastui view of the users profile
    ...


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
