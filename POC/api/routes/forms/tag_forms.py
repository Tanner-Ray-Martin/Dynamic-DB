from __future__ import annotations as _annotations
from typing import Annotated
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.forms import (
    SelectSearchResponse,
    fastui_form,
    SelectOption,
)
from sqlmodel import Session, select
from POC.db.models.stock_models.db_models import (
    TagsInfo,
    db_engine,
    SelectTagForm,
    CreateTagsForm,
)

router = APIRouter()


@router.get("/search", response_model=SelectSearchResponse)
async def search_view() -> SelectSearchResponse:
    with Session(db_engine) as session:
        statement = select(TagsInfo)
        data = session.exec(statement).all()
        """for tag in data:
            tags[tag.tag_name].append({"value": tag.tag_name, "label": tag.tag_name})"""
        tags: list[SelectOption] = [
            SelectOption(value=tag.tag_name, label=tag.tag_name) for tag in data
        ]
        # options = [{"label": k, "options": v} for k, v in tags.items()]

    return SelectSearchResponse(options=tags)


@router.get("/select", response_model=FastUI, response_model_exclude_none=True)
def select_tags():
    return [
        c.Page(
            components=[
                c.Heading(text="Select Form", level=2, class_name="text-center"),
                c.Paragraph(
                    text="Form showing different ways of doing select.",
                    class_name="text-center",
                ),
                c.ModelForm(
                    model=SelectTagForm,
                    display_mode="page",
                    submit_url="/forms/tags/select",
                ),
            ]
        )
    ]


@router.post("/select", response_model=FastUI, response_model_exclude_none=True)
async def submit_selected_tags(
    form: Annotated[SelectTagForm, fastui_form(SelectTagForm)],
):
    all_tags: list[TagsInfo] = []
    for tag_name in form.tag_name:
        with Session(db_engine) as session:
            statement = select(TagsInfo).where(TagsInfo.tag_name == tag_name)
            data = session.exec(statement).all()
            all_tags.extend(data)

    return [c.Table(data=all_tags)]


@router.get("/create", response_model=FastUI, response_model_exclude_none=True)
def create_new_tag():
    return [
        c.Page(
            components=[
                c.ModelForm(
                    model=CreateTagsForm,
                    display_mode="page",
                    submit_url="/forms/tags/create",
                ),
            ]
        )
    ]


@router.post("/create", response_model=FastUI, response_model_exclude_none=True)
def submit_new_tag(
    form: Annotated[CreateTagsForm, fastui_form(CreateTagsForm)],
) -> list[AnyComponent]:
    with Session(db_engine) as session:
        db = TagsInfo(**form.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
    with Session(db_engine) as session:
        statement = select(TagsInfo)
        data = session.exec(statement).all()

    return [c.Text(text="Tag created successfully"), c.Table(data=data)]
