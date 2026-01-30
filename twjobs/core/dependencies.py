from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .db import engine
from .models import User
from .security import get_sub_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(session: SessionDep, token: TokenDep):
    unauthenticated_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Token is invalid or has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    sub = get_sub_from_token(token)
    if sub is None:
        raise unauthenticated_exception

    user = session.get(User, sub)

    if user is None:
        raise unauthenticated_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
