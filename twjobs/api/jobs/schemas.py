from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class JobRequest(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str, Field(min_length=10)]
    level: Literal["junior", "mid", "senior"]
    employment_type: Literal["clt", "pj", "freelancer", "internship"]
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
    company_id: int
