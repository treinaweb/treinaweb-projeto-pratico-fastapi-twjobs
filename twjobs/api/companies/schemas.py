from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from validate_docbr import CNPJ

SizeOptions = Literal["micro", "small", "medium", "large"]


class CompanyRequest(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=100)]
    email: EmailStr
    cnpj: Annotated[str, Field(min_length=14, max_length=14)]
    description: Annotated[str, Field(min_length=10, max_length=1000)]
    size: SizeOptions
    website: HttpUrl

    @field_validator("cnpj")
    def validate_cnpj(cls, value: str):
        if not value.isdigit():
            raise ValueError("CNPJ must contain only digits.")
        if not CNPJ().validate(value):
            raise ValueError("Invalid CNPJ.")
        return value


class CompanyResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    cnpj: str
    description: str
    size: SizeOptions
    website: HttpUrl
