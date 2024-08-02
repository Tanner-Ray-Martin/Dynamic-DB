from sqlmodel import SQLModel, Field, create_engine
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


sqlite_url = "sqlite:///database_db.sqlite3"

DATA_TYPES = Literal[
    "str", "int", "float", "bool", "date", "datetime", "time", "json", "list", "dict"
]


class DbInfoForm(SQLModel):
    name: str = Field(
        title="Database Name",
        description="The common name for your database",
    )
    short_name: str = Field(
        title="Database Short Name",
        description="The Short name for the database.",
        max_length=10,
    )
    display_name: str = Field(
        title="Database Display Name",
        description="The display name of the database",
    )
    category: Optional[str] = Field(
        title="Database Category",
        description="Category of Database. Like Your department, or the type of records.",
    )
    alias: Optional[str] = Field(
        title="Database Alias",
        description="What other people or systems might refer your database or category as.",
    )
    description: Optional[str] = Field(
        title="Detailed Description",
        description="Write a detailed description of this database and what it is for.",
    )


class DbInfo(DbInfoForm, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    status: Optional[str] = Field(default="building", max_length=100)


# make a new fieldform the user can fill out to add a new field to the database


class FieldForm(SQLModel):
    name: str = Field(
        title="Field Name",
        description="The name of the field in the database",
    )
    data_type: str = Field(
        title="Data Type",
        description="The type of data this field will store",
    )
    required: bool = Field(
        title="Required",
        description="Is this field required for the database?",
    )
    default: str = Field(
        title="Default Value",
        description="The default value for this field in the database",
    )


class FieldInfo(FieldForm, table=True):
    id: int = Field(primary_key=True)
    db_id: int
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())


class AddFieldForm(BaseModel): ...


# create the engine
db_engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(db_engine)
