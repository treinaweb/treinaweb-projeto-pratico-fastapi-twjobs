from typing import Generic, TypeVar

from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: int
    name: str


class SkillListRequest(BaseModel):
    skills: list[int]


class CompanyResponse(BaseModel):
    user_id: int
    name: str
    email: str
    cnpj: str
    description: str
    size: str
    website: str


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    level: str
    employment_type: str
    salary_min: float | None
    salary_max: float | None
    location: str
    is_remote: bool
    status: str
    company: CompanyResponse
    skills: list[SkillResponse]


class CandidateResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone: str
    headline: str
    bio: str
    cpf: str
