#!/usr/bin/env python3
"""
Script to encrypt existing plaintext PII data in the database.

Run this script AFTER running the Alembic migration 005_encrypt_pii_fields.

Usage:
    cd api
    python scripts/encrypt_existing_data.py

Requirements:
    - ENCRYPTION_KEY must be set in environment
    - Database must be accessible
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker
from utils.encryption import encrypt_value, is_encrypted

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Define which fields to encrypt in each table
ENCRYPTION_CONFIG = {
    'cases': [
        'passport_series',
        'passport_number',
        'passport_issued_by',
        'passport_code',
        'inn',
        'snils',
        'phone',
        'email',
        'registration_address',
    ],
    'children': [
        'child_name',
        'child_certificate_number',
        'child_passport_series',
        'child_passport_number',
        'child_passport_issued_by',
        'child_passport_code',
    ],
    'creditors': [
        'inn',
        'address',
    ],
    'properties': [
        'vehicle_vin',
    ],
    'users': [
        'phone',
    ],
    'refresh_tokens': [
        'ip_address',
    ],
}


async def encrypt_table_data(session: AsyncSession, table_name: str, fields: list[str]) -> dict:
    """
    Encrypt plaintext data in a table.

    Returns:
        dict with 'total', 'encrypted', 'skipped', 'errors' counts
    """
    from sqlalchemy import text

    stats = {'total': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    # Get all rows
    result = await session.execute(text(f"SELECT id, {', '.join(fields)} FROM {table_name}"))
    rows = result.fetchall()

    stats['total'] = len(rows)
    logger.info(f"Processing {len(rows)} rows in {table_name}")

    for row in rows:
        row_id = row[0]
        updates = {}

        for i, field in enumerate(fields):
            value = row[i + 1]

            if value is None:
                continue

            # Skip if already encrypted
            if is_encrypted(value):
                stats['skipped'] += 1
                continue

            try:
                encrypted = encrypt_value(value)
                updates[field] = encrypted
            except Exception as e:
                logger.error(f"Error encrypting {table_name}.{field} for id={row_id}: {e}")
                stats['errors'] += 1
                continue

        if updates:
            try:
                set_clause = ', '.join([f"{k} = :{k}" for k in updates.keys()])
                updates['row_id'] = row_id
                await session.execute(
                    text(f"UPDATE {table_name} SET {set_clause} WHERE id = :row_id"),
                    updates
                )
                stats['encrypted'] += len(updates) - 1  # -1 for row_id
            except Exception as e:
                logger.error(f"Error updating {table_name} id={row_id}: {e}")
                stats['errors'] += 1

    await session.commit()
    return stats


async def main():
    """Main encryption process."""
    logger.info("=" * 60)
    logger.info("PII Data Encryption Script")
    logger.info("=" * 60)

    # Verify encryption key is set
    if not os.getenv("ENCRYPTION_KEY"):
        logger.error("ENCRYPTION_KEY environment variable is not set!")
        logger.error("Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        sys.exit(1)

    logger.info(f"Starting encryption at {datetime.now().isoformat()}")
    logger.info("")

    total_stats = {'total': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    async with async_session_maker() as session:
        for table_name, fields in ENCRYPTION_CONFIG.items():
            logger.info(f"\n--- Processing table: {table_name} ---")
            logger.info(f"Fields to encrypt: {', '.join(fields)}")

            try:
                stats = await encrypt_table_data(session, table_name, fields)

                logger.info(f"  Total rows: {stats['total']}")
                logger.info(f"  Fields encrypted: {stats['encrypted']}")
                logger.info(f"  Already encrypted (skipped): {stats['skipped']}")
                logger.info(f"  Errors: {stats['errors']}")

                for key in total_stats:
                    total_stats[key] += stats[key]

            except Exception as e:
                logger.error(f"Error processing table {table_name}: {e}")
                total_stats['errors'] += 1

    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total rows processed: {total_stats['total']}")
    logger.info(f"Total fields encrypted: {total_stats['encrypted']}")
    logger.info(f"Total already encrypted: {total_stats['skipped']}")
    logger.info(f"Total errors: {total_stats['errors']}")

    if total_stats['errors'] > 0:
        logger.warning("There were errors during encryption. Review the logs above.")
        sys.exit(1)
    else:
        logger.info("Encryption completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
