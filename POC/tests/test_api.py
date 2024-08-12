from fastapi.testclient import TestClient
from json.decoder import JSONDecodeError
from POC.api.main import app
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    FieldInfoForm,
    DbInfo,
    FieldInfo,
    MethodNotAllowedResponse,
)

import pytest


client = TestClient(app)


@pytest.fixture
def db_info_form() -> DbInfoForm:
    return DbInfoForm(
        **{
            "name": "PyTestDB",
            "short_name": "PTDB",
            "display_name": "PyTest Database",
            "category": "PyTest",
            "alias": "PyTDB Alias",
            "description": "This is a py test database",
        }
    )


@pytest.fixture
def db_field_form() -> FieldInfoForm:
    return FieldInfoForm(
        **{
            "name": "TestField",
            "data_type": "string",
            "required": True,
            "default": "default_value",
        }
    )


@pytest.fixture
def frontend_url() -> str:
    return "/api/forms/"


@pytest.fixture
def backend_url() -> str:
    return "/api/backend/"


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("create/database", 200, list),
        ("create/database/does/not/exist", 400, JSONDecodeError),
        ("create/databaseField/1", 200, list),
        ("create/databaseField/does/not/exist", 400, JSONDecodeError),
    ],
)
def test_create_new_database(
    frontend_url: str, url: str, expected_status: int, expected_response: type
) -> None:
    if expected_status == 200:
        response = client.get(f"{frontend_url}{url}")
        data = response.json()
        assert isinstance(data, expected_response)
    else:
        with pytest.raises(expected_response):
            response = client.get(f"{frontend_url}{url}")
            data = response.json()


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("create/database", 200, list),
        ("create/database/does/not/exist", 405, dict),
    ],
)
def test_create_database(
    db_info_form: DbInfoForm,
    frontend_url: str,
    url: str,
    expected_status: int,
    expected_response: type,
) -> None:
    response = client.post(f"{frontend_url}{url}", data=db_info_form.model_dump())
    assert response.status_code == expected_status
    data = response.json()
    assert isinstance(data, expected_response)


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("create/databaseField/1", 200, list),
        ("create/databaseField/does/not/exist", 405, dict),
    ],
)
def test_create_database_field(
    db_field_form: FieldInfoForm,
    frontend_url: str,
    url: str,
    expected_status: int,
    expected_response: type,
) -> None:
    response = client.post(f"{frontend_url}{url}", data=db_field_form.model_dump())
    assert response.status_code == expected_status
    data = response.json()
    assert isinstance(data, expected_response)


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("read/database", 200, list),
        ("read/database/does/not/exist", 400, JSONDecodeError),
        ("read/database/1", 200, dict),
        ("read/database/1/does/not/exist", 400, JSONDecodeError),
        ("read/databaseField", 200, list),
        ("read/databaseField/does/not/exist", 400, JSONDecodeError),
    ],
)
def test_list_databases(
    backend_url: str, url: str, expected_status: int, expected_response: type
) -> None:
    if expected_status == 200:
        response = client.get(f"{backend_url}{url}")
        data = response.json()
        assert isinstance(data, expected_response)
    else:
        with pytest.raises(expected_response):
            response = client.get(f"{frontend_url}{url}")
            data = response.json()


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("update/database/1", 200, DbInfo),
        ("update/database/1/does/not/exist", 405, MethodNotAllowedResponse),
    ],
)
def test_update_database(
    db_info_form: DbInfoForm,
    backend_url: str,
    url: str,
    expected_status: int,
    expected_response: type,
) -> None:
    response = client.put(f"{backend_url}{url}", json=db_info_form.model_dump())
    assert response.status_code == expected_status
    data = response.json()
    expected_response(**data)


@pytest.mark.parametrize(
    "url, expected_status, expected_response",
    [
        ("update/databaseField/1/1", 200, FieldInfo),
        ("update/database/1/1/does/not/exist", 405, MethodNotAllowedResponse),
    ],
)
def test_update_database_field(
    db_field_form: FieldInfoForm,
    backend_url: str,
    url: str,
    expected_status: int,
    expected_response: type,
) -> None:
    response = client.put(f"{backend_url}{url}", json=db_field_form.model_dump())
    assert response.status_code == expected_status
    data = response.json()
    expected_response(**data)


### ADD DELETE TESTS ###


"""
# Finish Database Creation
def test_finish_database_creation(): ...
"""
