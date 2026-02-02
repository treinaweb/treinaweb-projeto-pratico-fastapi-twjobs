from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Education

from .schemas import EducationRequest, EducationResponse

router = APIRouter(tags=["Candidates", "Educations"])


@router.get("/me/educations", response_model=list[EducationResponse])
def get_current_candidate_educations(
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    return current_user.candidate.educations


@router.post(
    "/me/educations",
    response_model=EducationResponse,
    status_code=HTTPStatus.CREATED,
)
def create_education_for_current_candidate(
    req: EducationRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_education = Education(
        **req.model_dump(mode="json"),
        candidate_id=current_user.candidate.user_id,
    )
    session.add(db_education)
    session.commit()
    session.refresh(db_education)
    return db_education


@router.get("/me/educations/{education_id}", response_model=EducationResponse)
def get_education_by_id_for_current_candidate(
    education_id: int,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_education = session.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_education is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Education not found for the current candidate.",
        )

    return db_education


@router.put(
    "/me/educations/{education_id}",
    response_model=EducationResponse,
)
def update_education_for_current_candidate(
    education_id: int,
    req: EducationRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_education = session.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_education is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Education not found for the current candidate.",
        )

    for key, value in req.model_dump(mode="json").items():
        setattr(db_education, key, value)

    session.commit()
    session.refresh(db_education)
    return db_education


@router.delete(
    "/me/educations/{education_id}", status_code=HTTPStatus.NO_CONTENT
)
def delete_education_for_current_candidate(
    education_id: int,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found for the current user.",
        )

    db_education = session.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_id == current_user.candidate.user_id,
        )
    )

    if db_education is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Education not found for the current candidate.",
        )

    session.delete(db_education)
    session.commit()


@router.get("/{user_id}/educations", response_model=list[EducationResponse])
def get_educations_by_user_id(
    user_id: int,
    current_user: CurrentAdminOrCompanyUserDep,
    session: SessionDep,
):
    db_candidate = session.get(Candidate, user_id)

    if db_candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate not found.",
        )

    return db_candidate.educations


@router.get(
    "/{user_id}/educations/{education_id}", response_model=EducationResponse
)
def get_education_by_id_and_user_id(
    user_id: int,
    education_id: int,
    current_user: CurrentAdminOrCompanyUserDep,
    session: SessionDep,
):
    db_education = session.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_id == user_id,
        )
    )

    if db_education is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Education not found for the given candidate.",
        )

    return db_education
