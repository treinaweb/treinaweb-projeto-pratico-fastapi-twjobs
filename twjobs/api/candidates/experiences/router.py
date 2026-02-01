from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Experience

from .schemas import ExperienceRequest, ExperienceResponse

router = APIRouter(tags=["Candidates", "Experiences"])


@router.get("/me/experiences", response_model=list[ExperienceResponse])
def get_current_candidate_experiences(
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    return current_user.candidate.experiences


@router.post(
    "/me/experiences",
    response_model=ExperienceResponse,
    status_code=HTTPStatus.CREATED,
)
def create_experience_for_current_candidate(
    req: ExperienceRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_experience = Experience(
        **req.model_dump(mode="json"),
        candidate_id=current_user.candidate.user_id,
    )
    session.add(db_experience)
    session.commit()
    session.refresh(db_experience)
    return db_experience


@router.get(
    "/me/experiences/{experience_id}", response_model=ExperienceResponse
)
def get_experience_by_id_for_current_candidate(
    experience_id: int,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_experience = session.scalar(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_experience is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Experience not found for the current candidate.",
        )

    return db_experience


@router.put(
    "/me/experiences/{experience_id}", response_model=ExperienceResponse
)
def update_experience_for_current_candidate(
    experience_id: int,
    req: ExperienceRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_experience = session.scalar(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_experience is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Experience not found for the current candidate.",
        )

    for key, value in req.model_dump(mode="json").items():
        setattr(db_experience, key, value)

    session.commit()
    session.refresh(db_experience)
    return db_experience


@router.delete(
    "/me/experiences/{experience_id}", status_code=HTTPStatus.NO_CONTENT
)
def delete_experience_for_current_candidate(
    experience_id: int,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_experience = session.scalar(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_experience is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Experience not found for the current candidate.",
        )

    session.delete(db_experience)
    session.commit()


@router.get("/{user_id}/experiences", response_model=list[ExperienceResponse])
def get_candidate_experiences_by_user_id(
    user_id: int,
    session: SessionDep,
    current_user: CurrentAdminOrCompanyUserDep,
):
    db_candidate = session.get(Candidate, user_id)

    if db_candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate not found.",
        )

    return db_candidate.experiences


@router.get(
    "/{user_id}/experiences/{experience_id}",
    response_model=ExperienceResponse,
)
def get_candidate_experience_by_id(
    user_id: int,
    experience_id: int,
    session: SessionDep,
    current_user: CurrentAdminOrCompanyUserDep,
):
    db_experience = session.scalar(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.candidate_id == user_id,
        )
    )

    if db_experience is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Experience not found for the specified candidate.",
        )

    return db_experience
