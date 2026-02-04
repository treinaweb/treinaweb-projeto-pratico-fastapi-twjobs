from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from twjobs.api.common.schemas import CompanyResponse, SkillResponse

LevelOptions = Literal["junior", "mid", "senior"]
EmploymentTypeOptions = Literal["clt", "pj", "freelancer", "internship"]


class JobRequest(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str, Field(min_length=10)]
    level: LevelOptions
    employment_type: EmploymentTypeOptions
    salary_min: Annotated[float | None, Field(ge=0)] = None
    salary_max: Annotated[float | None, Field(ge=0)] = None
    location: Annotated[str, Field(min_length=3, max_length=100)]
    is_remote: bool

    @model_validator(mode="after")
    def check_salaries(self):
        if self.salary_min is not None and self.salary_max is None:
            raise ValueError(
                "salary_max must be provided if salary_min is provided"
            )

        if self.salary_max is not None and self.salary_min is None:
            raise ValueError(
                "salary_min must be provided if salary_max is provided"
            )

        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_max < self.salary_min:
                raise ValueError(
                    "salary_max must be greater than or equal to salary_min"
                )

        return self


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


class JobFilters(BaseModel):
    page: Annotated[int, Field(gt=0)] = 1
    size: Annotated[int, Field(gt=0, le=100)] = 20
    search: str | None = None
    level: LevelOptions | None = None
    employment_type: EmploymentTypeOptions | None = None
    is_remote: bool | None = None
    company_id: int | None = None
    status: Literal["open", "close"] | None = None
    skills: list[int] | None = None
    order_by: Literal[
        "id", "title", "salary_min", "salary_max", "created_at"
    ] = "id"
    order_dir: Literal["asc", "desc"] = "asc"
