"""add unique in user_id for companies table

Revision ID: 98cfb6dd7e81
Revises: e5a3345b7cbb
Create Date: 2026-02-03 17:11:16.131175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98cfb6dd7e81'
down_revision: Union[str, Sequence[str], None] = 'e5a3345b7cbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        constraint_name='uq_companies_user_id',
        table_name='companies',
        columns=['user_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        constraint_name='uq_companies_user_id',
        table_name='companies',
        type_='unique'
    )
