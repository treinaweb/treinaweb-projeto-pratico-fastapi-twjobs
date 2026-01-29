from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class SkillRequest(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]

    @field_validator("name")
    def normalize_name(cls, value: str):
        return value.strip().upper()


class SkillResponse(BaseModel):
    id: int
    name: str
