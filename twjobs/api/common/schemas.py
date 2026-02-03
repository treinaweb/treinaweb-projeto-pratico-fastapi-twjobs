from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: int
    name: str


class SkillListRequest(BaseModel):
    skills: list[int]
