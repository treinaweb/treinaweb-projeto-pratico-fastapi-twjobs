from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, func, select

from twjobs.api.common.schemas import PaginatedResponse
from twjobs.core.dependencies import (
    CurrentCompanyUserDep,
    CurrentUserDep,
    SessionDep,
)
from twjobs.core.models import Application, Candidate, Job

from .schemas import (
    ApplicationFilters,
    ApplicationResponse,
    ApplicationStatusUpdateRequest,
)

router = APIRouter(tags=["Applications"])


@router.get("/", response_model=PaginatedResponse[ApplicationResponse])
def list_applications(
    filters: Annotated[ApplicationFilters, Query()],
    current_user: CurrentUserDep,
    session: SessionDep,
):
    base_stmt = (
        select(Application)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, Application.candidate_id == Candidate.user_id)
    )

    if current_user.is_company():
        base_stmt = base_stmt.where(
            Job.company_id == current_user.company.user_id
        )
    elif current_user.is_candidate():
        base_stmt = base_stmt.where(
            Application.candidate_id == current_user.candidate.user_id
        )

    if filters.job is not None:
        base_stmt = base_stmt.where(Application.job_id == filters.job)

    if filters.status is not None:
        base_stmt = base_stmt.where(Application.status == filters.status)

    total = session.scalar(
        select(func.count()).select_from(base_stmt.subquery())
    )

    order_column = getattr(Application, filters.order_by)
    order_func = asc if filters.order_dir == "asc" else desc
    offset = (filters.page - 1) * filters.size

    stmt = (
        base_stmt
        .order_by(order_func(order_column))
        .offset(offset)
        .limit(filters.size)
    )

    applications_db = session.scalars(stmt).all()

    return {
        "total": total,
        "page": filters.page,
        "size": filters.size,
        "items": applications_db,
    }


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application_by_id(
    application_id: int, current_user: CurrentUserDep, session: SessionDep
):
    application_db = session.get(Application, application_id)

    if application_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Application not found."
        )

    is_company_owner = (
        current_user.is_company()
        and application_db.job.company_id == current_user.company.user_id
    )
    is_candidate_owner = (
        current_user.is_candidate()
        and application_db.candidate_id == current_user.candidate.user_id
    )

    if not (is_company_owner or is_candidate_owner):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to access this application.",
        )

    return application_db


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    req: ApplicationStatusUpdateRequest,
    current_user: CurrentCompanyUserDep,
    session: SessionDep,
):
    application_db = session.get(Application, application_id)

    if application_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Application not found."
        )

    if application_db.job.company_id != current_user.company.user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to update this application.",
        )

    try:
        application_db.transition_to(req.status)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    session.commit()
    session.refresh(application_db)

    return application_db
