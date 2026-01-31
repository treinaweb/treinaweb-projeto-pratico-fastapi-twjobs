from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from validate_docbr import CPF


class CandidateRequest(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=100)]
    email: EmailStr
    phone: Annotated[str, Field(min_length=11, max_length=11)]
    headline: Annotated[str, Field(min_length=10, max_length=150)]
    bio: Annotated[str, Field(min_length=50, max_length=1000)]
    cpf: Annotated[str, Field(min_length=11, max_length=11)]

    @field_validator("phone")
    def validate_phone(cls, value: str):
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        return value

    @field_validator("cpf")
    def validate_cpf(cls, value: str):
        if not value.isdigit():
            raise ValueError("CPF must contain only digits.")
        if not CPF().validate(value):
            raise ValueError("Invalid CPF number.")
        return value


class CandidateResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: str
    headline: str
    bio: str
    cpf: str


class SkillRequest(BaseModel):
    skills: list[int]


class SkillResponse(BaseModel):
    id: int
    name: str


class LinkResponse(BaseModel):
    id: int
    url: str
    link_type: str


class LinkRequest(BaseModel):
    url: HttpUrl
    link_type: Literal["linkedin", "github", "portfolio", "other"]
