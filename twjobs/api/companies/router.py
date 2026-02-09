from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import select

from twjobs.api.common.schemas import CompanyResponse
from twjobs.core.dependencies import CurrentCompanyUserDep, SessionDep
from twjobs.core.mail import WelcomeEmailContext, mail_service
from twjobs.core.models import Company

from .schemas import CompanyRequest

router = APIRouter(tags=["Companies"])


@router.put("/me", response_model=CompanyResponse)
async def create_or_update_company(
    req: CompanyRequest,
    session: SessionDep,
    current_user: CurrentCompanyUserDep,
    background_tasks: BackgroundTasks,
):
    email_exists = session.scalar(
        select(Company).where(
            Company.email == req.email, Company.user_id != current_user.id
        )
    )

    if email_exists:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A company with the given email already exists.",
        )

    cnpj_exists = session.scalar(
        select(Company).where(
            Company.cnpj == req.cnpj, Company.user_id != current_user.id
        )
    )

    if cnpj_exists:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A company with the given CNPJ already exists.",
        )

    is_new = current_user.company is None

    if not is_new:
        db_company = current_user.company
        for key, value in req.model_dump(mode="json").items():
            setattr(db_company, key, value)
    else:
        db_company = Company(
            **req.model_dump(mode="json"), user_id=current_user.id
        )
        session.add(db_company)

    session.commit()
    session.refresh(db_company)

    if is_new:
        background_tasks.add_task(
            mail_service.send_welcome_mail,
            to=db_company.email,
            context=WelcomeEmailContext(name=db_company.name, role="company"),
        )

    return db_company


@router.get("/me", response_model=CompanyResponse)
def get_current_company(
    current_user: CurrentCompanyUserDep,
):
    if current_user.company is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Company not found for the current user.",
        )
    return current_user.company


@router.get("/{user_id}", response_model=CompanyResponse)
def get_company_by_user_id(
    user_id: int,
    session: SessionDep,
):
    db_company = session.get(Company, user_id)

    if db_company is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Company not found for the given user ID.",
        )

    return db_company
