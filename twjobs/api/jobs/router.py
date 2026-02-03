from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import CurrentCompanyUserDep, SessionDep
from twjobs.core.models import Job

from .schemas import JobRequest, JobResponse
from .skills.router import router as skills_router

router = APIRouter(tags=["Jobs"])

router.include_router(skills_router)


@router.post("/", response_model=JobResponse, status_code=HTTPStatus.CREATED)
def create_job(
    req: JobRequest, session: SessionDep, current_user: CurrentCompanyUserDep
):
    if current_user.company is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Current user does not have an associated company.",
        )

    db_job = Job(
        **req.model_dump(mode="json"),
        status="open",
        company_id=current_user.company.user_id,
    )
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return db_job


@router.get("/", response_model=list[JobResponse])
def list_jobs(session: SessionDep):
    return session.scalars(select(Job)).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, session: SessionDep):
    db_job = session.get(Job, job_id)
    if db_job is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Job not found."
        )
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    req: JobRequest,
    session: SessionDep,
    current_user: CurrentCompanyUserDep,
):
    db_job = session.scalar(
        select(Job).where(
            Job.id == job_id,
            Job.company_id == current_user.company.user_id,
        )
    )

    for key, value in req.model_dump(mode="json").items():
        setattr(db_job, key, value)

    session.commit()
    session.refresh(db_job)
    return db_job


@router.delete("/{job_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_job(
    job_id: int,
    session: SessionDep,
    current_user: CurrentCompanyUserDep,
):
    db_job = session.scalar(
        select(Job).where(
            Job.id == job_id,
            Job.company_id == current_user.company.user_id,
        )
    )

    if db_job is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Job not found."
        )

    session.delete(db_job)
    session.commit()
