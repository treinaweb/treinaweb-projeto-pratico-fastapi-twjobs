from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Skill

from .schemas import (
    CandidateRequest,
    CandidateResponse,
    SkillRequest,
    SkillResponse,
)

router = APIRouter(tags=["Candidates"])


@router.put("/me", response_model=CandidateResponse)
def create_or_update_candidate(
    req: CandidateRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
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

    if current_user.candidate is not None:
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


@router.put("/me/skills", response_model=list[SkillResponse])
def update_current_candidate_skills(
    req: SkillRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )

    skills = session.scalars(
        select(Skill).where(Skill.id.in_(req.skills))
    ).all()

    current_user.candidate.skills = skills
    session.commit()
    session.refresh(current_user.candidate)
    return current_user.candidate.skills


@router.get("/me/skills", response_model=list[SkillResponse])
def get_current_candidate_skills(
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )
    return current_user.candidate.skills


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


@router.get("/{user_id}/skills", response_model=list[SkillResponse])
def get_candidate_skills_by_user_id(
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
    return candidate.skills
