from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from twjobs.api.common.schemas import SkillResponse


class SkillRequest(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]

    @field_validator("name")
    def normalize_name(cls, value: str):
        return value.strip().upper()


class PaginatedSkillResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[SkillResponse]


class SkillFilters(BaseModel):
    page: Annotated[int, Field(gt=0)] = 1
    size: Annotated[int, Field(gt=0, le=100)] = 20
    search: str | None = None
    order_by: Literal["id", "name"] = "name"
    order_dir: Literal["asc", "desc"] = "asc"
