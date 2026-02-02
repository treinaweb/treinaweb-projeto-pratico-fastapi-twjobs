from datetime import date

from sqlalchemy import Column, ForeignKey, Table, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


candidate_skills = Table(
    "candidate_skills",
    table_registry.metadata,
    Column(
        "candidate_id",
        ForeignKey("candidates.user_id"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        ForeignKey("skills.id"),
        primary_key=True,
    ),
)


@mapped_as_dataclass(table_registry)
class Skill:
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True)


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str]
    password_hash: Mapped[str]

    company: Mapped["Company"] = relationship(
        init=False, back_populates="user"
    )

    candidate: Mapped["Candidate"] = relationship(
        init=False, back_populates="user"
    )


@mapped_as_dataclass(table_registry)
class Company:
    __tablename__ = "companies"

    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    cnpj: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text)
    size: Mapped[str]
    website: Mapped[str]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(
        init=False, back_populates="company", single_parent=True
    )


@mapped_as_dataclass(table_registry)
class Candidate:
    __tablename__ = "candidates"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    headline: Mapped[str]
    bio: Mapped[str] = mapped_column(Text)
    phone: Mapped[str]
    cpf: Mapped[str] = mapped_column(unique=True)

    user: Mapped["User"] = relationship(
        init=False, back_populates="candidate", single_parent=True
    )

    skills: Mapped[list["Skill"]] = relationship(
        init=False, secondary=candidate_skills
    )

    links: Mapped[list["Link"]] = relationship(
        init=False, back_populates="candidate", cascade="all, delete-orphan"
    )

    experiences: Mapped[list["Experience"]] = relationship(
        init=False, back_populates="candidate", cascade="all, delete-orphan"
    )

    educations: Mapped[list["Education"]] = relationship(
        init=False, back_populates="candidate", cascade="all, delete-orphan"
    )


@mapped_as_dataclass(table_registry)
class Link:
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    url: Mapped[str]
    link_type: Mapped[str]
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.user_id"))

    candidate: Mapped["Candidate"] = relationship(
        init=False, back_populates="links"
    )


@mapped_as_dataclass(table_registry)
class Experience:
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    title: Mapped[str]
    company: Mapped[str]
    role: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.user_id"))

    candidate: Mapped["Candidate"] = relationship(
        init=False, back_populates="experiences"
    )


@mapped_as_dataclass(table_registry)
class Education:
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    institution: Mapped[str]
    degree: Mapped[str]
    field_of_study: Mapped[str]
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.user_id"))

    candidate: Mapped["Candidate"] = relationship(
        init=False, back_populates="educations"
    )
