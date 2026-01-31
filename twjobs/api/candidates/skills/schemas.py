from pydantic import BaseModel


class SkillRequest(BaseModel):
    skills: list[int]


class SkillResponse(BaseModel):
    id: int
    name: str
