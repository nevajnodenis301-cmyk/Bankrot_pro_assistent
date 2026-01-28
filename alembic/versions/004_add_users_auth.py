"""Add users and refresh_tokens tables

Revision ID: 004_add_users_auth
Revises: 003_add_case_number_sequence
Create Date: 2026-01-28 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_users_auth'
down_revision: Union[str, None] = '003_add_case_number_sequence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('telegram_username', sa.String(100), nullable=True),
        sa.Column('telegram_linked_at', sa.DateTime(), nullable=True),
        sa.Column('linking_code', sa.String(10), nullable=True),
        sa.Column('linking_code_expires', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)
    op.create_index('ix_users_linking_code', 'users', ['linking_code'], unique=True)
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for refresh_tokens
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)
    
    # Add owner_id to cases table (link cases to users)
    op.add_column('cases', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_index('ix_cases_owner_id', 'cases', ['owner_id'])
    op.create_foreign_key(
        'fk_cases_owner_id', 
        'cases', 'users',
        ['owner_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remove foreign key and column from cases
    op.drop_constraint('fk_cases_owner_id', 'cases', type_='foreignkey')
    op.drop_index('ix_cases_owner_id', table_name='cases')
    op.drop_column('cases', 'owner_id')
    
    # Drop refresh_tokens table
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    # Drop users table
    op.drop_index('ix_users_linking_code', table_name='users')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_uuid', table_name='users')
    op.drop_table('users')
