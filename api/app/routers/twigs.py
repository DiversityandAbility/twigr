from typing import List
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.types import TIMESTAMP

from app import db

router = APIRouter()


class Twig(BaseModel):
    data: dict
    project: str = Field(
        None, max_length=64, title="The project this twig belongs to"
    )


class TwigOut(Twig):
    added_on: datetime


class ListFilters:
    def __init__(self, request: Request):
        self.filters = []
        for param, value in request.query_params.multi_items():
            try:
                if param == "project":
                    exp = db.twigs.c.project == value
                elif param == "added_on":
                    op, value = self.split_by_operator(value, "datetime")
                    value = self.convert(value, "datetime")
                    exp = db.twigs.c.added_on.op(op)(value)
                else:
                    exp = self.query_to_expression(param, value)
                if exp is not None:
                    self.filters.append(exp)
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unrecognised {param} parameter: {value}",
                )

    def query_to_expression(self, param, value):
        type_ = self.determine_field_type(param)
        col = db.twigs.c.data[param]
        col = self.cast_json_field(col, type_)
        op, value = self.split_by_operator(value, type_)
        value = self.convert(value, type_)
        return col.op(op)(value)

    def cast_json_field(self, col, type_):
        if type_ == "datetime":
            return col.astext.cast(TIMESTAMP(timezone=True))
        return col.astext

    def convert(self, value, type_):
        if type_ == "datetime":
            return datetime.fromisoformat(value)
        return value

    def determine_field_type(self, param):
        if ":" in param:
            return param.split(":", 1)[1]
        return "str"

    def split_by_operator(self, value, type_):
        if ":" in value:
            op, rest = value.split(":", 1)
            if op == "lte":
                return "<=", rest
            if op == "lt":
                return "<", rest
            if op == "gt":
                return ">", rest
            if op == "gte":
                return ">=", rest
            if op == "eq":
                return "=", rest
            if op == "like":
                return "ilike", f"%{rest}%"
        return self.default_op(value, type_)

    def default_op(self, value, type_):
        if type_ == "datetime":
            return "=", value
        return "ilike", f"%{value}%"


@router.get("/", response_model=List[TwigOut])
async def list_twigs(filters: ListFilters = Depends()):
    return await db.find_twigs(filters.filters)


@router.post("/", response_class=Response, status_code=201)
async def create_twig(twig: Twig, background: BackgroundTasks):
    background.add_task(save_twig, twig)
    return None


async def save_twig(twig: Twig):
    await db.create_twig(twig.dict())
