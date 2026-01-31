"""Encrypt additional PII fields

Revision ID: 006_encrypt_additional_pii
Revises: 005_encrypt_pii_fields
Create Date: 2026-01-31 14:00:00.000000

This migration encrypts additional sensitive fields:
- cases: notes, employer_name, sro_name, sro_address
- users: email, full_name (with email_hash for uniqueness)

For users.email: Since encryption uses random nonces, the same email
produces different ciphertexts. We add email_hash (SHA-256) for
uniqueness checks and lookups while keeping email encrypted.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_encrypt_additional_pii'
down_revision: Union[str, None] = '005_encrypt_pii_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Encrypt additional PII fields and add email_hash for users.
    """

    # ==================== CASES TABLE ====================
    # notes: Text -> Text (EncryptedText in model, no column change needed)
    # Already Text type, encryption is transparent via TypeDecorator

    # employer_name: String(255) -> String(400) for encryption overhead
    op.alter_column('cases', 'employer_name',
                    type_=sa.String(400),
                    existing_type=sa.String(255),
                    existing_nullable=True)

    # sro_name: String(255) -> String(400) for encryption overhead
    op.alter_column('cases', 'sro_name',
                    type_=sa.String(400),
                    existing_type=sa.String(255),
                    existing_nullable=True)

    # sro_address: Text -> Text (EncryptedText in model, no column change needed)
    # Already Text type, encryption is transparent via TypeDecorator

    # ==================== USERS TABLE ====================
    # Add email_hash column for uniqueness checks (before modifying email)
    op.add_column('users',
                  sa.Column('email_hash', sa.String(64), nullable=True))

    # Populate email_hash with SHA-256 of existing emails
    # This is done in raw SQL for efficiency
    op.execute("""
        UPDATE users
        SET email_hash = encode(sha256(lower(email)::bytea), 'hex')
        WHERE email IS NOT NULL
    """)

    # Create unique index on email_hash
    op.create_index('ix_users_email_hash', 'users', ['email_hash'], unique=True)

    # Drop old unique constraint and index on email
    op.drop_index('ix_users_email', table_name='users')

    # Expand email column for encryption overhead: String(255) -> String(400)
    op.alter_column('users', 'email',
                    type_=sa.String(400),
                    existing_type=sa.String(255),
                    existing_nullable=False)

    # Create non-unique index on email (for queries, though encrypted)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)

    # full_name: String(255) -> String(400) for encryption overhead
    op.alter_column('users', 'full_name',
                    type_=sa.String(400),
                    existing_type=sa.String(255),
                    existing_nullable=False)


def downgrade() -> None:
    """
    Revert encryption changes.

    WARNING: This requires decrypting all data first, otherwise
    data will be corrupted/truncated.
    """

    # ==================== USERS TABLE ====================
    # Revert full_name
    op.alter_column('users', 'full_name',
                    type_=sa.String(255),
                    existing_type=sa.String(400),
                    existing_nullable=False)

    # Drop non-unique index on email
    op.drop_index('ix_users_email', table_name='users')

    # Revert email column size
    op.alter_column('users', 'email',
                    type_=sa.String(255),
                    existing_type=sa.String(400),
                    existing_nullable=False)

    # Recreate unique index on email
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Drop email_hash index and column
    op.drop_index('ix_users_email_hash', table_name='users')
    op.drop_column('users', 'email_hash')

    # ==================== CASES TABLE ====================
    # Revert sro_name
    op.alter_column('cases', 'sro_name',
                    type_=sa.String(255),
                    existing_type=sa.String(400),
                    existing_nullable=True)

    # Revert employer_name
    op.alter_column('cases', 'employer_name',
                    type_=sa.String(255),
                    existing_type=sa.String(400),
                    existing_nullable=True)
