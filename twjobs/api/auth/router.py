from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from twjobs.core.dependencies import SessionDep
from twjobs.core.models import User
from twjobs.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from .schemas import RegisterRequest, TokenResponse, UserResponse

router = APIRouter(tags=["Auth"])


@router.post(
    "/register", status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def register_user(req: RegisterRequest, session: SessionDep):
    db_user = User(
        **req.model_dump(exclude={"password"}),
        password_hash=hash_password(req.password),
    )

    session.add(db_user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="User with given email already exists.",
        )

    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    db_user = session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if db_user is None or not verify_password(
        form_data.password, db_user.password_hash
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(
        sub=db_user.id,
        extra_claims={"username": db_user.username, "role": db_user.role},
    )

    return TokenResponse(access_token=access_token)
