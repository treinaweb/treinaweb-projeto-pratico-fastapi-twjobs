from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import select

from twjobs.api.common.schemas import CandidateResponse
from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.mail import WelcomeEmailContext, mail_service
from twjobs.core.models import Candidate

from .educations.router import router as educations_router
from .experiences.router import router as experiences_router
from .links.router import router as links_router
from .schemas import CandidateRequest
from .skills.router import router as skills_router

router = APIRouter(tags=["Candidates"])

router.include_router(links_router)
router.include_router(skills_router)
router.include_router(experiences_router)
router.include_router(educations_router)


@router.put("/me", response_model=CandidateResponse)
async def create_or_update_candidate(
    req: CandidateRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
    background_tasks: BackgroundTasks,
):
    email_exists = session.scalar(
        select(Candidate).where(
            Candidate.email == req.email, Candidate.user_id != current_user.id
        )
    )

    if email_exists:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A candidate with the given email already exists.",
        )

    cpf_exists = session.scalar(
        select(Candidate).where(
            Candidate.cpf == req.cpf, Candidate.user_id != current_user.id
        )
    )

    if cpf_exists:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A candidate with the given CPF already exists.",
        )

    is_new = current_user.candidate is None

    if not is_new:
        db_candidate = current_user.candidate
        for key, value in req.model_dump(mode="json").items():
            setattr(db_candidate, key, value)
    else:
        db_candidate = Candidate(
            **req.model_dump(mode="json"), user_id=current_user.id
        )
        session.add(db_candidate)

    session.commit()
    session.refresh(db_candidate)

    if is_new:
        background_tasks.add_task(
            mail_service.send_welcome_mail,
            to=db_candidate.email,
            context=WelcomeEmailContext(
                name=db_candidate.name, role="candidate"
            ),
        )

    return db_candidate


@router.get("/me", response_model=CandidateResponse)
def get_current_candidate(
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )
    return current_user.candidate


@router.get("/{user_id}", response_model=CandidateResponse)
def get_candidate_by_user_id(
    user_id: int,
    current_user: CurrentAdminOrCompanyUserDep,
    session: SessionDep,
):
    candidate = session.get(Candidate, user_id)
    if candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate not found.",
        )
    return candidate
