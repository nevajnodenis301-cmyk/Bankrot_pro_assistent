"""Add case number sequence

Revision ID: 003
Revises: 002
Create Date: 2026-01-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequence for case numbers
    # Start at 1 for the first case, increment by 1
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS case_number_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
    """)

    # Set the sequence to the current max case number if cases exist
    op.execute("""
        SELECT setval('case_number_seq',
            COALESCE(
                (SELECT MAX(CAST(SPLIT_PART(case_number, '-', 3) AS INTEGER))
                 FROM cases
                 WHERE case_number ~ '^BP-[0-9]{4}-[0-9]{4}$'),
                0
            )
        );
    """)


def downgrade() -> None:
    # Drop the sequence
    op.execute("DROP SEQUENCE IF EXISTS case_number_seq;")
