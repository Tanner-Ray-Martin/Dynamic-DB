from fastui.events import GoToEvent
from fastui import FastUI, prebuilt_html, components as c, AnyComponent
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
from POC.api.routes.forms.db_forms import router as form_db_router
from POC.api.routes.forms.field_forms import router as form_field_router
from POC.api.routes.forms.tag_forms import router as form_tag_router

all_routes = [
    ("/databases" + route.path, route.name)
    for route in form_db_router.routes
    if isinstance(route, Route)
    and route.methods is not None
    and "GET" in route.methods
    and "{" not in route.path
]
all_routes.extend(
    [
        ("/fields" + route.path, route.name)
        for route in form_field_router.routes
        if isinstance(route, Route)
        and route.methods is not None
        and "GET" in route.methods
        and "{" not in route.path
    ]
)
all_routes.extend(
    [
        ("/tags" + route.path, route.name)
        for route in form_tag_router.routes
        if isinstance(route, Route)
        and route.methods is not None
        and "GET" in route.methods
        and "{" not in route.path
    ]
)
router = APIRouter()


### DEFAULT ENDPOINTS AND REDIRECTS
@router.get("/forms/welcome", response_model=FastUI, response_model_exclude_none=True)
async def welcome() -> list[AnyComponent]:
    """form_routes: list[Route] = [
        route
        for route in router.routes
        if isinstance(route, Route)
        and "forms" in route.path
        and "{" not in route.path
        and route.methods is not None
        and "GET" in route.methods
    ]"""

    return [
        c.Page(
            components=[
                c.Div(
                    components=[
                        c.Heading(
                            text=" ",
                        ),
                        c.Button(
                            text=route[1].replace("_", " ").title(),
                            on_click=GoToEvent(url=route[0]),
                        ),
                    ]
                )
                for route in all_routes
            ]
        )
    ]


@router.get("/api/", response_class=RedirectResponse)
async def home_redirect_backend() -> RedirectResponse:
    return RedirectResponse("/openapi.json", status_code=302)


@router.get("/", response_class=RedirectResponse)
async def home_redirect() -> RedirectResponse:
    return RedirectResponse("/welcome", status_code=302)


@router.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo", api_root_url="/forms"))
