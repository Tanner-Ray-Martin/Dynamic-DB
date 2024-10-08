# POC/tests/test_db_models.py

from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    DbInfo,
    FieldInfoForm,
    FieldInfo,
)

import random

from datetime import datetime


def test_db_random() -> None:
    n = random.randint(1, 100)
    assert n >= 0 and n <= 101


def test_db_info_form_initialization() -> None:
    db_info_form = DbInfoForm(
        name="Test Database",
        short_name="TestDB",
        display_name="Test Database Display",
        category="Testing",
        alias="TDB",
        description="This is a test database.",
    )

    assert db_info_form.name == "Test Database"
    assert db_info_form.short_name == "TestDB"
    assert db_info_form.display_name == "Test Database Display"
    assert db_info_form.category == "Testing"
    assert db_info_form.alias == "TDB"
    assert db_info_form.description == "This is a test database."


def test_db_info_initialization() -> None:
    db_info = DbInfo(
        name="Test Database",
        short_name="TestDB",
        display_name="Test Database Display",
        category="Testing",
        alias="TDB",
        description="This is a test database.",
    )

    assert db_info.name == "Test Database"
    assert db_info.short_name == "TestDB"
    assert db_info.display_name == "Test Database Display"
    assert db_info.category == "Testing"
    assert db_info.alias == "TDB"
    assert db_info.description == "This is a test database."
    assert db_info.status == "building"
    assert isinstance(db_info.created_at, datetime)
    assert isinstance(db_info.updated_at, datetime)


def test_field_form_initialization() -> None:
    field_form = FieldInfoForm(
        name="Test Field", data_type="String", required=True, default="N/A"
    )

    assert field_form.name == "Test Field"
    assert field_form.data_type == "String"
    assert field_form.required is True
    assert field_form.default == "N/A"


def test_field_info_initialization() -> None:
    field_info = FieldInfo(
        name="Test Field", data_type="String", required=True, default="N/A", db_id=1
    )

    assert field_info.name == "Test Field"
    assert field_info.data_type == "String"
    assert field_info.required is True
    assert field_info.default == "N/A"
    assert field_info.db_id == 1
    assert isinstance(field_info.created_at, datetime)
    assert isinstance(field_info.updated_at, datetime)
