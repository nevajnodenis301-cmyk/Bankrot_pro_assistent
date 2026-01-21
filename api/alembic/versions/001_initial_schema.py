"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create cases table
    op.create_table(
        'cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_number', sa.String(length=20), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='new'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=True),
        sa.Column('passport_series', sa.String(length=4), nullable=True),
        sa.Column('passport_number', sa.String(length=6), nullable=True),
        sa.Column('passport_issued_by', sa.Text(), nullable=True),
        sa.Column('passport_issued_date', sa.Date(), nullable=True),
        sa.Column('inn', sa.String(length=12), nullable=True),
        sa.Column('snils', sa.String(length=14), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('registration_address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('total_debt', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('monthly_income', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cases_case_number'), 'cases', ['case_number'], unique=True)
    op.create_index(op.f('ix_cases_telegram_user_id'), 'cases', ['telegram_user_id'], unique=False)

    # Create creditors table
    op.create_table(
        'creditors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('creditor_type', sa.String(length=50), nullable=True),
        sa.Column('debt_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('debt_type', sa.String(length=100), nullable=True),
        sa.Column('contract_number', sa.String(length=100), nullable=True),
        sa.Column('contract_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('creditors')
    op.drop_index(op.f('ix_cases_telegram_user_id'), table_name='cases')
    op.drop_index(op.f('ix_cases_case_number'), table_name='cases')
    op.drop_table('cases')
