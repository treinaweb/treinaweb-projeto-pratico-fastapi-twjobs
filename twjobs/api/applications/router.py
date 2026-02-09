from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from twjobs.core.dependencies import CurrentUserDep, SessionDep
from twjobs.core.models import Application

from .schemas import ApplicationResponse

router = APIRouter(tags=["Applications"])


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
