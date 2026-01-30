from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


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


@mapped_as_dataclass(table_registry)
class Company:
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    cnpj: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text)
    size: Mapped[str]
    website: Mapped[str]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )

    user: Mapped["User"] = relationship(
        init=False, back_populates="company", single_parent=True
    )
