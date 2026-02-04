from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, func, select

from twjobs.api.common.schemas import PaginatedResponse
from twjobs.core.dependencies import CurrentCompanyUserDep, SessionDep
from twjobs.core.models import Job, job_skills

from .schemas import JobFilters, JobRequest, JobResponse
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


@router.get("/", response_model=PaginatedResponse[JobResponse])
def list_jobs(session: SessionDep, filters: Annotated[JobFilters, Query()]):
    base_stmt = select(Job)

    if filters.search:
        base_stmt = base_stmt.where(Job.title.ilike(f"%{filters.search}%"))

    if filters.level:
        base_stmt = base_stmt.where(Job.level == filters.level)

    if filters.employment_type:
        base_stmt = base_stmt.where(
            Job.employment_type == filters.employment_type
        )

    if filters.is_remote is not None:
        base_stmt = base_stmt.where(Job.is_remote == filters.is_remote)

    if filters.company_id:
        base_stmt = base_stmt.where(Job.company_id == filters.company_id)

    if filters.skills:
        base_stmt = (
            base_stmt
            .join(job_skills)
            .where(job_skills.c.skill_id.in_(filters.skills))
            .distinct()
        )

    total = session.scalar(
        select(func.count()).select_from(base_stmt.subquery())
    )

    order_column = getattr(Job, filters.order_by)
    order_func = asc if filters.order_dir == "asc" else desc
    offset = (filters.page - 1) * filters.size

    stmt = (
        base_stmt
        .order_by(order_func(order_column))
        .offset(offset)
        .limit(filters.size)
    )

    jobs = session.scalars(stmt).all()

    return {
        "total": total,
        "page": filters.page,
        "size": filters.size,
        "items": jobs,
    }


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
