from fastapi.testclient import TestClient
from POC.api.main import app
from POC.db.models.stock_models.db_models import (
    DbInfoForm,
    FieldInfoForm,
)

client = TestClient(app)


# Test for GET /api/forms/create/database
def test_create_new_database():
    response = client.get("/api/forms/create/database")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["components"][0]["text"] == "Dynamic-DB"
    assert (
        data[0]["components"][1]["text"]
        == "Welcome! Here you will begin creating a new database."
    )
    assert (
        data[0]["components"][3]["components"][0]["text"]
        == "Step 1. Basic Database Information"
    )


# Test for POST /api/forms/create/database
def test_create_database():
    form_data = {
        "name": "TestDB",
        "short_name": "TDB",
        "display_name": "Test Database",
        "category": "Test",
        "alias": "TDB Alias",
        "description": "This is a test database",
    }
    db_info_form = DbInfoForm(**form_data)
    response = client.post("/api/forms/create/database", data=db_info_form.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data[0]["text"] == "Database Info Created!"
    assert data[1]["text"] == "Database Info"
    assert data[2]["text"] == "Name: TestDB"


# Test for GET /api/forms/create/databaseField/{database_id}
def test_create_new_database_field():
    database_id = 1
    response = client.get(f"/api/forms/create/databaseField/{database_id}")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["text"] == "New Field Info."
    assert data[1]["type"] == "ModelForm"


# Test for POST /api/forms/create/databaseField/{database_id}
def test_create_database_field():
    database_id = 1
    form_data = {
        "name": "TestField",
        "data_type": "string",
        "required": True,
        "default": "default_value",
    }
    db_field_form = FieldInfoForm(**form_data)
    response = client.post(
        f"/api/forms/create/databaseField/{database_id}",
        data=db_field_form.model_dump(),
    )
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data[3]["text"] == "Name: TestField"
    assert data[4]["text"] == "Data Type: string"
    assert data[5]["text"] == "Required: True"
    assert data[6]["text"] == "Default: default_value"
