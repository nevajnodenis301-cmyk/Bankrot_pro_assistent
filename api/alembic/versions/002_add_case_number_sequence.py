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
    # Create a sequence for case numbers
    # This sequence will be used to generate sequential numbers for case_number
    # Format: BP-YYYY-#### where #### is from this sequence
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS case_number_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    """)

    # Create a function to generate the next case number
    op.execute("""
        CREATE OR REPLACE FUNCTION generate_case_number()
        RETURNS TEXT AS $$
        DECLARE
            next_num INTEGER;
            year_str TEXT;
            case_num TEXT;
        BEGIN
            -- Get the next sequence value
            next_num := nextval('case_number_seq');

            -- Get current year
            year_str := to_char(CURRENT_DATE, 'YYYY');

            -- Format: BP-YYYY-#### (4 digits, zero-padded)
            case_num := 'BP-' || year_str || '-' || lpad(next_num::TEXT, 4, '0');

            RETURN case_num;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create a trigger to automatically set case_number on insert if not provided
    op.execute("""
        CREATE OR REPLACE FUNCTION set_case_number()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.case_number IS NULL OR NEW.case_number = '' THEN
                NEW.case_number := generate_case_number();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_set_case_number
        BEFORE INSERT ON cases
        FOR EACH ROW
        EXECUTE FUNCTION set_case_number();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_set_case_number ON cases")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS set_case_number()")
    op.execute("DROP FUNCTION IF EXISTS generate_case_number()")

    # Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS case_number_seq")
