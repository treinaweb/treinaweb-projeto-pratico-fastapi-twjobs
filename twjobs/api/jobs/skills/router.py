from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from twjobs.api.common.schemas import SkillListRequest, SkillResponse
from twjobs.core.dependencies import CurrentCompanyUserDep, SessionDep
from twjobs.core.models import Job, Skill

router = APIRouter(tags=["Jobs", "Skills"])


@router.get("/{job_id}/skills", response_model=list[SkillResponse])
def get_job_skills(job_id: int, session: SessionDep):
    db_job = session.get(Job, job_id)
    if db_job is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Job not found."
        )
    return db_job.skills


@router.put(
    "/{job_id}/skills",
    response_model=list[SkillResponse],
)
def update_job_skills(
    job_id: int,
    req: SkillListRequest,
    session: SessionDep,
    current_user: CurrentCompanyUserDep,
):
    db_job = session.scalar(
        select(Job).where(
            Job.id == job_id, Job.company_id == current_user.company.user_id
        )
    )

    if db_job is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Job not found."
        )

    skills = session.scalars(
        select(Skill).where(Skill.id.in_(req.skills))
    ).all()

    db_job.skills = skills
    session.commit()
    session.refresh(db_job)
    return db_job.skills
