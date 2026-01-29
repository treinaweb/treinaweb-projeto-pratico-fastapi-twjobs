from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator


class SkillRequest(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]

    @field_validator("name")
    def normalize_name(cls, value: str):
        return value.strip().upper()


class SkillResponse(BaseModel):
    id: int
    name: str


app = FastAPI()

skills_db = [
    {"id": 1, "name": "PYTHON"},
    {"id": 2, "name": "FASTAPI"},
    {"id": 3, "name": "DOCKER"},
]
next_skill_id = 4


@app.get("/")
def read_root():
    return {"message": "Hello, TWJobs!"}


@app.get(
    "/api/skills",
    summary="Retrieve all skills",
    tags=["Skills"],
    response_model=list[SkillResponse],
)
def get_skills():
    return skills_db


@app.post(
    "/api/skills",
    status_code=HTTPStatus.CREATED,
    summary="Create a new skill",
    tags=["Skills"],
    response_model=SkillResponse,
)
def create_skill(skill: SkillRequest):
    global next_skill_id
    new_skill = {"id": next_skill_id, "name": skill.name}
    skills_db.append(new_skill)
    next_skill_id += 1
    return new_skill


@app.get(
    "/api/skills/{skill_id}",
    summary="Retrieve a skill by ID",
    tags=["Skills"],
    response_model=SkillResponse,
)
def get_skill(skill_id: int):
    for skill in skills_db:
        if skill["id"] == skill_id:
            return skill
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
    )


@app.put(
    "/api/skills/{skill_id}",
    summary="Update a skill by ID",
    tags=["Skills"],
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


@app.delete(
    "/api/skills/{skill_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete a skill by ID",
    tags=["Skills"],
)
def delete_skill(skill_id: int):
    for index, skill in enumerate(skills_db):
        if skill["id"] == skill_id:
            del skills_db[index]
            return
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Skill not found"
    )
