from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.core.dependencies import (
    CurrentAdminOrCompanyUserDep,
    CurrentCandidateUserDep,
    SessionDep,
)
from twjobs.core.models import Candidate, Link

from .schemas import LinkRequest, LinkResponse

router = APIRouter(tags=["Candidates", "Links"])


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
