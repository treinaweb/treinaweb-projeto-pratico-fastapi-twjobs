from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from .schemas import SkillRequest, SkillResponse

router = APIRouter(tags=["Skills"])

skills_db = [
    {"id": 1, "name": "PYTHON"},
    {"id": 2, "name": "FASTAPI"},
    {"id": 3, "name": "DOCKER"},
]
next_skill_id = 4


@router.get(
    "/",
    summary="Retrieve all skills",
    response_model=list[SkillResponse],
)
def get_skills():
    return skills_db


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    summary="Create a new skill",
    response_model=SkillResponse,
)
def create_skill(skill: SkillRequest):
    global next_skill_id
    new_skill = {"id": next_skill_id, "name": skill.name}
    skills_db.append(new_skill)
    next_skill_id += 1
    return new_skill


@router.get(
    "/{skill_id}",
    summary="Retrieve a skill by ID",
    response_model=SkillResponse,
)
def get_skill(skill_id: int):
    for skill in skills_db:
        if skill["id"] == skill_id:
            return skill
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
    )


@router.put(
    "/{skill_id}",
    summary="Update a skill by ID",
    response_model=SkillResponse,
)
def update_skill(skill_id: int, skill: SkillRequest):
    for existing_skill in skills_db:
        if existing_skill["id"] == skill_id:
            existing_skill["name"] = skill.name
            return existing_skill
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
    )


@router.delete(
    "/{skill_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete a skill by ID",
)
def delete_skill(skill_id: int):
    for index, skill in enumerate(skills_db):
        if skill["id"] == skill_id:
            del skills_db[index]
            return
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
    )
