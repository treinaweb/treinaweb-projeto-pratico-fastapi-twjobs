import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=100)]
    password: Annotated[str, Field(min_length=6, max_length=128)]
    role: Literal["company", "candidate"]

    @field_validator("password")
    def validate_password(cls, value: str):
        pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$")

        if not pattern.match(value):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one number, and one special character."
            )

        return value


class UserResponse(BaseModel):
    id: int
    username: str
    role: Literal["admin", "company", "candidate"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
