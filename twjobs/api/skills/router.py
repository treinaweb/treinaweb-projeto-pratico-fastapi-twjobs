from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError

from twjobs.core.dependencies import SessionDep
from twjobs.core.models import Skill

from .schemas import (
    PaginatedSkillResponse,
    SkillFilters,
    SkillRequest,
    SkillResponse,
)

router = APIRouter(tags=["Skills"])


@router.get(
    "/",
    summary="Retrieve all skills",
    response_model=PaginatedSkillResponse,
)
def get_skills(session: SessionDep, filters: Annotated[SkillFilters, Query()]):
    base_stmt = select(Skill)

    if filters.search:
        base_stmt = base_stmt.where(Skill.name.ilike(f"%{filters.search}%"))

    total = session.scalar(
        select(func.count()).select_from(base_stmt.subquery())
    )

    order_column = getattr(Skill, filters.order_by)
    order_func = asc if filters.order_dir == "asc" else desc
    offset = (filters.page - 1) * filters.size

    stmt = (
        base_stmt.order_by(order_func(order_column))
        .offset(offset)
        .limit(filters.size)
    )

    skills = session.scalars(stmt).all()

    return {
        "total": total,
        "page": filters.page,
        "size": filters.size,
        "items": skills,
    }


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
