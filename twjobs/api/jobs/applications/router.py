from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from twjobs.core.dependencies import CurrentCandidateUserDep, SessionDep
from twjobs.core.models import Application, Job

router = APIRouter(tags=["Applications"])


@router.post("/{job_id}/apply", status_code=HTTPStatus.NO_CONTENT)
def apply_to_job(
    job_id: int, session: SessionDep, current_user: CurrentCandidateUserDep
):
    job_db = session.get(Job, job_id)

    if job_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Job not found."
        )

    if job_db.status != "open":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Job is not open for applications.",
        )

    application_db = Application(
        job_id=job_id,
        candidate_id=current_user.candidate.user_id,
        status="applied",
    )
    session.add(application_db)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="You have already applied to this job.",
        )

    session.refresh(application_db)
