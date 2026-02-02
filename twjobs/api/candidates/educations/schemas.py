from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class EducationRequest(BaseModel):
    institution: Annotated[str, Field(min_length=3, max_length=100)]
    degree: Annotated[str, Field(min_length=3, max_length=100)]
    field_of_study: Annotated[str, Field(min_length=3, max_length=100)]
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class EducationResponse(BaseModel):
    id: int
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: date | None = None
