from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.api.common.schemas import SkillListRequest, SkillResponse
from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Skill

router = APIRouter(tags=["Candidates", "Skills"])


@router.put("/me/skills", response_model=list[SkillResponse])
def update_current_candidate_skills(
    req: SkillListRequest,
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
