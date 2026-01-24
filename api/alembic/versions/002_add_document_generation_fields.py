"""Add document generation fields

Revision ID: 002
Revises: 001
Create Date: 2026-01-21 00:00:00.000000

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
    # Add new fields to cases table for document generation
    op.add_column('cases', sa.Column('passport_code', sa.String(length=10), nullable=True))
    op.add_column('cases', sa.Column('court_name', sa.String(length=255), nullable=True))
    op.add_column('cases', sa.Column('court_address', sa.Text(), nullable=True))
    op.add_column('cases', sa.Column('gender', sa.String(length=1), nullable=True))
    op.add_column('cases', sa.Column('marital_status', sa.String(length=50), nullable=True))
    op.add_column('cases', sa.Column('sro_name', sa.String(length=255), nullable=True))
    op.add_column('cases', sa.Column('sro_address', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove added columns
    op.drop_column('cases', 'sro_address')
    op.drop_column('cases', 'sro_name')
    op.drop_column('cases', 'marital_status')
    op.drop_column('cases', 'gender')
    op.drop_column('cases', 'court_address')
    op.drop_column('cases', 'court_name')
    op.drop_column('cases', 'passport_code')
