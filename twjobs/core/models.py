from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry

from .db import engine

table_registry = registry()


@mapped_as_dataclass(table_registry)
class Skill:
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(unique=True)


table_registry.metadata.create_all(engine)
