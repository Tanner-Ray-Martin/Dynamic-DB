from sqlmodel import SQLModel, Field as SField
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DbInfoForm(BaseModel):
    name: str = Field(
        json_schema_extra={"placeholder": "My Database"},
        title="Database Name",
        description="The common name for your database",
    )
    short_name: str = SField(
        title="Database Short Name",
        description="The Short name for the database.",
        max_length=2,
    )
    display_name: str = SField(
        title="Database Display Name",
        description="The display name of the database",
        schema_extra={"placeholder": "My Database #1"},
    )
    category: Optional[str] = Field(
        title="Database Category",
        description="Category of Database. Like Your department, or the type of records.",
        json_schema_extra={"placeholder": "Warehouse"},
    )
    alias: Optional[str] = Field(
        title="Database Alias",
        description="What other people or systems might refer your database or category as.",
        examples=["inventory"],
    )
    description: Optional[str] = Field(
        title="Detailed Description",
        description="Write a detailed description of this database and what it is for.",
    )


class AddFieldForm(BaseModel):
    add_field: bool


# make a new fieldform the user can fill out to add a new field to the database
class FieldForm(BaseModel):
    name: str = Field(
        title="Field Name",
        description="The name of the field in the database",
        json_schema_extra={"placeholder": "My Field"},
    )
    data_type: Literal[
        "str",
        "int",
        "float",
        "bool",
        "date",
        "datetime",
        "time",
        "json",
        "list",
        "dict",
    ] = Field(
        title="Data Type",
        description="The type of data this field will store",
        json_schema_extra={"placeholder": "str"},
    )
    required: bool = Field(
        title="Required",
        description="Is this field required for the database?",
        json_schema_extra={"placeholder": True},
    )
    default: Optional[str] = Field(
        title="Default Value",
        description="The default value for this field in the database",
        json_schema_extra={"placeholder": "Default Value"},
    )
