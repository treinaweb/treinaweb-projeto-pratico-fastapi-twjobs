from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from twjobs.api.common.schemas import CandidateResponse, JobResponse


class ApplicationResponse(BaseModel):
    id: int
    candidate: CandidateResponse
    job: JobResponse
    status: str
    applied_at: datetime
    updated_at: datetime


StatusOptions = Literal["applied", "reviewing", "approved", "rejected"]


class ApplicationStatusUpdateRequest(BaseModel):
    status: StatusOptions


class ApplicationFilters(BaseModel):
    page: Annotated[int, Field(gt=0)] = 1
    size: Annotated[int, Field(gt=0, le=100)] = 20
    job: Annotated[int | None, Field(gt=0)] = None
    status: StatusOptions | None = None
    order_by: Literal["id", "status", "applied_at", "updated_at"] = "id"
    order_dir: Literal["asc", "desc"] = "asc"
