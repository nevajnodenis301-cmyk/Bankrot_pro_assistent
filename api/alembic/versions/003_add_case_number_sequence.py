"""Add case number sequence

Revision ID: 003
Revises: 002
Create Date: 2026-01-23
"""
from alembic import op

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Create sequence for case numbers
    op.execute("CREATE SEQUENCE IF NOT EXISTS case_number_seq START WITH 1 INCREMENT BY 1;")
    
    # Set sequence to max existing case number + 1 (only if cases exist)
    op.execute("""
        DO $$
        DECLARE
            max_num INTEGER;
        BEGIN
            SELECT COALESCE(
                MAX(CAST(SPLIT_PART(case_number, '-', 3) AS INTEGER)),
                0
            ) INTO max_num
            FROM cases
            WHERE case_number ~ '^BP-[0-9]{4}-[0-9]{4}$';
            
            -- Only set sequence value if there are existing cases
            IF max_num > 0 THEN
                PERFORM setval('case_number_seq', max_num);
            END IF;
        END $$;
    """)

def downgrade():
    op.execute("DROP SEQUENCE IF EXISTS case_number_seq;")
