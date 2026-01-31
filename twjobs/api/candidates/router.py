from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Link, Skill

from .schemas import (
    CandidateRequest,
    CandidateResponse,
    LinkRequest,
    LinkResponse,
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


@router.post("/me/links", response_model=LinkResponse)
def create_current_candidate_link(
    req: LinkRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )

    db_link = Link(
        **req.model_dump(mode="json"),
        candidate_id=current_user.candidate.user_id,
    )
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link


@router.put("/me/links/{link_id}", response_model=LinkResponse)
def update_current_candidate_link(
    link_id: int,
    req: LinkRequest,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )

    db_link = session.scalar(
        select(Link).where(
            Link.id == link_id,
            Link.candidate_id == current_user.candidate.user_id,
        )
    )
    if db_link is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Link not found.",
        )

    for key, value in req.model_dump(mode="json").items():
        setattr(db_link, key, value)

    session.commit()
    session.refresh(db_link)
    return db_link


@router.delete("/me/links/{link_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_current_candidate_link(
    link_id: int,
    session: SessionDep,
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )

    db_link = session.scalar(
        select(Link).where(
            Link.id == link_id,
            Link.candidate_id == current_user.candidate.user_id,
        )
    )
    if db_link is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Link not found.",
        )

    session.delete(db_link)
    session.commit()


@router.get("/me/links", response_model=list[LinkResponse])
def get_current_candidate_links(
    current_user: CurrentCandidateUserDep,
):
    if current_user.candidate is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Candidate profile not found.",
        )
    return current_user.candidate.links


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


@router.get("/{user_id}/links", response_model=list[LinkResponse])
def get_candidate_links_by_user_id(
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
    return candidate.links
