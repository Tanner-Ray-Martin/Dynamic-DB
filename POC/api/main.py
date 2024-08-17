from fastapi import APIRouter, FastAPI

from POC.api.routes.forms import field_forms, db_forms, tag_forms
from POC.api.routes.backend import field_apis, db_apis
from POC.api.routes import base

app = FastAPI(title="Dynamic-DB")
api_router = APIRouter()
api_router.include_router(db_apis.router, prefix="/api/databases", tags=["databases"])
api_router.include_router(field_apis.router, prefix="/api/fields", tags=["fields"])
api_router.include_router(
    db_forms.router,
    prefix="/forms/databases",
    tags=["databases"],
    include_in_schema=False,
)
api_router.include_router(
    field_forms.router,
    prefix="/forms/fields",
    tags=["fields"],
    include_in_schema=False,
)
api_router.include_router(
    tag_forms.router,
    prefix="/forms/tags",
    tags=["tags"],
    include_in_schema=False,
)

api_router.include_router(base.router, tags=["base"], include_in_schema=False)

app.include_router(api_router)
