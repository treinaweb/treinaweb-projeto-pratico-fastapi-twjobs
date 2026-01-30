from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from twjobs.core.dependencies import SessionDep
from twjobs.core.models import User
from twjobs.core.security import hash_password

from .schemas import RegisterRequest, UserResponse

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
