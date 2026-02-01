from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class ExperienceRequest(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100)]
    company: Annotated[str, Field(min_length=3, max_length=100)]
    role: Annotated[str, Field(min_length=3, max_length=50)]
    description: Annotated[str, Field(min_length=10, max_length=1000)]
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ExperienceResponse(BaseModel):
    id: int
    title: str
    company: str
    role: str
    description: str
    start_date: date
    end_date: date | None
