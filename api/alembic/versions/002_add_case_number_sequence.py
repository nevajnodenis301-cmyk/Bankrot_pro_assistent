"""Add case number sequence

Revision ID: 002
Revises: 001
Create Date: 2026-01-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequence for case numbers
    op.execute("CREATE SEQUENCE IF NOT EXISTS case_number_seq START 1")


def downgrade() -> None:
    # Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS case_number_seq")
