from datetime import datetime

from pydantic import BaseModel

from twjobs.api.common.schemas import CandidateResponse, JobResponse


class ApplicationResponse(BaseModel):
    id: int
    candidate: CandidateResponse
    job: JobResponse
    status: str
    applied_at: datetime
    updated_at: datetime
