from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from twjobs.core.dependencies import SessionDep
from twjobs.core.models import Skill

from .schemas import SkillRequest, SkillResponse

router = APIRouter(tags=["Skills"])


@router.get(
    "/",
    summary="Retrieve all skills",
    response_model=list[SkillResponse],
)
def get_skills(session: SessionDep):
    return session.scalars(select(Skill)).all()


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    summary="Create a new skill",
    response_model=SkillResponse,
)
def create_skill(skill: SkillRequest, session: SessionDep):
    db_skill = Skill(**skill.model_dump())
    session.add(db_skill)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Skill already exists"
        )

    session.refresh(db_skill)
    return db_skill


@router.get(
    "/{skill_id}",
    summary="Retrieve a skill by ID",
    response_model=SkillResponse,
)
def get_skill(skill_id: int, session: SessionDep):
    db_skill = session.get(Skill, skill_id)
    if db_skill is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
        )
    return db_skill


@router.put(
    "/{skill_id}",
    summary="Update a skill by ID",
    response_model=SkillResponse,
)
def update_skill(
    skill_id: int,
    skill: SkillRequest,
    session: SessionDep,
):
    db_skill = session.get(Skill, skill_id)
    if db_skill is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
        )
    db_skill.name = skill.name

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Skill already exists"
        )

    session.refresh(db_skill)
    return db_skill


@router.delete(
    "/{skill_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete a skill by ID",
)
def delete_skill(skill_id: int, session: SessionDep):
    db_skill = session.get(Skill, skill_id)
    if db_skill is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
        )
    session.delete(db_skill)
    session.commit()
