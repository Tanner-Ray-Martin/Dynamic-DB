from __future__ import annotations
from sqlmodel import SQLModel, Field, create_engine

from datetime import datetime as dt, timedelta, date
from typing import Literal, Optional
from pydantic import (
    BaseModel,
    FieldSerializationInfo,
    field_serializer,
    Field as PydanticField,
    field_validator,
)
# from pydantic.functional_validators import WrapValidator

NOW: dt = dt.now() - timedelta(hours=25)
TODAY: date = NOW.date()
TODAY_STR = TODAY.strftime("%Y-%m-%d")
sqlite_url = f"sqlite:///database_db_{TODAY_STR}.sqlite3"

DATA_TYPES = Literal[
    "str", "int", "float", "bool", "date", "datetime", "time", "json", "list", "dict"
]


# Form Definition
class DbInfoForm(SQLModel):
    name: str = Field(
        title="Database Name",
        description="The common name for your database",
    )
    short_name: str = Field(
        title="Database Short Name",
        description="The short name for the database.",
    )
    display_name: str = Field(
        title="Database Display Name",
        description="The display name of the database.",
    )
    category: Optional[str] = Field(
        title="Database Category",
        description="Category of Database. For example, your department or the type of records.",
    )
    alias: Optional[str] = Field(
        title="Database Alias",
        description="What other people or systems might refer to your database or category as.",
    )
    description: Optional[str] = Field(
        title="Detailed Description",
        description="Write a detailed description of this database and its purpose.",
    )


# Model Definition That performs Validation
class DbInfo(DbInfoForm):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: dt = Field(default_factory=dt.now)
    updated_at: dt = Field(default_factory=dt.now)
    status: Optional[str] = Field(default="building", max_length=100)

    @field_serializer("created_at", "updated_at", when_used="always")
    def dt_to_json(self, v: dt, info: FieldSerializationInfo) -> str | dt:
        return v.replace(microsecond=0)


# Model with Table Configuration
class DbInfoModel(DbInfo, table=True):  # type: ignore
    ...


class TDBInfo(BaseModel):
    name: str
    short_name: str
    display_name: str
    category: str = ""
    alias: str = ""
    description: str = ""
    id: int
    created_at: dt
    updated_at: dt
    status: str | None = None


class FieldInfoForm(SQLModel):
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


class FieldInfo(FieldInfoForm):
    id: int = Field(default=None, primary_key=True)
    db_id: int = Field(default=None)
    created_at: dt = Field(default_factory=dt.now)
    updated_at: dt = Field(default_factory=dt.now)
    is_active: bool = Field(default=True)

    @field_serializer("created_at", "updated_at", when_used="always")
    def dt_to_json(self, v: dt, info: FieldSerializationInfo) -> str | dt:
        return v.replace(microsecond=0)


class FieldInfoModel(FieldInfo, table=True):  # type: ignore
    ...


class CreateTagsForm(SQLModel):
    tag_name: str = Field(
        title="Tag Name",
        description="The common name for your tag",
    )


class TagsInfo(CreateTagsForm, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)


class SelectTagForm(SQLModel):
    tag_name: list[str] = PydanticField(
        json_schema_extra={"search_url": "/forms/tags/search"}
    )

    @field_validator("tag_name", mode="before")
    @classmethod
    def correct_select_multiple(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, list):
            return v
        return [v]


class AddFieldForm(BaseModel): ...


class MethodNotAllowedResponse(BaseModel):
    detail: str = "Method Not Allowed"


# create the engine
db_engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(db_engine)
