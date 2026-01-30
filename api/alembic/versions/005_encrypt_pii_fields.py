"""Encrypt PII fields with AES-256-GCM

Revision ID: 005_encrypt_pii_fields
Revises: 004_add_users_auth
Create Date: 2026-01-30 12:00:00.000000

This migration:
1. Alters column types to accommodate encrypted data (base64 adds ~40% overhead)
2. The actual encryption happens transparently via SQLAlchemy TypeDecorator
3. Existing plaintext data will be encrypted on first read/write

IMPORTANT: Ensure ENCRYPTION_KEY is set in environment before running this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_encrypt_pii_fields'
down_revision: Union[str, None] = '004_add_users_auth'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Alter column types to accommodate encrypted data.

    Encrypted values are base64-encoded and include:
    - 12 bytes nonce
    - 16 bytes auth tag
    - ciphertext (same length as plaintext)

    Total overhead: ~40 chars for base64 of 28 bytes + plaintext expansion
    """

    # ==================== CASES TABLE ====================
    # Passport fields
    op.alter_column('cases', 'passport_series',
                    type_=sa.String(100),
                    existing_type=sa.String(4))

    op.alter_column('cases', 'passport_number',
                    type_=sa.String(100),
                    existing_type=sa.String(6))

    op.alter_column('cases', 'passport_code',
                    type_=sa.String(100),
                    existing_type=sa.String(10))

    # passport_issued_by is already Text, no change needed

    # INN, SNILS
    op.alter_column('cases', 'inn',
                    type_=sa.String(100),
                    existing_type=sa.String(12))

    op.alter_column('cases', 'snils',
                    type_=sa.String(100),
                    existing_type=sa.String(14))

    # Contact info
    op.alter_column('cases', 'phone',
                    type_=sa.String(100),
                    existing_type=sa.String(20))

    op.alter_column('cases', 'email',
                    type_=sa.String(200),
                    existing_type=sa.String(100))

    # registration_address is already Text, no change needed

    # ==================== CHILDREN TABLE ====================
    op.alter_column('children', 'child_name',
                    type_=sa.String(400),
                    existing_type=sa.String(255))

    op.alter_column('children', 'child_certificate_number',
                    type_=sa.String(200),
                    existing_type=sa.String(100))

    op.alter_column('children', 'child_passport_series',
                    type_=sa.String(100),
                    existing_type=sa.String(4))

    op.alter_column('children', 'child_passport_number',
                    type_=sa.String(100),
                    existing_type=sa.String(6))

    op.alter_column('children', 'child_passport_code',
                    type_=sa.String(100),
                    existing_type=sa.String(10))

    # child_passport_issued_by is already Text, no change needed

    # ==================== CREDITORS TABLE ====================
    op.alter_column('creditors', 'inn',
                    type_=sa.String(100),
                    existing_type=sa.String(12))

    # address is already Text, no change needed

    # ==================== PROPERTIES TABLE ====================
    op.alter_column('properties', 'vehicle_vin',
                    type_=sa.String(150),
                    existing_type=sa.String(50))

    # ==================== USERS TABLE ====================
    op.alter_column('users', 'phone',
                    type_=sa.String(100),
                    existing_type=sa.String(20))

    # ==================== REFRESH_TOKENS TABLE ====================
    op.alter_column('refresh_tokens', 'ip_address',
                    type_=sa.String(150),
                    existing_type=sa.String(45))


def downgrade() -> None:
    """
    Revert column types to original sizes.

    WARNING: This will FAIL if encrypted data exists that is longer than
    the original column size. Decrypt all data before downgrading.
    """

    # ==================== REFRESH_TOKENS TABLE ====================
    op.alter_column('refresh_tokens', 'ip_address',
                    type_=sa.String(45),
                    existing_type=sa.String(150))

    # ==================== USERS TABLE ====================
    op.alter_column('users', 'phone',
                    type_=sa.String(20),
                    existing_type=sa.String(100))

    # ==================== PROPERTIES TABLE ====================
    op.alter_column('properties', 'vehicle_vin',
                    type_=sa.String(50),
                    existing_type=sa.String(150))

    # ==================== CREDITORS TABLE ====================
    op.alter_column('creditors', 'inn',
                    type_=sa.String(12),
                    existing_type=sa.String(100))

    # ==================== CHILDREN TABLE ====================
    op.alter_column('children', 'child_passport_code',
                    type_=sa.String(10),
                    existing_type=sa.String(100))

    op.alter_column('children', 'child_passport_number',
                    type_=sa.String(6),
                    existing_type=sa.String(100))

    op.alter_column('children', 'child_passport_series',
                    type_=sa.String(4),
                    existing_type=sa.String(100))

    op.alter_column('children', 'child_certificate_number',
                    type_=sa.String(100),
                    existing_type=sa.String(200))

    op.alter_column('children', 'child_name',
                    type_=sa.String(255),
                    existing_type=sa.String(400))

    # ==================== CASES TABLE ====================
    op.alter_column('cases', 'email',
                    type_=sa.String(100),
                    existing_type=sa.String(200))

    op.alter_column('cases', 'phone',
                    type_=sa.String(20),
                    existing_type=sa.String(100))

    op.alter_column('cases', 'snils',
                    type_=sa.String(14),
                    existing_type=sa.String(100))

    op.alter_column('cases', 'inn',
                    type_=sa.String(12),
                    existing_type=sa.String(100))

    op.alter_column('cases', 'passport_code',
                    type_=sa.String(10),
                    existing_type=sa.String(100))

    op.alter_column('cases', 'passport_number',
                    type_=sa.String(6),
                    existing_type=sa.String(100))

    op.alter_column('cases', 'passport_series',
                    type_=sa.String(4),
                    existing_type=sa.String(100))
