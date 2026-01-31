from typing import Literal

from pydantic import BaseModel, HttpUrl


class LinkResponse(BaseModel):
    id: int
    url: str
    link_type: str


class LinkRequest(BaseModel):
    url: HttpUrl
    link_type: Literal["linkedin", "github", "portfolio", "other"]
